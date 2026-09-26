'use client';

import { AlertTriangle, CircleSlash, Info, RefreshCw, WifiOff } from 'lucide-react';
import { ApiError } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import type { InsightSeverity, Level } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';

export const buttonClass = {
  primary:
    'inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-leaf-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-leaf-700 disabled:cursor-not-allowed disabled:bg-line-strong disabled:text-ink-faint',
  secondary:
    'inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-line-strong bg-surface px-5 py-2.5 text-sm font-semibold text-ink transition-colors hover:border-leaf-500 hover:text-leaf-700 disabled:cursor-not-allowed disabled:opacity-60',
  ghost:
    'inline-flex min-h-11 items-center justify-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold text-leaf-700 transition-colors hover:bg-leaf-50',
};

export const inputClass =
  'block w-full min-h-11 rounded-xl border border-line-strong bg-surface px-3 py-2 text-base text-ink placeholder:text-ink-faint focus:border-leaf-500 focus:outline-none focus:ring-2 focus:ring-leaf-200';

export function Card({ className, children, as: Tag = 'section', ...rest }: React.HTMLAttributes<HTMLElement> & { as?: 'section' | 'div' | 'article' }) {
  return (
    <Tag className={cn('rounded-[var(--radius-card)] border border-line bg-surface p-5 shadow-[var(--shadow-card)] sm:p-6', className)} {...rest}>
      {children}
    </Tag>
  );
}

export function CardTitle({ icon: Icon, children, action, id }: { icon?: React.ElementType; children: React.ReactNode; action?: React.ReactNode; id?: string }) {
  return (
    <div className="mb-4 flex items-start justify-between gap-3">
      <h2 id={id} className="flex items-center gap-2 text-lg font-semibold tracking-tight text-ink">
        {Icon && <Icon className="h-5 w-5 shrink-0 text-leaf-600" aria-hidden />}
        {children}
      </h2>
      {action}
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div aria-hidden className={cn('animate-pulse rounded-lg bg-line/70', className)} />;
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
  info: 'border-sky-100 bg-sky-50 text-sky-700',
  watch: 'border-watch-200 bg-watch-50 text-watch-700',
  warning: 'border-warn-200 bg-warn-50 text-warn-700',
  low: 'border-leaf-100 bg-leaf-50 text-leaf-700',
  moderate: 'border-watch-200 bg-watch-50 text-watch-700',
  medium: 'border-watch-200 bg-watch-50 text-watch-700',
  high: 'border-warn-200 bg-warn-50 text-warn-700',
  critical: 'border-warn-200 bg-warn-50 text-warn-700',
};

export function SeverityBadge({ severity, className }: { severity: InsightSeverity | 'critical'; className?: string }) {
  const { t } = useI18n();
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-semibold', severityStyles[severity], className)}>
      {severity !== 'info' && <AlertTriangle className="h-3.5 w-3.5" aria-hidden />}
      {t(`severity.${severity}` as MessageKey)}
    </span>
  );
}

export function LevelBadge({ level, label, className }: { level: Level | 'medium'; label?: string; className?: string }) {
  const { t } = useI18n();
  return (
    <span className={cn('inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold', severityStyles[level], className)}>
      {label ? `${label}: ` : ''}
      {t(`level.${level}` as MessageKey)}
    </span>
  );
}

export function errorMessage(t: (k: MessageKey) => string, error: ApiError): string {
  if (typeof navigator !== 'undefined' && !navigator.onLine) return t('state.offline');
  const key = `error.${error.code}` as MessageKey;
  const text = t(key);
  return text === key ? t('error.generic') : text;
}

/** Explicit failure state for one panel. Keeps the layout; never shows placeholder data. */
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
  const offline = error.code === 'NETWORK_ERROR';
  const Icon = offline ? WifiOff : AlertTriangle;
  return (
    <div role="alert" className={cn('rounded-xl border border-warn-200 bg-warn-50/60 text-ink', compact ? 'p-3' : 'p-4')}>
      <div className="flex items-start gap-3">
        <Icon className="mt-0.5 h-5 w-5 shrink-0 text-warn-700" aria-hidden />
        <div className="min-w-0 flex-1">
          {title && <p className="font-semibold">{title}</p>}
          <p className="text-sm text-ink-soft">{errorMessage(t, error)}</p>
          {updatedAt && <p className="mt-1 text-xs text-ink-faint">{t('state.lastUpdated', { time: fmt.relative(updatedAt) })}</p>}
          {error.requestId && <p className="mt-1 text-xs text-ink-faint">{t('error.reference', { id: error.requestId.slice(0, 8) })}</p>}
          {onRetry && error.retryable && (
            <button type="button" onClick={onRetry} className={cn(buttonClass.secondary, 'mt-3 min-h-10 px-4 py-1.5')}>
              <RefreshCw className="h-4 w-4" aria-hidden />
              {t('action.retry')}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

/** A data source that is honestly absent (not configured / no data), as opposed to a transient error. */
export function UnavailableNote({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn('flex items-start gap-3 rounded-xl border border-dashed border-line-strong bg-paper p-4 text-sm text-ink-soft', className)}>
      <CircleSlash className="mt-0.5 h-5 w-5 shrink-0 text-ink-faint" aria-hidden />
      <div>{children}</div>
    </div>
  );
}

export function Note({ children, className, tone = 'info' }: { children: React.ReactNode; className?: string; tone?: 'info' | 'watch' | 'warning' }) {
  const Icon = tone === 'info' ? Info : AlertTriangle;
  return (
    <div className={cn('flex items-start gap-3 rounded-xl border p-3 text-sm', severityStyles[tone], className)}>
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

/** Reusable "where this comes from" line: source, data kind, freshness, and an optional note. */
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
    <div className={cn('mt-4 border-t border-line pt-3 text-xs text-ink-faint', className)}>
      <p className="flex flex-wrap items-center gap-x-2 gap-y-1">
        <span className="font-semibold text-ink-soft">{t('provenance.source')}:</span>
        {url ? (
          <a href={url} target="_blank" rel="noopener noreferrer" className="underline decoration-line-strong underline-offset-2 hover:text-leaf-700">
            {source}
          </a>
        ) : (
          <span>{source}</span>
        )}
        {kind && KIND_KEYS[kind] && (
          <span className="rounded-full bg-paper px-2 py-0.5 font-medium text-ink-soft ring-1 ring-line">{t(KIND_KEYS[kind])}</span>
        )}
        {time && <span>· {t('state.updated', { time: fmt.relative(time) })}</span>}
      </p>
      {note && <p className="mt-1 leading-relaxed">{note}</p>}
    </div>
  );
}
