'use client';

import { useState } from 'react';
import Link from 'next/link';
import { BarChart3, BookOpen, ChevronRight, Code2, MapPin, Sprout } from 'lucide-react';
import FarmProfileForm, { useLocationLabel } from '@/components/FarmProfileForm';
import LanguageSelect from '@/components/layout/LanguageSelect';
import { buttonClass, LoadingBlock, PageHeader } from '@/components/ui';
import { useFarmProfile } from '@/lib/farm-profile';
import { useI18n } from '@/lib/i18n';
import type { MessageKey } from '@/locales/en';

function Row({ href, icon: Icon, title, body, external }: { href: string; icon: React.ElementType; title: string; body: string; external?: boolean }) {
  const inner = (
    <>
      <Icon className="mt-0.5 h-5 w-5 shrink-0 text-ink-soft" aria-hidden />
      <span className="min-w-0 flex-1">
        <span className="block font-semibold">{title}</span>
        <span className="mt-0.5 block text-sm text-ink-soft">{body}</span>
      </span>
      <ChevronRight className="mt-0.5 h-5 w-5 shrink-0 text-ink-faint" aria-hidden />
    </>
  );
  const cls = 'flex items-start gap-3 py-4 transition-colors hover:text-leaf-700';
  return (
    <li>
      {external ? <a href={href} target="_blank" rel="noopener noreferrer" className={cls}>{inner}</a> : <Link href={href} className={cls}>{inner}</Link>}
    </li>
  );
}

/** Settings and everything that is not a daily farm task: farm details, language, methods, the officers' view. */
export default function MorePage() {
  const { t, fmt } = useI18n();
  const { profile, ready } = useFarmProfile();
  const locationLabel = useLocationLabel();
  const [editing, setEditing] = useState(false);
  const block = 'border-t border-line py-7';
  const label = 'mb-3 text-sm font-semibold text-ink-soft';

  return (
    <div className="mx-auto w-full max-w-2xl px-4 pb-12 pt-8 sm:px-6 sm:pt-12">
      <PageHeader title={t('more.title')} subtitle={t('more.subtitle')} />

      <section aria-labelledby="more-farm" className={block}>
        <h2 id="more-farm" className={label}>{t('farm.title')}</h2>
        {!ready ? (
          <LoadingBlock lines={2} />
        ) : editing || !profile.location ? (
          <FarmProfileForm onDone={() => setEditing(false)} onCancel={profile.location ? () => setEditing(false) : undefined} />
        ) : (
          <div className="flex flex-wrap items-start justify-between gap-4">
            <dl className="space-y-2">
              <div className="flex items-center gap-2">
                <dt className="sr-only">{t('profile.location')}</dt>
                <MapPin className="h-4 w-4 text-leaf-600" aria-hidden />
                <dd className="font-semibold">{locationLabel(profile.location)}</dd>
              </div>
              <div className="flex items-center gap-2 text-ink-soft">
                <dt className="sr-only">{t('profile.crop')}</dt>
                <Sprout className="h-4 w-4 text-leaf-600" aria-hidden />
                <dd>
                  {profile.crop ? t(`crop.${profile.crop}` as MessageKey) : t('profile.cropNone')}
                  {profile.sowingDate && ` · ${fmt.date(profile.sowingDate, { day: 'numeric', month: 'long', year: 'numeric' })}`}
                </dd>
              </div>
            </dl>
            <button type="button" onClick={() => setEditing(true)} className={buttonClass.secondary}>
              {t('action.change')}
            </button>
          </div>
        )}
      </section>

      <section aria-labelledby="more-lang" className={block}>
        <h2 id="more-lang" className={label}>{t('nav.language')}</h2>
        <LanguageSelect large className="max-w-xs" />
        <p className="mt-2 text-sm text-ink-soft">{t('landing.lang.body')}</p>
      </section>

      <section aria-labelledby="more-about" className={block}>
        <h2 id="more-about" className="sr-only">{t('nav.about')}</h2>
        <ul className="divide-y divide-line">
          <Row href="/about" icon={BookOpen} title={t('nav.about')} body={t('about.subtitle')} />
          <Row href="https://github.com/varad-oss/krishisathi" icon={Code2} title={t('footer.code')} body={t('footer.built')} external />
        </ul>
      </section>

      {/* The officers' view is deliberately set apart from the farmer's daily tasks. */}
      <section aria-labelledby="more-officers" className="rounded-[var(--radius-card)] border border-line bg-surface px-5">
        <h2 id="more-officers" className="pt-5 text-sm font-semibold text-ink-soft">{t('more.officers')}</h2>
        <ul>
          <Row href="/dashboard" icon={BarChart3} title={t('nav.policy')} body={t('more.officersBody')} />
        </ul>
      </section>
    </div>
  );
}
