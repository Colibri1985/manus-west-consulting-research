# D. GTM Experiment System

**Статус:** система принятия решений, а не прогноз воронки. Все перечисленные тесты — **ГИПОТЕЗЫ** до появления повторяемых наблюдений в CRM.

## 1. Operating principle

**РЕКОМЕНДАЦИЯ.** В каждый момент держать не более двух активных acquisition‑тестов плюс site/content foundation. Solo practice не должна одновременно запускать referral campaign, партнёрский outreach, SEO, Директ, Telegram‑посевы и вебинары: это скрывает причинность и перегружает delivery capacity.

### Уровни доказательности

| Уровень | Определение | Что разрешено делать |
|---|---|---|
| Гипотеза | Есть логичное предположение и desk evidence, но нет повторяемого поведения целевых клиентов. | Малый эксперимент, вручную фиксировать исход. |
| Первая проверка | Есть несколько корректных действий целевой аудитории, но нет повторяемости/сравнения. | Уточнить message, scope, entry offer. |
| Подтверждённый паттерн | Один и тот же сегмент + trigger + канал дают повторяемые качественные действия и проходят capacity/quality gate. | Стандартизировать playbook и осторожно масштабировать. |

## 2. Реестр GTM‑гипотез

| ID | Гипотеза | Сегмент / trigger | Канал | Entry offer / артефакт | Signal подтверждения | Decision rule | CRM data | Capacity gate |
|---|---|---|---|---|---|---|---|---|
| G01 | Problem‑first формулировка «прибыль есть, а денег нет» вызывает более точные интро, чем «ищу клиентов на CFO». | Owners проектного/торгового МСБ; cash ambiguity. | Тёплая сеть. | Referral one‑liner + scenario card. | Интро содержит конкретную ситуацию и owner‑sponsor. | Продолжить, если интро проходят qualification; изменить язык, если идут generic «посоветоваться». | Source person, phrase used, trigger, sponsor, fit. | Не назначать больше N квалификационных call в неделю — N задаётся фактической capacity. |
| G02 | Платный Cash & Finance Review лучше фильтрует intent, чем бесплатная содержательная консультация. | Owner с локальным cash/visibility issue. | Website + referrals. | One‑page paid review with output/exclusions. | Клиент соглашается на scope и даёт минимальные данные. | Продолжить при paid commitment; если все ожидают free audit — пересобрать scope/trust, а не снижать цену автоматически. | Offer version, objection, next step, outcome, reason lost. | Одновременно не более согласованного числа reviews; reserve delivery time. |
| G03 | Для комплексной проблемы Financial Diagnostic понятнее, чем Cash Review. | Несколько юрлиц/направлений, отчёты/роли/automation issue. | Warm + site service page. | Diagnostic scope card. | Sponsor выбирает diagnostic после qualification. | Перевести в core project только при owner/data readiness; stop при отсутствующем sponsor. | Complexity flags, data readiness, buyer committee, selected entry. | Не брать diagnostic без date‑bound client inputs. |
| G04 | Интегратору полезен West как owner‑side методолог/UAT, а не как ещё один внедренец. | 1С/БИТ.ФИНАНС/BI partner; unclear requirements. | Partner motion. | Partner one‑pager + joint case discussion. | Partner предлагает совместный discovery или scope exercise. | Continue if RACI and non‑compete role accepted; stop on price‑shopping or exclusivity pressure. | Partner type, lead profile, RACI, feedback, next action. | Один live partner pilot одновременно до repeatable handoff. |
| G05 | Страница «Не автоматизируйте хаос» помогает собрать более готовый automation lead. | Owner/CFO before 1С/BI. | Website / partner link. | Checklist + Automation Advisory page. | Lead identifies target system and agrees to requirements readiness step. | Keep if leads have sponsor/data/process; revise if traffic is only developer job/cheap implementation intent. | Query/page, planned system, maturity, owner, urgency. | No proposal for implementation; West capacity covers discovery only. |
| G06 | Telegram — useful to test pain language and nurture, not to prove demand by subscribers. | Owners/partners who already know founder. | Telegram. | 6 short posts + one checklist. | Replies with contextual problem, partner intro, or saved/forwarded content leading to conversation. | Continue topic if it assists quality conversations; stop posts that create reach but no relevant action over review window. | Post ID, topic, qualitative response, assisted touch. | Max one useful post/week until delivery cadence stable. |
| G07 | SEO problem pages can create high‑intent inbound over time. | Searchers with finance problem. | Organic search. | Pillar + service + scenario internal cluster. | Search query aligns with ICP and lead reaches service page before SQL. | Build next cluster only when indexation/intent and conversion evidence are visible; do not infer from traffic alone. | Landing page, query class, first/last/assisted touch, qualification outcome. | Content production must not replace client delivery. |
| G08 | Paid search/Telegram seeding is premature before message and qualification rules work. | High‑intent audience after validated ICP. | Директ / paid distribution. | One narrow landing page to paid entry. | Qualified request with source tracking; no dependence on vanity clicks. | Start only after prerequisites; pause if quality or capacity fails. | Cost, source, term/creative, MQL/SQL/paid entry, lost reason. | Hard weekly lead cap; pause ads when slots filled. |

## 3. Обязательные GTM‑треки

### 3.1. Тёплая сеть и рекомендации

**Цель:** проверить язык боли и получить первые качественные discovery conversations.  
**Не считать:** гарантированным каналом продаж.

