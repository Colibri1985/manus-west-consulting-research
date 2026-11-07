# Афина 2.0 — передача в тред деплоя и порядок применения материалов

Редакция HANDOFF-DEPLOY-001 r1. Дата: 05.11.2026.
Назначение: самостоятельная контрольная точка для нового разговора по развёртыванию. Это порядок подготовки, а не разрешение автоматически исполнить все изменения.

## 1. Главные правила нового треда

1. Архитектура обсуждается отдельно. Новый тред отвечает за состояние сервера, конкретные config/code changes, команды, тесты, backup/restore и эксплуатацию.
2. Не начинать с docker compose up. Сначала сверить фактическое состояние, recovery, ресурсы, storage, принятые profiles и образа.
3. Предложено / выполнено / прочитано обратно / функционально проверено / принято — разные статусы. Удачная генерация документа или YAML не означает установленную функцию.
4. Команды выдавать маленькими цельными блоками с явным местом выполнения: Windows PowerShell, Ubuntu WSL или SSH HostHatch. Один блок → результат → решение о следующем.
5. До изменяющего действия назвать цель, затронутые файлы/сервисы/сети, возможный простой, проверку результата и путь отката; получить конкретное согласование, если его ещё нет.
6. Оригиналы, рабочие настройки, SSH keys, backups, пользовательские файлы не удалять/не перемещать/не перезаписывать без отдельного разрешения. Предпочитать копию и отдельный новый release directory.
7. Не выводить в чат secrets, auth.json, .env values, private keys или raw confidential dumps. Настройки реальных credentials — локально приватным способом.
8. Если существующая backup/cloud/provider функция ограничена, говорить об этом явно. Не компенсировать отказ памяти скрытой записью в MEMORY.md, skills, notes или иной store.
9. Не выдавать агенту Docker socket, blanket sudo/root shell или unrestricted host management ради удобства установки.
10. Новому треду передать артефакты явно. Нельзя полагаться, что он автоматически получил ZIP/PDF, temporary files и все детали этой беседы.

## 2. Какой документ применять и когда

| Приоритет/материал | Что определяет | Момент использования |
|---|---|---|
| Явные актуальные решения владельца | Утверждённые границы и объём конкретного действия | На каждом шаге; отсутствие ответа не approval |
| ACP-SEC-001 r2 | Действующая уточнённая security policy: managed autonomy, profiles, exclusions, phasing | До выбора settings/routes и при всех implementation changes |
| Архитектура 3.3 | Целевые функции, owners и boundaries компонентов | При планировании всего deployment и его этапов |
| Athena_Deploy_r2.zip | Compose/scripts/templates — candidate implementation | Только после проверки применимости к ACP r2, release/image compatibility и storage |
| DEPLOYMENT_SPEC_RU.md внутри ZIP | Runbook кандидата, требования к путям/UUID/ресурсам | Пошагово, с учётом более нового ACP r2; не весь документ как автоматический script |
| SEC-MODEL-REVIEW-001 r1 | Основание модели, утверждённой 05.11.2026 12:52 MSK | Для трассируемости/уточнения; не установочный компонент |
| ACP r1 / security reference v1.4 / старые briefings | История и rationale | Не применять противоречащие ACP r2 требования как обязательный стартовый gate |

ACP r2 не заменяет функциональную 3.3; 3.3 не отменяет новый security profile. При обнаружении реального противоречия остановить только затронутый шаг и вынести его владельцу/в архитектурный тред. Не выбирать молча старый более жёсткий или более свободный вариант.

### Различать два r2
- Athena_Deploy_r2.zip — версия deployment-кандидата.
- ACP-SEC-001 r2 — версия документа решений по безопасности.
Совпадение суффикса r2 не означает, что архив был обновлён по новой policy. Единого deployment release с подтверждёнными изменениями ACP r2 ещё не выпускали.

## 3. Какие артефакты приложить в новый тред

