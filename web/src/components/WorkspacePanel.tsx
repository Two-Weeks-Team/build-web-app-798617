"use client";

import { useState } from "react";

const seeds = [
  "AI meal planner for busy parents with grocery sync",
  "Local service marketplace for last-minute home repairs",
  "Creator research notebook that turns scattered links into content plans",
  "Micro-SaaS for tracking freelance project scope drift",
  "Student study companion that converts lecture notes into revision packs"
];

export default function WorkspacePanel({ onGenerate, loading, error }: { onGenerate: (q: string, p: string) => void; loading: boolean; error: string | null; }) {
  const [query, setQuery] = useState(seeds[0]);
  const [preferences, setPreferences] = useState("Audience: Busy parents; Budget: Lean MVP; Timeline: 8 weeks; Focus: retention");

  return (
    <section className="rounded-lg border border-border bg-card p-4 shadow-card">
      <h2 className="text-xl">Idea Intake Canvas</h2>
      <label className="mt-3 block text-sm">Paste your rough product idea</label>
      <textarea className="mt-1 h-36 w-full rounded-md border border-border bg-white p-3" value={query} onChange={(e) => setQuery(e.target.value)} />
      <label className="mt-3 block text-sm">Planning constraints or preferences</label>
      <textarea className="mt-1 h-24 w-full rounded-md border border-border bg-white p-3" value={preferences} onChange={(e) => setPreferences(e.target.value)} />
      <div className="mt-3 flex flex-wrap gap-2">
        {seeds.map((seed) => (
          <button key={seed} onClick={() => setQuery(seed)} className="rounded-full border border-border bg-muted px-3 py-1 text-xs">{seed}</button>
        ))}
      </div>
      <button onClick={() => onGenerate(query, preferences)} disabled={loading} className="mt-4 rounded-md bg-primary px-4 py-2 text-white">
        {loading ? "Pressing notes into brief..." : "Generate Brief"}
      </button>
      {error ? <p className="mt-2 text-sm text-red-700">{error}</p> : null}
    </section>
  );
}
