# Афина 3.3 — полная спецификация деплоя r2
Дата: 04.11.2026. Основа: полный аудит Athena_Deploy, commit 985d9b1eb6cdc62b7a922188f7ee3cd17589d78f; сверка архитектуры 3.3 из пользовательского Markdown.
Статус: production-oriented candidate, NOT verified production. Документ не является разрешением на изменение сервера или GitHub.

## 1. Решение о размещении
Основная цель актуальной архитектуры — HostHatch/Docker, отдельные Compose проекты core/honcho/data/team. Не переносить core на старый Beget по исторической памяти. Все external bridge networks в этом комплекте действуют только в одном Docker daemon. Если сервисы впоследствии разносятся по VPS, этот комплект требует отдельного ADR: private VPN transport, TLS/auth, адреса, ACL, firewall, другие endpoint bindings. Docker external network сама по себе не соединяет серверы.
Core — личная Афина независимо от команды; Honcho — отдельная долговременная память; Catalog — независимый владелец склада; Team — операционное состояние и координация. Девять постоянных сервисов: 2+4+1+2. Workers, proxy и опциональный собственный TTS не включены в этот счёт. Логический компонент не обязан быть контейнером.
Один существующий VPN и один выбранный proxy; ничего не устанавливать/заменять вслепую. По умолчанию HTTP endpoints доступны только через loopback/SSH tunnel. Публичный reverse proxy не создаётся без выбранного домена/TLS/auth и проверки existing VPN.

## 2. Факты, предположения, blockers
Из исходного deployment документа: HostHatch Ubuntu24.04 x86_64, 2CPU,7.8GiB RAM, root≈32.6GiB, free≈19GiB, Docker не был найден, dedicated data volume отсутствовал. Это не свежий inventory. Перед любыми изменениями повторить read-only uname/lsblk/findmnt/df/free, проверить Docker/VPN/systemd и provider recovery console. Независимый backup/download/restore — отдельное доказательство; локальный архив не достаточен.
Открытые blockers: утверждённые image digests и исходные release commits; main model/auth; Honcho text models; реальный data UUID; новый RAM/disk capacity; framework ADR; собственные реализации; restore evidence; реальные endpoint/schema/plugin/UID tests. Ни один placeholder не заменяется случайным значением ради PASS.

## 3. Состав готового комплекта
- compose.core.yaml: runtime + SSH executor.
- compose.honcho.yaml: pgvector PostgreSQL15-compatible image, Redis, API, Deriver.
- compose.data.planned.yaml: контракт собственного Catalog; не upstream продукт.
- compose.team.planned.yaml: Project DB + контракт собственного Team Control.
- compose.dashboard.optional.yaml: только overlay core после auth gate.
- executor/: правильный build context, ssh config, server config, entrypoint.
- database/: одноразовая инициализация только новых PGDATA.
- scripts/: aggregate static preflight, storage/key preparation, health wait, passive HTTP, Honcho bootstrap.
- ops/: точная UUID-проверка до Docker autostart; включать отдельным решением.
Шаблоны env, release gates и release manifest не содержат настоящих секретов. Полные YAML находятся в отдельных файлах; они являются нормативной конфигурацией, а не сокращёнными примерами внутри документа.

## 4. Supply chain и совместимость
Каждый production image — registry/repository@sha256:<64hex>. Использовать approved patch release, зафиксировать upstream source commit, architecture x86_64, SBOM/scan evidence, effective config schema. Не latest/main и не rebuild при каждом up. Сначала build/тесты executor, затем promotion того же digest. Локальный image ID не pullable RepoDigest.
Пример сборки после утверждения base image: docker build --build-arg UBUNTU_BASE=<approved Ubuntu24.04 repo@sha256> -t <approved registry/executor:release> executor/. Затем функциональные тесты, push в разрешённый registry и фиксация RepoDigest. APT snapshot не закреплён этим Dockerfile: повторяемость сборки ограничена; deployment повторяет уже принятый digest.
Hermes: сохранить официальный ENTRYPOINT/s6, не ставить generic user/init/read_only без проверки. В r2 explicit TERMINAL_ENV=ssh плюс terminal.backend=ssh; проверить effective backend, иначе исполнение может оказаться local. HERMES_UID/GID=10000 — требование к конкретному release, проверить реальный UID. Платные и вспомогательные зависимости bake в принятый образ; runtime lazy installs выключить.
Honcho: bootstrap ожидает /app/.venv/bin/python, /app/docker/entrypoint.sh, src.deriver, DB_CONNECTION_URI, CACHE_URL и env schema исходного комплекта. Проверить всё по pinned source и effective readback; текущий upstream main не доказательство совместимости выбранного образа. API startup migrations остаются штатными для этого release. Не выносить несуществующую migrate-команду ради красивого depends_on.

