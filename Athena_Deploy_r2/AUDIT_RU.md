# Аудит исходного Athena_Deploy
## Объём и фиксация
Коммит 985d9b1eb6cdc62b7a922188f7ee3cd17589d78f. Deploy_1:16 путей; Deploy_2:22; Deploy_3:11. Всего 49 файлов, вложенных подкаталогов в этих трёх папках нет. 28 уникальных blob SHA прочитаны полностью. Совпадающие SHA означают тождественные Git blobs; это не предположение по имени. Полная ведомость в SOURCE_INVENTORY.csv.
Существующий Deploy_3 — не третья работоспособная версия кода, а частичный пакет документации и дубликатов. compose.core.yaml совпадает во всех трёх папках. prepare_storage.py совпадает в Deploy_2/3; settings.env.example совпадает во всех; две Mermaid-копии идентичны; data.json.example/team.json.example идентичны и запрещают активацию.

## Находки и исправления
|ID|Исходный пробел|Влияние|Решение r2|
|---|---|---|---|
|A01|Плоское расположение, ссылки ./executor, ./scripts, ./database, ./env|Compose не найдёт binds; build context не соответствует инструкции|Единая правильная структура файлов|
|A02|В Deploy_1 отсутствует entrypoint.sh, хотя Dockerfile COPY требует его|Сборка executor невозможна из этой папки|entrypoint в executor/ из Deploy_2 + sshd -t|
|A03|Deploy_3 неполный: отсутствуют Honcho/team/data configs и scripts зависимости|Нельзя объявлять standalone bundle|Все компоненты в одном r2|
|A04|preflight суммирует RAM только одного stage|Каждый проект PASS отдельно, вместе OOM|Aggregate preflight всех выбранных и уже работающих Athena projects + резерв прочих служб|
|A05|prepare_storage проверяет Honcho mount даже для core|Core-only пилот требует отдельной процедурной подготовки|Полный storage script остаётся для полной инфраструктуры; core pilot допускается отдельно с ручной подготовкой только своих каталогов/сетей|
|A06|UUID guard перед Docker представлен комментарием|После reboot можно писать не на ожидаемый том|Root-owned executable guard + systemd drop-in, отдельное согласование|
|A07|safe_path допускает лексический '..'; существующий volume не проверяет Driver/type|Выход из approved tree/чужой volume|Запрет '..'/symlink; exact Driver и Options|
|A08|Shared internal network задана external: true без собственной гарантии Internal|Сеть могла быть создана незащищённой|Проверка actual Docker network policy до допуска|
|A09|Redis allkeys-lru без подтверждения cache-only contract|Возможная потеря нужных записей|Консервативный noeviction; проверка роли Redis обязательна, при OOM command errors/alert, не гарантия durability|
|A10|Deriver только running, без readiness|HTTP200 API не доказывает обработку|Не выдуман HTTP endpoint; backlog/last-success + synthetic derivation gate|
|A11|Catalog/Team остаются контрактами без реализации|Полная команда не запускается от YAML|Сохранена блокировка gate; не добавлен игрушечный сервер|
|A12|Runtime отсутствуют credentials клиента Catalog/Team и verified adapters|Network membership не обеспечивает успешный authenticated API call|Явный release blocker: client adapter + scoped secret loader до активации, credentials не выданы вслепую|
|A13|Voice paths из 3.3 не включены в исходную persistency ведомость|Будущие jobs/rights могут потеряться|Полная матрица persistency, монтирование только при реализации владельца|
|A14|Дублированные ENTRYPOINT/CMD в Dockerfile|Неочевидный effective entrypoint|Одна финальная пара|
|A15|health_http использует assert, GET следует redirects|python -O отключает проверки; риск перенаправления bearer|Явные проверки, no redirects, local-only tunnel, ограничение bytes|
|A16|env/config template не равен accepted upstream schema|Неизвестные опции могут быть игнорированы|Pinned compatibility gate, effective readback, ключ TERMINAL_ENV=ssh явно задан|
|A17|init scripts одноразовы на empty PGDATA|Перезапуск не создаёт отсутствующую роль/extension в старой БД|Никакого повторного init на existing data; отдельная migration/recovery|
|A18|Release gates root600 не являются подписью и обходятся direct compose|Ложное ощущение enforced CD policy|Явно документирована доверенная административная модель, агентам нет docker group/sudo|

## Не выдуманные значения
Не присвоены фиктивные image digests, UUID, основная LLM, Honcho text model IDs, framework CrewAI/CADTopo, voice IDs, бюджеты, retention/RPO/RTO. Это неизвестные параметры либо решения владельца, не факты, которые можно восстановить из YAML.
Обнаруженные в исходном документе характеристики HostHatch — историческая входная запись, не новая проверка сервера. Сведения памяти о Beget не подменяют более новую архитектуру HostHatch.

## Граница исправления
r2 исправляет структуру и задаёт эксплуатационный контракт. Он не реализует Catalog, Team Control, workers, voice ledger, Kaiten adapter, restricted remote dispatcher. Их отсутствие — функциональные blockers, не пропущенная строка Compose.
