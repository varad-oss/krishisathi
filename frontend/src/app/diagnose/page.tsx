'use client';

import { useEffect, useId, useRef, useState } from 'react';
import Link from 'next/link';
import { Camera, ImagePlus, Loader2, MapPin, MessageCircle, ScanSearch, X } from 'lucide-react';
import Conversation, { type ChatMessage } from '@/components/Conversation';
import DiagnosisResult from '@/components/diagnose/DiagnosisResult';
import { useLocationLabel } from '@/components/FarmProfileForm';
import { buttonClass, Card, ErrorState, inputClass, Note } from '@/components/ui';
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
  const { t, language } = useI18n();
  const { profile } = useFarmProfile();
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
      setMessages((m) => [...m, { id: newId(), role: 'assistant', text: res.advisory_text, sources: res.data_sources, generatedAt: res.generated_at }]);
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
    <div className="mx-auto w-full max-w-3xl px-4 pb-10 pt-6 sm:px-6">
      <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('diagnose.title')}</h1>
      <p className="mt-1 text-ink-soft">{t('diagnose.subtitle')}</p>

      <ol className="my-5 flex items-center gap-2 text-xs font-medium" aria-label={t('diagnose.title')}>
        {steps.map((s, i) => (
          <li key={s.key} className="flex items-center gap-2" aria-current={i === stepIndex ? 'step' : undefined}>
            <span
              className={cn(
                'flex h-6 w-6 items-center justify-center rounded-full tabular-nums',
                i < stepIndex ? 'bg-leaf-600 text-white' : i === stepIndex ? 'bg-leaf-100 text-leaf-700 ring-2 ring-leaf-500' : 'bg-line text-ink-faint',
              )}
            >
              {i + 1}
            </span>
            <span className={i === stepIndex ? 'text-ink' : 'text-ink-faint'}>{t(s.label)}</span>
            {i < steps.length - 1 && <span aria-hidden className="h-px w-6 bg-line-strong" />}
          </li>
        ))}
      </ol>

      {phase === 'result' && result ? (
        <div className="space-y-5">
          <DiagnosisResult result={result} previewUrl={previewUrl} onReset={reset} />
          {result.status !== 'not_a_plant' && (
            <Card aria-labelledby="followup-title">
              <h2 id="followup-title" className="mb-4 flex items-center gap-2 text-lg font-semibold">
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
            </Card>
          )}
        </div>
      ) : (
        <Card className="space-y-5">
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
                'flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-4 py-10 text-center transition-colors',
                dragging ? 'border-leaf-500 bg-leaf-50' : 'border-line-strong bg-paper',
              )}
            >
              <ImagePlus className="h-10 w-10 text-leaf-600" aria-hidden />
              <p className="mt-3 font-semibold">{t('diagnose.upload.title')}</p>
              <div className="mt-4 flex w-full max-w-sm flex-col gap-3 sm:flex-row sm:justify-center">
                <button type="button" onClick={() => cameraInput.current?.click()} className={cn(buttonClass.primary, 'w-full sm:w-auto')}>
                  <Camera className="h-4 w-4" aria-hidden /> {t('diagnose.upload.camera')}
                </button>
                <button type="button" onClick={() => fileInput.current?.click()} className={cn(buttonClass.secondary, 'w-full sm:w-auto')}>
                  {t('diagnose.upload.browse')}
                </button>
              </div>
              <p className="mt-4 hidden text-sm text-ink-soft sm:block">{t('diagnose.upload.drop')} {t('diagnose.upload.browse')}</p>
              <p className="mt-2 max-w-md text-xs text-ink-faint">{t('diagnose.upload.hint')}</p>
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
            <div className="relative overflow-hidden rounded-2xl bg-ink/5">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={previewUrl ?? ''} alt={t('diagnose.upload.preview')} className="mx-auto max-h-80 w-full object-contain" />
              {phase !== 'analyzing' && (
                <button
                  type="button"
                  onClick={reset}
                  aria-label={t('diagnose.upload.remove')}
                  className="absolute right-3 top-3 flex h-10 w-10 items-center justify-center rounded-full bg-surface/90 text-ink shadow hover:bg-surface"
                >
                  <X className="h-5 w-5" aria-hidden />
                </button>
              )}
              {phase === 'analyzing' && (
                <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 bg-leaf-900/60 text-white" role="status" aria-live="polite">
                  <Loader2 className="h-8 w-8 animate-spin" aria-hidden />
                  <p className="font-semibold">{t('diagnose.analyzing')}</p>
                  <p className="text-sm text-leaf-100">{t('diagnose.analyzingHint')}</p>
                </div>
              )}
            </div>
          )}

          {problem && <Note tone="warning">{t(`diagnose.upload.${problem}` as MessageKey)}</Note>}
          <p className="text-xs text-ink-faint">{t('diagnose.upload.tips')}</p>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor={cropId} className="mb-1 block text-sm font-semibold">
                {t('diagnose.crop')}
              </label>
              <select id={cropId} value={crop} onChange={(e) => setCrop(e.target.value as Crop | '')} className={inputClass} disabled={phase === 'analyzing'}>
                <option value="">{t('diagnose.cropUnknown')}</option>
                {CROPS.map((c) => (
                  <option key={c} value={c}>
                    {t(`crop.${c}` as MessageKey)}
                  </option>
                ))}
              </select>
            </div>
            <div className="text-sm">
              <p className="mb-1 font-semibold">{t('profile.location')}</p>
              {profile.location ? (
                <label className="flex min-h-11 items-start gap-2 rounded-xl border border-line-strong p-3">
                  <input type="checkbox" checked={useLocation} onChange={(e) => setUseLocation(e.target.checked)} className="mt-1 h-4 w-4 accent-leaf-600" />
                  <span>
                    {t('diagnose.location')}
                    <span className="block text-xs text-ink-faint">
                      <MapPin className="mr-1 inline h-3 w-3" aria-hidden />
                      {locationLabel(profile.location)}
                    </span>
                  </span>
                </label>
              ) : (
                <p className="rounded-xl bg-paper p-3 text-ink-soft">
                  {t('diagnose.noLocation')}{' '}
                  <Link href="/farm" className="font-semibold text-leaf-700 underline underline-offset-2">
                    {t('profile.title')}
                  </Link>
                </p>
              )}
            </div>
          </div>

          {error && <ErrorState error={error} title={t('diagnose.failed')} onRetry={analyze} />}

          <div className="flex flex-col gap-3 sm:flex-row">
            <button type="button" onClick={analyze} disabled={!file || phase === 'analyzing'} className={cn(buttonClass.primary, 'w-full sm:flex-1')}>
              {phase === 'analyzing' ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : <ScanSearch className="h-4 w-4" aria-hidden />}
              {phase === 'analyzing' ? t('diagnose.analyzing') : t('diagnose.analyze')}
            </button>
            {phase === 'analyzing' && (
              <button type="button" onClick={() => controller.current?.abort()} className={buttonClass.secondary}>
                {t('diagnose.cancel')}
              </button>
            )}
          </div>
          <p className="text-xs text-ink-faint">{t('diagnose.result.disclaimer')}</p>
        </Card>
      )}
    </div>
  );
}
