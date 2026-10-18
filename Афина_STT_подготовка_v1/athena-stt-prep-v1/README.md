# Афина: подготовка локального STT, v1 — НА РАССМОТРЕНИЕ

**Сборка, установка, загрузка модели, тест распознавания и переключение НЕ выполнены.**
Этот пакет создаёт только проекты файлов. Прежняя конфигурация и gateway не изменены.

## 1. Уточнение архитектуры

Базовый образ: `nousresearch/hermes-agent@sha256:9774f4f39a9bb8c2f68ce728ed5e99ddbad282163be56764afacf88ed952b784`. Вместо замены библиотек рабочего Python — изолированный
`/opt/athena-stt/venv` внутри производного образа. Hermes вызывает его штатным
`local_command` и `HERMES_LOCAL_STT_COMMAND`. Это уточнение предложенной архитектуры,
НЕ молчаливый переход к другому способу: просим отдельно принять именно этот адаптер.
Так PyAV/CTranslate2 не подменяют версии других инструментов Hermes. Родительские
ENTRYPOINT/CMD и пользователь образа сохраняются; в gateway не добавляются права.
Поддержку команды и её протокол необходимо сверить с исходником ИМЕННО закреплённого
образа через preflight: актуальная документация/main не доказывает тождество версии.

## 2. PyAV: установленная причина риска

faster-whisper v1.2.1 вызывает `av.open(..., metadata_errors="ignore")`.
В PyAV 19.0.0 удалены `metadata_encoding` и `metadata_errors` из `av.open`.
Неограниченное `av>=11` может поэтому установить несовместимый API. Выбран строгий
pin `av==16.1.0`, у которого API ниже границы удаления; готовый CPython 3.14 Linux x86_64
wheel найден в PyPI. Это **статическое подтверждение API/тегов wheel, НЕ доказательство
успешного распознавания нашего образа**. Набор нельзя называть проверенным runtime,
пока тесты после отдельного разрешения не пройдут.

Основные pins: faster-whisper 1.2.1; av 16.1.0; ctranslate2 4.6.2; onnxruntime 1.24.1;
numpy 2.3.4; huggingface-hub 0.36.0; tokenizers 0.22.1. Полное замыкание: requirements.lock,
точные версии и SHA-256 wheel; `dependency-evidence.json` содержит PyPI URL и активные
зависимости. Не выполнялись pip install, Docker build или скачивание весов.
Сборка с --only-binary и --require-hashes остановится, а не станет компилировать зависимости
или выбирать непроверенные новые версии. pip check выполняется в будущем образе.
Дополнительный runtime-тест обязателен: наличие wheel не гарантирует работу CPU/AVX/glibc.

Первичные источники:
- https://raw.githubusercontent.com/SYSTRAN/faster-whisper/v1.2.1/faster_whisper/audio.py
- https://raw.githubusercontent.com/PyAV-Org/PyAV/main/CHANGELOG.rst
- https://pypi.org/pypi/av/16.1.0/json
- https://pypi.org/pypi/faster-whisper/1.2.1/json
- https://hermes-agent.nousresearch.com/docs/user-guide/features/tts/
- https://raw.githubusercontent.com/NousResearch/hermes-agent/main/tools/transcription_local.py

## 3. Подготовка на VPS без сборки и переключения

Разместить распакованный пакет в `/srv/hermes-agent/athena-stt-prep-v1`.
Контекст сборки — ТОЛЬКО `build-context/`, семь разрешённых файлов плюс .dockerignore.
Не использовать `/srv/hermes-agent` как build context. Fixtures, backups и рабочие
секреты не включаются в образ. .dockerignore — whitelist.

Разрешённая диагностическая команда:
```
cd /srv/hermes-agent/athena-stt-prep-v1
sudo python3 preflight.py
```
Она читает метаданные образа и identity PID7; выводит только признаки baked credentials,
пользователя образа, UID/GID процесса, boolean allow_lazy_installs и исходники выбора
backend. Токены и значения env не печатаются. PID7 проверяется по назначению.
Фактический UID/GID gateway и allow_lazy_installs из текущего исполнителя пока НЕ
установлены; UID10000 SSH-исполнителя не используется как замена.
Если allow_lazy_installs не распознан, значение помечено NOT_ESTABLISHED; default
не угадывается. Ни один подготовленный файл его не включает. Командный backend
использует готовое окружение и не вызывает глобальную автоустановку Whisper.