## 5. Постоянное хранение
|Host path|Container path|Writer|Backup|
|---|---|---|---|
|state/hermes/default|/opt/data|одна authority Hermes|обязательно, config/auth/state.db/native memory|
|state/executor/inputs|/inputs RO|trusted staging, не runner|исходники либо воспроизводимый manifest|
|work/jobs/personal-default|/workspace RW|runner10000|неопубликованные результаты до проверки|
|state/executor/home|/home/runner|runner10000|назначенные зависимости/нужное состояние|
|honcho-data/postgres|/var/lib/postgresql/data|PostgreSQL|consistent dump+full image|
|honcho-data/redis|/data|Redis|в составе full image и recovery contract|
|state/catalog|/state|Catalog10000|SQLite consistent snapshot+manifest|
|warehouse|/warehouse|Catalog/publisher|все retained artifact revisions|
|control/db|/var/lib/postgresql/data|Project DB|dump+full image|
|state/team|/state|TeamControl10000|attempt/leases/receipts по реализации|
|workshop/workspaces|/work|TeamControl в scoped boundary|пока незавершённые работы/retention|
|control/governance/approved|/governance RO|trusted operator|обязательно|
|state/voice|ещё не mounted; contract владельца|trusted controller|jobs/selection/budget/receipts|
|model-assets/voice|ещё не mounted; RO reader|trusted asset publisher|reference/transcript/rights/manifests|
|work/tts|ещё не mounted; scoped job scratch|TTS adapter/controller|до safe publish, не долговечный cache|
|warehouse/media/generated/tts|через Catalog/publication|Catalog|retained audio по policy|
|/etc/athena/secrets|адресные /run/secrets либо env_file|администратор|зашифрованная независимая копия|
Пути таблицы относительны /srv/athena, кроме /etc. Voice paths не объявляются используемыми, пока нет реализации/точного mount contract. Native Edge pilot использует штатное Hermes home; долговечные принятые аудио нужно публиковать через контролируемую процедуру.
Bind create_host_path:false обязателен. Долговечные данные не в container writable layer и не в /tmp tmpfs. /inputs не весь warehouse. Не монтировать /srv, /home хоста, Hermes home, Docker socket в executor. Существующие права не переписываются chown -R. Новый пустой executor home/work —10000:10000; inputs RO с читаемыми runner файлами. DB/Redis UID определить по accepted image, не hardcode999.
External volumes: athena_honcho_pgdata→honcho-data/postgres; athena_honcho_redisdata→honcho-data/redis; athena_team_pgdata→control/db. Driver local, Options exactly type=none,o=bind,device=<approved absolute path>. Именованный volume не backup и не доказательство отдельного диска.

## 6. Dedicated filesystem и reboot safety
Honcho data — отдельная смонтированная FS с exact UUID. 100GiB — прежний проектный ориентир, не факт покупки. Сначала inventory и подтверждение владельцем устройства; mkfs/wipefs/resize не входят в пакет.
После подготовки FS администратором mount по UUID, подтвердить findmnt --mountpoint /srv/athena/honcho-data -o UUID,SOURCE,FSTYPE,OPTIONS. До mkdir проверяется exact UUID. При отсутствии тома stop, не создавать новую пустую БД на root.
prepare_storage.py проверяет mount до каталогов/networks/volumes. Он не меняет диски, не мигрирует existing volumes, не исправляет mismatch автоматически. Сбой частичной подготовки не откатывает уже созданные объекты: разбор и повтор только после review.
Для автозапуска: установить root-owned executable ops/check-data-mount как /usr/local/sbin/check-athena-data-mount, root600 /etc/athena/storage-guard.env с настоящим UUID, затем предложенный systemd drop-in. Не source env в root shell: guard читает только две строки. Проверка запускается ДО Docker restart policy.
Включение drop-in влияет на все Docker workloads и, возможно, VPN. Только отдельное owner approval, доступная provider console, проверка systemd unit и безопасное окно. Не делать daemon restart в рамках выпуска документа. Потеря mount при уже работающем Docker/live-restore — отдельный critical alert и остановка новых записей; ExecStartPre не runtime watchdog.

