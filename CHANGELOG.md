# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
