# Афина — переключаемые голосовые профили, VOICE-1.0
04.11.2026. Конфигурационная заготовка, сервер не изменён. Включает нативный Hermes TTS-фрагмент и минимальный adapter whole-file synthesis; никаких платных API calls не выполнено.

## Файлы и применение
1. config.tts.yaml — только tts-секция. Слить с config.yaml выбранного Hermes profile; не перезаписывать весь config и не создавать второй tts ключ.
2. voice_profiles.yaml — наш проектный реестр для будущего selector/UI. Hermes не читает его сам. active_profile здесь — описание, а не действующий switch. Фактический выбор сейчас tts.provider в config.yaml.
3. voice.env.example — ключи и отдельный gate платного TTS. Слить в runtime environment/профильный .env, chmod600. Глобально не передавать ключи executor.
4. tts_adapter.py — установить в управляемый image по /opt/athena/voice/tts_adapter.py RO. Command provider должен видеть Python3/скрипт. Не вносить package installs в работающий runtime вручную. CLI принимает path, не текст в shell command.

## Профили и switch
Светлана: tts.provider: edge (начальный безопасный по расходам профиль, не офлайн).
ElevenLabs: tts.provider: athena_elevenlabs. Требуются реальный voice ID, OpenRouter key, paid gate=true, утверждённый бюджет и smoke.
Fish: tts.provider: athena_fish. Резервный будущий профиль, НЕ уже выбранный сервис; нужны реальный model/reference ID, key и разрешение затрат.
Выключение голоса через штатный speech toggle выбранного интерфейса Hermes; не выдумывать provider:none.
Переключение применяется после проверки readback и поддерживаемого config reload/restart. Hot switch без restart и отдельный выбор на чат не заявлены готовыми. Одна выбранная настройка относится к profile; granularity chat требует собственного selector/state.
Модель ElevenLabs v4 Turbo — ранее предложенный стартовый кандидат. ID/доступность/voice надо подтвердить на account до оплаты. Fish model специально placeholder: его выбор не совершён автоматически. Direct Fish и Fish через OpenRouter разные routes, их keys/IDs не взаимозаменяемы.

## Почему command providers
Hermes документирует tts.providers.<custom-name>, env_passthrough и voice_compatible. Не подменять built-in names. Edge использует встроенный adapter. ElevenLabs через OpenRouter и Fish direct возвращают MP3. Hermes с ffmpeg преобразует MP3 в Opus/OGG для Telegram voice. Output format должен совпадать с реальным codec; ffprobe проверить отдельно.
Нет второй очереди, отдельного постоянного контейнера или изменения STT. Вход и выход TTS одинаковы. Whole-file mode выбран первым; настоящий realtime PCM streaming — последующий plugin, не имитация shell stream.

## Предлагаемые guards и ограничения
ATHENA_PAID_TTS_ENABLED=false по умолчанию. Adapter отклоняет невыбранный voice/model/пустой key. Передача только текста для произнесения, без памяти и hidden instructions. Keys читаются только из env и явно разрешены env_passthrough, в argv не передаются. Сырые provider error bodies не выдаются агенту. No automatic retry: timeout может означать уже оплаченный запрос.
timeout90s — idle timeout native command runner; HTTP timeout60s — socket-operation bound, не строгий общий SLA. 4000chars — предлагаемый per-request cap, не monthly cap. Финансовый hard budget/лимиты параллельности/approval paid usage отдельно по runtime/provider доступным средствам, здесь не реализованы.
MP3 MIME+nonempty проверяется, но codec не доказан. Для production добавить checked ffprobe/decode и synthetic delivery. Fail text-only и отсутствие silent voice fallback — целевая политика общего runtime, не уже реализованный selector. При provider error Hermes tool получает typed failure; сохранение видимого текстового ответа проверяется отдельно.
Новый direct Fish API имеет server fallback на default model при неизвестном header, поэтому adapter whitelist проверяет model ДО сети и не отправляет неизвестные IDs. Этот guard не отменяет необходимости проверить account rights и тариф.

## Короткая приёмка
Проверить pinned Hermes command-provider API, наличие python3/ffmpeg/libopus и Edge dependency. Проверить Svetlana actual voice list. Затем разрешить один короткий paid ElevenLabs test, voice/codec/Telegram; текст ответа не теряется при error/key missing. Fish не тестировать до отдельного выбора. На смене profile текущую запись не обрывать; future UI должен фиксировать snapshot профиля на каждый reply.
Проверить наличие/отсутствие secret canaries в child environment: env_passthrough не объявляется полной OS isolation. Command template — trusted local code с правами runtime. Не дать пользователю/карточке менять endpoint/argv.

## Источники
https://hermes-agent.nousresearch.com/docs/user-guide/features/tts
https://openrouter.ai/docs/guides/overview/multimodal/tts
https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech
Все файлы созданы локально; syntax/guards проверены offline. Hermes/provider SDK не запускался, network/TTS calls отсутствуют. Main config и deployment3.2 не перезаписаны.
