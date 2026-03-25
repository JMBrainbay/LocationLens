import type { LocationProfile } from "@nl-location-lens/contracts/src/profile";

type Props = {
  title: string;
  profile: LocationProfile;
};

export function CompareCard({ title, profile }: Props) {
  return (
    <section className="panel">
      <h3>{title}</h3>
      <p>{profile.place.label}</p>
      <p className="muted">{profile.place.id}</p>
      <ul className="list compact">
        {Object.entries(profile.areaMetrics).map(([key, value]) => (
          <li key={key}>
            {key}: {value ?? "-"}
          </li>
        ))}
      </ul>
    </section>
  );
}
