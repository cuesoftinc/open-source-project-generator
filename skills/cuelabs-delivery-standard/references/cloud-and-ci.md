# Cloud and CI standard

## Contents

- CueLABS cloud and environment policy
- GitHub Actions workflow families
- Test layout and fleet parity
- Email, data plane, and protocol decisions

## Canon

- Backends deploy to GCP Cloud Run (provisioned via the `cuesoft-iac` Pulumi
  ecosystem — never ad-hoc); frontends deploy to Firebase App Hosting; the
  Helm chart remains the self-host path.
- AI features use **Vertex AI** (Gemini via `aiplatform.googleapis.com`, ADC —
  see `cuesoft-iac/functions/cueprise-gemini-proxy`); no consumer AI-vendor
  API keys in cloud deployments. Self-host fallback: BYO Gemini/Groq env keys.
- Environments & deploy gating: `stg` = sandbox is the ONLY environment for
  CueLABS™ products (no production); Doppler config `stg` holds its secrets.
  **Open-source deviation from the cueprise flow**, scoped by surface:
  the WEBSITES ride Firebase App Hosting automatic rollouts from `main`
  (declared in cuesoft-iac `Pulumi.cuesoft.yaml` appHosting backends,
  `rootDirectory: /web`, Cloudflare-proxied; a web-visible merge is live
  in ~30 min — verified 2026-07-23). API-SERVICE deploys are the
  tag-gated path: they fire **only on `v*` tag creation**, gated by a
  tag ruleset (owner-level) + protected GitHub environment, via the
  pending `release.yml` (lands with the deploy phase). GitHub Actions
  itself never deploys the sites.
