# Client compatibility

The catalog follows the Agent Skills directory convention:
`skills/<skill-name>/SKILL.md`.

| Client | User installation | Project installation | Notes |
|---|---|---|---|
| Codex | `gh skill install ... --agent codex --scope user` | Shared `.agents/skills/` | Includes `agents/openai.yaml` UI metadata |
| Cursor | `gh skill install ... --agent cursor --scope user` | Shared `.agents/skills/` | Skills can trigger automatically or explicitly |
| GitHub Copilot | `--agent github-copilot` | Shared `.agents/skills/` | Supported by GitHub CLI |
| Claude Code | `--agent claude-code` | Client-specific directory | Supported by GitHub CLI |

Run `gh skill install --help` for the current list of supported clients and
destinations. GitHub's skill commands are in preview, so pin the GitHub CLI in
managed environments and validate installation behavior before organization-
wide rollout.

## Compatibility policy

- The canonical skill frontmatter uses only `name` and `description`.
- Client-specific metadata lives under `agents/`.
- Skills do not rely on one client's private tool names.
- Scripts use Python's standard library unless a dependency is explicitly
  documented.
- Client-specific behavior must be additive and must not change the portable
  workflow.

CI validates the catalog with the local validator and GitHub's official
non-publishing validation.
