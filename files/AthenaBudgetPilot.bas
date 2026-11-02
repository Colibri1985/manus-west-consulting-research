Attribute VB_Name = "AthenaBudgetPilotModule"
Option Explicit

' Local VBA prototype. Native Excel compilation/execution is still to be tested.
' Inputs: only the two synthetic XLSX files in LOCALAPPDATA\AthenaExcelTest.
' Outputs: a NEW, UNSAVED workbook; no external links; no source writes.

Public Sub AthenaBudgetPilot()
    Dim folder As String, fileA As String, fileB As String
    Dim sourceA As Workbook, sourceB As Workbook, candidate As Workbook
    Dim report As Workbook, budget As Worksheet, checks As Worksheet
    Dim valuesA As Variant, valuesB As Variant, headers As Variant, links As Variant
    Dim previousSecurity As Long, securityCaptured As Boolean
    Dim readOnlyA As Boolean, readOnlyB As Boolean, allPassed As Boolean
    Dim sumA As Double, sumB As Double
    Dim i As Long, checkRow As Long
    Dim linkState As String, formulaState As String, failureText As String

    If MsgBox("Read the two synthetic source files in read-only mode and create a NEW report?" & vbCrLf & _
              "No files will be saved. Existing books will not be edited." & vbCrLf & _
              "Automatic macro execution for source opens will be forced OFF temporarily," & vbCrLf & _
              "then the previous mode will be restored.", vbOKCancel + vbInformation, _
              "Athena VBA pilot - confirmation") <> vbOK Then Exit Sub

    On Error GoTo Failed
    folder = Environ$("LOCALAPPDATA")
    If Len(folder) = 0 Then Err.Raise vbObjectError + 100, , "LOCALAPPDATA is not available."
    folder = folder & Application.PathSeparator & "AthenaExcelTest" & Application.PathSeparator
    fileA = folder & "AuditSourceA.xlsx"
    fileB = folder & "AuditSourceB.xlsx"
    If Len(Dir$(fileA)) = 0 Then Err.Raise vbObjectError + 101, , "Missing file: " & fileA
    If Len(Dir$(fileB)) = 0 Then Err.Raise vbObjectError + 102, , "Missing file: " & fileB

    For Each candidate In Application.Workbooks
        If StrComp(candidate.Name, "AuditSourceA.xlsx", vbTextCompare) = 0 Or _
           StrComp(candidate.Name, "AuditSourceB.xlsx", vbTextCompare) = 0 Then
            Err.Raise vbObjectError + 103, , "Close the two test sources before running this pilot."
        End If
    Next candidate

    previousSecurity = Application.AutomationSecurity
    securityCaptured = True
    Application.AutomationSecurity = 3 ' msoAutomationSecurityForceDisable; never lower protection.
    Set sourceA = Application.Workbooks.Open(Filename:=fileA, UpdateLinks:=0, _
        ReadOnly:=True, IgnoreReadOnlyRecommended:=True, Notify:=False, AddToMru:=False)
    Set sourceB = Application.Workbooks.Open(Filename:=fileB, UpdateLinks:=0, _
        ReadOnly:=True, IgnoreReadOnlyRecommended:=True, Notify:=False, AddToMru:=False)
    readOnlyA = sourceA.ReadOnly
    readOnlyB = sourceB.ReadOnly
    If Not readOnlyA Or Not readOnlyB Then Err.Raise vbObjectError + 104, , "Read-only mode is required."

    valuesA = ReadInput(sourceA)
    valuesB = ReadInput(sourceB)
    For i = 1 To 3
        sumA = sumA + CDbl(valuesA(i, 1))
        sumB = sumB + CDbl(valuesB(i, 1))
    Next i

    sourceA.Close SaveChanges:=False
    Set sourceA = Nothing
    sourceB.Close SaveChanges:=False
    Set sourceB = Nothing
    Application.AutomationSecurity = previousSecurity
    securityCaptured = False

    Set report = Application.Workbooks.Add(Template:=xlWBATWorksheet)
    Set budget = report.Worksheets(1)
    budget.Name = "BudgetCompare"
    Set checks = report.Worksheets.Add(After:=budget)
    checks.Name = "Checks"

    headers = Array("Item", "Source_A", "Source_B", "Delta", "Delta_pct")
    For i = 0 To 4
        budget.Cells(1, i + 1).Value2 = headers(i)
    Next i
    For i = 1 To 3
        budget.Cells(i + 1, 1).Value2 = "Item " & CStr(i)
        budget.Cells(i + 1, 2).Value2 = CDbl(valuesA(i, 1))
        budget.Cells(i + 1, 3).Value2 = CDbl(valuesB(i, 1))
        budget.Cells(i + 1, 4).Formula = "=C" & CStr(i + 1) & "-B" & CStr(i + 1)
        budget.Cells(i + 1, 5).Formula = "=IF(B" & CStr(i + 1) & "=0,NA(),D" & CStr(i + 1) & "/B" & CStr(i + 1) & ")"
    Next i
    budget.Range("A5").Value2 = "TOTAL"
    budget.Range("B5").Formula = "=SUM(B2:B4)"
    budget.Range("C5").Formula = "=SUM(C2:C4)"
    budget.Range("D5").Formula = "=C5-B5"
    budget.Range("E5").Formula = "=IF(B5=0,NA(),D5/B5)"
    budget.Range("B2:D5").NumberFormat = "#,##0.00"
    budget.Range("E2:E5").NumberFormat = "0.0%"
    budget.Range("A5:E5").Font.Bold = True
    budget.Range("A7").Value2 = "Synthetic test data only. Report was not saved."
    budget.Range("A8").Value2 = "Sources: AuditSourceA.xlsx and AuditSourceB.xlsx; AuditInputs."
    budget.Range("A9").Value2 = "Actual totals are Excel formulas; expected totals are checked separately."
    budget.Calculate

    headers = Array("Check", "Actual", "Expected", "Status")
    For i = 0 To 3
        checks.Cells(1, i + 1).Value2 = headers(i)
    Next i
    links = report.LinkSources(xlExcelLinks)
    If IsEmpty(links) Then linkState = "NONE" Else linkState = "FOUND"
    formulaState = "YES"
    For i = 2 To 5
        If Not budget.Cells(5, i).HasFormula Then formulaState = "NO"
    Next i

    checkRow = 2
    allPassed = True
    allPassed = WriteCheck(checks, checkRow, "Source A opened read-only", readOnlyA, True) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Source B opened read-only", readOnlyB, True) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Source A input rows", UBound(valuesA, 1), 3) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Source B input rows", UBound(valuesB, 1), 3) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Excel total A", budget.Range("B5").Value2, 600#) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Excel total B", budget.Range("C5").Value2, 660#) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Excel total delta", budget.Range("D5").Value2, 60#) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Excel total delta fraction", budget.Range("E5").Value2, 0.1, 0.000000001) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Excel A vs independent VBA sum", budget.Range("B5").Value2, sumA) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Excel B vs independent VBA sum", budget.Range("C5").Value2, sumB) And allPassed
    allPassed = WriteCheck(checks, checkRow, "Report external Excel links", linkState, "NONE") And allPassed
    allPassed = WriteCheck(checks, checkRow, "Total cells still contain formulas", formulaState, "YES") And allPassed

    StyleHeader budget.Range("A1:E1")
    StyleHeader checks.Range("A1:D1")
    budget.Columns("A:E").ColumnWidth = 16
    checks.Columns("A").ColumnWidth = 44
    checks.Columns("B:C").ColumnWidth = 17
    checks.Columns("D").ColumnWidth = 12
    budget.Activate
    If allPassed Then
        MsgBox "PASS: the report was created and all native checks passed." & vbCrLf & _
               "TOTAL: 600 / 660 / 60 / 10%. See the Checks sheet." & vbCrLf & _
               "Report was not saved. Source files were closed without saving.", _
               vbInformation, "Athena VBA pilot"
    Else
        checks.Activate
        MsgBox "FAIL: review the Checks sheet. Do not treat this pilot as passed." & vbCrLf & _
               "Report was not saved. Source files were closed without saving.", _
               vbExclamation, "Athena VBA pilot"
    End If
    Exit Sub

