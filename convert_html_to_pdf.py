import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "applications_ai_optimized"

# CONFIGURATION
NAME_PART = "JanussBarila"
DATE_STR = datetime.now().strftime('%Y%m%d')

BROWSER_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

def sanitize_filename(text, max_len=40):
    text = re.sub(r'[\\/*?:"<>|]', '_', text)
    text = re.sub(r'[\s\-\.]+', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    if len(text) > max_len:
        text = text[:max_len]
    return text.strip('_')

def find_browser():
    for path in BROWSER_PATHS:
        if Path(path).exists():
            return path
    return None

def extract_vacancy_from_html(html_path):
    try:
        content = html_path.read_text(encoding='utf-8')
        match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group(1).strip()
            if "CV -" in title:
                parts = title.split(" - ")
                if len(parts) >= 3:
                    return parts[-1].strip()
            elif "Cover Letter -" in title:
                subject_match = re.search(r'<div class="subject">Application for (.*?) position at', content, re.IGNORECASE)
                if subject_match:
                    return subject_match.group(1).strip()
    except:
        pass
    folder_name = html_path.parent.name
    if "_" in folder_name:
        return folder_name.split("_", 1)[-1]
    return folder_name

def get_pdf_name(html_path):
    file_name = html_path.stem
    vacancy = sanitize_filename(extract_vacancy_from_html(html_path), max_len=40)
    if "CV" in file_name or "cv" in file_name.lower():
        return f"CV_{NAME_PART}_{vacancy}_{DATE_STR}.pdf"
    else:
        return f"CoverLetter_{NAME_PART}_{vacancy}_{DATE_STR}.pdf"

def convert_html_to_pdf(html_path, pdf_path, browser_path):
    html_abs = html_path.resolve()
    pdf_abs = pdf_path.resolve()
    cmd = [
        browser_path,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",          # ← removes file path and page numbers
        f"--print-to-pdf={pdf_abs}",
        f"file:///{html_abs.as_posix()}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ❌ Error converting {html_path.name}: {result.stderr[:200]}")
            return False
        print(f"  ✅ PDF saved: {pdf_path.name}")
        return True
    except subprocess.TimeoutExpired:
        print(f"  ❌ Timeout converting {html_path.name}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("=== CONVERT HTML TO PDF (with structured naming) ===\n")
    browser = find_browser()
    if not browser:
        print("❌ No browser found (Edge or Chrome).")
        return 1
    print(f"✅ Using browser: {browser}\n")

    html_files = list(OUTPUT_DIR.rglob("*.html"))
    if not html_files:
        print(f"No HTML files found in {OUTPUT_DIR}")
        return 0

    print(f"Found {len(html_files)} HTML files.\n")
    converted = failed = 0
    for html_path in html_files:
        pdf_name = get_pdf_name(html_path)
        pdf_path = html_path.parent / pdf_name
        print(f"Converting: {html_path.parent.name}/{html_path.name} -> {pdf_name}")
        if convert_html_to_pdf(html_path, pdf_path, browser):
            converted += 1
        else:
            failed += 1
        print()

    print(f"=== DONE ===")
    print(f"✅ Converted: {converted}")
    print(f"❌ Failed: {failed}")
    if converted > 0:
        print(f"\n📁 PDFs are saved in: {OUTPUT_DIR}")
        print("📋 Filename structure: CV_JanussBarila_Vacancy_YYYYMMDD.pdf")
    return 0

if __name__ == "__main__":
    sys.exit(main())