# nl-location-lens

Workshop starter monorepo for Dutch location intelligence: small, hackable, and easy to extend (comparator, buyer brief, neighborhood explainer, and similar ideas) without locking into one product.

**Default is fixture mode:** deterministic data, no external APIs required.

---

## Quick start (from repo root)

```bash
cp .env.example .env
npm install
python3 -m pip install -e apps/api
npm run dev
```

- **Web:** [http://localhost:3000](http://localhost:3000)  
- **API:** [http://localhost:4000](http://localhost:4000)

Then run checks:

```bash
npm run test
npm run typecheck
```

Optional: rewrite `.env` for fixture vs live providers and refresh deps without starting servers:

```bash
npm run workshop:prep:fixture   # or workshop:prep:live
```

One-shot reset (writes `.env`, installs deps, starts dev):

```bash
npm run workshop:reset:fixture    # or workshop:reset:live
```

---

## Five-minute walkthrough

1. **`apps/api/src/fixtures/places.py`** — Three fake addresses (Amsterdam, Utrecht, Rotterdam). Search text matches these labels in fixture mode.
2. **`apps/api/src/integrations/index.py`** — Chooses fixture vs live providers from env.
3. **`apps/api/src/routes/`** — Thin HTTP handlers; errors use `lib/errors.py` for a consistent JSON shape.
4. **`packages/contracts`** — Shared Zod types; **`apps/web`** consumes them for the UI.
5. **Try the API** — With the stack running, use the curl block under [Fixture IDs and curl](#fixture-ids-and-curl) below.

---

## Architecture

| Path | Role |
|------|------|
| `apps/web` | Next.js + TypeScript App Router playground |
| `apps/api` | FastAPI + Pydantic + httpx + pytest |
| `packages/contracts` | Zod contracts + TS types for the web app |

---

## Fixture IDs and curl

With `LOCATION_PROVIDER=fixture` (default), these place IDs are always valid:

| ID | City |
|----|------|
| `adr-damrak-1-amsterdam` | Amsterdam |
| `adr-oudegracht-120-utrecht` | Utrecht |
| `adr-blaak-88-rotterdam` | Rotterdam |

```bash
curl "http://localhost:4000/api/health"
curl "http://localhost:4000/api/places/suggest?q=damrak"
curl "http://localhost:4000/api/places/resolve?id=adr-damrak-1-amsterdam"
curl "http://localhost:4000/api/places/profile?id=adr-damrak-1-amsterdam"
curl "http://localhost:4000/api/compare?left=adr-damrak-1-amsterdam&right=adr-oudegracht-120-utrecht"
curl "http://localhost:4000/api/debug/providers"
```

---

## Docker

```bash
docker compose up --build
# or: npm run docker:up
```

Stop:

```bash
docker compose down --remove-orphans
# or: npm run docker:down
```

---

## Environment variables

- `API_PORT`
- `NEXT_PUBLIC_API_BASE_URL`
- `LOCATION_PROVIDER` (`fixture`, `pdok`, `live`) — `live` maps to PDOK
- `BUILDING_PROVIDER` (`fixture`, `bag`, `none`, `live`) — `live` maps to BAG
- `METRICS_PROVIDER` (`fixture`, `cbs`, `none`, `live`) — `live` maps to CBS
- `PDOK_LOCATIESERVER_BASE_URL`, `PDOK_BAG_OGC_BASE_URL`
- `CBS_ODATA_BASE_URL`, `CBS_TABLE_ID`, `CBS_QUERY_STRATEGY` (`batch` or `targeted`, default `batch`)
- `ENABLE_EP_ONLINE`, `EP_ONLINE_BASE_URL`, `EP_ONLINE_API_KEY`

## Fixture vs live mode

- **Fixture:** offline suggest/resolve/profile/compare.
- **Live:** PDOK, BAG, CBS behind the same JSON contracts.
- **Degradation:** failed live lookups yield empty sections or `404` on resolve instead of crashing.

## Datasources

Wired in `apps/api/src/integrations/index.py`:

- **Place:** `FixturePlaceProvider` or `PdokLocatieserverProvider`
- **Building:** `FixtureBuildingProvider`, `PdokBagProvider`, optional `EpOnlineProvider`, or `NoneBuildingProvider`
- **Metrics:** `FixtureMetricsProvider`, `CbsMetricsProvider`, or `NoneMetricsProvider`

Fallback behavior:

- PDOK suggest failure → empty list
- PDOK resolve failure → `404` with `not_found`
- BAG/CBS failure → empty normalized section + `sourceBreakdown` `none`

## PDOK → BAG / CBS (live mode)

- **BAG:** `postalCode` → `place.address.postalCode`; `huisnummer` → `houseNumber`; optional letter/suffix fields.
- **CBS:** `buurtcode` → `place.areaCodes.buurtCode`; OData filter `RegioS eq '<buurtcode>'`.

CBS: prefer `CBS_QUERY_STRATEGY=batch` in workshops (one buurt fetch, map in memory).

### Live-mode trace example

1. Suggest:

```bash
curl "http://localhost:4000/api/places/suggest?q=damrak%201%20amsterdam"
```

2. Resolve with `results[0].id`:

```bash
curl "http://localhost:4000/api/places/resolve?id=<PDOK_ID>"
```

3. Profile:

```bash
curl "http://localhost:4000/api/places/profile?id=<PDOK_ID>"
```

Check `sourceBreakdown` in the profile for `pdok` / `bag` / `cbs` / `none`.

## Workshop extension ideas

- Curated metrics in `apps/api/src/integrations/cbs.py`
- Scoring or narrative in `apps/api/src/routes/compare.py`
- UI experiments in `apps/web/app/` pages
