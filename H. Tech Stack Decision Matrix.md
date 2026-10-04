# H. Tech Stack Decision Matrix

**Рамка решения:** West Consulting — content‑first B2B expert site с русским языком, формами, CRM Bitrix24 и требованием к управляемому маршруту персональных данных. Окончательная privacy‑оценка требует российского профильного юриста.

**Шкала:** Высокая / Средняя / Низкая — сравнительная оценка для описанного сценария, а не независимый бенчмарк платформ.

## 1. Матрица решений

| Критерий | Astro + CMS | Next.js + CMS | WordPress self‑hosted | Tilda | Webflow | Framer | Bitrix CMS |
|---|---|---|---|---|---|---|---|
| Качество custom design | Высокая | Высокая | Средняя–высокая | Средняя | Высокая | Высокая | Средняя–высокая |
| SEO | Высокая, static‑first | Высокая, при тех. дисциплине | Высокая, при hygiene | Средняя–высокая | Высокая | Средняя–высокая | Высокая |
| Скорость | Высокая | Высокая, но зависит от rendering/cache | Средняя–высокая | Высокая | Высокая | Высокая | Средняя |
| Блог / editorial workflow | Высокая с CMS/content collections | Высокая с CMS | Высокая | Средняя | Высокая | Средняя | Высокая |
| Российский хостинг | Высокая — self‑host | Высокая — self‑host | Высокая | Экспорт возможен, но встроенные формы требуют отдельной схемы | Низкая для managed hosting goal | Низкая для managed hosting goal | Высокая |
| Первичное хранение лидов | Высокий контроль с server endpoint | Высокий контроль с server endpoint | Высокий контроль с form/backend | Требует отдельного маршрута/настройки | Низкий control в managed default | Низкий control в managed default | Высокий control |
| Bitrix24 | Высокая через API/webhook | Высокая через API/webhook | Высокая через plugin/custom endpoint | Нативная интеграция есть | Webhook/API; проверить route | Webhook; проверить route | API/custom integration |
| Русский язык | Высокая | Высокая | Высокая | Высокая | Высокая | Высокая | Высокая |
| Стоимость запуска | Средняя | Средняя–высокая | Низкая–средняя | Низкая | Средняя | Средняя | Высокая |
| Стоимость владения | Низкая–средняя | Средняя–высокая | Средняя | Низкая–средняя | Средняя | Средняя | Средняя–высокая |
| Зависимость от подрядчика | Средняя | Высокая | Средняя | Средняя | Средняя | Средняя | Высокая |
| Владение кодом | Высокое | Высокое | Высокое | Ограниченное / export‑dependent | Ограниченное в managed model | Ограниченное в managed model | Высокое |
| Безопасность | Высокая при patching/hardening | Высокая при infra discipline | Средняя: plugin hygiene critical | Управляемая vendor‑модель + route risk | Vendor managed; data region risk | Vendor managed; data transfer risk | Высокая при admin/security discipline |
| Backup | На стороне West/hoster | На стороне West/hoster | На стороне West/hoster | Проверить export/backup process | Vendor process; verify | Vendor process; verify | На стороне West/hoster |
| Масштабирование | Высокое | Высокое, но cache/deployment complexity | Среднее | Среднее | Высокое managed | Высокое managed | Среднее–высокое |
| Поддержка форм | Custom, полный control | Custom, полный control | Mature ecosystem | Strong native forms | Strong native forms | Native/webhook forms | Mature modules/custom |
| Контентная команда / редактура | Средняя–высокая, зависит от CMS | Средняя–высокая, зависит от CMS | Высокая | Высокая | Высокая | Средняя | Высокая |
| Миграция домена / portability | Высокая | Высокая | Высокая | Средняя | Средняя | Средняя | Высокая |
| Риски ПДн и внешних сервисов | Контролируемы, но legal/ops responsibility на West | Контролируемы, но legal/ops responsibility на West | Контролируемы, но plugin/process risk | Высокая потребность проверить storage and transfers | Высокая: Webflow говорит о storage в США | Высокая: Framer раскрывает AWS и transfers outside EEA/UK | Контролируемы при self‑hosting, нужен legal review |
| Необходимость юридической проверки | Да | Да | Да | **Да, повышенная** | **Да, повышенная** | **Да, повышенная** | Да |

## 2. Факты, которые определяют решение

