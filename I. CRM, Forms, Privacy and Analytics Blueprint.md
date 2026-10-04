# I. CRM, Forms, Privacy and Analytics Blueprint

**Цель:** минимально жизнеспособная операционная архитектура лидов без потери qualification logic и privacy discipline.  
**Правовой статус:** все положения о ПДн, consent, cookies, уведомлении оператора, хранении/передаче данных и договорах требуют проверки профильным российским юристом до запуска. Это не юридическое заключение.

## 1. Рекомендованный поток данных

```text
Посетитель сайта
  → минимальная form submission
  → server-side endpoint в согласованном контуре
  → Bitrix24 CRM: lead + source/UTM + consent version
  → email notice без чувствительного текста
  → Telegram alert: только факт/ID новой заявки
  → ручная qualification
  → protected data room/NDA только после fit
```

**ФАКТ.** Bitrix24 document forms позволяют создавать CRM‑сущности, настраивать поля/соглашения, использовать anti‑spam и передавать технические значения; Tilda документирует передачу form data в Bitrix24 и отдельно хранит submissions в Leads, если такой режим включён. [1] [2]

## 2. Lead lifecycle

| Стадия | Критерий входа | Владелец | Следующее действие | Обязательные поля | Причина выхода | Метрика качества |
|---|---|---|---|---|---|---|
| New lead | Форма/ручной referral создал запись. | CRM owner. | Проверить duplicate, consent, source и безопасный канал. | Created date, source, consent version, contact, brief situation. | Duplicate / spam / invalid contact. | % валидных источников и non‑duplicate. |
| Contacted | Отправлено первое персональное сообщение/звонок. | Founder. | Согласовать короткий qualification call. | Contact date/method, next action date. | No response / requested later. | Time to first meaningful response. |
| Qualified | Есть fit: sponsor, problem, basic scope, legal communication path. | Founder. | Решить entry: review / diagnostic / referral / decline. | Segment, trigger, sponsor, urgency, data readiness, role. | No fit / no sponsor / no readiness. | % qualified with complete qualification fields. |
| MQL | Есть problem‑fit и намерение обсудить конкретный следующий шаг. | Founder. | Send relevant scope card or schedule call. | Entry offer candidate, use case, source detail. | Nurture / disqualified. | MQL → SQL quality, not volume. |
| SQL | Buyer/sponsor обсуждает paid scope/критерии. | Founder. | Prepare scoped proposal/NDA if required. | Buying committee, decision process, budget process (if volunteered), timing. | Lost / nurture. | Proposal readiness without missing data. |
| Opportunity | Proposal или written scope отправлен. | Founder. | Follow agreed next action; protect scope. | Offer version, scope, exclusions, amount only if set, decision date. | Won / lost / paused. | Scope change count; cycle aging. |
| Paid entry product | Клиент оплатил Cash Review/Diagnostic. | Founder. | Deliver, debrief, decide next route. | Contract/SOW, inputs, deliverable date, privacy access log. | Completed → core/referral/stop. | On‑time deliverable and next decision clarity. |
| Core project | Подписан project SOW. | Founder + named client sponsor. | Milestones, RACI, change management. | Milestone, acceptance, dependencies, risk log. | Completed / paused / terminated. | Milestone acceptance and scope integrity. |
| Retainer | Recurring scope and minimum commitment active. | Founder. | Monthly/weekly cadence. | Capacity, recurring agenda, renewal date. | Renewed / ended / moved to nurture. | Client value signal + capacity load. |
| Partner‑led project | Партнёр и client roles agreed. | Founder + partner contact. | Maintain RACI and shared next action. | Partner, role split, referral origin, disclosure. | Direct / partner closed / stop. | Repeatability and no conflict. |
| Nurture | Not ready but consent/contact basis allows lawful follow‑up. | Founder. | Send relevant educational item at low frequency. | Reason, topic, consent basis, revisit date. | Reactivated / unsubscribed / deleted. | Assisted SQL, opt‑out rate. |
| Disqualified | Permanent no‑fit/unsafe/out‑of‑scope. | Founder. | Referral or close; minimise data. | Reason code, referral given (yes/no). | Closed. | Accurate reason coding. |
| Closed‑lost | SQL/Opportunity did not proceed. | Founder. | Record non‑speculative reason; set consented follow‑up only. | Lost reason, competitor/alternative if volunteered, date. | Nurture/closed. | Learned reason quality. |
| Referral / repeat | Prior client/partner introduces or returns. | Founder. | Treat as New lead but preserve relationship link. | Relationship type, original record, consent. | Move through lifecycle. | Repeat/referred qualified rate. |

