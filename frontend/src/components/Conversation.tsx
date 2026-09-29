'use client';

import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Loader2, Mic, MicOff, Send, Sprout } from 'lucide-react';
import { ApiError } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { recordingSupported, startRecording, stopRecording } from '@/lib/speech';
import type { DataSourceUse, LanguageCode } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import ReadAloud from './ReadAloud';
import { ErrorState, errorMessage } from './ui';

export type ChatMessage =
  | { id: string; role: 'user'; text: string; imageUrl?: string }
  | { id: string; role: 'assistant'; text: string; language: LanguageCode; sources: DataSourceUse[]; generatedAt: string }
  | { id: string; role: 'error'; error: ApiError; retryText: string };

export function SourceList({ sources, className }: { sources: DataSourceUse[]; className?: string }) {
  const { t } = useI18n();
  return (
    <p className={cn('flex flex-wrap items-center gap-1.5 text-xs text-ink-faint', className)}>
      <span className="font-semibold text-ink-soft">{t('advisor.basedOn')}:</span>
      {sources.map((s) => (
        <span
          key={s.id}
          className={cn(
            'inline-flex items-center gap-1 rounded-md px-2 py-0.5',
            s.status === 'used' ? 'bg-leaf-50 text-leaf-700' : 'bg-paper text-ink-faint',
          )}
        >
          <span aria-hidden className={cn('h-1.5 w-1.5 rounded-full', s.status === 'used' ? 'bg-leaf-500' : 'bg-line-strong')} />
          {t(`advisor.source.${s.id}` as MessageKey)} · {t(`advisor.status.${s.status}` as MessageKey)}
        </span>
      ))}
    </p>
  );
}

function AssistantMessage({ m }: { m: Extract<ChatMessage, { role: 'assistant' }> }) {
  const { t, fmt } = useI18n();
  return (
    <article lang={m.language} className="w-full max-w-[40rem] border-l-2 border-leaf-500 pl-4 sm:pl-5">
      <p className="mb-1.5 flex items-center gap-1.5 text-sm font-semibold text-leaf-700">
        <Sprout className="h-3.5 w-3.5" aria-hidden /> {t('advisor.assistant')}
        <span className="font-normal normal-case tracking-normal text-ink-faint">· {fmt.relative(m.generatedAt)}</span>
      </p>
      <div className="prose prose-sm max-w-none text-[0.95rem] leading-relaxed text-ink prose-p:my-2 prose-ul:my-2 prose-li:my-0.5 prose-headings:mb-1 prose-headings:mt-4 prose-headings:text-base prose-headings:text-ink prose-strong:text-ink">
        <ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml>
          {m.text}
        </ReactMarkdown>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-3">
        <ReadAloud text={m.text} language={m.language} />
        <span className="text-xs text-ink-faint">{t('advisor.aiLabel')}</span>
      </div>
      {m.sources.length > 0 && <SourceList sources={m.sources} className="mt-3" />}
    </article>
  );
}

