"use client";

import { useState } from "react";
import type { CompareResponse } from "@nl-location-lens/contracts/src/compare";
import type { SuggestResult } from "@nl-location-lens/contracts/src/place";
import { SearchBox } from "../../components/search-box";
import { CompareCard } from "../../components/compare-card";
import { JsonPanel } from "../../components/json-panel";
import { comparePlaces } from "../../lib/api";

export default function ComparePage() {
  const [left, setLeft] = useState<SuggestResult | null>(null);
  const [right, setRight] = useState<SuggestResult | null>(null);
  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runCompare = async (nextLeft: SuggestResult | null, nextRight: SuggestResult | null) => {
    if (!nextLeft || !nextRight) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      setData(await comparePlaces(nextLeft.id, nextRight.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  const onLeft = async (item: SuggestResult) => {
    setLeft(item);
    await runCompare(item, right);
  };

  const onRight = async (item: SuggestResult) => {
    setRight(item);
    await runCompare(left, item);
  };

  return (
    <section className="stack">
      <h2>Compare</h2>
      <div className="grid2">
        <SearchBox label="Left place" onSelect={onLeft} />
        <SearchBox label="Right place" onSelect={onRight} />
      </div>
      {loading && <p className="muted">Comparing...</p>}
      {error && <p className="error">{error}</p>}
      {data && (
        <>
          <div className="grid2">
            <CompareCard title="Left" profile={data.left} />
            <CompareCard title="Right" profile={data.right} />
          </div>
          <section className="panel">
            <h3>Deltas</h3>
            {data.deltas.length === 0 && <p className="muted">No overlapping metrics found.</p>}
            <ul className="list compact">
              {data.deltas.map((delta) => (
                <li key={delta.key}>
                  {delta.label}: {delta.left} vs {delta.right} (diff {delta.difference})
                </li>
              ))}
            </ul>
          </section>
          <JsonPanel data={data} />
        </>
      )}
      <p className="muted">Ideas to extend: persona weighting, ranked winners, explainable trade-offs.</p>
    </section>
  );
}
