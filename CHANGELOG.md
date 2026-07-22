# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- `SKILL.md`: eight interaction-integrity locks from the mobile
  interaction-contract audit (stale siblings, fake optimism, dead controls,
  silent failures, danger ladder, MI primitives, destinations, forms) (#129).

- `SKILL.md`: eight cross-platform parity canons from the apparule
  mobile↔web adjudication — chrome-scoped alignment, canon-fact sweep
  checklist, parity scope rules, session-restore gate, danger-ladder
  additions, entity-reference affordances, unit-toggle conversion, and
  single-listing cross-client constants (#128).

- `SKILL.md` mobile standard: the canvas-first rule — every shipped screen
  has a Figma frame (design first or drop); frameless screens escape visual
  QA (#127).

- `SKILL.md`: Mobile (Flutter) implementation standard — FVM-pinned toolchain,
  official MVVM+Repository vocabulary over a feature-first tree, Riverpod 3,
  typed go_router, mock-first fake repositories with seeded assets (TEST_MODE
  parity), Figma-variable-generated ThemeExtensions, one module per Figma
  component set, very_good_analysis + alchemist/patrol testing, dev/stg/prd
  flavors with Doppler-fed dart-defines, and the Google-only Firebase auth
  flow (#120).

- `SKILL.md` web-canon sections from the 2026-07-20/21 program waves: tri-state
  theme contract (#94), double-writer coordination-ledger protocol (#95),
  unset-theme-is-design-default ruling (#96), audit-convergence sync — danger
  ladder, chart construction, micro-labels, star-badge construction (#97),
  fleet chrome naming + date idioms (#98), settings IA shapes (#99),
  review-round canons — floating-layer Y-flip, anatomy fidelity, findings-are-
  classes (#100), chart dash-normalization gotcha (#101), landing type-fidelity
  canon (#102), quiet-danger reference implementation (#104), worktree removal
  at the merge gate + the 2-build-worktree cap (#105), the FAH
  `images.unoptimized` gotcha + WebP loader canon (#106), overlay focus
  contract + named-control API (#107), SEO plumbing canon (#108),
  contrast-token canon — `-text` variants, `on-crit`, fixed-light locales
  (#109, #110), the canonical `web/src/` tree — shape is a parity item (#111),
  heavy-embed intent-gate canon (#112), legal-link canon (#113), pre-paint
  persisted-chrome init + deferred-hydration contract (#114), layout-stability
  canon (#115), and the a11y closeout canons — skip link, real `inert`, stable
  tab ids, ⌘K, `test-session` key, unique landmarks (#116).

- `templates/Dockerfile.python`, per-context `templates/dockerignore.{go,web,python}`,
  `templates/env.example`, standard-form Helm chart skeleton (`templates/helm/`),
  and cluster-agnostic terraform (`templates/terraform/`).
- Port convention (`api/common`=8080, `web`=3000, additional APIs increment from
  8081) and a per-language file & folder naming standard in `SKILL.md`.
- `SKILL.md`: the CueLABS repository standard plus bootstrap and standardize
  procedures for coding agents.
- `templates/`: canonical community-health and config templates (LICENSE,
  CODEOWNERS, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, dotfile templates stored
  without the leading dot — `gitignore`, `editorconfig`, `dockerignore.root` —
  a dependabot example, and PR/issue templates), shared byte-identically across
  CueLABS repositories.

### Changed

- `SKILL.md` mobile standard: platform floors & flavor plumbing (iOS 15 with
  Firebase 12, flutter-tool-only builds, load-bearing flavor config naming,
  seed-bundling assertion in CI) and the safe-area contract with notched test
  surfaces — both verified on live devices (#126).

- `SKILL.md` mobile standard: goldens are authored on Linux (alchemist CI
  config normalizes text only; curve/gradient AA is platform-bound) via a
  dockerized regen script or dispatch workflow; `url_launcher` joins the
  pin ledger (#125).

- `SKILL.md` mobile standard: flavors mirror the org environment model —
  `dev` + `prod` only (the sandbox account is CueLABS production); the
  generic dev/stg/prd trio is rejected (#124).

- `SKILL.md` mobile standard: resolver-verified pin corrections from the
  skeleton wave — riverpod_lint 3.x as a native analyzer plugin (custom_lint
  retired), build_runner/freezed/intl caps, gen-l10n key removal,
  go_router_builder public mixins, AGP 9 resValues default (#123).

- `SKILL.md` mobile standard: legacy-quarantine rule — superseded code moves
  to `lib/legacy/` and is removed only after its replacement ships with an
  explicit user go (#121).

- `SKILL.md` deferral-sweep updates (2026-07-21): upstat's Floating-UI
  deviation retired (converged to Radix; bespoke layers recorded), nav-rail
  prefetch canon revised to intent-based (hover/focus `router.prefetch`),
  web manifest + `SkipLink.tsx` join the SEO canon and byte-identical
  shared-files list, transform-only rule for per-frame movers joins the
  layout-stability canon, and changelog discipline (single bucket headings,
  merged top-ups).

- `SKILL.md`: retired-system references scrubbed to current-system voice
  throughout (#103).


- Refined the production service-structure guidance (singular Go packages,
  FastAPI `lifespan`, web `src/` + route conventions) and synced the `Makefile`,
  `Dockerfile.go`, `Dockerfile.web`, and `docker-compose.example.yml` templates.

- SKILL.md: per-service internals standard (README/.gitignore/.dockerignore/
  .env.example per service), canonical Go module paths, SSR-safety and
  127.0.0.1-healthcheck gotchas, envoy-in-compose pattern, standard-form
  Helm/terraform deploy convention, scoped `.dockerignore` parity claim, and
  several accuracy fixes (docs/ list, data stores, root-layout wording).
- PR template: dropped the CI reference (the standard has no CI workflows).
