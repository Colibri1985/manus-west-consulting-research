# Афина STT v2 — подготовка на просмотр, НЕ сборка/переключение

Архитектура сохранена: производный образ от прежнего digest, изолированная venv,
local_command, мультиязычная base. Зависимости и модель из v1 не обновлялись.
Ничего не установлено, модель не загружена, Docker не запускался. Текущий gateway и
конфиг не менялись. В архиве нет успехов тестов, которых ещё не было.

## Состав и воспроизводимость архива

build-context/.dockerignore — реальный файл в ZIP, а не только запись в тексте.
В имеющейся у исполнителя v1-копии ZIP он тоже присутствует; причина его отсутствия
после передачи/распаковки владельцу не установлена. В v2 проверены точные имена ZIP.
MANIFEST перечисляет ВСЕ поставляемые файлы, кроме самого MANIFEST (во избежание
рекурсивного хэша); архив проверяется на равенство набора и каждого SHA-256.
prepare_bundle.py намеренно НЕ поставляется и НЕ перечислен. Это служебный генератор
v1, а не команда сборки образа. Воспроизводимые команды — Dockerfile/build.sh/control.py;
все необходимые им файлы включены. Архив включает fixtures отдельно от build context.
Внутри build context whitelist .dockerignore; ни workspace, ни /srv/hermes-agent целиком
в контекст не передаются. Runtime receipts хранятся ВНЕ пакета и образа.

## Подтверждение закреплённой версии

См. CONTRACT_AND_PERMISSIONS.md и evidence/base-image/. Код получен из публичных слоёв
точного manifest, а не из main. Проверены digest index, platform manifest и compressed
layer SHA. Runtime сравнит исходники выбранной ветки с этими хэшами: при изменении
живого /opt/hermes тест остановится. Не путать index digest9774... с Docker image ID373d....
Поддержка placeholder/выходного txt/error/timeout подтверждена чтением этого кода.

## Pins и несовместимость PyAV

faster-whisper1.2.1 вызывает metadata_errors в av.open; PyAV19 удалил этот аргумент.
Pin av16.1.0 сохранён. Полные26pins с wheel hashes в requirements.lock и versions.json.
PyPI metadata/API и wheel tags проверены, runtime совместимость — ЕЩЁ НЕТ.
Первичные ссылки см. dependency-evidence.json и прежние исходники:
https://raw.githubusercontent.com/SYSTRAN/faster-whisper/v1.2.1/faster_whisper/audio.py
https://raw.githubusercontent.com/PyAV-Org/PyAV/main/CHANGELOG.rst

## Важные ограничения производительности/изоляции

Runner на КАЖДЫЙ вызов создаёт процесс и загружает модель. Второй проход повторно
использует файлы кэша, но НЕ загруженную модель. Это не тёплый inference и задержку
надо измерять. Демон/пул не добавлялся: архитектура не переделана.
Python audit hook — дополнительный сигнал, НЕ гарантия сетевой изоляции нативного кода.
Реальная изоляция теста — Docker --network=none. В рабочем gateway вся сеть не выключается,
поскольку нужны Telegram/LLM; поэтому абсолютная OS-гарантия офлайна runner в production
не заявляется. Runner использует только локальный путь модели и local_files_only=True.
Строгий per-process egress контроль был бы отдельным согласованным изменением.

## Этапы. Сейчас НИЧЕГО из них не выполнялось на VPS

Сначала распаковать пакет в /srv/hermes-agent/athena-stt-prep-v2 при отдельном разрешении.
Полезно проверить скрытые файлы не средствами просмотра, скрывающими dotfiles.
Все команды ниже — будущая процедура, НЕ поручение выполнить их сейчас.

### A. Адресный preflight (чтение текущей политики, не общая диагностика)

После отдельного разрешения:
```
cd /srv/hermes-agent/athena-stt-prep-v2
sudo env ATHENA_APPROVE_PREFLIGHT=YES python3 control.py preflight
```
Он получает эффективные UID/GID/существующие группы PID7, bool security.allow_lazy_installs,
эффективный запрет PM (с учётом HERMES_DISABLE_LAZY_INSTALLS) и hash рабочего config.
Секреты/полный env/config не выводятся. config loader защищён от файловых изменений;
пропускается только mkdir(exist_ok=True) существующего каталога. Если loader пытается
реально писать/ходить в сеть — пробник фиксирует блокировку, а не обходится.
Результат сохраняется в /srv/hermes-agent/athena-stt-state/v2/preflight.json mode0600.
Если глобальная автоустановка НЕ подтверждена отключённой, дальнейшие этапы блокируются;
скрипт сам её не отключает и не включает. Важна политика, а не произвольный bool.

### B. Сборка — отдельное разрешение

```
ATHENA_APPROVE_BUILD=YES bash build.sh
```
Сборка использует ТОЛЬКО build-context; проверяет manifest и preflight, восстанавливает
пользователя исходного образа, не трогает Python/PM Hermes. Сеть нужна для pinned wheel.
Тег образа v2; ему присваивается label с fingerprint всех build inputs.

### C. Модель — отдельное разрешение

