import "./globals.css";
import Link from "next/link";
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="header">
          <h1>nl-location-lens</h1>
          <nav>
            <Link href="/">Home</Link> | <Link href="/playground">Playground</Link> |{" "}
            <Link href="/compare">Compare</Link>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}
