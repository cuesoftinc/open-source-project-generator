# CueLABS Engineering Standards

The canonical repository standard for CueLABS projects, packaged as a skill for
coding agents.

## What this is

This repository defines how CueLABS repositories are structured and provides the
reusable files to achieve it:

- **[`SKILL.md`](SKILL.md)** — the standard and the procedures (bootstrap a new
  repo; standardize an existing one), for a coding agent to follow.
- **[`templates/`](templates/)** — reusable file templates: community-health
  files, a `dependabot.example.yml`, and issue/PR templates. Dotfile templates
  are stored without the leading dot (copy `gitignore` → `.gitignore`,
  `dockerignore.root` → `.dockerignore`, `editorconfig` → `.editorconfig`).

The reference implementation of the standard is **cuesoftinc/apparule**.

## Usage

Point a coding agent at [`SKILL.md`](SKILL.md) and ask it to bootstrap a new
repository or standardize an existing one. The skill defines the directory
structure, naming rules (`api/common` for the Go backend; other services named
by function, never by language), required root files, the deploy convention (one
Helm chart deploys all services including Envoy), recommended versions, and the
cleanup rules.

## Repository contents

```
SKILL.md        The standard + bootstrap/standardize procedures
templates/      Reusable file templates
.github/        Issue and pull-request templates for this repo
```

Plus the usual community-health files: `LICENSE`, `CONTRIBUTING.md`,
`CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`.

## License

See [LICENSE](LICENSE).
