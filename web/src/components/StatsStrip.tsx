"use client";

type Props = { score: number; status: "idle" | "loading" | "error" | "success" };

export default function StatsStrip({ score, status }: Props) {
  return (
    <section className="grid grid-cols-2 gap-3 md:grid-cols-4">
      <div className="rounded-md border border-border bg-card p-3">Validation Signal: <strong>{score}/100</strong></div>
      <div className="rounded-md border border-border bg-card p-3">Transformation Trail: <strong>Visible</strong></div>
      <div className="rounded-md border border-border bg-card p-3">Source Trace: <strong>Section-linked</strong></div>
      <div className="rounded-md border border-border bg-card p-3">Run Status: <strong className="capitalize">{status}</strong></div>
    </section>
  );
}
