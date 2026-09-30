export default function Logo({ className = 'h-8 w-8' }: { className?: string }) {
  // A sprout over two furrows: agriculture and growth, legible at favicon size.
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden>
      <rect width="32" height="32" rx="9" fill="#2b673b" />
      <path d="M6 24.5c3.2-1.3 6.6-1.9 10-1.9s6.8.6 10 1.9M8.5 28c2.4-.7 4.9-1 7.5-1s5.1.3 7.5 1" stroke="#b3cfb5" strokeWidth="1.4" fill="none" strokeLinecap="round" />
      <path d="M16 22.5V13.5" stroke="#fff" strokeWidth="1.9" strokeLinecap="round" />
      <path d="M16 15.6c-3.8 0-5.9-2.1-5.9-5.5 3.6 0 5.9 2 5.9 5.5Z" fill="#d9e8d9" />
      <path d="M16 14c0-3.8 2.3-6 6.1-6 0 3.7-2.3 6-6.1 6Z" fill="#fff" />
    </svg>
  );
}
