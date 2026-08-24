'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Globe } from 'lucide-react';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { SUPPORTED_LANGUAGES } from '@/lib/languages';
import { useLanguage } from '@/lib/LanguageContext';

export default function Header() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLangMenuOpen, setIsLangMenuOpen] = useState(false);
  const { language, setLanguage } = useLanguage();

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Diagnose', path: '/diagnose' },
    { name: 'Chat', path: '/chat' },
    { name: 'Map', path: '/map' },
    { name: 'Dashboard', path: '/dashboard' },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-green-900 text-white shadow-sm">
      <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-2xl">🌾</span>
            <span className="text-xl font-bold tracking-tight">KrishiSathi</span>
          </Link>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <Link
              key={link.name}
              href={link.path}
              className={cn(
                "text-sm font-medium transition-colors hover:text-green-200",
                pathname === link.path ? "text-green-200 font-semibold" : "text-white"
              )}
            >
              {link.name}
            </Link>
          ))}
          
          {/* Language Selector */}
          <div className="relative">
            <button 
              onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
              className="flex items-center gap-1 text-sm font-medium hover:text-green-200"
            >
              <Globe className="h-4 w-4" />
              {SUPPORTED_LANGUAGES.find(l => l.code === language)?.nativeName}
            </button>
            
            {isLangMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5">
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setLanguage(lang.code);
                      setIsLangMenuOpen(false);
                    }}
                    className={cn(
                      "block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-green-50",
                      language === lang.code ? "bg-green-100 font-semibold" : ""
                    )}
                  >
                    {lang.nativeName} ({lang.name})
                  </button>
                ))}
              </div>
            )}
          </div>
        </nav>

        {/* Mobile menu button */}
        <div className="flex items-center md:hidden">
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="text-white hover:text-green-200 focus:outline-none"
          >
            {isMobileMenuOpen ? (
              <X className="h-6 w-6" aria-hidden="true" />
            ) : (
              <Menu className="h-6 w-6" aria-hidden="true" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-green-800 border-t border-green-700">
          <div className="space-y-1 px-4 pb-3 pt-2">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                href={link.path}
                onClick={() => setIsMobileMenuOpen(false)}
                className={cn(
                  "block rounded-md px-3 py-2 text-base font-medium",
                  pathname === link.path
                    ? "bg-green-700 text-white"
                    : "text-green-100 hover:bg-green-700 hover:text-white"
                )}
              >
                {link.name}
              </Link>
            ))}
            <div className="mt-4 pt-4 border-t border-green-700">
              <p className="px-3 text-xs font-semibold text-green-300 uppercase tracking-wider mb-2">Language</p>
              <div className="grid grid-cols-2 gap-2 px-2">
                {SUPPORTED_LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setLanguage(lang.code);
                      setIsMobileMenuOpen(false);
                    }}
                    className={cn(
                      "text-left rounded-md px-3 py-2 text-sm",
                      language === lang.code
                        ? "bg-green-700 text-white"
                        : "text-green-100 hover:bg-green-700 hover:text-white"
                    )}
                  >
                    {lang.nativeName}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
