'use client';

import { useState } from 'react';
import { CheckCircle2, History as HistoryIcon } from 'lucide-react';
import { ApiError, sendFeedback } from '@/lib/api';
import { enqueue, isConnectivityError } from '@/lib/offline';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { FarmHistory, FarmSnapshot, FarmTwin, Followed, Outcome, TwinAction } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { buttonClass, EmptyState, ErrorState, LoadingBlock, UnavailableNote } from '../ui';
import { SeverityChip } from './Intelligence';
import { actionTitle, stageText } from './intelligence-text';

const FOLLOWED: Followed[] = ['yes', 'partial', 'no', 'not_applicable'];
const OUTCOMES: Outcome[] = ['improved', 'same', 'worse', 'not_sure'];

export function Choices<T extends string>({ question, options, labelPrefix, onPick, busy }: { question: string; options: T[]; labelPrefix: string; onPick: (v: T) => void; busy: boolean }) {
  const { t } = useI18n();
  return (
    <fieldset disabled={busy}>
      <legend className="font-semibold">{question}</legend>
      <div className="mt-2.5 flex flex-wrap gap-2">
        {options.map((o) => (
          <button key={o} type="button" onClick={() => onPick(o)} className={cn(buttonClass.secondary, 'min-h-11 px-4 py-1.5 hover:border-leaf-600 hover:bg-leaf-50')}>
            {t(`${labelPrefix}.${o}` as MessageKey)}
          </button>
        ))}
      </div>
    </fieldset>
  );
}

/** "Did you do it?" now, and "How did the crop respond?" once the farmer followed it. Self-reported, never proof. */
export function ActionFeedback({ twin, action, onSaved, compact }: { twin: FarmTwin; action: TwinAction; onSaved?: (a: TwinAction) => void; compact?: boolean }) {
  const { t } = useI18n();
  const [current, setCurrent] = useState(action);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [queued, setQueued] = useState(false);

  const save = async (feedback: { followed?: Followed; outcome?: Outcome }) => {
    setBusy(true);
    setError(null);
    try {
      const updated = await sendFeedback(twin, current.action_id, feedback);
      setCurrent(updated);
      onSaved?.(updated);
    } catch (e) {
      if (e instanceof ApiError && isConnectivityError(e.code)) {
        // Offline: keep the answer on the device and send it when the connection returns.
        enqueue({ id: `feedback:${current.action_id}:${Object.keys(feedback).join()}`, kind: 'feedback', farmId: twin.farmId, token: twin.token, actionId: current.action_id, body: feedback as Record<string, string> });
        setCurrent({ ...current, ...feedback });
        setQueued(true);
        return;
      }
      setError(e instanceof ApiError ? e : new ApiError('error', 'INTERNAL_ERROR', null, true));
    } finally {
      setBusy(false);
    }
  };

  const outcomes = current.source_type === 'diagnosis' ? [...OUTCOMES.slice(0, 3), 'diagnosis_wrong' as Outcome, 'not_sure' as Outcome] : OUTCOMES;
  const askOutcome = (current.followed === 'yes' || current.followed === 'partial') && !current.outcome;
  return (
    <div className={cn('space-y-3', !compact && 'rounded-[var(--radius-inner)] border border-line bg-paper/60 p-4')} aria-live="polite">
      {!current.followed ? (
        <Choices question={t('feedback.question')} options={FOLLOWED} labelPrefix="feedback.followed" onPick={(v) => save({ followed: v })} busy={busy} />
      ) : askOutcome && !compact ? (
        <p className="flex animate-rise items-start gap-2 text-sm text-ink">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-leaf-600" aria-hidden /> {t('feedback.thanksLater')}
        </p>
      ) : askOutcome ? (
        <Choices question={t('feedback.outcomeQuestion')} options={outcomes} labelPrefix="feedback.outcome" onPick={(v) => save({ outcome: v })} busy={busy} />
      ) : (
        <p className="flex animate-rise items-start gap-2 text-sm text-ink">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-leaf-600" aria-hidden /> {t('feedback.thanks')}
        </p>
      )}
      {queued && <p className="text-xs font-medium text-sky-700">{t('offline.queued')}</p>}
      {error && <ErrorState compact error={error} title={t('feedback.failed')} />}
      {!compact && <p className="text-xs text-ink-soft">{t('feedback.note')}</p>}
    </div>
  );
}

type Entry = { at: string; kind: 'action'; action: TwinAction } | { at: string; kind: 'check'; snapshot: FarmSnapshot };

/**
 * The farm's story as a timeline: what KrishiSathi suggested, what the farmer reported back, and the routine
 * checks in between, newest first and grouped by day. Farmer answers are shown as their own report, never as proof.
 */
