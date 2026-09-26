export default function Logo({ className = 'h-8 w-8' }: { className?: string }) {
  // Sprout inside a field-row circle: agriculture + growth, no emoji dependency.
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <circle cx="16" cy="16" r="15" fill="#2f6b3f" stroke="#b9d7b2" strokeWidth="1.5" />
      <path d="M6 23c3-1.2 6.5-1.8 10-1.8S23 21.8 26 23" stroke="#b9d7b2" strokeWidth="1.4" fill="none" strokeLinecap="round" />
      <path d="M16 21V13" stroke="#fff" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M16 15c-3.6 0-5.6-2-5.6-5.2 3.4 0 5.6 1.9 5.6 5.2Z" fill="#dcebd8" />
      <path d="M16 13.5c0-3.6 2.2-5.7 5.8-5.7 0 3.5-2.2 5.7-5.8 5.7Z" fill="#fff" />
    </svg>
  );
}
