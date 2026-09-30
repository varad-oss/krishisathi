'use client';

import { CheckCircle2, CircleDashed, Radar, XCircle } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { DataQualityItem, Evidence, FarmIntelligence, Level, Risk, RiskSeverity, RuleRef } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { Card, CardTitle, ErrorState, KindTag, LevelBadge, LoadingBlock } from '../ui';
import { actionTitle, actionWhat, basisKind, because, evidenceText, impactText, reasonText } from './intelligence-text';

export function SeverityChip({ severity, className }: { severity: RiskSeverity; className?: string }) {
  const { t } = useI18n();
  if (severity === 'unavailable') {
    return (
      <span className={cn('inline-flex items-center gap-1.5 rounded-md bg-paper-deep/70 px-2 py-0.5 text-xs font-semibold text-ink-soft', className)}>
        <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-line-strong" />
        {t('state.unavailable')}
      </span>
    );
  }
  return <LevelBadge level={severity} className={className} />;
}

/** Evidence confidence, kept visibly separate from the risk level. */
export function ConfidenceChip({ level, className }: { level: Level; className?: string }) {
  const { t } = useI18n();
  const tone = level === 'high' ? 'ring-leaf-500 text-leaf-700' : level === 'moderate' ? 'ring-line-strong text-ink' : 'ring-watch-200 text-watch-700';
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-semibold ring-1', tone, className)} data-testid="confidence-chip">
      {t('risk.evidenceConfidence', { level: t(`level.${level}` as MessageKey) })}
    </span>
  );
}

/** Why the evidence confidence is what it is, from the engine's basis ids. */
export function ConfidenceWhy({ basis }: { basis?: string[] }) {
  const { t } = useI18n();
  const items = (basis ?? []).map((b) => [b, t(`risk.basis.${b}` as MessageKey)] as const).filter(([b, text]) => text !== `risk.basis.${b}`);
  if (!items.length) return null;
  return (
    <div className="text-sm">
      <p className="font-semibold">{t('risk.confidenceWhy')}</p>
      <ul className="mt-1 list-disc space-y-0.5 pl-5 text-ink-soft">
        {items.map(([b, text]) => (
          <li key={b}>{text}</li>
        ))}
      </ul>
    </div>
  );
}

