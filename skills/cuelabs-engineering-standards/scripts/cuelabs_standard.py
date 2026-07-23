#!/usr/bin/env python3
"""Audit and safely apply the portable CueLABS repository baseline."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "templates"
PROJECT_SCHEMA = SKILL_ROOT / "assets" / "schema" / "project.schema.json"

PORTABLE_TEMPLATE_TARGETS = {
    "gitignore": ".gitignore",
    "editorconfig": ".editorconfig",
}

CUELABS_TEMPLATE_TARGETS = {
    **PORTABLE_TEMPLATE_TARGETS,
    "CODEOWNERS": "CODEOWNERS",
    "CODE_OF_CONDUCT.md": "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md": "CONTRIBUTING.md",
    "LICENSE": "LICENSE",
    "SECURITY.md": "SECURITY.md",
    "PULL_REQUEST_TEMPLATE.md": ".github/PULL_REQUEST_TEMPLATE.md",
    "ISSUE_TEMPLATE/bug_report.md": ".github/ISSUE_TEMPLATE/bug_report.md",
    "ISSUE_TEMPLATE/config.yml": ".github/ISSUE_TEMPLATE/config.yml",
    "ISSUE_TEMPLATE/feature_request.md": ".github/ISSUE_TEMPLATE/feature_request.md",
}

CUELABS_APPLICATION_TEMPLATE_TARGETS = {
    "Makefile": "Makefile",
    "dockerignore.root": ".dockerignore",
    "env.example": ".env.example",
}

PORTABLE_REPOSITORY_FILES = [
    "CODEOWNERS",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "SECURITY.md",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/feature_request.md",
]
PORTABLE_APPLICATION_FILES = ["Makefile", ".dockerignore", ".env.example"]

STATUSES = {"active", "planned", "paused", "absent"}


class ManifestError(ValueError):
    """The project manifest cannot be parsed or violates its schema."""


class BlockingCollision(RuntimeError):
    """A required file target is occupied by a directory or blocked by a file."""

    def __init__(self, collisions: list[str]):
        super().__init__("blocking path collisions: " + ", ".join(collisions))
        self.collisions = collisions


@dataclass(frozen=True)
class Manifest:
    state: str
    profile: str
    data: dict[str, Any] | None
    errors: list[str]


@dataclass(frozen=True)
class Audit:
    repository: str
    profile: str
    manifest: str
    manifest_errors: list[str]
    active_deviations: list[dict[str, Any]]
    surfaces: dict[str, str]
    missing_shared_files: list[str]
    drifted_shared_files: list[str]
    blocking_collisions: list[str]
    missing_repository_files: list[str]

    @property
    def conforming(self) -> bool:
        return (
            self.manifest not in {"missing", "invalid"}
            and not self.manifest_errors
            and not self.missing_shared_files
            and not self.drifted_shared_files
            and not self.blocking_collisions
            and not self.missing_repository_files
        )


@dataclass(frozen=True)
class PlanStep:
    order: int
    action: str
    mode: str
    paths: list[str]
    reason: str


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return None
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError as error:
            raise ManifestError(f"invalid quoted scalar: {error}") from error
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def yaml_tokens(text: str) -> list[tuple[int, str, int]]:
    tokens: list[tuple[int, str, int]] = []
    for line_number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise ManifestError(f"line {line_number}: tabs are not allowed")
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2:
            raise ManifestError(
                f"line {line_number}: indentation must use multiples of two spaces"
            )
        content = raw.strip()
        quote: str | None = None
        for index, character in enumerate(content):
            if character in {"'", '"'}:
                quote = None if quote == character else (character if quote is None else quote)
            elif character == "#" and quote is None and (
                index == 0 or content[index - 1].isspace()
            ):
                content = content[:index].rstrip()
                break
        if content:
            tokens.append((indent, content, line_number))
    return tokens


def split_mapping(content: str, line_number: int) -> tuple[str, str]:
    if ":" not in content:
        raise ManifestError(f"line {line_number}: expected a mapping entry")
    key, raw_value = content.split(":", 1)
    key = key.strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", key):
        raise ManifestError(f"line {line_number}: invalid key {key!r}")
    return key, raw_value.strip()


def parse_yaml_block(
    tokens: list[tuple[int, str, int]], index: int, indent: int
) -> tuple[Any, int]:
    if index >= len(tokens) or tokens[index][0] != indent:
        raise ManifestError("invalid indentation")
    is_list = tokens[index][1].startswith("-")
    container: Any = [] if is_list else {}

    while index < len(tokens):
        current_indent, content, line_number = tokens[index]
        if current_indent < indent:
            break
        if current_indent > indent:
            raise ManifestError(f"line {line_number}: unexpected indentation")

        if is_list:
            if not content.startswith("-"):
                break
            item = content[1:].strip()
            index += 1
            if not item:
                if index >= len(tokens) or tokens[index][0] <= indent:
                    raise ManifestError(f"line {line_number}: empty list item")
                value, index = parse_yaml_block(tokens, index, tokens[index][0])
                container.append(value)
                continue
            if ":" not in item:
                container.append(parse_scalar(item))
                continue

            key, raw_value = split_mapping(item, line_number)
            entry: dict[str, Any] = {}
            if raw_value:
                entry[key] = parse_scalar(raw_value)
            elif index < len(tokens) and tokens[index][0] > indent:
                entry[key], index = parse_yaml_block(tokens, index, tokens[index][0])
            else:
                entry[key] = None
            if index < len(tokens) and tokens[index][0] > indent:
                continuation, index = parse_yaml_block(tokens, index, tokens[index][0])
                if not isinstance(continuation, dict):
                    raise ManifestError(
                        f"line {line_number}: list mapping continuation must be a mapping"
                    )
                duplicates = set(entry) & set(continuation)
                if duplicates:
                    raise ManifestError(
                        f"line {line_number}: duplicate keys {sorted(duplicates)}"
                    )
                entry.update(continuation)
            container.append(entry)
            continue

        if content.startswith("-"):
            break
        key, raw_value = split_mapping(content, line_number)
        if key in container:
            raise ManifestError(f"line {line_number}: duplicate key {key!r}")
        index += 1
        if raw_value:
            container[key] = parse_scalar(raw_value)
        elif index < len(tokens) and tokens[index][0] > indent:
            container[key], index = parse_yaml_block(tokens, index, tokens[index][0])
        else:
            container[key] = None
    return container, index


def parse_yaml_subset(text: str) -> dict[str, Any]:
    tokens = yaml_tokens(text)
    if not tokens:
        raise ManifestError("manifest is empty")
    if tokens[0][0] != 0:
        raise ManifestError("top-level keys must not be indented")
    value, index = parse_yaml_block(tokens, 0, 0)
    if index != len(tokens):
        _, _, line_number = tokens[index]
        raise ManifestError(f"line {line_number}: could not parse entry")
    if not isinstance(value, dict):
        raise ManifestError("manifest root must be a mapping")
    return value


def validate_status(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or value not in STATUSES:
        errors.append(f"{path} must be one of {sorted(STATUSES)}")


def validate_manifest_data(data: dict[str, Any]) -> list[str]:
    # Load the bundled schema so a missing or malformed published contract fails
    # before the manual, dependency-free validation below.
    try:
        schema = json.loads(PROJECT_SCHEMA.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return [f"bundled project schema is unavailable: {error}"]

    errors: list[str] = []
    allowed = set(schema["properties"])
    unknown = sorted(set(data) - allowed)
    if unknown:
        errors.append(f"unknown top-level fields: {unknown}")
    missing = sorted(set(schema["required"]) - set(data))
    if missing:
        errors.append(f"missing required fields: {missing}")

    if data.get("schemaVersion") != 1:
        errors.append("schemaVersion must be 1")
    name = data.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        errors.append("name must use lowercase letters, digits, and hyphens")
    if data.get("profile") not in {"base", "cuelabs"}:
        errors.append("profile must be 'base' or 'cuelabs'")

    surfaces = data.get("surfaces")
    if not isinstance(surfaces, dict):
        errors.append("surfaces must be a mapping")
    else:
        for key, value in surfaces.items():
            if not isinstance(key, str):
                errors.append("surface names must be strings")
            elif isinstance(value, dict):
                for child, status in value.items():
                    validate_status(status, f"surfaces.{key}.{child}", errors)
            else:
                validate_status(value, f"surfaces.{key}", errors)

    capabilities = data.get("capabilities", {})
    if not isinstance(capabilities, dict):
        errors.append("capabilities must be a mapping")
    else:
        for key, value in capabilities.items():
            validate_status(value, f"capabilities.{key}", errors)

    deployment = data.get("deployment", {})
    if not isinstance(deployment, dict) or any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in deployment.items()
    ):
        errors.append("deployment must map string keys to string values")

    deviations = data.get("deviations", [])
    if not isinstance(deviations, list):
        errors.append("deviations must be a list")
    else:
        for index, item in enumerate(deviations):
            prefix = f"deviations[{index}]"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            unknown_deviation = sorted(set(item) - {"id", "reason", "expires"})
            if unknown_deviation:
                errors.append(f"{prefix} has unknown fields: {unknown_deviation}")
            for required in ("id", "reason"):
                if not isinstance(item.get(required), str) or not item[required]:
                    errors.append(f"{prefix}.{required} must be a non-empty string")
            expires = item.get("expires")
            if expires is not None:
                if not isinstance(expires, str):
                    errors.append(f"{prefix}.expires must be a date or null")
                else:
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", expires):
                        errors.append(f"{prefix}.expires must use YYYY-MM-DD")
                    else:
                        try:
                            expiration = date.fromisoformat(expires)
                        except ValueError:
                            errors.append(f"{prefix}.expires must use YYYY-MM-DD")
                        else:
                            if expiration < date.today():
                                errors.append(
                                    f"{prefix}.expires has passed "
                                    f"({expiration.isoformat()})"
                                )
    return errors


def load_manifest(path: Path, *, required: bool) -> Manifest:
    if not path.is_file():
        return Manifest(
            state="missing" if required else "not-required",
            profile="unknown",
            data=None,
            errors=[],
        )
    try:
        data = parse_yaml_subset(path.read_text())
    except (OSError, ManifestError) as error:
        return Manifest("invalid", "unknown", None, [str(error)])
    errors = validate_manifest_data(data)
    if errors:
        return Manifest("invalid", str(data.get("profile", "unknown")), data, errors)
    return Manifest("valid", str(data["profile"]), data, [])


def infer_surfaces(repo: Path) -> dict[str, str]:
    checks = {
        "web": (repo / "web" / "package.json").is_file(),
        "go-api": (repo / "api" / "common" / "go.mod").is_file(),
        "flutter": (repo / "mobile" / "flutter" / "pubspec.yaml").is_file(),
        "helm": (repo / "deploy" / "helm" / "Chart.yaml").is_file(),
        "terraform": any((repo / "deploy" / "terraform").glob("*.tf")),
    }
    return {name: ("active" if active else "not-detected") for name, active in checks.items()}


def aggregate_status(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        statuses = set(value.values())
        for status in ("active", "planned", "paused", "absent"):
            if status in statuses:
                return status
    return "absent"


def declared_surfaces(data: dict[str, Any]) -> dict[str, str]:
    declared = data["surfaces"]
    mobile = declared.get("mobile", declared.get("flutter", "absent"))
    flutter = (
        mobile.get("flutter", mobile)
        if isinstance(mobile, dict)
        else mobile
    )
    backend = declared.get("backend", declared.get("api", "absent"))
    return {
        "web": aggregate_status(declared.get("web", "absent")),
        "go-api": aggregate_status(backend),
        "flutter": aggregate_status(flutter),
        "helm": (
            "active"
            if data.get("deployment", {}).get("selfHost") == "helm"
            else "not-declared"
        ),
        "terraform": (
            "active"
            if data.get("deployment", {}).get("infrastructure") == "terraform"
            else "not-declared"
        ),
    }


def find_collision(repo: Path, destination_name: str) -> str | None:
    destination = repo / destination_name
    current = destination.parent
    while current != repo:
        if current.is_symlink() or (current.exists() and not current.is_dir()):
            return destination_name
        current = current.parent
    if destination.is_symlink() or (
        destination.exists() and not destination.is_file()
    ):
        return destination_name
    return None


def has_active_application(surfaces: dict[str, str]) -> bool:
    return any(
        surfaces.get(name) == "active" for name in ("web", "go-api", "flutter")
    )


def required_targets(profile: str, surfaces: dict[str, str]) -> dict[str, str]:
    targets = dict(
        CUELABS_TEMPLATE_TARGETS
        if profile == "cuelabs"
        else PORTABLE_TEMPLATE_TARGETS
    )
    if profile == "cuelabs" and has_active_application(surfaces):
        targets.update(CUELABS_APPLICATION_TEMPLATE_TARGETS)
    return targets


def inspect(repo: Path) -> Audit:
    inferred = infer_surfaces(repo)
    product_evidence = any(
        inferred.get(name) == "active" for name in ("web", "go-api", "flutter")
    )
    manifest = load_manifest(repo / ".cuelabs" / "project.yaml", required=product_evidence)
    if manifest.state == "valid" and manifest.data is not None:
        surfaces = declared_surfaces(manifest.data)
    elif manifest.state == "invalid":
        surfaces = {name: "unknown-invalid-manifest" for name in inferred}
    else:
        surfaces = inferred

    active_deviations = (
        [dict(item) for item in manifest.data.get("deviations", [])]
        if manifest.state == "valid" and manifest.data is not None
        else []
    )
    targets = required_targets(manifest.profile, surfaces)
    missing_shared: list[str] = []
    drifted_shared: list[str] = []
    collisions: list[str] = []
    for source_name, destination_name in targets.items():
        collision = find_collision(repo, destination_name)
        if collision:
            collisions.append(collision)
            continue
        destination = repo / destination_name
        if not destination.is_file():
            missing_shared.append(destination_name)
            continue
        source = TEMPLATE_ROOT / source_name
        if not source.is_file():
            collisions.append(f"{destination_name} (bundled template missing)")
        elif destination.read_bytes() != source.read_bytes():
            drifted_shared.append(destination_name)

    repository_specific = ["README.md", "CHANGELOG.md"]
    if manifest.profile != "cuelabs":
        repository_specific.extend(PORTABLE_REPOSITORY_FILES)
        if has_active_application(surfaces):
            repository_specific.extend(PORTABLE_APPLICATION_FILES)
    if has_active_application(surfaces):
        repository_specific.append(".github/dependabot.yml")
    missing_specific = sorted(
        path for path in repository_specific if not (repo / path).is_file()
    )
    return Audit(
        repository=str(repo),
        profile=manifest.profile,
        manifest=manifest.state,
        manifest_errors=manifest.errors,
        active_deviations=active_deviations,
        surfaces=surfaces,
        missing_shared_files=sorted(missing_shared),
        drifted_shared_files=sorted(drifted_shared),
        blocking_collisions=sorted(collisions),
        missing_repository_files=missing_specific,
    )


def build_plan(audit: Audit) -> list[PlanStep]:
    steps: list[PlanStep] = []

    def add(action: str, mode: str, paths: list[str], reason: str) -> None:
        steps.append(PlanStep(len(steps) + 1, action, mode, paths, reason))

    if audit.manifest == "missing":
        add(
            "Author and validate the project manifest",
            "manual",
            [".cuelabs/project.yaml"],
            "Surface readiness must be declared before application files are applied.",
        )
    elif audit.manifest == "invalid":
        add(
            "Repair and validate the project manifest",
            "manual",
            [".cuelabs/project.yaml"],
            "; ".join(audit.manifest_errors),
        )
    if audit.active_deviations:
        deviation_ids = ", ".join(
            str(deviation["id"]) for deviation in audit.active_deviations
        )
        add(
            "Review active manifest deviations",
            "manual",
            [".cuelabs/project.yaml"],
            f"Documented exceptions still require follow-up: {deviation_ids}.",
        )
    if audit.blocking_collisions:
        add(
            "Resolve blocking path collisions",
            "manual",
            audit.blocking_collisions,
            "A required file target or one of its parents is not the expected type.",
        )
    if audit.drifted_shared_files:
        add(
            "Review shared-file drift and replace intentionally",
            "manual",
            audit.drifted_shared_files,
            "Existing files differ from the canonical templates and are never overwritten automatically.",
        )
    if audit.missing_shared_files:
        add(
            "Copy missing canonical templates",
            "automatic",
            audit.missing_shared_files,
            "The apply operation can create these files without overwriting existing paths.",
        )
    if audit.missing_repository_files:
        add(
            "Author repository-specific files",
            "manual",
            audit.missing_repository_files,
            "These files require repository-specific content and are not copied blindly.",
        )
    add(
        "Run verification and repository-native checks",
        "automatic",
        [],
        "Confirm the baseline, then run tests appropriate to active surfaces.",
    )
    return steps


def print_audit(audit: Audit, *, heading: str) -> None:
    print(f"# {heading}")
    print()
    print(f"- Repository: `{audit.repository}`")
    print(f"- Profile: `{audit.profile}`")
    print(f"- Project manifest: {audit.manifest}")
    print(f"- Baseline conforming: {'yes' if audit.conforming else 'no'}")
    if audit.manifest_errors:
        print("- Manifest errors:")
        for error in audit.manifest_errors:
            print(f"  - {error}")
    print()
    print("## Active deviations")
    print()
    if audit.active_deviations:
        for deviation in audit.active_deviations:
            expiry = deviation.get("expires")
            expiry_text = (
                f"expires `{expiry}`" if expiry is not None else "no expiry"
            )
            print(
                f"- `{deviation['id']}`: {deviation['reason']} ({expiry_text})"
            )
    else:
        print("- None")
    print()
    print("## Detected surfaces")
    print()
    for name, state in audit.surfaces.items():
        print(f"- `{name}`: {state}")
    sections = (
        ("Missing shared files", audit.missing_shared_files),
        ("Drifted shared files", audit.drifted_shared_files),
        ("Blocking collisions", audit.blocking_collisions),
        ("Missing repository-specific files", audit.missing_repository_files),
    )
    for title, paths in sections:
        print()
        print(f"## {title}")
        print()
        if paths:
            for path in paths:
                suffix = (
                    " (author for this repository; do not copy blindly)"
                    if title == "Missing repository-specific files"
                    else ""
                )
                print(f"- `{path}`{suffix}")
        else:
            print("- None")


def print_plan(audit: Audit, plan: list[PlanStep]) -> None:
    print_audit(audit, heading="CueLABS standards plan")
    print()
    print("## Ordered actions")
    print()
    for step in plan:
        print(f"{step.order}. **{step.action}** (`{step.mode}`)")
        print(f"   - Why: {step.reason}")
        if step.paths:
            print(f"   - Paths: {', '.join(f'`{path}`' for path in step.paths)}")
    print()
    print("## Assumptions")
    print()
    print("- Existing files are preserved unless a human approves replacement.")
    print("- A valid manifest overrides placeholder filesystem evidence.")
    print("- Only declared active product surfaces receive application-only files.")


def emit_audit(audit: Audit, output_format: str, *, heading: str) -> None:
    if output_format == "json":
        payload = asdict(audit)
        payload["conforming"] = audit.conforming
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_audit(audit, heading=heading)


def emit_plan(audit: Audit, output_format: str) -> None:
    plan = build_plan(audit)
    if output_format == "json":
        payload = asdict(audit)
        payload["conforming"] = audit.conforming
        payload["plan"] = [asdict(step) for step in plan]
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_plan(audit, plan)


def apply_missing(repo: Path) -> list[str]:
    audit = inspect(repo)
    if audit.manifest == "missing":
        raise ManifestError(
            "required project manifest is missing: .cuelabs/project.yaml"
        )
    if audit.manifest == "invalid":
        raise ManifestError("; ".join(audit.manifest_errors))
    if audit.blocking_collisions:
        raise BlockingCollision(audit.blocking_collisions)
    copied: list[str] = []
    targets = required_targets(audit.profile, audit.surfaces)
    for source_name, destination_name in targets.items():
        source = TEMPLATE_ROOT / source_name
        destination = repo / destination_name
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        copied.append(destination_name)
    return copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit or apply the CueLABS repository baseline."
    )
    parser.add_argument("operation", choices=("audit", "plan", "apply", "verify"))
    parser.add_argument("--repo", default=".", help="Target repository path")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args()


def is_git_worktree(repo: Path) -> bool:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(repo),
                "rev-parse",
                "--is-inside-work-tree",
                "--show-toplevel",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    lines = result.stdout.splitlines()
    if result.returncode != 0 or len(lines) != 2 or lines[0] != "true":
        return False
    return Path(lines[1]).resolve() == repo.resolve()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    if not is_git_worktree(repo):
        print(f"error: not a git repository: {repo}", file=sys.stderr)
        return 2

    before = inspect(repo)
    if args.operation == "audit":
        emit_audit(before, args.format, heading="CueLABS standards audit")
        return 0
    if args.operation == "plan":
        emit_plan(before, args.format)
        return 0
    if args.operation == "apply":
        try:
            copied = apply_missing(repo)
        except (BlockingCollision, ManifestError) as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
        after = inspect(repo)
        emit_audit(after, args.format, heading="CueLABS standards apply result")
        if args.format == "markdown":
            print()
            print("## Copied files")
            print()
            if copied:
                for path in copied:
                    print(f"- `{path}`")
            else:
                print("- None; existing files were preserved.")
        return 0 if after.conforming else 1

    emit_audit(before, args.format, heading="CueLABS standards verification")
    return 0 if before.conforming else 1


if __name__ == "__main__":
    raise SystemExit(main())
