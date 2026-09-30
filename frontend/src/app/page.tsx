'use client';

import Link from 'next/link';
import { ArrowRight, BarChart3, Bell, Camera, CheckCircle2, ChevronRight, CloudSun, Leaf, Sprout } from 'lucide-react';
import { buttonClass } from '@/components/ui';
import { useI18n } from '@/lib/i18n';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';

const FEATURES: { key: string; icon: React.ElementType; href: string }[] = [
  { key: 'today', icon: Sprout, href: '/farm#today' },
  { key: 'diagnose', icon: Camera, href: '/problem' },
  { key: 'weather', icon: CloudSun, href: '/farm#weather' },
  { key: 'regen', icon: Leaf, href: '/farm#soil' },
  { key: 'alerts', icon: Bell, href: '/farm#risks' },
  { key: 'policy', icon: BarChart3, href: '/dashboard' },
];

const STEPS = [
  { title: 'landing.flow.signals', body: 'landing.flow.signalsBody' },
  { title: 'landing.flow.reasoning', body: 'landing.flow.reasoningBody' },
  { title: 'landing.flow.action', body: 'landing.flow.actionBody' },
] as const;

/**
 * A calm field at the start of the day: sky, sun, ploughed rows running to the horizon and a few stalks that
 * move gently (the sway stops for people who prefer reduced motion). Decorative only.
 */
function FieldScene({ className }: { className?: string }) {
  const stalks = [40, 78, 118, 300, 338, 372];
  return (
    <svg viewBox="0 0 420 300" aria-hidden className={cn('h-auto w-full', className)} preserveAspectRatio="xMidYMax slice">
      <rect width="420" height="300" fill="var(--color-sky-50)" />
      <circle cx="318" cy="92" r="30" fill="var(--color-watch-200)" />
      <path d="M0 150 C 90 128, 190 140, 260 132 S 380 124, 420 134 V300 H0Z" fill="var(--color-leaf-200)" />
      <path d="M0 176 C 120 158, 250 170, 420 156 V300 H0Z" fill="var(--color-leaf-500)" opacity="0.55" />
      <path d="M0 200 C 140 186, 280 194, 420 182 V300 H0Z" fill="var(--color-soil-100)" />
      {/* Rows converge on the horizon to give the field depth. */}
      {Array.from({ length: 9 }, (_, i) => {
        const x = -60 + i * 68;
        const top = 210 + (x - 210) * 0.08;
        return (
          <g key={i}>
            <path d={`M${top} 190 L${x} 300`} stroke="var(--color-soil-500)" strokeOpacity="0.25" strokeWidth="2" />
            {/* Young crop along each row, smaller towards the horizon. */}
            {[0.25, 0.45, 0.65, 0.85].map((f) => {
              const cx = top + (x - top) * f;
              const cy = 190 + 110 * f;
              const s = 1 + f * 2.2;
              return <path key={f} d={`M${cx} ${cy} q ${-2 * s} ${-3 * s} ${-3 * s} ${-5 * s} M${cx} ${cy} q ${2 * s} ${-3 * s} ${3 * s} ${-5 * s} M${cx} ${cy} v ${-6 * s}`} stroke="var(--color-leaf-600)" strokeWidth={0.6 + f} fill="none" strokeLinecap="round" />;
            })}
          </g>
        );
      })}
      {stalks.map((x, i) => (
        <g key={x} className="origin-bottom animate-sway" style={{ transformBox: 'fill-box', animationDelay: `${-i * 1.3}s` }}>
          <path d={`M${x} 300 C ${x - 1} 276, ${x + 2} 250, ${x + 1} 214`} stroke="var(--color-leaf-700)" strokeWidth="2" fill="none" strokeLinecap="round" />
          <path d={`M${x} 272 C ${x - 12} 262, ${x - 18} 250, ${x - 22} 236`} stroke="var(--color-leaf-600)" strokeWidth="2" fill="none" strokeLinecap="round" />
          {/* Wheat ear: paired grains up the tip, with short awns. */}
          {[0, 1, 2, 3, 4].map((g) => (
            <g key={g}>
              <ellipse cx={x - 2.2} cy={214 - g * 5} rx="2" ry="3.6" transform={`rotate(-22 ${x - 2.2} ${214 - g * 5})`} fill="var(--color-watch-500)" />
              <ellipse cx={x + 3.2} cy={212 - g * 5} rx="2" ry="3.6" transform={`rotate(22 ${x + 3.2} ${212 - g * 5})`} fill="var(--color-watch-500)" />
            </g>
          ))}
          <path d={`M${x + 1} 190 l -4 -12 M${x + 1} 190 l 4 -12 M${x + 1} 190 v -13`} stroke="var(--color-watch-700)" strokeWidth="0.8" strokeLinecap="round" />
        </g>
      ))}
    </svg>
  );
}