export function EvidenceList({ evidence, rules }: { evidence: Evidence[]; rules?: RuleRef[] }) {
  const { t, fmt } = useI18n();
  if (!evidence.length && !rules?.length) return null;
  return (
    <div className="space-y-3 text-sm">
      {evidence.length > 0 && (
        <div>
          <p className="font-semibold">{t('risk.evidence')}</p>
          <ul className="mt-1 space-y-1.5">
            {evidence.map((e, i) => (
              <li key={`${e.id}-${i}`} className={cn('flex flex-wrap items-baseline gap-x-2 gap-y-1 text-ink-soft', e.role === 'context' && 'opacity-75')}>
                <span>{evidenceText(t, fmt, e)}</span>
                <KindTag kind={basisKind(e.basis)} className="text-xs" />
                {e.role === 'context' && <span className="text-xs text-ink-faint">{t('risk.evidence.context')}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
      {rules && rules.length > 0 && (
        <div>
          <p className="font-semibold">{t('risk.rules')}</p>
          <ul className="mt-1 space-y-1 text-xs text-ink-faint" lang="en">
            {rules.filter((r, i) => rules.findIndex((x) => x.source === r.source) === i).map((r) => (
              <li key={r.id}>
                {r.url ? (
                  <a href={r.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-leaf-700">
                    {r.source}
                  </a>
                ) : (
                  r.source
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function RiskRow({ risk, cropLabel }: { risk: Risk; cropLabel: string | null }) {
  const { t, fmt, language } = useI18n();
  const reason = because(t, language, risk.drivers);
  const summary =
    risk.severity === 'unavailable' ? reasonText(t, risk.reason) : risk.action ? actionTitle(t, risk.action) : reason ?? t('risk.lowNote');
  const impact = risk.severity === 'moderate' || risk.severity === 'high' ? impactText(t, risk) : null;
  return (
    <li id={`risk-${risk.category}`}>
      <details className="group bg-surface open:bg-paper/50">
        <summary className="flex min-h-11 cursor-pointer list-none items-start justify-between gap-3 px-4 py-3.5">
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-semibold">{t(`risk.${risk.category}` as MessageKey)}</span>
              <SeverityChip severity={risk.severity} />
              {risk.severity !== 'unavailable' && risk.confidence && <ConfidenceChip level={risk.confidence} />}
            </div>
            <p className="mt-0.5 text-sm text-ink-soft">{summary}</p>
          </div>
          <span aria-hidden className="mt-1 text-ink-faint transition-transform group-open:rotate-180">▾</span>
        </summary>
        <div className="space-y-3 px-4 pb-4 text-sm">
          {risk.severity !== 'unavailable' && reason && (
            <p>
              <span className="font-semibold">{t('farm.alerts.why')}: </span>
              <span className="text-ink-soft">{reason}</span>
            </p>
          )}
          {risk.action && (
            <p>
              <span className="font-semibold">{t('risk.whatToDo')}: </span>
              <span className="text-ink-soft">{actionWhat(t, risk.action, risk.drivers, cropLabel)}</span>
            </p>
          )}
          {impact && (
            <p>
              <span className="font-semibold">{t('farm.alerts.impact')}: </span>
              <span className="text-ink-soft">{impact}</span>
            </p>
          )}
          {risk.severity !== 'unavailable' && risk.confidence && <ConfidenceWhy basis={risk.confidence_basis} />}
          <EvidenceList evidence={risk.evidence} rules={risk.rules} />
          {risk.date && <p className="text-xs text-ink-faint">{fmt.date(risk.date, { weekday: 'long', day: 'numeric', month: 'short' })}</p>}
        </div>
      </details>
    </li>
  );
}

export function RiskRadar({ intel, cropLabel }: { intel: Resource<FarmIntelligence>; cropLabel: string | null }) {
  const { t } = useI18n();
  const data = intel.data;
  return (
    <Card id="risks" aria-labelledby="risks-title" className="scroll-mt-header">
      <CardTitle icon={Radar} id="risks-title" description={t('risk.subtitle')}>
        {t('risk.title')}
      </CardTitle>
      {!data && intel.status === 'loading' ? (
        <LoadingBlock lines={5} />
      ) : !data && intel.status === 'error' ? (
        <ErrorState error={intel.error} onRetry={intel.reload} title={t('risk.unavailable')} />
      ) : data ? (
        <>
          {intel.status === 'error' && <ErrorState compact error={intel.error} onRetry={intel.reload} updatedAt={intel.updatedAt} />}
          <ul className="divide-y divide-line overflow-hidden rounded-[var(--radius-inner)] ring-1 ring-line">
            {data.risks.map((r) => (
              <RiskRow key={r.category} risk={r} cropLabel={cropLabel} />
            ))}
          </ul>
          <p className="mt-3 text-sm text-ink-soft">{t('risk.levelVsConfidence')}</p>
          <p className="mt-2 text-xs text-ink-faint">{t('risk.engineNote')}</p>
        </>
      ) : null}
    </Card>
  );
}

const DQ_ICON = { good: CheckCircle2, partial: CircleDashed, bad: XCircle };

function dqTone(d: DataQualityItem): keyof typeof DQ_ICON {
  if (d.status === 'available') return 'good';
  if (d.status === 'unavailable' || d.status === 'not_configured') return 'bad';
  return 'partial';
}

/** One line per source: is it in use, how fresh, and what kind of data it is. */
export function DataQualityStrip({ items }: { items: DataQualityItem[] }) {
  const { t, fmt } = useI18n();
  const detail = (d: DataQualityItem) => {
    if (d.status !== 'available') return t(`dq.status.${d.status}` as MessageKey);
    if (d.source === 'satellite' && d.as_of) return t('dq.imageFrom', { date: fmt.date(d.as_of) });
    if (d.as_of) return t('state.updated', { time: fmt.relative(d.as_of) });
    return t('dq.status.available');
  };
  return (
    <section aria-labelledby="dq-title" className="border-t border-line bg-paper/40 px-5 py-4 sm:px-8">
      <h3 id="dq-title" className="text-xs font-semibold text-ink-soft">{t('dq.title')}</h3>
      <ul className="mt-2 grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2 lg:grid-cols-5">
        {items.map((d) => {
          const tone = dqTone(d);
          const Icon = DQ_ICON[tone];
          return (
            <li key={d.source} className="flex items-start gap-2">
              <Icon aria-hidden className={cn('mt-0.5 h-4 w-4 shrink-0', tone === 'good' ? 'text-leaf-600' : tone === 'bad' ? 'text-warn-700' : 'text-ink-faint')} />
              <span className="min-w-0">
                <span className="font-medium">{t(`dq.source.${d.source}` as MessageKey)}</span>
                <span className="block text-xs text-ink-faint">
                  {detail(d)}
                  {d.status === 'available' && <> · <KindTag kind={d.kind} /></>}
                </span>
              </span>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
