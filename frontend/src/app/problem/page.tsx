'use client';

import Link from 'next/link';
import { Bug, Camera, ChevronRight, CircleDot, CloudRain, Droplets, HelpCircle, Layers, Leaf, Sprout, Sun } from 'lucide-react';
import { PageHeader } from '@/components/ui';
import { useI18n } from '@/lib/i18n';
import type { MessageKey } from '@/locales/en';

/**
 * "Something is wrong with my crop": one question, plain answers grouped by where the farmer is looking, each
 * routed to the existing tool that handles it (photo check, farm risks, soil, or the advisor with a starting
 * question). No new diagnosis logic.
 */
type Problem = { id: string; icon: React.ElementType; href: string };

const ON_PLANT: Problem[] = [
  { id: 'spots', icon: CircleDot, href: '/diagnose' },
  { id: 'leaves', icon: Leaf, href: '/diagnose' },
  { id: 'pest', icon: Bug, href: '/diagnose' },
];

const IN_FIELD: Problem[] = [
  { id: 'drying', icon: Sun, href: '/farm#risks' },
  { id: 'notGrowing', icon: Sprout, href: '/advisor?topic=notGrowing' },
  { id: 'water', icon: Droplets, href: '/farm#risks' },
  { id: 'weather', icon: CloudRain, href: '/farm#weather' },
  { id: 'soil', icon: Layers, href: '/farm#soil' },
];

function ProblemLink({ p }: { p: Problem }) {
  const { t } = useI18n();
  return (
    <li>
      <Link href={p.href} className="group flex min-h-[4.5rem] items-start gap-4 py-4 transition-colors hover:bg-surface sm:px-3">
        <span aria-hidden className="flex h-11 w-11 shrink-0 items-center justify-center rounded-[var(--radius-inner)] bg-leaf-50 text-leaf-700">
          <p.icon className="h-5 w-5" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-[1.05rem] font-semibold leading-snug">{t(`problem.${p.id}.title` as MessageKey)}</span>
          <span className="mt-0.5 block text-ink-soft">{t(`problem.${p.id}.body` as MessageKey)}</span>
        </span>
        <ChevronRight className="mt-3 h-5 w-5 shrink-0 text-ink-faint transition-transform group-hover:translate-x-0.5" aria-hidden />
      </Link>
    </li>
  );
}

export default function ProblemPage() {
  const { t } = useI18n();
  return (
    <div className="mx-auto w-full max-w-2xl px-4 pb-12 pt-8 sm:px-6 sm:pt-12">
      <PageHeader title={t('problem.title')} subtitle={t('problem.subtitle')} />

      {/* The quickest route for most problems: show us. */}
      <Link href="/diagnose" className="group flex items-center gap-4 rounded-[var(--radius-card)] bg-leaf-700 p-5 text-white transition-colors hover:bg-leaf-900 sm:p-6">
        <span aria-hidden className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-white/15">
          <Camera className="h-7 w-7" />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block text-xl font-semibold">{t('problem.photo.title')}</span>
          <span className="mt-0.5 block text-leaf-100">{t('problem.photo.body')}</span>
        </span>
        <ChevronRight className="h-6 w-6 shrink-0 transition-transform group-hover:translate-x-0.5" aria-hidden />
      </Link>

      <section aria-labelledby="problem-plant" className="mt-10">
        <h2 id="problem-plant" className="font-display text-lg">{t('problem.group.plant')}</h2>
        <ul className="mt-2 divide-y divide-line border-y border-line">
          {ON_PLANT.map((p) => <ProblemLink key={p.id} p={p} />)}
        </ul>
      </section>

      <section aria-labelledby="problem-field" className="mt-10">
        <h2 id="problem-field" className="font-display text-lg">{t('problem.group.field')}</h2>
        <ul className="mt-2 divide-y divide-line border-y border-line">
          {IN_FIELD.map((p) => <ProblemLink key={p.id} p={p} />)}
        </ul>
      </section>

      <ul className="mt-6">
        <ProblemLink p={{ id: 'unknown', icon: HelpCircle, href: '/advisor?topic=unknown' }} />
      </ul>

      <p className="mt-8 rounded-[var(--radius-inner)] border-l-4 border-warn-500 bg-warn-50 p-4 text-ink">{t('problem.urgent')}</p>
    </div>
  );
}
