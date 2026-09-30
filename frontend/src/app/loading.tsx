export default function Loading() {
  return (
    <div role="status" className="mx-auto w-full max-w-6xl space-y-4 px-4 py-10 sm:px-6">
      <span className="sr-only">Loading</span>
      <div className="h-4 w-40 animate-pulse rounded-md bg-paper-deep" />
      <div className="h-10 w-2/3 animate-pulse rounded-md bg-paper-deep" />
      <div className="h-32 animate-pulse rounded-[var(--radius-card)] bg-paper-deep/70" />
    </div>
  );
}
