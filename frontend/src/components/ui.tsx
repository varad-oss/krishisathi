'use client';

import { AlertTriangle, CircleSlash, Clock, Info, RefreshCw, Settings2, Timer, WifiOff } from 'lucide-react';
import { ApiError, codeForStatus } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import type { InsightSeverity, Level } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';

const press = 'transition-[background-color,border-color,color,box-shadow,transform] duration-200 active:scale-[0.98]';

export const buttonClass = {
  primary: cn(
    'inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-leaf-600 px-5 py-2.5 text-sm font-semibold text-white shadow-[0_1px_0_rgb(255_255_255/0.15)_inset,0_6px_16px_-8px_rgb(35_82_48/0.6)] hover:bg-leaf-700 disabled:cursor-not-allowed disabled:bg-line-strong disabled:text-ink-faint disabled:shadow-none',
    press,
  ),
  secondary: cn(
    'inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-surface px-5 py-2.5 text-sm font-semibold text-ink ring-1 ring-line-strong hover:text-leaf-700 hover:ring-leaf-500 disabled:cursor-not-allowed disabled:opacity-60',
    press,
  ),
  ghost: cn('inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-leaf-700 hover:bg-leaf-50', press),
};

export const inputClass =
  'block w-full min-h-11 rounded-xl border border-line-strong bg-surface px-3 py-2 text-base text-ink placeholder:text-ink-faint transition-colors focus:border-leaf-500 focus:outline-none focus:ring-2 focus:ring-leaf-200';

export function Card({ className, children, as: Tag = 'section', ...rest }: React.HTMLAttributes<HTMLElement> & { as?: 'section' | 'div' | 'article' }) {
  return (
    <Tag className={cn('rounded-[var(--radius-card)] bg-surface p-5 shadow-[var(--shadow-card)] ring-1 ring-line/80 sm:p-7', className)} {...rest}>
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
      <div className="flex min-w-0 items-start gap-3">
        {Icon && (
          <span aria-hidden className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-leaf-50 text-leaf-700">
            <Icon className="h-[1.1rem] w-[1.1rem]" />
          </span>
        )}
        <div className="min-w-0">
          <h2 id={id} className="font-display text-[1.3rem] font-medium leading-tight text-ink">
            {children}
          </h2>
          {description && <p className="mt-1 text-sm text-ink-soft">{description}</p>}
        </div>
      </div>
      {action}
    </div>
  );
}

/** Page heading shared by the four main pages so they read as one product. */
export function PageHeader({ eyebrow, title, subtitle, children }: { eyebrow?: React.ReactNode; title: React.ReactNode; subtitle?: React.ReactNode; children?: React.ReactNode }) {
  return (
    <header className="mb-6 flex flex-col gap-4 sm:mb-8 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        {eyebrow && <p className="mb-2 text-sm font-medium text-leaf-700">{eyebrow}</p>}
        <h1 className="font-display text-[2rem] font-medium leading-[1.1] text-ink sm:text-[2.5rem]">{title}</h1>
        {subtitle && <p className="mt-2 max-w-[62ch] text-ink-soft">{subtitle}</p>}
      </div>
      {children}
    </header>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden className={cn('animate-pulse rounded-lg bg-paper-deep/80', className)} />;
}

export function LoadingBlock({ lines = 3, className }: { lines?: number; className?: string }) {
  const { t } = useI18n();
  return (
    <div role="status" aria-live="polite" className={cn('space-y-3', className)}>
      <span className="sr-only">{t('state.loading')}</span>
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton key={i} className={cn('h-4', i === 0 ? 'w-2/3' : i % 2 ? 'w-full' : 'w-5/6')} />
      ))}
    </div>
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

export function SeverityBadge({ severity, className }: { severity: InsightSeverity | 'critical'; className?: string }) {
  const { t } = useI18n();
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-semibold', severityStyles[severity], className)}>
      <span aria-hidden className={cn('h-1.5 w-1.5 rounded-full', severityDot[severity])} />
      {t(`severity.${severity}` as MessageKey)}
    </span>
  );
}

