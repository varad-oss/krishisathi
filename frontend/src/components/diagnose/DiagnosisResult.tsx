'use client';

import { AlertTriangle, BookOpenCheck, CheckCircle2, CircleHelp, Eye, FlaskConical, ImageOff, Leaf, ShieldCheck, Share2, Timer, Volume2, VolumeX } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useI18n } from '@/lib/i18n';
import { onSpeechStateChange, speakText, stopSpeaking } from '@/lib/speech';
import type { DiagnosisResponse } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { buttonClass, Card, LevelBadge, Note } from '../ui';

function StepList({ icon: Icon, title, items, tone }: { icon: React.ElementType; title: string; items: string[]; tone: string }) {
  if (!items.length) return null;
  return (
    <div className={cn('rounded-xl border p-4', tone)}>
      <h4 className="mb-2 flex items-center gap-2 font-semibold">
        <Icon className="h-4 w-4" aria-hidden /> {title}
      </h4>
      <ul className="list-disc space-y-1 pl-5 text-sm text-ink">
        {items.map((s, i) => (
          <li key={i}>{s}</li>
        ))}
      </ul>
    </div>
  );
}

export default function DiagnosisResult({ result, previewUrl, onReset }: { result: DiagnosisResponse; previewUrl: string | null; onReset: () => void }) {
  const { t, language } = useI18n();
  const [speaking, setSpeaking] = useState(false);
  useEffect(() => onSpeechStateChange((s) => !s && setSpeaking(false)), []);
  const r = result;
  const detected = r.status === 'disease_detected';
  const lowCertainty = r.certainty === 'low' || r.status === 'uncertain';

  const heading =
    r.status === 'disease_detected' && r.disease_name
      ? t('diagnose.result.possible', { disease: r.disease_name })
      : r.status === 'healthy'
        ? t('diagnose.result.healthy')
        : r.status === 'not_a_plant'
          ? t('diagnose.result.notPlant')
          : t('diagnose.result.uncertain');
  const HeadingIcon = r.status === 'healthy' ? CheckCircle2 : r.status === 'not_a_plant' ? ImageOff : r.status === 'uncertain' ? CircleHelp : AlertTriangle;

  const readAloud = () => {
    if (speaking) return stopSpeaking();
    setSpeaking(true);
    speakText([heading, r.summary, ...r.treatment.immediate].join('. '), language);
  };

  const share = () => {
    const text = t('diagnose.result.shareText', { result: heading, certainty: t(`level.${r.certainty}` as MessageKey) });
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="space-y-5 animate-rise">
      <Card aria-labelledby="result-title">
        <div className="flex flex-col gap-4 sm:flex-row">
          {previewUrl && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={previewUrl} alt={t('diagnose.upload.preview')} className="h-32 w-full rounded-xl object-cover sm:h-28 sm:w-28" />
          )}
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold uppercase tracking-wide text-ink-faint">{t('diagnose.result.title')} · {t('kind.ai_model')}</p>
            <h2 id="result-title" className="mt-1 flex items-start gap-2 text-2xl font-semibold tracking-tight">
              <HeadingIcon className={cn('mt-1 h-6 w-6 shrink-0', r.status === 'healthy' ? 'text-leaf-600' : detected ? 'text-warn-700' : 'text-ink-faint')} aria-hidden />
              <span>{heading}</span>
            </h2>
            {r.scientific_name && <p className="mt-0.5 text-sm italic text-ink-soft">{r.scientific_name}</p>}
            <div className="mt-3 flex flex-wrap gap-2">
              <LevelBadge level={r.certainty} label={t('diagnose.result.certainty')} />
              {r.severity && <LevelBadge level={r.severity} label={t('diagnose.result.severity')} />}
              {r.spread_risk && <LevelBadge level={r.spread_risk} label={t('diagnose.result.spread')} />}
            </div>
          </div>
        </div>

        {r.status === 'healthy' && <p className="mt-4 text-ink-soft">{t('diagnose.result.healthyBody')}</p>}
        {r.status === 'uncertain' && <p className="mt-4 text-ink-soft">{t('diagnose.result.uncertainBody')}</p>}
        {r.status === 'not_a_plant' && <p className="mt-4 text-ink-soft">{t('diagnose.result.notPlantBody')}</p>}

        {lowCertainty && r.status !== 'not_a_plant' && (
          <Note tone="warning" className="mt-4 font-medium">
            {t('diagnose.result.lowWarning')}
          </Note>
        )}
        {r.image_quality === 'poor' && (
          <Note tone="watch" className="mt-3">
            {t('diagnose.result.poorImage')}
          </Note>
        )}

        <details className="mt-4 rounded-xl bg-paper p-3 text-sm">
          <summary className="cursor-pointer font-semibold">{t('diagnose.result.certaintyWhy')}</summary>
          <p className="mt-2 text-ink-soft">{r.certainty_reason}</p>
        </details>

        {r.summary && (
          <div className="mt-4">
            <h3 className="text-sm font-semibold">{t('diagnose.result.summary')}</h3>
            <p className="mt-1 text-ink-soft">{r.summary}</p>
          </div>
        )}

        {detected && (
          <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
            <div className="flex items-start gap-2">
              <Timer className="mt-0.5 h-4 w-4 text-ink-faint" aria-hidden />
              <div>
                <dt className="font-semibold">{t('diagnose.result.urgency')}</dt>
                <dd className="text-ink-soft">{t(`urgency.${r.urgency}` as MessageKey)}</dd>
              </div>
            </div>
            {r.affected_part && (
              <div className="flex items-start gap-2">
                <Leaf className="mt-0.5 h-4 w-4 text-ink-faint" aria-hidden />
                <div>
                  <dt className="font-semibold">{t('diagnose.result.affected')}</dt>
                  <dd className="text-ink-soft">{r.affected_part}</dd>
                </div>
              </div>
            )}
          </dl>
        )}

        {(r.observed_symptoms.length > 0 || r.alternative_causes.length > 0) && (
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {r.observed_symptoms.length > 0 && (
              <div>
                <h3 className="flex items-center gap-2 text-sm font-semibold">
                  <Eye className="h-4 w-4 text-leaf-600" aria-hidden /> {t('diagnose.result.symptoms')}
                </h3>
                <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-ink-soft">
                  {r.observed_symptoms.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
            {r.alternative_causes.length > 0 && (
              <div>
                <h3 className="flex items-center gap-2 text-sm font-semibold">
                  <CircleHelp className="h-4 w-4 text-ink-faint" aria-hidden /> {t('diagnose.result.alternatives')}
                </h3>
                <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-ink-soft">
                  {r.alternative_causes.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="mt-6 flex flex-wrap gap-2">
          <button type="button" onClick={readAloud} className={buttonClass.secondary}>
            {speaking ? <VolumeX className="h-4 w-4" aria-hidden /> : <Volume2 className="h-4 w-4" aria-hidden />}
            {speaking ? t('action.stopReading') : t('action.readAloud')}
          </button>
          <button type="button" onClick={share} className={buttonClass.secondary}>
            <Share2 className="h-4 w-4" aria-hidden /> {t('diagnose.result.share')}
          </button>
          <button type="button" onClick={onReset} className={buttonClass.ghost}>
            {t('diagnose.result.another')}
          </button>
        </div>
      </Card>

      {r.status !== 'not_a_plant' && (
        <Card aria-labelledby="steps-title">
          <h2 id="steps-title" className="mb-4 text-lg font-semibold">{t('diagnose.result.steps')}</h2>
          <div className="grid gap-3 md:grid-cols-2">
            <StepList icon={AlertTriangle} title={t('diagnose.result.immediate')} items={r.treatment.immediate} tone="border-warn-200 bg-warn-50/50" />
            <StepList icon={Leaf} title={t('diagnose.result.organic')} items={r.treatment.organic} tone="border-leaf-100 bg-leaf-50/60" />
            <StepList icon={ShieldCheck} title={t('diagnose.result.prevention')} items={r.treatment.prevention} tone="border-line bg-paper" />
            {detected && (
              <div className="rounded-xl border border-sky-100 bg-sky-50/60 p-4">
                <h4 className="mb-2 flex items-center gap-2 font-semibold">
                  <FlaskConical className="h-4 w-4" aria-hidden /> {t('diagnose.result.chemical')}
                </h4>
                {r.treatment.chemical.length > 0 ? (
                  <>
                    <ul className="list-disc space-y-1 pl-5 text-sm">
                      {r.treatment.chemical.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                    <p className="mt-3 text-sm font-medium text-warn-700">{t('diagnose.result.chemicalWarning')}</p>
                  </>
                ) : (
                  <p className="text-sm text-ink-soft">{t('diagnose.result.noChemical')}</p>
                )}
              </div>
            )}
          </div>
        </Card>
      )}

      {r.reference && (
        <Card aria-labelledby="ref-title" className="border-leaf-200">
          <h2 id="ref-title" className="flex items-center gap-2 text-lg font-semibold">
            <BookOpenCheck className="h-5 w-5 text-leaf-600" aria-hidden /> {t('diagnose.result.reference')}
          </h2>
          <p className="mt-1 text-sm text-ink-soft">{t('diagnose.result.referenceBody')}</p>
          <div lang="en" className="mt-4 space-y-3 text-sm">
            <p className="font-semibold">
              {r.reference.name} {r.reference.scientific_name && <span className="font-normal italic text-ink-soft">({r.reference.scientific_name})</span>}
            </p>
            <div>
              <p className="font-semibold">{t('diagnose.result.referenceSymptoms')}</p>
              <p className="text-ink-soft">{r.reference.symptoms}</p>
            </div>
            <div>
              <p className="font-semibold">{t('diagnose.result.referenceManagement')}</p>
              <p className="text-ink-soft">{r.reference.treatment}</p>
            </div>
            <ul className="text-xs text-ink-faint">
              {r.reference.sources.map((s) => (
                <li key={s.title}>
                  {s.url ? (
                    <a href={s.url} target="_blank" rel="noopener noreferrer" className="underline underline-offset-2">
                      {s.organization} — {s.title}
                    </a>
                  ) : (
                    `${s.organization} — ${s.title}`
                  )}
                </li>
              ))}
            </ul>
          </div>
        </Card>
      )}

      <Card aria-labelledby="ctx-title" className="bg-paper">
        <h2 id="ctx-title" className="text-sm font-semibold">{t('diagnose.result.context')}</h2>
        <ul className="mt-2 flex flex-wrap gap-2 text-xs">
          {(['crop', 'location', 'weather', 'reference'] as const).map((k) => (
            <li key={k} className="rounded-full bg-surface px-2.5 py-1 ring-1 ring-line">
              {t(`diagnose.result.ctx.${k}` as MessageKey)}: <strong>{t(`diagnose.result.ctx.${r.context_used[k]}` as MessageKey)}</strong>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-sm font-medium text-ink">{t('diagnose.result.disclaimer')}</p>
        {!r.recorded && <p className="mt-1 text-xs text-ink-faint">{t('diagnose.result.notRecorded')}</p>}
        <p className="mt-1 text-xs text-ink-faint">{r.generated_by.model}</p>
      </Card>
    </div>
  );
}
