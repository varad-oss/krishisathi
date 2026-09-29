'use client';

import { useRef, useState } from 'react';
import { ImagePlus, MapPin, Sprout, X } from 'lucide-react';
import Conversation, { type ChatMessage } from '@/components/Conversation';
import FarmProfileForm, { useLocationLabel } from '@/components/FarmProfileForm';
import { buttonClass, Card, LoadingBlock, Note, PageHeader } from '@/components/ui';
import { ApiError, getAdvisory } from '@/lib/api';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import { blobToBase64, checkImageFile, prepareImage } from '@/lib/image';
import type { MessageKey } from '@/locales/en';
import { cn, newId } from '@/lib/utils';

export default function AdvisorPage() {
  const { t, language } = useI18n();
  const { profile, ready } = useFarmProfile();
  const locationLabel = useLocationLabel();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [image, setImage] = useState<{ blob: Blob; url: string } | null>(null);
  const [imageProblem, setImageProblem] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

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

  const send = async (text: string) => {
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
      });
      setMessages((m) => [...m, { id: newId(), role: 'assistant', text: res.advisory_text, language: res.language, sources: res.data_sources, generatedAt: res.generated_at }]);
    } catch (e) {
      const err = e instanceof ApiError ? e : new ApiError('error', 'INTERNAL_ERROR', null, true);
      setMessages((m) => [...m, { id: newId(), role: 'error', error: err, retryText: text }]);
    } finally {
      setBusy(false);
    }
  };

  if (!ready) return <div className="mx-auto w-full max-w-3xl px-4 py-10"><LoadingBlock /></div>;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-12 pt-6 sm:px-6 sm:pt-10">
      <PageHeader
        title={t('advisor.title')}
        subtitle={t('advisor.subtitle')}
        eyebrow={
          profile.location && !editing ? (
            <span className="flex flex-wrap items-center gap-x-2 gap-y-1">
              <MapPin className="h-4 w-4" aria-hidden /> {locationLabel(profile.location)}
              {profile.crop && <span className="text-ink-soft">· {t(`crop.${profile.crop}` as MessageKey)}</span>}
              <button type="button" onClick={() => setEditing(true)} className="min-h-10 font-semibold text-leaf-700 underline underline-offset-2">
                {t('action.change')}
              </button>
            </span>
          ) : undefined
        }
      />

      {!profile.location || editing ? (
        <Card>
          {!profile.location && <Note className="mb-5">{t('advisor.needProfile')}</Note>}
          <FarmProfileForm onDone={() => setEditing(false)} onCancel={profile.location ? () => setEditing(false) : undefined} />
        </Card>
      ) : (
        <Conversation
          messages={messages}
          onSend={send}
          busy={busy}
          placeholder={t('advisor.placeholder')}
          suggestions={messages.length ? [] : [t('advisor.q1'), t('advisor.q2'), t('advisor.q3'), t('advisor.q4')]}
          intro={
            <div className="flex items-start gap-3 rounded-[var(--radius-inner)] bg-leaf-50/70 p-4 text-sm text-ink-soft">
              <Sprout className="mt-0.5 h-5 w-5 shrink-0 text-leaf-600" aria-hidden />
              <p className="text-ink">{t('advisor.welcome')}</p>
            </div>
          }
          attachment={
            <div className="flex flex-wrap items-center gap-3">
              {image ? (
                <span className="relative inline-block">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={image.url} alt={t('advisor.attachedPhoto')} className="h-16 w-16 rounded-lg object-cover ring-1 ring-line" />
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
                <button type="button" onClick={() => fileInput.current?.click()} className={cn(buttonClass.ghost, 'min-h-10 px-2')}>
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
