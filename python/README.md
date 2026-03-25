# nl-location-lens

Workshop starter monorepo for Dutch location intelligence.

This scaffold is intentionally small and hackable. It helps teams build different workshop directions
fast (comparator, buyer brief, family-fit lens, sustainability lens, ranking helper, neighborhood explainer)
without locking into one product.

## Architecture

- `apps/web`: Next.js + TypeScript App Router playground UI
- `apps/api`: FastAPI + Pydantic + httpx + pytest normalized API
- `packages/contracts`: shared Zod contracts + TypeScript client types for web

Default mode is fixture mode and runs without external API dependencies.

## Local setup

1. Copy env:

```bash
cp .env.example .env
```

Quick workshop reset (recommended):

```bash
corepack pnpm workshop:prep:fixture
# or
corepack pnpm workshop:prep:live
```

This rewrites `.env` from `.env.example`, sets providers for the selected mode, and stops stale dev servers.

2. Install JS deps:

```bash
pnpm install
```

3. Install API Python deps:

```bash
cd apps/api && python -m pip install -e .
```

4. Run web + API:

```bash
cd ../..
pnpm dev
```

One-command clean start:

```bash
corepack pnpm workshop:reset:fixture
# or
corepack pnpm workshop:reset:live
```

## Docker quick start

Run both API and web in containers:

```bash
docker compose up --build
```

Or via scripts:

```bash
corepack pnpm docker:up
```

Stop containers cleanly (and remove orphans):

```bash
docker compose down --remove-orphans
```

Or via script:

```bash
corepack pnpm docker:down
```

5. Run tests:

```bash
pnpm test
```

6. Run type checks:

```bash
pnpm typecheck
```

## Environment variables

- `API_PORT`
- `NEXT_PUBLIC_API_BASE_URL`
- `LOCATION_PROVIDER` (`fixture`, `pdok`, `live`) - `live` aliases to `pdok`
- `BUILDING_PROVIDER` (`fixture`, `bag`, `none`, `live`) - `live` aliases to `bag`
- `METRICS_PROVIDER` (`fixture`, `cbs`, `none`, `live`) - `live` aliases to `cbs`
- `PDOK_LOCATIESERVER_BASE_URL`
- `PDOK_BAG_OGC_BASE_URL`
- `CBS_ODATA_BASE_URL`
- `CBS_TABLE_ID`
- `CBS_QUERY_STRATEGY` (`batch` or `targeted`, default `batch`)
- `ENABLE_EP_ONLINE`
- `EP_ONLINE_BASE_URL`
- `EP_ONLINE_API_KEY`

## Fixture mode vs live mode

- **Fixture mode (default):** deterministic offline data for suggest/resolve/profile/compare.
- **Live mode:** env-switchable adapters (PDOK, BAG, CBS) behind same public contracts.
- **Graceful degradation:** when live lookup fails, adapters return stable empty values (`[]`, `none`, `null`) instead of crashing.

## Datasources currently used

Active providers are wired in `apps/api/src/integrations/index.py`:

- **Place provider:** `FixturePlaceProvider` or `PdokLocatieserverProvider`
- **Building provider:** `FixtureBuildingProvider`, `PdokBagProvider`, `EpOnlineProvider` (optional/stub), or `NoneBuildingProvider`
- **Metrics provider:** `FixtureMetricsProvider`, `CbsMetricsProvider`, or `NoneMetricsProvider`

Fallback behavior is provider-local:

- PDOK suggest failure -> empty results list
- PDOK resolve failure -> route returns `404 not_found`
- BAG/CBS failure -> empty normalized section and `sourceBreakdown` value `none`

Quickly inspect active providers at runtime:

```bash
curl "http://localhost:4000/api/debug/providers"
```

## PDOK chaining into other datasources

The normalized place from PDOK lookup is used as the bridge object for other sources:

- **PDOK -> BAG**
  - `postcode` -> `place.address.postalCode`
  - `huisnummer` -> `place.address.houseNumber`
  - optional: `huisletter` -> `place.address.houseLetter`
  - optional: `huisnummertoevoeging` -> `place.address.houseNumberSuffix`
- **PDOK -> CBS**
  - `buurtcode` -> `place.areaCodes.buurtCode`
  - used as OData filter: `RegioS eq '<buurtcode>'`

Notes:

- PDOK coordinate mapping is conservative (`centroide_ll` when available).
- Public API contracts stay stable between fixture and live mode.

CBS query modes:

- `CBS_QUERY_STRATEGY=batch` (default): fetch all `Observations` rows for one buurt in one call, then map relevant measures in memory.
- `CBS_QUERY_STRATEGY=targeted`: fetch one `Observations` query per mapped measure and aggregate.
- Recommended for workshops: **`batch`** (fewer moving parts, fewer HTTP calls).

## PDOK -> BAG/CBS trace example

This example shows the full live-mode chain for one address search.

1. Suggest an address in PDOK:

```bash
curl "http://localhost:4000/api/places/suggest?q=damrak%201%20amsterdam"
```

Take the first `results[0].id` from the response.

2. Resolve that id via PDOK lookup:

```bash
curl "http://localhost:4000/api/places/resolve?id=<PDOK_ID>"
```

In the normalized output, the API keeps the bridge fields used downstream:

- `place.address.postalCode`
- `place.address.houseNumber`
- `place.address.houseLetter` (optional)
- `place.address.houseNumberSuffix` (optional)
- `place.areaCodes.buurtCode`

3. Build a profile (PDOK + BAG + CBS):

```bash
curl "http://localhost:4000/api/places/profile?id=<PDOK_ID>"
```

How downstream lookups are driven:

- **BAG enrichment** uses address keys:
  - `postalCode`, `houseNumber`, and optional `houseLetter` / `houseNumberSuffix`
- **CBS metrics** uses neighborhood key:
  - `buurtCode` -> OData filter `RegioS eq '<buurtCode>'`

Inspect `sourceBreakdown` in the profile response to see which datasource produced each section (`fixture|pdok`, `fixture|bag|none`, `fixture|cbs|none`).

## API endpoints and curl examples

```bash
curl "http://localhost:4000/api/health"
curl "http://localhost:4000/api/places/suggest?q=damrak"
curl "http://localhost:4000/api/places/resolve?id=adr-damrak-1-amsterdam"
curl "http://localhost:4000/api/places/profile?id=adr-damrak-1-amsterdam"
curl "http://localhost:4000/api/compare?left=adr-damrak-1-amsterdam&right=adr-oudegracht-120-utrecht"
```

## Workshop extension ideas

- Add curated metrics in `apps/api/src/integrations/cbs.py`.
- Add persona scoring near `apps/api/src/routes/compare.py`.
- Add narratives/insights generation from profile and deltas.
- Add UI experiments in `apps/web/app/playground/page.tsx` and `apps/web/app/compare/page.tsx`.
