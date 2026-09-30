'use client';

import { useState } from 'react';
import { CheckCircle2, ChevronDown } from 'lucide-react';
import { ApiError, recordPractice } from '@/lib/api';
import { enqueue, isConnectivityError } from '@/lib/offline';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { CropOptions, FarmTwin, PracticeStatus, RegenerativeResponse, RegenHorizon, RegenPlanItem, RegenTrigger } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { ErrorState, LoadingBlock, Note, SavedCopyTag, Section } from '../ui';
import { Choices } from './History';

const HORIZONS: RegenHorizon[] = ['current', 'next', 'long_term'];
const ADOPTION: PracticeStatus[] = ['adopted', 'partial', 'skipped'];

type TriggerText = (tr: RegenTrigger) => string | null;

/** "Are you doing this?" for one practice. Self-reported; saved to the farm history so outcomes can be followed up. */
function PracticeAdoption({ twin, practice, onSaved }: { twin: FarmTwin; practice: string; onSaved?: () => void }) {
  const { t } = useI18n();
  const [saved, setSaved] = useState<PracticeStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [queued, setQueued] = useState(false);

  const save = async (status: PracticeStatus) => {
    setBusy(true);
    setError(null);
    try {
      await recordPractice(twin, practice, status);
      setSaved(status);
      onSaved?.();
    } catch (e) {
      if (e instanceof ApiError && isConnectivityError(e.code)) {
        // Offline: kept on the device and sent when the connection returns.
        enqueue({ id: `practice:${practice}`, kind: 'practice', farmId: twin.farmId, token: twin.token, body: { practice, status } });
        setSaved(status);
        setQueued(true);
        return;
      }
      setError(e instanceof ApiError ? e : new ApiError('error', 'INTERNAL_ERROR', null, true));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="sm:col-span-2" aria-live="polite">
      {queued && <p className="mb-1 text-xs font-medium text-sky-700">{t('offline.queued')}</p>}
      {saved ? (
        <p className="flex items-start gap-2 text-sm text-ink-soft">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-leaf-600" aria-hidden />
          {t('farm.regen.adopt.saved', { answer: t(`farm.regen.adopt.${saved}` as MessageKey) })}
        </p>
      ) : (
        <Choices question={t('farm.regen.adopt.question')} options={ADOPTION} labelPrefix="farm.regen.adopt" onPick={save} busy={busy} />
      )}
      {error && <ErrorState compact error={error} title={t('farm.regen.adopt.failed')} />}
    </div>
  );
}

function PracticeItem({ rec, index, triggerText, twin, onSaved }: { rec: RegenPlanItem; index: number; triggerText: TriggerText; twin: FarmTwin | null; onSaved?: () => void }) {
  const { t, fmt } = useI18n();
  const base = `regen.${rec.id}`;
  const basis = rec.triggers.map(triggerText).filter(Boolean) as string[];
  return (
    <li>
      <details className="group">
        <summary className="flex min-h-14 cursor-pointer list-none items-center justify-between gap-3 py-4 hover:bg-paper/60 sm:px-2">
          <span className="flex min-w-0 items-start gap-3">
            <span aria-hidden className="mt-0.5 w-5 font-display text-lg leading-none text-soil-500 tabular-nums">{fmt.num(index + 1, 0)}</span>
            <span className="min-w-0">
              <span className="block font-semibold leading-snug">{t(`${base}.title` as MessageKey)}</span>
              <span className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs font-medium">
                <span className={cn('inline-flex items-center gap-1.5', rec.priority === 'high' ? 'text-soil-700' : rec.priority === 'medium' ? 'text-leaf-700' : 'text-ink-faint')}>
                  <span aria-hidden className={cn('h-1.5 w-1.5 rounded-full', rec.priority === 'high' ? 'bg-soil-500' : rec.priority === 'medium' ? 'bg-leaf-500' : 'bg-line-strong')} />
                  {t(`farm.regen.priority.${rec.priority}` as MessageKey)}
                </span>
                <span className="text-ink-soft">{t(`farm.regen.timing.${rec.timing}` as MessageKey)}</span>
              </span>
            </span>
          </span>
          <ChevronDown aria-hidden className="h-5 w-5 shrink-0 text-ink-faint transition-transform group-open:rotate-180" />
        </summary>
        <dl className="grid gap-3 pb-5 pl-8 text-sm sm:grid-cols-2 sm:pl-10">
          {(['why', 'what', 'when', 'benefit'] as const).map((f) => (
            <div key={f}>
              <dt className="font-semibold">{t(`farm.regen.${f}` as MessageKey)}</dt>
              <dd className="text-ink-soft">{t(`${base}.${f}` as MessageKey)}</dd>
            </div>
          ))}
          <div className="sm:col-span-2">
            <dt className="font-semibold">{t('farm.regen.basis')}</dt>
            <dd className="text-ink-soft">
              {basis.length ? basis.join(' · ') : t('farm.regen.basisGeneral')}
              <span className="block text-xs text-ink-soft">{t(`farm.regen.confidence.${rec.confidence}` as MessageKey)}</span>
            </dd>
          </div>
          {twin && <PracticeAdoption twin={twin} practice={rec.id} onSaved={onSaved} />}
        </dl>
      </details>
    </li>
  );
}

/** Practices placed on the crop cycle: this season, next season, lasting habits. Order within a group is priority. */
export function PracticePlan({ data, triggerText, twin, onSaved }: { data: RegenerativeResponse; triggerText: TriggerText; twin: FarmTwin | null; onSaved?: () => void }) {
  const { t } = useI18n();
  let n = 0;
  return (
    <div className="space-y-6">
      <p className="text-sm text-ink-soft">{t(data.crop_stage?.status === 'estimated' ? 'farm.regen.stageNote' : 'farm.regen.noStage')}</p>
      {HORIZONS.map((h) => {
        const items = data.plan.filter((r) => r.horizon === h);
        if (!items.length) return null;
        return (
          <section key={h} aria-labelledby={`regen-${h}`}>
            <h4 id={`regen-${h}`} className="mb-1 text-sm font-semibold text-soil-700">{t(`farm.regen.horizon.${h}` as MessageKey)}</h4>
            <ol className="divide-y divide-line border-y border-line">
              {items.map((rec) => (
                <PracticeItem key={rec.id} rec={rec} index={n++} triggerText={triggerText} twin={twin} onSaved={onSaved} />
              ))}
            </ol>
          </section>
        );
      })}
    </div>
  );
}

/** Trade-offs between the farm's crop and crops grown nearby, from verified sources only. Never a ranking. */
export function CropOptionsCard({ options }: { options: Resource<CropOptions> }) {
  const { t, fmt } = useI18n();
  const data = options.data;
  const dash = <span className="text-ink-faint">{t('farm.options.notAvailable')}</span>;
  return (
    <Section
      id="options"
      title={t('farm.options.title')}
      description={t(data?.basis === 'all_supported_crops' ? 'farm.options.subtitleAll' : 'farm.options.subtitle')}
      action={options.cached && options.updatedAt ? <SavedCopyTag time={options.updatedAt} /> : undefined}
    >
      {!data && options.status === 'loading' ? (
        <LoadingBlock lines={4} />
      ) : !data && options.status === 'error' ? (
        <ErrorState error={options.error} onRetry={options.reload} title={t('farm.options.unavailable')} />
      ) : data ? (
        <>
          {options.status === 'error' && <ErrorState compact error={options.error} onRetry={options.reload} updatedAt={options.updatedAt} />}
          <div className="relative -mx-1 overflow-x-auto">
            <table className="w-full min-w-[34rem] text-left text-sm">
              <thead className="text-xs text-ink-soft">
                <tr className="border-b border-line">
                  <th scope="col" className="px-1 py-2 font-medium">{t('farm.options.crop')}</th>
                  <th scope="col" className="px-1 py-2 font-medium">{t('farm.options.water')}</th>
                  <th scope="col" className="px-1 py-2 font-medium">{t('farm.options.season')}</th>
                  <th scope="col" className="px-1 py-2 font-medium">{t('farm.options.diseaseRef')}</th>
                  <th scope="col" className="px-1 py-2 font-medium">{t('farm.options.clusters')}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line">
                {data.crops.map((c) => (
                  <tr key={c.crop} className={cn(c.is_current && 'bg-leaf-50/60')}>
                    <th scope="row" className="px-1 py-2.5 font-medium">
                      {t(`crop.${c.crop}` as MessageKey)}
                      {c.is_current && <span className="ml-2 rounded-full bg-leaf-100 px-2 py-0.5 text-xs font-medium text-leaf-700">{t('farm.options.yours')}</span>}
                    </th>
                    <td className="px-1 py-2.5 tabular-nums">
                      {c.water_need_mm ? t('farm.options.waterValue', { min: fmt.num(c.water_need_mm.min, 0), max: fmt.num(c.water_need_mm.max, 0) }) : dash}
                    </td>
                    <td className="px-1 py-2.5 tabular-nums">{c.season_length_days ? t('farm.options.seasonValue', { days: fmt.num(c.season_length_days, 0) }) : dash}</td>
                    <td className="px-1 py-2.5 tabular-nums">{fmt.num(c.verified_disease_entries, 0)}</td>
                    <td className="px-1 py-2.5 tabular-nums">{c.nearby_disease_clusters === null ? <span className="text-ink-faint">{t('farm.options.unknown')}</span> : fmt.num(c.nearby_disease_clusters, 0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Note className="mt-4">{t('farm.options.market')}</Note>
          <div className="mt-6 space-y-1 border-t border-line pt-3 text-xs text-ink-soft">
            <p className="font-semibold text-ink-soft">{t('provenance.source')}:</p>
            <p>
              {t('farm.options.water')}: <a className="underline underline-offset-2" href={data.sources.water_need.url} target="_blank" rel="noreferrer">{data.sources.water_need.source}</a>. {t('farm.options.waterNote')}
            </p>
            <p>
              {t('farm.options.season')}: <a className="underline underline-offset-2" href={data.sources.season_length.url} target="_blank" rel="noreferrer">{data.sources.season_length.source}</a>
            </p>
            <p>{t('farm.options.clusters')}: {t('kind.ai_classified_user_reports')}</p>
          </div>
        </>
      ) : null}
    </Section>
  );
}
