---
name: oss-engineering-standards
description: >-
  The CueLABS repository standard for coding agents. Use when bootstrapping a
  new CueLABS repo or standardizing an existing one (apparule, expendit, upstat,
  and future projects) — the canonical directory structure, per-service
  conventions, OSS community-health files, deploy layout, and cleanup rules.
---

# CueLABS Engineering Standards

This skill encodes how CueLABS repositories are structured so a coding agent can
**bootstrap a new repo** or **standardize an existing one** consistently.
Scaffolding is just directory creation, file templates, and standard tool
invocations (`create-next-app`, `go mod init`, …), all of which an agent does
directly — and an agent can also refactor an existing repo in place.

The reference implementation is **cuesoftinc/apparule** — when in doubt, mirror it.

## Canonical structure

```
api/
  common/            Go backend — auth + core API. ALWAYS named "common".
  <service-name>/    Additional services, named by FUNCTION not language:
                     e.g. measure (apparule, Python pose), observability
                     (upstat, Python), image (TS/Node file service).
web/                 Next.js marketing site + dashboard
mobile/
  flutter/           Primary cross-platform app (Dart)
  android/           Native Android (Kotlin) — placeholder until built
  ios/               Native iOS (Swift) — placeholder until built
deploy/
  docker/            Extra container assets (compose itself lives at the repo root)
  helm/              ONE standard-form chart that deploys ALL services (incl. Envoy) to k8s
  terraform/         Cluster-agnostic IaC: installs the Helm chart via kubeconfig
docs/                overview.md, setup.md (+ optional api/, architecture.md)
scripts/             Developer / CI helper scripts
```

Plus the root files listed under **Community health & config** below.

### Naming rule (important)
`api/common` is the shared Go backend in every repo. Every **other** service is
named by what it *does* (`measure`, `observability`, `image`), **never** by its
language (`go`/`python`/`nodejs`). Only create a service directory when a real
service exists — do not add empty `api/image` placeholders.

## Community health & config (required root files)

**These files must have parity across all CueLABS repos** — byte-identical,
sourced from [`templates/`](templates/). Only `README.md`, `CHANGELOG.md`,
and `.github/dependabot.yml` are repo-specific (repo overview, its own history,
and its own manifest scoping); everything else in the table below — including the
compose-driven `Makefile` — is identical across repos.

| File | Purpose |
|------|---------|
| `README.md` | Overview, architecture diagram, repo structure, getting started, links |
| `CONTRIBUTING.md` | Fork/branch flow, Conventional Commits, review, layout |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1 |
| `SECURITY.md` | Private vulnerability reporting; secret-handling rules |
| `CODEOWNERS` | Default reviewers |
| `CHANGELOG.md` | Keep a Changelog format |
| `LICENSE` | Project license |
| `.gitignore` | Must NOT ignore `.dockerignore`; must ignore `.env*`, secrets |
| `.dockerignore` | Root byte-identical; plus one per build context (repo-specific, see `templates/dockerignore.*`) |
| `.editorconfig` | Shared editor settings (tabs for Go) |
| `Makefile` | Compose-driven standard targets (up/down/build/logs/…); identical across repos |
| `.env.example` | Root env template: per-service sections, dev-safe defaults, `NEXT_PUBLIC_*` block |
| `.github/dependabot.yml` | **Scoped per manifest**, grouped per ecosystem |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist |
| `.github/ISSUE_TEMPLATE/` | bug_report, feature_request, config.yml |

