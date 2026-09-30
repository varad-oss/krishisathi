'use client';

import { AlertTriangle, CircleSlash, Clock, History, Info, RefreshCw, Settings2, Timer, WifiOff } from 'lucide-react';
import { ApiError, codeForStatus } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import type { InsightSeverity, Level } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';

const press = 'transition-[background-color,border-color,color,transform] duration-150 active:scale-[0.98] active:translate-y-px';

/** Buttons are 48px tall by default: comfortable for thumbs, gloves and cheap touchscreens. */
export const buttonClass = {
  primary: cn(
    'inline-flex min-h-12 items-center justify-center gap-2 rounded-[var(--radius-inner)] bg-leaf-600 px-5 py-2.5 text-[0.95rem] font-semibold text-white hover:bg-leaf-700 disabled:cursor-not-allowed disabled:bg-line-strong disabled:text-ink-soft',
    press,
  ),
  secondary: cn(
    'inline-flex min-h-12 items-center justify-center gap-2 rounded-[var(--radius-inner)] border border-line-strong bg-surface px-5 py-2.5 text-[0.95rem] font-semibold text-ink hover:border-ink-soft disabled:cursor-not-allowed disabled:opacity-60',
    press,
  ),
  ghost: cn('inline-flex min-h-11 items-center justify-center gap-2 rounded-[var(--radius-inner)] px-3 py-2 text-[0.95rem] font-semibold text-leaf-700 hover:bg-leaf-50', press),
};

/** Inline text action ("See all", "Change"): underlined so it reads as a link in bright light. */
export const linkClass = 'inline-flex min-h-11 items-center gap-1 font-semibold text-leaf-700 underline decoration-leaf-200 decoration-2 underline-offset-4 hover:decoration-leaf-600';

export const inputClass =
  'block w-full min-h-12 rounded-[var(--radius-inner)] border border-line-strong bg-surface px-3.5 py-2 text-base text-ink placeholder:text-ink-faint transition-colors focus:border-leaf-600 focus:outline-none focus:ring-2 focus:ring-leaf-200';

/** A contained surface. Use only when the grouping needs its own edge; most content sits in a Section. */
export function Card({ className, children, as: Tag = 'section', ...rest }: React.HTMLAttributes<HTMLElement> & { as?: 'section' | 'div' | 'article' }) {
  return (
    <Tag className={cn('rounded-[var(--radius-card)] border border-line bg-surface p-5 sm:p-6', className)} {...rest}>
      {children}
    </Tag>
  );
}

export function CardTitle({
  icon: Icon,
  children,
  action,
  id,
  description,
}: {
  icon?: React.ElementType;
  children: React.ReactNode;
  action?: React.ReactNode;
  id?: string;
  description?: React.ReactNode;
}) {
  return (
    <div className="mb-5 flex items-start justify-between gap-3">
      {/* Long single words in Indic scripts must wrap rather than widen the card on small phones. */}
      <div className="min-w-0 [overflow-wrap:anywhere]">
        <h2 id={id} className="flex items-center gap-2 font-display text-lg leading-snug text-ink sm:text-xl">
          {Icon && <Icon className="h-[1.1rem] w-[1.1rem] shrink-0 text-ink-faint" aria-hidden />}
          {children}
        </h2>
        {description && <p className="mt-1 text-sm text-ink-soft">{description}</p>}
      </div>
      {action}
    </div>
  );
}

/** Page heading shared by every page so they read as one product. */
export function PageHeader({ eyebrow, title, subtitle, children }: { eyebrow?: React.ReactNode; title: React.ReactNode; subtitle?: React.ReactNode; children?: React.ReactNode }) {
  return (
    <header className="mb-8 flex flex-col gap-4 sm:mb-10 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0 [overflow-wrap:anywhere]">
        {eyebrow && <p className="mb-2 text-sm font-medium text-ink-soft">{eyebrow}</p>}
        <h1 className="font-display text-[1.85rem] leading-[1.15] text-ink sm:text-[2.5rem]">{title}</h1>
        {subtitle && <p className="mt-3 max-w-[60ch] text-[1.05rem] text-ink-soft">{subtitle}</p>}
      </div>
      {children}
    </header>
  );
}