export function FarmTimeline({ history, twin }: { history: Resource<FarmHistory>; twin: FarmTwin | null }) {
  const { t, fmt } = useI18n();
  const h = history.data;
  const entries: Entry[] = h
    ? [
        ...h.actions.map((a) => ({ at: a.created_at, kind: 'action' as const, action: a })),
        ...h.snapshots.map((s) => ({ at: s.created_at, kind: 'check' as const, snapshot: s })),
      ].sort((a, b) => b.at.localeCompare(a.at))
    : [];
  const days = new Map<string, Entry[]>();
  for (const e of entries) {
    const day = fmt.date(e.at, { weekday: 'long', day: 'numeric', month: 'long' });
    days.set(day, [...(days.get(day) ?? []), e]);
  }

  return (
    <div id="history" className="scroll-mt-header" aria-labelledby="history-title" role="region">
      <h2 id="history-title" className="sr-only">{t('history.title')}</h2>
      {!twin ? (
        <UnavailableNote>{t('history.localOnly')}</UnavailableNote>
      ) : !h && history.status === 'loading' ? (
        <LoadingBlock lines={4} />
      ) : !h && history.status === 'error' ? (
        <ErrorState error={history.error} onRetry={history.reload} title={t('history.unavailable')} />
      ) : entries.length === 0 ? (
        <EmptyState icon={HistoryIcon}>{t('history.empty')}</EmptyState>
      ) : (
        <ol className="space-y-8">
          {[...days.entries()].map(([day, list]) => (
            <li key={day}>
              <h3 className="mb-3 text-sm font-semibold text-ink-soft">{day}</h3>
              <ol className="relative ml-2 space-y-5 border-l-2 border-line pl-6">
                {list.map((e) => (e.kind === 'action' ? <ActionEntry key={e.action.action_id} a={e.action} twin={twin} onSaved={history.reload} /> : <CheckEntry key={e.snapshot.snapshot_id} s={e.snapshot} />))}
              </ol>
            </li>
          ))}
        </ol>
      )}
      {history.status === 'error' && h && <ErrorState compact error={history.error} onRetry={history.reload} updatedAt={history.updatedAt} />}
      <p className="mt-8 border-t border-line pt-4 text-sm text-ink-soft">{t('feedback.note')}</p>
    </div>
  );
}

const DOT: Record<string, string> = { high: 'bg-warn-500', moderate: 'bg-watch-500', low: 'bg-leaf-500' };

function ActionEntry({ a, twin, onSaved }: { a: TwinAction; twin: FarmTwin; onSaved: () => void }) {
  const { t, fmt } = useI18n();
  const pending = !a.followed || ((a.followed === 'yes' || a.followed === 'partial') && !a.outcome);
  return (
    <li className="relative">
      <span aria-hidden className={cn('absolute -left-[1.94rem] top-1.5 h-3.5 w-3.5 rounded-full ring-4 ring-paper', (a.severity && DOT[a.severity]) || 'bg-leaf-600')} />
      <p className="flex flex-wrap items-center gap-x-2 text-sm text-ink-soft">
        <span className="font-medium">{t(`history.source.${a.source_type}` as MessageKey)}</span>
        <span aria-hidden>·</span>
        <time dateTime={a.created_at}>{fmt.date(a.created_at, { hour: 'numeric', minute: '2-digit' })}</time>
        {a.severity && a.severity !== 'low' && <SeverityChip severity={a.severity} />}
      </p>
      <p className="mt-1 text-[1.05rem] font-semibold leading-snug">{a.source_type === 'regenerative' ? t(`regen.${a.action}.title` as MessageKey) : actionTitle(t, a.action)}</p>
      {(a.followed || a.outcome) && (
        <ul className="mt-2 space-y-1 border-l-2 border-leaf-200 pl-3 text-sm">
          {a.followed && <li>{t('history.followed', { answer: t(`feedback.followed.${a.followed}` as MessageKey) })}</li>}
          {a.outcome && <li>{t('history.outcome', { answer: t(`feedback.outcome.${a.outcome}` as MessageKey) })}</li>}
        </ul>
      )}
      {pending && (
        <div className="mt-3">
          <ActionFeedback twin={twin} action={a} compact onSaved={onSaved} />
        </div>
      )}
    </li>
  );
}

function CheckEntry({ s }: { s: FarmSnapshot }) {
  const { t, fmt } = useI18n();
  return (
    <li className="relative text-sm">
      <span aria-hidden className="absolute -left-[1.81rem] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-line-strong bg-paper" />
      <p className="text-ink-soft">
        <span className="font-medium">{t('history.checks')}</span> · <time dateTime={s.created_at}>{fmt.date(s.created_at, { hour: 'numeric', minute: '2-digit' })}</time>
        {s.crop_stage && <> · {stageText(t, s.crop_stage)}</>}
      </p>
      <p className="mt-0.5 flex flex-wrap items-center gap-2 text-ink">
        {s.top_action ? actionTitle(t, s.top_action) : t('action.routine_monitoring.title')}
        {s.top_severity && s.top_severity !== 'low' && <SeverityChip severity={s.top_severity} />}
      </p>
    </li>
  );
}
