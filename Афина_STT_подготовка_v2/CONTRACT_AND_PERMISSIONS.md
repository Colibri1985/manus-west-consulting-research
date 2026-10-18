# Контракт и адресная проверка local_command — закреплённый образ

Исследование выполнено без запуска контейнера: через Docker Registry v2 прочитаны
публичные manifest и слои. SHA-256 compressed layers сверены с manifest. Образ не
собирался и не запускался. В production VPS ничего не выполнялось этим сбором.

- Index digest: `sha256:9774f4f39a9bb8c2f68ce728ed5e99ddbad282163be56764afacf88ed952b784`.
- Linux/amd64 manifest: `sha256:ffa4fbb471c2bc8c85fbcfc629347585cc1586c86d2e6db465d01203ce696d95`.
- Config / точный Docker image ID: `sha256:373ddd5e6649f525b17993e1c885cdf1352127f8e98fd329140a73237125e52f`.
- Index digest и image ID — РАЗНЫЕ идентификаторы; v1 сравнение исправлено.
- Родительский image USER: root. Это не доказывает effective UID процесса gateway,
  который может быть понижен entrypoint. Никакой UID исполнителя не подставляется.

## Подтверждённый код

`tools/transcription_local.py`, `_get_local_command_template`, строки 62–72:
сначала HERMES_LOCAL_STT_COMMAND. `_transcribe_local_command`, строки 298–344:
placeholders ровно input_path, output_dir, language, model; значения shell-quoted,
затем shlex.split -> subprocess, без shell=True. Шаблон нашего адаптера использует
первые три; base закреплена в пути модели самого runner и в STT.local.model.
`_prepare_local_audio` возвращает исходный WAV/поддерживаемый формат или временный WAV
через ffmpeg; ошибки препроцессинга возвращаются до запуска runner.

Результат — первый по сортировке `*.txt` в выделенном output_dir; чтение utf-8-sig,
strip. Не stdout. Отсутствие txt — success=False. Ненулевой exit — Local STT failed.
Неверный placeholder — отдельная ошибка. TimeoutExpired попадает в общий except,
возвращая Local transcription failed. Штатный код не гарантирует отказ на пустом txt;
наш runner не создаёт успешный пустой transcript. Семантика исходника не меняется.

`tools/transcription_audio.py`, `_run_quiet`, строки 44–50: subprocess.run с check=True,
capture_output, stdin=DEVNULL, utf8. Тайм-аут runner — 300 секунд; условная конвертация
ffmpeg имеет собственный timeout300. Это НЕ единый end-to-end deadline300.

`tools/transcription_tools.py`, `_EXPLICIT_RESOLVERS` 230–233, `_route_stt_provider`
522–531: local_command — встроенный provider и штатная ветка вызова. Маршрут не
переопределяется пользовательским command-provider. `transcribe_audio` проверяет вход,
включая file safety, и затем маршрутизирует. Integration test вызывает именно его.

## Какие проверки разрешений завершены, какие нет

**Статически завершено по digest:** в выбранной ветке нет обращения к terminal-tool,
approvals, sudo, Docker socket или PM ensure_import. `_run_quiet` напрямую запускает
заданную администратором команду. Это НЕ означает, что всем командам агента разрешён
запуск; разрешение terminal tool — другая граница. Скрипт не меняет approvals/deny.
`hermes_subprocess_env(inherit_credentials=False)` очищает окружение ребёнка. Собственные
секреты в образ/runner не добавляются.

Runner — Python-файл, требует R_OK, не chmod+x; исполнитель /opt/athena-stt/venv/bin/python
требует X_OK. Build и тесты проверяют это адресно. Кэш — read-only на inference;
для загрузки отдельный контейнер получает только этот кэш RW. UID/GID и фактическая
возможность запуска/чтения обязаны подтвердиться integration test без новых прав.
Группы в тест копируются только из уже существующих supplementary groups процесса.

**Не проверено сейчас:** effective UID/GID живого gateway, live security.allow_lazy_installs,
политика LSM/seccomp на VPS, исполнение adapter на целевом сервере. Пробник preflight
подготовлен, но по запрету ничего не запускалось на VPS. Он использует штатный merged
readonly loader, PM lazy_installs_allowed и audit запрет записи/сети, фиксирует любые
помехи. Неоднозначный результат блокирует дальнейшие этапы.

Из закреплённого pm/install.py 164–193: HERMES_DISABLE_LAZY_INSTALLS=1/true/yes запрещает
lazy installs; иначе bool security.allow_lazy_installs читается штатно (default=True
именно в ЭТОМ коде), ошибки чтения fail-closed. Наличие default не доказывает live value.
В новых тестовых контейнерах env-флаг явно равен1; рабочий параметр НЕ меняется.

## Интеграционная проверка

`integration_test.py` запускается Python Hermes, а не STT venv. Синтетический STT config
подаётся в памяти только теста. Исходные transcribe_audio, dispatch, template rendering,
subprocess и чтение txt НЕ подменены. Реальный публичный fixture проходит Whisper base.
Дополнительно реальные subprocess проверяют stdout без txt и exit7; неверный placeholder
проверяется исходным кодом; для timeout инъецируется TimeoutExpired и проверяется
передача300 (это не реальное ожидание300сек). Рабочая конфигурация и Telegram отсутствуют.

**Результаты:** тест добавлен, но не запускался: сборка/модель/исполнение не согласованы.
Прямой тест и integration выдадут отдельные receipts. До этого switch обязан отказать.
