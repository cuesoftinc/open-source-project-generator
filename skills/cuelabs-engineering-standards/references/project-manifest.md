# Project manifest syntax

`.cuelabs/project.yaml` uses a deliberately bounded YAML subset so the bundled
CLI remains dependency-free and behaves consistently in Codex, Cursor, CI, and
local shells.

## Supported syntax

- One UTF-8 document containing a mapping at its root.
- Bare mapping keys matching `[A-Za-z][A-Za-z0-9_-]*`.
- Block mappings and sequences using spaces. Use two-space indentation.
- Indentationless sequences immediately below a mapping key.
- Flow mappings and sequences, including nested collections.
- Plain single-line strings, single- and double-quoted strings, base-10
  integers, `true`, `false`, and YAML null spellings.
- Literal and folded block strings (`|` and `>`), including indentation and
  chomping indicators.
- Comments outside quoted or block strings.

## Unsupported syntax

Do not use anchors, aliases, tags, merge keys, directives, document markers,
complex keys, quoted block-mapping keys, tabs for indentation, multi-document
streams, or multi-line plain strings. Quote a plain string when it begins with
a reserved YAML indicator.

These exclusions are part of the manifest format, not missing parser features.
The bundled CLI rejects them with an actionable error. The JSON Schema defines
the parsed data shape; it does not broaden the serialization syntax.

## Canonical shape

Use `assets/project.example.yaml` as the starting point. Declare only current
approved state, keep surface and capability names stable, and record exceptions
under `deviations` with a durable ID and reason.
