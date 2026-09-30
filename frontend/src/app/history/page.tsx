'use client';

import Link from 'next/link';
import { useLocationLabel } from '@/components/FarmProfileForm';
import { FarmTimeline } from '@/components/farm/History';
import { LoadingBlock, PageHeader, buttonClass } from '@/components/ui';
import { getFarmHistory } from '@/lib/api';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import { useResource } from '@/lib/use-resource';
import type { MessageKey } from '@/locales/en';

export default function HistoryPage() {
  const { t } = useI18n();
  const { profile, ready, twin, twinRevision } = useFarmProfile();
  const locationLabel = useLocationLabel();
  const history = useResource(twin ? (s) => getFarmHistory(twin, s) : null, [twin?.farmId, twinRevision]);

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-12 pt-8 sm:px-6 sm:pt-12">
      <PageHeader
        eyebrow={profile.location ? [locationLabel(profile.location), profile.crop && t(`crop.${profile.crop}` as MessageKey)].filter(Boolean).join(' · ') : undefined}
        title={t('history.title')}
        subtitle={t('history.subtitle')}
      />
      {!ready ? (
        <LoadingBlock lines={4} />
      ) : !profile.location ? (
        <div className="space-y-4">
          <p className="text-ink-soft">{t('profile.body')}</p>
          <Link href="/farm" className={buttonClass.primary}>{t('profile.title')}</Link>
        </div>
      ) : (
        <FarmTimeline history={history} twin={twin} />
      )}
    </div>
  );
}
