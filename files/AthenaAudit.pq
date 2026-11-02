// Read-only pilot: reads only the two local synthetic sources.
// Prepared for local validation; not executed by the Power Query engine on the server.
let
    FolderPath = "C:\Users\Admin\AppData\Local\AthenaExcelTest\",

    ReadSource = (FileName as text, ExpectedSum as number) as record =>
        let
            Workbook = Excel.Workbook(File.Contents(FolderPath & FileName), null, true),
            Matches = Table.SelectRows(
                Workbook,
                each [Kind] = "DefinedName" and [Item] = "AuditInputs"
            ),
            NamedRange =
                if Table.RowCount(Matches) = 1 then Matches{0}[Data]
                else error Error.Record(
                    "AuditInputsNotFound",
                    "Expected exactly one workbook-level AuditInputs named range.",
                    [File = FileName, Matches = Table.RowCount(Matches)]
                ),
            Columns = Table.ColumnNames(NamedRange),
            RawValues =
                if List.Count(Columns) = 1 then Table.Column(NamedRange, Columns{0})
                else error Error.Record(
                    "UnexpectedColumnCount",
                    "AuditInputs must contain exactly one column.",
                    [File = FileName, Columns = List.Count(Columns)]
                ),
            Values =
                if List.Count(RawValues) <> 3 then
                    error Error.Record(
                        "UnexpectedRowCount",
                        "AuditInputs must contain exactly three rows for this pilot.",
                        [File = FileName, Rows = List.Count(RawValues)]
                    )
                else if not List.AllTrue(List.Transform(RawValues, each Value.Is(_, type number))) then
                    error Error.Record(
                        "NonNumericInput",
                        "All three source values must be numbers; nulls and numeric text are rejected.",
                        [File = FileName]
                    )
                else RawValues,
            ActualSum = List.Sum(Values),
            Result = [
                Source = FileName,
                InputName = "AuditInputs",
                RowCount = List.Count(Values),
                ActualSum = ActualSum,
                ExpectedSum = ExpectedSum,
                Status = if ActualSum = ExpectedSum then "OK" else "MISMATCH"
            ]
        in
            Result,

    Result = Table.FromRecords({
        ReadSource("AuditSourceA.xlsx", 600),
        ReadSource("AuditSourceB.xlsx", 660)
    }),
    TypedResult = Table.TransformColumnTypes(Result, {
        {"Source", type text},
        {"InputName", type text},
        {"RowCount", Int64.Type},
        {"ActualSum", type number},
        {"ExpectedSum", type number},
        {"Status", type text}
    })
in
    TypedResult
