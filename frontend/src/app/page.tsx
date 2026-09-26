'use client';

import Link from 'next/link';
import {
  ArrowRight, BarChart3, Bell, Camera, CheckCircle2, CloudSun, Cpu, Languages, Layers, Leaf, Satellite, ShieldCheck, Sprout, Users,
} from 'lucide-react';
import { buttonClass } from '@/components/ui';
import { useI18n } from '@/lib/i18n';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import type { MessageKey } from '@/locales/en';
import { cn } from '@/lib/utils';

const FEATURES: { key: string; icon: React.ElementType; href: string }[] = [
  { key: 'today', icon: Sprout, href: '/farm#today' },
  { key: 'diagnose', icon: Camera, href: '/diagnose' },
  { key: 'weather', icon: CloudSun, href: '/farm#weather' },
  { key: 'regen', icon: Leaf, href: '/farm#soil' },
  { key: 'alerts', icon: Bell, href: '/farm#alerts' },
  { key: 'policy', icon: BarChart3, href: '/dashboard' },
];

function WorkflowDiagram() {
  const { t } = useI18n();
  const signals = [
    { icon: CloudSun, label: 'wx' },
    { icon: Layers, label: 'soil' },
    { icon: Satellite, label: 'sat' },
    { icon: Camera, label: 'photo' },
    { icon: Users, label: 'reports' },
  ];
  const col = 'flex flex-1 flex-col rounded-2xl border border-line bg-surface p-5 shadow-[var(--shadow-card)]';
  return (
    <div className="flex flex-col items-stretch gap-3 lg:flex-row lg:items-center">
      <div className={col}>
        <p className="text-xs font-semibold uppercase tracking-wide text-leaf-700">1 · {t('landing.flow.signals')}</p>
        <div className="my-3 flex gap-2" aria-hidden>
          {signals.map((s) => (
            <span key={s.label} className="flex h-9 w-9 items-center justify-center rounded-lg bg-leaf-50 text-leaf-700">
              <s.icon className="h-4 w-4" />
            </span>
          ))}
        </div>
        <p className="text-sm text-ink-soft">{t('landing.flow.signalsBody')}</p>
      </div>
      <ArrowRight className="mx-auto h-5 w-5 rotate-90 text-line-strong lg:rotate-0" aria-hidden />
      <div className={col}>
        <p className="text-xs font-semibold uppercase tracking-wide text-leaf-700">2 · {t('landing.flow.reasoning')}</p>
        <div className="my-3 flex gap-2" aria-hidden>
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-50 text-sky-700"><Cpu className="h-4 w-4" /></span>
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-50 text-sky-700"><ShieldCheck className="h-4 w-4" /></span>
        </div>
        <p className="text-sm text-ink-soft">{t('landing.flow.reasoningBody')}</p>
      </div>
      <ArrowRight className="mx-auto h-5 w-5 rotate-90 text-line-strong lg:rotate-0" aria-hidden />
      <div className={cn(col, 'border-leaf-200 bg-leaf-50')}>
        <p className="text-xs font-semibold uppercase tracking-wide text-leaf-700">3 · {t('landing.flow.action')}</p>
        <div className="my-3 flex gap-2" aria-hidden>
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface text-leaf-700"><CheckCircle2 className="h-4 w-4" /></span>
        </div>
        <p className="text-sm text-ink-soft">{t('landing.flow.actionBody')}</p>
      </div>
    </div>
  );
}

