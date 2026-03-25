import type { LocationProfile } from "@nl-location-lens/contracts/src/profile";

type Props = {
  title: string;
  profile: LocationProfile | null;
  /** Shown when profile is not loaded yet but user picked a suggestion */
  pendingLabel?: string | null;
};

export function CompareCard({ title, profile, pendingLabel }: Props) {
  return (
    <section className="panel">
      <h3>{title}</h3>
      {!profile && !pendingLabel && <p className="muted">Select a location.</p>}
      {!profile && pendingLabel && (
        <p>
          Selected: <span className="muted">{pendingLabel}</span>
        </p>
      )}
      {profile && (
        <>
          <p>{profile.place.label}</p>
          <p className="muted">{profile.place.id}</p>
          <ul className="list compact">
            {Object.entries(profile.areaMetrics).map(([key, value]) => (
              <li key={key}>
                {key}: {value ?? "-"}
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
