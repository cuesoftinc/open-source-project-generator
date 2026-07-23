---
name: cuelabs-mobile-standard
description: Build, audit, or standardize CueLABS mobile applications. Use for Flutter architecture, Riverpod, routing, repositories, TEST_MODE fakes, flavors, Firebase authentication, design tokens, golden tests, mobile CI, device behavior, or web-to-mobile product parity.
---

# CueLABS Mobile Standard

Build mobile surfaces only after the product has approved mobile scope and
design frames. Keep product behavior consistent across clients without forcing
web chrome or interaction idioms onto mobile.

## Required reference

Read [references/flutter-implementation.md](references/flutter-implementation.md)
before changing a Flutter application, its native platform projects, mobile
tests, mobile workflows, or mobile architecture.

## Workflow

1. Inspect `.cuelabs/project.yaml`, mobile documentation, Figma frames, the
   Flutter tree, flavors, and current tests.
2. Confirm mobile is `active`. If it is `planned`, do not run `flutter create`
   or add mobile CI unless the user explicitly starts the mobile phase.
3. Map the work to feature-first presentation, domain, data, app, routing, or
   core layers.
4. Preserve abstract repositories and environment-specific provider overrides.
   Keep remote APIs and fakes behind the same interfaces.
5. Implement screens only when a corresponding approved frame and flow exist.
6. Use shared design-system primitives for recurring interaction patterns.
7. Update code generation outputs, tests, and documentation together.
8. Run formatting, codegen-fresh checks, analysis, unit/widget tests, relevant
   goldens, and a platform build proportionate to the change.
9. Clean regenerable build state at closeout.

## Guardrails

- Do not create empty native or Flutter applications for future plans.
- Do not wire production APIs before the repository interfaces and product
  contracts are ready.
- Do not hand-edit generated code or generated token output.
- Do not silently delete quarantined legacy code.
- Do not generate golden baselines on an incompatible host and weaken
  tolerances to hide the difference.
- Do not use screen-local state invalidation when a domain mutation affects
  sibling surfaces.
- Do not ship a mobile screen without an approved design frame.

## Result format

Report the product state, frames and contracts consulted, architectural layers
changed, platform-specific decisions, tests/builds run, and remaining external
dependencies.
