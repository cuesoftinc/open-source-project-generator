# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
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

- Refined the production service-structure guidance (singular Go packages,
  FastAPI `lifespan`, web `src/` + route conventions) and synced the `Makefile`,
  `Dockerfile.go`, `Dockerfile.web`, and `docker-compose.example.yml` templates.

### Changed
- SKILL.md: per-service internals standard (README/.gitignore/.dockerignore/
  .env.example per service), canonical Go module paths, SSR-safety and
  127.0.0.1-healthcheck gotchas, envoy-in-compose pattern, standard-form
  Helm/terraform deploy convention, scoped `.dockerignore` parity claim, and
  several accuracy fixes (docs/ list, data stores, root-layout wording).
- PR template: dropped the CI reference (the standard has no CI workflows).

