# Афина 2.0 — актуализированная спецификация и архитектура приложения
Редакция 3.2 • 04.11.2026, 20:19 МСК • Владелец решений: Андрей
Статус: консолидированная проектная архитектура с интеграцией Kaiten; не отчёт об установленной системе. Не отчёт о развёртывании. Неизвестные параметры и выбранные проектировщиком варианты отмечены явно.



## 1. Цель и приоритет этой редакции
Новая Афина — персональный помощник Андрея и единая точка входа в профессиональные команды агентов. Её назначение — понимать поручение, работать с голосом/файлами/знаниями, выполнять разрешённое самостоятельно, организовывать специалистов и возвращать проверяемый результат.
Создаётся на HostHatch в Docker. Не копируется вся прежняя установка. Полезные требования, роли, проверенные артефакты и опыт сохраняются после ревизии, ошибки и временные обходы не становятся правилами новой версии.
Решения владельца в текущем диалоге имеют приоритет над документами 26.10–01.11, где Beget сохранялся как дом Афины, а Orca — как выбранная мастерская. Новая площадка согласована; CrewAI и CADTopo теперь основные кандидаты. Orca/OpenCode остаются исследованными вариантами исполнения, а не автоматически обязательными зависимостями.
Honcho включён в проект. Продуктовое интервью не завершено: настоящее ТЗ даёт согласованное ядро и проектную модель, но не подменяет недостающие ответы. Нет разрешения на покупку, облачную передачу переписки, DNS-изменения или установку только из-за выпуска документа.
[РЕШЕНИЕ 3.1, сохранено в 3.2] Honcho self-hosted на HostHatch, PostgreSQL+pgvector; embeddings openai/text-embedding-3-large через OpenRouter, 1536. Text functions Honcho также OpenRouter, IDs ещё выбираются. Внепроектное хранение — нормальный режим; project_id=null допустим. Маршрутизация и архивирование независимы.
[РЕШЕНИЕ 3.2] Kaiten включён как планируемая интеграция управления человеческими/бизнес-задачами и портфелем работ, не как ранее работавший подтверждённый connector. Исполнительные attempts/handoff остаются в Афине. Другие решения и выбор командного framework не меняются этой редакцией.


## 2. Метки статуса
[РЕШЕНИЕ] — явно принято владельцем. [ТРЕБОВАНИЕ] — извлечено из источников и подлежит подтверждению актуальности, если спорно. [ПРОЕКТ] — выбранный вариант реализации; не выдаётся за установленное. [ИСТОРИЯ] — ранее наблюдалось, не факт о HostHatch сейчас. [ОТКРЫТО] — требуется решение/проверка. [ПЕРСПЕКТИВА] — не функция первого релиза.
Изменение статуса по evidence: planned → designed → implemented → verified → accepted. Конфигурация, успешная команда и полезный E2E-результат — разные уровни доказательства.
[ПЛАНИРУЕМАЯ ИНТЕГРАЦИЯ] означает принятую архитектурную функцию без утверждения о настроенном token/board/adapter. Для Kaiten сейчас именно этот статус. Новые точные пороги/расписания и число процессов не становятся решениями владельца автоматически. Все diagrams целевые логические модели, не native SQL schema Hermes/Honcho.


## 3. Функциональные контуры и границы объёма
A. Личная Афина: диалог, голос, документы/архивы, память, поиск, уточнение и выдача результатов.
B. Команды специалистов: роли, маршруты, handoff, параллельное исполнение, проверка, приёмка и контроль стоимости. Многоагентная команда — целевая функция, её нельзя заменить одним CLI ради простоты. В пилоте разрешён меньший маршрут для проверки инфраструктуры, не сокращение целевой команды.
C. Эксплуатация: инфраструктура, доступ, мониторинг, резервирование и restore. Административные права не передаются личному агенту.
[ИСТОРИЯ] Голосовое распознавание/общение, офисные документы и ZIP/RAR/7z работали по сообщению владельца. Это функциональная отправная точка, а не гарантия всех форматов и режимов.
[ПЕРСПЕКТИВА] Frigga/Saga/Mimir/Heimdall и dashboard v4 — проекты, не готовые возможности прошлой Афины и не обязательный фронтенд первого этапа. Профессиональные роли команд не надо смешивать с этими четырьмя названиями.
Финансовая команда, методология и анализ — не исключаются понятием «Мастерская», но получают отдельные процессы/источники/критерии и допуск к чувствительным данным. Платежи и утверждение бюджета не автоматизируются по названию роли.
Личный runtime/executor сохраняет собственные способности после подключения команды. Нельзя делать сохранение standalone файла зависимым от Team DB/Kaiten. Самостоятельный защищённый вход Team Control — проектный интерфейс с теми же approvals/budget/audit. Kaiten не обязателен для обычного ответа, локального документа и исполнения разрешённой one-off задачи. Его отказ отображается sync pending, не блокирует весь Hermes.


## 4. Пользовательские интерфейсы
Telegram — первичная точка общения-кандидат с прежним ботом при подтверждении владельцем; allowlist numeric user ID, отдельные разрешённые адресаты, один production consumer token. Старый token после инцидента заменяется по административной процедуре.
Голос: audio → разрешённое STT → transcript с ссылкой на message → проверка неоднозначности → задача → текст/согласованный TTS. Дословная расшифровка и проверка исходного аудио различаются. Подтверждение текста не разрешает внешнее действие.
Штатный dashboard Hermes — управление/чат на athena.west39.ru, не v4. Нужны поддерживаемая авторизация, API/WebSocket protection и отсутствие прямого обхода upstream. Выбор trusted VPN+password либо поддерживаемого публичного auth уточняется для release; Caddy/TLS не отменяет ограничения upstream.
Windows — файловый обмен/скачивание backup, не автоматически управляемый рабочий стол. Подключение локального Excel или всего ПК требует отдельного проекта и разрешения.
Контроль команд сначала доступен через команды статуса/вопросы/отчёты и штатные возможности; собственный UI не является условием backend-пилота. Позже UI — проекция состояния, а не второй task registry.
[3.2] Kaiten — дополнительный рабочий интерфейс задач и внешней координации. Карточка предоставляет input, но текст/комментарий не trusted instruction и не разрешение запуска. Explicit bound author+board policy+TaskRevision обязательны. Изменение карточки не выдаёт administrative grants. Итоговая сдача может отражаться в карточке без автоматического release.


## 5. Сквозная схема
```text
Андрей → проверенная identity/scope/policy → Афина / Hermes
  ├─ краткий ответ / голос / поиск
  ├─ личный executor → scoped workspace
  ├─ Team Control → выбранный adapter → специалисты
  └─ Kaiten adapter → разрешённые boards/cards/comments

Kaiten: business task intent / сроки / исполнитель / рабочая доска
Team ledger: TaskRevision / run / attempt / handoff / checks / budget
CardTaskLink: стабильная связь и snapshot требований, не вторая editable доска

Honcho: API + Deriver + собственный PostgreSQL/pgvector + Redis cache
OpenRouter: embeddings 3-large/1536 + ещё не выбранные text models
Warehouse/catalog: originals / immutable revisions / evidence / ACL
Результат → независимая проверка → Афина/разрешённая доставка → Андрей
Приёмка отдельно от release approval. Backup — административный контур.
```
Kaiten не заменяет ни memory, ни knowledge, ни durable execution ledger. Полные диаграммы поставляются отдельными .mmd; стрелка — интерфейс, не общий mount. Блоки не равны контейнерам.


