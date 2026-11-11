$workspaceDocs = "c:\Users\hp\OneDrive\Desktop\tejus nlp\Project_Documentation"
$desktopDocs = "C:\Users\hp\OneDrive\Desktop\Warangal_HealthRAG_Project_Documentation"

# Create directories
New-Item -ItemType Directory -Path $workspaceDocs -Force | Out-Null
New-Item -ItemType Directory -Path $desktopDocs -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $workspaceDocs "Figures_and_Diagrams") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $desktopDocs "Figures_and_Diagrams") -Force | Out-Null

# Copy main documents
Copy-Item "B.Tech_Project_Report_RAG_Warangal_Medical_System.doc" (Join-Path $workspaceDocs "B.Tech_Project_Report_RAG_Warangal_Medical_System.doc") -Force
Copy-Item "B.Tech_Project_Report_RAG_Warangal_Medical_System.docx" (Join-Path $workspaceDocs "B.Tech_Project_Report_RAG_Warangal_Medical_System.docx") -Force
Copy-Item "B.Tech_Project_Report_RAG_Warangal_Medical_System.pdf" (Join-Path $workspaceDocs "B.Tech_Project_Report_RAG_Warangal_Medical_System.pdf") -Force

Copy-Item "B.Tech_Project_Report_RAG_Warangal_Medical_System.doc" (Join-Path $desktopDocs "B.Tech_Project_Report_RAG_Warangal_Medical_System.doc") -Force
Copy-Item "B.Tech_Project_Report_RAG_Warangal_Medical_System.docx" (Join-Path $desktopDocs "B.Tech_Project_Report_RAG_Warangal_Medical_System.docx") -Force
Copy-Item "B.Tech_Project_Report_RAG_Warangal_Medical_System.pdf" (Join-Path $desktopDocs "B.Tech_Project_Report_RAG_Warangal_Medical_System.pdf") -Force

# Copy research paper and summary if they exist
if (Test-Path "Research_Paper_RAG_Warangal_Medical_System.docx") {
    Copy-Item "Research_Paper_RAG_Warangal_Medical_System.docx" $workspaceDocs -Force
    Copy-Item "Research_Paper_RAG_Warangal_Medical_System.docx" $desktopDocs -Force
}
if (Test-Path "Summary of Created Files.docx") {
    Copy-Item "Summary of Created Files.docx" $workspaceDocs -Force
    Copy-Item "Summary of Created Files.docx" $desktopDocs -Force
}

# Copy figures
Copy-Item "figures\*.*" (Join-Path $workspaceDocs "Figures_and_Diagrams") -Force
Copy-Item "figures\*.*" (Join-Path $desktopDocs "Figures_and_Diagrams") -Force

# Create README text file
$readme = @"
===================================================================================
PROJECT DOCUMENTATION PACKAGE
Project: RAG-Based Medical Information System for Warangal Patients
SR University, Warangal, Telangana
Authors: B. Sai Tejaswi (2303A51184) & V. Abhilash (2303A51227)
===================================================================================

FILES IN THIS FOLDER:
1. B.Tech_Project_Report_RAG_Warangal_Medical_System.doc
   - Complete 59-page university project documentation report in Microsoft Word .doc format.

2. B.Tech_Project_Report_RAG_Warangal_Medical_System.docx
   - Complete 59-page university project documentation report in Microsoft Word .docx format.

3. B.Tech_Project_Report_RAG_Warangal_Medical_System.pdf
   - Complete 59-page print-ready PDF version with figures and IEEE references.

4. Research_Paper_RAG_Warangal_Medical_System.docx
   - IEEE format academic conference research paper.

5. Figures_and_Diagrams/
   - High-resolution architecture diagrams, DFDs, use-case diagrams, sequence diagrams,
     emergency triage flowcharts, and live system screenshots.

GitHub Repository:
https://github.com/2303A51184/NLP-Project
===================================================================================
"@

Set-Content -Path (Join-Path $workspaceDocs "README.txt") -Value $readme
Set-Content -Path (Join-Path $desktopDocs "README.txt") -Value $readme

# Also copy to local Desktop if available
if (Test-Path "C:\Users\hp\Desktop") {
    Copy-Item $desktopDocs "C:\Users\hp\Desktop\" -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Documentation package successfully organized in folders!"

# Launch Windows File Explorer pointing to the desktop documentation folder
Start-Process explorer.exe $desktopDocs
