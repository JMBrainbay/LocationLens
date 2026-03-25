import Link from "next/link";

export default function HomePage() {
  return (
    <section className="stack">
      <h2>Dutch location intelligence workshop starter</h2>
      <p>
        This scaffold gives teams a stable normalized API and minimal UI to quickly build different
        workshop lenses without starting from scratch.
      </p>
      <p>
        You can turn this into a comparator, buyer brief helper, family-fit lens, sustainability
        lens, ranking experiment, or neighborhood explainer.
      </p>
      <div className="row">
        <Link href="/playground">Open Playground</Link>
        <Link href="/compare">Open Compare</Link>
      </div>
      <section className="panel">
        <h3>Ideas to extend</h3>
        <p>Add persona scoring, richer narratives, custom metric weighting, or alternative UI cards.</p>
      </section>
    </section>
  );
}