Минимум:
1. Athena_Deploy_r2.zip — сам архив с 34 файлами, не только ссылку/название.
2. ACP-SEC-001 r2 — PDF или ZIP (в ZIP PDF/MD/CSV/MMD).
3. Архитектуру 3.3 в Markdown — для функций и границ.
4. Этот HANDOFF-DEPLOY-001 r1.

SEC-MODEL-REVIEW-001 r1 можно приложить как дополнительное основание, но объединять его bytes с Compose не нужно. Архив резервной копии и секреты в чат не загружать. Из backup при необходимости передавать только safe diagnostics, checksums и scope.

Если перечисленные исходники в новом треде отсутствуют — сначала запросить их, а не реконструировать deployment scripts по памяти и выдавать это за точную копию.

## 4. Подтверждённое состояние, а не предположение

### HostHatch
- SSH-user: andreym; системное имя в последнем выводе: claude-vps. Используется привычное подключение VS Code Remote — SSH.
- Сохранённый адрес из прошлой истории: 85.155.184.29; перед использованием сверить с текущей панелью/рабочей SSH-записью. Не менять SSH config вслепую.
- В панели выбран тариф: 4 CPU (2 dedicated + 2 fair-shared), 16 GB RAM, 75 GB NVMe. Применение ресурсов внутри гостевой ОС НЕ подтверждено.
- Последний присланный inventory: 2026-11-04T21:37:02+00:00 = 05.11.2026 00:37 MSK. Ubuntu 24.04.5 LTS, x86_64, KVM; nproc=2; RAM=7.8 GiB; swap=0.
- Диск vda=32.6 GiB; vda1 ext4 около31.6 GiB под /; root filesystem около31 GiB, занято13 GiB, свободно19 GiB.
- Отдельного диска/filesystem Honcho в показанном inventory нет.
- Docker требует корректной повторной проверки: предыдущий shell if/else введён с ошибкой; вывод не считать полным подтверждением текущего состояния.
- Перезапуск для применения upgrade, расширение раздела/filesystem, установка Docker, создание data volume, переименование и deployment не подтверждены как выполненные.

### Windows / WSL
- GnuPG и Kleopatra установлены на Windows; скачанная backup успешно расшифрована.
- WSL list: docker-desktop Stopped VERSION2; Ubuntu-24.04 Stopped VERSION2.
- Предложен запуск обычной Ubuntu с bash --noprofile --norc и проверка id/df/tar/gzip/python3/stat. Вывод запуска/диагностики ещё не получен.
- Ничего не распаковывать в root действующей Ubuntu, /etc, /home или /root. docker-desktop не использовать для restore drill.

## 5. Резервная копия: уже сделано и что ещё осталось

Папка Windows:
D:\Афина — резервная копия HostHatch — 2026-11-04

Скачаны:
- hosthatch-predeploy.tar.gz.gpg
- packages.tsv
- SCOPE.txt
- SHA256SUMS.txt

Зашифрованный archive: 246385954 bytes.
SHA256: 76dff1b1c37895016382706648b66f34b0df4f0e3978cc03142845f706dbe9af
SCOPE.txt SHA256: da8195c07bae20781ca7cf0140bd12745dc758abe302f0c330328243e6f4836d
packages.tsv SHA256: d927acba221c4a6652e64aee431170efb6fb032c67902e9b7b1a63360b6fda98
Все три фактические суммы на Windows совпали с сохранённым SHA256SUMS.txt. Это сверка с manifest, не отдельно выполненный в этой части разговора новый hash серверного оригинала.

Расшифровка Kleopatra успешна; отсутствие подписи отмечено как отсутствие проверки авторства, не ошибка расшифровки. Сохранён hosthatch-predeploy.tar.gz: 246277263 bytes. Оригинал .gpg сохранён.

Windows tar.exe -tzf завершился с TAR_LIST_EXIT_CODE=0.
В списке13674 archive entries. Проверены True для etc/, home/, root/, srv/, usr/local/, var/spool/cron/, etc/passwd, etc/fstab, etc/ssh/sshd_config, home/andreym/.