/**
 * A titled band of a page. On wide screens the heading sits in its own column and stays in view while its
 * content scrolls, so long pages read like a report instead of a stack of cards.
 */
export function Section({
  id,
  title,
  eyebrow,
  description,
  action,
  children,
  className,
}: {
  id: string;
  title: React.ReactNode;
  eyebrow?: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section id={id} aria-labelledby={`${id}-title`} className={cn('scroll-mt-header border-t border-line py-9 sm:py-12 lg:grid lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-12 xl:grid-cols-[16rem_minmax(0,1fr)]', className)}>
      <header className="mb-6 min-w-0 [overflow-wrap:anywhere] lg:sticky lg:top-[calc(var(--header-h)+4.5rem)] lg:mb-0 lg:self-start">
        {eyebrow && <p className="mb-1.5 text-sm font-medium text-ink-faint">{eyebrow}</p>}
        <h2 id={`${id}-title`} className="font-display text-[1.4rem] leading-tight text-ink sm:text-2xl">
          {title}
        </h2>
        {description && <p className="mt-2 max-w-[48ch] text-sm text-ink-soft">{description}</p>}
        {action && <div className="mt-3">{action}</div>}
      </header>
      <div className="min-w-0">{children}</div>
    </section>
  );
}

/** A small heading inside a section: sentence case, no decoration. */
export function SubHeading({ children, id, className }: { children: React.ReactNode; id?: string; className?: string }) {
  return (
    <h3 id={id} className={cn('mb-3 text-[0.95rem] font-semibold text-ink', className)}>
      {children}
    </h3>
  );
}

/** "Do this": the one action a block leads to, set apart so it can be found at a glance. */
export function ActionBlock({ label, children, className, lang }: { label: React.ReactNode; children: React.ReactNode; className?: string; lang?: string }) {
  return (
    <div className={cn('rounded-[var(--radius-inner)] border-l-4 border-leaf-600 bg-leaf-50 px-4 py-3.5 sm:px-5 sm:py-4', className)}>
      <p className="text-sm font-semibold text-leaf-700">{label}</p>
      <p className="mt-1 text-[1.1rem] font-medium leading-snug text-ink sm:text-[1.2rem]" lang={lang}>
        {children}
      </p>
    </div>
  );
}

/** One piece of supporting evidence: what was measured, and what it says. */
export function EvidenceRow({
  icon: Icon,
  tone = 'ink',
  label,
  value,
  detail,
  tag,
}: {
  icon: React.ElementType;
  tone?: 'ink' | 'sky' | 'soil' | 'leaf' | 'watch';
  label: React.ReactNode;
  value: React.ReactNode;
  detail?: React.ReactNode;
  tag?: React.ReactNode;
}) {
  const toneClass = { ink: 'text-ink-soft', sky: 'text-sky-600', soil: 'text-soil-500', leaf: 'text-leaf-600', watch: 'text-watch-700' }[tone];
  return (
    <li className="flex items-start gap-3 py-3.5">
      <Icon className={cn('mt-0.5 h-5 w-5 shrink-0', toneClass)} aria-hidden />
      <div className="min-w-0 flex-1 [overflow-wrap:anywhere]">
        <p className="text-sm text-ink-soft">{label}</p>
        <div className="mt-0.5 font-semibold text-ink">{value}</div>
        {detail && <div className="mt-0.5 text-sm text-ink-soft">{detail}</div>}
      </div>
      {tag && <div className="shrink-0 text-xs">{tag}</div>}
    </li>
  );
}

const RISK_FILL: Record<string, string> = { low: 'bg-leaf-500', moderate: 'bg-watch-500', medium: 'bg-watch-500', high: 'bg-warn-500' };
const RISK_TEXT: Record<string, string> = { low: 'text-leaf-700', moderate: 'text-watch-700', medium: 'text-watch-700', high: 'text-warn-700' };