## 6. Компоненты и предварительное физическое размещение
[ПРОЕКТ] athena-runtime (Hermes/gateway/dashboard по release), athena-executor (ограниченное исполнение). Один active HERMES_HOME/profile, native schema не заменяется task DB.
[ПРОЕКТ] athena-team-control: Task API/coordinator/bounded scheduler/adapters; athena-project-db: PostgreSQL задач/attempts/approvals. CrewAI/CADTopo выбор открыт, workers динамические по лимитам. Один writable workspace owner, scope из trusted service.
[ПРОЕКТ] Honcho: honcho-api, honcho-deriver, honcho-db PostgreSQL+pgvector, honcho-redis cache. На HostHatch, не Cloud. MCP отдельный контейнер не требуется автоматически. Pinned backend/plugin SDK compatibility проверяется.
Предварительная базовая ведомость: 2 personal +2 team +4 Honcho =8 app services до proxy/workers/catalog. Не фиксированное итоговое число Docker containers. Shared catalog/publisher service физически выделяется по ADR; personal registry может быть отдельным SQLite trusted writer, затем shared backend. Team DB хранит artifact refs, не второй primary catalog. Самостоятельная команда должна обращаться к catalog без Hermes.
[3.2, ПРОЕКТ] Kaiten adapter логически отдельный integration boundary. На старте может жить в trusted integration process личного контура с собственным persistence, позже быть отдельным сервисом. Выделять девятый контейнер автоматически нельзя: решение зависит от изоляции token, scopes и resources. Kaiten DB не переносится на VPS, контракт использует внешний workspace. Adapter secrets не выдаются executor/workers.
Compose projects: core, honcho, team; точечные общие API networks. Native Hermes subagents не тождественны team workers; их реальное размещение и tool isolation проверяется отдельно. terminal.backend=docker не доказательство подключения заранее созданного executor.
Один Caddy либо Nginx, не два. Существующий VPN не менять без административного решения; детали Amnezia остаются open. Docker socket/privileged/admin shell агентам не выдаются. UID/GID, cap_drop/read-only root и grants проверяются на фактическом release.
Claude Code/Kilo/OpenCode/Codex — возможные runners, не владельцы production. Auth каждой подписки проверяется, не считается универсальным API.


## 7. Выбор CrewAI/CADTopo и LLM
CrewAI — основной проектный кандидат для контролируемых процессов; CADTopo — равноправный кандидат испытания динамического выбора команды/моделей. Окончательный выбор открыт. Не запускать сразу CrewAI поверх CADTopo поверх Hermes Global.
Сохранить framework-neutral контракт: submit/status/result/answer/cancel/reconcile. Реализацию native API и доступные гарантия проверить. Не выдумывать «официальный Hermes ModelRouter» или model_tier на основе стороннего примера.
Обязательные проверки framework: handoff schemas, версия артефакта, обязательный QA, ожидание approval, continuation/restart, stop/cancel, cost telemetry, внешние tools, parallel workspaces. Динамика топологии не разрешает пропустить обязательный этап.
[ОТКРЫТО] Роль подписки Perplexity: основной LLM-runtime или отдельное исследование. Computer MCP не объявляется drop-in LLM endpoint. API-платёж не подключается без решения. Прежний openai-codex config — исторический факт, не новый выбор.
Для ролей нужны per-role model policy и OpenRouter как желаемый путь с проверкой конкретных моделей и tools/structured output. Названия из старых примеров не копируются как существующие IDs.
Model policy: approved model IDs, provider, allowed data classes, escalation/fallback list, max cost, timeout, max attempts, context limit. Изменение fallback не расширяет права. Квота/ошибка auth и плохое качество — разные причины, не один слепой retry.
Бюджет: reserve перед допуском попытки, settle по реальному usage, UNKNOWN usage отдельно, не ноль. Жёсткий локальный лимит не гарантирует мгновенный внешний stop уже начатых вызовов. Финансовый лимит provider key и отложенные списания учитываются. Менеджер, повторные проверки и embeddings/reasoning входят в общую стоимость.
[3.1 сохранено] Embedding выбор закрыт: openai/text-embedding-3-large/OpenRouter/1536; нет Qwen/Cohere automatic fallback. Main Hermes model и Honcho text IDs отдельные открытые решения. Короткий synthetic compatibility smoke вместо длительного конкурса моделей.
[3.2] Kaiten card не меняет model policy/budget/fallback. Стоимость синхронизации и исполнения различается; чтение REST не требует обязательного LLM вызова на каждом poll.


## 8. Функции и skills
Skill — процедура; tool — действие; role — ответственность; workflow — состояния/переходы; memory — контекст. Skill не равен праву исполнения.
Проектный реестр skills:
SK-01 task-intake: уточнение цели, in/out scope, criteria и classification.
SK-02 voice-interaction: transcript policy, спорный смысл, TTS/fallback и доставка.
SK-03 document-processing: PDF/DOCX/CSV/Markdown и общие проверки артефактов.
SK-04 spreadsheet-safe-workflow: простые книги отдельно от сложных Excel; формулы отдельно от вычисленных значений.
SK-05 archive-processing: ZIP/RAR/7z, ограничения распаковки, безопасные пути и отчёт.
SK-06 research-with-sources: разрешённый поиск, сопоставление, источники/даты/неопределённость.
SK-07 memory-curation: кандидаты, исправления, provenance и запрет повышения данных до правил.
SK-08 knowledge-workflow: выбранный vault/страницы, atomic versioned edits после разрешения.
SK-09 team-dispatch: только валидированные операции Team Control, не administrative shell.
SK-10 handoff-and-evidence: версии inputs/outputs, критерии и фактические checks.
SK-11 acceptance-report: что passed/failed/not_tested/blocked, не самоприёмка.
SK-12 integration-governance: schema/scopes/unknown outcomes и разрешённые adapters.
Это логические capability packs, не утверждение о существовании одноимённых пакетов upstream. Для каждого выбрать совместимый навык или написать минимальный свой, фиксируя commit/version и тест.
Не ставить весь skill pack без отбора. Skill registry: id, version, source/commit, content_hash, description, dependencies, toolset, role/scope allowlist, data_policy, tests, enabled status, update approval. Развёрнутые версии в одном active directory; канонический исходник и release manifest в Git. Неактивные исходники вне skill discovery.
Baseline/AGENTS не исполняют enforcement. Мутации skills через инструменты и обходной terminal контролируются. Старая численность 53/58 навыков не критерий готовности.
SK-13 kaiten-task-integration [ПЛАНИРУЕТСЯ]: read allowed tasks, propose/create/update/comment per policy, reconcile receipts, map business progress to task revision. Это наш capability contract, не утверждение о существующем upstream skill. MCP необязателен: REST adapter достаточно, детали API/secret isolation проверяются.


## 9. Документы, архивы и граница Excel
[ТРЕБОВАНИЕ] Поддержать реально нужные операции с Office и ZIP/RAR/7z. Форматы/объекты/лимиты уточнить на интервью. Архивы: запрет path traversal/symlink escape, квоты файлов/объёма/времени, карантин, encrypted/unsupported error, никакого auto-execute; не обещать поддержку всех RAR-операций одним extractor.
Простой отчёт: создать → открыть → проверить значения/структуру → artifact hash → отправить → outbox. PDF: русский шрифт и проверка чтения. Formula string не означает расчёт.
Целевая старая рабочая среда — Excel 2021 на Windows 10 Pro 64-bit; разрядность Excel отдельно неизвестна. Сложные книги с внешними связями, именами, PQ/Pivot/VBA не пересохранять openpyxl/LibreOffice без доказанной сохранности. LibreOffice не утверждён как их главный движок.
Нужная нативная проверка Excel — отдельный workflow/Windows runner после согласования, не уже имеющийся доступ к ПК. Пока его нет: «подготовлено, не проверено в целевой среде». Отдельный синтетический тест внешних ссылок/имён не доказывает сохранность всех Excel-объектов.
Финансовые расчёты выполняются проверяемым кодом/SQL/целевым движком по согласованным правилам, а не только LLM-оценкой. Отсутствующие ставки, сроки и суммы unknown, не выдуманные числа.

