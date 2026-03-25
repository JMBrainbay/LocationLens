import type { LocationProfile } from "@nl-location-lens/contracts/src/profile";

type Props = {
  profile: LocationProfile;
};

export function PlaceCard({ profile }: Props) {
  const { place, building, sourceBreakdown } = profile;
  return (
    <section className="panel">
      <h3>{place.label}</h3>
      <p className="muted">
        {place.type} | {place.source}
      </p>
      <p>
        {(place.address?.street ?? "Unknown street")} {(place.address?.houseNumber ?? "").trim()}
      </p>
      <p>
        {(place.address?.postalCode ?? "-")} {(place.address?.city ?? "-")}
      </p>
      <p className="muted">
        lat/lon: {place.lat ?? "-"}, {place.lon ?? "-"}
      </p>
      <hr />
      <p>Year built: {building.yearBuilt ?? "-"}</p>
      <p>Usage: {building.usageType ?? "-"}</p>
      <p>Floor area m2: {building.floorAreaM2 ?? "-"}</p>
      <p className="muted">
        Sources: place={sourceBreakdown.place}, building={sourceBreakdown.building}, metrics=
        {sourceBreakdown.metrics}
      </p>
    </section>
  );
}
