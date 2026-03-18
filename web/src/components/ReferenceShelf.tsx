"use client";

type Props = { onInspect: () => void | Promise<void> };

const dossiers = [
  { title: "Study Sprint Brief v2", note: "Saved 10m ago", score: 84 },
  { title: "Home Repair Rapid Match", note: "Saved yesterday", score: 78 },
  { title: "Freelance Scope Drift Watch", note: "Saved 2 days ago", score: 81 }
];

export default function ReferenceShelf({ onInspect }: Props) {
  return (
    <section className="rounded-lg border border-border bg-card p-4 shadow-soft">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-xl">Planning Dossier Shelf</h3>
        <button onClick={onInspect} className="rounded-md border border-accent px-3 py-1 text-xs text-accent">Refresh trace insights</button>
      </div>
      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
        {dossiers.map((d) => (
          <article key={d.title} className="rotate-[-0.4deg] rounded-md border border-border bg-background p-3 transition hover:-translate-y-0.5">
            <div className="text-xs uppercase tracking-wide text-foreground/60">Saved Planning Dossier</div>
            <div className="mt-1 font-semibold">{d.title}</div>
            <div className="mt-2 text-xs text-foreground/75">{d.note}</div>
            <div className="mt-2 text-xs">Viability: <strong>{d.score}</strong> — solid user pain and feasible MVP contour.</div>
          </article>
        ))}
      </div>
    </section>
  );
}