## 10. Память и Honcho
[РЕШЕНИЕ] Self-hosted Honcho на HostHatch: API/Deriver/PostgreSQL+pgvector/Redis. Embeddings openai/text-embedding-3-large через OpenRouter, 1536; text functions через OpenRouter, конкретные IDs открыты. Собственное хранение не равно local inference: разрешённые тексты уходят модельному provider. Honcho Cloud не вариант постоянного хранения.
Четыре слоя: trusted rules, knowledge/sources, personal memory, operational ledger. Один active external memory provider согласно runtime. Plugin/API и release compatibility проверяются, latest docs не installed fact.
Identity binding principal/environment/privacy_domain/profile/workspace/peer/session. Session ID не ACL. Prod/test и work/personal разделять реальными credentials/workspaces/scoped recall; native MEMORY.md/USER.md тоже проверить. Developers не получают всю личную память.
Один memory sender: accepted message не derived-ready. Native sync/prefetch hooks использовать, gap в durability решать одним ledger/outbox adapter, не второй независимой отправкой. UNKNOWN after accept требует reconcile, not blind replay. Cache keys включают scope/policy; corrections/tombstones invalidation обязательна. Forget conclusion не уничтожает source/backup автоматически.
Actual embeddings single+batch должны быть 1536 из Honcho client; одного env dimensions недостаточно. При ошибке pinned compatibility — blocker, не truncation/vendor change. По каждому text module explicit model/base_url.
API keys, private keys, raw tool logs не сохранять. Native secret scrub не полный DLP. Honcho outage: bounded timeout, explicit degraded; важные decisions из trusted record. Новое сохранение подтверждается durable receipt, не текстом модели.
Obsidian/Wiki один primary, memory гипотеза не approved policy. Honcho не редактирует knowledge автоматически.
[3.2] Карточки Kaiten не синхронизируются сплошным потоком в personal memory. Для task context берём минимальную разрешённую проекцию со source URL/id/version/fetched_at. Нельзя записать чужую рабочую карточку в общий пользовательский профиль. Approved business decisions попадают в knowledge/memory только по policy. Kaiten и Honcho credentials различны.


## 11. Данные: источники истины и хранилища
Hermes state.db — нативное runtime state, руками схему не меняем. PostgreSQL project DB — наш task/attempt/handoff/approval ledger. Honcho — внешний/private memory backend. Obsidian — primary выбранных заметок. Git — версия исходников. Files/artifacts — неизменяемые версии результатов. Monitoring/UI — проекции, не дополнительные источники истины.
Не синхронизировать активные БД копированием файлов. Миграции versioned; init SQL не способ upgrade live DB. JSON Schema и payload limits обязательны. Contract adapters отделены от native DB/API framework.
Дальше перечислены проектные сущности, а не уже встроенные таблицы Hermes/CrewAI/CADTopo.
[3.1] Artifact catalog — primary ID/revision/access/lifecycle/location metadata, warehouse — основной payload. Manifest — portable versioned snapshot, не второй editable authority. Personal catalog не зависит от Team Control. Native Hermes, Honcho, Kaiten и наш ledger имеют отдельные schema owners.
[3.2] Kaiten — authority business fields карточек: title/description/due_date/assignees/location при отсутствии специально согласованного иного владельца. Локальный TaskRevision хранит immutable requirements snapshot, а не конкурирующую live-карточку. Execution attempts/checks/actual usage — authority internal ledger. Поле-владелец и conflict policy явно заданы; no blanket last-writer-wins.


## 12. Сущности модели данных
Identity: Principal(id,type,status), ExternalIdentity(principal_id,channel,external_id,verified_at), ContextScope(id,environment,privacy_domain,project_id). Unique channel+external_id; scope определяется доверенной стороной.
Project(id,owner_id,scope_id,name,status,version,repo_ref,vault_ref); model/privacy policies ссылками на immutable revisions. Наличие repo/vault не право доступа.
BusinessTask(id,project_id,created_by,title,current_revision,status,priority,version); TaskRevision(task_id,revision,objective,in_scope,out_scope,acceptance_criteria,input_refs,constraints,approved_decision_ref,payload_hash). Unique task+revision; утверждённая revision immutable.
WorkflowRun(id,task_id,revision,framework,adapter_version,plan_revision,status,started_at,completed_at,budget_policy_ref); Stage(id,run_id,role_profile_revision,dependencies,required_gate,status,version). Один task может иметь много runs по явным причинам, а не из-за retry сетевого запроса.
ExecutionAttempt(id,stage_id,attempt_no,fencing_token,lease_until,worker_ref,model_policy_revision,bundle_id,base_snapshot,result_snapshot,status,heartbeat_at,external_refs,error_code). Unique stage+attempt_no. По умолчанию один активный владелец writable workspace; stale fencing token не может завершить новую попытку.
Artifact(id,owner_id,scope_id,project_id nullable,storage_category,classification_status,lifecycle_status,context,access_policy_ref,retention_policy_ref). ArtifactRevision(id,artifact_id,revision,relative_storage_key,sha256,size_bytes,mime,validation_status,original_filename,source_ref,received_at,created_at,supersedes). TaskArtifactLink(task_revision_id,artifact_revision_id,relation) и AttemptArtifactLink(attempt_id,artifact_revision_id,relation) many-to-many без копирования. Snapshot не-кода — manifest/hash, не обязательный Git commit. Project relation не расширяет ACL.
Handoff(id,from_stage,to_stage,task_revision_id,producer_attempt_id,input_snapshot,output_snapshot,bundle_id,artifact_refs,checks,limitations,questions,status,accepted_by). Handoff immutable после принятия; новый результат создаёт новую версию и инвалидирует затронутые проверки.
CheckResult(id,subject_snapshot,criteria_revision,check_type,status,evidence_artifact_id,executor_identity,started_at,exit_code). passed/failed/not_tested/blocked; null exit code не 0. LLM review и test execution помечаются разными типами.
Approval(id,actor_id,operation,target,canonical_payload_hash,target_version,scope,expires_at,one_time,status,consumed_at); Decision(id,task_revision_id,kind,visible_payload,actor_id,outcome,reason,evidence_refs). Приёмка и release — разные kinds, не один флаг approved.
PolicyRevision(id,rule_id,revision,layer,scope,role_filter,effect,resource,operation,statement,typed_conditions,status,hash); TrustedApprovalRecord отдельно от worker fields. GovernanceBundle(id,scope,policy_refs,role_revision,manifest_hash,created_at,status). Хеш — идентификатор целостности, не доказательство автора.
RoleProfile(id,revision,goal,input_schema,output_schema,skill_versions,tool_scope,model_policy_ref,review_policy); SkillRevision и ModelPolicyRevision согласно разделам 7–8.
InboxMessage(id,source,external_event_id,payload_hash,processed_at), OutboxEvent(id,type,aggregate_id,sequence,payload_ref,status,attempts,next_retry_at), AuditEvent(id,correlation_id,actor,operation,target,outcome,decision_ref,safe_metadata,utc). Unique source+external_event_id; не хранить секреты в metadata.
MemoryBinding(principal,environment,privacy_domain,profile,remote_workspace,peer_ref), MemorySyncEvent(source_ids,event_id,payload_hash,scope,status,remote_refs), CorrectionRecord(id,scope,source_refs,status,supersedes,tombstone_at); schema принадлежит integration, не ручной модификации Honcho DB.
BudgetAccount(id,scope,currency,limit,period), BudgetReservation(id,attempt_id,estimated,committed,status), UsageRecord(id,attempt_id,provider_request_id,tokens,cost,pricing_version,status). Авторизация запуска атомарно резервирует ресурс; уточнённый bill сохраняется отдельно.
BackupSet(id,server_id,capture_method,point_in_time,completed_at,consistency,manifest_hash,files,status,windows_verified_at,ssd_verified_at,restore_verified_at,error). Три места хранения и restore — отдельные статусы.
BusinessTask.project_id nullable, ContextScope.project_id nullable. Standalone file не требует task/attempt. ArtifactProjectLink — дополнительные проекты; StorageLocation/ArtifactLocation фиксируют physical refs и одно primary payload. AccessPolicyRevision/RetentionPolicyRevision отдельно от категории; archive status не directory requirement.
AttachmentRef связывает native event с revision, не дублирует whole Hermes transcript. BackupCopy и RestoreTest отражают отдельные independent copy/restore results.
Новые сущности3.2: KaitenConnection, KaitenScopeBinding, KaitenCardRef, CardTaskLink, CardSnapshot, FieldMappingPolicy, IntegrationOperation, SyncCursor, IntegrationEvent, SyncConflict. Состав полей/кардинальности — раздел31 и04_Data_Model.mmd. Это application/integration entities, не новые таблицы Kaiten/Hermes/Honcho.