Failed:
    failureText = CStr(Err.Number) & ": " & Err.Description
    On Error Resume Next
    If Not sourceA Is Nothing Then sourceA.Close SaveChanges:=False
    If Not sourceB Is Nothing Then sourceB.Close SaveChanges:=False
    If securityCaptured Then
        Err.Clear
        Application.AutomationSecurity = previousSecurity
        If Err.Number <> 0 Then failureText = failureText & vbCrLf & "WARNING: could not restore the previous automation security mode."
    End If
    If Not report Is Nothing Then report.Worksheets(1).Range("A1").Value2 = "FAILED - incomplete report"
    On Error GoTo 0
    MsgBox "Pilot stopped: " & failureText & vbCrLf & _
           "No files were saved. Do not treat any partial output as a passed test.", _
           vbExclamation, "Athena VBA pilot"
End Sub

Private Function ReadInput(ByVal book As Workbook) As Variant
    Dim area As Range, owner As Workbook, data As Variant, i As Long
    Set area = book.Names("AuditInputs").RefersToRange
    Set owner = area.Worksheet.Parent
    If Not owner Is book Then Err.Raise vbObjectError + 110, , "AuditInputs must belong to its source workbook."
    If area.Worksheet.Name <> "Data" Then Err.Raise vbObjectError + 111, , "Expected source sheet Data."
    If area.Areas.Count <> 1 Then Err.Raise vbObjectError + 112, , "Expected one contiguous range."
    If area.Address(False, False, xlA1) <> "B2:B4" Then Err.Raise vbObjectError + 113, , "Expected AuditInputs = Data!B2:B4."
    If area.Rows.Count <> 3 Or area.Columns.Count <> 1 Then Err.Raise vbObjectError + 114, , "Expected three rows and one column."
    data = area.Value2
    For i = 1 To 3
        If IsError(data(i, 1)) Then Err.Raise vbObjectError + 115, , "Source input contains an error."
        If IsEmpty(data(i, 1)) Then Err.Raise vbObjectError + 116, , "Source input contains an empty cell."
        If VarType(data(i, 1)) = vbString Or VarType(data(i, 1)) = vbBoolean Then Err.Raise vbObjectError + 117, , "Source input must be numeric, not text or Boolean."
        If Not IsNumeric(data(i, 1)) Then Err.Raise vbObjectError + 118, , "Source input is not numeric."
        If area.Cells(i, 1).HasFormula Then Err.Raise vbObjectError + 119, , "This synthetic pilot expects literal source values, not formulas."
    Next i
    ReadInput = data
