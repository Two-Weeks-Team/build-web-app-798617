"use client";

import { PlanResponse } from "@/lib/api";

export default function InsightPanel({ plan, selected, onSelectSection, insights, onSave, loading }: { plan: PlanResponse | null; selected: string; onSelectSection: (s: string, c: string) => void; insights: string[]; onSave: () => void; loading: boolean; }) {
  if (loading) return <section className="rounded-lg border border-border bg-card p-4">Assembling structured brief...</section>;
  if (!plan) return <section className="rounded-lg border border-border bg-card p-4">No brief yet. Use a seed and generate your first dossier.</section>;

  const sections = Object.entries(plan.items);

  return (
    <section className="rounded-lg border border-border bg-card p-4 shadow-card">
      <div className="flex items-center justify-between">
        <h2 className="text-xl">Structured Product Brief</h2>
        <span className="rounded-full bg-success/20 px-3 py-1 text-xs">Viability {plan.score.value}/100 — {plan.score.rationale}</span>
      </div>
      <p className="mt-2 text-sm">{plan.summary}</p>
      <div className="mt-4 grid gap-2">
        {sections.map(([key, value]) => (
          <button key={key} onClick={() => onSelectSection(key, value)} className={`rounded-md border p-3 text-left ${selected === key ? "border-accent bg-accent/10" : "border-border bg-white"}`}>
            <p className="text-xs uppercase tracking-wide text-foreground/60">{key.replaceAll("_", " ")}</p>
            <p className="mt-1 text-sm">{value}</p>
          </button>
        ))}
      </div>
      <div className="mt-4 rounded-md border border-border bg-muted p-3">
        <p className="text-xs uppercase tracking-wide">Source Trace Inspector</p>
        <ul className="mt-2 list-disc space-y-1 pl-4 text-sm">
          {insights.length ? insights.map((h) => <li key={h}>{h}</li>) : <li>No highlights yet.</li>}
        </ul>
      </div>
      <div className="mt-4 flex gap-2">
        <button className="rounded-md border border-border px-3 py-2 text-sm">Regenerate section</button>
        <button className="rounded-md border border-border px-3 py-2 text-sm">Accept edits</button>
        <button onClick={onSave} className="rounded-md bg-primary px-3 py-2 text-sm text-white">Save to Dossier Shelf</button>
      </div>
    </section>
  );
}