## 13. Инварианты, конкурентность и долговечность
Любая изменяемая значимая сущность: version/expected_version; конфликт 409 или аналогичный typed error, не last-writer-wins. Change может создать новую TaskRevision с повторным approval/QA.
Повтор submit с тем же idempotency key+actor+operation и hash возвращает прежний receipt. Иной payload — конфликт. Локальная транзакция фиксирует state+outbox до acknowledgement. Внешний запуск не атомарен с DB; UNKNOWN требует сверки перед новым execution.
Один execution owner; leases/fencing для многопроцессного control plane. После restart сначала reconcile с workers/framework, затем новые starts. Heartbeat absence означает suspect, не автоматическую смерть. Kill/cancel не rollback внешних изменений.
Ещё не опубликованный durable outbox — не гарантия exactly-once. Delivery at-least-once, dedup локального эффекта и reconciliation. Порядок сообщений — sequence агрегата; нельзя принять old attempt result вместо current.
Переходы: DRAFT → AWAITING_APPROVAL при необходимости → QUEUED → RUNNING → VERIFYING → AWAITING_ACCEPTANCE → ACCEPTED. Боковые: WAITING_FOR_INPUT, WAITING_FOR_QUOTA, BLOCKED, FAILED, OUTCOME_UNKNOWN. CANCEL_REQUESTED завершается только после установленного фактического исхода; NEEDS_REVIEW допустим. Native framework states отображаются, не отождествляются.

## 14. API и контракты
[ПРОЕКТ] Закрытый Task API version /v1, HTTPS/private network или authenticated Unix/локальный канал. Authentication и route-level authorization; client не выбирает owner/scope из prompt.
POST /v1/tasks — регистрация/валидация; GET /v1/tasks/{id} — статус; POST /v1/tasks/{id}/revisions — изменение требований; GET /v1/tasks/{id}/artifacts — только разрешённые refs; POST /v1/decisions/{id}/answer — конкретное решение; POST /v1/tasks/{id}/cancel — запрос остановки. Это наши будущие endpoints, не native API CrewAI/Hermes.
Сервисные start/poll/cancel/reconcile спрятаны в framework adapter, не прямые публичные handlers. Providers не принимают произвольный shell или path из пользовательского payload.
```json
{
  "schema_version": "1.0",
  "idempotency_key": "project-task-r1-submit",
  "project_id": "approved-project-id",
  "objective": "Подготовить проверенный результат",
  "inputs": [{"artifact_id": "source-id", "revision": 1}],
  "acceptance_criteria": [{"id": "AC-1", "statement": "Определённый проверяемый результат"}],
  "constraints": {"deployment_allowed": false, "budget_policy_id": "approved-policy"}
}
```
Reply: task_id, revision, status, correlation_id; accepted/queued не completed. Ошибка: code, retryable, safe message; no secret traceback. Large attachments идут отдельным зарегистрированным artifact upload, limits после измерения; произвольные URL/local paths не принимаются без политики.
Approval отвечает только на существующий server-issued decision и видимый payload. Проверка approval, consumption и local mutation транзакционны. Для внешних действий фиксируется intent; повтор проверяется по request ID, а не формулировке «да».
[3.1] project_id может быть null. Standalone register/read/publish/link/archive/delete — catalog contract, не обязательный POST task в team DB. Exact catalog endpoints — ADR, не выдуманные native Hermes APIs.
[3.2] Вход из Kaiten проходит те же TaskRevision/policy/approval/budget gates. Adapter операции read/list/propose create/update/comment/move имеют scope-bound API; raw provider token и arbitrary URL клиент не получает. Native REST routes и versions сверяются по official docs, не используются как webhook execution permission.


## 15. Governance и команда
Наследуется не Orca-specific naming, а baseline+role+approved project/task overlays. Один trusted writer; workers не редактируют approved registry, approvals и validator code. Proposed architect overlay не approved policy.
Builder deterministic: scope → current approved revisions → trusted authority/hash → conflicts → effective bundle. Deny-first для точных типизированных операций; не утверждать, что демо решает semantic conflicts текста. Отдельные краткосрочные исключения: exact target/operation/expiry/approver, не общий bypass.
Normative bundle закреплён на Attempt. Новые версии не меняют active work silently; revocation блокирует новые starts и запускает контролируемую процедуру для текущих. Worker acknowledgement bundle не доказательство реального tool permission: нужна проверка runtime.
GitHub packages из ревизии fba0cde7247c90b427e4d65a3612ea4f8546c839 — reference prototypes. В Blueprint demo есть проверка trusted digest, а Implementation Kit проверяет status и имеет ограниченные unit tests. Нельзя слить их механически или выдать тестовый output за production enforcement. Исходники не исполнялись данным документом.

## 16. Роли и handoff маршруты
Каталог команды: Product Manager; Business Analyst; System Analyst; System Architect; 1C Analyst по проекту; UI/UX Designer; Frontend/Backend или общий Developer; Data Engineer; QA; Code Reviewer; Git Manager; DevOps/Release; Technical Coordinator. Это логические роли; не все активны на каждой задаче.
Athena отвечает за понятную цель и коммуникацию; PM за scope/ценность; coordinator за технический план/очередь/attempts; reviewer не финальный пользователь-approver.
Пример software route: Intake → PM/BA → SA ↔ Architect; UX параллельно при необходимости → Developers → Integration snapshot → QA + Code/Design review → acceptance package → Андрей → отдельный release.
Пример analytical route: Intake → Business/Domain Analyst → Data prep → Methodology/SA → расчёты/сопоставление → независимый review → отчёт → Андрей. Кода может не быть, immutable artifact manifest всё равно нужен.
Пример finance template: Data Steward → Budget Planner → Controller → расчётный pipeline → Reporting → review. Проект ещё требует правил источников/лимитов/оплат/сроков; нельзя «вывести БДДС из БДР» без условий. Ни один manager не утверждает платёж или бюджет за владельца.
Handoff включает task revision, role, attempt, rules bundle, inputs, result snapshot, checks/evidence, open questions/limitations, next owner. Missing required field → BLOCKED, не догадка. Обнаруженный QA defect → новая попытка с ссылкой на исходный результат. Исчерпание quality/cost limit → эскалация.

