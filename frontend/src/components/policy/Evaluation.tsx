'use client';

import { MessageSquareQuote } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { AdvisoryFeedback, DiagnosisFeedback, EvaluationMetrics, Level } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { Card, CardTitle, ErrorState, LoadingBlock, Note } from '../ui';

const TIERS: Level[] = ['high', 'moderate', 'low'];

/**
 * KrishiSathi self-reported feedback: diagnosis feedback by model confidence and advice follow-through.
 * Labelled as app feedback everywhere; never presented as success, yield or accuracy.
 */
export function EvaluationPanel({ evaluation }: { evaluation: Resource<EvaluationMetrics> }) {
  const { t, fmt } = useI18n();
  const e = evaluation.data;
  const pct = (v: number | null | undefined) => (v == null ? '—' : `${fmt.num(Math.round(v * 100), 0)}%`);
  const overall = e?.advisory.overall;
  const hasOverall = overall && 'followed_rate' in overall;
  return (
    <Card aria-labelledby="eval-title" data-testid="evaluation-panel">
      <CardTitle icon={MessageSquareQuote} id="eval-title" description={e ? t('eval.subtitle', { days: fmt.num(e.window_days, 0), min: fmt.num(e.minimum_group_size, 0) }) : undefined}>
        {t('eval.title')}
      </CardTitle>
      {!e && evaluation.status === 'loading' ? (
        <LoadingBlock lines={4} />
      ) : !e && evaluation.status === 'error' ? (
        <ErrorState error={evaluation.error} onRetry={evaluation.reload} title={t('eval.unavailable')} />
      ) : e ? (
        <div className="space-y-5 text-sm">
          <Note tone="watch">{t('eval.notProof')}</Note>
          <section aria-labelledby="eval-diag">
            <h3 id="eval-diag" className="font-semibold">{t('eval.diagnosis.title')}</h3>
            <p className="text-xs text-ink-faint">{t('eval.diagnosis.note')}</p>
            <ul className="mt-2 divide-y divide-line rounded-[var(--radius-inner)] ring-1 ring-line">
              {TIERS.map((tier) => {
                const row = e.diagnosis.observed_feedback_by_model_confidence.tiers[tier];
                const ok = row && 'feedback_count' in row;
                return (
                  <li key={tier} className="flex flex-wrap items-baseline justify-between gap-2 px-3 py-2" data-testid={`eval-tier-${tier}`}>
                    <span className="min-w-0 [overflow-wrap:anywhere]">{t('eval.tier', { level: t(`level.${tier}` as MessageKey) })}</span>
                    <span className="min-w-0 tabular-nums text-ink-soft [overflow-wrap:anywhere]">
                      {ok
                        ? t('eval.tier.value', { wrong: fmt.num((row as DiagnosisFeedback).diagnosis_wrong, 0), total: fmt.num((row as DiagnosisFeedback).feedback_count, 0) })
                        : t('eval.suppressed')}
                    </span>
                  </li>
                );
              })}
            </ul>
          </section>
          <section aria-labelledby="eval-adv">
            <h3 id="eval-adv" className="font-semibold">{t('eval.advisory.title')}</h3>
            {hasOverall ? (
              <dl className="mt-2 grid grid-cols-1 gap-2 text-center sm:grid-cols-3">
                {(['followed_rate', 'partial_rate', 'not_followed_rate'] as const).map((k) => (
                  <div key={k} className="rounded-[var(--radius-inner)] bg-paper/70 p-2">
                    <dt className="text-xs text-ink-soft [overflow-wrap:anywhere]">{t(`eval.advisory.${k}` as MessageKey)}</dt>
                    <dd className="font-display text-xl tabular-nums">{pct((overall as AdvisoryFeedback)[k])}</dd>
                  </div>
                ))}
              </dl>
            ) : (
              <p className="mt-1 text-ink-soft">{t('eval.insufficient')}</p>
            )}
            {hasOverall && (
              <p className="mt-2 text-xs text-ink-faint">{t('eval.advisory.answers', { count: fmt.num((overall as AdvisoryFeedback).follow_through_answers, 0) })}</p>
            )}
          </section>
          <p className="text-xs text-ink-faint">
            {t('provenance.source')}: <span lang="en">{e.provenance.source}</span> · {e.label}
          </p>
        </div>
      ) : null}
    </Card>
  );
}
