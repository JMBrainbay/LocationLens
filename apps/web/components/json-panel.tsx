"use client";

import { useState } from "react";

type Props = {
  data: unknown;
  title?: string;
};

export function JsonPanel({ data, title = "Debug JSON" }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <section className="panel">
      <button type="button" className="listButton" onClick={() => setOpen((v) => !v)}>
        {open ? "Hide" : "Show"} {title}
      </button>
      {open && <pre className="pre">{JSON.stringify(data, null, 2)}</pre>}
    </section>
  );
}
