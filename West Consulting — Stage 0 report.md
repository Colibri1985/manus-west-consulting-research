# West Consulting — Stage 0 report

**Статус:** подготовлено локально; GitHub repository не изменён.  
**Дата проверки:** 11 октября 2026 г.  
**Repository:** `Colibri1985/west-consulting-site`  
**Base snapshot:** `051a7b08498e5a0dd6be71a176a206c107bd95f1`

## Целостность контекста

- Части 1–5 единого финального задания получены.
- Исходное ТЗ доступно в `docs/ТЗ_сайт_West_Consulting_CFO_Advisory.md`.
- Hybrid homepage reference доступен локально: `west_consulting_hybrid_homepage_concept.png`.
- Hybrid internal reference доступен локально: `west_consulting_hybrid_internal_concept.png`.
- GitHub repository доступен через GitHub integration.
- Repository остаётся **private**.
- `master` не изменялся на Stage 0.

## Проверенное состояние

```text
Remote HEAD: 051a7b08498e5a0dd6be71a176a206c107bd95f1
Commit: Snapshot of current prototype before independent audit
Parents: 0
Branch: master
Diff from base snapshot: none
Working tree after read-only clone: clean
```

## Фактическая архитектура

Текущая версия — статический пакет HTML/CSS/JS:

- отдельная inline-styled homepage `west_consulting_homepage_prototype.html`;
- отдельная legacy diagnostic page `west_consulting_financial_diagnostic.html`;
- многостраничный каталог `west_consulting_site/pages/`;
- общий `west_consulting_site/assets/site.css` и `site.js`;
- `build_pages.py`, который генерирует часть внутренних страниц;
- package manager, Astro/WordPress config и lockfiles отсутствуют;
- CRM, server endpoint, analytics, CMS, production host и domain отсутствуют.

Это закрывает preview-потребности, но не закрывает production-требование исходного ТЗ о CMS/content layer, server-side validation, CRM/test adapter, SEO infrastructure и deployment contract.

## Существующие полезные функции

- четыре клиентские ситуации на homepage;
- четыре основных формата услуг;
- founder trust block, фото и подтверждённые контакты;
- финансовая диагностика;
- калькулятор с демонстрационной числовой логикой;
- интерактивный synthetic case navigator;
- demo forms without external submission;
- multi-page prototype и route index;
- `prefers-reduced-motion` правило в общем CSS.

## Главные подтверждённые расхождения

1. Homepage использует inline CSS и не подключает общий `site.css`, поэтому founder block и поздние shared components не являются единым источником стилей.
2. Mobile menu script только toggles `.is-open`; в общем CSS `.nav-links` на mobile имеет `display:none` без правила показа `.is-open`; aria-expanded/aria-controls/focus management отсутствуют.
3. Homepage scenario links ведут на `#contact`, `#approach` или общий CTA, а не на четыре отдельные scenario detail pages.
4. Homepage services contain links to the legacy diagnostic and generic contact anchors; several cards do not lead to corresponding detail pages.
5. Homepage has `id="insights"` on the trust block; a real latest-materials section is absent on homepage.
6. `build_pages.py` contains a competing generated source with a different navigation, hero, content and routes; it points to `../west_consulting_homepage_prototype.html`, while the generated pages are nested under `west_consulting_site/pages/` and the broader site has later manual changes.
7. Two diagnostic documents exist: `west_consulting_financial_diagnostic.html` and `west_consulting_site/pages/financial-diagnostic.html`.
8. Current `site.js` demo success state says only that a local success state is shown; it does not implement the final required wording, unified form contract, no-JS fallback or error states.
9. Current forms do not yet demonstrate the complete TЗ contract: stable names, unified scenario/intent allowlist, channel-aware contact validation, explicit length limits and production consent versioning.
10. Required target routes are missing as actual pages: four scenario details, `/cash-risk-check`, legal routes, `/404`, sitemap/robots and glossary phase route.

## Stage 0 package and deferred decisions

The separate `stage0-report.md` exists and is included in the Stage 0 package. The package is local planning material and is not a change to the GitHub repository.

The current preview stack is explicitly recorded as **static HTML/CSS/JS**. The long-term stack, source of truth and production integrations are **not yet approved**. They must be agreed before Stage 3 implementation, but they do not block Stage 1 mockups. Until that decision, Stage 1 uses an isolated preview-only mockup workspace and does not migrate the stack, connect CRM/analytics/forms or change `master`.

## Stage 0 conclusion

Proceeding directly to mass implementation would risk mixing source-of-truth repair, visual redesign, new route creation and production architecture. Stage 1 should start only after owner confirms the plan below and any blocking decisions. No site code or Git history has been changed in Stage 0.