## 7. Сети и auth
|Network|Участники|Policy|
|---|---|---|
|core executor_rpc|runtime,executor|internal:true; SSH2222, executor no direct internet|
|core runtime_egress|runtime|internet по approved policy|
|athena_memory_api|runtime,Honcho API|external pre-created INTERNAL bridge|
|honcho db|API,Deriver,DB|internal; raw DB недоступна runtime|
|honcho cache|API,Deriver,Redis|internal; no published Redis|
|honcho inference_egress|API,Deriver|OpenRouter/outbound; не domain allowlist|
|athena_catalog_api|runtime,Catalog,TeamControl|internal bridge; authenticated API|
|athena_team_api|runtime,TeamControl|internal bridge; authenticated API|
|team team_db|ProjectDB,TeamControl|internal|
|team team_egress|TeamControl|outbound по approval|
Host ports только 127.0.0.1:8642,127.0.0.1:18000; dashboard override добавляет127.0.0.1:9119. DB/Redis/executor/Catalog/Team не публикуются. YAML expose не является firewall rule. Internal bridge не per-user ACL и не защита от trusted host/Docker admin.
Runtime multihomed имеет egress, может обращаться к своим API networks; поэтому нужны live scopes и API auth. Запрет egress executor проверять на IPv4/IPv6 и доступ к host gateways, а не только один curl. Internal network сама по себе не доказывает полную изоляцию от хоста; default host-management ports закрыть отдельной reviewed policy, не ломая SSH/VPN. Никаких blanket firewall commands.
DNS/TLS провайдеров доступны только разрешённым internet clients. Строгий domain allowlist требует отдельного egress proxy/firewall и негативных тестов. Не заявлять, что он реализован этим bridge.

