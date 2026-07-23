# Web tooling parity canon

## Contents

- Package scripts and boundary checks
- Prettier, Vitest, Playwright, and TypeScript
- Tailwind and Next.js conventions
- Accessibility and layout stability
- Legal links, contrast, SEO, overlays, images, and known exceptions

## Canon

Ratified 2026-07-19 (converged via the cross-repo tooling-parity pass; the
listed shared files are BYTE-IDENTICAL across repos — verify by shasum):

- **Scripts** — identical name set in every `web/package.json`:
  `dev / build / start / lint / lint:fix / typecheck / test / test:watch /
  test:e2e / check:boundaries`. Compositions pinned: `lint` =
  `prettier --check` + eslint + `check:boundaries`; `typecheck` =
  `next typegen && tsc --noEmit`; `test` = `vitest run`.
- **Boundaries** — ONE byte-identical `web/scripts/check-boundaries.mjs`:
  engine = superset rule library (legacyImport, forbiddenImports, rawHex,
  fetchOnlyIn, viewBoundaries); per-repo active-rule lists live in a
  marked config section keyed by `package.json` name; every rule is
  negative-tested (fires on an injected violation).
- **Prettier** — byte-identical `.prettierrc`/`.prettierignore`;
  `.prettierignore` is sourced from the core skill's
  `assets/templates/prettierignore.web` and carries
  the fleet superset of generated OpenAPI + protocol-client paths so products
  never customize it when gRPC arrives; one brace glob
  `**/*.{ts,tsx,js,jsx,mjs,cjs}` (prettier hard-errors on zero-match patterns —
  never enumerate separate globs).
- **Vitest** — canonical config: `@vitejs/plugin-react` +
  `vite-tsconfig-paths` + root `./vitest.setup.ts`, jsdom default.
  Repo-specific needs stay as COMMENTED, labeled blocks (apparule: no
  `NEXT_PUBLIC_TEST_MODE` in unit env — two suites assert the unset
  defaults — plus its jsdom URL option).
- **Playwright** — `PW_PORT` env convention (defaults: apparule 3311 ·
  expendit 3100 · upstat 3131), host `127.0.0.1`, e2e in CI mode =
  `next start` against the prebuilt TEST_MODE app. upstat runs serial
  (`workers: 1`) by design — shared mutable mock narrative.
