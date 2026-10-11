## Target sitemap and route mapping — Stage 0

## Public/client route model

The current repository uses flat HTML paths. The target information architecture from the original TЗ is expressed below as logical routes; the physical implementation must be chosen after the source-of-truth decision.

```text
/
├── /about
├── /approach
├── /services
│   ├── /services/financial-diagnostic
│   ├── /services/finance-under-control
│   ├── /services/external-cfo
│   └── /services/finance-automation
├── /partners
├── /scenarios
│   ├── /scenarios/cash-visibility
│   ├── /scenarios/profitability
│   ├── /scenarios/scaling-control
│   └── /scenarios/automation-readiness
├── /insights
│   └── /insights/[slug]
├── /glossary (phase 2 if content capacity is insufficient)
├── /cash-risk-check
├── /contact
├── /calculator
├── /privacy
├── /personal-data-consent
├── /cookies
├── /requisites-and-terms
├── /404
├── /sitemap.xml
└── /robots.txt
```

## Current-to-target mapping

| Current physical path | Target logical route | Action |
|---|---|---|
| `west_consulting_homepage_prototype.html` | `/` | Canonical homepage candidate; current physical file name retained for preview |
| `west_consulting_site/index.html` | service-only route index | Keep, clearly marked and out of client navigation |
| `pages/about.html` | `/about` | Recompose as personal/approach family |
| `pages/approach.html` | `/approach` | Recompose with hybrid internal concept and five TЗ stages |
| `pages/services.html` | `/services` | Rebuild hub from situation entry and four formats |
| `pages/financial-diagnostic.html` | `/services/financial-diagnostic` | Canonical diagnostic candidate |
| root `west_consulting_financial_diagnostic.html` | compatibility alias | Redirect/align only after decision |
| `pages/finance-under-control.html` | `/services/finance-under-control` | Recompose reports → rules → roles → calendar → decisions |
| `pages/external-cfo.html` | `/services/external-cfo` | Recompose preparation → discussion → decision → action → review |
| `pages/finance-automation.html` | `/services/finance-automation` | Recompose Client / West / Technical partner and controlled AI |
| `pages/partners.html` | `/partners` | Make partner intent explicit |
| `pages/scenarios.html` | `/scenarios` | Hub with four demonstrational scenarios |
| `pages/case-client.html` | `/navigator` | Existing four-state navigator; client-facing name becomes «Навигатор финансовых ситуаций» |
| missing | `/scenarios/cash-visibility` | Add |
| missing | `/scenarios/profitability` | Add |
| missing | `/scenarios/scaling-control` | Add |
| missing | `/scenarios/automation-readiness` | Add |
| `pages/insights.html` | `/insights` | Hub with category and related routes |
| `pages/article-*.html` | `/insights/[slug]` | Keep content, add metadata/status/sources/reading-time calculation |
| missing | `/glossary` | Phase decision in original TЗ |
| `pages/cost-calculator.html` | `/calculator` | Preserve interactive numeric demo; separate public-disabled state |
| missing | `/cash-risk-check` | Add ungated 12-question self-check |
| `pages/contact.html` | `/contact` | Standardize form/demo wording and contract |
| missing | `/privacy` etc. | Add staging placeholders, legal approval required |
| missing | `/404` | Add page; real HTTP status depends on host/deployment |

## Current CTA discrepancies to resolve

- Homepage primary CTA points to root legacy diagnostic instead of a unified primary contact flow.
- Homepage scenario links do not point to detail scenario pages.
- Some service cards point to `#contact` instead of service details.
- Generator navigation and homepage navigation are not identical.
- `route index` must remain a service/developer route, not a normal customer entry.
