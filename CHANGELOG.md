# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed

- Transformed the repository from a Go scaffolding CLI into a skill for coding
  agents: added `SKILL.md` (the CueLABS repository standard plus bootstrap and
  standardize procedures) and `templates/` (canonical community-health and
  config file templates).
- Renamed the repository from `open-source-project-generator` to
  `oss-engineering-standards`.
- Established parity: `templates/` now holds the byte-identical community-health
  files shared across CueLABS repos (LICENSE, CODEOWNERS, CONTRIBUTING,
  CODE_OF_CONDUCT, SECURITY, .gitignore, .editorconfig, .dockerignore, and
  PR/issue templates). The `dependabot.example.yml` has no `github-actions`
  entry (this standard uses no CI workflows).

### Removed

- The Go CLI implementation (`cmd/`, `internal/`, `pkg/`), `go.mod`/`go.sum`,
  the three Dockerfiles, `docker-compose.yml`, build/version scripts, the stale
  Go-CLI `Makefile`, and the outdated CLI documentation.
