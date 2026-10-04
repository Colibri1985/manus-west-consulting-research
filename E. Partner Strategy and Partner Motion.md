# E. Partner Strategy and Partner Motion

**Статус:** модель для будущих проверяемых отношений. Ни один тип партнёра ниже не означает существующее партнёрство West Consulting. Все коммерческие условия, referrals и совместные statements требуют отдельного согласования.

## 1. Партнёрский тезис West Consulting

> **РЕКОМЕНДАЦИЯ.** West Consulting подключается там, где до software/automation‑delivery нужно сформулировать финансовую задачу, принять business requirements и обеспечить owner‑side acceptance. West не продаёт себя как конкурента бухгалтерскому бюро, интегратору, BI‑команде или SaaS‑вендору.

## 2. Partner fit matrix

| Тип партнёра | Job to be done партнёра | Что West решает для него | Что получает партнёр | Граница / non‑competition | Подходящие лиды | Неподходящие лиды | Первый совместный формат | Риски | Continue / stop criterion |
|---|---|---|---|---|---|---|---|---|---|
| 1С / БИТ.ФИНАНС‑интегратор | Delivery без scope creep, согласованные требования и acceptance. | AS‑IS/TO‑BE finance model, финансовые классификаторы, requirements, RACI, UAT/business acceptance. | Более чёткий заказчик, меньше переделок, прозрачные решения по business priorities. | Партнёр отвечает за software/config/integration; West не пишет код и не продаёт лицензии. | Несколько юрлиц/ЦФО, бюджетирование, казначейство, спор о правилах. | Клиент ждёт «установить БИТ.ФИНАНС за неделю» без sponsor/data. | Совместный discovery: 60–90 минут, раздельные роли. | Channel conflict; integrator хочет скрыть gaps; клиент путает роли. | **Continue:** RACI принят и один scoped discovery даёт ясность. **Stop:** West обязан давать бесплатное ТЗ/продавать продукт партнёра. |
| BI / CRM / data‑интегратор | Получить согласованные KPI, data rules и владельцев показателей. | Финансовые показатели, management cadence, logic план‑факт, data ownership, acceptance criteria. | Меньше dashboard rework, понятные KPI, owner for business decisions. | Интегратор строит data model/dashboards; West определяет business logic. | 1С/ERP/CRM есть, отчёты расходятся, нужен P&L/ДДС/маржа. | «Нарисуйте красивый dashboard» без решения, какие вопросы он должен отвечать. | KPI‑alignment workshop + single dashboard specification. | West ошибочно считают BI‑vendor; скрытые data quality issues. | **Continue:** client sponsor признаёт business‑owner role. **Stop:** единственный запрос — цена dashboard. |
| Бухгалтерское бюро | Сохранить клиента, когда его вопрос выходит за compliance. | Объяснить разницу между управленческим и бухгалтерским контуром; создать finance roadmap и повысить зрелость клиента. | Честный referral без обещания закрыть всё; меньше конфликтов ожиданий. | Бюро остаётся владельцем compliance; West не даёт налоговых заключений и не берёт первичку. | Бухучёт стабилен, собственник не видит P&L/ДДС/маржу. | Налоговый спор, восстановление бухучёта, кадры/первичка. | «Finance gap triage» для одного клиента после согласия клиента. | Threat perception главбуха, границы данных и NDA. | **Continue:** referral не разрушает отношения с бухгалтерией. **Stop:** роль West подменяет бухгалтерию. |
| Финансовый SaaS | Удержать/активировать клиента и обеспечить adoption. | Process readiness, role setup, finance cadence, owner decisions до/после tool. | Более готовый клиент и понятные use cases. | SaaS owns product/support; West не обещает platform implementation без scoped agreement. | Client выбирает tool, данные/процессы не готовы. | Простая self‑serve настройка; конфликт интересов с vendor’s own implementation. | Vendor‑neutral readiness session. | Co‑sell conflict, давление на recommendation одного tool. | **Continue:** neutrality и referral rules accepted. **Stop:** требуется эксклюзив/условное продвижение. |
| Банк / лизинг | Понятный finance pack и forecast для оценки заявки. | Улучшить управляемость данных и readiness, но не гарантировать финансирование. | Клиент с более структурированными материалами. | Банк/лизинг решает кредитный вопрос; West не агент и не обещает одобрение. | Компания готовит финансовый пакет/forecast. | Просьба «гарантировать кредит» или замаскировать данные. | Readiness checklist for client. | Регуляторные/репутационные риски, perception paid referral. | **Continue:** прозрачность ролей. **Stop:** referral fee/влияние на решение. |
| Юристы / M&A / оценщики | Качественная финансовая подготовка сделки/структуры. | Finance data readiness, forecast, management reporting, business‑side modelling. | Меньше gaps в финансовом блоке клиента. | Юрист/оценщик отвечает за legal/valuation opinion; West — за finance operating picture. | Сделка, реструктуризация, инвестор, но finance data fragmented. | Юридическое/налоговое заключение, valuation opinion. | Joint issue‑spotting call с клиентом. | Ответственность, confidentiality, conflicts. | **Continue:** письменные role boundaries. **Stop:** West просят подписать вывод вне компетенции. |
| AI / no‑code команда | Выбрать process with value и дать корректное ТЗ. | Use‑case selection, baseline, process owner, human oversight, adoption. | Реалистичный pilot вместо «автоматизируйте всё». | AI/RPA partner builds/operates tech; West governs business use case. | Устойчивый процесс с объёмом и исходными данными. | Нестабильная методология, нет owner/quality rule. | Process discovery + pilot charter. | Hype, privacy, automation of bad data. | **Continue:** baseline/owner/stop‑go agreed. **Stop:** нет process readiness или security approval. |

