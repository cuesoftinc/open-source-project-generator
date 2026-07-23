# Containers and deployment

Use the templates bundled with `$cuelabs-engineering-standards` when applying
these conventions.

## Deploy convention
A single `deploy/helm` chart deploys **all** services — including the Envoy
gRPC-Web proxy where used — into a Kubernetes cluster. Do **not** create a
standalone `deploy/envoy/`; Envoy config lives inside the Helm chart.

The chart is standard-form (see core `assets/templates/helm/`): split
`deployment.yaml`/`service.yaml` ranging over a `services:` values map,
`_helpers.tpl` with the k8s recommended labels (name/instance/part-of/chart),
liveness+readiness probes (`healthPath`/`readyPath`, tcp fallback),
`runAsNonRoot`, `resources`, and `NOTES.txt`. Envoy's config is embedded via
`.Files.Get` in a ConfigMap. Always `helm lint` + `helm template` before
shipping.

Chart gotchas that cost real time:
- Pods run `runAsNonRoot` with a **numeric** `runAsUser` (default 10001;
  web images run as `node` = 1000, Envoy as 101) — kubelet cannot verify
  named users and rejects the pod otherwise.
- **Bump `Chart.yaml` version on every chart change** — the terraform helm
  provider does not upgrade local charts whose version is unchanged.
- Images live under the `cuesoft` Docker Hub org: `cuesoft/<repo>-<service>`.

`deploy/terraform` (see core `assets/templates/terraform/`) is **cluster-agnostic**: the
helm provider authenticates via kubeconfig (`kubeconfig_path`/`kube_context`
variables) and installs the repo chart — no cloud-specific providers.

## Local development (Docker)
Each repo has a root `docker-compose.yml` and a compose-driven `Makefile`
(`make up` / `make down` / `make logs` / `make build`). Copy `.env.example` →
`.env` first. Service packaging (see core `assets/templates/Dockerfile.go`,
`assets/templates/Dockerfile.web`, `assets/templates/docker-compose.example.yml`):

- **Go services** — multi-stage, static binary (`CGO_ENABLED=0`), non-root user,
  honors `$PORT` (default 8080), `/health` HEALTHCHECK.
- **Next.js web** — `output: "standalone"` + multi-stage build that runs
  `node server.js` as the non-root `node` user (never `npm run dev` in an image).
- **Python services** — core `assets/templates/Dockerfile.python`: `python:3.12-slim`,
  non-root uid 10001, PORT-aware 127.0.0.1 `/health` healthcheck with a long
  start period (model loads), `uvicorn app.main:app`.
- **gRPC-Web repos** — run Envoy in compose (image pinned, config mounted from
  `deploy/helm/envoy/envoy.yaml`, backend network-aliased to the cluster
  target); Envoy takes the next port slot (e.g. upstat :8082) and the web image
  gets `NEXT_PUBLIC_ENVOY_URL` as a build arg.

**Port convention (parity across repos):** so muscle memory carries between
services, every repo publishes the same host ports — `api/common` → **8080**,
`web` → **3000**, and each additional API increments from there (**8081**, 8082, …;
e.g. apparule's `api/measure` → 8081). Compose sets `PORT` and the published port
to the same value, and the web image's `NEXT_PUBLIC_BASE_URL` build arg targets
`http://localhost:8080`.

Gotchas that cost real time:
- Build the web image on **`node:*-slim` (glibc), not Alpine** — Next 16's
  Turbopack build workers are unreliable on musl.
- Keep **TypeScript on 5.x**; Next's build-time TS check crashes on the
  TypeScript 7 native compiler. Dependabot npm-group PRs can silently bump
  `typescript`/`eslint`/`@types/node` to breaking majors — pin them.
- `NEXT_PUBLIC_*` are inlined at build time → pass them as Docker build args.
- **SSR safety**: never touch `localStorage`/`window` during render — only in
  `useEffect`/handlers (or behind `typeof window !== "undefined"`); prerender
  crashes otherwise. Session state that both client and shell components need
  belongs in cookies, written and read by the same names.
- All healthchecks (web and APIs) target `127.0.0.1`, never `localhost`
  (IPv6 resolution causes false-unhealthy containers).

## Cleanup rules (when standardizing)
Remove (safe — not application code):
- **Non-canonical GitHub Actions workflow files**: preserve the ratified
  `.github/workflows/build-and-test.yml`, the deferred tag-gated `release.yml`
  when present, and ratified surface workflows such as Apparule's
  `mobile-goldens.yml` and `mobile-e2e.yml`; remove obsolete, duplicate,
  misplaced, or unratified workflow files.
- Buggy/one-off scripts (e.g. old `refactor-structure.sh`).
- Stale planning/aspirational docs that no longer match reality.
- Generated artifacts committed by mistake (e.g. `output_landmarks.jpg`),
  committed build binaries, `tmp/` output.
- Dead `.gitkeep` files in directories that now hold real content.

Never remove:
- **Application code**, service assets/models, or test fixtures.
- Placeholder `.gitkeep`s in genuinely-empty standard dirs (`deploy/*`,
  `mobile/android`, `mobile/ios`, `scripts`).