## 3. Data minimisation and secure handoff

| Moment | What to collect/do | What not to collect/do |
|---|---|---|
| First form | Name, company/industry, role, one contact channel, short high‑level situation, consent version. | Financial attachments, bank statements, screenshots of 1С, contracts, passwords, card data, special category personal data. |
| Qualification | Business trigger, sponsor, general complexity, preferred safe channel. | Detailed bank balances, full client/employee lists, confidential datasets before fit/NDA. |
| NDA | Use lawyer‑approved NDA/terms; confirm legal entity and intended data exchange method. | Treat a website checkbox as a universal NDA. |
| Data request | Request only minimum documents needed for paid scope, via agreed restricted data room/secure transfer. | Telegram/WhatsApp transfer of financial packs, account credentials or unrestricted links. |
| Telegram | Alert: “New lead #ID, check CRM.” | Text of application, files, personal/financial data, passwords, statements. |
| Email | Short notification and CRM link; business email access controls. | Full form data to broad mailing lists or personal inboxes. |

## 4. UTM and attribution convention

| Field | Format | Example / rule |
|---|---|---|
| `utm_source` | stable lowercase source | `telegram`, `yandex`, `partner_name`, `referral` |
| `utm_medium` | channel mechanism | `organic`, `cpc`, `post`, `email`, `referral`, `event` |
| `utm_campaign` | readable campaign/offer | `cash-risk-check-2026q4` |
| `utm_content` | creative/placement/version | `tg-post-cash-v1`, `partner-onepager-v2` |
| `utm_term` | paid query only | Preserve platform term, no personal data. |
| First touch | First recorded non‑direct source. | Never overwrite. |
| Last touch | Latest known meaningful source before conversion. | Store separately from first touch. |
| Assisted touch | Prior content/channel viewed before qualification. | Use a simple multi‑value interaction log, not a fabricated attribution formula. |
| Partner/referral | Controlled picklist plus free text. | `partner_type`, `partner_name`, `referrer_name` with access control. |

**РЕКОМЕНДАЦИЯ.** Source is not proof of causality. Keep first/last/assisted fields distinct and review qualitatively during small sample sizes.

## 5. Lead scoring structure

No numeric score is asserted as a market fact. Use the structure below; calibrate only against observed outcomes.

| Component | Positive signals | Negative signals |
|---|---|---|
| Contact fit | Owner/CEO/CFO/authorised sponsor; complete lawful contact. | Anonymous form, competitor/vendor research only, cannot reach. |
| Company fit | Complexity consistent with target ICP; recurring finance problem. | Pure tax/bookkeeping request; microbusiness without need/readiness. |
| Intent | Specific trigger, asks for a defined next step, accepts qualification. | Wants a free full audit, generic «познакомиться», no timeframe. |
| Readiness | Data owner, decision process, confidentiality path. | No sponsor, no access, insists on solution before discovery. |
| Negative risk | — | Potential legal/tax opinion, unauthorised data, unrealistic guarantee, unbounded urgency. |