## 3. Текстовый макет partner one‑pager

# Когда подключать West Consulting

**Подключите West Consulting, если у клиента:**

- есть 1С, банк, CRM или Excel, но собственник не доверяет связке цифр;
- перед внедрением не согласованы ЦФО, статьи, правила факта, бюджеты или ответственность;
- нужен независимый finance‑взгляд со стороны клиента до выбора платформы/подрядчика;
- проект буксует из‑за неясных business requirements, спорных KPI или отсутствия владельца UAT;
- главный бухгалтер/финменеджер собирает цифры, но решения и ownership не определены.

**Что делает West Consulting:**

1. Формулирует business question и границы финансового контура.
2. Проводит ограниченный review или diagnostic.
3. Создаёт finance‑методологию, requirements, RACI и decision log.
4. Участвует в Fit‑Gap, UAT и business acceptance как представитель интересов заказчика.
5. Помогает собственнику встроить отчётность и решения в регулярный cadence.

**Что остаётся за партнёром:**

- выбор, лицензирование, настройка и разработка software;
- интеграции, data engineering, техническое тестирование и support;
- бухгалтерия, налоги, юридические заключения — у соответствующих специалистов.

**Как выглядит совместный discovery:**

- согласовать проблему, sponsor и доступный контекст;
- West ведёт business/finance часть; партнёр — technical feasibility;
- после встречи — отдельный документ с вариантами scope, ролями, next step;
- не обещать клиенту fixed budget/срок delivery до discovery.

**Non‑exclusive pilot:** один совместный discovery или scope exercise, без публичного использования логотипов, статусов «официальный партнёр», эксклюзивности или обязательства приводить лиды. После retrospective обе стороны решают, повторять ли модель.

## 4. 90‑дневный non‑exclusive pilot

| Этап | Цель | Обязательный артефакт | Решение |
|---|---|---|---|
| 1. Exploratory conversation | Сверить ICP, buyer trigger, services и conflict map. | One‑page notes: shared / incompatible lead types. | Перейти к одному scenario или остановить. |
| 2. Joint discovery / case discussion | Проверить language и role split на конкретном или учебном сценарии. | Problem statement, RACI draft, data boundaries. | Есть ли взаимодополняемость без бесплатной работы. |
| 3. Role matrix | Согласовать who does what before клиентского scope. | RACI: methodology, technical design, configuration, UAT, support, commercial owner. | Не брать lead без owner и acceptance path. |
| 4. Scope exercise | Выполнить один реальный paid или clearly simulated mini‑scope. | Scope, assumptions, exclusions, pricing ownership, retrospective agenda. | Реальная работа подтверждает/опровергает fit. |
| 5. Retrospective | Оценить quality, communication, scope, economics, repeatability. | Scorecard and decision memo. | Continue, redesign, or stop. |

### Pilot scorecard

| Критерий | Вопрос |
|---|---|
| Client fit | Пришёл ли owner/sponsor с решаемой проблемой? |
| Role clarity | Было ли понятно, кто отвечает за методологию, технику и acceptance? |
| Commercial transparency | Не было ли скрытого referral fee, price shopping или обещаний за другую сторону? |
| Data/privacy | Были ли согласованы NDA, доступы и минимизация данных? |
| Delivery quality | Можно ли повторить процесс без увеличения бесплатной нагрузки? |
| Repeatability | Есть ли второй очевидный тип похожего кейса? |

## 5. Правила партнёрской этики

1. Не выдавать себя за партнёра до реального совместного опыта и письменного согласования формулировки.
2. Не использовать logo, case, имя, referral или коммерческие условия без письменного согласия.
3. Не обещать заказчику скидки, сроки, функции продукта или результат партнёра.
4. Фиксировать referral origin и потенциальный conflict в CRM.
5. Не принимать или не обещать вознаграждение, которое может повлиять на vendor‑neutral recommendation клиента, без прозрачного раскрытия и проверки юристом.
6. Не передавать персональные/финансовые данные потенциальному партнёру без правового основания, согласия и согласованного безопасного канала.
