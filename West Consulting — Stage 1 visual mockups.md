# West Consulting — Stage 1 visual mockups

Это изолированный preview-пакет Stage 1. Он не является изменением сайта, не заменяет approval макетов и не подключён к GitHub, CRM, аналитике, email или production.

## Что подготовлено

Отдельные responsive-макеты для пяти страниц:

| Страница | Desktop | Mobile | Source |
|---|---|---|---|
| Главная | `screenshots/desktop/stage1-home.png` | `screenshots/mobile/stage1-home.png` | `pages/stage1-home.html` |
| Финансовая диагностика | `screenshots/desktop/stage1-diagnostic.png` | `screenshots/mobile/stage1-diagnostic.png` | `pages/stage1-diagnostic.html` |
| Внешний CFO | `screenshots/desktop/stage1-external-cfo.png` | `screenshots/mobile/stage1-external-cfo.png` | `pages/stage1-external-cfo.html` |
| Контакты | `screenshots/desktop/stage1-contact.png` | `screenshots/mobile/stage1-contact.png` | `pages/stage1-contact.html` |
| Калькулятор диагностики | `screenshots/desktop/stage1-calculator.png` | `screenshots/mobile/stage1-calculator.png` | `pages/stage1-calculator.html` |

Служебная карта макетов находится в `pages/stage1-route-index.html`. Корневой `index.html` ведёт на неё.

## Полный состав блоков

### Главная

Hero с Андреем Муллером и descriptor личной CFO Advisory practice; рабочий headline «Видеть систему. Принимать сильные решения.»; рабочий подзаголовок о прибыли, денежном потоке, финансовом управлении, цифровых инструментах и AI; два CTA; статичная карта `финансовая картина → данные и правила → роли и процессы → AI — если уместно → следующий шаг`; четыре ситуации; reframe-блок; четыре этапа подхода; founder block с реальным фото, контактами и границами ответственности; четыре формата услуг; controlled digital/AI layer; финальный CTA и footer.

### Финансовая диагностика

Breadcrumbs; компактный hybrid hero; демонстрационная маркировка; CTA применимости; horizon visual; главный вопрос собственника; читаемый рабочий документ «Карта решения»; блоки «Кому подходит», «Что разбираем», «Что может измениться», «Когда не подходит»; четыре этапа работы; disclaimer demo-формата; FAQ; CTA; переход к калькулятору.

### Внешний CFO

Breadcrumbs; hero с ролью и границами; CTA fit; horizon visual; четырёхэтапный cadence `подготовка → обсуждение → решение → review`; блоки подходящих условий и ограничений; FAQ; CTA без обещания full-time replacement или безлимитной доступности.

### Контакты

Breadcrumbs; hero с объяснением qualification; инструкция, что описать; предупреждение о чувствительных материалах; реальные телефон и email; demo-form с name, company/industry, role, preferred channel, contact, scenario, description, consent; длина полей и labels; кнопка «Проверить форму»; текст о том, что данные не отправляются и обращение не создаётся.

### Калькулятор

Preview/Demo hero; заметный disclaimer; числовой инструмент с параметрами сложности вопроса, количества контуров, workshop и приоритетности; initial state; changed state; demo-result `75 000 ₽`; public-disabled state; объяснение, что значения не являются утверждёнными тарифами; CTA «Обсудить параметры диагностики». Калькулятор не заменён анкетой и не является обязательным барьером.

## Планируемые компоненты, которые не входят в первые пять макетов

- **Approach:** hybrid internal concept, five stages, question → indicators → rules → responsibility → next step, examples, boundaries and FAQ. Entry from homepage `#approach` and main navigation.
- **Services hub:** entry from situation, four formats, one-off/project/recurring comparison. Entry from header and service cards.
- **Finance under control:** reports → rules → roles → calendar → decisions. Entry from services hub and S3 scenario.
- **Finance automation:** Client / West / Technical partner, AS-IS/TO-BE, requirements, Fit-Gap, RACI, UAT and controlled AI. Entry from services hub and S4 scenario.
- **Partners:** roles, scope, boundaries and `intent=partner` entry. Entry from footer and relevant automation content.
- **Scenarios hub and four detail pages:** cash visibility, profitability, scaling control, automation readiness. Entry from homepage situation rows and navigator.
- **Navigator:** current four-state interactive navigator renamed «Навигатор финансовых ситуаций». Entry from scenarios hub and selected scenario routes.
- **Cash Risk Check:** ungated 12-question self-check without forced contact or diagnosis. Entry from insights and cash-related scenario/article.
- **Insights/articles:** category, approved status, reading time based on text, sources, related scenario/service and one CTA. Entry from header/footer and contextual cards.
- **Legal routes:** privacy, personal-data-consent, cookies and requisites-and-terms with staging placeholders until approval. Entry from footer.
- **404:** clear message and links to home, services and contact; real HTTP status remains deployment-dependent.
- **Route index:** service-only map for review, kept out of ordinary client navigation.

## CTA маршруты в Stage 1

- Hero primary: `stage1-contact.html#request` — единый первичный контакт.
- Hero secondary: `#situations` — выбор ситуации.
- Situation cards: переходят к релевантному detail/mockup входу, а не к безымянному нижнему CTA.
- Service cards: ведут к соответствующему формату/mockup.
- Diagnostic CTA: контакт применимости и отдельный calculator route.
- External CFO CTA: проверка fit через контакт.
- Calculator CTA: `stage1-contact.html#request`, без передачи параметров в URL.
- Email и телефон: явные альтернативы в founder/contact/footer blocks.

## Что требует approval

### Визуальная система

Нужно подтвердить или скорректировать: тёмный navy hero; ivory/stone content surfaces; copper accents; serif/sans pairing; spatial horizon; static decision map; плотность линий и узлов; состав верхней навигации; раннее размещение founder block.

### Тексты

Headline и подзаголовок главной являются рабочими текстами для approval, а не автоматически утверждённой production-копией. Также требуют проверки формулировки descriptor, service descriptions, qualification language и текстов о controlled AI.

### Коммерческие и юридические границы

Числа калькулятора — только демонстрационные. Для production необходимы утверждённые тарифы и формула. Demo-form не отправляет и не сохраняет данные. Legal routes, consent text, privacy, cookies, requisites and terms пока не реализованы как финальные юридические документы.

### Архитектура

Стек, source of truth и production-интеграции согласуются до Stage 3. Stage 1 подготовлен как изолированный статический preview и не блокируется этими решениями.

## Проверка

- Сгенерировано 6 HTML-файлов: 5 mockup pages и 1 route index.
- Сгенерировано 10 screenshots: 5 desktop и 5 mobile.
- Использованы реальные контакты и настоящее фото Андрея Муллера.
- Внешних запросов, CRM, analytics и form submission нет.
- `master` и рабочая ветка сайта не изменялись.

## После передачи

Работа останавливается на Stage 1. Следующий шаг — отдельное визуальное approval или список правок к этим макетам. Без такого approval переход к Stage 2/3 и массовой реализации не выполняется.
