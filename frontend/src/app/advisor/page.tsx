'use client';

import { Suspense, useRef, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { History, ImagePlus, MapPin, Sprout, X } from 'lucide-react';
import Conversation, { type ChatMessage } from '@/components/Conversation';
import FarmProfileForm, { useLocationLabel } from '@/components/FarmProfileForm';
import { buttonClass, LoadingBlock, Note, PageHeader } from '@/components/ui';
import { ApiError, getAdvisory } from '@/lib/api';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import { blobToBase64, checkImageFile, prepareImage } from '@/lib/image';
import type { MessageKey } from '@/locales/en';
import { cn, newId } from '@/lib/utils';
import { readCached, saveCached } from '@/lib/offline';
import type { DataSourceUse, LanguageCode } from '@/lib/types';

const LAST_ANSWER = 'advisor:last';
type SavedAnswer = { question: string; answer: string; language: LanguageCode; sources: DataSourceUse[] };

/** The last answer received on this device, clearly marked as saved and dated (useful offline). */
function LastAnswer() {
  const { t, fmt } = useI18n();
  // Rendered only after the profile has loaded on the client, so reading storage here cannot mismatch SSR.
  const [saved] = useState(() => readCached<SavedAnswer>(LAST_ANSWER));
  if (!saved) return null;
  return (
    <details className="rounded-[var(--radius-inner)] border border-dashed border-sky-600/40 bg-sky-50/60 p-4 text-sm">
      <summary className="flex min-h-10 cursor-pointer items-center gap-2 font-semibold text-sky-700">
        <History className="h-4 w-4" aria-hidden />
        {t('offline.lastAnswer', { time: fmt.relative(saved.savedAt) })}
      </summary>
      <p className="mt-2 font-medium">{saved.data.question}</p>
      <p lang={saved.data.language} className="mt-1 whitespace-pre-wrap text-ink-soft">{saved.data.answer}</p>
      <p className="mt-2 text-xs text-ink-soft">{t('offline.savedCopy')}</p>
    </details>
  );
}

// Topics the problem page can open the advisor with; anything else in the URL is ignored.
const TOPICS = ['notGrowing', 'unknown'] as const;

export default function AdvisorRoute() {
  // useSearchParams needs a Suspense boundary on a prerendered page.
  return (
    <Suspense fallback={<div className="mx-auto w-full max-w-3xl px-4 py-10"><LoadingBlock /></div>}>
      <AdvisorPage />
    </Suspense>
  );
}

function AdvisorPage() {
  const { t, language } = useI18n();
  const { profile, ready } = useFarmProfile();
  const locationLabel = useLocationLabel();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [image, setImage] = useState<{ blob: Blob; url: string } | null>(null);
  const [imageProblem, setImageProblem] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const topic = useSearchParams()?.get('topic');
  const initialText = TOPICS.find((x) => x === topic) ? t(`problem.${topic}.question` as MessageKey) : '';

  const attach = async (f: File | undefined) => {
    if (!f) return;
    const issue = checkImageFile(f);
    if (issue) return setImageProblem(t(`diagnose.upload.${issue}` as MessageKey));
    try {
      const blob = await prepareImage(f);
      setImageProblem(null);
      setImage({ blob, url: URL.createObjectURL(blob) });
    } catch {
      setImageProblem(t('diagnose.upload.unreadable'));
    }
  };

  const send = async (text: string, opts?: { spoken: boolean }) => {
    const spoken = !!opts?.spoken;
    const loc = profile.location;
    if (!loc) return;
    const sent = image;
    setImage(null);
    setMessages((m) => [...m, { id: newId(), role: 'user', text, imageUrl: sent?.url }]);
    setBusy(true);
    try {
      const res = await getAdvisory({
        query: text,
        latitude: loc.lat,
        longitude: loc.lng,
        crop_type: profile.crop,
        language,
        image_base64: sent ? await blobToBase64(sent.blob) : undefined,
        mode: spoken ? 'speech' : 'text',
        sowing_date: profile.sowingDate,
      });
      setMessages((m) => [...m, { id: newId(), role: 'assistant', text: res.advisory_text, language: res.language, sources: res.data_sources, generatedAt: res.generated_at, spoken: res.mode === 'speech' }]);
      saveCached<SavedAnswer>(LAST_ANSWER, { question: text, answer: res.advisory_text, language: res.language, sources: res.data_sources });
    } catch (e) {
      const err = e instanceof ApiError ? e : new ApiError('error', 'INTERNAL_ERROR', null, true);
      setMessages((m) => [...m, { id: newId(), role: 'error', error: err, retryText: text }]);
    } finally {
      setBusy(false);
    }
  };

  if (!ready) return <div className="mx-auto w-full max-w-3xl px-4 py-10"><LoadingBlock /></div>;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-12 pt-8 sm:px-6 sm:pt-12">
      <PageHeader
        title={t('advisor.title')}
        subtitle={t('advisor.subtitle')}
        eyebrow={
          profile.location && !editing ? (
            <span className="flex flex-wrap items-center gap-x-2 gap-y-1">
              <MapPin className="h-4 w-4 text-leaf-600" aria-hidden /> <span className="text-ink">{locationLabel(profile.location)}</span>
              {profile.crop && <span className="text-ink-soft">· {t(`crop.${profile.crop}` as MessageKey)}</span>}
              <button type="button" onClick={() => setEditing(true)} className="min-h-11 font-semibold text-leaf-700 underline underline-offset-4">
                {t('action.change')}
              </button>
            </span>
          ) : undefined
        }
      />

      {!profile.location || editing ? (
        <div>
          {!profile.location && <Note className="mb-6">{t('advisor.needProfile')}</Note>}
          <FarmProfileForm onDone={() => setEditing(false)} onCancel={profile.location ? () => setEditing(false) : undefined} />
        </div>
      ) : (
        <Conversation
          messages={messages}
          onSend={send}
          initialText={initialText}
          busy={busy}
          placeholder={t('advisor.placeholder')}
          suggestions={messages.length ? [] : [t('advisor.q1'), t('advisor.q2'), t('advisor.q3'), t('advisor.q4')]}
          intro={
            <>
              <div className="flex items-start gap-3 rounded-[var(--radius-inner)] bg-leaf-50 p-4">
                <Sprout className="mt-0.5 h-5 w-5 shrink-0 text-leaf-600" aria-hidden />
                <p className="text-ink">{t('advisor.welcome')}</p>
              </div>
              {messages.length === 0 && <LastAnswer />}
            </>
          }
          attachment={
            <div className="flex flex-wrap items-center gap-3">
              {image ? (
                <span className="relative inline-block">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={image.url} alt={t('advisor.attachedPhoto')} className="h-16 w-16 rounded-[var(--radius-inner)] border border-line object-cover" />
                  <button
                    type="button"
                    onClick={() => setImage(null)}
                    aria-label={t('advisor.removeAttachment')}
                    className="absolute -right-2 -top-2 flex h-7 w-7 items-center justify-center rounded-full bg-ink text-white"
                  >
                    <X className="h-4 w-4" aria-hidden />
                  </button>
                </span>
              ) : (
                <button type="button" onClick={() => fileInput.current?.click()} className={cn(buttonClass.ghost, 'min-h-11 px-2')}>
                  <ImagePlus className="h-4 w-4" aria-hidden /> {t('advisor.attach')}
                </button>
              )}
              <input ref={fileInput} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" tabIndex={-1} aria-hidden onChange={(e) => attach(e.target.files?.[0])} />
              {imageProblem && <p role="alert" className="text-sm text-warn-700">{imageProblem}</p>}
            </div>
          }
        />
      )}
    </div>
  );
}
