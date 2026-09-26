'use client';

import { useRef, useState } from 'react';
import { ImagePlus, MapPin, X } from 'lucide-react';
import Conversation, { type ChatMessage } from '@/components/Conversation';
import FarmProfileForm, { useLocationLabel } from '@/components/FarmProfileForm';
import { buttonClass, Card, LoadingBlock, Note } from '@/components/ui';
import { ApiError, getAdvisory } from '@/lib/api';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import { blobToBase64, checkImageFile, prepareImage } from '@/lib/image';
import type { MessageKey } from '@/locales/en';
import { newId } from '@/lib/utils';

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
      setMessages((m) => [...m, { id: newId(), role: 'assistant', text: res.advisory_text, sources: res.data_sources, generatedAt: res.generated_at }]);
    } catch (e) {
      const err = e instanceof ApiError ? e : new ApiError('error', 'INTERNAL_ERROR', null, true);
      setMessages((m) => [...m, { id: newId(), role: 'error', error: err, retryText: text }]);
    } finally {
      setBusy(false);
    }
  };

  if (!ready) return <div className="mx-auto w-full max-w-3xl px-4 py-8"><LoadingBlock /></div>;

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-10 pt-6 sm:px-6">
      <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('advisor.title')}</h1>
      <p className="mt-1 text-ink-soft">{t('advisor.subtitle')}</p>

      {!profile.location || editing ? (
        <Card className="mt-5">
          {!profile.location && <Note className="mb-5">{t('advisor.needProfile')}</Note>}
          <FarmProfileForm onDone={() => setEditing(false)} onCancel={profile.location ? () => setEditing(false) : undefined} />
        </Card>
      ) : (
        <>
          <div className="mb-4 mt-4 flex flex-wrap items-center gap-2 text-sm">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-leaf-50 px-3 py-1.5 font-medium text-leaf-700">
              <MapPin className="h-4 w-4" aria-hidden /> {locationLabel(profile.location)}
              {profile.crop && ` · ${t(`crop.${profile.crop}` as MessageKey)}`}
            </span>
            <button type="button" onClick={() => setEditing(true)} className={buttonClass.ghost}>
              {t('action.change')}
            </button>
          </div>
          <Card>
            <Conversation
              messages={messages}
              onSend={send}
              busy={busy}
              placeholder={t('advisor.placeholder')}
              suggestions={messages.length ? [] : [t('advisor.q1'), t('advisor.q2'), t('advisor.q3'), t('advisor.q4')]}
              intro={
                <div className="rounded-2xl bg-paper p-4 text-sm text-ink-soft">
                  <p>{t('advisor.welcome')}</p>
                </div>
              }
              attachment={
                <div className="flex flex-wrap items-center gap-3">
                  {image ? (
                    <span className="relative inline-block">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img src={image.url} alt="" className="h-16 w-16 rounded-lg object-cover ring-1 ring-line" />
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
                    <button type="button" onClick={() => fileInput.current?.click()} className={buttonClass.ghost}>
                      <ImagePlus className="h-4 w-4" aria-hidden /> {t('advisor.attach')}
                    </button>
                  )}
                  <input ref={fileInput} type="file" accept="image/jpeg,image/png,image/webp" className="sr-only" tabIndex={-1} aria-hidden onChange={(e) => attach(e.target.files?.[0])} />
                  {imageProblem && <p role="alert" className="text-sm text-warn-700">{imageProblem}</p>}
                </div>
              }
            />
          </Card>
        </>
      )}
    </div>
  );
}
