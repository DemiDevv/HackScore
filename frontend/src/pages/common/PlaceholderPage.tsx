type PlaceholderPageProps = {
  title: string;
  description: string;
};

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold">{title}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-hs-t2">{description}</p>
      </div>
      <div className="rounded-xl border border-hs-border bg-hs-card p-6 shadow-hs-panel">
        <div className="h-2 w-32 rounded-full bg-hs-accent-15" />
        <div className="mt-5 grid gap-3 md:grid-cols-3">
          <div className="h-28 rounded-lg border border-hs-border bg-hs-bg" />
          <div className="h-28 rounded-lg border border-hs-border bg-hs-bg" />
          <div className="h-28 rounded-lg border border-hs-border bg-hs-bg" />
        </div>
      </div>
    </div>
  );
}
