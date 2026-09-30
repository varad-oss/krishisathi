import { Camera, CircleEllipsis, History, MessageCircle, Sprout } from 'lucide-react';
import type { MessageKey } from '@/locales/en';

/** The five farmer destinations, identical on phone (bottom bar) and desktop (header). */
/** `short` is the one-word label for the phone tab bar; `label` is used in the desktop header and as the accessible name. */
export const NAV_ITEMS: { href: string; label: MessageKey; short: MessageKey; icon: typeof Sprout; also?: string[] }[] = [
  { href: '/farm', label: 'nav.farm', short: 'nav.short.farm', icon: Sprout },
  { href: '/diagnose', label: 'nav.diagnose', short: 'nav.short.diagnose', icon: Camera, also: ['/problem'] },
  { href: '/advisor', label: 'nav.advisor', short: 'nav.short.advisor', icon: MessageCircle },
  { href: '/history', label: 'farm.section.history', short: 'nav.short.history', icon: History },
  // Settings, methods and the officers' dashboard live behind "More" so they never compete with daily tasks.
  { href: '/more', label: 'nav.more', short: 'nav.more', icon: CircleEllipsis, also: ['/about', '/dashboard'] },
];

const under = (pathname: string, href: string) => pathname === href || pathname.startsWith(`${href}/`);

export const isActive = (pathname: string, item: { href: string; also?: string[] }) =>
  under(pathname, item.href) || !!item.also?.some((p) => under(pathname, p));