## 17. Каталоги, склад и карта прав
```text
/srv/athena/
  deployment/{core,honcho,team}/          # Compose/templates/versions
  state/
    hermes/<profile>/                   # единственный active home
    catalog/                            # artifact registry, не Hermes state.db
    integrations/kaiten/                # bindings/cursor/receipts; payload minimal
  warehouse/
    intake/YYYY-MM/IN-ID/payload/
    standalone/{personal,work}/{documents,spreadsheets,presentations,administration,other}/
    standalone/unclassified/
    one-off/YYYY-MM/TASK-ID_Название/{sources,results,evidence}/
    library/{templates,instructions,references}/
    media/conversations/YYYY/MM/DD/CONVERSATION-ID/MESSAGE-ID/
    knowledge/telegram/{original,normalized,migration-review}/
    projects/PRJ-ID_Название/
  work/jobs/                            # intermediates, scoped RW
  cache/                                # recreatable
  model-assets/                         # versioned assets, not tmp
  control/db/                           # project-db/admin only
  control/governance/{baseline,roles,proposals,approved,bundles}/
  control/policies/
  workshop/{repos,worktrees,worker-homes}/
  runtime/{executor-home,memory-ledger,caches}/
  honcho-data/{postgres,redis,manifests}/ # target dedicated FS/UUID
  operations/{inventory,decisions,runbooks,acceptance,backup-catalog}/
/etc/athena/secrets/                     # Kaiten key адресно, не весь каталог агенту
```
Фигурные скобки сокращают схему, не буквальные имена. Actual volumes/FS/UID/GID после inventory; не форматировать unknown disk. Нативные auth/cache/logs Hermes сохранять по release. Primary Obsidian отдельно, не три изменяемые копии.
Новые результаты: Название_YYYY-MM-DD_rNNN.ext, UTC timestamps, дата по Москве; business period отдельно. Original filename/source event сохраняются, hashes вычисляет publisher. Excel linked комплекты не rename автоматически. Git code — штатные filenames/commits.
Personal/admin docs в standalone; operations/deployment/governance/secrets различаются. Original immutable, новая revision при изменении. Shared project refs не независимые editable payloads.
Runtime RW own home и разрешённые операции; executor inputs RO/job RW, не warehouse целиком. Reviewer RO snapshot, review через сервис. Workers не видят secrets/native state/control raw DB. Listing/search/preview/download проверяют ACL до metadata. Permission не повышается по card URL.
Kaiten token только adapter. Нельзя хранить его в skill, memory, card description, Git или широком env executor. Локальные snapshot/receipts содержат private data, доступны по исходному connection/scope policy и имеют retention. Они не объявляются полной offline копией Kaiten.


## 18. Ночная копия и Windows
[РЕШЕНИЕ] Каждый день в 00:00 Europe/Moscow автоматически создаётся полный образ всех требуемых дисков. Он не ждёт владельца/Windows/Kingston. Вечером владелец скачивает готовое в Windows, затем переносит на Kingston и проверяет. S3 не обязательная покупка.
[ОТКРЫТО] Механизм capture/export: provider snapshot с доступным экспортом, offline/rescue или доказанный snapshot-capable способ. SSH сам по себе не даёт согласованный full image. Provider snapshot без независимого export и docker save не выполняют требование.
На том же HostHatch можно держать готовый комплект только как промежуточный. Нельзя создавать растущий image внутри включённого source disk/tree. Отдельный исключённый staging volume/external capture или согласованный иной способ выбирается после inventory. При выключении guest нужен внешний controller. Если prerequisites отсутствуют — blocker, не ложный full backup.
Lifecycle: lock/preflight → согласованное состояние → capture → возврат сервисов → export/check → SHA256 manifest → READY → atomic latest. Дисковое состояние и приложения, включая project DB/Honcho self-hosted, должны быть согласованы выбранным методом.
Нужны athena-imagectl (server/admin create/status/verify), Download-AthenaImage.ps1 (готовый ID в Windows, partial/resume по транспорту, hashes, fresh date) и Verify-AthenaBackup.ps1 (проверка Kingston). Это поставка реализации, не созданные данным документом scripts. Диск и пути не угадываются.
Ready/Windows verified/SSD verified/restore tested — отдельно. Старые версии не затираются молча, retention по фактической ёмкости. Ошибка/старый image/пропуск/место/неподнятый сервис дают alerts. Внешний watchdog выбран отдельно; сам HostHatch не наблюдает собственное полное выключение.
Honcho dedicated volume входит в capture. После restore сверить source events/outbox/corrections/tombstones до новых writes; reconstruction не точный restore. Секреты image зашифровать, recovery key вне VPS. SHA256 не доказательство загрузки системы: isolated restore с отключёнными production tokens/cron/VPN identities.
[3.1] Logical dump перед migration дополняет full image. Roles/config/secrets/release manifests отдельно; pg_restore list/hash не actual restore. RPO/RTO открыты.
[3.2] Backup включает local Kaiten bindings, receipt/outbox, snapshot versions и mapping policy. Внешняя БД Kaiten не входит в VPS image. Полный export/backup данных Kaiten и его retention отдельно согласуются; не обещать восстановление hosted board из local cache. При restore adapter сначала read-only reconcile current remote state и pending intents, затем writes; не публиковать повторно старые comments/cards.


## 19. Сетевая и эксплуатационная безопасность
Read-only inventory HostHatch: hardware/ОС/disks/FS/Docker/backend firewall/IPv4/IPv6/VPN/Caddy/доступ. Не форматировать, не менять SSH/UFW и не выключать VPN вслепую. Нужен проверенный резервный вход и rollback перед network changes.
Public listeners — только согласованные SSH/HTTPS/VPN. Docker ports не считать закрытыми из-за UFW; no wildcard publication для служебного. Backend iptables/nftables проверяется, не копировать DOCKER-USER recipe туда, где такой цепочки нет. Не iptables:false, не второй Caddy. Internal network не даёт egress policy сервису, подключённому одновременно к другой egress-сети.
Обновления по pinned versions, release notes/migrations, backup и rollback; не unattended application update. Логи ограничены; disk/inode/RAM/OOM/restarts/queue age/cost/export freshness observable. No arbitrary admin shell от агента. Read-only root/cap_drop/no-new-privileges/limits по совместимости; исключения SSH startup документируются.

## 20. Доработки относительно исходников и ошибок
Не писать «память была выключена»: phase3 показал enabled defaults и toolset gap; не писать «config mismatch установлен»: сравнение его опровергло. Из наличия root PID1 executor не следует root у команд Афины. Эти выводы — обязательные lesson records с источниками.
Сохраняем baseline/roles/handoff и reliability contracts из оригиналов, а не обязательные Orca flags и старые имена хостов. Предыдущие handoff demos не являются IAM или готовым coordinator.
Не считать файлы Word/PDF «проверенными» по установленным библиотекам; не превращать request timeout в успешное выполнение; не объявлять source main текущим installed release; не менять global lazy-install policy ради local STT без основания.
Для каждой ошибки есть regression test и статус. Использовать старые arifacts как источник, не обновлять production их содержимым автоматически.