- **Артефакты:** one‑liner, three scenario cards, fit/no‑fit referral guide.
- **Проверять:** какие описания ситуации приводят к корректным интро; кто реально выступает referral source; какие triggers повторяются.
- **Stop rule:** прекращать broad outreach, если интро стабильно не имеют owner‑sponsor, конкретной проблемы или ожидания paid step.

### 3.2. Partner GTM

**Цель:** получить сложные, квалифицированные ситуации, где West дополняет delivery партнёра.

- Фокус первого круга: 1С/БИТ.ФИНАНС, BI/CRM, бухгалтерские бюро.
- Financial SaaS — только после отдельной проверки co‑sell fit.
- **Do not do:** объявлять «партнёрство» без real work, использовать чужой логотип или договариваться об эксклюзивности до pilot.

### 3.3. Website + content

**Цель:** trust layer, terminology test и долгосрочный inbound asset.

- Проверять темы, ведущие к содержательным обращениям.
- Отмечать service pages, просмотренные до SQL.
- Разделять прямой и assisted contribution.

### 3.4. SEO

**Цель:** захватывать problem‑intent; не обещать быстрый pipeline или фиксированный traffic.

- Сначала: 3 problem clusters + 3 service pages + 1 partner scenario.
- Затем: расширять только по query/lead evidence.

### 3.5. Telegram и TenChat

**Цель:** personal visibility, nurture, partner conversations и language test.

- Не использовать число подписчиков как proxy спроса.
- Не публиковать клиентские детали, расчёты или непроверенные claims.

### 3.6. Контекстная реклама и посевы

**Статус:** поздний, ограниченный test. Предусловия: подтверждённый ICP, понятный paid entry, service page, CRM source tracking, consent/privacy layer, capacity gate и владелец follow‑up.

## 4. План на 90 дней

| Период | Решение / артефакт | Тест | Decision gate |
|---|---|---|---|
| Недели 1–2 | Qualification script, review/diagnostic cards, proposal skeleton, refusal/referral rules. | Internal readiness. | Нельзя начинать acquisition без scope/exclusions/CRM fields. |
| Недели 3–4 | Core website pages и one‑pager для партнёра. | G01 и G02 на тёплой сети. | Проверить, корректны ли problem phrasing и entry choice. |
| Недели 5–6 | Три problem‑led материала, Cash Risk Check. | G06; контент как language test. | Качество диалогов важнее охвата. |
| Недели 7–8 | До двух exploratory partner conversations на тип партнёра — только после отдельной деловой готовности. | G04. | RACI / non‑compete / target lead согласуемы или нет. |
| Недели 9–10 | Automation scenario page + checklist. | G05. | Есть ли requests с owner/data readiness. |
| Недели 11–12 | CRM review и offer/version review. | Compare G01–G06 evidence. | Choose one ICP + one entry + one primary motion for next cycle. |

## 5. План на шесть месяцев

| Месяцы | Фокус | Решение, которое требуется принять |
|---|---|---|
| 1–2 | Foundation и qualitative learning. | Какие words / triggers приводят к qualified conversation. |
| 3 | One entry offer and one partner role. | Cash Review, Diagnostic или partner‑led automation — где есть evidence. |
| 4 | Standardize successful follow‑up and proof assets. | Какие deliverables/FAQ safe to make public. |
| 5 | SEO cluster expansion and one constrained partner pilot. | Есть ли repeatable partner handoff. |
| 6 | Review retention, capacity and evidence. | Нужен ли support partner/финменеджер или надо сузить scope. |

## 6. Что не запускать до validation

1. Broad Яндекс.Директ.
2. Telegram‑посевы с лид‑формой.
3. «Бесплатный полный финансовый аудит».
4. Unbounded chat/WhatsApp support.
5. Публичный прайс full CFO retainer без WTP и capacity evidence.
6. Формальные партнёрские badges/logos.
7. AI‑услугу как самостоятельный flagship.
8. Массовый content calendar без измеримой гипотезы.

## 7. Реестр метрик без выдуманных целевых значений

| Уровень | Метрики | Не использовать как единственный KPI |
|---|---|---|
| Demand quality | Fit, trigger, sponsor presence, data readiness, urgency, complexity. | Pageviews, likes, subscribers. |
| Funnel | New lead → contacted → qualified → MQL → SQL → paid entry → project/retainer. | Общее число заявок. |
| Offer | Paid‑entry request/acceptance, scope change, objection, outcome. | «Интерес к услуге» без commitment. |
| Channel | Referral source, partner intro, source/medium/campaign, first/last/assisted touch. | Последний клик как единственная attribution. |
| Economics | Senior capacity used, unpaid time, gross delivery hours, partner cost. | Выручка без delivery load. |
| Trust/content | Material assisted SQL, repeat visits from target company, reply quality. | Reach/repost. |
| Partner | Joint discovery, RACI acceptance, repeat intro, handoff quality. | Число подписанных «партнёрств». |

## 8. Founder Dashboard

**РЕКОМЕНДАЦИЯ.** Еженедельно — один экран, не более 15 строк.

| Блок | Показывать |
|---|---|
| Demand | New leads by source; qualified share; top three triggers. |
| Pipeline | Count/value/status by stage; next action and owner; aging. |
| Offers | Entry format selected; objections; lost reason. |
| Capacity | Booked senior hours/days; unpaid discovery; next two weeks availability. |
| Partners | New intro, active pilot, RACI issue, next action. |
| Content | Asset published; assisted conversations; learning statement. |
| Risk | Privacy/data issue; scope creep; no sponsor; delivery dependency. |
| Decision | One thing to continue, change, stop next week. |