export default function Conversation({
  messages,
  onSend,
  busy,
  suggestions = [],
  placeholder,
  intro,
  attachment,
  disabled,
}: {
  messages: ChatMessage[];
  onSend: (text: string) => void;
  busy: boolean;
  suggestions?: string[];
  placeholder: string;
  intro?: React.ReactNode;
  attachment?: React.ReactNode;
  disabled?: boolean;
}) {
  const { t, language } = useI18n();
  const [text, setText] = useState('');
  const [listening, setListening] = useState(false);
  const [voiceError, setVoiceError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messages.length) endRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [messages.length, busy]);

  const submit = (value: string) => {
    const v = value.trim();
    if (!v || busy || disabled) return;
    onSend(v);
    setText('');
  };

  const toggleVoice = () => {
    setVoiceError(null);
    if (listening) return stopRecording();
    if (!recordingSupported()) return setVoiceError(t('advisor.micUnsupported'));
    setListening(true);
    startRecording(
      language,
      (heard) => setText(heard),
      (err) => {
        if (err instanceof ApiError) setVoiceError(errorMessage(t, err));
        else if (err instanceof DOMException && err.name === 'NotAllowedError') setVoiceError(t('advisor.micDenied'));
        else setVoiceError(t('error.generic'));
      },
      () => setListening(false),
    );
  };

  return (
    <div className="flex flex-col gap-5">
      <div aria-live="polite" className="space-y-6">
        {intro}
        {messages.map((m) =>
          m.role === 'user' ? (
            <div key={m.id} className="flex justify-end">
              <div className="max-w-[85%] rounded-2xl rounded-br-md bg-ink px-4 py-2.5 text-paper">
                <span className="sr-only">{t('advisor.you')}: </span>
                {m.imageUrl && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={m.imageUrl} alt={t('advisor.attachedPhoto')} className="mb-2 max-h-40 rounded-lg object-cover" />
                )}
                <p className="whitespace-pre-wrap">{m.text}</p>
              </div>
            </div>
          ) : m.role === 'assistant' ? (
            <AssistantMessage key={m.id} m={m} />
          ) : (
            <div key={m.id} className="max-w-[40rem]">
              <ErrorState error={m.error} title={t('advisor.failed')} onRetry={() => submit(m.retryText)} compact />
            </div>
          ),
        )}
        {busy && (
          <p role="status" className="flex items-center gap-2 border-l-2 border-leaf-200 pl-4 text-sm text-ink-soft">
            <Loader2 className="h-4 w-4 animate-spin text-leaf-600" aria-hidden /> {t('advisor.thinking')}
          </p>
        )}
        <div ref={endRef} />
      </div>

      {suggestions.length > 0 && (
        <div>
          <p className="mb-2 text-xs font-semibold text-ink-soft">{t('advisor.try')}</p>
          <ul className="grid gap-2 sm:grid-cols-2">
            {suggestions.map((s) => (
              <li key={s}>
                <button
                  type="button"
                  disabled={busy || disabled}
                  onClick={() => submit(s)}
                  className="flex min-h-11 w-full items-center justify-between gap-3 rounded-xl bg-paper/80 px-4 py-2.5 text-left text-sm font-medium text-ink ring-1 ring-line transition-[background-color,box-shadow] hover:bg-leaf-50 hover:ring-leaf-200 disabled:opacity-50"
                >
                  {s}
                  <Send className="h-3.5 w-3.5 shrink-0 text-leaf-600" aria-hidden />
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {voiceError && <p role="alert" className="text-sm text-warn-700">{voiceError}</p>}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit(text);
        }}
        className="rounded-2xl bg-surface p-2 shadow-[var(--shadow-card)] ring-1 ring-line-strong focus-within:ring-2 focus-within:ring-leaf-500"
      >
        {attachment && <div className="px-2 pb-1 pt-1">{attachment}</div>}
        <label className="sr-only" htmlFor="chat-input">
          {placeholder}
        </label>
        <div className="flex items-end gap-2">
          <textarea
            id="chat-input"
            rows={1}
            value={text}
            maxLength={2000}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submit(text);
              }
            }}
            placeholder={listening ? t('advisor.listening') : placeholder}
            disabled={disabled}
            className="max-h-40 min-h-12 flex-1 resize-none bg-transparent px-3 py-3 text-base text-ink placeholder:text-ink-faint focus:outline-none"
          />
          <button
            type="button"
            onClick={toggleVoice}
            disabled={disabled}
            aria-pressed={listening}
            aria-label={listening ? t('advisor.stopVoice') : t('advisor.voice')}
            className={cn(
              'flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors disabled:opacity-50',
              listening ? 'bg-warn-50 text-warn-700' : 'text-ink-soft hover:bg-paper hover:text-leaf-700',
            )}
          >
            {listening ? <MicOff className="h-5 w-5" aria-hidden /> : <Mic className="h-5 w-5" aria-hidden />}
          </button>
          <button
            type="submit"
            disabled={!text.trim() || busy || disabled}
            aria-label={t('action.send')}
            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-leaf-600 text-white transition-[background-color,transform] hover:bg-leaf-700 active:scale-95 disabled:bg-line-strong"
          >
            <Send className="h-5 w-5" aria-hidden />
          </button>
        </div>
      </form>
    </div>
  );
}
