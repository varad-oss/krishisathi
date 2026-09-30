'use client';

import dynamic from 'next/dynamic';
import { useEffect, useId, useRef, useState } from 'react';
import { Check, Eraser, Loader2, PenLine, Shapes, Trash2, Undo2, X } from 'lucide-react';
import { ApiError, deletePlot, savePlot } from '@/lib/api';
import { areaHa, fromPolygon, outlineProblem, outlinePath, toPolygon, type Position } from '@/lib/geo';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { FarmPlot, FarmTwin } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { buttonClass, ErrorState, Skeleton, UnavailableNote } from '../ui';

const PlotMap = dynamic(() => import('./PlotMap'), { ssr: false, loading: () => <Skeleton className="h-full min-h-72 rounded-none" /> });

/** The saved outline drawn to scale, without map tiles: instant, free on data, and recognisable. */
function ShapePreview({ points, className }: { points: Position[]; className?: string }) {
  return (
    <svg viewBox="0 0 64 64" className={cn('shrink-0 rounded-[var(--radius-inner)] border border-leaf-200 bg-leaf-50', className)} aria-hidden>
      <path d={outlinePath(points)} className="fill-leaf-200 stroke-leaf-600" strokeWidth="2" strokeLinejoin="round" />
    </svg>
  );
}

/**
 * Draw → preview → see area → save. On phones the map takes the whole screen with one compact action bar at the
 * bottom (nothing covers the map); on larger screens it opens in place.
 */
