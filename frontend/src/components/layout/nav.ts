import { BarChart3, Camera, Home, MessageCircle, Sprout } from 'lucide-react';
import type { MessageKey } from '@/locales/en';

export const NAV_ITEMS: { href: string; label: MessageKey; icon: typeof Home; mobile: boolean }[] = [
  { href: '/farm', label: 'nav.farm', icon: Sprout, mobile: true },
  { href: '/diagnose', label: 'nav.diagnose', icon: Camera, mobile: true },
  { href: '/advisor', label: 'nav.advisor', icon: MessageCircle, mobile: true },
  { href: '/dashboard', label: 'nav.policy', icon: BarChart3, mobile: true },
];

export const isActive = (pathname: string, href: string) => pathname === href || pathname.startsWith(`${href}/`);
