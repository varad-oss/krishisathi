'use client';

import { useState } from 'react';
import { CheckCircle2, History } from 'lucide-react';
import { ApiError, sendFeedback } from '@/lib/api';
import { enqueue, isConnectivityError } from '@/lib/offline';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { FarmHistory, FarmTwin, Followed, Outcome, TwinAction } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { buttonClass, Card, CardTitle, ErrorState, LoadingBlock, UnavailableNote } from '../ui';
import { SeverityChip } from './Intelligence';
import { actionTitle, stageText } from './intelligence-text';

const FOLLOWED: Followed[] = ['yes', 'partial', 'no', 'not_applicable'];
const OUTCOMES: Outcome[] = ['improved', 'same', 'worse', 'not_sure'];

export function Choices<T extends string>({ question, options, labelPrefix, onPick, busy }: { question: string; options: T[]; labelPrefix: string; onPick: (v: T) => void; busy: boolean }) {
  const { t } = useI18n();
  return (
    <fieldset disabled={busy}>
      <legend className="text-sm font-semibold">{question}</legend>
      <div className="mt-2 flex flex-wrap gap-2">
        {options.map((o) => (
          <button key={o} type="button" onClick={() => onPick(o)} className={cn(buttonClass.secondary, 'min-h-10 px-3.5 py-1.5')}>
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
    <div className={cn('space-y-3', !compact && 'rounded-[var(--radius-inner)] bg-paper/70 p-4')} aria-live="polite">
      {!current.followed ? (
        <Choices question={t('feedback.question')} options={FOLLOWED} labelPrefix="feedback.followed" onPick={(v) => save({ followed: v })} busy={busy} />
      ) : askOutcome && !compact ? (
        <p className="flex items-start gap-2 text-sm text-ink-soft">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-leaf-600" aria-hidden /> {t('feedback.thanksLater')}
        </p>
      ) : askOutcome ? (
        <Choices question={t('feedback.outcomeQuestion')} options={outcomes} labelPrefix="feedback.outcome" onPick={(v) => save({ outcome: v })} busy={busy} />
      ) : (
        <p className="flex items-start gap-2 text-sm text-ink-soft">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-leaf-600" aria-hidden /> {t('feedback.thanks')}
        </p>
      )}
      {queued && <p className="text-xs font-medium text-sky-700">{t('offline.queued')}</p>}
      {error && <ErrorState compact error={error} title={t('feedback.failed')} />}
      {!compact && <p className="text-xs text-ink-faint">{t('feedback.note')}</p>}
    </div>
  );
}

export function FarmHistoryCard({ history, twin }: { history: Resource<FarmHistory>; twin: FarmTwin | null }) {
  const { t, fmt } = useI18n();
  const h = history.data;
  return (
    <Card id="history" aria-labelledby="history-title" className="scroll-mt-header">
      <CardTitle icon={History} id="history-title" description={t('history.subtitle')}>
        {t('history.title')}
      </CardTitle>
      {!twin ? (
        <UnavailableNote>{t('history.localOnly')}</UnavailableNote>
      ) : !h && history.status === 'loading' ? (
        <LoadingBlock lines={3} />
      ) : !h && history.status === 'error' ? (
        <ErrorState error={history.error} onRetry={history.reload} title={t('history.unavailable')} />
      ) : h && h.actions.length === 0 && h.snapshots.length === 0 ? (
        <p className="text-sm text-ink-soft">{t('history.empty')}</p>
      ) : h ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <section aria-labelledby="history-recs">
            <h3 id="history-recs" className="mb-2 text-sm font-semibold text-ink-soft">{t('history.recommendations')}</h3>
            <ul className="divide-y divide-line rounded-[var(--radius-inner)] ring-1 ring-line">
              {h.actions.map((a) => (
                <li key={a.action_id} className="space-y-2 p-3 text-sm">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs text-ink-faint">{fmt.date(a.created_at)} · {t(`history.source.${a.source_type}` as MessageKey)}</span>
                    {a.severity && <SeverityChip severity={a.severity} />}
                  </div>
                  <p className="font-medium">{a.source_type === 'regenerative' ? t(`regen.${a.action}.title` as MessageKey) : actionTitle(t, a.action)}</p>
                  {a.followed && <p className="text-ink-soft">{t('history.followed', { answer: t(`feedback.followed.${a.followed}` as MessageKey) })}</p>}
                  {a.outcome && <p className="text-ink-soft">{t('history.outcome', { answer: t(`feedback.outcome.${a.outcome}` as MessageKey) })}</p>}
                  {(!a.followed || ((a.followed === 'yes' || a.followed === 'partial') && !a.outcome)) && <ActionFeedback twin={twin} action={a} compact onSaved={history.reload} />}
                </li>
              ))}
            </ul>
          </section>
          <section aria-labelledby="history-checks">
            <h3 id="history-checks" className="mb-2 text-sm font-semibold text-ink-soft">{t('history.checks')}</h3>
            <ol className="space-y-2">
              {h.snapshots.map((s) => (
                <li key={s.snapshot_id} className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm">
                  <span className="w-24 shrink-0 text-xs text-ink-faint">{fmt.dateTime(s.created_at)}</span>
                  <span className="font-medium">{s.top_action ? actionTitle(t, s.top_action) : t('action.routine_monitoring.title')}</span>
                  {s.top_severity && s.top_severity !== 'low' && <SeverityChip severity={s.top_severity} />}
                  {s.crop_stage && <span className="text-xs text-ink-faint">· {stageText(t, s.crop_stage)}</span>}
                </li>
              ))}
            </ol>
          </section>
        </div>
      ) : null}
      <p className="mt-4 text-xs text-ink-faint">{t('feedback.note')}</p>
    </Card>
  );
}
