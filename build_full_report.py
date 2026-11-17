"""
===================================================================================
Master Build Script: build_full_report.py
Assembles all preliminary pages and 10 chapters into:
  1. B.Tech_Project_Report_RAG_Warangal_Medical_System.docx
  2. B.Tech_Project_Report_RAG_Warangal_Medical_System.pdf
===================================================================================
"""

import os
import sys
import subprocess
import docx
from docx import Document

from report_sections_part1 import (
    apply_academic_styles,
    generate_preliminary_pages,
    generate_chapter1,
    generate_chapter2,
    generate_chapter3
)
from report_sections_part2 import (
    generate_chapter4,
    generate_chapter5,
    generate_chapter6
)
from report_sections_part3 import (
    generate_chapter7,
    generate_chapter8,
    generate_chapter9,
    generate_chapter10
)

def build_report():
    print("=" * 80)
    print("BUILDING B.TECH ACADEMIC DOCUMENTATION REPORT")
    print("Project: RAG-Based Medical Information System for Warangal Patients")
    print("Authors: B. Sai Tejaswi (2303A51184) & V. Abhilash (2303A51227)")
    print("Institution: SR University, Warangal, Telangana")
    print("=" * 80)

    doc = Document()
    apply_academic_styles(doc)

    print("[1/11] Generating Preliminary Pages (SRU Model: Cover, Declaration, Acknowledgement, Abstract, TOC, Lists - No Certificate)...")
    generate_preliminary_pages(doc)

    print("[2/11] Generating Chapter 1: Introduction...")
    generate_chapter1(doc)

    print("[3/11] Generating Chapter 2: Literature Review...")
    generate_chapter2(doc)

    print("[4/11] Generating Chapter 3: Problem Statement and Objectives...")
    generate_chapter3(doc)

    print("[5/11] Generating Chapter 4: System Requirements...")
    generate_chapter4(doc)

    print("[6/11] Generating Chapter 5: System Architecture and Design...")
    generate_chapter5(doc)

    print("[7/11] Generating Chapter 6: Methodology...")
    generate_chapter6(doc)

    print("[8/11] Generating Chapter 7: Implementation...")
    generate_chapter7(doc)

    print("[9/11] Generating Chapter 8: Results and Discussion...")
    generate_chapter8(doc)

    print("[10/11] Generating Chapter 9: Conclusion and Future Enhancements...")
    generate_chapter9(doc)

    print("[11/11] Generating Chapter 10: References (IEEE Format)...")
    generate_chapter10(doc)

    base_name = "B.Tech_Project_Report_RAG_Warangal_Medical_System"
    docx_path = os.path.abspath(f"{base_name}.docx")
    pdf_path = os.path.abspath(f"{base_name}.pdf")
    doc_path = os.path.abspath(f"{base_name}.doc")

    print(f"\nSaving Word Document (.docx) to: {docx_path}")
    doc.save(docx_path)
    print(" -> Microsoft Word document successfully written!")

    # Convert to PDF and legacy DOC via Word COM Automation
    print(f"\nConverting to PDF (.pdf) and DOC (.doc) via Microsoft Word COM...")
    ps_cmd = f"""
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    if (Test-Path '{pdf_path}') {{ Remove-Item '{pdf_path}' -Force -ErrorAction SilentlyContinue }}
    if (Test-Path '{doc_path}') {{ Remove-Item '{doc_path}' -Force -ErrorAction SilentlyContinue }}
    $doc = $word.Documents.Open('{docx_path}', [ref]$false, [ref]$true)
    $wdFormatPDF = 17
    $doc.SaveAs([ref]'{pdf_path}', [ref]$wdFormatPDF)
    $wdFormatDoc = 0
    $doc.SaveAs([ref]'{doc_path}', [ref]$wdFormatDoc)
    $doc.Close([ref]0)
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($doc) | Out-Null
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()
    Write-Host 'PDF and DOC Conversion Finished Successfully!'
    """
    try:
        res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True)
        if res.returncode == 0:
            print(" -> PDF and DOC versions successfully created!")
        else:
            print(f" -> Word COM Notice: {res.stderr}")
    except Exception as e:
        print(f" -> Conversion skipped: {e}")

    # Synchronize all output files to documentation folders
    import shutil
    sync_dirs = [
        os.path.abspath("Project_Documentation"),
        r"C:\Users\hp\OneDrive\Desktop\Warangal_HealthRAG_Project_Documentation"
    ]
    for target_dir in sync_dirs:
        if os.path.exists(target_dir):
            for ext in [".docx", ".doc", ".pdf"]:
                src = os.path.abspath(f"{base_name}{ext}")
                if os.path.exists(src):
                    dst = os.path.join(target_dir, f"{base_name}{ext}")
                    shutil.copy2(src, dst)
                    print(f" -> Synchronized to: {dst}")

    print("\n" + "=" * 80)
    print("DOCUMENTATION GENERATION COMPLETE!")
    print(f"DOCX: {docx_path} ({os.path.getsize(docx_path) / 1024:.1f} KB)")
    if os.path.exists(pdf_path):
        print(f"PDF:  {pdf_path} ({os.path.getsize(pdf_path) / 1024:.1f} KB)")
    if os.path.exists(doc_path):
        print(f"DOC:  {doc_path} ({os.path.getsize(doc_path) / 1024:.1f} KB)")
    print("=" * 80)

if __name__ == "__main__":
    build_report()
