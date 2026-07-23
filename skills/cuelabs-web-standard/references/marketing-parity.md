# Marketing navigation, footer, and theme parity

## Contents

- Shared footer inventory
- CueLABS brand and legal copy
- Mobile footer structure
- Marketing navigation
- Theme behavior
- Link verification

## Canon

Ratified 2026-07-19. All products share ONE link inventory — same
sections, same link counts, same destinations (identical hrefs) — while
each product renders it in its own visual design. A diverging link set is
a parity violation. `<product>` = apparule/expendit/upstat (lowercase in
URLs); `<Product>` = display name.

- **Footer = brand block + 4 columns + legal bar.** Brand block:
  wordmark + one-line tagline. Columns (links pinned):
  - *Product* (4): Features · Try Cloud · Self Host · product slot
    (apparule "For designers" · expendit "Pricing" · upstat "Platform";
    slots are MARKETING anchors, never app routes) — landing anchors
    only.
  - *Community CTA placement* (2026-07-19): GitHub/Discord conversion
    moments live in exactly three spots — the nav star badge, ONE
    mid-page developers/community section (GitHub + Discord pair), and
    the footer Community column. Bottom sections use differentiated real
    destinations (status page, GitBook deep links, roadmap,
    cuelabs.cuesoft.io) — never extra GitHub/Discord CTAs.
  - *Docs* (4): Docs `https://cuesoft.gitbook.io/<product>` · Quickstart
    `…/setup` · API reference `https://<product>.cuesoft.io/docs/api`
    **[Ratified 2026-07-20]** — the in-app interactive Scalar reference
    rendered live from the repo's `docs/api/openapi.yaml` (a public
    `/docs/api` route in every product; the spec stays single-source in
    `docs/`, served to the embed by a route handler) · Self-host guide
    `…/system/deployment`. (GitBook URL slugs = SUMMARY.md group/page,
    e.g. `product/roadmap`, `system/deployment`; GitBook keeps the
    prose api-surface page.)
  - *Community* (4): GitHub `https://github.com/cuesoftinc/<product>` ·
    Discord `https://discord.gg/CDfZxxrxbb` · Roadmap
    `https://cuesoft.gitbook.io/<product>/product/roadmap` · CueLABS™
    `https://cuelabs.cuesoft.io`. Discord channel copy anywhere in the
    product reads **`#<product>-lab`** (`#apparule-lab` / `#expendit-lab`
    / `#upstat-lab` — the real channels on the CueLABS™ server; channel
    names are never invented).
- **Brand mark (ratified 2026-07-19)**: every text occurrence of the
  CueLABS™ name — docs, Figma canvases, UI copy, marketing prose, AND
  link labels/anchor text (the footer Community column link reads
  "CueLABS™") — is written **CueLABS™** (trademark symbol). The ONLY
  exemption is literal URLs/hostnames (`https://cuelabs.cuesoft.io`).
  **Brand copy (user-ratified 2026-07-19)**: the product attribution
  line reads "An open-source product by CueLABS™" — never
  "by Cuesoft CueLABS™" (the legal bar already establishes CueLABS™ as
  a Cuesoft Inc. division). The compound **"open-source" is always
  hyphenated** in UI copy, docs, and canvases (URLs/slugs keep their
  own spelling).
  - *Legal* (3): Privacy `https://privacy.cuesoft.io` · Terms
    `https://terms.cuesoft.io` · Status `https://status.cuesoft.io`.
- **Footer mobile structure (pinned 2026-07-19, reference: upstat
  MarketingFooter)**: below `md` — brand block full-width first, then
  the 4 link columns in an orderly 2-column grid, divider, legal bar
  with the © line first and the utilities (security + language) as ONE
  grouped cluster wrapping beneath; at `md+` the columns join one row
  (upstat reference classes: `grid grid-cols-2 gap-8 md:grid-cols-5`
  with brand `col-span-2 md:col-span-1`; legal bar `flex flex-wrap
  justify-between`). Each product keeps its visual design; the mobile
  STACKING structure is parity.
- **Legal bar** (verbatim, name substituted): `© Cuesoft Inc. 2026.
  <Product>. CueLABS™ Division. MIT License.` — "Cuesoft Inc." links to
  `https://cuesoft.io`; "CueLABS™ Division" links to
  `https://cuelabs.cuesoft.io`; "MIT License" links to
  `https://github.com/cuesoftinc/<product>/blob/main/LICENSE`. The bar
  also carries a language selector (English-only for now; ships ahead of
  i18n by ratified decision 2026-07-19) and a security-policy affordance
  linking `https://github.com/cuesoftinc/<product>/blob/main/SECURITY.md`
  — both styled per product design but present everywhere.
- **Marketing nav** (same composition everywhere, [Revised 2026-07-19]):
  4 text links — Features · product slot (same slot as the footer) · Docs
  (GitBook root) · GitHub, where the GitHub item renders as a compact
  **star badge** — fleet construction [Reconciled 2026-07-20]:
  GitHubMark(14) + star glyph(12) + "Star" label + live count fetched
  client-side from the repo's `stargazers_count`, cached; TEST_MODE or
  fetch failure → neutral "Star" with no number — counts are NEVER
  hardcoded, and Figma canvases show the neutral badge) — plus the ThemeToggle control,
  a "Sign in" **text link**, and the "Try Cloud" **primary CTA**
  (`/signin`). **Mobile**: below `md` the bar keeps the **Try Cloud
  primary CTA visible beside the hamburger** (user-ratified 2026-07-19
  from upstat's treatment — the conversion CTA never hides); the text
  links collapse into a menu-button disclosure (hamburger,
  `aria-expanded`) opening a panel with the same 4 links + ThemeToggle +
  Sign in; no canonical link may be unreachable at any viewport
  (ratified 2026-07-19 from review finding).
- **Theme toggle everywhere** — every product ships theme switching
  on the marketing nav AND the dashboard chrome (rail/top bar) and in
  settings. Contract = apparule's `src/design/ThemeProvider.tsx`
  replicated: `data-theme` on `<html>`, persisted at localStorage key
  `<product>.theme`, falling back to the product's design default.
  **[Revised 2026-07-20]** the contract is TRI-STATE: light | dark |
  system — system tracks `prefers-color-scheme` live (matchMedia
  listener; pre-paint init script covers it, no FOUC); the nav toggle
  cycles the three with distinct icons (sun/moon/monitor); settings
  offers a three-way control. **Key ABSENT = the product's design
  default** (apparule light · expendit dark · upstat dark) — the
  designed first impression is deterministic; "system" is an EXPLICIT
  choice stored like any preference (never modeled as key-absent).
  CI runs default to colorScheme light — specs asserting boot themes
  rely on this contract, not the runner's OS. Embedded surfaces with their own theming
  (e.g. the Scalar /docs/api reference) sync to the RESOLVED theme and
  hide their native toggles.
- **Links are real** — every external href must return HTTP 200
  (`curl -sIL`) when introduced; Playwright asserts the canonical hrefs
  on the marketing nav/footer and the theme toggle on both surfaces, so
  drift fails CI. Figma footer/nav masters carry the same inventory.
  This includes URLs inside seed/mock data and defaults that render as
  clickable links (EmptyState docsHref, demo runbook/monitor targets):
  invented hostnames like `docs.<product>.cuesoft.io` are placeholders
  that ship 404s — point them at the real GitBook pages (found live
  2026-07-19 as a dead "Self-host docs" link).