- **MQL rule:** fit + identifiable problem + allowed contact + next action.
- **SQL rule:** sponsor/buyer engages with a specific paid scope or commercial decision.
- **Manual override:** founder records why judgment changed score/status.
- **Score decay:** after a time window selected by West, open but inactive leads move to review/nurture; do not auto‑delete contrary to lawful retention rules.

## 6. Analytics event map

| Event | Platform/record | Required properties | Offline link |
|---|---|---|---|
| `view_service` | Яндекс.Метрика + site analytics | page, service, referrer, UTM. | Service viewed before MQL/SQL. |
| `click_contact` | Metrics | channel: phone/email/telegram/whatsapp. | Contact path. |
| `start_form` | Metrics | form_id, page, UTM, no field values. | Friction diagnostic. |
| `submit_form` | Metrics + CRM | form_id, consent version, lead ID (pseudonymous), source. | New lead. |
| `download_lead_magnet` | Metrics + CRM | asset ID, consent/permission status. | Nurture/assisted conversion. |
| `book_qualification` | CRM + Metrics | booking type, lead ID. | MQL/SQL. |
| `qualified` | CRM only | trigger, ICP, entry route. | Qualification conversion. |
| `paid_entry_won` | CRM only | offer version, source, partner. | Revenue/offer learning. |
| `core_project_won` / `retainer_won` | CRM only | project type, source path. | Offline conversion feedback. |

**ФАКТ.** Яндекс.Метрика поддерживает цели и события, но конкретная implementation должна быть проверена на актуальной документации/аккаунте при запуске. [3] 

## 7. Privacy and security checklist — review with Russian counsel

| Контроль | Минимальное действие | Статус до запуска |
|---|---|---|
| Consent | Separate, specific, versioned text; no pre‑ticked marketing consent. | Юрпроверка обязательна. |
| Privacy policy | Identify operator, purposes, data, periods, rights/contact, processors where required. | Юрпроверка обязательна. |
| Cookie/metrics notice | Explain categories and consent/notice logic under applicable law. | Юрпроверка обязательна. |
| Operator notification | Determine necessity/exceptions and file/update if required. | Юрпроверка обязательна. |
| Hoster/CRM contracts | Identify processors, data route, location, access and support terms. | Юрпроверка обязательна. |
| Primary storage | Map first receipt, CRM, backups, email and messenger flows. | Architecture + legal verification. |
| Access control | Named accounts, MFA where available, least privilege, access review. | Operational owner needed. |
| Role separation | Founder, site admin, CRM admin, contractor access defined. | RACI needed. |
| Backups | Encrypted backup, restore test, retention policy. | Technical runbook needed. |
| Retention/deletion | Schedule by purpose and contract; deletion request process. | Юрпроверка обязательна. |
| Incident process | Detect, contain, record, notify/escalate according to applicable law. | Written incident playbook. |
| Rate limiting | Server‑side limits, WAF/reverse proxy where applicable. | Technical configuration. |
| Anti‑spam | CAPTCHA/honeypot + server validation; assess provider data route. | Technical + legal check. |
| External scripts | Inventory every analytics/chat/font/captcha provider before production. | Privacy review gate. |

**ФАКТ.** Роскомнадзор публикует форму уведомления об обработке (о намерении осуществлять обработку) персональных данных и ресурсы по согласию; Закон №152‑ФЗ является базовым правовым источником, но его применение к конкретной архитектуре должен оценивать юрист. [4] [5]

## References

[1]: https://helpdesk.bitrix24.ru/open/24730032/ "Битрикс24 — создание и настройка CRM‑формы"
[2]: https://help.tilda.cc/forms "Tilda — Data Capture Forms"
[3]: https://yandex.ru/support/metrica/ "Яндекс.Метрика — документация"
[4]: https://pd.rkn.gov.ru/operators-registry/notification/ "Роскомнадзор — уведомление об обработке персональных данных"
[5]: https://www.consultant.ru/document/cons_doc_LAW_61801/ "Федеральный закон №152‑ФЗ о персональных данных"