/**
 * Risk level as a coloured three-step bar with its word. Colour is reserved for risk; evidence strength is drawn
 * in neutral ink (StrengthDots) so the two are never read as the same scale.
 */
export function RiskLevel({ level, className }: { level: Level | 'unavailable'; className?: string }) {
  const { t } = useI18n();
  if (level === 'unavailable') {
    return (
      <span className={cn('inline-flex items-center gap-2 text-sm font-semibold text-ink-soft', className)}>
        <span aria-hidden className="flex gap-0.5">
          {[0, 1, 2].map((i) => <span key={i} className="h-2 w-4 rounded-sm border border-dashed border-line-strong" />)}
        </span>
        {t('state.unavailable')}
      </span>
    );
  }
  const filled = level === 'high' ? 3 : level === 'moderate' ? 2 : 1;
  return (
    <span className={cn('inline-flex items-center gap-2 text-sm font-semibold', RISK_TEXT[level], className)}>
      <span aria-hidden className="flex gap-0.5">
        {[0, 1, 2].map((i) => <span key={i} className={cn('h-2 w-4 rounded-sm', i < filled ? RISK_FILL[level] : 'bg-paper-deep')} />)}
      </span>
      {t('risk.level', { level: t(`level.${level}` as MessageKey) })}
    </span>
  );
}

/** How strong the evidence is: hollow-to-filled neutral dots, deliberately unlike the risk bar. */
export function StrengthDots({ level, className }: { level: Level; className?: string }) {
  const filled = level === 'high' ? 3 : level === 'moderate' ? 2 : 1;
  return (
    <span aria-hidden className={cn('inline-flex gap-1', className)}>
      {[0, 1, 2].map((i) => (
        <span key={i} className={cn('h-2.5 w-2.5 rounded-full border-2 border-ink-soft', i < filled ? 'bg-ink-soft' : 'bg-transparent')} />
      ))}
    </span>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden className={cn('animate-pulse rounded-md bg-paper-deep', className)} />;
}

/** Loading with a sentence about what is being fetched, above a skeleton of the content's shape. */
export function LoadingBlock({ lines = 3, className, label }: { lines?: number; className?: string; label?: string }) {
  const { t } = useI18n();
  return (
    <div role="status" aria-live="polite" className={cn('space-y-3', className)}>
      {label ? <p className="text-sm text-ink-soft">{label}</p> : <span className="sr-only">{t('state.loading')}</span>}
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton key={i} className={cn('h-4', i === 0 ? 'w-2/3' : i % 2 ? 'w-full' : 'w-5/6')} />
      ))}
    </div>
  );
}

/** Nothing here yet: say why, and what will fill it. */
export function EmptyState({ icon: Icon = Info, title, children, action, className }: { icon?: React.ElementType; title?: React.ReactNode; children: React.ReactNode; action?: React.ReactNode; className?: string }) {
  return (
    <div className={cn('flex items-start gap-3 rounded-[var(--radius-inner)] border border-line bg-paper/60 p-4 text-sm sm:p-5', className)}>
      <Icon className="mt-0.5 h-5 w-5 shrink-0 text-ink-faint" aria-hidden />
      <div className="min-w-0 flex-1 text-ink-soft">
        {title && <p className="mb-0.5 font-semibold text-ink">{title}</p>}
        {children}
        {action && <div className="mt-3">{action}</div>}
      </div>
    </div>
  );
}

/** Marks data shown from this device's saved copy, so it never looks like a fresh reading. */
export function SavedCopyTag({ time, className }: { time: number; className?: string }) {
  const { t, fmt } = useI18n();
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-[var(--radius-tag)] border border-dashed border-sky-600/50 bg-sky-50 px-2 py-0.5 text-xs font-semibold text-sky-700', className)}>
      <History className="h-3.5 w-3.5" aria-hidden />
      {t('offline.savedTag', { time: fmt.relative(time) })}
    </span>
  );
}

