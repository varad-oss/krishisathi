import type { Metadata, Viewport } from 'next';
import {
  Figtree,
  Fraunces,
  Noto_Sans_Bengali,
  Noto_Sans_Devanagari,
  Noto_Sans_Gujarati,
  Noto_Sans_Gurmukhi,
  Noto_Sans_Kannada,
  Noto_Sans_Malayalam,
  Noto_Sans_Tamil,
  Noto_Sans_Telugu,
} from 'next/font/google';
import './globals.css';
import Header from '@/components/layout/Header';
import Footer from '@/components/layout/Footer';
import MobileNav from '@/components/layout/MobileNav';
import OfflineStatus from '@/components/layout/OfflineStatus';
import Providers from './providers';

// Latin text: Figtree (body) and Fraunces (display). Indic scripts use Noto Sans for consistent matras and
// conjuncts across devices; those files have unicode-range subsets, so browsers only download the script
// actually on screen, and they are not preloaded.
const body = Figtree({ subsets: ['latin'], display: 'swap', variable: '--font-figtree' });
const display = Fraunces({ subsets: ['latin'], display: 'swap', variable: '--font-fraunces', axes: ['opsz'] });
const deva = Noto_Sans_Devanagari({ subsets: ['devanagari'], display: 'swap', preload: false, variable: '--font-deva' });
const beng = Noto_Sans_Bengali({ subsets: ['bengali'], display: 'swap', preload: false, variable: '--font-beng' });
const guru = Noto_Sans_Gurmukhi({ subsets: ['gurmukhi'], display: 'swap', preload: false, variable: '--font-guru' });
const gujr = Noto_Sans_Gujarati({ subsets: ['gujarati'], display: 'swap', preload: false, variable: '--font-gujr' });
const taml = Noto_Sans_Tamil({ subsets: ['tamil'], display: 'swap', preload: false, variable: '--font-taml' });
const telu = Noto_Sans_Telugu({ subsets: ['telugu'], display: 'swap', preload: false, variable: '--font-telu' });
const knda = Noto_Sans_Kannada({ subsets: ['kannada'], display: 'swap', preload: false, variable: '--font-knda' });
const mlym = Noto_Sans_Malayalam({ subsets: ['malayalam'], display: 'swap', preload: false, variable: '--font-mlym' });
const scripts = [deva, beng, guru, gujr, taml, telu, knda, mlym];

export const metadata: Metadata = {
  title: { default: 'KrishiSathi — Agricultural intelligence for climate-resilient farming', template: '%s · KrishiSathi' },
  description:
    'Explained, localized farm advice from weather forecasts, soil data, satellite signals and crop photos, with honest data provenance. Available in 10 Indian languages.',
  manifest: '/manifest.json',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#f4f1e8',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={[body.variable, display.variable, ...scripts.map((f) => f.variable)].join(' ')}>
      <body className="flex min-h-screen flex-col font-sans antialiased">
        <Providers>
          <Header />
          <OfflineStatus />
          <main id="main" className="flex flex-1 flex-col pb-20 md:pb-0">
            {children}
          </main>
          <Footer />
          <MobileNav />
        </Providers>
      </body>
    </html>
  );
}