**СТОП GATE A:** владелец сверяет исходник local_command из digest, identity, разрешения
выполнения команд и текущую политику lazy install. Если backend/выполнение команды
запрещены — не отключать approvals/deny, а вернуть вопрос владельцу.

## 4. После ОТДЕЛЬНОГО разрешения: сборка

```
ATHENA_APPROVE_BUILD=YES bash build.sh
```
Сеть нужна только для Python wheel. Основной образ фиксирован digest; он уже имеется
на VPS. В процессе сборки секреты не монтируются. Производный образ не запускает gateway
на build. Финальный USER восстанавливается из Config.User базового образа, не из догадки.
Готовая изолированная venv и runner доступны на чтение/исполнение без расширения прав
рабочего процесса. Изменения .venv Hermes/PM, security и approvals не делаются.

## 5. После ОТДЕЛЬНОГО разрешения: кэш и модель

Из preflight взять effective UID/GID gateway (`Uid[1]`, `Gid[1]`), не пользователя сборки.
В командах ниже `<UID>`/`<GID>` — обязательные подстановки после наблюдения, не значения
по умолчанию. Создаётся только новый выделенный каталог; рекурсивный chown рабочих
директорий ЗАПРЕЩЁН. Если каталог уже существует, сначала проверить владельца/содержимое.

```
sudo install -d -m 0750 -o <UID> -g <GID> /srv/hermes-agent/athena-stt-cache
export GATEWAY_UID=<UID> GATEWAY_GID=<GID>
ATHENA_APPROVE_DOWNLOAD=YES bash test.sh download
```
Это отдельный docker run, НЕ Compose: нет env_file, токенов Telegram/OpenAI, Docker socket,
SSH-ключей, каталога `/var/lib/hermes`, production volumes или gateway entrypoint.
Если исходный образ содержит baked credentials, preflight останавливает процедуру.
Контейнер скачивания получает только RW-монтирование нового кэша и сетевой доступ к
публичному Hugging Face. Аудио в него не монтируется. Веса Systran/faster-whisper-base
закреплены revision `ebe41f70d5b6dfa9166e2c581c45c9c0cfc57b66`. Скрипт пишет manifest с SHA-256 весов.
Скачивание выполняется под тем же UID/GID, что gateway. При отказе доступа не выполнять
chmod777 и не менять владельца общих каталогов.

## 6. Настоящее распознавание — до переключения

В пакет включён реальный `jfk.flac` из тестов faster-whisper v1.2.1, происхождение,
точный URL и SHA-256 — fixtures/provenance.json. Это английский отрывок речи JFK,
не синтетический голос и не запись Андрея. Скачан только этот публичный fixture;
модель и зависимости не скачивались. Он проверяет распознавание, но не качество русского.

```
ATHENA_APPROVE_TEST=YES bash test.sh offline
```
Тестовый контейнер: --network=none, --entrypoint изолированный Python, exact UID/GID,
--cap-drop=ALL, no-new-privileges, readonly root, временный /tmp, 2 CPU и 2 GiB.
Кэш и fixtures монтируются read-only. Секреты/рабочий каталог не монтируются.
Проверяются ВСЕ версии, checksum записи и модели, чтение кэша, настоящий decode+VAD+
inference, принудительное потребление ленивого генератора segments и две известные
фразы в результате. Выполняется второй проход из существующего offline кэша.
FAIL на нехватке памяти/времени не обходится увеличением лимитов без согласования.
Факт успешного прямого теста не равен успешной доставке Telegram.

**СТОП GATE B:** распознавание должно пройти под рабочим UID/GID. Затем обязательна
изолированная проверка штатного Hermes local_command на том же fixture в новом образе;
её запуск пока не включён автоматически, поскольку контракт закреплённой версии
local_command ещё не предоставлен полностью. Не считать этап принятым только по
прямому faster-whisper-тесту. Сборка/модель/тесты ещё не выполнялись.

## 7. STT-diff и сохранение прочих параметров

