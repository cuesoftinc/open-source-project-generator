# Contributing

This repository holds the CueLABS™ engineering standard as a skill for coding
agents ([`SKILL.md`](SKILL.md)) plus reusable file [`templates/`](templates/).

## How to contribute

- **Change the standard:** open a PR editing [`SKILL.md`](SKILL.md) and/or the
  relevant file under [`templates/`](templates/). Explain the rationale and which
  repositories it affects.
- **Fix a template:** edit the file under `templates/`. Note that dotfile
  templates are stored without a leading dot (e.g. `templates/gitignore` →
  `.gitignore`).
- Use [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `chore:`, `docs:`).
- At least one approving review from a [CODEOWNER](CODEOWNERS) is required
  before merge.

## Applying the standard

To bootstrap a new repository or standardize an existing one, point a coding
agent at [`SKILL.md`](SKILL.md).

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md).
