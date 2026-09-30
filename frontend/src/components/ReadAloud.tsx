'use client';

import { useEffect, useRef, useState } from 'react';
import { Loader2, Square, Volume2 } from 'lucide-react';
import { useI18n } from '@/lib/i18n';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import { useSpeech } from '@/lib/speech';
import type { LanguageCode } from '@/lib/types';
import { cn } from '@/lib/utils';

/**
 * Read aloud → Preparing audio… → Stop. `language` is the language the text is written in (not the
 * current UI language), so an earlier English answer is never read with a Hindi voice or vice versa.
 */
export default function ReadAloud({ text, language, className, autoPlay }: { text: string; language: LanguageCode; className?: string; autoPlay?: boolean }) {
  const { t } = useI18n();
  const { status, error, play, stop } = useSpeech();
  // Plays once when the message appears (only for answers to voice questions, right after the user spoke).
  const autoPlayed = useRef(false);
  useEffect(() => {
    if (!autoPlay || autoPlayed.current) return;
    autoPlayed.current = true;
    play(text, language);
  }, [autoPlay, play, text, language]);
  const busy = status === 'loading' || status === 'playing' || status === 'paused';

  // Announce transitions, including "Stopped", for screen-reader users.
  const [announcement, setAnnouncement] = useState('');
  const previous = useRef(status);
  useEffect(() => {
    const was = previous.current;
    previous.current = status;
    if (was === status) return;
    const text =
      status === 'loading' ? t('speech.preparing')
        : status === 'playing' ? t('speech.status.playing')
          : status === 'idle' && was !== 'error' ? t('speech.status.stopped')
            : '';
    setAnnouncement(text);
  }, [status, t]);

  const languageName = SUPPORTED_LANGUAGES.find((l) => l.code === language)?.nativeName ?? language;

  return (
    <span className={cn('inline-flex flex-col items-start gap-1', className)}>
      <button
        type="button"
        onClick={() => (busy ? stop() : play(text, language))}
        aria-pressed={busy}
        className={cn(
          'inline-flex min-h-10 items-center gap-2 rounded-full border px-3.5 text-sm font-semibold transition-[background-color,border-color,color,transform] active:scale-[0.98]',
          busy ? 'border-ink bg-ink text-paper hover:bg-ink/90' : 'border-line-strong bg-surface text-ink hover:border-leaf-600 hover:text-leaf-700',
        )}
      >
        {status === 'loading' ? (
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
        ) : busy ? (
          <Square className="h-3.5 w-3.5 fill-current" aria-hidden />
        ) : (
          <Volume2 className="h-4 w-4" aria-hidden />
        )}
        {status === 'loading' ? t('speech.preparing') : busy ? t('speech.stop') : t('action.readAloud')}
      </button>
      {error && (
        <span role="alert" className="text-xs text-warn-700">
          {t(error === 'blocked' ? 'speech.error.blocked' : 'speech.error.service', { language: languageName })}
        </span>
      )}
      <span className="sr-only" aria-live="polite">
        {announcement}
      </span>
    </span>
  );
}
