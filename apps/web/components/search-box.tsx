"use client";

import { useEffect, useId, useState, type KeyboardEvent } from "react";
import type { SuggestResult } from "@nl-location-lens/contracts/src/place";
import { suggestPlaces } from "../lib/api";

type SearchBoxProps = {
  label: string;
  onSelect: (item: SuggestResult) => void;
};

export function SearchBox({ label, onSelect }: SearchBoxProps) {
  const baseId = useId();
  const listId = `${baseId}-list`;
  const optionId = (index: number) => `${baseId}-opt-${index}`;

  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SuggestResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeIndex, setActiveIndex] = useState(-1);

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

  useEffect(() => {
    setActiveIndex(-1);
  }, [results]);

  const pick = (item: SuggestResult) => {
    onSelect(item);
    setActiveIndex(-1);
  };

  const onInputKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (results.length === 0) {
      return;
    }
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActiveIndex((i) => (i < results.length - 1 ? i + 1 : i));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActiveIndex((i) => (i <= 0 ? -1 : i - 1));
    } else if (event.key === "Enter" && activeIndex >= 0) {
      event.preventDefault();
      pick(results[activeIndex]);
    } else if (event.key === "Escape") {
      setActiveIndex(-1);
    }
  };

  return (
    <section className="panel">
      <label className="label">{label}</label>
      <input
        className="input"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        onKeyDown={onInputKeyDown}
        placeholder="Search Dutch address or place..."
        autoComplete="off"
        role="combobox"
        aria-expanded={results.length > 0}
        aria-controls={listId}
        aria-activedescendant={activeIndex >= 0 ? optionId(activeIndex) : undefined}
      />
      {loading && <p className="muted">Loading suggestions...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && query.trim().length >= 2 && results.length === 0 && !error && (
        <p className="muted">No suggestions found.</p>
      )}
      <ul id={listId} className="list" role="listbox">
        {results.map((item, index) => (
          <li key={item.id} role="option" aria-selected={index === activeIndex}>
            <button
              id={optionId(index)}
              className={index === activeIndex ? "listButton listButtonActive" : "listButton"}
              type="button"
              onClick={() => pick(item)}
            >
              {item.label} <span className="muted">({item.source})</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