export default function Home() {
  const { t } = useI18n();
  return (
    <div className="flex-1">
      <section aria-labelledby="hero-title" className="border-b border-line">
        <div className="mx-auto grid max-w-6xl items-center gap-10 px-4 pb-12 pt-10 sm:px-6 sm:pt-16 lg:grid-cols-[1.1fr_1fr] lg:gap-14 lg:pb-20 lg:pt-20">
          <div className="min-w-0">
            <p className="flex items-center gap-2 text-sm font-medium text-leaf-700">
              <Sprout className="h-4 w-4" aria-hidden /> {t('landing.badge')}
            </p>
            <h1 id="hero-title" className="mt-4 font-display text-[2.1rem] leading-[1.1] tracking-tight sm:text-5xl lg:text-[3.4rem]">
              {t('landing.title')}
            </h1>
            <p className="mt-5 max-w-xl text-lg text-ink-soft">{t('landing.subtitle')}</p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Link href="/farm" className={cn(buttonClass.primary, 'min-h-12 px-5 text-base')}>
                <Sprout className="h-5 w-5" aria-hidden /> {t('landing.ctaFarm')}
              </Link>
              <Link href="/problem" className={cn(buttonClass.secondary, 'min-h-12 px-5 text-base')}>
                <Camera className="h-5 w-5" aria-hidden /> {t('problem.cta')}
              </Link>
            </div>
            <Link href="/dashboard" className="mt-5 inline-flex min-h-11 items-center gap-1.5 text-sm font-semibold text-ink-soft underline-offset-4 hover:text-leaf-700 hover:underline">
              {t('landing.ctaPolicy')} <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
          </div>
          <div className="overflow-hidden rounded-[var(--radius-card)] ring-1 ring-line">
            <FieldScene className="max-h-[22rem]" />
          </div>
        </div>
      </section>

      <section aria-labelledby="how-title" className="mx-auto max-w-6xl px-4 py-14 sm:px-6 sm:py-20">
        <h2 id="how-title" className="font-display text-2xl tracking-tight sm:text-3xl">{t('landing.flow.title')}</h2>
        <p className="mt-2 max-w-2xl text-ink-soft">{t('landing.flow.subtitle')}</p>
        <ol className="mt-10 grid gap-8 lg:grid-cols-3 lg:gap-10">
          {STEPS.map((s, i) => (
            <li key={s.title} className="relative border-t-2 border-line pt-5 first:border-leaf-600">
              <span className="font-display text-sm font-semibold tabular-nums text-leaf-700">{String(i + 1).padStart(2, '0')}</span>
              <h3 className="mt-1 text-lg font-semibold">{t(s.title)}</h3>
              <p className="mt-2 text-ink-soft">{t(s.body)}</p>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="features-title" className="border-y border-line bg-surface">
        <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6 sm:py-20">
          <h2 id="features-title" className="font-display text-2xl tracking-tight sm:text-3xl">{t('landing.features.title')}</h2>
          <ul className="mt-8 grid border-t border-line sm:grid-cols-2 sm:gap-x-10">
            {FEATURES.map((f) => (
              <li key={f.key} className="border-b border-line">
                <Link href={f.href} className="group flex min-h-[5rem] items-start gap-4 py-5">
                  <f.icon className="mt-0.5 h-6 w-6 shrink-0 text-leaf-600" aria-hidden />
                  <span className="min-w-0 flex-1">
                    <span className="block font-semibold leading-snug">{t(`landing.feature.${f.key}.title` as MessageKey)}</span>
                    <span className="mt-1 block text-ink-soft">{t(`landing.feature.${f.key}.body` as MessageKey)}</span>
                  </span>
                  <ChevronRight className="mt-0.5 h-5 w-5 shrink-0 text-ink-faint transition-transform group-hover:translate-x-0.5" aria-hidden />
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-12 px-4 py-14 sm:px-6 sm:py-20 lg:grid-cols-2 lg:gap-16">
        <div aria-labelledby="trust-title">
          <h2 id="trust-title" className="font-display text-2xl tracking-tight">{t('landing.trust.title')}</h2>
          <p className="mt-3 text-ink-soft">{t('landing.trust.body')}</p>
          <ul className="mt-6 space-y-3">
            {(['landing.trust.point1', 'landing.trust.point2', 'landing.trust.point3', 'landing.trust.point4'] as const).map((k) => (
              <li key={k} className="flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-leaf-600" aria-hidden /> {t(k)}
              </li>
            ))}
          </ul>
          <Link href="/about" className="mt-6 inline-flex min-h-11 items-center gap-1.5 font-semibold text-leaf-700 underline-offset-4 hover:underline">
            {t('nav.about')} <ArrowRight className="h-4 w-4" aria-hidden />
          </Link>
        </div>
        <div aria-labelledby="lang-title" className="lg:border-l lg:border-line lg:pl-16">
          <h2 id="lang-title" className="font-display text-2xl tracking-tight">{t('landing.lang.title')}</h2>
          <p className="mt-3 text-ink-soft">{t('landing.lang.body')}</p>
          <ul className="mt-6 flex flex-wrap gap-2">
            {SUPPORTED_LANGUAGES.map((l) => (
              <li key={l.code} lang={l.code} className="rounded-full bg-surface px-3.5 py-1.5 ring-1 ring-line">
                {l.nativeName}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section aria-labelledby="cta-title" className="border-t border-line bg-leaf-50/60">
        <div className="mx-auto flex max-w-6xl flex-col items-start gap-5 px-4 py-12 sm:px-6 md:flex-row md:items-center md:justify-between">
          <div className="min-w-0">
            <h2 id="cta-title" className="font-display text-2xl tracking-tight">{t('landing.cta.title')}</h2>
            <p className="mt-1 text-ink-soft">{t('landing.cta.body')}</p>
          </div>
          <Link href="/farm" className={cn(buttonClass.primary, 'min-h-12 px-5 text-base')}>
            {t('landing.ctaFarm')} <ArrowRight className="h-5 w-5" aria-hidden />
          </Link>
        </div>
      </section>
    </div>
  );
}
