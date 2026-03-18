"use client";

type Props = { status: "idle" | "loading" | "error" | "success"; error?: string; successText?: string };

export default function StatePanel({ status, error, successText }: Props) {
  if (status === "loading") return <div className="rounded-md border border-border bg-muted p-2 text-sm">Parsing rough input → normalizing concepts → assembling brief...</div>;
  if (status === "error") return <div className="rounded-md border border-warning bg-warning/10 p-2 text-sm">Could not generate brief. {error}</div>;
  if (status === "success") return <div className="rounded-md border border-success bg-success/10 p-2 text-sm">{successText}</div>;
  return <div className="rounded-md border border-border bg-background p-2 text-sm">Ready for idea intake. Pick a seed or paste your own notes.</div>;
}