## 21. Этапы и критерии выхода
E0 Завершить точечное интервью: приоритеты, каналы, scope данных, основной LLM и text models Honcho, бюджет/простой. Уже описанные роли повторно не изобретать.
E1 Inventory/security и независимая исходная копия действующего HostHatch при доступном методе. Выход — безопасный план, не разрушение имеющегося.
E2 Feasibility: основной LLM; pinned Hermes+Honcho; full image; CrewAI/CADTopo controlled comparison. Выход — ADR и доказанные capabilities/gaps.
E3 Личная Афина: runtime/executor/voice/documents/archives/profile. Выход — E2E, negative cases, recreate.
E4 Honcho: короткий synthetic pilot actual embeddings1536 single/batch, correction/isolation/outage/restore; controlled import. Длительное сравнение embeddings не требуется.
E5 Team contracts: project DB, schema, registry/approval/bundle, bounded coordinator/adapter; функциональный маршрут включает разные роли и независимого проверяющего.
E6 Параллельность, model escalation, retry/restart, budgets и evidence. Выход — одинаковые тестовые проекты для кандидатов, final framework ADR. Не требуется одновременно production обеих систем.
E7 Full image/Windows/Kingston/isolated restore; alerts и эксплуатационная передача.
Разработка может идти с перекрытием при независимости шагов. Точные сроки после gates; это не обещание построить весь stack и все специализации за один день. Конец этапа — checkpoint implemented/verified/blocked со ссылками, а не фраза «готово».
E8 Kaiten planned integration: tenant/boards/access policy → read-only smoke с pagination → local mapping/requirements snapshot → controlled test card/comment/move → timeout/dedup/conflict/access tests → acceptance. Не ждать готовой команды для read integration, не превращать every card в автоматический execution. Public webhook receiver не условие первого этапа.


## 22. Матрица приёмки
A01 Личное текстовое и голосовое поручение проходит до доставленного проверенного результата.
A02 Неавторизованные Telegram/web/API и приватные network ports отклонены; IPv6 проверен.
A03 PDF/DOCX/XLSX/ZIP/RAR/7z по утверждённым сценариям, quotas и negative cases. Complex Excel отдельно target-tested.
A04 Preferences/corrections в новой сессии/recreate; origin и статус не выдуманы; Honcho не смешивает peer/workspaces.
A05 Honcho failure bounded, secret canaries не уходят; cache invalidation/delete/restore tested или limitations blocked.
A06 Самостоятельная команда передаёт versioned handoff, выполняет обязательный независимый review и возвращает defects на новую попытку.
A07 Проверка связана с snapshot и requirements revision; новая версия не наследует старый PASS автоматически; acceptance не deploy.
A08 Workers не могут утвердить свои grants/правила; proposed/tampered/other-scope bundle отвергается. Runtime denies tested alternative tools.
A09 Повтор submit, lost launch receipt, crash до/после ack, stale attempt и cancellation не дают дублированный эффект без обнаружения.
A10 Per-role model choice и разрешённая эскалация, blocked quota и бюджет без скрытого платного fallback.
A11 Отключение ноутбука не останавливает серверный процесс; reboot/restart вызывают reconcile.
A12 Пустой tmp/recreate не теряют dependencies/memory/results.
A13 Full image всех дисков READY, Windows/Kingston verification и isolate restore; пропуск запуска/старый backup detected.
A14 Полная traceability: requirement → stage/role → artifact snapshot → check evidence → decision. Неиспытанное not_tested, unknown cost не 0.
A15 Standalone/one-off с project_id=null работают без Team DB/Kaiten; artifact links не повышают доступ.
A16 Archive/category/ID/provenance сохраняются; cleanup active input/result не удаляет без policy.
A17 Honcho actual embeddings1536 single/batch; recreate не теряет state/warehouse; missing UUID не создаёт blank DB.
A18 Scoped direct team client и независимая личная Афина; tools alternative paths не обходят grants.
K01 Connection+board allowlist: outside-scope listing/read/write denied.
K02 Paginated cards read, больше одной страницы; board metadata не источник всех cards.
K03 Стабильный CardTaskLink и immutable requirements snapshot; нет автоматического исполнения arbitrary card text.
K04 Controlled create/comment/update; lost response→UNKNOWN→reconcile, no duplicate write promise.
K05 Human concurrent field change не затёрт; version/diff conflict показывает owner.
K06 QA pass не автоматически Done/release; статус mapping и acceptance отдельно.
K07 No token/private content leakage into memory/tools/logs/public links.
K08 Adapter restore read-only reconciliation не переигрывает прежние writes.
K09 Kaiten unavailable не останавливает ordinary dialog/local work; sync pending visible.


## 23. Открытые решения и риски
Закрыто: HostHatch, Hermes, own Honcho/PostgreSQL+pgvector, OpenRouter embeddings3-large/1536, nullable project/warehouse categories, archive independent lifecycle, backup00:00МСК/Windows/Kingston. Kaiten включён архитектурно как planned integration, не working connector.
Открыто: main Hermes model/подписка, Honcho text IDs/releases, CrewAI/CADTopo, executor physical bridge/subagent isolation, catalog/publisher service placement, factual resource/storage UUID, proxy/VPN/Amnezia details, Obsidian primary, native Excel runner, capture/export/staging/controller, classifications/retention/RPO/RTO, CI registry/restricted dispatcher, monitor external placement.
Kaiten-specific open: tenant domain, scopes/boards/lanes, token identity+actual permissions, allowed fields/operations, status mapping, sync frequency, polling→webhook gate, fields concurrent updates protocol, export/retention. Никаких invented credentials/IDs/«общий доступ пока временно».
Work/personal не sensitivity taxonomy. Старые Black/Red/Yellow/Green не смешивать с Green/Amber/Red. Numeric RAM/DR policies ниже — предложения, не order/purchase. Реальный сервер/backup evidence ведётся отдельно, не меняется из-за version bump документа.


## 24. Источники и история решений
R01 Текущая переписка 03–04.11.2026: новая HostHatch, Honcho, nightly image, интервью и переработка наследия.
R02 Athena_AI_Infrastructure_Technical_Spec_RU_v1_1.md и AI_Infrastructure_Baseline_RU_v1.md — исторические границы и требования; placement Beget superseded.
R03 audit-phase2/phase3 и inventory 30.10 — исторические наблюдения, не state HostHatch.
R04 excel-target-contract-and-link-test.md — отдельные режимы простых и сложных Excel.
R05 Orca_Team_Role_Specification_RU.md и Athena_Orca_System_Design.md — роли/handoff/attempts/reliability, native Orca details остаются исторической реализацией-кандидатом.
R06 Governance_Runbook.md и оба пакета GitHub на commit fba0cde7247c90b427e4d65a3612ea4f8546c839 — reference prototypes и ограничения.
R07 DeepSeek research MD и длинная ветка Perplexity — пользовательские сценарии и варианты; ответы ассистентов не первичная сертификация API.
R08 Предыдущие официальные технические проверки Hermes/Honcho/CrewAI/CADTopo в диалоге — выбрать и перепроверить pinned release до implementation.
Эта редакция заменяет конфликтующие проектные рекомендации прошлых редакций, но не задним числом утверждает открытые решения. Файлы и diagrams созданы, серверы не изменены, code не установлен.
R09 Решения текущей переписки: Honcho self-hosted, embeddings3-large/1536, warehouse и nullable project, короткий integration smoke, handoff и deployment methodology3.1.
R10 Уточнение Андрея04.11.2026 20:07 и20:19МСК: Kaiten раньше был запланирован архитектурно, не реализован; редакция3.2 добавляет именно эту интеграцию. Framework selection неизменён.
R11 Official Kaiten API https://developers.kaiten.ru/ ; boards/get-board ; external-webhooks, проверено04.11.2026. Документация backend — не доказательство настроенного token/плановых функций.
Приоритет: прямое решение владельца→актуальная спецификация→ADR→implementation/evidence. Предположения ассистента не становятся accepted автоматически.


