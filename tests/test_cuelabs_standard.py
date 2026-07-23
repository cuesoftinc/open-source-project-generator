from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "cuelabs-engineering-standards"
    / "scripts"
    / "cuelabs_standard.py"
)
SPEC = importlib.util.spec_from_file_location("cuelabs_standard", SCRIPT)
assert SPEC and SPEC.loader
standard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = standard
SPEC.loader.exec_module(standard)


class StandardsCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        (self.repo / ".git").mkdir()
        (self.repo / "README.md").write_text("# Fixture\n")
        (self.repo / "CHANGELOG.md").write_text("# Changelog\n")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_manifest(self, surfaces: str = "  web: active\n") -> None:
        manifest = self.repo / ".cuelabs" / "project.yaml"
        manifest.parent.mkdir()
        manifest.write_text(
            "schemaVersion: 1\n"
            "name: fixture\n"
            "profile: cuelabs\n"
            "surfaces:\n"
            f"{surfaces}"
            "capabilities: {}\n"
            "deployment: {}\n"
            "deviations: []\n"
        )

    def copy_required_templates(self, *, application: bool) -> None:
        targets = dict(standard.BASE_TEMPLATE_TARGETS)
        if application:
            targets.update(standard.APPLICATION_TEMPLATE_TARGETS)
        for source_name, destination_name in targets.items():
            source = standard.TEMPLATE_ROOT / source_name
            destination = self.repo / destination_name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())

    def test_declared_planned_surface_overrides_placeholder_files(self) -> None:
        self.write_manifest("  web: planned\n")
        (self.repo / "web").mkdir()
        (self.repo / "web" / "package.json").write_text('{"name":"placeholder"}\n')
        self.copy_required_templates(application=False)

        audit = standard.inspect(self.repo)

        self.assertEqual(audit.surfaces["web"], "planned")
        self.assertNotIn("Makefile", audit.missing_shared_files)
        self.assertNotIn(".env.example", audit.missing_shared_files)
        self.assertNotIn(".github/dependabot.yml", audit.missing_repository_files)
        self.assertTrue(audit.conforming)

    def test_shared_file_drift_fails_conformance(self) -> None:
        self.copy_required_templates(application=False)
        (self.repo / "LICENSE").write_text("not the canonical license\n")

        audit = standard.inspect(self.repo)

        self.assertIn("LICENSE", audit.drifted_shared_files)
        self.assertFalse(audit.conforming)

    def test_invalid_manifest_is_rejected(self) -> None:
        manifest = self.repo / ".cuelabs" / "project.yaml"
        manifest.parent.mkdir()
        manifest.write_text("schemaVersion: nope\nsurfaces: []\n")
        self.copy_required_templates(application=False)

        audit = standard.inspect(self.repo)

        self.assertEqual(audit.manifest, "invalid")
        self.assertTrue(audit.manifest_errors)
        self.assertFalse(audit.conforming)
        with self.assertRaises(standard.ManifestError):
            standard.apply_missing(self.repo)

    def test_plan_is_ordered_and_distinguishes_manual_and_automatic(self) -> None:
        (self.repo / "web").mkdir()
        (self.repo / "web" / "package.json").write_text('{"name":"fixture"}\n')

        plan = standard.build_plan(standard.inspect(self.repo))

        self.assertEqual([step.order for step in plan], list(range(1, len(plan) + 1)))
        self.assertEqual(plan[0].action, "Author and validate the project manifest")
        self.assertTrue(any(step.mode == "automatic" for step in plan))
        self.assertTrue(any(step.mode == "manual" for step in plan))

    def test_apply_rejects_directory_collision(self) -> None:
        self.copy_required_templates(application=False)
        (self.repo / "CODEOWNERS").unlink()
        (self.repo / "CODEOWNERS").mkdir()

        with self.assertRaises(standard.BlockingCollision) as context:
            standard.apply_missing(self.repo)

        self.assertIn("CODEOWNERS", context.exception.collisions)

    def test_apply_is_idempotent_and_preserves_existing_files(self) -> None:
        first = standard.apply_missing(self.repo)
        second = standard.apply_missing(self.repo)

        self.assertTrue(first)
        self.assertEqual(second, [])
        self.assertTrue(standard.inspect(self.repo).conforming)

    def test_manifest_deviation_list_is_parsed_and_validated(self) -> None:
        manifest = self.repo / ".cuelabs" / "project.yaml"
        manifest.parent.mkdir()
        manifest.write_text(
            "schemaVersion: 1\n"
            "name: fixture\n"
            "profile: base\n"
            "surfaces:\n"
            "  web: absent # intentionally not implemented\n"
            "deviations:\n"
            "  - id: EX-1\n"
            "    reason: Intentional exception\n"
            "    expires: 2026-12-31\n"
        )
        self.copy_required_templates(application=False)

        audit = standard.inspect(self.repo)

        self.assertEqual(audit.manifest, "valid")
        self.assertEqual(audit.manifest_errors, [])
        self.assertTrue(audit.conforming)


if __name__ == "__main__":
    unittest.main()