SCOPE:
TYPE: selected-files pre-deployment backup; NOT full VPS image
INCLUDED: /etc /home /root /srv /usr/local /var/spool/cron
EXCLUDED: this backup directory, VS Code Server, listed caches

НЕ выполнено/не подтверждено:
- пробное извлечение в Linux filesystem;
- сохранение/проверка Unix metadata на восстановленных файлах;
- рабочее восстановление системы;
- полный образ всех дисков;
- актуальная проверка server original hash и перечня текущих изменений после backup.

Не называть эту копию full-image и не просить скачивать её повторно без причины. До серьёзных изменений подтвердить recovery console и согласовать достаточный recovery plan: протестированная файловая копия + проверенный полный backup/snapshot с известным охватом либо отдельное явное принятие владельцем оставшегося recovery risk. Provider root-only snapshot не выдавать за backup всех дисков.

## 6. Действующие security rules ACP r2

- Black: значения secrets не AI/context/memory/ordinary logs; affected packet stopped. Credentials используют адресно разрешённые workloads по отдельным auth bindings.
- Red: обязательный local-only/запрет external processing. Если нет approved isolated backend, affected task blocked/deferred, не cloud fallback. Свой VPS не автоматически trusted local inference.
- Yellow: разрешённый непубличный personal/work scope для approved cloud profiles; без обезличивания каждого имени и approval каждого запроса.
- Green: обычная approved processing; не отменяет grants, budgets и gated actions.
- «Не запоминать»: не Honcho и не скрытый alternate store. «Не сохранять содержимое вообще»: отдельное более строгое требование; поддержку history/cache/channel/provider проверить, не обещать абсолютную тишину.
- Honcho исключает secrets, «не запоминать», local-only, данные без права передачи, полные dumps/logs/environment «на всякий случай».
- В разрешённой памяти обычные имена людей, проекты и рабочие связи не вырезаются автоматически.
- Fixed models per function. Основная LLM, Honcho text models, embeddings, STT/TTS могут быть разными статическими назначениями. Нет automatic role/complexity/local-cloud model selection.
- Little LLM Gate и draft/speculative decoding отложены. Gateway позже отдельным этапом; не prerequisite штатного Honcho.
- Cloud memory/audio risk принят по типу и scope, но exact new models/routes/credentials/retention/paid budgets ещё заполняются до подключения. Никакого unlimited spending.
- Failure памяти/voice отражается честно. Accepted memory message не равно derived/recall-ready.

## 7. Порядок реального развёртывания: stage gates

### E0. Приём исходников и baseline
Действия: проверить actual ZIP content; сохранить исходный скачанный ZIP без изменения; сверить 34-file tree; отделить документы от executable configs.
Результат: перечень источников/версий; нет подмены scripts реконструкцией.
STOP: отсутствует исходник, конфликт versions или неподтверждённая структура.

### E1. Завершить проверку recovery copy
Действия: продолжить именно с WSL Ubuntu диагностики; проверить свободное Linux space, формат/размер распаковки и безопасные archive paths/types/links. Согласовать отдельный закрытый пустой restore-test directory; original .gpg и .tar.gz не изменять. Не применять root extraction к живому filesystem.
Результат: извлечение/выборочная проверка metadata и важных восстановленных файлов; ни один файл/скрипт из backup не запускать автоматически.
STOP: checksum/decryption/archive errors, unsafe paths, недостаточно места, неясный recovery coverage. Решение о полном backup/остаточном риске — явно до рискованных операций.

### E2. Новый read-only inventory HostHatch
Действия: подтвердить target server/panel identity и рабочий SSH; OS/CPU/RAM/disks/mounts/space/inodes; Docker version/Compose/containers/daemon config, существующие VPN/proxy/listeners/services.
Результат: фактическое текущее состояние. Не делать вывод о new16GB по одной панели.
STOP: wrong target, отсутствие console/recovery, неучтённые службы, неожиданные mounts.

