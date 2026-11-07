# Известные замечания к внешнему Athena_Deploy_r2
Этот FINAL — документальная архитектура, НЕ исправленный deployment bundle. Внешние файлы GitHub не изменены.
Источник: Colibri1985/manus-west-consulting-research commit 504c0520f5f53a6bc1faa18cef5e03704909c245.
D33-001: прежний HANDOFF говорит 34 файла, перечисленное дерево содержит 33. Не объявлять E0 завершённым до сверки exact archive; не создавать фиктивный 34-й файл.
D33-002: старые ACCEPTANCE_RU.md/VALIDATION_REPORT.json/SOURCE_INVENTORY.csv отсутствуют в перечисленном tree. Contracts/Acceptance_Tests.csv и Validation_Report.json ЭТОГО выпуска — новые records, не доказательство наличия тех файлов и не runtime tests.
D33-003: preflight core не проверяет merged dashboard overlay/env. Dashboard OFF. При отдельном включении нужны local rendered merged config, dashboard secret placeholders/readability, auth/loopback/recipient/port checks; не публиковать секретный config.
D33-004: core preflight не доказывает root ownership всего deployment/parent directories. Отдельно проверить trusted ownership, отсутствие agent/group/other write, symlink chain и защищённость всех root-executed scripts. Не расширять права агента.
D33-005: 8 без Catalog, 9 с Catalog; не runtime inventory. Уточнено в архитектуре, новых контейнеров это не вводит.
Эти notices не исправляют код preflight. Host/Docker/Compose/build/schema/network tests NOT_RUN. Отсутствующие возможности controlled voice/Team/Catalog не блокируют разрешённый ограниченный Core, но не объявляются реализованными.