- **tsconfig** — byte-identical (route-types entries included).
- **Tailwind v4 + typed config org-wide [Ratified 2026-07-20]**: all
  repos run Tailwind v4 (`@tailwindcss/postcss`, tokens via a
  `@theme inline` block in globals.css over the tokens.css vars; alpha
  via native v4 modifiers) and a typed `next.config.ts`. No
  husky/lint-staged anywhere — formatting and lint are CI-enforced.
  **Pre-paint persisted-chrome init (ratified 2026-07-21)**: ANY
  persisted layout-affecting chrome state (rail expansion, theme,
  density) resolves in a pre-paint init script in the root layout —
  the themeInitScript pattern — never post-hydration (upstat's rail
  animating 56→240px after hydrate was 0.3–0.5 CLS on every
  dashboard route); skeletons reserve their loaded heights. React 19
  hydration truths (verified empirically): the lazy-hydration
  dangerouslySetInnerHTML skip silently NUKES mismatched server DOM,
  and dehydrated Suspense boundaries are discarded if a parent
  re-render reaches them — deferred-hydration wrappers must not
  re-render, must keep band elements identity-stable, and bands own
  their own state swaps (upstat Defer.tsx documents the contract).
  **Heavy-embed intent gate (ratified 2026-07-21, fleet)**: heavyweight
  third-party embeds (the Scalar API reference is the archetype) load
  behind a `next/dynamic ssr:false` boundary whose SSR placeholder
  RESERVES the embed's viewport slice (no CLS), and the import itself
  is gated on USER INTENT (first pointer/key/wheel gesture, plus an
  explicit load button for the SR virtual-cursor path) — `ssr:false`
  alone still downloads right after hydration. Page chrome stays
  SSR'd. `docs-api-payload.spec.ts` (byte-identical fleet file) locks
  the settled pre-intent JS per product and that intent still mounts
  the full embed. Related bundle truths: the framework floor is ~107K
  encoded, and nav-rail prefetch is INTENT-BASED (ratified 2026-07-21,
  expendit reference: `prefetch={false}` + `router.prefetch` on first
  pointerenter/focus per item) — viewport-prefetching every pillar
  converged all dashboard routes to one ~350K chunk union; intent
  prefetch keeps cold routes at their own chunk set (−42% settled JS)
  while hover/focus still fires the fetch before click completes.
  **Changelog discipline (ratified 2026-07-21)**: Keep a Changelog
  strictly — ONE `### <Bucket>` heading per bucket per section, in
  canonical order (Added, Changed, Deprecated, Removed, Fixed,
  Security). Top-ups MERGE entries into the existing bucket headings
  under `[Unreleased]`, never append a second `### Changed` (five
  duplicate heading sets accumulated across three repos before this
  was caught — user-flagged). The standards repo's own CHANGELOG gets
  an entry with every SKILL canon merge, same rules.
  **A11y closeout canons (ratified 2026-07-21, fleet)**: (1) every
  route ships a skip-to-content link — `components/ui/SkipLink.tsx`,
  first focusable in the root layout/shell, `href="#main"`, hidden
  until focus, token-only construction; every `<main>` carries
  `id="main"` + `tabIndex={-1}`; e2e: first Tab on a fresh load lands
  on it, activation moves focus to main. (2) Decorative interactive
  mocks set the REAL `inert` attribute (React 19 boolean prop) —
  `aria-hidden` + `pointer-events-none` alone leaves focusables in
  the tab order. (3) Radix Tabs (and any aria-controls consumer)
  never derive `value` from display labels — slugified stable ids
  (spaces make invalid IDREFs, an axe critical). (4) Command palette
  opens on ⌘K/Ctrl+K wherever a palette exists (product-specific
  aliases like upstat's "/" may coexist; products without a palette
  are per-product scope, not drift). (5) TEST_MODE session state:
  sessionStorage, key `<product>.test-session`. (6) Landmarks with
  the same role carry DISTINCT labels (two navs both "Primary"/
  "Marketing" fail landmark-unique; suffix the variant: "Primary,
  compact", "Marketing, sticky"). Axe home gates lock the regression
  families per repo (IDREF/name/table/landmark rules at any impact).
  **Layout-stability canon (ratified 2026-07-21, fleet)**: CLS's
  dominant cause is client-persisted layout state resolving
  post-paint — any state that changes GEOMETRY (nav rail width,
  sidebar collapse, density) resolves PRE-PAINT via a root-layout
  init script setting a `data-*` attr on `<html>` (the theme-script
  pattern), with CSS binding the geometry to a var; the React store
  hydrates from the same source (`useSyncExternalStore`). Async
  widgets reserve their rendered size via `--widget-h-*` tokens +
  `Skeleton kind="frame"`; shell-level banners reserve their slot.
  Below-the-fold demo panels mount IO-gated (`DeferredPanel`:
  intersection + startTransition + height-reserving placeholder).
  Lock: session-windowed CLS probe e2e (< 0.1) on home + the densest
  dashboards, run against the TEST_MODE prod build. Anything that
  MOVES per-frame (crosshair tooltips, hover followers) positions via
  `transform`, never `left`/`top` — layout-property movers are CLS
  sources (upstat home 0.0108→0.0001 from one tooltip).
  **Legal-link canon (ratified 2026-07-21, fleet)**: Terms =
  `https://terms.cuesoft.io`, Privacy = `https://privacy.cuesoft.io` —
  the ONLY legal-link targets (always https; never local `/terms` or
  `/privacy` routes — two products shipped dead or `/` placeholder
  hrefs on signin for two months). Signin carries the consent line
  ("By continuing you agree to the Terms and Privacy Policy.") with
  both links; MarketingFooter Legal column points at the same URLs;
  external-link idiom is `target="_blank" rel="noreferrer"`
  (noopener is implied; apparule's `noopener noreferrer` converges on
  next touch). Each repo's signin e2e pins the exact hrefs.
  **Contrast-token canon (ratified 2026-07-21, fleet)**: the
  tinted-chip recipe (`text-X on bg-X/14`) fails AA in light theme for
  mid-lightness hues — every hue used AS TEXT on its own tint ships a
  paired `--<hue>-text` variant (OKLCH: darken L only until ≥4.5:1 on
  the tint composited over the worst surface; base hue stays for
  fills, borders, icons ≥3:1, and AA-large stats). White-on-critical
  text uses an explicit `--on-crit` token, never raw #FFFFFF
  (brand-mandated surfaces exempt). Fixed-light locales (gradient CTA
  bands, public status pages) pin `data-theme="light"` in code and the
  Light mode on the canvas frame. Lock shape: an e2e recomputing every
  recipe pair from the SERVED CSS in both themes asserting ≥4.5:1,
  plus a rendered sweep with walk-up backdrop compositing on the
  densest chip surface. Figma carries the same `-text` variables
  (same collection, both modes) bound to chip/pill/nav text fills.
  **SEO plumbing canon (ratified 2026-07-21, fleet)**: every product
  ships `app/sitemap.ts` (public routes only — never dashboard/auth),
  `app/robots.ts` (disallow /dashboard + /api, sitemap ref),
  `metadataBase` + `alternates.canonical: "./"` in the ROOT layout
  (the "./" form resolves per-route — verified in dev and prod),
  a 1200×630 `opengraph-image` card + twitter summary_large_image,
  and REAL brand icons (favicon.ico multi-size + apple-icon 180 —
  the create-next-app stock Vercel favicon shipped on two products
  for two months; the shared e2e pins each product's favicon hash ≠
  siblings'), plus `app/manifest.ts` (served /manifest.webmanifest:
  product name/short_name, token theme/background colors, the icon
  set — the shared spec asserts it's linked, resolves, names the
  product, and every icon 200s). `web/e2e/seo.spec.ts`,
  `web/components/ui/SkipLink.tsx` (sha-verified across products), and
  `web/scripts/generate-brand-assets.mjs` join the byte-identical
  shared-files list (config keyed by package name).
  **Overlay focus contract (ratified 2026-07-21, fleet)**: every
  Sheet/Modal/Dialog/palette captures its opener on open and restores
  focus to it on close (Radix controlled dialogs with a null triggerRef
  restore to BODY — capture in `onOpenAutoFocus`, restore in
  `onCloseAutoFocus`); Escape dismisses from ANY focused element inside
  (bind on the dialog container, never an inner input); dialogs carry
  `aria-modal`. e2e probe shape per repo: open → Tab inside → Escape
  closes → focus is back on the trigger. **Named-control API
  (ratified 2026-07-21)**: selection/icon-only controls make the
  accessible name COMPILE-MANDATORY (union prop: visible `label` OR
  `aria-label` — expendit `Checkbox` is the reference); axe e2e gates
  pin zero criticals on the densest table surface per product.
  **Firebase App Hosting image gotcha (root-caused 2026-07-21)**: the
  FAH Next adapter injects `images.unoptimized = true` at deploy build
  unless `images.loader`/`unoptimized` is explicitly set — `next/image`
  silently serves raw originals live (no srcset, `/_next/image` 404s).
  Products with raster imagery ship pre-generated WebP width buckets +
  a custom loader (apparule `demo-image-loader.ts` is the reference);
  an e2e pins every demo img to a sized-WebP srcset and the LCP
  candidate to `fetchpriority=high` (Next 16: `priority` alone no
  longer emits the hint), never lazy.
  v4 gotchas (root-caused, pixel-verified):
  pin `text-*` line-heights to px where nested font-size scopes
  inherit; v4's universal reset zeroes UA `td/th` padding (base rule
  if tables relied on it); `shadow-sm`→`shadow-xs` rename; fractional
  sizes like `h-4.5` were v3 no-ops but real in v4 (audit icons);
  responsive visibility lives on wrappers (display-utility CSS order).
- **Catalogued non-parity (deliberate)**: per-repo `eslint.config.mjs`
  extensions (expendit import bans + testing-library; upstat X-8
  ignores). Changing these is an ecosystem decision, not repo drift.