STT.diff — точный семантический целевой набор, НЕ фактический unified diff неизвестного
живого config.yaml. Целевой блок — stt-target.yaml. security/остальные секции не меняются.
config_transaction.py заменяет только top-level stt-блок и сохраняет всё остальное
побайтово; при inline-YAML, aliases, документах или дубликатах останавливается.
Он сознательно заменяет весь STT-блок. Возможные старые STT timeout/настройки также
заменятся: ДО переключения нужен просмотр фактического diff с маскированием секретов.
Если надо сохранить дополнительные STT-поля, target корректируется до согласования.
Полную конфигурацию/backup в чат НЕ присылать; backup содержит возможные секреты.

## 8. После успешных тестов и ОТДЕЛЬНОГО согласования: переключение

Перед применением проверить владельцу способ автоматического запуска/обновления Compose.
Он пока не установлен: Docker restart-policy сохраняет существующий контейнер после
перезапуска daemon, но host unit/скрипт может пересоздать его без STT override.
До выяснения нельзя объявить постоянное развёртывание завершённым. Существующие
файлы не переписываются. При будущем пересоздании нужен четвёртый Compose-файл.

Сначала при отдельном согласовании создать новый каталог транзакций (0700):
```
sudo install -d -m 0700 /srv/hermes-agent/athena-stt-backups
export BACKUP_DIR=/srv/hermes-agent/athena-stt-backups/transaction-001
ATHENA_APPROVE_SWITCH=YES bash switch.sh
```
Транзакция сохраняет исходный config с mode0600 и SHA-256, атомарно применяет STT-блок,
затем запускает точную команду:
```
sudo docker compose \
 -f /srv/hermes-agent/compose.telegram.yaml \
 -f /srv/hermes-agent/compose.telegram.workspace.yaml \
 -f /srv/hermes-agent/compose.telegram.executor.yaml \
 -f /srv/hermes-agent/athena-stt-prep-v1/compose.telegram.stt.yaml \
 up -d --no-deps --no-build --pull never --force-recreate gateway
```
Dashboard и executor не пересоздаются; gateway кратковременно недоступен.
Override добавляет только новый образ, команду локального распознавания и readonly кэш.
Он не меняет user, groups, capabilities, approvals или security.allow_lazy_installs.
До запуска сверить sha образа/тесты; после запуска проверить actual UID/GID, backend,
передачу контрольного русского голосового и точную расшифровку. Старую ошибку не
объявлять установленной задним числом. Тест после reboot не выполнялся.

## 9. Откат ОБРАЗА И КОНФИГУРАЦИИ

```
ATHENA_APPROVE_SWITCH=YES bash rollback.sh
```
Использовать тот же BACKUP_DIR. Скрипт сначала восстанавливает точные исходные bytes
config, только если текущий SHA совпадает с применённым; при последующих правках
останавливается вместо стирания новой работы. Затем выполняет up только с тремя
исходными Compose-файлами (без STT override), возвращая исходный digest.
Рабочие данные, кэш, образы и записи НЕ удаляются. Смена образа без отката STT запрещена.
Если после атомарной замены config gateway держит старый bind отдельного файла,
force-recreate переподключает его; в данном случае смонтирован каталог Hermes целиком.
Если compose up при переключении дал ошибку — не заявлять успех, выполнить откат при
том же разрешении. Отдельный запуск rollback предусмотрен и после частичного apply.
После отката подтвердить старый image ID и SHA конфигурации; статус Running не
является проверкой голоса.

## 10. Честный статус подготовки

Выполнено сейчас: подготовлены файлы; получены первичные API/metadata; pins и SHA wheel;
публичный audio fixture; статические проверки файлов и транзакции на искусственных
конфигах. НЕ выполнены: Docker build, установка пакетов, загрузка весов, реальный ASR,
проверка в gateway, фактический allow_lazy_installs и runtime UID/GID, автозапуск хоста.
Требование «проверенный совместимый набор» в смысле runtime пока НЕ закрыто: его
невозможно честно подтвердить без отдельно согласованной сборки/теста. Не смешивать
статический API-анализ с успешным распознаванием. Требование фактического unified diff
и Hermes adapter integration test также остаётся gate до переключения.
