"use client";

type Props = { section: string; content: string; source: string };

export default function FeaturePanel({ section, content, source }: Props) {
  const snippet = source.slice(0, 220);
  return (
    <section className="mt-4 rounded-md border border-border bg-background p-3">
      <h3 className="font-semibold">Source Trace Inspector — {section}</h3>
      <p className="mt-1 text-sm">{content}</p>
      <div className="mt-2 rounded border border-accent/40 bg-accent/10 p-2 text-xs">
        Highlighted source phrase: “{snippet}...”
      </div>
      <div className="mt-2 text-xs text-foreground/80">Assumption label: Inferred from constraints and phrasing confidence.</div>
    </section>
  );
}
