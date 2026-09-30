'use client';

import Link from 'next/link';
import { ArrowRight, Bug, Camera, CloudRain, Droplets, HelpCircle, Layers, Sprout } from 'lucide-react';
import { PageHeader } from '@/components/ui';
import { useI18n } from '@/lib/i18n';
import type { MessageKey } from '@/locales/en';

/**
 * "Something is wrong with my crop": one question, seven plain answers, each routed to the existing tool that
 * handles it (photo check, farm risks, soil, or the advisor with a starting question). No new diagnosis logic.
 */
const PROBLEMS: { id: string; icon: React.ElementType; href: string }[] = [
  { id: 'photo', icon: Camera, href: '/diagnose' },
  { id: 'pest', icon: Bug, href: '/diagnose' },
  { id: 'weather', icon: CloudRain, href: '/farm#weather' },
  { id: 'water', icon: Droplets, href: '/farm#risks' },
  { id: 'notGrowing', icon: Sprout, href: '/advisor?topic=notGrowing' },
  { id: 'soil', icon: Layers, href: '/farm#soil' },
  { id: 'unknown', icon: HelpCircle, href: '/advisor?topic=unknown' },
];

export default function ProblemPage() {
  const { t } = useI18n();
  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-12 pt-6 sm:px-6 sm:pt-10">
      <PageHeader title={t('problem.title')} subtitle={t('problem.subtitle')} />
      <ul className="grid gap-3 sm:grid-cols-2">
        {PROBLEMS.map((p) => (
          <li key={p.id}>
            <Link
              href={p.href}
              className="group flex h-full min-h-[4.5rem] items-start gap-4 rounded-[var(--radius-card)] bg-surface p-4 ring-1 ring-line transition-[box-shadow,background-color] hover:bg-leaf-50/60 hover:ring-leaf-500"
            >
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-leaf-50 text-leaf-700">
                <p.icon className="h-5 w-5" aria-hidden />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block font-semibold leading-snug">{t(`problem.${p.id}.title` as MessageKey)}</span>
                <span className="mt-0.5 block text-sm text-ink-soft">{t(`problem.${p.id}.body` as MessageKey)}</span>
              </span>
              <ArrowRight className="mt-1 h-4 w-4 shrink-0 text-leaf-600 transition-transform group-hover:translate-x-0.5" aria-hidden />
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-6 text-sm text-ink-soft">{t('problem.urgent')}</p>
    </div>
  );
}
