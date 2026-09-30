'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import { NAV_ITEMS, isActive } from './nav';

/** Bottom tab bar on phones: every farmer destination is one thumb-tap away, and the current one is unmistakable. */
export default function MobileNav() {
  const pathname = usePathname();
  const { t } = useI18n();
  return (
    <nav aria-label={t('nav.menu')} className="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface pb-[env(safe-area-inset-bottom)] shadow-[0_-8px_24px_-18px_rgb(26_30_26/0.35)] md:hidden">
      <ul className="mx-auto grid max-w-lg grid-cols-5">
        {NAV_ITEMS.map((item) => {
          const active = isActive(pathname, item);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={active ? 'page' : undefined}
                aria-label={t(item.label)}
                className={cn(
                  'relative flex min-h-[4.25rem] flex-col items-center justify-center gap-1 px-0 pb-1.5 pt-2 text-[0.72rem] leading-tight transition-colors',
                  active ? 'font-semibold text-leaf-700' : 'font-medium text-ink-soft',
                )}
              >
                {active && <span aria-hidden className="absolute inset-x-3 top-0 h-[3px] rounded-b bg-leaf-600" />}
                <span className={cn('flex h-8 w-12 items-center justify-center rounded-full transition-colors', active && 'bg-leaf-100')}>
                  <item.icon className={cn('h-[1.35rem] w-[1.35rem]', active && 'stroke-[2.3]')} aria-hidden />
                </span>
                <span aria-hidden className="line-clamp-2 max-w-full text-center [overflow-wrap:normal] [word-break:keep-all]">{t(item.short)}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