function Editor({ twin, center, initial, onSaved, onCancel }: { twin: FarmTwin; center: { lat: number; lng: number }; initial: Position[]; onSaved: () => void; onCancel: () => void }) {
  const { t, fmt } = useI18n();
  const [points, setPoints] = useState<Position[]>(initial);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const problem = outlineProblem(points);
  const area = areaHa(points);
  const titleId = useId();
  const heading = useRef<HTMLHeadingElement>(null);

  // Full-screen on phones: keep the page behind still, start focus on the title, and let Escape leave.
  useEffect(() => {
    heading.current?.focus();
    const phone = window.matchMedia('(max-width: 767px)').matches;
    const previous = document.body.style.overflow;
    if (phone) document.body.style.overflow = 'hidden';
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onCancel();
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = previous;
      window.removeEventListener('keydown', onKey);
    };
  }, [onCancel]);

  const save = async () => {
    setSaving(true);
    setError(null);
    try {
      await savePlot(twin, toPolygon(points));
      onSaved();
    } catch (e) {
      setError(e instanceof ApiError ? e : new ApiError('Could not save.', 'UNKNOWN', null, true));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-labelledby={titleId}
      className="fixed inset-0 z-50 flex flex-col bg-surface md:static md:z-auto md:overflow-hidden md:rounded-[var(--radius-card)] md:border md:border-line"
      data-testid="plot-editor"
    >
      <div className="flex items-start justify-between gap-3 border-b border-line px-4 py-3">
        <div className="min-w-0">
          <h3 id={titleId} ref={heading} tabIndex={-1} className="font-display text-lg focus:outline-none">{t('farm.plot.title')}</h3>
          <p className="text-sm text-ink-soft">{t('farm.plot.drawHelp')}</p>
        </div>
        <button type="button" onClick={onCancel} className={cn(buttonClass.ghost, 'shrink-0 px-2 text-ink-soft')}>
          <X className="h-5 w-5" aria-hidden /> {t('action.cancel')}
        </button>
      </div>

      <PlotMap center={center} points={points} onAdd={(p) => setPoints((ps) => [...ps, p])} label={t('farm.plot.mapLabel')} className="h-auto min-h-0 flex-1 sm:h-auto md:h-[26rem] md:flex-none" />

      <div className="border-t border-line bg-surface px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3">
        <div aria-live="polite" className="min-h-12">
          {points.length >= 3 ? (
            <p className="font-display text-xl tabular-nums" data-testid="plot-area">{t('farm.plot.area', { area: fmt.num(area, area < 1 ? 2 : 1) })}</p>
          ) : (
            <p className="text-ink-soft">{t('farm.plot.corners', { count: fmt.num(points.length, 0) })}</p>
          )}
          {problem && problem !== 'too_few_points' && <p className="text-sm font-medium text-warn-700">{t(`farm.plot.problem.${problem}` as MessageKey)}</p>}
        </div>
        {error && <ErrorState compact error={error} title={t('farm.plot.saveFailed')} />}
        <div className="mt-2 grid grid-cols-[auto_auto_1fr] gap-2 md:flex md:flex-wrap">
          <button type="button" onClick={() => setPoints((ps) => ps.slice(0, -1))} disabled={!points.length} className={cn(buttonClass.secondary, 'px-3.5')}>
            <Undo2 className="h-5 w-5" aria-hidden /> {t('farm.plot.undo')}
          </button>
          <button type="button" onClick={() => setPoints([])} disabled={!points.length} className={cn(buttonClass.secondary, 'px-3.5')}>
            <Eraser className="h-5 w-5" aria-hidden /> {t('farm.plot.clear')}
          </button>
          <button type="button" onClick={save} disabled={!!problem || saving} className={cn(buttonClass.primary, 'md:min-w-40')}>
            {saving ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden /> : <Check className="h-5 w-5" aria-hidden />}
            {saving ? t('state.loading') : t('action.save')}
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * "My field": an optional outline that makes satellite values specific to the farmer's own field. Skipping it is
 * fine: the page then uses the area around the farm location. Nothing personal is asked for.
 */
export function FieldOutline({ twin, center, plot, onChanged }: { twin: FarmTwin | null; center: { lat: number; lng: number }; plot: Resource<{ plot: FarmPlot | null }>; onChanged: () => void }) {
  const { t, fmt } = useI18n();
  const [editing, setEditing] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const current = plot.data?.plot ?? null;
  const outline = fromPolygon(current?.geometry as { coordinates: Position[][] } | undefined);

  if (!twin) return <UnavailableNote>{t('farm.plot.needsRecord')}</UnavailableNote>;
  if (plot.status === 'loading' && !plot.data) return <Skeleton className="h-24 w-full" />;

  if (editing) {
    return (
      <Editor
        twin={twin}
        center={center}
        initial={outline}
        onCancel={() => setEditing(false)}
        onSaved={() => {
          setEditing(false);
          onChanged();
        }}
      />
    );
  }

  const remove = async () => {
    setError(null);
    try {
      await deletePlot(twin);
      setConfirming(false);
      onChanged();
    } catch (e) {
      setError(e instanceof ApiError ? e : new ApiError('Could not remove.', 'UNKNOWN', null, true));
    }
  };

  return (
    <div className={cn('rounded-[var(--radius-card)] border p-4 sm:p-5', current ? 'border-line bg-surface' : 'border-dashed border-line-strong bg-paper/60')} data-testid="field-outline">
      <div className="flex items-start gap-4">
        {current ? <ShapePreview points={outline} className="h-16 w-16" /> : <Shapes className="mt-0.5 h-7 w-7 shrink-0 text-ink-faint" aria-hidden />}
        <div className="min-w-0 flex-1">
          <p className="font-semibold">{t('farm.plot.title')}</p>
          {current ? (
            <p className="font-display text-xl tabular-nums" data-testid="plot-summary">{t('farm.plot.saved', { area: fmt.num(current.area_ha, current.area_ha < 1 ? 2 : 1) })}</p>
          ) : (
            <p className="text-ink-soft">{t('farm.plot.none')}</p>
          )}
          <p className="mt-1 text-sm text-ink-soft">{t('farm.plot.why')}</p>
        </div>
      </div>
      {plot.status === 'error' && <div className="mt-3"><ErrorState compact error={plot.error} onRetry={plot.reload} /></div>}
      {error && <div className="mt-3"><ErrorState compact error={error} title={t('farm.plot.removeFailed')} /></div>}
      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" onClick={() => setEditing(true)} className={current ? buttonClass.secondary : buttonClass.primary}>
          <PenLine className="h-5 w-5" aria-hidden /> {current ? t('farm.plot.edit') : t('farm.plot.define')}
        </button>
        {current &&
          (confirming ? (
            <>
              <button type="button" onClick={remove} className={cn(buttonClass.secondary, 'border-warn-200 text-warn-700 hover:border-warn-500')}>
                {t('farm.plot.confirmRemove')}
              </button>
              <button type="button" onClick={() => setConfirming(false)} className={buttonClass.ghost}>
                {t('action.cancel')}
              </button>
            </>
          ) : (
            <button type="button" onClick={() => setConfirming(true)} className={cn(buttonClass.ghost, 'text-ink-soft')}>
              <Trash2 className="h-4 w-4" aria-hidden /> {t('farm.plot.remove')}
            </button>
          ))}
      </div>
    </div>
  );
}
