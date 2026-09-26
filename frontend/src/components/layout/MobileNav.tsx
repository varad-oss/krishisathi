'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useI18n } from '@/lib/i18n';
import { cn } from '@/lib/utils';
import { NAV_ITEMS, isActive } from './nav';

/** Bottom tab bar on phones: the main farmer tasks stay one thumb-tap away. */
export default function MobileNav() {
  const pathname = usePathname();
  const { t } = useI18n();
  return (
    <nav aria-label={t('nav.menu')} className="fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface/95 backdrop-blur md:hidden">
      <ul className="mx-auto grid max-w-md grid-cols-4">
        {NAV_ITEMS.filter((i) => i.mobile).map((item) => {
          const active = isActive(pathname, item.href);
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                aria-current={active ? 'page' : undefined}
                className={cn(
                  'flex min-h-16 flex-col items-center justify-center gap-1 px-1 text-[11px] font-medium leading-tight',
                  active ? 'text-leaf-700' : 'text-ink-faint',
                )}
              >
                <item.icon className={cn('h-5 w-5', active && 'stroke-[2.4]')} aria-hidden />
                <span className="line-clamp-2 text-center">{t(item.label)}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