## 25. Маршрутизация, жизненный цикл и исключения
Intake: новое до решения; standalone: самостоятельное; one-off: разовое файловое поручение; library: reusable; project: реальный проект; conversation-media: сохраняемые вложения. Обычная беседа остаётся native history, без обязательного DOCX/task/project. Неизвестное → needs_review с причиной и решающим, не uncontrolled misc. Other — тип известного материала, не отсутствие классификации.
Category и lifecycle независимы. Archive по completion/supersession/утрате актуальности/указанию владельца, сначала status без физического переезда. ID/access/source сохраняются. Возраст открытия не deletion. Trash не backup.
SHA duplicates сохраняют source events, одноимённый файл не overwrite. Damaged/encrypted/quarantine без ложного processed. Linked Excel paths сохраняются. Copy между FS: staged check/commit/reconcile; исходник не удалять до проверки. Hold блокирует уничтожение.
Cleanup jobs после terminal+published required outputs+leases/refs+approved retention. Numeric сроки audio/intake/cache/trash/archive открыты. Dry-run deletion показывает exact IDs/объём/основания/backup status. Source/result не удаляются автоматически по возрасту.

## 26. Физическое хранение и ресурсный бюджет Honcho
Dedicated FS по UUID, pgdata/redis external volumes bind после mount guard. Docker restart containers при boot должен ждать том; preflight только ручного deploy недостаточен. Изменения fstab/systemd не применять без проверки SSH/VPN/других служб.
Проектные бюджеты: Honcho4vCPU/8GiB/100GiB data; личный runtime/команды дополнительно. Малый pilot2vCPU/4GiB ограничен; общий VPS6–8vCPU/16GiB ориентир, не доказанная ёмкость/закупка. GPU для remote inference не нужна.
DB3072+API1024+Deriver1536+Redis512 MiB=6144; host reserve2048. DB envelope: shared768+backend200+work256+autovac128+maintenance256+background256+filecache512=2376MiB; reserve696 до3GiB. Допущения20sessions/8heavyqueries×2operations×8MiB×hash2. Не hard ceiling, pools/private allocations/parallel plans тестировать. Effective cache hint не allocation.
vector1536=6152bytes/value; 100k≈0.573GiB,1m≈5.729GiB без heap/text/index/WAL. Active set не обязан помещаться вRAM, P95 зависит отIO/cache. Не обещать быстрый миллион при DBlimit3GiB. Ресурсные параметры здесь сохранены из проекта3.1 и этой редакцией не утверждаются заново.

## 27. Deployment, CI/CD, migration и rollback
Отдельные Compose core/honcho/team; shared API network Hermes↔Honcho, private DB/cache, egress не domain allowlist. Proxy один. Native health/readiness различаются. Перед pinned deployment inventory+independent copy.
CI внеprod: syntax/secret scan→pinned build→SBOM/security→disposable migration/role tests→trusted synthetic model smoke→staging→immutable manifest. PR не получаетprod secrets/docker socket. Optional SDK adapter не добавляет framework автоматически.
CD: exact digest approval/serial lock→UUID/free disk/config→pull before downtime→all writers quiesced→final dump/hash→один migration owner→API auth/schema→Deriver→memory/scope tests→evidence/приёмка. Restricted root dispatcher — обязательная доработка, прежний ops.py не делает manifest signature/UUID enforcement.
Rollback несовместимой схемы: failed DB сохранить, old backup восстановить отдельно, old image/config, тесты, switch. Postbackup events replay только с доказанным ledger/dedup, не zero-loss обещание. Honcho/PGmajor/disk/model не менять одним шагом. Init.sql не upgrade script.
[3.2] Adapter rollout read-only first; writes отдельным gate, собственная mapping schema migration и backup. Restore сначала live Kaiten reconciliation. Его outage не даёт повышенных прав.

## 28. Логи, мониторинг и восстановление
local logging10m×5/container, compress; size retention не time retention. DBstderr без duplicate collector; raw payload/token/SQL не логировать без redaction policy. File logs/proxy/journal отдельно. Info не полная гарантия отсутствия персональных данных.
Passive checks: auth read, SQL, process/OOM/restart, backlog/oldest item, disk/inodes/WAL, retrievalP95, model errors/cost, mount UUID, backupage/TLSexpiry. Running Deriver не recall-ready. Restart policy не лечит автоматически unhealthy. Внешний watchdog для полного падения VPS.
Решение: full image00:00 Europe/Moscow и вечер Windows→Kingston. Предложения: weeklyThu14 logical restore, firstSat12 monthly image drill — только после согласования. Restore target безprod tokens/cron/VPN identities. RPO/RTO открыты, offsitecopy age фактический; SHA не bootability.
Kaiten monitoring: lastsuccessfulread, cursorage, pendingwrite/unknownconflicts,429/403, mapping failures. Alerts не включают card private text/token. Remote hosted data backup отдельно от VPSimage.

## 29. Содержание поставки и правила моделей
Athena_2_0_Architecture_v3_2.mmd и01_Architecture.mmd — идентичные логические диаграммы.
02_Physical_Deployment.mmd — размещение/сетевые boundaries, adapter placement project.
03_Data_Map.mmd — primary stores и sync.
04_Data_Model.mmd — полная logical ER, nullable project иKaiten refs.
05_Agent_Workflow.mmd — диалог/личный/командный/Kaiten маршруты.
Architecture_v3_2.png — overview как прежняя картинка; Athena_2_0_Data_Model_v3_2.png — отдельная группированная карта сущностей.
Cross-store refs не physical SQL FK; native schemas не правим. Диаграммы описывают интерфейсы, не гарантии готовности. Markdown иWord имеют одинаковый основной текст.

## 30. База редакции и scope изменения3.2
Сохранены решения3.1: ядро/инструменты/память/команды/warehouse, snapshots+approvals+budget+reconcile, own Honcho+OpenRouter1536, deployment/DR, role routes, Excel restrictions. Внесено только предметное дополнение Kaiten в связанные архитектурные разделы, модели, flows и acceptance.
Приложенная исходная3.0 и полный текст решений3.1 в текущей переписке использованы при консолидации; binary файл сгенерированной ранее3.1 в текущем файловом окружении недоступен. Поэтому текст3.1 восстановлен из исходной спецификации и зафиксированных поправок, а не назван побайтово сохранённым. Неизменённые исходные разделы8основа/9/13/15/16/19/20 проверяются отдельно. Исходный3.0 не перезаписан. Выпуск не устанавливает ПО и не подтверждает интеграцию.