- **ФАКТ.** Astro документирует deployment на многих host‑провайдерах, static build в `dist` и адаптеры для on‑demand rendering. [1]
- **ФАКТ.** Next.js поддерживает self‑hosting на Node.js, Docker или static export; для self‑hosted сервера рекомендует reverse proxy. При сложном/multi‑instance deployment нужно управлять cache, deployment/version skew и ключами Server Functions. [2]
- **ФАКТ.** WordPress для рекомендуемой конфигурации требует PHP 8.3+, MariaDB 10.11+ или MySQL 8.0+ и HTTPS; рекомендуются Apache/Nginx. [3]
- **ФАКТ.** Tilda документирует интеграцию форм с Bitrix24; по умолчанию Tilda хранит captured data в разделе Leads в течение месяца, с настройкой срока. [4] [5]
- **ФАКТ.** Webflow пишет, что хранит данные клиентов и конечных пользователей в США и использует subprocessors; клиент остаётся controller за данные посетителя сайта. [6]
- **ФАКТ.** Framer указывает, что customer выступает controller, Framer — processor, и называет AWS своим hosting environment; его statement описывает трансферы за пределы EEA/UK. [7]
- **ФАКТ.** 1С‑Битрикс сообщает, что сайт можно размещать на любом хостинге, удовлетворяющем техтребованиям продукта, и публикует варианты shared/VPS/VM. [8]

## 3. Рекомендованные варианты

### Lean MVP recommendation — **WordPress self‑hosted на российском хостинге**

**РЕКОМЕНДАЦИЯ.** Выбрать при отсутствии постоянного technical partner и потребности быстро публиковать блог/страницы собственными силами.

- Контент: один лёгкий theme/build, ограниченный перечень поддерживаемых плагинов.
- Форма: custom server‑side integration → Bitrix24; не отправлять данные одновременно во множество сторонних сервисов.
- Required ops: ежемесячные updates, backup/restore test, least‑privilege admin, WAF/rate‑limit, vulnerability and plugin register.
- Почему не «самый дешёвый навсегда»: безопасность и editor workflow требуют владельца процесса.

### Balanced professional site — **Astro + лёгкий CMS/editorial layer на российском хостинге**

**РЕКОМЕНДАЦИЯ.** Предпочтительный вариант, если West готов обеспечить разовую качественную разработку и понятный support‑owner.

- Static‑first pages; dynamic work только для защищённого endpoint формы.
- Content collections/CMS позволяют иметь versioned content и аккуратный Markdown workflow.
- Формы: endpoint в российском контуре → Bitrix24, email/Telegram notifications без sensitive text.
- Преимущество: performance, SEO‑контроль, low runtime surface, дизайн без platform lock‑in.
- Ограничение: нужен developer для changes beyond editor scope.

### Premium custom build — **Next.js + CMS + российская инфраструктура**

**РЕКОМЕНДАЦИЯ.** Только если будущий сайт становится сложным digital product: gated content, personalised flows, сложная integration layer, много ролей/инструментов.

- Нужны: Docker/Node ops, reverse proxy, build/deploy, cache strategy, security monitoring, backup/runbook.
- Не выбирать просто ради «premium». Для content‑first v1 Astro обычно достаточнее и операционно проще.

## 4. Почему не managed builders как default

**РЕКОМЕНДАЦИЯ.** Webflow и Framer не выбирать default‑вариантом для lead form, пока российский юрист не подтвердит legal data route и применимые трансграничные механизмы. Tilda может быть быстрым маркетинговым MVP, но только с отдельно спроектированным route форм и правовой проверкой Tilda Leads, Bitrix24, аналитики и consent.

## 5. Не делать до выбора стека

1. Не переносить форму «как есть» между платформами без data‑flow map.
2. Не хранить submissions в Google Sheets/личной почте «на всякий случай».
3. Не использовать captcha/analytics/chat‑widgets до инвентаризации processors и legal review.
4. Не считать наличие российского хостинга автоматическим соответствием всем требованиям ПДн.
5. Не публиковать бюджет разработки как факт: доказательной базы о российском scope‑comparable pricing не собиралось.

## References

[1]: https://docs.astro.build/en/guides/deploy/ "Astro — Deploy your Astro Site"
[2]: https://nextjs.org/docs/app/guides/self-hosting "Next.js — How to self-host your Next.js application"
[3]: https://wordpress.org/about/requirements/ "WordPress — Requirements"
[4]: https://help.tilda.cc/forms/bitrix "Tilda — How to Connect Data Collection Forms to Bitrix24"
[5]: https://help.tilda.cc/forms "Tilda — Data Capture Forms"
[6]: https://webflow.com/legal/privacy-faqs "Webflow — Privacy FAQs"
[7]: https://www.framer.com/legal/privacy-statement "Framer — Privacy Statement"
[8]: https://www.1c-bitrix.ru/products/cms/hosting.php "1С‑Битрикс — Хостинг для продуктов"
