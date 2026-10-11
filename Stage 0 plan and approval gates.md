# Stage 0 plan and approval gates

## Proposed execution stages

### Stage 0 — input, state and decisions (current)

- confirm repository and base snapshot;
- inspect current source and documented functions;
- map requirements and routes;
- record remediation evidence and decisions;
- identify blockers without changing code.

**Output:** this Stage 0 package.  
**Repository action:** none.

### Stage 1 — first design set

Prepare separate desktop/mobile mockups or a clickable static prototype for:

1. homepage;
2. financial diagnostic;
3. external CFO;
4. contacts;
5. diagnostic calculator, including initial, changed, demo result and public-disabled states.

Stop after these mockups and request visual-system approval.

### Stage 2 — remaining layout/content outlines

Define approach, services hub, finance-under-control, finance automation, partners, scenarios hub, four scenario details, about, insights/articles, navigator, Cash Risk Check, legal placeholders and 404.

### Stage 3 — implementation

- create a working branch from `master`;
- choose one source of truth;
- introduce shared tokens/components/content/routes/build;
- remediate current code findings;
- preserve calculator, navigator, founder block, contacts, demo forms and route index;
- use logical commits; no merge.

### Stage 4 — tests

Automated: routes, local links/assets, anchors, duplicate IDs, labels, metadata, required pages, reproducible build, calculator boundaries, allowlisted intent/scenario, secret scan.

Manual/browser: desktop/mobile menu, CTA routes, keyboard, forms with and without JS, calculator, navigator, Cash Risk Check, responsive layouts, console errors, images and reduced motion.

### Stage 5 — audit handoff

Prepare branch, SHA, PR without merge, changed-files list, screenshots, route map, design system, matrices, remediation report, decision log, blockers, README, tests and unfinished items.

## Decisions that block the next stage

The following are not silently assumed:

1. **Stage 1 visual approval:** the hybrid direction is selected, but the first five page mockups still require owner approval before mass implementation.
2. **Source of truth / architecture:** current code is static HTML/CSS/JS with a drifting Python generator. Owner must approve whether to keep a static build with a new content/build layer, migrate to Astro, or use WordPress. No migration is performed automatically.
3. **Public pricing model:** demo calculator formula remains in preview; public numerical pricing is blocked until formula, coefficients, scope and terms are approved.
4. **Legal content:** privacy, consent, cookies and requisites remain placeholders until owner/legal approval.
5. **Production data route:** CRM, email, analytics and server-side form delivery require separate approval and credentials; none will be connected during design/remediation by default.
6. **Canonical diagnostic path:** choose the internal diagnostic page as canonical and decide whether the root legacy path is redirected or retained as a compatibility alias.
7. **Public content claims:** approve production copy, founder biography, article authorship/status, partner claims and any future case evidence.

## Explicitly not blocking Stage 1

- real CRM access;
- analytics;
- production domain/hosting;
- legal final text;
- public pricing;
- production deployment.

These are blockers for production, not for preparing mockups and a preview-only implementation.
