#!/usr/bin/env python3
"""Audit and safely apply the portable CueLABS repository baseline."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).resolve().parents[1] / "assets" / "templates"

BASE_TEMPLATE_TARGETS = {
    "CODEOWNERS": "CODEOWNERS",
    "CODE_OF_CONDUCT.md": "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md": "CONTRIBUTING.md",
    "LICENSE": "LICENSE",
    "SECURITY.md": "SECURITY.md",
    "gitignore": ".gitignore",
    "editorconfig": ".editorconfig",
    "PULL_REQUEST_TEMPLATE.md": ".github/PULL_REQUEST_TEMPLATE.md",
    "ISSUE_TEMPLATE/bug_report.md": ".github/ISSUE_TEMPLATE/bug_report.md",
    "ISSUE_TEMPLATE/config.yml": ".github/ISSUE_TEMPLATE/config.yml",
    "ISSUE_TEMPLATE/feature_request.md": ".github/ISSUE_TEMPLATE/feature_request.md",
}

APPLICATION_TEMPLATE_TARGETS = {
    "Makefile": "Makefile",
    "dockerignore.root": ".dockerignore",
    "env.example": ".env.example",
}


@dataclass(frozen=True)
class Audit:
    repository: str
    profile: str
    manifest: str
    surfaces: dict[str, str]
    missing_shared_files: list[str]
    missing_repository_files: list[str]

    @property
    def conforming(self) -> bool:
        return (
            self.manifest != "missing"
            and not self.missing_shared_files
            and not self.missing_repository_files
        )


def detect_profile(manifest: Path) -> str:
    if not manifest.is_file():
        return "unknown"
    match = re.search(
        r"(?m)^\s*profile\s*:\s*[\"']?([a-z0-9-]+)", manifest.read_text()
    )
    return match.group(1) if match else "unknown"


def detect_surfaces(repo: Path) -> dict[str, str]:
    checks = {
        "web": (repo / "web" / "package.json").is_file(),
        "go-api": (repo / "api" / "common" / "go.mod").is_file(),
        "flutter": (repo / "mobile" / "flutter" / "pubspec.yaml").is_file(),
        "helm": (repo / "deploy" / "helm" / "Chart.yaml").is_file(),
        "terraform": any((repo / "deploy" / "terraform").glob("*.tf")),
    }
    return {name: ("active" if active else "not-detected") for name, active in checks.items()}


def inspect(repo: Path) -> Audit:
    manifest = repo / ".cuelabs" / "project.yaml"
    surfaces = detect_surfaces(repo)
    has_product_surface = any(
        state == "active"
        for name, state in surfaces.items()
        if name in {"web", "go-api", "flutter"}
    )
    template_targets = dict(BASE_TEMPLATE_TARGETS)
    if has_product_surface:
        template_targets.update(APPLICATION_TEMPLATE_TARGETS)
    missing_shared = sorted(
        destination
        for destination in template_targets.values()
        if not (repo / destination).is_file()
    )
    repository_specific = ["README.md", "CHANGELOG.md"]
    if has_product_surface:
        repository_specific.append(".github/dependabot.yml")
    missing_specific = sorted(
        path for path in repository_specific if not (repo / path).is_file()
    )
    return Audit(
        repository=str(repo),
        profile=detect_profile(manifest),
        manifest=(
            "present"
            if manifest.is_file()
            else ("missing" if has_product_surface else "not-required")
        ),
        surfaces=surfaces,
        missing_shared_files=missing_shared,
        missing_repository_files=missing_specific,
    )


def print_markdown(audit: Audit, *, heading: str) -> None:
    print(f"# {heading}")
    print()
    print(f"- Repository: `{audit.repository}`")
    print(f"- Profile: `{audit.profile}`")
    print(f"- Project manifest: {audit.manifest}")
    print(f"- Baseline conforming: {'yes' if audit.conforming else 'no'}")
    print()
    print("## Detected surfaces")
    print()
    for name, state in audit.surfaces.items():
        print(f"- `{name}`: {state}")
    print()
    print("## Missing shared files")
    print()
    if audit.missing_shared_files:
        for path in audit.missing_shared_files:
            print(f"- `{path}`")
    else:
        print("- None")
    print()
    print("## Missing repository-specific files")
    print()
    if audit.missing_repository_files:
        for path in audit.missing_repository_files:
            print(f"- `{path}` (author for this repository; do not copy blindly)")
    else:
        print("- None")


def emit(audit: Audit, output_format: str, *, heading: str) -> None:
    if output_format == "json":
        payload = asdict(audit)
        payload["conforming"] = audit.conforming
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_markdown(audit, heading=heading)


def apply_missing(repo: Path) -> list[str]:
    copied: list[str] = []
    surfaces = detect_surfaces(repo)
    has_product_surface = any(
        state == "active"
        for name, state in surfaces.items()
        if name in {"web", "go-api", "flutter"}
    )
    template_targets = dict(BASE_TEMPLATE_TARGETS)
    if has_product_surface:
        template_targets.update(APPLICATION_TEMPLATE_TARGETS)
    for source_name, destination_name in template_targets.items():
        source = TEMPLATE_ROOT / source_name
        destination = repo / destination_name
        if destination.exists():
            continue
        if not source.is_file():
            raise FileNotFoundError(f"missing bundled template: {source}")
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
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()
    if not (repo / ".git").exists():
        print(f"error: not a git repository: {repo}", file=sys.stderr)
        return 2

    before = inspect(repo)
    if args.operation == "audit":
        emit(before, args.format, heading="CueLABS standards audit")
        return 0
    if args.operation == "plan":
        emit(before, args.format, heading="CueLABS standards plan")
        return 0
    if args.operation == "apply":
        copied = apply_missing(repo)
        after = inspect(repo)
        emit(after, args.format, heading="CueLABS standards apply result")
        if args.format == "markdown":
            print()
            print("## Copied files")
            print()
            if copied:
                for path in copied:
                    print(f"- `{path}`")
            else:
                print("- None; existing files were preserved.")
        return 0

    emit(before, args.format, heading="CueLABS standards verification")
    return 0 if before.conforming else 1


if __name__ == "__main__":
    raise SystemExit(main())
