export default function Loading() {
  return (
    <div role="status" className="mx-auto w-full max-w-5xl space-y-3 px-4 py-8">
      <span className="sr-only">Loading</span>
      <div className="h-8 w-1/3 animate-pulse rounded-lg bg-line/70" />
      <div className="h-40 animate-pulse rounded-2xl bg-line/50" />
      <div className="h-40 animate-pulse rounded-2xl bg-line/50" />
    </div>
  );
}
