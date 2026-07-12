# CueLABS Project Standard

The canonical repository standard for CueLABS projects, packaged as a **skill for
coding agents** rather than a CLI.

## What this is

This repository used to be a Go scaffolding CLI that generated new projects. Scaffolding, though, is just directory creation, file
templates, and standard tool invocations (`create-next-app`, `go mod init`, …) —
all of which a coding agent does directly, and an agent can additionally
*standardize an existing repo*, which the CLI could not. So the CLI has been
replaced by:

- **[`SKILL.md`](SKILL.md)** — the standard and the procedures (bootstrap a new
  repo; standardize an existing one), for a coding agent to follow.
- **[`templates/`](templates/)** — reusable file templates: community-health
  files, a scoped `dependabot.example.yml`, and issue/PR templates. Dotfile
  templates are stored without the leading dot (copy `dockerignore.root` →
  `.dockerignore`, `editorconfig` → `.editorconfig`).

The reference implementation of the standard is **cuesoftinc/apparule**.

## Usage

Point a coding agent at [`SKILL.md`](SKILL.md) and ask it to either bootstrap a
new repository or standardize an existing one. The skill defines the directory
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