const severityStyles: Record<string, string> = {
  info: 'bg-sky-50 text-sky-700',
  watch: 'bg-watch-50 text-watch-700',
  warning: 'bg-warn-50 text-warn-700',
  low: 'bg-leaf-50 text-leaf-700',
  moderate: 'bg-watch-50 text-watch-700',
  medium: 'bg-watch-50 text-watch-700',
  high: 'bg-warn-50 text-warn-700',
  critical: 'bg-warn-50 text-warn-700',
};

export const severityDot: Record<string, string> = {
  info: 'bg-sky-600',
  watch: 'bg-watch-500',
  warning: 'bg-warn-500',
  critical: 'bg-warn-500',
  low: 'bg-leaf-500',
  moderate: 'bg-watch-500',
  medium: 'bg-watch-500',
  high: 'bg-warn-500',
};

const badge = 'inline-flex items-center gap-1.5 rounded-[var(--radius-tag)] px-2 py-0.5 text-xs font-semibold';

export function SeverityBadge({ severity, className }: { severity: InsightSeverity | 'critical'; className?: string }) {
  const { t } = useI18n();
  return (
    <span className={cn(badge, severityStyles[severity], className)}>
      <span aria-hidden className={cn('h-1.5 w-1.5 rounded-full', severityDot[severity])} />
      {t(`severity.${severity}` as MessageKey)}
    </span>
  );
}

export function LevelBadge({ level, label, className }: { level: Level | 'medium'; label?: string; className?: string }) {
  const { t } = useI18n();
  return (
    <span className={cn(badge, severityStyles[level], className)}>
      <span aria-hidden className={cn('h-1.5 w-1.5 rounded-full', severityDot[level])} />
      {label ? `${label}: ` : ''}
      {t(`level.${level}` as MessageKey)}
    </span>
  );
}

/** User-facing explanation for an error: its own code, else its HTTP status family, else generic. */
export function errorMessage(t: (k: MessageKey) => string, error: ApiError): string {
  const text = (code: string) => {
    const key = `error.${code}` as MessageKey;
    const value = t(key);
    return value === key ? null : value;
  };
  return text(error.code) ?? (error.status ? text(codeForStatus(error.status)) : null) ?? t('error.generic');
}

const ERROR_LOOK: Record<string, { icon: React.ElementType; tone: string; iconTone: string }> = {
  OFFLINE: { icon: WifiOff, tone: 'bg-sky-50 border-sky-100', iconTone: 'text-sky-700' },
  NETWORK_ERROR: { icon: WifiOff, tone: 'bg-sky-50 border-sky-100', iconTone: 'text-sky-700' },
  CONFIG_ERROR: { icon: Settings2, tone: 'bg-paper border-line-strong', iconTone: 'text-ink-soft' },
  RATE_LIMITED: { icon: Clock, tone: 'bg-watch-50 border-watch-200', iconTone: 'text-watch-700' },
  TIMEOUT: { icon: Timer, tone: 'bg-watch-50 border-watch-200', iconTone: 'text-watch-700' },
};
const DEFAULT_LOOK = { icon: AlertTriangle, tone: 'bg-watch-50 border-watch-200', iconTone: 'text-watch-700' };

/**
 * Explicit failure state for one panel: what happened (title), why (message for the error code), what to
 * do (retry), and when data was last good. Keeps the layout; never shows placeholder data.
 */
