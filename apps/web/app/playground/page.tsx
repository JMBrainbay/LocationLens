"use client";

import { useState } from "react";
import type { LocationProfile } from "@nl-location-lens/contracts/src/profile";
import type { SuggestResult } from "@nl-location-lens/contracts/src/place";
import { SearchBox } from "../../components/search-box";
import { PlaceCard } from "../../components/place-card";
import { JsonPanel } from "../../components/json-panel";
import { resolveProfile } from "../../lib/api";

export default function PlaygroundPage() {
  const [selected, setSelected] = useState<SuggestResult | null>(null);
  const [profile, setProfile] = useState<LocationProfile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSelect = async (item: SuggestResult) => {
    setSelected(item);
    setLoading(true);
    setError(null);
    try {
      const nextProfile = await resolveProfile(item.id);
      setProfile(nextProfile);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="stack">
      <h2>Playground</h2>
      <SearchBox label="Search place" onSelect={onSelect} />
      {loading && <p className="muted">Loading profile...</p>}
      {error && <p className="error">{error}</p>}
      {!loading && selected && !profile && !error && <p className="muted">No profile data found.</p>}
      {profile && (
        <>
          <PlaceCard profile={profile} />
          <section className="panel">
            <h3>Area metrics</h3>
            <ul className="list compact">
              {Object.entries(profile.areaMetrics).map(([key, value]) => (
                <li key={key}>
                  {key}: {value ?? "-"}
                </li>
              ))}
            </ul>
          </section>
          <JsonPanel data={profile} />
        </>
      )}
      <p className="muted">Ideas to extend: map previews, narratives, persona scoring, metric weighting.</p>
    </section>
  );
}
