'use client';

import { useEffect } from 'react';
import { CloudUpload, WifiOff } from 'lucide-react';
import { recordPractice, sendFeedback } from '@/lib/api';
import { useI18n } from '@/lib/i18n';
import { flushOutbox, useOnline, useOutboxCount, type OutboxItem } from '@/lib/offline';
import type { Followed, Outcome, PracticeStatus } from '@/lib/types';

async function deliver(item: OutboxItem) {
  const twin = { farmId: item.farmId, token: item.token };
  if (item.kind === 'feedback') await sendFeedback(twin, item.actionId, item.body as { followed?: Followed; outcome?: Outcome });
  else await recordPractice(twin, item.body.practice, item.body.status as PracticeStatus);
}

/**
 * A slim bar under the header that says when the device is offline (so saved copies are read as such) and sends
 * queued answers on reconnect. It stays out of the way: one line, sky tone, no alarm colour.
 */
export default function OfflineStatus() {
  const { t, fmt } = useI18n();
  const online = useOnline();
  const pending = useOutboxCount();

  useEffect(() => {
    if (online && pending > 0) void flushOutbox(deliver);
  }, [online, pending]);

  if (online && pending === 0) return null;
  return (
    <div role="status" className="sticky top-[var(--header-h)] z-30 border-b border-sky-100 bg-sky-50 text-sm text-sky-700">
      <p className="mx-auto flex max-w-6xl items-start gap-2.5 px-4 py-2 sm:px-6">
        {online ? <CloudUpload className="mt-0.5 h-4 w-4 shrink-0" aria-hidden /> : <WifiOff className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />}
        <span className="min-w-0">
          {online ? t('offline.sending', { count: fmt.num(pending, 0) }) : t('offline.banner')}
          {!online && pending > 0 && <strong className="font-semibold"> {t('offline.pending', { count: fmt.num(pending, 0) })}</strong>}
        </span>
      </p>
    </div>
  );
}
