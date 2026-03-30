"use client";

import { useEffect, useState } from "react";
import type { CompareResponse } from "@nl-location-lens/contracts/src/compare";
import type { SuggestResult } from "@nl-location-lens/contracts/src/place";
import { SearchBox } from "../../components/search-box";
import { CompareCard } from "../../components/compare-card";
import { JsonPanel } from "../../components/json-panel";
import { comparePlaces } from "../../lib/api";

export default function ComparePage() {
  const [left, setLeft] = useState<SuggestResult | null>(null);
  const [right, setRight] = useState<SuggestResult | null>(null);
  const [compare, setCompare] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      if (!left || !right) {
        setCompare(null);
        return;
      }
      setCompare(null);
      setLoading(true);
      setError(null);
      try {
        setCompare(await comparePlaces(left.id, right.id));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
        setCompare(null);
      } finally {
        setLoading(false);
      }
    };
    void run();
  }, [left, right]);

  return (
    <section className="stack">
      <h2>Compare</h2>
      <div className="grid2">
        <SearchBox label="Left place" onSelect={setLeft} />
        <SearchBox label="Right place" onSelect={setRight} />
      </div>
      {loading && <p className="muted">Comparing...</p>}
      {error && <p className="error">{error}</p>}
      <div className="grid2">
        <CompareCard title="Left" profile={compare?.left ?? null} pendingLabel={left?.label ?? null} />
        <CompareCard title="Right" profile={compare?.right ?? null} pendingLabel={right?.label ?? null} />
      </div>
      {compare && (
        <>
          <section className="panel">
            <h3>Deltas</h3>
            {compare.deltas.length === 0 && <p className="muted">No overlapping metrics found.</p>}
            <ul className="list compact">
              {compare.deltas.map((delta) => (
                <li key={delta.key}>
                  {delta.label}: {delta.left} vs {delta.right} (diff {delta.difference})
                </li>
              ))}
            </ul>
          </section>
          <JsonPanel data={compare} />
        </>
      )}
      <p className="muted">Ideas to extend: persona weighting, ranked winners, explainable trade-offs.</p>
    </section>
  );
}
