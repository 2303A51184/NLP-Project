$pptxPath = "c:\Users\hp\OneDrive\Desktop\tejus nlp\Project_Presentation\Project_Presentation.pptx"
$pptPath = "c:\Users\hp\OneDrive\Desktop\tejus nlp\Project_Presentation\Project_Presentation.ppt"
$desktopDir = "C:\Users\hp\OneDrive\Desktop\Warangal_HealthRAG_Project_Presentation"

$pptApp = New-Object -ComObject PowerPoint.Application
$presentation = $pptApp.Presentations.Open($pptxPath, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)

# 1 = ppSaveAsPresentation (.ppt format)
$presentation.SaveAs($pptPath, 1)
$presentation.Close()
$pptApp.Quit()

[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pptApp) | Out-Null
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()

Write-Host "Successfully converted to PPT: $pptPath"

# Copy to Desktop folder as well
Copy-Item $pptPath (Join-Path $desktopDir "Project_Presentation.ppt") -Force
Write-Host "Copied to Desktop: $(Join-Path $desktopDir 'Project_Presentation.ppt')"

if (Test-Path "C:\Users\hp\Desktop\Warangal_HealthRAG_Project_Presentation") {
    Copy-Item $pptPath "C:\Users\hp\Desktop\Warangal_HealthRAG_Project_Presentation\Project_Presentation.ppt" -Force
}