export default function Home() {
  const { t } = useI18n();
  return (
    <div className="flex-1">
      <section className="relative overflow-hidden bg-leaf-900 text-white">
        <svg aria-hidden className="absolute inset-x-0 bottom-0 h-24 w-full text-leaf-700/40" viewBox="0 0 1200 100" preserveAspectRatio="none">
          <path d="M0 70 C 200 40, 400 40, 600 60 S 1000 90, 1200 55 V100 H0Z" fill="currentColor" />
          <path d="M0 85 C 250 65, 500 70, 700 82 S 1050 95, 1200 80 V100 H0Z" fill="currentColor" opacity="0.6" />
        </svg>
        <div className="relative mx-auto max-w-6xl px-4 pb-20 pt-14 sm:px-6 sm:pt-20">
          <p className="inline-flex items-center gap-2 rounded-full bg-leaf-700/70 px-3 py-1 text-xs font-medium text-leaf-100 ring-1 ring-leaf-500/50">
            <Sprout className="h-3.5 w-3.5" aria-hidden /> {t('landing.badge')}
          </p>
          <h1 className="mt-5 max-w-3xl text-3xl font-semibold leading-tight tracking-tight sm:text-5xl sm:leading-[1.1]">{t('landing.title')}</h1>
          <p className="mt-5 max-w-2xl text-base text-leaf-100 sm:text-lg">{t('landing.subtitle')}</p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Link href="/farm" className={cn(buttonClass.primary, 'bg-white text-leaf-900 hover:bg-leaf-50')}>
              <Sprout className="h-4 w-4" aria-hidden /> {t('landing.ctaFarm')}
            </Link>
            <Link href="/diagnose" className={cn(buttonClass.secondary, 'border-leaf-500 bg-transparent text-white hover:border-white hover:text-white')}>
              <Camera className="h-4 w-4" aria-hidden /> {t('landing.ctaDiagnose')}
            </Link>
            <Link href="/dashboard" className={cn(buttonClass.ghost, 'text-leaf-100 hover:bg-leaf-700/60')}>
              {t('landing.ctaPolicy')} <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-14 sm:px-6" aria-labelledby="how-title">
        <h2 id="how-title" className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('landing.flow.title')}</h2>
        <p className="mb-8 mt-2 text-ink-soft">{t('landing.flow.subtitle')}</p>
        <WorkflowDiagram />
      </section>

      <section className="border-y border-line bg-surface" aria-labelledby="features-title">
        <div className="mx-auto max-w-6xl px-4 py-14 sm:px-6">
          <h2 id="features-title" className="mb-8 text-2xl font-semibold tracking-tight sm:text-3xl">{t('landing.features.title')}</h2>
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map((f) => (
              <li key={f.key}>
                <Link href={f.href} className="group flex h-full flex-col rounded-2xl border border-line bg-paper p-5 transition-colors hover:border-leaf-500 hover:bg-surface">
                  <f.icon className="h-6 w-6 text-leaf-600" aria-hidden />
                  <h3 className="mt-3 font-semibold">{t(`landing.feature.${f.key}.title` as MessageKey)}</h3>
                  <p className="mt-1 flex-1 text-sm text-ink-soft">{t(`landing.feature.${f.key}.body` as MessageKey)}</p>
                  <ArrowRight className="mt-3 h-4 w-4 text-leaf-600 transition-transform group-hover:translate-x-1" aria-hidden />
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="mx-auto grid max-w-6xl gap-5 px-4 py-14 sm:px-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-line bg-surface p-6" aria-labelledby="trust-title">
          <ShieldCheck className="h-7 w-7 text-leaf-600" aria-hidden />
          <h2 id="trust-title" className="mt-3 text-xl font-semibold">{t('landing.trust.title')}</h2>
          <p className="mt-2 text-ink-soft">{t('landing.trust.body')}</p>
          <ul className="mt-4 space-y-2 text-sm">
            {(['landing.trust.point1', 'landing.trust.point2', 'landing.trust.point3', 'landing.trust.point4'] as const).map((k) => (
              <li key={k} className="flex items-start gap-2">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-leaf-600" aria-hidden /> {t(k)}
              </li>
            ))}
          </ul>
          <Link href="/about" className={cn(buttonClass.ghost, 'mt-4 -ml-3')}>
            {t('nav.about')} <ArrowRight className="h-4 w-4" aria-hidden />
          </Link>
        </div>
        <div className="rounded-2xl border border-line bg-surface p-6" aria-labelledby="lang-title">
          <Languages className="h-7 w-7 text-leaf-600" aria-hidden />
          <h2 id="lang-title" className="mt-3 text-xl font-semibold">{t('landing.lang.title')}</h2>
          <p className="mt-2 text-ink-soft">{t('landing.lang.body')}</p>
          <ul className="mt-4 flex flex-wrap gap-2">
            {SUPPORTED_LANGUAGES.map((l) => (
              <li key={l.code} lang={l.code} className="rounded-full bg-paper px-3 py-1 text-sm ring-1 ring-line">
                {l.nativeName}
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="bg-leaf-50" aria-labelledby="cta-title">
        <div className="mx-auto flex max-w-6xl flex-col items-start gap-4 px-4 py-12 sm:px-6 md:flex-row md:items-center md:justify-between">
          <div>
            <h2 id="cta-title" className="text-2xl font-semibold tracking-tight">{t('landing.cta.title')}</h2>
            <p className="mt-1 text-ink-soft">{t('landing.cta.body')}</p>
          </div>
          <Link href="/farm" className={buttonClass.primary}>
            {t('landing.ctaFarm')} <ArrowRight className="h-4 w-4" aria-hidden />
          </Link>
        </div>
      </section>
    </div>
  );
}