### E3. Применение тарифа и проверка диска
Действия: если ресурсы старые, сверить provider pending-upgrade instructions и согласовать штатное применение/перезапуск с console fallback; затем повторить inventory. Отличать размер block device, partition и filesystem. Expansion — только после фактической разметки и отдельного одобренного плана.
Результат: OS видит принятые ресурсы; disk/FS размеры известны.
STOP: не выбирать Reinstall/Delete/Reset; не запускать mkfs/wipefs/resize/growpart наугад.

### E4. Выбор storage и protection plan
Действия: решить размещение Honcho persistent FS, images/logs и других stores; подтвердить устройство/UUID/ёмкость/backup coverage. Нынешний bundle ожидает dedicated Honcho filesystem и UUID. Если отдельного тома нет — выбрать обеспечивающий требование вариант или согласовать отдельное архитектурное изменение; не подставлять root UUID ради PASS.
Результат: storage plan и approved paths/ownership. Перед autoboot stateful containers — согласованный mount/UUID guard.
STOP: неизвестное устройство, absent mount, mismatch UUID, inadequate capacity. Systemd Docker guard может затронуть все containers/VPN — отдельный change window.

### E5. Уточнение deployment candidate под ACP r2
Действия: diff-check actual configs; определить точные поддерживаемые versions/images/digests и native schemas/hooks/auth. Main LLM/provider и Honcho text IDs выбрать отдельно. Сохранять штатный Hermes ENTRYPOINT/s6; не добавлять generic user/init/read_only без compatibility proof.
Результат: reviewed implementation-candidate manifest + список разрешённых edits/точечных adapter changes + rollback.
STOP: placeholders, фиктивные digests, unsupported native config keys, конфликт новой policy. Не пытаться сейчас внедрить gateway/Little/draft ради формального соответствия старому ACP r1.

### E6. Bootstrap host dependencies и release directory
Действия: после конкретного approval установить/проверить Docker Engine/Compose, если отсутствуют; existing daemon/VPN не переустанавливать. Разместить reviewed release в новом каталоге с правильными подпапками. Не распаковывать поверх прежней установки без diff.
Результат: Docker/Compose и unmanaged workloads известны; files соответствуют paths; agent не может менять privileged deployment code.
STOP: installer conflict, потеря SSH/VPN, неизвестный daemon data-root/permissions. Не давать docker group агенту автоматически.

