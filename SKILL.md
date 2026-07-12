---
name: cuelabs-project-standard
description: >-
  The CueLABS repository standard for coding agents. Use when bootstrapping a
  new CueLABS repo or standardizing an existing one (apparule, expendit, upstat,
  and future projects) — the canonical directory structure, per-service
  conventions, OSS community-health files, deploy layout, and cleanup rules.
---

# CueLABS Project Standard

This skill encodes how CueLABS repositories are structured so a coding agent can
**bootstrap a new repo** or **standardize an existing one** consistently. It
replaces the former `open-source-project-generator` Go CLI: scaffolding is just
directory creation, file templates, and standard tool invocations
(`create-next-app`, `go mod init`, …), all of which an agent does directly — and
an agent can also refactor an existing repo, which the CLI never could.

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
  docker/            Container / compose configuration
  helm/              ONE chart that deploys ALL services (incl. Envoy) to k8s
  terraform/         Infrastructure as code
docs/                overview.md, setup.md, api/, ui/
scripts/             Developer / CI helper scripts
```

Plus the root files listed under **Community health & config** below.

### Naming rule (important)
`api/common` is the shared Go backend in every repo. Every **other** service is
named by what it *does* (`measure`, `observability`, `image`), **never** by its
language (`go`/`python`/`nodejs`). Only create a service directory when a real
service exists — do not add empty `api/image` placeholders.

## Community health & config (required root files)

Mirror these from apparule (templates in [`templates/`](templates/)):

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
| `.dockerignore` | Root + one per build context; exclude `.env`/secrets/artifacts |
| `.editorconfig` | Shared editor settings (tabs for Go) |
| `Makefile` | Common tasks across services |
| `.github/dependabot.yml` | **Scoped per manifest**, grouped per ecosystem |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist |
| `.github/ISSUE_TEMPLATE/` | bug_report, feature_request, config.yml |

`dependabot.yml` must list one `updates` entry per real manifest directory
(`gomod /api/common`, `pip /api/<python-service>`, `npm /web`,
`pub /mobile/flutter`, `github-actions /`) and **must not** point at dead or
deprecated directories.

## Deploy convention
A single `deploy/helm` chart deploys **all** services — including the Envoy
gRPC-Web proxy where used — into a Kubernetes cluster. Do **not** create a
standalone `deploy/envoy/`; Envoy config lives inside the Helm chart.

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
                                               Aiven Postgres & Valkey (Redis)
```
- Auth: Firebase Authentication / Google sign-in.
- Backends deploy to GCP Cloud Run (and/or the Helm chart for k8s).
- gRPC services front a gRPC-Web Envoy proxy (deployed via the Helm chart).

## Recommended versions
Keep current; last reviewed with the values below.

| Area | Version |
|------|---------|
| Next.js / React / TypeScript | 16.x / 19.2 / 5.9 |
| Go | 1.25+ (`1.25-alpine` image) |
| Gin | v1.11 |
| Node | 20+ |
| Android (Kotlin / Gradle / compileSdk) | 2.2 / 9.1 / 36 |
| Python | 3.11+ |

Pin exact versions in each service's manifest; let Dependabot (scoped, grouped)
propose upgrades.