End Function

Private Function WriteCheck(ByVal sheet As Worksheet, ByRef targetRow As Long, _
                            ByVal label As String, ByVal actual As Variant, _
                            ByVal expected As Variant, Optional ByVal tolerance As Double = 0) As Boolean
    Dim passed As Boolean
    If IsError(actual) Or IsNull(actual) Then
        passed = False
    ElseIf tolerance > 0 Then
        If IsNumeric(actual) Then passed = (Abs(CDbl(actual) - CDbl(expected)) <= tolerance)
    Else
        passed = (CStr(actual) = CStr(expected))
    End If
    sheet.Cells(targetRow, 1).Value2 = label
    sheet.Cells(targetRow, 2).Value2 = actual
    sheet.Cells(targetRow, 3).Value2 = expected
    If passed Then
        sheet.Cells(targetRow, 4).Value2 = "PASS"
        sheet.Cells(targetRow, 4).Interior.Color = RGB(222, 242, 228)
    Else
        sheet.Cells(targetRow, 4).Value2 = "FAIL"
        sheet.Cells(targetRow, 4).Interior.Color = RGB(255, 223, 223)
    End If
    targetRow = targetRow + 1
    WriteCheck = passed
End Function

Private Sub StyleHeader(ByVal cells As Range)
    cells.Font.Bold = True
    cells.Font.Color = vbWhite
    cells.Interior.Color = RGB(25, 58, 82)
End Sub