### E7. Settings, secrets, mounts и networks
Действия: создать settings.env и нужные env/*.env из templates только локально; заполнить accepted digests/resources/paths. Реальные secrets — приватные файлы с verified readability/owners. Подготовить каталоги/volumes/internal API networks/SSH keys согласно approved plan; не переписывать существующие keys.
Результат: отсутствуют REPLACE в используемом stage, реальные mounts/options/UUID проверены, secret access per-service.
ВАЖНО: prepare_storage.py в r2 проверяет Honcho mount и создаёт инфраструктуру нескольких контуров — это не безусловный core-only bootstrap. Не запускать его до E4/E5. Для core-only — отдельная reviewed подготовка. Полный prepare_executor_keys.sh тоже меняет host state и не запускается без согласования.

### E8. Preflight выбранной совокупности
Действия: проверить rendered Compose локально без публикации env/secrets; actual volume/network options; суммарные caps всех одновременно работающих Athena projects + host/other workloads. Зафиксировать stages и approved profile settings.
Результат: static config PASS. Это не proof runtime compatibility или security policy.
STOP: RAM/disk budget, missing secrets/binds, non-loopback unintended ports, wrong mount, unimplemented own component. Не снижать guards/лимиты наугад ради прохождения.

### E9. Core pilot: executor → runtime
Действия: accepted images pull; executor start→health; проверить SSH authentication, actual runner UID, RO inputs/RW work, отсутствие доступа к runtime home/provider secrets/host admin. Затем runtime native setup/readback/model/auth и gateway start в согласованном порядке без двух writers одного profile home.
Результат: synthetic dialog + безопасная личная tool/document task, valid auth/recipient и policy checks.
STOP: wrong backend (local вместо isolated), root agent command, unknown keys/model/auth; alternate browser/file paths не объявлять isolated по одному SSH test.

### E10. Honcho pilot и подключение памяти
Действия: aggregate preflight; database+Redis→healthy; app roles/extensions→API/native migrations→schema compatibility gate→Deriver. Проверить actual embeddings1536 single+batch и нужные text functions. Затем compatible Hermes plugin, один sender, approved memory scope.
Результат: synthetic ingest→accepted→derived→new-session recall/correction и scope denial. Проверить no-memory/local-only exclusions поддерживаемым способом; нет alternate store.
STOP: неизвестные migrations/привилегии, wrong dimensions/route, двойной sync, no proof memory support. Accepted не выдавать за recall-ready.

### E11. Каналы, документы, голос
Действия: channels/allowlists/auth; реальные document workflows и target constraints. Начальный Edge/Svetlana проверить отдельно. STT/TTS paid profiles только после exact route/model/account/budget/retention и approved data scope; synthetic preview → decode/codec/rate/delivery/text fallback.
Результат: рабочие личные функции и явные ограничения без total rebuild.
STOP: неизвестный recipient, unsupported strict no-retention, no paid budget, raw PCM под видом MP3, hidden provider switch, repeat paid synthesis on delivery retry.

### E12. Backup/restore, reboot resilience и release acceptance
Действия: подтвердить persistent-state survive recreate/reboot, mount guard impact, отдельные согласованные backup и independent restore evidence. В архитектуре цель daily full image00:00 Europe/Moscow → Windows → Kingston; ещё не installed schedule. Обеспечить consistency native SQLite/PG и все нужные FS; signed provider backup claims не выдумывать.
Результат: зафиксированный scope/limitations/restore evidence; приёмка Core и/или memory/voice по отдельности, exact release manifest. Реальный state и required remote effects после restore сверяются read-first.
STOP: provider root-only snapshot выдают за all-disks backup; copy живой SQLite/DB объявляют consistent; down -v/volume prune/destructive init в штатной процедуре.

### E13. Каталог, команда, Kaiten — последующие реализации
Catalog/Publisher и Team Control .planned.yaml — контракты, не готовые образы. До реализации нельзя создавать true release gates или подставлять fake image ради up. Framework и worker provisioning ещё открыты; не устанавливать Orca/CrewAI/CADTopo автоматически.
Порядок при готовности: Catalog verified implementation → Project DB → own migrations → TeamControl → separately scoped workers/QA. Kaiten read-first→scope/pagination→approved writes/UNKNOWN/conflict tests. Эти контуры не blocker обычной личной Афины.

### E14. Gateway и сложная модельная оптимизация
Отдельный будущий change: gateway compatibility пилот, static routes, real auth/protocol/retention/budget/logging checks. No automatic routing, Little LLM и draft на ближайшем этапе. Они потребуют нового ADR/approval и своей приёмки, а не будут добавлены попутно.

## 8. Важные ловушки файлов deployment

1. Сохранить одну root папку Athena_Deploy_r2 и предусмотренные config/env/executor/database/scripts/ops/release-gates. Не класть всё плоско.
2. compose.core.yaml, compose.honcho.yaml, compose.data.planned.yaml и compose.team.planned.yaml — независимые проекты. Не складывать все через -f как overrides: имена database/network/paths могут изменить смысл модели.
3. Единственный предусмотренный overlay в этом bundle — core + compose.dashboard.optional.yaml, только после auth/private-route проверки. Это может пересоздать runtime; не во время active job.
4. settings.env.example — инфраструктурный шаблон; settings.env — рабочие substitutions Compose. env/hermes.env и env/honcho.env — runtime environments контейнеров. Нужные механизмы secret-file loading проверяются по image, не предполагаются универсально.
5. Compose secrets на standalone host — адресные file mounts, не автоматически encrypted vault; metadata/readability реально проверить.
6. External named volume сам по себе не dedicated FS/backup. Existing volume Options mismatch — manual migration review, не volume create fix.
7. DB init scripts работают только для нового empty PGDATA. Existing DB не чинится delete/init; major version не менять подключением прежнего PGDATA к новому major.
8. В old docs есть ссылки ACCEPTANCE_RU.md, SOURCE_INVENTORY.csv, VALIDATION_REPORT.json, которых нет в exact34-file ZIP. Не считать их существующими gates/evidence. Подготовить нужные реальные release records явно.
9. Статические AST/bash/YAML tests ZIP не заменяют docker compose config, builds, SSHD/DB startup, negative ACL или restore tests.
10. Per-stage up не подтверждает межпроектный порядок. Healthy process не business readiness. Нужны явные gates между E9/E10/E11.

## 9. Минимальная форма отчёта после каждого шага

- Stage/operation ID и место выполнения.
- Было предложено / согласовано / выполнено.
- Target files/services, observed versions/digests/config revision.
- Safe output, exit codes, actual verification и pending tests.
- Что НЕ выполнялось; остаточные риски/UNKNOWN.
- Backup/rollback record, если были изменения.
- Чёткий следующий шаг без скрытых side effects.

## 10. Готовый текст первого сообщения в новом треде

Продолжаем DEPLOY Афины2.0 на HostHatch. Архитектура обсуждается отдельно. Используй приложенные Athena_Deploy_r2.zip, архитектуру3.3, ACP-SEC-001 r2 и этот HANDOFF. ACP r2 утверждён по SEC-MODEL-REVIEW-001 r1 сообщением 05.11.2026 12:52 MSK. Архив deployment НЕ обновлён автоматически под ACP.

Policy: managed autonomy; fixed models per function; Honcho штатно с exclusions, embedding1536/OpenRouter сохранён. Без automatic model routing, Little LLM и draft; gateway позже. Не спрашивать на каждый permitted cloud request, но новые recipients/purposes/gated actions отдельно. Secrets/local-only/no-memory соблюдать. No hidden alternative memory stores.

Последний подтверждённый HostHatch inventory ещё старый: Ubuntu24.04.5,2CPU,7.8GiB,vda32.6GiB,root≈31GiB/free19GiB. В панели выбран4CPU/16GB/75GB, но применение upgrade НЕ подтверждено. Dedicated Honcho filesystem не обнаружен; Docker перепроверить. Системное имя claude-vps, SSH-user andreym. Рестарт/resize/install/rename/deploy не подтверждены.

Backup уже скачан и расшифрован на Windows. Это selected-files backup, НЕ full image. SHA256 всех3файлов совпали с manifest; tar list exit0,13674entries, ожидаемые paths присутствуют. Пробное Linux extraction ещё не выполнено. Папка D:\Афина — резервная копия HostHatch — 2026-11-04; original .gpg и plain .tar.gz сохранены. WSL Ubuntu-24.04 установлен VERSION2/Stopped; docker-desktop не трогать. Следующий незавершённый шаг — безопасная диагностика обычной WSL Ubuntu и подготовка отдельного restore-test directory, без extraction в живые /etc,/home,/root.

Начни с E0–E1, не с docker compose up. Перед изменениями сверяй фактическое состояние и конкретное approval. Команды маленькими блоками с меткой PowerShell/WSL/SSH, ждать результата. Оригиналы не удалять/не переносить/не перезаписывать; secrets в чат не выводить. Если исходники не доступны, запроси их, не восстанавливай scripts по памяти. Выпуск документов не означает внедрение. Не добавляй future Team/Catalog/gateway components как обязательный стартовый blocker.