- **GitHub Actions standard (uniform across repos, ratified 2026-07-18)**:
  standardized workflow families with identical shared jobs and conventions —
  `.github/workflows/build-and-test.yml` (workflow name `build-and-test`;
  triggers `push: branches [main]` + `pull_request`, no path filters —
  build-ready surfaces join as jobs; `permissions: contents: read`; `concurrency:
  build-and-test-${{ github.ref }}` with cancel-in-progress; one job per
  surface: `web` = "web · lint + typecheck + unit + build" on Node 24
  (`npm ci → lint → typecheck → test → build`), `web-e2e` = "web ·
  Playwright (TEST_MODE)" (`playwright install --with-deps chromium →
  test:e2e`). API jobs land when a product backend reaches its build-ready
  phase; mobile jobs land when mobile implementation begins. Once present,
  stack-equivalent API/mobile jobs follow the same fleet naming, setup, cache,
  and command shape; action steps
  pin the LATEST major of official actions — currently
  `actions/checkout@v7`, `actions/setup-node@v7`,
  `actions/upload-artifact@v7` (verify via
  `gh api repos/actions/<name>/releases/latest` when touching workflows,
  never copy stale versions from older files). **Shared web jobs are
  BYTE-IDENTICAL across repos** — repo variance lives in `package.json`
  scripts, never in workflow YAML; a mobile product's file additionally
  carries its mobile jobs (and the two ratified mobile workflows,
  `mobile-goldens` dispatch + `mobile-e2e` nightly — see the Mobile
  section); named steps only (Checkout · Setup Node ·
  Install dependencies · Lint · Typecheck · Unit & integration tests ·
  Build (TEST_MODE with `NEXT_PUBLIC_TEST_MODE: "1"`)); the e2e job builds
  in TEST_MODE, installs chromium, runs `test:e2e` with TEST_MODE+CI env,
  and uploads `web/playwright-report` as artifact `playwright-report`
  (retention 7) on failure) and the
  tag-gated `release.yml` (X-6; getpp/cueprise are the deploy-pattern
  references — NOT YET LANDED in any product repo; lands with the deploy
  phase). Workflow files beyond these families and explicitly ratified
  surface workflows are a standards deviation and need ratification. CodeQL
  runs via GitHub DEFAULT SETUP
  (a repo setting, `gh api repos/<org>/<repo>/code-scanning/default-setup`),
  not a workflow file — parity audits check the API, not `.github/`.
- **Test layout standard (uniform across repos, 2026-07-18)**: unit/
  integration tests co-locate with their source as `<name>.test.ts(x)`
  (component `Button.test.tsx` beside `Button.tsx`; kebab for module tests);
  Playwright e2e specs live in `web/e2e/<flow>.spec.ts` (flow names mirror
  the design.md §8.4 prototype journeys) with `playwright.config.ts` at the
  web root; npm scripts are `test` (unit), `test:e2e` (Playwright), `lint`,
  `typecheck` in every web app.
- **Fleet parity canons (ratified 2026-07-23, cross-repo review)**:
  - **Node 24 single-truth**: `setup-node` in CI, `web/.nvmrc`, the web
    Dockerfile (`node:24-slim`), and the README prerequisite all say 24;
    `@types/node` tracks the runtime major (`^24`). No repo states a
    different floor anywhere.
  - **Go single-truth**: one fleet Go version (currently `go 1.26` in
    go.mod, `golang:1.26-alpine` images); service binaries build as
    `app`; HEALTHCHECK `start-period` 10s (model-loading services may
    extend — apparule measure 40s, upstat observability 30s — with the
    reason in the Dockerfile).
  - **Web dep alignment**: `next`/`react`/`react-dom`/`eslint-config-next`
    are EXACT-pinned and fleet-identical; remaining shared devDeps stay
    caret but version-aligned across repos; the dependabot npm `ignore`
    block (eslint/typescript/@types/node majors) ships in every repo.
  - **TEST_MODE web canon (extends the session-gate canon)**: provider
    file is `web/src/auth/test-mode-provider.ts`, storage const
    `SESSION_KEY`, key `<product>.test-session`, value = the JSON session
    snapshot (never a bare sentinel; restore validates the payload,
    treats missing/corrupt as signed_out, and re-resolves identity so
    mutable account state is never served stale). Mock server lives at
    `web/src/app/api/mock/v1/`, store at `web/src/mocks/store.ts`, seeds
    at `web/src/mocks/seed.ts`, reset at `POST /api/mock/v1/testing/reset`.
  - **Org lint bans fleet-wide**: `no-restricted-imports` blocks `@mui/*`,
    `@emotion/*`, `dayjs`, `moment` (plus the legacy-path ban) in every
    web app; `eslint-plugin-testing-library` is WIRED (flat/react preset
    scoped to `src/**/*.test.{ts,tsx}`) with `no-container` and
    `no-node-access` disabled via a documenting comment — bespoke
    token-layer components assert non-semantic structure by design.
  - **README fleet template**: badge row (License MIT + build-and-test
    status) after the intro paragraph; prose overview; plain-indent repo
    tree; `cp .env.example .env` + make-target quickstart; Node/Go
    versions per the single-truths above. Root `.env.example` uses
    `── section ──` comment headers; `web/.env.example` stays headerless.
  - **next.config**: `devIndicators: { position: "bottom-right" }` — keep
    the dev indicator, keep it out of content corners.
  - **Changelog PR refs**: every entry carries its `(#NNN)` ref; a lane
    writing entries pre-merge opens the PR first, then amends the entry
    with the real number before handoff (refs are part of the entry, not
    optional garnish). Entries are APPENDED INTO the section's existing
    bucket heading — emitting a second `### Added`/`### Fixed` heading is
    the defect that forced dedup rounds in every repo (apparule twice);
    grep for an existing heading before writing one.
- Transactional email: **Brevo REST API** only (`BREVO_API_KEY/FROM_EMAIL/
  FROM_NAME` via Doppler; irealty is the reference) — **no SMTP** in any
  CueLABS™ product.
- Data plane (cloud): per-product choice of **Aiven Postgres** or **Firestore**
  (Firebase-native/real-time products → Firestore; financial/relational →
  Postgres). Shared **Aiven Redis** with `REDIS_DB`-index tenancy per
  product/config (irealty pattern: discrete `REDIS_*` vars). **Doppler** is
  the env source of truth — project per repo, configs `dev / dev_personal /
  stg / prd`. Object storage: the sandbox project's default **Cloud Storage** bucket
  with per-product/env prefixes. Self-host compose bundles its own stores.
- Protocols (X-8): **HTTP/JSON is the default product API**; gRPC is a
  standardized option wherever a domain needs streaming, telemetry ingest,
  high-throughput internal s2s, or another documented transport requirement.
  Generated protocol clients live in `src/proto/` (with transitional generated
  client paths covered by the fleet `.prettierignore`). Upstat currently uses
  gRPC for OTLP ingest + internal s2s; its browser gRPC-Web/Envoy path is
  sunsetting at monitors-v2. Cloud Run requires end-to-end HTTP/2 (h2c) for
  gRPC services. A product's self-host Helm chart deploys Envoy only while that
  product exposes a gRPC-Web path.
