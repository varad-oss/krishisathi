'use client';

import { useEffect, useId, useRef, useState } from 'react';
import Link from 'next/link';
import { Camera, ImagePlus, Loader2, MapPin, MessageCircle, ScanSearch, X } from 'lucide-react';
import Conversation, { type ChatMessage } from '@/components/Conversation';
import DiagnosisResult from '@/components/diagnose/DiagnosisResult';
import { useLocationLabel } from '@/components/FarmProfileForm';
import { buttonClass, ErrorState, inputClass, Note, PageHeader } from '@/components/ui';
import { ApiError, diagnoseCrop, getFollowUpAdvisory } from '@/lib/api';
import { CROPS, type Crop } from '@/lib/catalog';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import { checkImageFile, prepareImage, type ImageProblem } from '@/lib/image';
import type { DiagnosisResponse } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn, newId } from '@/lib/utils';

type Phase = 'select' | 'analyzing' | 'result';

export default function DiagnosePage() {
  const { t, fmt, language } = useI18n();
  const { profile, twin } = useFarmProfile();
  const locationLabel = useLocationLabel();
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [problem, setProblem] = useState<ImageProblem | null>(null);
  // null = not chosen on this page yet, so the farm profile's crop applies.
  const [cropChoice, setCrop] = useState<Crop | '' | null>(null);
  const [useLocation, setUseLocation] = useState(true);
  const [phase, setPhase] = useState<Phase>('select');
  const [error, setError] = useState<ApiError | null>(null);
  const [result, setResult] = useState<DiagnosisResponse | null>(null);
  const [dragging, setDragging] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [askBusy, setAskBusy] = useState(false);
  const idempotencyKey = useRef(newId());
  const controller = useRef<AbortController | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const cameraInput = useRef<HTMLInputElement>(null);
  const cropId = useId();

  useEffect(() => () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
  }, [previewUrl]);

  const crop: Crop | '' = cropChoice ?? profile.crop ?? '';
  const location = useLocation ? profile.location : null;

  const pick = (f: File | undefined) => {
    if (!f) return;
    const issue = checkImageFile(f);
    setProblem(issue);
    setError(null);
    if (issue) return;
    setFile(f);
    setPreviewUrl(URL.createObjectURL(f));
    idempotencyKey.current = newId();
  };

  const reset = () => {
    controller.current?.abort();
    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setProblem(null);
    setMessages([]);
    setPhase('select');
  };

  const analyze = async () => {
    if (!file) return;
    setError(null);
    setPhase('analyzing');
    controller.current = new AbortController();
    try {
      const image = await prepareImage(file).catch(() => {
        throw new ApiError('unreadable', 'UNSUPPORTED_MEDIA_TYPE', null, false);
      });
      const res = await diagnoseCrop(image, {
        crop: crop || null,
        lat: location?.lat ?? null,
        lng: location?.lng ?? null,
        language,
        idempotencyKey: idempotencyKey.current,
        // The sowing date belongs to the profile crop; the farm record is linked only when the farmer shares location.
        sowingDate: crop && crop === profile.crop ? profile.sowingDate : null,
        twin: location ? twin : null,
        signal: controller.current.signal,
      });
      setResult(res);
      setMessages([]);
      setPhase('result');
      window.scrollTo({ top: 0 });
    } catch (e) {
      if (controller.current?.signal.aborted) {
        setPhase('select');
        return;
      }
      setError(e instanceof ApiError ? e : new ApiError('error', 'INTERNAL_ERROR', null, true));
      setPhase('select');
    }
  };

  const ask = async (question: string) => {
    if (!result || !profile.location) return;
    setMessages((m) => [...m, { id: newId(), role: 'user', text: question }]);
    setAskBusy(true);
    try {
      const res = await getFollowUpAdvisory({
        query: question,
        latitude: profile.location.lat,
        longitude: profile.location.lng,
        crop_type: crop || null,
        language,
        disease_name: result.disease_name ?? result.status,
        severity: result.severity,
      });
      setMessages((m) => [...m, { id: newId(), role: 'assistant', text: res.advisory_text, language: res.language, sources: res.data_sources, generatedAt: res.generated_at }]);
    } catch (e) {
      const err = e instanceof ApiError ? e : new ApiError('error', 'INTERNAL_ERROR', null, true);
      setMessages((m) => [...m, { id: newId(), role: 'error', error: err, retryText: question }]);
    } finally {
      setAskBusy(false);
    }
  };

  const steps: { key: Phase | 'details'; label: MessageKey }[] = [
    { key: 'select', label: 'diagnose.step.photo' },
    { key: 'details', label: 'diagnose.step.details' },
    { key: 'result', label: 'diagnose.step.result' },
  ];
  const stepIndex = phase === 'result' ? 2 : file ? 1 : 0;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-12 pt-8 sm:px-6 sm:pt-12">
      <PageHeader title={t('diagnose.title')} subtitle={phase === 'result' ? undefined : t('diagnose.subtitle')} />

      <ol className="mb-8 grid grid-cols-3 gap-2 text-sm font-medium" aria-label={t('diagnose.title')}>
        {steps.map((s, i) => (
          <li key={s.key} aria-current={i === stepIndex ? 'step' : undefined}>
            <span aria-hidden className={cn('block h-1.5 rounded-full', i <= stepIndex ? 'bg-leaf-600' : 'bg-paper-deep')} />
            <span className={cn('mt-2 flex items-center gap-1.5', i === stepIndex ? 'font-semibold text-ink' : 'text-ink-soft')}>
              <span className="tabular-nums">{fmt.num(i + 1, 0)}</span> {t(s.label)}
            </span>
          </li>
        ))}
      </ol>

      {phase === 'result' && result ? (
        <div className="space-y-10">
          <DiagnosisResult result={result} previewUrl={previewUrl} onReset={reset} twin={location ? twin : null} />
          {result.status !== 'not_a_plant' && (
            <section aria-labelledby="followup-title" className="border-t border-line pt-8">
              <h2 id="followup-title" className="mb-5 flex items-center gap-2 font-display text-xl">
                <MessageCircle className="h-5 w-5 text-leaf-600" aria-hidden /> {t('diagnose.followup.title')}
              </h2>
              {profile.location ? (
                <Conversation
                  messages={messages}
                  onSend={ask}
                  busy={askBusy}
                  placeholder={t('diagnose.followup.placeholder')}
                  suggestions={messages.length ? [] : [t('diagnose.followup.q1'), t('diagnose.followup.q2'), t('diagnose.followup.q3')]}
                />
              ) : (
                <Note>
                  {t('diagnose.followup.needLocation')}{' '}
                  <Link href="/farm" className="font-semibold underline underline-offset-2">
                    {t('profile.title')}
                  </Link>
                </Note>
              )}
            </section>
          )}
        </div>
      ) : (
        <div className="space-y-8">
          {!file ? (
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragging(true);
              }}
              onDragLeave={() => setDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragging(false);
                pick(e.dataTransfer.files?.[0]);
              }}
              className={cn(
                'rounded-[var(--radius-card)] border-2 border-dashed p-5 transition-colors sm:p-8',
                dragging ? 'border-leaf-500 bg-leaf-50' : 'border-line-strong bg-surface',
              )}
            >
              <p className="font-display text-xl">{t('diagnose.upload.title')}</p>
              <p className="mt-1 text-ink-soft">{t('diagnose.upload.tips')}</p>
              <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                <button type="button" onClick={() => cameraInput.current?.click()} className={cn(buttonClass.primary, 'min-h-16 w-full text-base sm:w-auto sm:px-8')}>
                  <Camera className="h-6 w-6" aria-hidden /> {t('diagnose.upload.camera')}
                </button>
                <button type="button" onClick={() => fileInput.current?.click()} className={cn(buttonClass.secondary, 'min-h-16 w-full sm:w-auto')}>
                  <ImagePlus className="h-5 w-5" aria-hidden /> {t('diagnose.upload.browse')}
                </button>
              </div>
              <p className="mt-4 hidden text-sm text-ink-soft sm:block">{t('diagnose.upload.drop')} {t('diagnose.upload.browse')}</p>
              <p className="mt-2 max-w-md text-xs text-ink-soft">{t('diagnose.upload.hint')}</p>
              <input ref={cameraInput} type="file" accept="image/*" capture="environment" className="sr-only" tabIndex={-1} aria-hidden onChange={(e) => pick(e.target.files?.[0])} />
              <input
                ref={fileInput}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                className="sr-only"
                aria-label={t('diagnose.upload.browse')}
                data-testid="file-input"
                onChange={(e) => pick(e.target.files?.[0])}
              />
            </div>
          ) : (
            <div className="relative overflow-hidden rounded-[var(--radius-card)] bg-ink">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={previewUrl ?? ''} alt={t('diagnose.upload.preview')} className="mx-auto max-h-[22rem] w-full object-contain" />
              {phase !== 'analyzing' && (
                <button
                  type="button"
                  onClick={reset}
                  aria-label={t('diagnose.upload.remove')}
                  className="absolute right-3 top-3 flex h-11 w-11 items-center justify-center rounded-full bg-surface text-ink shadow-[var(--shadow-raised)] hover:bg-paper"
                >
                  <X className="h-5 w-5" aria-hidden />
                </button>
              )}
              {phase === 'analyzing' && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-ink/75 px-6 text-center text-white" role="status" aria-live="polite">
                  <ScanSearch className="h-9 w-9 animate-pulse" aria-hidden />
                  <p className="text-lg font-semibold">{t('diagnose.analyzing')}</p>
                  <p className="text-sm text-leaf-100">{t('diagnose.analyzingHint')}</p>
                </div>
              )}
            </div>
          )}

          {problem && <Note tone="warning">{t(`diagnose.upload.${problem}` as MessageKey)}</Note>}

          <fieldset className="grid gap-5 sm:grid-cols-2" disabled={phase === 'analyzing'}>
            <legend className="sr-only">{t('diagnose.step.details')}</legend>
            <div>
              <label htmlFor={cropId} className="mb-1.5 block font-semibold">
                {t('diagnose.crop')}
              </label>
              <select id={cropId} value={crop} onChange={(e) => setCrop(e.target.value as Crop | '')} className={inputClass}>
                <option value="">{t('diagnose.cropUnknown')}</option>
                {CROPS.map((c) => (
                  <option key={c} value={c}>
                    {t(`crop.${c}` as MessageKey)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <p className="mb-1.5 font-semibold">{t('profile.location')}</p>
              {profile.location ? (
                <label className="flex min-h-12 cursor-pointer items-start gap-3 rounded-[var(--radius-inner)] border border-line-strong bg-surface p-3">
                  <input type="checkbox" checked={useLocation} onChange={(e) => setUseLocation(e.target.checked)} className="mt-1 h-5 w-5 shrink-0 accent-leaf-600" />
                  <span className="text-sm">
                    {t('diagnose.location')}
                    <span className="mt-0.5 flex items-center gap-1 text-ink-soft">
                      <MapPin className="h-3.5 w-3.5" aria-hidden />
                      {locationLabel(profile.location)}
                    </span>
                  </span>
                </label>
              ) : (
                <p className="rounded-[var(--radius-inner)] border border-dashed border-line-strong p-3 text-sm text-ink-soft">
                  {t('diagnose.noLocation')}{' '}
                  <Link href="/farm" className="font-semibold text-leaf-700 underline underline-offset-2">
                    {t('profile.title')}
                  </Link>
                </p>
              )}
            </div>
          </fieldset>

          {error && <ErrorState error={error} title={t('diagnose.failed')} onRetry={analyze} />}

          {/* On phones the main action stays in reach of the thumb once a photo is chosen. */}
          <div className={cn('flex flex-col gap-3 sm:flex-row', file && 'sticky bottom-[calc(4.25rem+env(safe-area-inset-bottom))] z-20 -mx-4 border-t border-line bg-paper/95 px-4 py-3 backdrop-blur sm:static sm:mx-0 sm:border-0 sm:bg-transparent sm:p-0')}>
            <button type="button" onClick={analyze} disabled={!file || phase === 'analyzing'} className={cn(buttonClass.primary, 'w-full text-base sm:flex-1')}>
              {phase === 'analyzing' ? <Loader2 className="h-5 w-5 animate-spin" aria-hidden /> : <ScanSearch className="h-5 w-5" aria-hidden />}
              {phase === 'analyzing' ? t('diagnose.analyzing') : t('diagnose.analyze')}
            </button>
            {phase === 'analyzing' && (
              <button type="button" onClick={() => controller.current?.abort()} className={buttonClass.secondary}>
                {t('diagnose.cancel')}
              </button>
            )}
          </div>
          <p className="text-sm text-ink-soft">{t('diagnose.result.disclaimer')}</p>
        </div>
      )}
    </div>
  );
}