export function LevelBadge({ level, label, className }: { level: Level | 'medium'; label?: string; className?: string }) {
  const { t } = useI18n();
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-semibold', severityStyles[level], className)}>
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
  OFFLINE: { icon: WifiOff, tone: 'bg-sky-50/70 ring-sky-100', iconTone: 'text-sky-700' },
  NETWORK_ERROR: { icon: WifiOff, tone: 'bg-sky-50/70 ring-sky-100', iconTone: 'text-sky-700' },
  CONFIG_ERROR: { icon: Settings2, tone: 'bg-paper ring-line-strong', iconTone: 'text-ink-soft' },
  RATE_LIMITED: { icon: Clock, tone: 'bg-watch-50/70 ring-watch-200', iconTone: 'text-watch-700' },
  TIMEOUT: { icon: Timer, tone: 'bg-watch-50/70 ring-watch-200', iconTone: 'text-watch-700' },
};
const DEFAULT_LOOK = { icon: AlertTriangle, tone: 'bg-watch-50/70 ring-watch-200', iconTone: 'text-watch-700' };

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
    <div role="alert" className={cn('rounded-[var(--radius-inner)] text-ink ring-1', look.tone, compact ? 'p-3' : 'p-4 sm:p-5')}>
      <div className="flex items-start gap-3">
        <Icon className={cn('mt-0.5 h-5 w-5 shrink-0', look.iconTone)} aria-hidden />
        <div className="min-w-0 flex-1">
          {title && <p className="font-semibold leading-snug">{title}</p>}
          <p className={cn('text-sm text-ink-soft', title && 'mt-0.5')}>{errorMessage(t, error)}</p>
          {(onRetry && error.retryable) || updatedAt || error.requestId ? (
            <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-2">
              {onRetry && error.retryable && (
                <button type="button" onClick={onRetry} className={cn(buttonClass.secondary, 'min-h-10 px-4 py-1.5')}>
                  <RefreshCw className="h-4 w-4" aria-hidden />
                  {t('action.retry')}
                </button>
              )}
              {updatedAt && <span className="text-xs text-ink-faint">{t('state.lastUpdated', { time: fmt.relative(updatedAt) })}</span>}
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
  return (
    <div className={cn('flex items-start gap-3 rounded-[var(--radius-inner)] border border-dashed border-line-strong bg-paper/70 p-4 text-sm text-ink-soft', className)}>
      <CircleSlash className="mt-0.5 h-5 w-5 shrink-0 text-ink-faint" aria-hidden />
      <div className="min-w-0 flex-1">
        {children}
        {action && <div className="mt-3">{action}</div>}
      </div>
    </div>
  );
}

export function Note({ children, className, tone = 'info' }: { children: React.ReactNode; className?: string; tone?: 'info' | 'watch' | 'warning' }) {
  const Icon = tone === 'info' ? Info : AlertTriangle;
  return (
    <div className={cn('flex items-start gap-3 rounded-[var(--radius-inner)] p-3 text-sm', severityStyles[tone], className)}>
      <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
      <div className="text-ink">{children}</div>
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

export function KindTag({ kind, className }: { kind: string; className?: string }) {
  const { t } = useI18n();
  if (!KIND_KEYS[kind]) return null;
  return <span className={cn('rounded-md bg-paper-deep/70 px-1.5 py-0.5 font-medium text-ink-soft', className)}>{t(KIND_KEYS[kind])}</span>;
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
    <div className={cn('mt-6 border-t border-dashed border-line pt-3 text-xs text-ink-faint', className)}>
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
        <details className="group mt-1.5">
          <summary className="inline-flex min-h-8 cursor-pointer list-none items-center gap-1 font-medium text-ink-soft hover:text-leaf-700">
            {t('provenance.about')}
            <span aria-hidden className="transition-transform group-open:rotate-180">▾</span>
          </summary>
          <div className="max-w-[70ch] pb-1 leading-relaxed">{note}</div>
        </details>
      )}
    </div>
  );
}
