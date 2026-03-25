"use client";

import { useEffect, useState } from "react";
import type { SuggestResult } from "@nl-location-lens/contracts/src/place";
import { suggestPlaces } from "../lib/api";

type SearchBoxProps = {
  label: string;
  onSelect: (item: SuggestResult) => void;
};

export function SearchBox({ label, onSelect }: SearchBoxProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SuggestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([]);
      setError(null);
      return;
    }

    const timeout = setTimeout(async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await suggestPlaces(query);
        setResults(response.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => clearTimeout(timeout);
  }, [query]);

  return (
    <section className="panel">
      <label className="label">{label}</label>
      <input
        className="input"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Search Dutch address or place..."
      />
      {loading && <p className="muted">Loading suggestions...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && query.trim().length >= 2 && results.length === 0 && !error && (
        <p className="muted">No suggestions found.</p>
      )}
      <ul className="list">
        {results.map((item) => (
          <li key={item.id}>
            <button className="listButton" type="button" onClick={() => onSelect(item)}>
              {item.label} <span className="muted">({item.source})</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