**What's in `templates/`:** ready-to-copy `LICENSE`, `CODEOWNERS`,
`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `PULL_REQUEST_TEMPLATE.md`,
`ISSUE_TEMPLATE/*`, `Makefile`, a `dependabot.example.yml`, an `env.example`,
Docker templates (`Dockerfile.go`, `Dockerfile.web`, `Dockerfile.python`,
`docker-compose.example.yml`, per-context `dockerignore.*`), the standard-form
Helm chart skeleton (`helm/`), and cluster-agnostic terraform (`terraform/`). Dotfile templates are stored
**without** a leading dot so they stay visible and are never applied to this repo
by accident — when adopting them, copy `templates/gitignore` → `.gitignore`,
`templates/dockerignore.root` → `.dockerignore`, and `templates/editorconfig` →
`.editorconfig`.

`dependabot.yml` is the one config that is **not** identical across repos: it
lists one `updates` entry per real manifest directory (`gomod /api/common`,
`pip /api/<python-service>`, `npm /web`, `pub /mobile/flutter`), grouped per
ecosystem, and **must not** point at dead/deprecated directories. It has **no**
`github-actions` entry — this standard uses no CI workflows, so that updater
would fail with "no workflows found".

## Service structure (production)
When bootstrapping or standardizing a service, **migrate existing code into
these layouts** — don't scaffold empty projects.

**Every service directory** (each `api/*`, `web`) carries its own internals,
consistent across repos: `README.md` (layout/run/config/test), `.gitignore`,
`.dockerignore` (see `templates/dockerignore.*`), and `.env.example` with the
service's native-run variables (compose users rely on the root `.env`).
Go module paths are canonical: `github.com/cuesoftinc/<repo>/api/common`.

**Go (`api/common`):**
```
cmd/server/main.go            entrypoint: slog JSON, config → deps → graceful shutdown
internal/config/              typed env config (fail-fast on missing secrets)
internal/handler/             thin HTTP/gRPC handlers
internal/middleware/          slog logging, request-id, CORS allowlist, recovery
internal/model/  internal/service/  internal/repository/  internal/router/
internal/util/   internal/proto/ (generated)
```
Singular package names. `/health` + `/ready`, `$PORT` (8080), structured `slog`,
graceful shutdown on SIGINT/SIGTERM. gRPC services multiplex gRPC + `/health`
over `$PORT` via h2c.

**Python (`api/<service>`, FastAPI):**
```
app/main.py app/config.py     FastAPI + lifespan (load models/clients once)
router/  service/  model/  repository/   (+ domain pkgs, e.g. ml/, analysis/, database/)
```
Singular folders. `lifespan` (never `@app.on_event`), `/health` + `/ready`, uvicorn,
non-root image, pinned deps.

**Next.js (`web`):**
```
src/app/                      routes — home at `/`, product dashboard at `/dashboard`
src/{components,lib,hooks,types,config,context}   src/proto/ (generated grpc-web, verbatim)
```
Minimal root `layout.tsx` (html/body — plus a CSS-in-JS registry only where the
repo uses one); the home page
renders its own shell; `/dashboard` gets a nested `layout.tsx`. `@/*` → `./src/*`,
`output: "standalone"`.

**Flutter (`mobile/flutter`):**
```
lib/main.dart
lib/src/features/<feature>/   lib/src/core/{theme,localization}
lib/src/services/  lib/src/shared/{,model}   lib/l10n/ (generated — stays)
```
Prefer `package:` imports over relative so moves are mechanical.

### File & folder naming (uniform across repos)
Same language ⇒ same conventions; each project keeps its own *features*.

| Language | Folders | Files |
|----------|---------|-------|
| Go | lowercase, **singular** package (`handler`, `service`, `model`, `repository`, `router`, `util`, `config`, `middleware`, `proto`) | `snake_case.go` |
| Python | lowercase, **singular** (`router`, `service`, `model`, `repository`) | `snake_case.py` |
| Next / TS | **kebab-case** (`shared-layouts/`, `change-password/`) | **Components PascalCase** (`NavBar.tsx`); modules/hooks/styles/types **kebab-case** (`use-auth.ts`, `home-context.ts`, `nav-bar.styles.ts`); Next reserved lowercase (`page.tsx`, `layout.tsx`, `route.ts`) |
| Dart | `snake_case` | `snake_case.dart` |

Generated code (`proto/`, `*_pb.*`, grpc-web clients) keeps its generated names — never rename it.

## Deploy convention
A single `deploy/helm` chart deploys **all** services — including the Envoy
gRPC-Web proxy where used — into a Kubernetes cluster. Do **not** create a
standalone `deploy/envoy/`; Envoy config lives inside the Helm chart.

The chart is standard-form (see `templates/helm/`): split
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

`deploy/terraform` (see `templates/terraform/`) is **cluster-agnostic**: the
helm provider authenticates via kubeconfig (`kubeconfig_path`/`kube_context`
variables) and installs the repo chart — no cloud-specific providers.

## Local development (Docker)
Each repo has a root `docker-compose.yml` and a compose-driven `Makefile`
(`make up` / `make down` / `make logs` / `make build`). Copy `.env.example` →
`.env` first. Service packaging (see `templates/Dockerfile.go`,
`templates/Dockerfile.web`, `templates/docker-compose.example.yml`):

- **Go services** — multi-stage, static binary (`CGO_ENABLED=0`), non-root user,
  honors `$PORT` (default 8080), `/health` HEALTHCHECK.
- **Next.js web** — `output: "standalone"` + multi-stage build that runs
  `node server.js` as the non-root `node` user (never `npm run dev` in an image).
- **Python services** — `templates/Dockerfile.python`: `python:3.12-slim`,
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
- **All GitHub Actions workflow files** (`.github/workflows/**`, or misplaced
  workflow YAMLs directly under `.github/`). CI is not part of this standard.
- Buggy/one-off scripts (e.g. old `refactor-structure.sh`).
- Stale planning/aspirational docs that no longer match reality.
- Generated artifacts committed by mistake (e.g. `output_landmarks.jpg`),
  committed build binaries, `tmp/` output.
- Dead `.gitkeep` files in directories that now hold real content.

Never remove:
- **Application code**, service assets/models, or test fixtures.
- Any `web/.deprecated/` directory (retained deliberately).
- Placeholder `.gitkeep`s in genuinely-empty standard dirs (`deploy/*`,
  `mobile/android`, `mobile/ios`, `scripts`).

## Procedure A — standardize an existing repo
1. Branch `chore/standardize-structure`.
2. Move services into place with `git mv` (preserves history). `api/common`
   (Go) stays put — its module path is unaffected. Rename functional services
   (e.g. `reliability-service` → `observability`).
3. `git grep -n <old-path>` and update every reference (Dockerfiles, compose,
   Makefile, docs, CI). Go modules with logical/bare module names are unaffected
   by folder moves; only path-based module names need a `go.mod` + import
   rewrite.
4. Add the community-health/config files (mirror apparule, adapt content).
5. Create any missing standard dirs (`deploy/{docker,helm,terraform}`, `scripts`)
   with `.gitkeep` placeholders.
6. Apply the cleanup rules above.
7. Verify: build/imports intact, `git status` clean, no app code deleted,
   `.deprecated` preserved. Open a PR (do not self-merge without review).

## Procedure B — bootstrap a new repo
1. Create the structure above (only the services you actually have).
2. `web`: `npx create-next-app@<version>` (see versions).
3. `api/common`: `go mod init github.com/cuesoftinc/<repo>/api/common` + Gin.
4. `mobile/flutter`: `flutter create`.
5. Add all community-health/config files from `templates/`.
6. Wire `deploy/helm` to deploy every service.

## Architecture conventions
```
client                                   server
web + dashboard (Next.js) ─┐             api/common (Go)  ── GCP Cloud Run
                           ├─ Firebase /  api/<svc> (Python/…) ── Cloud Run
flutter mobile ────────────┘  Google auth
                                         data: Firebase Firestore & Storage,
                                               Firebase (apparule), MongoDB (+ Redis) elsewhere
```
- Auth: Firebase Authentication, **Google sign-in ONLY** — no username/password
  signup or login anywhere in the ecosystem. Enforce at three layers:
  Email/Password provider disabled on the Firebase project; backends reject
  tokens with `sign_in_provider != google.com`; UI ships exactly one
  "Continue with Google" CTA. Sandbox identity project: `sandbox-e306a`;
  `account.cuesoft.io` is a future facade over the same Firebase project.
- Backends deploy to GCP Cloud Run (provisioned via the `cuesoft-iac` Pulumi
  ecosystem — never ad-hoc); frontends deploy to Firebase App Hosting; the
  Helm chart remains the self-host path.
- AI features use **Vertex AI** (Gemini via `aiplatform.googleapis.com`, ADC —
  see `cuesoft-iac/functions/cueprise-gemini-proxy`); no consumer AI-vendor
  API keys in cloud deployments. Self-host fallback: BYO Gemini/Groq env keys.
- gRPC services front a gRPC-Web Envoy proxy (deployed via the Helm chart).

## Recommended versions
Keep current; last reviewed with the values below.

| Area | Version |
|------|---------|
| Next.js / React / TypeScript | 16.x / 19.2 / 5.9 |
| Go | 1.25+ — builder image matches the module's `go` directive (`golang:1.25-alpine`; apparule is on 1.26) |
| Gin | v1.12 |
| Node | 24 (`node:24-slim` images) |
| Android (Kotlin / Gradle / compileSdk) | 2.2 / 9.1 / 36 — for future native apps |
| Python | 3.12 (`python:3.12-slim` images) |

Pin exact versions in each service's manifest; let Dependabot (scoped, grouped)
propose upgrades.
