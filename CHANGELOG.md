# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
