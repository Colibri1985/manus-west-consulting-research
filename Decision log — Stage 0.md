# Decision log — Stage 0

| ID | Topic | Evidence / conflict | Proposed decision | Status |
|---|---|---|---|---|
| D-001 | Visual direction | Final task selects «Карта решений + Перспектива»; concept images are available | Use hybrid as art direction, not raster UI | Fixed by owner; implement after Stage 1 approval |
| D-002 | Practice positioning | Final task says CFO is core; AI is controlled supporting capability | Show financial management and decisions as primary; AI/digital as supporting branches | Fixed |
| D-003 | Calculator | Current demo formula exists; original TЗ and final task prohibit unapproved public prices but require preserving calculator | Preserve numerical demo in preview with prominent disclaimer and public-disabled state; move formula to one config | Fixed requirement; public pricing blocked |
| D-004 | Navigator | Current `case-client.html` is a four-state synthetic navigator | Rename client-facing module «Навигатор финансовых ситуаций»; retain four states and add scenario detail links | Fixed requirement |
| D-005 | Source of truth | `build_pages.py` differs from current HTML and can overwrite or omit later changes | Do not run generator until source-of-truth is selected; proposal: one content/build layer and generated output only | Needs owner decision before Stage 3 |
| D-006 | Stack | Current project has no package config and is static HTML/CSS/JS; TЗ suggests Astro with WordPress alternative | Do not migrate automatically. Stage 1 can use current static preview; decide before foundation implementation | Needs owner decision before Stage 3 |
| D-007 | Diagnostic duplicate | Root legacy page and internal page both exist | Proposal: canonical internal service route; root path becomes compatibility alias/redirect after verification | Needs owner decision |
| D-008 | Cash & Finance Review | Original TЗ references it for S1, but current services do not have an approved standalone scope | Do not create a new commercial service silently; keep as scenario recommendation or request owner scope | Needs owner decision |
| D-009 | Legal pages | Required routes exist in TЗ but no approved legal text | Add staging placeholders only; production blocked | Blocked external/legal approval |
| D-010 | Form route | Current forms are local demo only; no CRM/server architecture approved | Keep safe demo adapter; do not connect CRM/email/analytics | Blocked owner/architecture approval |
| D-011 | Site URL/canonical | TЗ uses `https://example.ru` as placeholder; no production domain approved | Use staging-safe noindex/canonical-disabled configuration; do not invent domain | Blocked owner input |
| D-012 | Route index | Current route index is useful for preview but not client navigation | Preserve and clearly label as service/developer route | Fixed requirement |
| D-013 | Founder content | Real photo/contact confirmed; biography and credentials are not fully evidenced in snapshot | Use approved name/photo/role/contact only; missing biography remains placeholder/blocker | Partially blocked |
| D-014 | Case evidence | No approved client cases/results | Use demonstrational scenarios only; no case claims | Fixed |