Взять effective UID/GID из preflight. Значения <UID>/<GID> ниже не выдуманы и требуют
подстановки наблюдаемых чисел. Для НОВОГО каталога (существующий не chown-ить рекурсивно):
```
sudo install -d -m 0750 -o <UID> -g <GID> /srv/hermes-agent/athena-stt-cache
ATHENA_APPROVE_DOWNLOAD=YES bash test.sh download
```
Download container без production mounts/секретов/fixtures/gateway entrypoint.
Только dedicated cache RW; пользователь gateway; сеть для публичного HF.
Модель Systran/faster-whisper-base закреплена revision из download_model.py;
файлы и их SHA фиксируются в model-manifest.json.

### D. Два теста — отдельное разрешение на исполнение

```
ATHENA_APPROVE_TEST=YES bash test.sh direct
ATHENA_APPROVE_TEST=YES bash test.sh integration
```
Оба запускаются docker run по точному image ID (не изменяемому тегу), --network=none,
readonly root/cache/fixtures, cap-dropALL, no-new-privileges, tmpfs/tmp, 2CPU/2GiB.
ENTRYPOINT явно заменён Python; нет Telegram gateway, env-file, API-ключей, Docker socket,
рабочего каталога Hermes. Только код Hermes из образа и synthetic config в памяти теста.
Прямой тест проверяет26версий и реальный inference два раза. Интеграционный тест:
Hermes public transcribe_audio → local_command → реальный runner → txt → Hermes result.
Тестовая запись — публичный upstream jfk.flac, v1.2.1, английская речь JFK; происхождение
и hash в fixtures/provenance.json. Это НЕ проверка качества русского; русский clip нужен
после отдельного переключения или отдельно предоставленный локальный файл до него.

Успехи записываются host-контроллером в direct.json/integration.json вне пакета. Запись
создаётся только после exit0 и единственного валидного test result; перед новой попыткой
старый PASS инвалидируется. Receipts связаны с точным imageID, build-input fingerprint,
package manifest SHA, preflight SHA, UID/GID, fixtureSHA и modelmanifestSHA. Перед switch
перепроверяются ВСЕ файлы весов, а не только JSON manifest. Изменённый пакет, образ,
config, Compose, модель или неуспешный тест → отказ. Это защита от случайной подмены,
не криптографическая защита от администратора root, способного переписать receipts.

### E. Проверка допуска без переключения

```
sudo python3 control.py gate
```
До успешных тестов это ОБЯЗАНО завершиться STOP. Сборка и download не считаются PASS.
Gate также требует неизменности прежних Compose/config и прежний образ рабочего gateway.

### F. Switch — только после отдельного согласования

STT-target сохраняет прежнюю архитектуру. config_transaction.py меняет только top-level
STT, остальные bytes не меняет; перед этим backup0700/config0600 и hashes. Необычный YAML
останавливает операцию. STT.diff — семантический diff, не выданный за фактический diff
неизвестного конфига. До согласования надо просмотреть реальные STT-поля: замена блока
может удалить другие старые STT-настройки. security/approvals не меняются.

Сначала учесть четвёртый файл в ПОСТОЯННОЙ процедуре запуска/обновления. Её настройка
на VPS пока не проверена/не менялась. Docker restart policy существующего контейнера
не гарантирует правильное пересоздание сторонним host unit/скриптом.

После согласования создать родительский каталог backup, затем:
```
sudo install -d -m 0700 /srv/hermes-agent/athena-stt-backups
export BACKUP_DIR=/srv/hermes-agent/athena-stt-backups/v2-transaction-001
ATHENA_APPROVE_SWITCH=YES ATHENA_FOURTH_COMPOSE_REVIEWED=YES bash switch.sh
```
Gate проверяется ДО любого изменения config. После apply создаётся четвёртый файл
$BACKUP_DIR/compose.tested-image.yaml: он равен просмотренному override, но тег заменён
точным протестированным image ID. Это исключает tag-race при up. Постоянная процедура
должна использовать ИМЕННО этот четвёртый файл:
```
sudo docker compose \
 -f /srv/hermes-agent/compose.telegram.yaml \
 -f /srv/hermes-agent/compose.telegram.workspace.yaml \
 -f /srv/hermes-agent/compose.telegram.executor.yaml \
 -f "$BACKUP_DIR/compose.tested-image.yaml" \
 up -d --no-deps --no-build --pull never --force-recreate gateway
```
Dashboard/executor не пересоздаются. После switch проверить UID/backend и русский voice.
Running≠успешное распознавание. Проверка после перезагрузки сервера не выполнялась.

### G. Откат после ошибки — РУЧНОЙ

Скрипт switch НЕ обещает автоматический rollback. При ошибке после apply — выполнить
следующую команду с ТЕМ ЖЕ BACKUP_DIR по согласованному разрешению:
```
ATHENA_APPROVE_SWITCH=YES bash rollback.sh
```
Сначала точные старые bytes config (если после switch не было посторонних правок),
затем up с ТРЕМЯ исходными Compose, без четвёртого файла. Проверяется старый imageID.
Если config менялся — отказ, нужна адресная ручная сверка, новая работа не стирается.
Также вернуть постоянную host-процедуру на три исходных файла; сам rollback.sh host
unit не меняет. Кэш, рабочие данные и образы не удаляются.

## Текущий статус

Статически подтверждён контракт именно digest и маршрут subprocess/очистки env.
Подготовлены интеграционный тест и fail-closed gate. Фактические UID/policy живого
процесса и выполнение под ними всё ещё требуют будущего preflight/test; по текущему
запрету на VPS они НЕ проверялись. Нет fabricated PASS/receipt. Это ограничение честно
сохраняется, не заменяется утверждением «все разрешения проверены».
