'use client';

import { useState } from 'react';
import { AlertTriangle, BookOpenCheck, CheckCircle2, CircleHelp, Copy, ExternalLink, Eye, FlaskConical, ImageOff, Leaf, ShieldCheck, Share2, Timer, UserRound } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import type { DiagnosisResponse, Escalation, FarmTwin } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import ReadAloud from '../ReadAloud';
import { buttonClass, Card, KindTag, LevelBadge, Note } from '../ui';
import { ActionFeedback } from '../farm/History';

function StepList({ icon: Icon, title, items, tone, lang }: { icon: React.ElementType; title: string; items: string[]; tone: string; lang?: string }) {
  if (!items.length) return null;
  return (
    <div className={cn('rounded-[var(--radius-inner)] p-4', tone)}>
      <h4 className="mb-2 flex items-center gap-2 font-semibold">
        <Icon className="h-4 w-4" aria-hidden /> {title}
      </h4>
      <ul className="list-disc space-y-1 pl-5 text-sm text-ink" lang={lang}>
        {items.map((s, i) => (
          <li key={i}>{s}</li>
        ))}
      </ul>
    </div>
  );
}

function EscalationCard({ escalation: e, result: r }: { escalation: Escalation; result: DiagnosisResponse }) {
  const { t, fmt } = useI18n();
  const [copied, setCopied] = useState(false);
  const c = e.case;
  const caseText = t('escalation.caseText', {
    crop: c.crop ? t(`crop.${c.crop}` as MessageKey) : '—',
    disease: c.ai_diagnosis.possible_disease ?? r.disease_name ?? '—',
    certainty: t(`level.${c.ai_diagnosis.certainty}` as MessageKey),
    symptoms: r.observed_symptoms.join('; ') || '—',
    location: c.location ? `${fmt.num(c.location.lat, 2)}, ${fmt.num(c.location.lng, 2)}` : '—',
    id: c.case_id.slice(0, 8),
  });
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(caseText);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  };
  return (
    <Card aria-labelledby="escalation-title" className="ring-2 ring-watch-200">
      <h2 id="escalation-title" className="flex items-center gap-2 font-display text-[1.3rem] font-medium">
        <UserRound className="h-5 w-5 text-watch-700" aria-hidden /> {t('escalation.title')}
      </h2>
      <p className="mt-2 text-ink-soft">{t(`escalation.body.${e.reason}` as MessageKey)}</p>
      <p className="mt-3 font-semibold">
        {e.kvk ? <span lang="en">{t('escalation.kvk', { name: e.kvk.name, district: e.kvk.district })}</span> : t('escalation.noKvk')}
      </p>
      <div className="mt-4 flex flex-wrap gap-3">
        <a
          href={`https://api.whatsapp.com/send?text=${encodeURIComponent(caseText)}`}
          target="_blank"
          rel="noopener noreferrer"
          className={buttonClass.primary}
        >
          <Share2 className="h-4 w-4" aria-hidden /> {t('escalation.share')}
        </a>
        <button type="button" onClick={copy} className={buttonClass.secondary}>
          <Copy className="h-4 w-4" aria-hidden /> {copied ? t('escalation.copied') : t('escalation.copy')}
        </button>
        <a href={e.kvk_portal} target="_blank" rel="noopener noreferrer" className={buttonClass.ghost}>
          {t('farm.kvk.portal')} <ExternalLink className="h-3.5 w-3.5" aria-hidden />
        </a>
      </div>
      <p className="mt-3 text-xs text-ink-faint">{t('escalation.photoNote')} {t('escalation.notSent')}</p>
    </Card>
  );
}

