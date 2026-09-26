'use client';

import { FarmProfileProvider } from '@/lib/farm-profile';
import { LanguageProvider } from '@/lib/i18n';

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <LanguageProvider>
      <FarmProfileProvider>{children}</FarmProfileProvider>
    </LanguageProvider>
  );
}
