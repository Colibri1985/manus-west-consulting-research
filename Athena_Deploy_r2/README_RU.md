# Athena Deploy r2
Полная спецификация и production-oriented deployment candidate на основе всех файлов Athena_Deploy.
Основание: Colibri1985/Athena, commit 985d9b1eb6cdc62b7a922188f7ee3cd17589d78f.
Все 49 путей в Deploy_1/2/3 рассмотрены; 28 уникальных Git blobs прочитаны; идентичные SHA не читались повторно.

Начать с DEPLOYMENT_SPEC_RU.md, AUDIT_RU.md и ACCEPTANCE_RU.md.
Это не установленный production и не готовая реализация Catalog/Team/voice controller.
Ничего не записано в GitHub и ничего не запущено на VPS. ZIP не содержит настоящих секретов.

Структура восстановлена: executor/, scripts/, database/, env/, config/, ops/, release-gates/.
Шаблоны .example не являются рабочими env: локально создайте settings.env и env/*.env после допуска.
Compose core/honcho/data/team запускаются как отдельные проекты, не объединять их одним -f.
Единственное допустимое слияние -f в этом комплекте: core + dashboard optional override.
Новые собственные сервисы остаются .planned.yaml до реализации и приёмки.
Скрипты — доверенные инструменты администратора, не безопасный CD API для агента.