## 8. Секреты и границы исполнения
settings.env/env/*.env mode600; /etc/athena/secrets root0700; dedicated admin/app DB credentials. App роли NOSUPERUSER/NOCREATEDB/NOCREATEROLE. В пилоте app владеет своей DB ради штатных миграций; разделение migrator/runtime role — отдельная проверенная миграция grants, не слепое ужесточение.
Compose file secrets на standalone host не шифруют файл; host metadata имеет значение. Client private key owner10000 mode600 для Hermes; executor host key root600. Public authorized/known hosts0644. Генерация идемпотентно запрещает overwrite; host key pin строится из локального public key, не доверяет network keyscan.
Core runtime не получает DB passwords Honcho/Team; executor не получает provider/Kaiten/Catalog keys. Hermes env_file делает provider/API key видимыми доверенному runtime и host/Docker admin: это не vault. Не выводить docker inspect/config env в чат или CI logs.
Catalog/Team client credentials и adapters в runtime ещё не реализованы исходниками. Сначала scoped client contract/secret loader/auth-denial tests; затем минимальные адресные secrets в отдельном accepted override. Не раздавать signingsecret как user JWT и не добавлять все будущие ключи runtime заранее.
Executor persistent personal scope: один active job до реализации scheduler/leases. MaxSessions2 и persistent_shell:false не являются scheduler. Незнакомые проекты/attempts требуют отдельных scopes/instances, не одного общего writable workspace. root sshd supervisor, команды runnerUID10000; проверить capabilities реального child. Альтернативные browser/audio/file tools могут выполняться вне terminal backend: до проверки отключены.

## 9. Ресурсный план и admission
Исходные caps: core3GiB; Honcho6GiB; Catalog0.5GiB; Team2GiB. Полный static caps11.5GiB + минимум2GiB ОС + прочие службы + workers. На7.8GiB это BLOCKED; даже Honcho6+2 требует отдельной оценки и не проходит такой консервативный cap admission. Full16GiB — ориентир до workers, не закупочная рекомендация и не доказательство достаточности CPU/disk.
CPU caps сумма6.25CPU по шаблону не reservation и не гарантия физического CPU. Ограничения pids/tmpfs заданы по сервисам. Суммарная RAM должна учитывать реальные proxy/VPN/monitoring/соседние контейнеры; OTHER_WORKLOAD_GIB заполнить на основании inventory. Swap не считать заменой RAM в admission.
python3 scripts/preflight.py core honcho data team проверяет совокупность и требует включить уже работающие Athena projects. Он проверяет static caps, не симулирует пики/throughput. Реальный нагрузочный тест отдельно; на Docker-free машине script закономерно BLOCKED.
Root capacity считать для image layers/build cache/logs/сохранённых releases/backup staging отдельно от dedicated data. До изменений: df -h,df -i,docker system df если Docker есть. Не prune ради прохождения. Watermarks/retention/RPO/RTO назначает владелец; не выдуманы 7/30 дней.

## 10. Honcho и Redis
Выбор embeddings сохраняется: openai/text-embedding-3-large через OpenRouter, output1536. Single+batch тест выполняется именно Honcho client, не только отдельным curl; подтвердить dimension реального stored vector, отсутствие silent provider/model fallback. Main Hermes provider отдельный.
Все текстовые модели Honcho явно выбраны владельцем и проверены на каждом модуле: Deriver,Summary,Dream,Dialectic levels. Один API process и Deriver worker на первом этапе. Auth enabled; JWT scope проверить на двух синтетических privacy domains. Один external sender Hermes; не добавить второй sync daemon.
Redis AOF everysec и external volume сохраняются. r2 noeviction — предосторожность, не подтверждение cache/queue semantics. При maxmemory записи могут возвращать ошибку; мониторинг/handling обязателен. Подтвердить upstream Redis role, требуемые TTL, восстановимость и maxmemory headroom/AOF rewrite. Если требуется cache eviction, новая reviewed policy; если durable queue, отдельный durability/replay contract. Redis не второй primary памяти.
Init scripts создают app role/extensions только в новом пустом PGDATA. Existing DB не инициализируется заново, не менять owner автоматически. PG major upgrade требует pg_upgrade/dump-restore plan. API startup выполняет release migrations одним владельцем; передача данных и фоновые writers запрещены до проверки schema head.

## 11. Health и readiness
Healthchecks не обращаются к платным моделям.
- executor: ssh-keyscan15s/timeout5/retries10 — только sshd слушает; E2E SSH auth/UID/изоляция отдельны.
- runtime: /health20s/timeout5/retries9/start90 — только liveness; detailed/capabilities/auth/model/config отдельно.
- PostgreSQL: pg_isready10s/timeout5/retries18/start60 — не app grants/schema/vector readiness.
- Redis: ping10s/timeout3/retries12 — не durability/queue correctness.
- Honcho API: /health15s/timeout5/retries12/start60 — не derived/recall-ready.
- Deriver: upstream HTTP server не предполагается. Liveness процесса + внешние last-success/backlog age/functional derivation checks. Не навязывать API healthcheck общему image.
- Catalog/Team: /opt/athena/bin/healthcheck ready — ОБЯЗАТЕЛЬНЫЙ ИНТЕРФЕЙС НАШЕГО будущего image, не уже существующий binary.
HTTP check script предназначен только для localhost через доверенный SSH tunnel, не следует redirects, не печатает body/token, имеет bounded bytes. Schema endpoints/status требуют pinned contract test; неизвестный schema BLOCKED. Readiness paid path проверяется отдельным approved synthetic smoke, не периодическим paid health.
Docker unhealthy сам по себе не вызывает restart unless-stopped. Внешний watchdog/alert обязателен; controlled recovery не должен повторно платить/публиковать. depends_on service_healthy задаёт порядок внутри проекта; не бизнес-транзакцию и не оркестрацию между проектами. wait_service.py ждёт конкретный сервис, но не подменяет acceptance gate.

## 12. Порядок установки
Любые команды ниже — runbook ДЛЯ УТВЕРЖДЁННОГО АДМИНИСТРАТОРА после backup/console/change approval, не выполненные действия.
1. Fresh inventory, независимая скачанная копия и проверенное восстановление; подтвердить VPN и административный SSH путь.
2. Approve capacity и dedicated filesystem; проверить mountUUID; approved Docker Engine/Compose install по ОС и проверка existing services. Не curl|sh из этого комплекта.
3. Разместить reviewed release root-owned в выбранном deployment directory, запретить агенту менять privileged scripts. Архив не распаковывать поверх действующего deployment без diff.
4. Создать settings.env из example, нужные env/*.env, mode600; реальные secrets через приватный канал. Никаких source settings.env в root shell и секретов в Git.
5. Подготовить все mounts/networks/volumes: sudo python3 scripts/prepare_storage.py --apply --independent-backup-confirmed. Флаг — утверждение оператора, не автоматическое доказательство backup. Затем approved UID ownership только новых пустых каталогов.
6. sudo bash scripts/prepare_executor_keys.sh --apply; проверить metadata и client readability реальным Hermes UID. Утвердить и установить boot UUID guard ДО включения restartable stateful containers.
7. Pin/test image compatibility; заполнить release manifest; сгенерировать native Hermes config/setup штатным release в этом же persistent home с одним writer. Не запускать одновременно setup и gateway. Readback/config validation/main model/auth; хранить auth в persistent home.
8. Preflight всех одновременно планируемых проектов, затем pull. Compose config --quiet локально; не публиковать rendered config с env secrets.
Core-only пилот без Honcho volume: не запускать full prepare_storage. Администратор отдельно готовит только home/inputs/work/home и три internal API networks, проверяет их actual policy; этот исключительный bootstrap не объявляет готовым full storage.

## 13. Первый запуск и rollout
Все команды из корня принятого release. Сначала preflight выбранной совокупности. Отдельные проекты не складывать через -f, иначе создаётся другой project model.
```sh
python3 scripts/preflight.py core
docker compose --env-file settings.env -f compose.core.yaml pull
docker compose --env-file settings.env -f compose.core.yaml up -d executor
python3 scripts/wait_service.py core executor
docker compose --env-file settings.env -f compose.core.yaml up -d runtime
python3 scripts/wait_service.py core runtime
```
Проверить config/doctor, authenticated HTTP и actual main model; SSH из user Hermes: ssh -F /etc/ssh/ssh_config runner@executor id. В docker exec указать фактический непривилегированный user accepted image, не root. Synthetic проверки: UID10000, /inputs no-write, workspaceRW, host/Hermes/provider secrets не видны, неожиданные сети недоступны. Root docker exec не доказательство агентских прав.
Honcho отдельно после aggregate RAM admission:
```sh
python3 scripts/preflight.py core honcho
docker compose --env-file settings.env -f compose.honcho.yaml pull
docker compose --env-file settings.env -f compose.honcho.yaml up -d database redis
python3 scripts/wait_service.py honcho database
python3 scripts/wait_service.py honcho redis
# Проверка extensions/app role/password/schema bootstrap; затем API migrations:
docker compose --env-file settings.env -f compose.honcho.yaml up -d api
python3 scripts/wait_service.py honcho api
# Оператор подтверждает migration head, auth/appDB/embedding client compatibility.
docker compose --env-file settings.env -f compose.honcho.yaml up -d deriver
```
Не использовать full up как обход промежуточных gates. API /health не доказывает schema head: проверить штатным pinned migration tooling, exact command закрепить в compatibility evidence. Не выдумывать CLI, которого ещё не сверяли. Smoke message→derive→new-session recall→correction→scope-denial; лишь затем enable Hermes Honcho plugin и исключить cloud fallback/двойной sender.
Catalog: только после настоящей реализации/миграций/auth/storage tests, root600 gate data.json с точным image digest и evidence; preflight core honcho data, затем pull/up catalog и wait. Team: отдельный accepted framework/worker provisioning ADR, root gate team.json; aggregate preflight; project-db→healthy→одна принятая migration operation→team-control→ready→отдельно проверенные workers.
Автоподъём workers не реализован. Не выдавать TeamControl docker.sock/host shell для компенсации. Catalog/Team функциональная готовность проверяется клиентом без Hermes. Обычный диалог не зависит жёстко от Team DB/Kaiten.
Обновление: запретить новые jobs→drain/зафиксировать intents→stop writers→consistent backup→один migration owner→API/schema tests→deriver→clients→workers. После Docker daemon restart порядок Compose повторно не оркестрируется: приложение обязано retry/backoff/reconnect безопасно, а supervisor runtime — не replay внешних эффектов.

## 14. Voice, Kaiten, dashboard
Сначала native Edge/Svetlana по фактическому accepted adapter. Edge внешняя обработка, не offline. Общий voice controller/job/billing/selection store ещё не реализован; .env flags не создают monthly ledger. Paid profiles OFF до выбранного voice/account/model/budget и одного разрешённого preview. Нельзя тихо переключить paid provider при отказе.
Отдельно тестировать decode/ffprobe/OpusOGG/Telegram receipt/text fallback; доставка не запускает повторный синтез. Один владелец автоозвучки, голос не дублирует canonical turn Honcho. Voice rights/assets входят в backup. Native config пример не заменяет selector с CAS/per-chat scope.
Kaiten read-first adapter planned: credentials только trusted boundary, pagination/scope/conflict/UNKNOWN/reconcile gates. Card Done не release approval. Public webhook не обязателен; outbound polling достаточно для первого accepted integration. Реализация отсутствует в audited folder.
Dashboard default OFF. После credentials/route tests применять только core+dashboard overlay; Compose merge сохраняет основной API port и добавляет dashboard port. Перед up проверить config --quiet и diff, остановить активную задачу: runtime может пересоздаться. Доступ через SSH/VPN; public mode требует отдельного поддерживаемого auth/TLS/forwarded headers/CORS плана. Не включать CORS*.

## 15. Логи, мониторинг, остановка
Docker local10m×5/compress — размерная ротация, не дни retention. Native Hermes logs/container-boot.log, journal, proxy, PG WAL и artifacts имеют отдельный рост. Не запускать внешний logrotate на Docker-managed log files. Не писать raw prompts/SQL/text/audio/providererror bodies/Authorization.
Read-only наблюдение: compose ps/logs --since30m --tail200; docker stats --no-stream; df -h;df -i;docker system df. Не вставлять секретные логи в чат.
Alerts: missingmount/UUID, disk+inode watermarks, OOM/restartburst, unhealthy, derivation backlog/age,last-success, DBconnections/WAL, provider rate errors/cost/UNKNOWN, job leases, backup freshness/restore failure,TLS/key expiry. Полный отказ VPS выявляет внешний watchdog с проверенной доставкой. Числовые пороги фиксируются после baseline в operations policy; daemon logs сами не уведомляют.
Остановка: admission закрыть→workers drain→team-control→catalog publication drain→runtime writers→deriver→Honcho API→DB/Redis. Использовать compose stop с grace periods, не kill по умолчанию; catalog/team jobs согласовать так, чтобы не обрубать публикацию активного результата. При аварии сохранять receipts/UNKNOWN; не объявлять успешный task failed из-за TTS.

## 16. Backup и restore
Сохраняется решение ежедневного full image00:00 Europe/Moscow→Windows→Kingston. План должен охватить root+dedicated Honcho+все прочие нужные FS, а не только provider root snapshot. DB consistency обеспечить согласованной остановкой writers/DB или доказанным snapshot protocol; crash-consistent образ не выдавать за проверенное восстановление. Расписание и retention ещё не установлены этим пакетом.
До upgrade: dump обеих PG databases, roles/extensions/schema heads, exact release/config/images, secrets в защищённом виде; SQLite online backup либо quiescent copy владельцем. Не cp живой SQLite вместе с недостающим WAL. Backup staging не включать рекурсивно в следующий capture. SHA256/list archive не actual restore.
Restore в изолированном окружении: сеть внешних эффектов OFF, verify mounts/UUID, восстановить primary данные/config/secrets/accepted image versions, проверить PG roles/extensions/schema, восстановить Hermes sole home, synthetic memory и artifact checks. Reconcile remote Kaiten/paid TTS/delivery UNKNOWN read-first, не replay outbox из backup автоматически. Только затем вручную разрешить реальные каналы/записи.
Rollback image только при backward-compatible schema. При несовместимости восстановить прежнюю БД в отдельную изоляцию; image downgrade не откатывает миграции/списания/доставки. Никогда down -v, volume prune, destructive init в штатном runbook. Числовые RPO/RTO/retention согласовать; замер restore drill записать в evidence.

## 17. Приёмка и статус
Нормативная матрица — ACCEPTANCE_RU.md. Все runtime tests сейчас NOT_TESTED. Local static tests: VALIDATION_REPORT.json. YAML parsing/PythonAST/bash -n не означают Docker Compose validation, запуск sshd, совместимость env, DB migrations, paid calls или restore.
Полный production принимается только после всех обязательных gates и owner approval exact manifest. Допускается отдельно accepted core pilot без приписывания ему готовых команды, памяти, selector или Kaiten. Подписанный provenance и restricted remote CD не заменяются root600 JSON.

## 18. Публичные первичные ссылки
Docker Compose startup: https://docs.docker.com/compose/how-tos/startup-order/
Docker services: https://docs.docker.com/reference/compose-file/services/
Hermes Docker: https://hermes-agent.nousresearch.com/docs/user-guide/docker
Hermes env: https://hermes-agent.nousresearch.com/docs/reference/environment-variables
Honcho upstream example: https://github.com/plastic-labs/honcho/blob/main/docker-compose.yml.example
Honcho changelog: https://github.com/plastic-labs/honcho/blob/main/CHANGELOG.md
Документация online проверена поиском; она не подменяет pin конкретного accepted image.
