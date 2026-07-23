# Contributing

CueLABS™ Engineering Standards is an open-source catalog of Agent Skills,
profiles, templates, and validation tools.

## Choose the change type

- **Clarification**: improve wording without changing required behavior.
- **Additive standard**: add an optional or newly supported capability.
- **Behavior change**: change a shared requirement or default.
- **Breaking change**: require repository migrations or change installation,
  manifest, template, or skill contracts.
- **Product decision**: keep it in the product repository unless it applies to
  the CueLABS profile as a whole.

Open an issue or discussion before a broad behavior or breaking change. Explain
the problem, affected profiles, affected products, migration, and rollback.

## Change a skill

1. Keep `SKILL.md` focused on triggers and workflow and below 500 lines.
2. Put detailed domain material one level deep in `references/`.
3. Put deterministic operations in `scripts/`.
4. Put copied templates and other output resources in `assets/`.
5. Keep `agents/openai.yaml` consistent with the skill name and purpose.
6. Add or update at least five evaluation cases covering trigger,
   do-not-trigger, and ambiguous requests.
7. Add migration guidance when behavior changes.

Do not add README, changelog, or installation files inside an individual skill.
Human-facing project documentation belongs at the repository root or in
`docs/`.

## Change a template

Templates live under
`skills/cuelabs-engineering-standards/assets/templates/`. Explain whether the
file is byte-identical across repositories or an example requiring
product-specific adaptation. Never put secrets or production identifiers in a
template.

## Validate

Run:

```bash
python3 scripts/validate_catalog.py
gh skill publish --dry-run
```

When changing the baseline tool, also exercise all four operations against a
temporary git repository:

```bash
python3 skills/cuelabs-engineering-standards/scripts/cuelabs_standard.py audit
python3 skills/cuelabs-engineering-standards/scripts/cuelabs_standard.py plan
python3 skills/cuelabs-engineering-standards/scripts/cuelabs_standard.py apply
python3 skills/cuelabs-engineering-standards/scripts/cuelabs_standard.py verify
```

Use Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`). At least one
CODEOWNER approval is required before merge.

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md).
