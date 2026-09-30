'use client';

import dynamic from 'next/dynamic';
import { useState } from 'react';
import { Eraser, PenLine, Shapes, Trash2, Undo2 } from 'lucide-react';
import { ApiError, deletePlot, savePlot } from '@/lib/api';
import { areaHa, fromPolygon, outlineProblem, toPolygon, type Position } from '@/lib/geo';
import { useI18n } from '@/lib/i18n';
import type { Resource } from '@/lib/use-resource';
import type { FarmPlot, FarmTwin } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { buttonClass, ErrorState, Skeleton } from '../ui';

const PlotMap = dynamic(() => import('./PlotMap'), { ssr: false, loading: () => <Skeleton className="h-72 sm:h-96" /> });

function Editor({ twin, center, initial, onSaved, onCancel }: { twin: FarmTwin; center: { lat: number; lng: number }; initial: Position[]; onSaved: () => void; onCancel: () => void }) {
  const { t, fmt } = useI18n();
  const [points, setPoints] = useState<Position[]>(initial);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const problem = outlineProblem(points);
  const area = areaHa(points);

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
    <div className="space-y-3" data-testid="plot-editor">
      <p className="text-sm text-ink-soft">{t('farm.plot.drawHelp')}</p>
      <PlotMap center={center} points={points} onAdd={(p) => setPoints((ps) => [...ps, p])} label={t('farm.plot.mapLabel')} />
      <p className="text-sm" aria-live="polite">
        {points.length >= 3 ? (
          <span className="font-semibold tabular-nums" data-testid="plot-area">{t('farm.plot.area', { area: fmt.num(area, area < 1 ? 2 : 1) })}</span>
        ) : (
          <span className="text-ink-soft">{t('farm.plot.corners', { count: fmt.num(points.length, 0) })}</span>
        )}
        {problem && problem !== 'too_few_points' && <span className="block text-warn-700">{t(`farm.plot.problem.${problem}` as MessageKey)}</span>}
      </p>
      {error && <ErrorState compact error={error} title={t('farm.plot.saveFailed')} />}
      <div className="flex flex-wrap gap-2">
        <button type="button" onClick={save} disabled={!!problem || saving} className={cn(buttonClass.primary, 'min-h-11 px-4')}>
          {saving ? t('state.loading') : t('action.save')}
        </button>
        <button type="button" onClick={() => setPoints((ps) => ps.slice(0, -1))} disabled={!points.length} className={cn(buttonClass.secondary, 'min-h-11 px-3')}>
          <Undo2 className="h-4 w-4" aria-hidden /> {t('farm.plot.undo')}
        </button>
        <button type="button" onClick={() => setPoints([])} disabled={!points.length} className={cn(buttonClass.secondary, 'min-h-11 px-3')}>
          <Eraser className="h-4 w-4" aria-hidden /> {t('farm.plot.clear')}
        </button>
        <button type="button" onClick={onCancel} className={cn(buttonClass.ghost, 'min-h-11 px-3')}>
          {t('action.cancel')}
        </button>
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

  if (!twin) return <p className="text-sm text-ink-soft">{t('farm.plot.needsRecord')}</p>;
  if (plot.status === 'loading' && !plot.data) return <Skeleton className="h-10 w-2/3" />;

  if (editing) {
    return (
      <Editor
        twin={twin}
        center={center}
        initial={fromPolygon(current?.geometry as { coordinates: Position[][] } | undefined)}
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
    <div className="rounded-[var(--radius-inner)] bg-paper/70 p-3 text-sm" data-testid="field-outline">
      <p className="flex items-center gap-1.5 font-semibold">
        <Shapes className="h-4 w-4 text-leaf-600" aria-hidden /> {t('farm.plot.title')}
      </p>
      {current ? (
        <p className="mt-1 tabular-nums" data-testid="plot-summary">{t('farm.plot.saved', { area: fmt.num(current.area_ha, current.area_ha < 1 ? 2 : 1) })}</p>
      ) : (
        <p className="mt-1 text-ink-soft">{t('farm.plot.none')}</p>
      )}
      <p className="mt-1 text-xs text-ink-faint">{t('farm.plot.why')}</p>
      {plot.status === 'error' && <ErrorState compact error={plot.error} onRetry={plot.reload} />}
      {error && <ErrorState compact error={error} title={t('farm.plot.removeFailed')} />}
      <div className="mt-2 flex flex-wrap gap-2">
        <button type="button" onClick={() => setEditing(true)} className={cn(buttonClass.secondary, 'min-h-10 px-3')}>
          <PenLine className="h-4 w-4" aria-hidden /> {current ? t('farm.plot.edit') : t('farm.plot.define')}
        </button>
        {current &&
          (confirming ? (
            <>
              <button type="button" onClick={remove} className={cn(buttonClass.secondary, 'min-h-10 px-3 text-warn-700')}>
                {t('farm.plot.confirmRemove')}
              </button>
              <button type="button" onClick={() => setConfirming(false)} className={cn(buttonClass.ghost, 'min-h-10 px-3')}>
                {t('action.cancel')}
              </button>
            </>
          ) : (
            <button type="button" onClick={() => setConfirming(true)} className={cn(buttonClass.ghost, 'min-h-10 px-3')}>
              <Trash2 className="h-4 w-4" aria-hidden /> {t('farm.plot.remove')}
            </button>
          ))}
      </div>
    </div>
  );
}