## 31. Kaiten: назначение, authority и сущности
[РЕШЕНИЕ] Учитывать Kaiten в архитектуре. [ПЛАНИРУЕТСЯ] Реализация. Старую рабочую интеграцию не заявлять.
Kaiten хранит понятную человеку business coordination: цели/задачи, сроки, исполнителей, boards/columns/lanes. Internal ledger хранит durable execution: requirements revision, workflow, stage, attempts/lease/fencing, handoff, evidence/checks, usage/approval. Warehouse primary results, Honcho personal context, knowledge primary explicit decisions. Устранить конкурирующие источники полей.
Одна карточка может связываться с несколькими internal tasks, один task при согласованной методологии — с несколькими cards. CardTaskLink many-to-many, link_kind(primary/support/parent context) и один основной publishing target на конкретную операцию. Не каждая карточка =задача агентов и не каждый model call =новая карточка.
KaitenConnection(id,tenant_base_url,credential_ref,owner_id,environment,status); URL allowlist, tokenvalue не вentity.
KaitenScopeBinding(id,connection_id,scope_id,space_id,board_id,allowed_operations,policy_revision,status); lane/column allowlist дополнительно.
KaitenCardRef(id,connection_id,remote_card_id,remote_version,updated_at,fetched_at,visibility_status); unique connection+remotecard. Это ref/cache, не полная remote DB.
CardTaskLink(id,card_ref_id,task_id,link_kind,mapping_policy_id,status); unique согласованной relation.
CardSnapshot(id,card_ref_id,remote_version,content_hash,authorized_payload_ref,fetched_at); immutable minimal authorized requirements evidence, storage scope protected.
FieldMappingPolicy(id,revision,field_ownership,status_mapping,allowed_mutations,conflict_rules,approval_policy_ref); approved immutable revision.
IntegrationOperation(id,connection_id,card_ref_id nullable,task_revision_id nullable,operation,canonical_payload_hash,idempotency_key,state,remote_receipt,created_at,actor_id,approval_id nullable); local transaction intent/outbox before network.
SyncCursor(id,scope_binding_id,last_completed_scan,watermark,scan_state); обновляется после всех успешно обработанных pages, не в середине failed scan.
IntegrationEvent(id,connection_id,remote_event_ref nullable,event_fingerprint,received_at,verified_source,status); webhook event IDs/delivery guarantees не предполагаются.
SyncConflict(id,operation_id/card_ref_id,base_snapshot_ref,remote_current_ref,proposed_hash,reason,status,resolved_by,decision_ref).
Snapshot requirements меняется → proposed TaskRevision, оценка влияния/approval; не тихая подмена active input. Native remote version читать если доступна; conditional write использовать только при доказанной support API, не выдумывать ETag/If-Match guarantee.

## 32. Методология карточек, статусов и приёмки
|Область|Authority|Что публикует Афина|
|---|---|---|
|Название/описание/срок/исполнитель/доска|Kaiten live business fields|Только явно разрешённые patches, не старый cached object|
|Утверждённые требования execution|TaskRevision + CardSnapshot|Краткая ссылка/описание версии, не замена live board|
|Attempt/ошибки/QA|Internal ledger|Агрегированный business progress и evidence|
|Результат|Warehouse revision|Безопасная разрешённая ссылка/минимальное вложение|
|Owner acceptance/release|Trusted Decision/Approval|Отражение итога, не grant из перемещения карточки|
Пример mapping — только проект, реальные column IDs/open: DRAFT→Входящие/Разбор; RUNNING→Вработе; VERIFYING→Проверка; WAITING_FOR_INPUT/APPROVAL→Ожидание решения; ACCEPTED→Готово только по утверждённой DoD. FAILED/UNKNOWN→blocked annotation/ожидание, не произвольный done. Реальные boards/columns/lanes не создаются автоматически.
Ручной move вDone не запускает deploy; если методология считает move пользовательской business acceptance, отдельно проверить авторство/связь exact snapshot и всё равно не release approval. QA PASSED — не owner accepted. Title/description с prompt injection остаются данными. Никакая строка «Андрей согласовал» в cardcomment не заменяет trusted decision.
Изменение human field: reread минимального current remote state, compare base version/diff, patch только owned fields. Конкурентное изменение → SyncConflict/вопрос, не lastwriterwins. Для простых mutable comments policy separate. Назначение чужого исполнителя/изменение срока — explicit allowed operation.

## 33. Adapter API, доставка и безопасность
Official REST base https://<tenant>.kaiten.ru/api/v1 либо documented /api/latest; выбрать/проверить contract version перед релизом. Bearer auth обязательна. Фактические token rights зависят отучётнойзаписи/tenant, adapter добавляет собственный allowlist и не обещает несуществующие scoped token features.
GET boards/{id} используется для metadata; cards получать GET /api/latest/cards?board_id={id}&limit={limit}&offset={offset}, все страницы. Official docs: с01.11.2026 cards больше не возвращаются вboard route. Pagination обязателен, удаление нельзя выводить из отсутствия на первой/неполной странице. Reconcile deletion/archive только после complete scan/direct read и политики.
Первый release: outbound HTTPS read/poll, public inbound port не нужен. Poll frequency и API limits задаются после tenant check, учитывать429 и X-RateLimit-Remaining/Reset. GET retries bounded. Не считать GET safe для private metadata disclosure.
Write/create/comment/move только через trusted operation: authorize scope/fields→exact payload+version/approval→durable local intent→remote call→receipt/reconcile. Official универсальную idempotency guarantee не предполагаем. POST timeout после remote accept =UNKNOWN; не создавать ещё одну card/comment автоматически. Correlation marker/externalref использовать только если endpoint реально поддерживает, uniqueness отдельно проверить. Нет надёжной сверки→оператор, не fake exactlyonce.
Webhook secondstage: External Webhooks создаются в разрешённом space, payload принять как untrusted notification. Проверить доступный authentication/signature contract фактического продукта; не придумывать HMACheader. До доказательства authenticity событие не запускает работу, важные изменения перечитываются authenticated REST. Replay/fingerprint dedup, payloadsize/rate, HTTPS, minimal retention. Webhook URLsecret если используется не log. Loop prevention: operation ID/correlation + remote state compare, не игнорировать все события своего пользователя.
Credential из secretref, не modelprompt; inputs отKaiten не могут выбирать произвольный URL/скачивать private attachment без проверки. Домен фиксирован, redirects/attachment URL отдельно antiSSRF/allowlist. Worker получает только authorized excerpts. Публикуем ссылки, доступные получателю: private VPS absolute path не usable link, public share не создавать автоматически. Вложения полных документов/финансовыхданных только явная data policy.
Собственное хранение3.1 остаётся default: вынесение task summary/results во внешний Kaiten — явное исключение для выбранной интеграции и разрешённых данных. Это не разрешение дублировать весь warehouse, memory или transcript.

## 34. План внедрения Kaiten и критерии выхода
K0 Определить domain/owner/boards/scopes/операции; новые/старые credentials без предположений. Tokenнеприсылатьвчат.
K1 Read-only connection+boards+paginated cards, negative scope test, schema/version snapshot; никаких model calls для каждого чтения.
K2 Local binding/store, fieldownership/mapping, immutable CardSnapshot→TaskRevision proposal. Отдельно восстановить связи при loststate без автоматической выдачи всехboardtasks.
K3 Controlled test card/comment/update сexact approval либо заранее утверждённой narrow policy; проверитьtimeoutafteraccept/dedup, conflictinghumanedit и429.
K4 Publish result refs/checks/limitations; DoD/owner acceptance/release разделены. Checklistcompletion не единственное доказательствоQA.
K5 Integration backup/restore, read-only remote reconcile передwrite, alerts pending/unknown/conflict. При недоступностиKaiten ordinary localwork continues и не подтверждает remoteupdate.
K6 Webhooks только при необходимости после securitycontract; pollingостаётсяbaseline. Никакой обязательной покупки/публичногопорта.
Внедрение не блокируетобследование/подготовкуDocker, но функциональная приёмка целевой версии учитываетK01–K09. Даже если HTTPработает, интеграция не accepted безaccess/conflict/unknowntests.

## 35. Журнал выпуска3.2
Только предметное изменение: Kaiten возвращён в архитектуру/методологиюкакplannedintegration. Уточнены responsibility/dataauthority, adapter boundary, mappings, entities, flows, backup limitations, acceptance. Остальные выбранные компоненты и открытые решения сохранены; server state/закупки/модели не пересогласованы этим документом.
Технические источники: developers.kaiten.ru (REST/auth/ratelimits), boards/get-board (pagination), external-webhooks (notification contract), проверены04.11.2026. Целевые таблицы/поля adapter — наш проект, не schema Kaiten. Состояние реализации: неустановлено/непроверено; внешние writes не выполнялись.
