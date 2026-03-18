"use client";

import Hero from "@/components/Hero";
import WorkspacePanel from "@/components/WorkspacePanel";
import InsightPanel from "@/components/InsightPanel";
import CollectionPanel from "@/components/CollectionPanel";
import { useState } from "react";
import { generatePlan, getInsights, saveDossier, type PlanResponse } from "@/lib/api";

export default function Page() {
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState("problem");
  const [insights, setInsights] = useState<string[]>([]);

  const onGenerate = async (query: string, preferences: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await generatePlan({ query, preferences });
      setPlan(result);
      const trace = await getInsights({ selection: "problem", context: query });
      setInsights(trace.highlights || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate brief");
    } finally {
      setLoading(false);
    }
  };

  const onSelectSection = async (section: string, context: string) => {
    setSelected(section);
    const res = await getInsights({ selection: section, context });
    setInsights(res.highlights || []);
  };

  const onSave = async () => {
    if (!plan) return;
    await saveDossier({ title: "Planning Dossier", summary: plan.summary, score: plan.score });
  };

  return (
    <main className="min-h-screen px-4 py-6 md:px-8">
      <Hero />
      <section className="mt-6 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <WorkspacePanel onGenerate={onGenerate} loading={loading} error={error} />
        <InsightPanel
          plan={plan}
          selected={selected}
          onSelectSection={onSelectSection}
          insights={insights}
          onSave={onSave}
          loading={loading}
        />
      </section>
      <CollectionPanel />
    </main>
  );
}
