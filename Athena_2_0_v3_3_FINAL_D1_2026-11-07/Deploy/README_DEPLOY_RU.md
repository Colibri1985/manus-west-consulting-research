# Передача FINAL-D1 в deploy
Архитектура 3.3 FINAL-D1 — документальная база, не server installation approval.
Порядок: server/recovery → ограниченный Core → checkpoint → Honcho → checkpoint. Каналы/voice далее по фактической готовности; Catalog/Team/Kaiten позднее. Никакого docker.sock, blanket sudo, security/destructive host management агенту.
ACP r2 применяется в принятом scope: approved standing cloud profiles; secrets/local-only/no-memory; fixed models per function. Не внедрять дополнительный LLM gateway/Little LLM/draft/automatic model selection сейчас. Hermes native session gateway — отдельное понятие.
Внешние первоисточники на pinned commit (не скачанные копии в этом FINAL):
https://github.com/Colibri1985/manus-west-consulting-research/blob/504c0520f5f53a6bc1faa18cef5e03704909c245/Athena_Deploy_Handoff_and_Sequence_RU_r1.md
https://github.com/Colibri1985/manus-west-consulting-research/tree/504c0520f5f53a6bc1faa18cef5e03704909c245/Athena_Deploy_r2
Перед E0 получить именно эти файлы/структуру, учесть Deployment_Errata.md. Ссылки не означают, что candidate исправлен или проверен полностью. Не реконструировать scripts по памяти.
До рискованных действий recovery и baseline; команды/changes только с exact target, approval, verification и rollback. Секреты не в чат/Git. Медицинские/банковские/клиентские материалы не в пилоте.
Формы checkpoints: было настроено / фактически проверено / запланировано; source/images/models/data, auth/tools/UID, сохранность/recovery, интерфейсы/права/отклонения. Honcho: versions/plugin/1536 single+batch, one sender, ingest→derive→new-session recall/correction/exclusion/scope tests; future health access boundary проверить, не создавать заранее.
Hermes v0.23.0 целевой deploy требует отдельной v3.3.1, не подменять этот FINAL её готовностью.
