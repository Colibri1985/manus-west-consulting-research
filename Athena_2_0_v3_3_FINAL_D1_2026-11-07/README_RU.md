# Афина 2.0 — архитектура v3.3 FINAL-D1
Документальный выпуск 07.11.2026 по текущему объёму аудита, закрытому владельцем. FINAL — статус выпуска документов, не verified production. Known residuals: Reports/Findings_Disposition.csv и Reports/Open_Decisions.csv.
## Что загружать
Весь этот каталог в отдельный release directory GitHub, без перезаписи historical. Этот архив не содержит real secrets и не выполняет push. SHA256SUMS.txt — контроль байтов, не цифровая подпись.
## Актуальные материалы
Athena_2_0_Current_Specification_v3_3.md — полный нормативный текст 36 разделов; .docx/.pdf/.doc — заново созданные copies (.doc является RTF). Таблицы и Mermaid в reader copies представлены текстом. OpenAPI/ER/dictionary/Contracts/*.csv — соответствующие проектные контракты. Policy/ACP_r2 — исходная действующая security policy, не изменена. При коллизии не выполнять affected action до разрешения.
## История
historical/source_v3_3 — исходная база с прежними hashes и validation. historical/reference — старые SYS-DRAFT/briefings/HTML/image/security review. Эти файлы могут содержать прежние примеры/схемы; они НЕ актуальные copies FINAL. Старые PNG сохранены только как historical, не выдаются за новый render. Не использовать historical config как effective settings.
## Для deploy
Применять Deploy/README_DEPLOY_RU.md и Deployment_Errata.md совместно с оригинальными pinned HANDOFF/deployment files. Они не входят как исправленный deployment bundle. server/recovery → Core → checkpoint → Honcho → checkpoint. Нет допуска real sensitive pilot data, Docker/admin/security/destructive rights агенту. Для v0.23.0 отдельно нужна v3.3.1.
## Проверки
Validation_Report.json содержит только фактически выполненные targeted static checks. Runtime/Compose/build/provider/restore/Mermaid CLI и полное historical coverage не подтверждены. Наличие acceptance scenario не PASS.