export default function DiagnosisResult({ result, previewUrl, onReset, twin }: { result: DiagnosisResponse; previewUrl: string | null; onReset: () => void; twin?: FarmTwin | null }) {
  const { t, language } = useI18n();
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

  // Read in the language the result was generated in; the heading is UI copy, so include it only when it matches.
  const spoken = [language === r.language ? heading : r.disease_name, r.summary, ...r.treatment.immediate].filter(Boolean).join('. ');

  const share = () => {
    const text = t('diagnose.result.shareText', { result: heading, certainty: t(`level.${r.certainty}` as MessageKey) });
    window.open(`https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`, '_blank', 'noopener,noreferrer');
  };

  const levels = ['low', 'moderate', 'high'] as const;
  const filled = levels.indexOf(r.certainty) + 1;
  const firstStep = r.treatment.immediate[0];

  return (
    <div className="space-y-6 animate-rise">
      <section aria-labelledby="result-title" className="overflow-hidden rounded-[var(--radius-card)] bg-surface shadow-[var(--shadow-raised)] ring-1 ring-line/80">
        <div className="grid sm:grid-cols-[13rem_1fr]">
          {previewUrl && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={previewUrl} alt={t('diagnose.upload.preview')} className="h-52 w-full object-cover sm:h-full sm:min-h-64" />
          )}
          <div className={cn('min-w-0 p-5 sm:p-7', !previewUrl && 'sm:col-span-2')}>
            <p className="flex flex-wrap items-center gap-2 text-sm text-ink-soft">
              {t('diagnose.result.title')} <KindTag kind="ai_model" className="text-xs" />
            </p>
            <h2 id="result-title" className="mt-2 flex items-start gap-2.5 font-display text-[1.9rem] font-medium leading-tight">
              <HeadingIcon className={cn('mt-1.5 h-6 w-6 shrink-0', r.status === 'healthy' ? 'text-leaf-600' : detected ? 'text-warn-700' : 'text-ink-faint')} aria-hidden />
              <span>{heading}</span>
            </h2>
            {r.scientific_name && <p className="mt-1 text-sm italic text-ink-soft" lang="la">{r.scientific_name}</p>}

            {r.status !== 'not_a_plant' && (
              <div className="mt-5">
                <div className="flex items-center justify-between gap-3 text-sm">
                  <span className="font-semibold">{t('diagnose.result.certainty')}</span>
                  <span className="font-semibold">{t(`level.${r.certainty}` as MessageKey)}</span>
                </div>
                <div className="mt-1.5 grid grid-cols-3 gap-1" role="img" aria-label={`${t('diagnose.result.certainty')}: ${t(`level.${r.certainty}` as MessageKey)}`}>
                  {levels.map((l, i) => (
                    <span
                      key={l}
                      className={cn('h-1.5 rounded-full', i < filled ? (r.certainty === 'high' ? 'bg-leaf-600' : r.certainty === 'moderate' ? 'bg-watch-500' : 'bg-warn-500') : 'bg-paper-deep')}
                    />
                  ))}
                </div>
                {r.certainty_reason && (
                  <p className="mt-2 text-sm text-ink-soft">
                    <span className="font-semibold text-ink">{t('diagnose.result.certaintyWhy')}: </span>
                    <span lang={r.language}>{r.certainty_reason}</span>
                  </p>
                )}
              </div>
            )}

            {r.status === 'healthy' && <p className="mt-4 text-ink-soft">{t('diagnose.result.healthyBody')}</p>}
            {r.status === 'uncertain' && <p className="mt-4 text-ink-soft">{t('diagnose.result.uncertainBody')}</p>}
            {r.status === 'not_a_plant' && <p className="mt-4 text-ink-soft">{t('diagnose.result.notPlantBody')}</p>}

            {detected && (
              <dl className="mt-5 grid grid-cols-2 gap-x-4 gap-y-3 border-t border-line pt-4 text-sm">
                <div>
                  <dt className="flex items-center gap-1.5 text-ink-soft"><Timer className="h-4 w-4" aria-hidden /> {t('diagnose.result.urgency')}</dt>
                  <dd className={cn('mt-0.5 font-semibold', r.urgency === 'immediate' && 'text-warn-700')}>{t(`urgency.${r.urgency}` as MessageKey)}</dd>
                </div>
                {r.affected_part && (
                  <div>
                    <dt className="flex items-center gap-1.5 text-ink-soft"><Leaf className="h-4 w-4" aria-hidden /> {t('diagnose.result.affected')}</dt>
                    <dd className="mt-0.5 font-semibold" lang={r.language}>{r.affected_part}</dd>
                  </div>
                )}
                {r.severity && (
                  <div>
                    <dt className="text-ink-soft">{t('diagnose.result.severity')}</dt>
                    <dd className="mt-1"><LevelBadge level={r.severity} /></dd>
                  </div>
                )}
                {r.spread_risk && (
                  <div>
                    <dt className="text-ink-soft">{t('diagnose.result.spread')}</dt>
                    <dd className="mt-1"><LevelBadge level={r.spread_risk} /></dd>
                  </div>
                )}
              </dl>
            )}
          </div>
        </div>

        <div className="space-y-3 border-t border-line bg-paper/50 p-5 sm:p-7">
          {firstStep && r.status !== 'not_a_plant' && (
            <div className="rounded-[var(--radius-inner)] bg-surface p-4 ring-1 ring-line">
              <p className="text-xs font-semibold text-leaf-700">{t('diagnose.result.doNow')}</p>
              <p className="mt-1 text-[1.05rem] font-medium leading-snug" lang={r.language}>{firstStep}</p>
            </div>
          )}
          {lowCertainty && r.status !== 'not_a_plant' && (
            <Note tone="warning" className="font-medium">
              {t('diagnose.result.lowWarning')}
            </Note>
          )}
          {(r.guidance.level === 'supported' || r.guidance.level === 'cautious') && (
            <Note tone={r.guidance.level === 'supported' ? 'info' : 'watch'}>{t(`diagnose.guidance.${r.guidance.level}` as MessageKey)}</Note>
          )}
          {r.guidance.level === 'escalate' && !lowCertainty && <Note tone="warning" className="font-medium">{t('diagnose.guidance.escalate')}</Note>}
          {r.image_quality === 'poor' && <Note tone="watch">{t('diagnose.result.poorImage')}</Note>}
          {language !== r.language && <Note>{t('diagnose.result.languageMismatch')}</Note>}
          {r.summary && (
            <p className="text-ink-soft" lang={r.language}>
              {r.summary}
            </p>
          )}
          <div className="flex flex-wrap items-center gap-3 pt-1">
            <ReadAloud text={spoken} language={r.language} />
            <button type="button" onClick={share} className={cn(buttonClass.secondary, 'min-h-10 rounded-full px-4')}>
              <Share2 className="h-4 w-4" aria-hidden /> {t('diagnose.result.share')}
            </button>
            <button type="button" onClick={onReset} className={buttonClass.ghost}>
              {t('diagnose.result.another')}
            </button>
          </div>
        </div>
      </section>

      {(r.observed_symptoms.length > 0 || r.alternative_causes.length > 0 || r.differential.length > 0) && (
        <Card aria-label={t('diagnose.result.symptoms')}>
          <div className="grid gap-6 sm:grid-cols-2">
            {r.observed_symptoms.length > 0 && (
              <div>
                <h3 className="flex items-center gap-2 font-semibold">
                  <Eye className="h-4 w-4 text-leaf-600" aria-hidden /> {t('diagnose.result.symptoms')}
                </h3>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-soft" lang={r.language}>
                  {r.observed_symptoms.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
            {r.differential.length > 0 ? (
              <div>
                <h3 className="flex items-center gap-2 font-semibold">
                  <CircleHelp className="h-4 w-4 text-ink-faint" aria-hidden /> {t('diagnose.differential.title')}
                </h3>
                <ol className="mt-2 space-y-2 text-sm">
                  {r.differential.map((d, i) => (
                    <li key={i}>
                      <span className="flex flex-wrap items-center gap-2">
                        <span className="font-medium" lang={r.language}>{d.name}</span>
                        <LevelBadge level={d.likelihood} label={t('diagnose.differential.likelihood')} />
                      </span>
                      {d.reason && <span className="block text-ink-soft" lang={r.language}>{d.reason}</span>}
                    </li>
                  ))}
                </ol>
              </div>
            ) : r.alternative_causes.length > 0 && (
              <div>
                <h3 className="flex items-center gap-2 font-semibold">
                  <CircleHelp className="h-4 w-4 text-ink-faint" aria-hidden /> {t('diagnose.result.alternatives')}
                </h3>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-ink-soft" lang={r.language}>
                  {r.alternative_causes.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
          </div>
        </Card>
      )}

      {r.escalation && <EscalationCard escalation={r.escalation} result={r} />}

      {twin && r.twin?.action && (
        <Card aria-label={t('feedback.question')}>
          <ActionFeedback twin={twin} action={r.twin.action} />
        </Card>
      )}

      {r.status !== 'not_a_plant' && (
        <Card aria-labelledby="steps-title">
          <h2 id="steps-title" className="mb-5 font-display text-[1.3rem] font-medium">{t('diagnose.result.steps')}</h2>
          <div className="grid gap-3 md:grid-cols-2">
            <StepList icon={AlertTriangle} title={t('diagnose.result.immediate')} items={r.treatment.immediate} lang={r.language} tone="bg-warn-50/60" />
            <StepList icon={Leaf} title={t('diagnose.result.organic')} items={r.treatment.organic} lang={r.language} tone="bg-leaf-50/70" />
            <StepList icon={ShieldCheck} title={t('diagnose.result.prevention')} items={r.treatment.prevention} lang={r.language} tone="bg-paper/80" />
            {detected && (
              <div className="rounded-[var(--radius-inner)] bg-sky-50/70 p-4">
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
          <h2 id="ref-title" className="flex items-center gap-2 font-display text-[1.3rem] font-medium">
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

      <Card aria-labelledby="ctx-title" className="bg-paper/60 shadow-none">
        <h2 id="ctx-title" className="text-sm font-semibold">{t('diagnose.result.context')}</h2>
        <ul className="mt-2 flex flex-wrap gap-2 text-xs">
          {(['crop', 'location', 'weather', 'reference', 'crop_stage', 'nearby_reports', 'satellite', 'farm'] as const).filter((k) => r.context_used[k]).map((k) => (
            <li key={k} className="rounded-md bg-surface px-2.5 py-1 ring-1 ring-line">
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
