# v3.3 FINAL-D1 — 07.11.2026
Версия архитектуры остаётся 3.3, идентификатор документальной сборки FINAL-D1. Это не v3.3.1/Hermes0.23 adaptation.
Основной текст: все 36 разделов сохранены; §29/34/36 переписаны под fresh install, provenance и текущий состав. Уточнения внесены непосредственно в соответствующие разделы, не одним overriding appendix.
API: JobStatus version/profile fields; AudioMetadata и READY constraints; обязательный Delivery Receipt; safe HTTP errors; nonempty IDs; operation ACL/dedup и preview provenance.
ER/CSV: добавлены logical version/operation/idempotency/origin/chunk plan поля; 69 сущностей и94 связи сохранены. Constraints отдельным каталогом, не native DDL.
Схемы: text/audio delivery→user; backup coverage дополнена. PNG не перерисованы и перенесены в historical; новые схемы Mermaid не отрендерены CLI.
DOCX/PDF/RTF сгенерированы заново из полного текущего Markdown, plain formatting; старые экземпляры сохранены. Не заявляется сохранение прежней вёрстки.
Добавлены constraints/state/boundary/backup/service/test catalogs, deploy notes/errata, findings dispositions, open decisions и новые hashes. Старые PASS и manifest не перенесены как текущие.
Внешний deployment-кандидат не исправлен и не упакован как новый релиз. Остаточные verification/implementation items не закрыты фиктивно.