export function ErrorState({
  error,
  onRetry,
  title,
  updatedAt,
  compact,
}: {
  error: ApiError;
  onRetry?: () => void;
  title?: string;
  updatedAt?: number | null;
  compact?: boolean;
}) {
  const { t, fmt } = useI18n();
  const look = ERROR_LOOK[error.code] ?? DEFAULT_LOOK;
  const Icon = look.icon;
  return (
    <div role="alert" className={cn('rounded-[var(--radius-inner)] border text-ink', look.tone, compact ? 'mb-4 p-3' : 'p-4 sm:p-5')}>
      <div className="flex items-start gap-3">
        <Icon className={cn('mt-0.5 h-5 w-5 shrink-0', look.iconTone)} aria-hidden />
        <div className="min-w-0 flex-1">
          {title && <p className="font-semibold leading-snug">{title}</p>}
          <p className={cn('text-sm text-ink-soft', title && 'mt-0.5')}>{errorMessage(t, error)}</p>
          {(onRetry && error.retryable) || updatedAt || error.requestId ? (
            <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2">
              {onRetry && error.retryable && (
                <button type="button" onClick={onRetry} className={cn(buttonClass.secondary, 'min-h-11 px-4 py-1.5')}>
                  <RefreshCw className="h-4 w-4" aria-hidden />
                  {t('action.retry')}
                </button>
              )}
              {updatedAt && <span className="text-xs text-ink-soft">{t('state.lastUpdated', { time: fmt.relative(updatedAt) })}</span>}
              {error.requestId && <span className="text-xs text-ink-faint">{t('error.reference', { id: error.requestId.slice(0, 8) })}</span>}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

/** A data source that is honestly absent (not configured / no data), as opposed to a transient error. */
export function UnavailableNote({ children, className, action }: { children: React.ReactNode; className?: string; action?: React.ReactNode }) {
  return <EmptyState icon={CircleSlash} className={cn('border-dashed border-line-strong', className)} action={action}>{children}</EmptyState>;
}

export function Note({ children, className, tone = 'info' }: { children: React.ReactNode; className?: string; tone?: 'info' | 'watch' | 'warning' }) {
  const Icon = tone === 'info' ? Info : AlertTriangle;
  return (
    <div className={cn('flex items-start gap-3 rounded-[var(--radius-inner)] p-3.5 text-sm', severityStyles[tone], className)}>
      <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
      <div className="min-w-0 text-ink">{children}</div>
    </div>
  );
}

const KIND_KEYS: Record<string, MessageKey> = {
  model: 'kind.model',
  forecast: 'kind.forecast',
  satellite_observation: 'kind.satellite_observation',
  ai_model: 'kind.ai_model',
  ai_generated_summary: 'kind.ai_generated_summary',
  ai_classified_user_reports: 'kind.ai_classified_user_reports',
  curated_reference: 'kind.curated_reference',
  static_reference: 'kind.static_reference',
  rule: 'kind.rule',
  authenticated_submissions: 'kind.authenticated_submissions',
};

/** What kind of data this is (forecast, model estimate, AI…). Outlined, never filled, so it reads as a label. */
export function KindTag({ kind, className }: { kind: string; className?: string }) {
  const { t } = useI18n();
  if (!KIND_KEYS[kind]) return null;
  return <span className={cn('inline-block max-w-full rounded-[var(--radius-tag)] border border-line-strong px-1.5 py-px font-medium text-ink-soft', className)}>{t(KIND_KEYS[kind])}</span>;
}

/**
 * "Where this comes from": source, data kind and freshness on one quiet line; coverage and limitations
 * behind "About this data" so they are available without cluttering the panel.
 */
export function ProvenanceLine({
  source,
  url,
  kind,
  time,
  note,
  className,
}: {
  source: string;
  url?: string | null;
  kind?: string;
  time?: string | number | null;
  note?: React.ReactNode;
  className?: string;
}) {
  const { t, fmt } = useI18n();
  return (
    <div className={cn('mt-6 border-t border-line pt-3 text-xs text-ink-soft', className)}>
      <p className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <span className="font-semibold text-ink-soft">{t('provenance.source')}:</span>
        {url ? (
          <a href={url} target="_blank" rel="noopener noreferrer" lang="en" className="underline decoration-line-strong underline-offset-2 hover:text-leaf-700">
            {source}
          </a>
        ) : (
          <span lang="en">{source}</span>
        )}
        {kind && <KindTag kind={kind} />}
        {time && <span>· {t('state.updated', { time: fmt.relative(time) })}</span>}
      </p>
      {note && (
        <details className="group mt-1">
          <summary className="inline-flex min-h-10 cursor-pointer list-none items-center gap-1 font-medium text-ink-soft hover:text-leaf-700">
            {t('provenance.about')}
            <span aria-hidden className="transition-transform group-open:rotate-180">▾</span>
          </summary>
          <div className="max-w-[70ch] pb-1 leading-relaxed">{note}</div>
        </details>
      )}
    </div>
  );
}
