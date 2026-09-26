'use client';

import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Loader2, Mic, MicOff, Send, Sparkles, Volume2, VolumeX } from 'lucide-react';
import { ApiError } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { onSpeechStateChange, recordingSupported, speakText, startRecording, stopRecording, stopSpeaking } from '@/lib/speech';
import type { DataSourceUse } from '@/lib/types';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';
import { ErrorState, errorMessage, inputClass } from './ui';

export type ChatMessage =
  | { id: string; role: 'user'; text: string; imageUrl?: string }
  | { id: string; role: 'assistant'; text: string; sources: DataSourceUse[]; generatedAt: string }
  | { id: string; role: 'error'; error: ApiError; retryText: string };

export function SourceList({ sources }: { sources: DataSourceUse[] }) {
  const { t } = useI18n();
  return (
    <p className="flex flex-wrap items-center gap-1.5 text-xs text-ink-faint">
      <span className="font-semibold text-ink-soft">{t('advisor.basedOn')}:</span>
      {sources.map((s) => (
        <span
          key={s.id}
          className={cn(
            'rounded-full px-2 py-0.5 ring-1',
            s.status === 'used' ? 'bg-leaf-50 text-leaf-700 ring-leaf-100' : 'bg-paper text-ink-faint ring-line line-through decoration-ink-faint/40',
          )}
        >
          {t(`advisor.source.${s.id}` as MessageKey)} · {t(`advisor.status.${s.status}` as MessageKey)}
        </span>
      ))}
    </p>
  );
}

function AssistantMessage({ m }: { m: Extract<ChatMessage, { role: 'assistant' }> }) {
  const { t, language } = useI18n();
  const [speaking, setSpeaking] = useState(false);
  useEffect(() => onSpeechStateChange((s) => !s && setSpeaking(false)), []);
  return (
    <div className="max-w-[92%] rounded-2xl rounded-tl-sm border border-line bg-surface px-4 py-3 shadow-[var(--shadow-card)]">
      <p className="mb-1 flex items-center gap-1 text-xs font-semibold text-leaf-700">
        <Sparkles className="h-3.5 w-3.5" aria-hidden /> {t('advisor.assistant')}
      </p>
      <div className="prose prose-sm max-w-none prose-p:my-2 prose-ul:my-2 prose-li:my-0.5 prose-headings:mb-1 prose-headings:mt-3 prose-headings:text-base">
        <ReactMarkdown remarkPlugins={[remarkGfm]} skipHtml>
          {m.text}
        </ReactMarkdown>
      </div>
      <div className="mt-3 space-y-2 border-t border-line pt-2">
        {m.sources.length > 0 && <SourceList sources={m.sources} />}
        <p className="text-xs text-ink-faint">{t('advisor.aiLabel')}</p>
        <button
          type="button"
          onClick={() => {
            if (speaking) return stopSpeaking();
            setSpeaking(true);
            speakText(m.text, language);
          }}
          className="inline-flex min-h-9 items-center gap-1.5 rounded-lg px-2 text-xs font-semibold text-leaf-700 hover:bg-leaf-50"
        >
          {speaking ? <VolumeX className="h-4 w-4" aria-hidden /> : <Volume2 className="h-4 w-4" aria-hidden />}
          {speaking ? t('action.stopReading') : t('action.readAloud')}
        </button>
      </div>
    </div>
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
    <div className="flex flex-col gap-4">
      <div aria-live="polite" className="space-y-4">
        {intro}
        {messages.map((m) =>
          m.role === 'user' ? (
            <div key={m.id} className="flex justify-end">
              <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-leaf-600 px-4 py-2.5 text-white">
                <span className="sr-only">{t('advisor.you')}: </span>
                {m.imageUrl && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={m.imageUrl} alt="" className="mb-2 max-h-40 rounded-lg object-cover" />
                )}
                <p className="whitespace-pre-wrap">{m.text}</p>
              </div>
            </div>
          ) : m.role === 'assistant' ? (
            <div key={m.id} className="flex justify-start">
              <AssistantMessage m={m} />
            </div>
          ) : (
            <div key={m.id} className="max-w-[92%]">
              <ErrorState error={m.error} title={t('advisor.failed')} onRetry={() => submit(m.retryText)} compact />
            </div>
          ),
        )}
        {busy && (
          <p role="status" className="flex items-center gap-2 text-sm text-ink-soft">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> {t('advisor.thinking')}
          </p>
        )}
        <div ref={endRef} />
      </div>

      {suggestions.length > 0 && (
        <div className="-mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
          {suggestions.map((s) => (
            <button
              key={s}
              type="button"
              disabled={busy || disabled}
              onClick={() => submit(s)}
              className="min-h-10 shrink-0 rounded-full border border-leaf-200 bg-leaf-50 px-3.5 text-sm font-medium text-leaf-700 hover:bg-leaf-100 disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {voiceError && <p role="alert" className="text-sm text-warn-700">{voiceError}</p>}
      {attachment}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit(text);
        }}
        className="flex items-end gap-2"
      >
        <label className="sr-only" htmlFor="chat-input">
          {placeholder}
        </label>
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
          className={cn(inputClass, 'max-h-40 min-h-12 resize-none py-3')}
        />
        <button
          type="button"
          onClick={toggleVoice}
          disabled={disabled}
          aria-pressed={listening}
          aria-label={listening ? t('advisor.stopVoice') : t('advisor.voice')}
          className={cn(
            'flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border transition-colors disabled:opacity-50',
            listening ? 'border-warn-200 bg-warn-50 text-warn-700' : 'border-line-strong bg-surface text-ink-soft hover:text-leaf-700',
          )}
        >
          {listening ? <MicOff className="h-5 w-5" aria-hidden /> : <Mic className="h-5 w-5" aria-hidden />}
        </button>
        <button
          type="submit"
          disabled={!text.trim() || busy || disabled}
          aria-label={t('action.send')}
          className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-leaf-600 text-white hover:bg-leaf-700 disabled:bg-line-strong"
        >
          <Send className="h-5 w-5" aria-hidden />
        </button>
      </form>
    </div>
  );
}
