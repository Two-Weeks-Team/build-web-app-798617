"use client";

import { useEffect, useState } from "react";
import { fetchDossiers } from "@/lib/api";

export default function CollectionPanel() {
  const [data, setData] = useState<Array<{ id: number; title: string; summary: string; score: number }>>([]);
  const [state, setState] = useState<"loading" | "error" | "empty" | "success">("loading");

  useEffect(() => {
    fetchDossiers()
      .then((items) => {
        setData(items);
        setState(items.length ? "success" : "empty");
      })
      .catch(() => setState("error"));
  }, []);

  return (
    <section className="mt-6 rounded-lg border border-border bg-card p-4 shadow-card">
      <h3 className="text-xl">Planning Dossier Shelf</h3>
      {state === "loading" && <p className="mt-2 text-sm">Loading saved artifacts...</p>}
      {state === "error" && <p className="mt-2 text-sm text-red-700">Could not load saved dossiers.</p>}
      {state === "empty" && <p className="mt-2 text-sm">No saved dossiers yet. Generate and save your first planning artifact.</p>}
      {state === "success" && (
        <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-3">
          {data.map((d) => (
            <article key={d.id} className="rounded-md border border-border bg-white p-3">
              <p className="text-xs uppercase tracking-wide text-foreground/60">Saved Planning Dossier</p>
              <h4 className="mt-1 text-base">{d.title}</h4>
              <p className="mt-1 text-sm text-foreground/80">{d.summary}</p>
              <p className="mt-2 text-xs">Viability score: {d.score}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
