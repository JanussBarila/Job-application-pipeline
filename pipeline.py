#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
One‑click pipeline: copy CSV → match → generate HTML/TXT → convert to PDF.
Run this script with your portable Python.
"""

import csv
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path
from datetime import datetime

# ============================================================
#  CONFIGURATION – adjust these as needed
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "applications_ai_optimized"

PYTHON_EXE = r"C:\Users\FlyUp Travel\PythonPortable\python.exe"  # used for subprocess (if needed)

# Filename structure
NAME_PART = "JanussBarila"
DATE_STR = datetime.now().strftime('%Y%m%d')

# Selected vacancies (ad_id from CSV)
SELECTED_IDS = [
    "1635673",
    "1643199",
    "1646879",
    "1647683",
    "1647714",
    "1643162",
]

CONTACT = {
    "vards": "Januss Barila",
    "telefons": "+371 25 512 631",
    "epasts": "yanushbarila@inbox.lv",
    "linkedin": "linkedin.com/in/yanush-barila",
    "github": "github.com/JanussBarila"
}

# Browser paths for PDF conversion
BROWSER_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

# ============================================================
#  STEP 1: Copy vacancies CSV from adjacent project
# ============================================================

def copy_vacancies_csv():
    print("\n--- STEP 1: Copy vacancies CSV ---")
    source = PROJECT_DIR.parent / "Python Biznesa datu analze" / "vacancies_live.csv"
    destination = DATA_DIR / "vacancies_live.csv"

    try:
        content = source.read_bytes()
        text = content.decode("utf-8-sig")
        first_line = text.splitlines()[0] if text.splitlines() else ""
        if not first_line.strip():
            raise ValueError("CSV fails ir tukšs vai tam nav kolonnu nosaukumu.")
        dialect = csv.Sniffer().sniff(first_line, delimiters=";,\t")
        reader = csv.reader(io.StringIO(text, newline=""), dialect, strict=True)
        columns = next(reader)
        if any(not name.strip() for name in columns):
            raise ValueError("CSV failā ir kolonna bez nosaukuma.")
        count = 0
        for row in reader:
            if not row or not any(value.strip() for value in row):
                continue
            if len(row) != len(columns):
                raise ValueError(
                    f"CSV rindā pie {reader.line_num}. līnijas nesakrīt kolonnu skaits."
                )
            count += 1
    except FileNotFoundError:
        print(f"⚠️ Nav atrasts fails: {source}")
        print("   Pārbaudi, vai abas projekta mapes ir blakus uz darbvirsmas.")
        print("   Turpināšu ar esošo CSV failu data/ (ja tāds ir).")
        return 0
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"❌ Neizdevās nolasīt vakanču failu: {error}")
        return 1

    temporary = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent, prefix=".vacancies_", delete=False
        ) as output:
            temporary = Path(output.name)
            output.write(content)
        os.replace(temporary, destination)
    except OSError as error:
        print(f"❌ Neizdevās saglabāt kopiju: {error}")
        return 1
    finally:
        if temporary is not None and temporary.exists():
            try:
                temporary.unlink()
            except OSError:
                pass

    print(f"✅ Vakanču fails nokopēts: {destination}")
    print(f"   Vakanču skaits: {count}")
    return 0

# ============================================================
#  STEP 2: Run matching (uses existing match_cv.py)
# ============================================================

def run_match_cv():
    print("\n--- STEP 2: Run matching (match_cv.py) ---")
    script = PROJECT_DIR / "match_cv.py"
    if not script.exists():
        print("⚠️ match_cv.py nav atrasts. Izlaižu šo soli.")
        return 0

    try:
        result = subprocess.run(
            [PYTHON_EXE, str(script)],
            cwd=str(PROJECT_DIR),
            capture_output=False,
            text=True,
            check=False
        )
        if result.returncode != 0:
            print(f"❌ match_cv.py beidzās ar kļūdu {result.returncode}")
            return 1
        print("✅ Matching veiksmīgs.")
        return 0
    except Exception as e:
        print(f"❌ Kļūda palaižot match_cv.py: {e}")
        return 1

# ============================================================
#  STEP 3: Generate HTML & TXT (embedded logic)
# ============================================================

# --- Helper functions for generation ---

def sanitize_filename(text, max_len=40):
    text = re.sub(r'[\\/*?:"<>|]', '_', text)
    text = re.sub(r'[\s\-\.]+', '_', text)
    text = re.sub(r'_+', '_', text)
    text = text.strip('_')
    if len(text) > max_len:
        text = text[:max_len]
    text = text.strip('_')
    return text

def fix_typos(text):
    typos = {
        r'\bEDISOFIT\b': 'EDISOFT',
        r'\bRESEBA\b': 'RISEBA',
        r'\bGrūga\b': 'Grupa',
        r'\bBaltiķe\b': 'Baltic',
        r'\bLatvija\b': 'Latvia',
    }
    for pat, repl in typos.items():
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    return text

def anonymize_text(text):
    text = fix_typos(text)
    clients = {
        r'\bERDA\b': 'SIA ERDA',
        r'\bBuvdizains\b': 'SIA Buvdizains',
    }
    for pat, repl in clients.items():
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    return text

def format_education(edu_list):
    html = ""
    for edu in edu_list:
        if isinstance(edu, dict):
            inst = edu.get('institution', '')
            period = edu.get('period', '')
            degree = edu.get('degree', '')
            details = edu.get('details', '')
            if details:
                details = re.sub(r'\(\d+\/\d+\)', '', details)
                details = re.sub(r'\s+', ' ', details).strip()
            text = f"{inst} ({period})"
            if degree:
                text += f" — {degree}"
            if details:
                text += f". {details}"
            html += f"<li>{text}</li>"
        else:
            html += f"<li>{edu}</li>"
    return html

def load_base_cv():
    with open(DATA_DIR / "base_cv.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def load_vacancy_matches():
    with open(DATA_DIR / "vacancy_matches.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_cv_html(job, base_cv, ranked_experience, matched_skills):
    title = job.get('title', '')
    company = job.get('company', '')

    base_summary = "Business and data analytics professional with 6+ years of experience across management reporting, process improvement, financial and workforce analysis, supply chain, forecasting and systems delivery. Skilled at turning fragmented operational data and business questions into reliable KPIs, dashboards, forecasts and practical recommendations. Hands-on experience with Power BI, DAX, Power Query, SQL, Python, advanced Excel and enterprise systems including HORIZON, IFS ERP and SAP. Comfortable working between business, Finance, HR, IT, Sales and Operations teams in Baltic and international environments."

    title_lower = title.lower()
    opening = ""
    if any(w in title_lower for w in ["logistik", "supply", "purchase", "iepirkum"]):
        opening = "Results-driven Business and Data Analytics professional with expertise in supply chain optimization, logistics operations, and data-driven decision-making. "
    elif any(w in title_lower for w in ["datu", "data", "analīt", "analytics", "engineer", "architect"]):
        opening = "Senior Data and Analytics professional with deep expertise in data engineering, BI, data modeling, and process automation. "
    elif any(w in title_lower for w in ["vadītājs", "manager", "director", "head"]):
        opening = "Strategic Business and Data Analytics leader with proven experience in driving operational excellence, leading cross-functional teams, and delivering data-driven business value. "
    else:
        opening = "Versatile Business and Data Analytics professional with a proven track record in delivering data-driven solutions across multiple industries and geographies. "

    summary = opening + base_summary
    if matched_skills:
        skills_str = ", ".join(matched_skills[:4])
        summary += f" Core strengths include {skills_str}."

    core_expertise = base_cv.get('core_expertise', [])
    prioritized = []
    for skill in matched_skills:
        for exp in core_expertise:
            if skill.lower() in exp.lower() and exp not in prioritized:
                prioritized.append(exp)
    for exp in core_expertise:
        if exp not in prioritized:
            prioritized.append(exp)
    prioritized = prioritized[:4]

    experience_html = ""
    for idx, exp in enumerate(ranked_experience):
        exp_title = exp.get('title', '')
        exp_company = exp.get('company', '')
        exp_period = exp.get('period', '')
        achievements = exp.get('achievements', [])
        achievements = [anonymize_text(ach) for ach in achievements]
        highlight = "background-color: #f0f4f8; border-left: 4px solid #1a5276; border-radius: 0 6px 6px 0; padding: 12px 12px 8px 12px;" if idx == 0 else "padding: 8px 0 4px 0;"
        experience_html += f"""
        <div style="{highlight} margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
                <span style="font-weight: 700; font-size: 15px; color: #1a1a1a;">{exp_title}</span>
                <span style="font-size: 13px; color: #1a5276; font-weight: 500;">{exp_period}</span>
            </div>
            <div style="font-size: 13.5px; color: #2c3e50; margin-bottom: 2px;">{exp_company}</div>
            <ul style="margin: 4px 0 0 0; padding-left: 18px; font-size: 13px; line-height: 1.5; color: #333;">
                {''.join(f'<li>{ach}</li>' for ach in achievements[:3])}
            </ul>
        </div>
        """

    skills = base_cv.get('skills', {})
    skills_html = ""
    for category, items in skills.items():
        label = category.replace('_', ' ').title()
        skills_html += f"""
        <div style="margin-bottom: 4px; font-size: 13px;">
            <span style="font-weight: 700; color: #1a5276; text-transform: uppercase; letter-spacing: 0.5px;">{label}:</span>
            <span style="color: #1a1a1a;">{', '.join(items)}</span>
        </div>
        """

    learning_html = f"""
        <div style="margin-bottom: 4px; font-size: 13px;">
            <span style="font-weight: 700; color: #1a5276; text-transform: uppercase; letter-spacing: 0.5px;">Currently Learning:</span>
            <span style="color: #1a1a1a;">Python (advanced), Full Automation, Vibe Coding, GitHub workflow, CI/CD pipelines</span>
        </div>
        """

    global_html = f"""
        <div style="margin-top: 6px; padding-top: 8px; border-top: 1px solid #e8edf2; font-size: 13px;">
            <span style="font-weight: 700; color: #1a5276; text-transform: uppercase; letter-spacing: 0.5px;">International & Technical:</span>
            <span style="color: #1a1a1a;">Experience working in Baltic and Nordic markets; developed Python-based automation pipelines, CI/CD workflows, and AI-assisted solutions for business intelligence and recruitment.</span>
        </div>
        """

    education_html = format_education(base_cv.get('education', []))

    languages = {
        "Latvian": "Fluent",
        "English": "Professional Working Proficiency",
        "Russian": "Fluent",
        "Polish": "Middle level"
    }
    languages_html = ", ".join(f"{lang} — {level}" for lang, level in languages.items())

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV - {CONTACT['vards']} - {title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;
            margin: 0;
            padding: 30px;
            background: #ffffff;
            color: #1a1a1a;
            line-height: 1.5;
            font-size: 14px;
        }}
        .page {{
            max-width: 850px;
            margin: 0 auto;
            padding: 20px 10px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 22px;
            padding-bottom: 16px;
            border-bottom: 3px solid #1a5276;
        }}
        .header h1 {{
            font-size: 32px;
            font-weight: 300;
            letter-spacing: 2px;
            color: #1a1a1a;
            margin-bottom: 4px;
        }}
        .header .contact {{
            font-size: 14px;
            color: #444;
            letter-spacing: 0.3px;
        }}
        .header .contact a {{
            color: #1a5276;
            text-decoration: none;
            border-bottom: 1px dotted transparent;
            transition: border-color 0.2s;
        }}
        .header .contact a:hover {{
            border-bottom-color: #1a5276;
        }}
        .section {{
            margin-bottom: 16px;
        }}
        .section h2 {{
            font-size: 15px;
            font-weight: 700;
            color: #1a5276;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #e8edf2;
            padding-bottom: 4px;
            margin-bottom: 8px;
        }}
        .summary {{
            font-size: 14px;
            line-height: 1.6;
            color: #1a1a1a;
        }}
        ul {{
            list-style: none;
            padding-left: 0;
        }}
        .section ul li {{
            padding-left: 18px;
            position: relative;
            margin-bottom: 2px;
            font-size: 13.5px;
            line-height: 1.5;
        }}
        .section ul li::before {{
            content: "—";
            position: absolute;
            left: 0;
            color: #1a5276;
            font-weight: 600;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 11px;
            color: #999;
            text-align: center;
            border-top: 1px solid #e8edf2;
            padding-top: 10px;
            letter-spacing: 0.3px;
        }}
        @media print {{
            body {{ padding: 15px; font-size: 12px; }}
            .header h1 {{ font-size: 28px; }}
            .section h2 {{ font-size: 13px; }}
            .page {{ max-width: 100%; padding: 0; }}
            .header .contact {{ font-size: 12px; }}
        }}
    </style>
</head>
<body>
<div class="page">

    <div class="header">
        <h1>{CONTACT['vards']}</h1>
        <div class="contact">
            <a href="tel:{CONTACT['telefons'].replace(' ', '')}">{CONTACT['telefons']}</a> &middot;
            <a href="mailto:{CONTACT['epasts']}">{CONTACT['epasts']}</a> &middot;
            <a href="https://{CONTACT['linkedin']}" target="_blank">linkedin.com/in/yanush-barila</a> &middot;
            <a href="https://{CONTACT['github']}" target="_blank">github.com/JanussBarila</a>
        </div>
    </div>

    <div class="section">
        <h2>Professional Profile</h2>
        <div class="summary">{summary}</div>
    </div>

    <div class="section">
        <h2>Core Expertise</h2>
        <ul>
            {''.join(f'<li>{exp}</li>' for exp in prioritized)}
        </ul>
    </div>

    <div class="section">
        <h2>Professional Experience</h2>
        {experience_html}
    </div>

    <div class="section">
        <h2>Technical Skills</h2>
        {skills_html}
        {learning_html}
        {global_html}
    </div>

    <div class="section">
        <h2>Education</h2>
        <ul>
            {education_html}
        </ul>
    </div>

    <div class="section">
        <h2>Languages</h2>
        <p style="font-size: 13.5px; margin: 0;">{languages_html}</p>
    </div>

    <div class="footer">
        Generated {datetime.now().strftime('%d %B %Y')} &bull; Tailored for: {title} &bull; {company}
    </div>

</div>
</body>
</html>"""
    return html

def generate_cover_letter_html(job, best_exp_text, base_cv, matched_skills):
    title = job.get('title', '')
    company = job.get('company', '')

    if not matched_skills:
        all_skills = []
        for cat, items in base_cv.get('skills', {}).items():
            all_skills.extend(items)
        title_lower = title.lower()
        if any(w in title_lower for w in ["logistik", "supply", "purchase", "iepirkum", "loģistik"]):
            keywords = ["supply chain", "logistics", "forecasting", "inventory", "procurement", "operations", "demand planning", "erp"]
        elif any(w in title_lower for w in ["datu", "data", "analīt", "analytics", "engineer", "architect", "bi", "business intelligence"]):
            keywords = ["data modeling", "bi", "sql", "python", "etl", "dax", "power bi", "analytics"]
        elif any(w in title_lower for w in ["vadītājs", "manager", "director", "head", "leader"]):
            keywords = ["strategic", "leadership", "process improvement", "kpi", "team", "budget", "reporting"]
        else:
            keywords = ["analysis", "reporting", "process", "improvement", "data"]
        matched = [s for s in all_skills if any(kw in s.lower() for kw in keywords)]
        if not matched:
            matched = all_skills[:3]
        matched_skills = matched[:4]

    skills_str = ", ".join(matched_skills) if matched_skills else "skills aligned with this position"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Cover Letter - {CONTACT['vards']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Arial, sans-serif;
            margin: 40px auto;
            max-width: 680px;
            padding: 0 20px;
            line-height: 1.6;
            color: #1a1a1a;
            font-size: 14px;
        }}
        .date {{
            text-align: right;
            margin-bottom: 20px;
            color: #555;
            font-size: 14px;
        }}
        .subject {{
            font-weight: 700;
            font-size: 16px;
            margin-bottom: 16px;
            color: #1a5276;
            border-bottom: 2px solid #e8edf2;
            padding-bottom: 8px;
        }}
        .body-text {{
            font-size: 14px;
            line-height: 1.7;
        }}
        .signature {{
            margin-top: 28px;
            padding-top: 8px;
            border-top: 1px solid #e8edf2;
        }}
        .footer {{
            margin-top: 30px;
            font-size: 11px;
            color: #999;
            border-top: 1px solid #e8edf2;
            padding-top: 10px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="date">{datetime.now().strftime('%d %B %Y')}</div>
    
    <div class="subject">Application for {title} position at {company}</div>
    
    <div class="body-text">
        <p>Dear Hiring Team,</p>
        
        <p>I am writing to express my interest in the <strong>{title}</strong> position at <strong>{company}</strong>. With 6+ years of experience in business and data analytics across multiple industries — including supply chain, financial services, and workforce planning — I am confident in my ability to contribute effectively to your team.</p>
        
        <p>My most relevant experience includes: <strong>{best_exp_text}</strong>.</p>
        
        <p>Key areas of expertise that align with your requirements: <strong>{skills_str}</strong>.</p>
        
        <p>I am particularly drawn to this opportunity because of {company}'s reputation for innovation and international presence. I look forward to the possibility of discussing how my background can support your strategic objectives.</p>
        
        <p>Thank you for your time and consideration. I have attached my CV for your review.</p>
    </div>
    
    <div class="signature">
        <p style="margin-bottom: 2px; font-weight: 600;">Yours sincerely,</p>
        <p style="font-weight: 700; font-size: 16px; margin-top: 2px;">{CONTACT['vards']}</p>
        <p style="font-size: 13px; color: #555; margin-top: 2px;">
            <a href="mailto:{CONTACT['epasts']}" style="color: #1a5276; text-decoration: none;">{CONTACT['epasts']}</a> &bull; 
            <a href="https://{CONTACT['linkedin']}" style="color: #1a5276; text-decoration: none;" target="_blank">linkedin.com/in/yanush-barila</a>
        </p>
    </div>
    
    <div class="footer">Tailored for: {title} at {company}</div>
</body>
</html>"""
    return html

def generate_all_documents():
    print("\n--- STEP 3: Generate HTML and TXT files ---")
    try:
        base_cv = load_base_cv()
        matches = load_vacancy_matches()
    except FileNotFoundError as e:
        print(f"❌ Kļūda ielādējot datus: {e}")
        return 1

    selected = [m for m in matches if m.get('ad_id') in SELECTED_IDS]
    print(f"Atrastas {len(selected)} no {len(SELECTED_IDS)} atlasītajām vakancēm.")
    if not selected:
        print("Nav nevienas vakances. Pabeidzu.")
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for idx, job in enumerate(selected, 1):
        title = job.get('title', '')
        company = job.get('company', '')
        ad_id = job.get('ad_id', f'vakance_{idx}')
        ranked = job.get('ranked_experience', [])
        matched_skills = job.get('matched_skills', [])

        print(f"[{idx}/{len(selected)}] Apstrādā: {title} @ {company}")

        # Generate filenames
        title_part = sanitize_filename(title, max_len=40)
        cv_filename = f"CV_{NAME_PART}_{title_part}_{DATE_STR}"
        cl_filename = f"CoverLetter_{NAME_PART}_{title_part}_{DATE_STR}"

        company_clean = company.replace(' ', '_').replace('/', '_').replace('\\', '_')
        job_folder = OUTPUT_DIR / f"{ad_id}_{company_clean}"
        job_folder.mkdir(parents=True, exist_ok=True)

        # CV HTML
        cv_html = generate_cv_html(job, base_cv, ranked, matched_skills)
        cv_path = job_folder / f"{cv_filename}.html"
        cv_path.write_text(cv_html, encoding='utf-8')
        print(f"  ✅ CV HTML: {cv_path.name}")

        # Cover Letter HTML
        best_exp_obj = ranked[0] if ranked else None
        best_exp_text = f"{best_exp_obj.get('title')} @ {best_exp_obj.get('company')} ({best_exp_obj.get('period')})" if best_exp_obj else "Relevant professional experience"
        cl_html = generate_cover_letter_html(job, best_exp_text, base_cv, matched_skills)
        cl_path = job_folder / f"{cl_filename}.html"
        cl_path.write_text(cl_html, encoding='utf-8')
        print(f"  ✅ Cover Letter HTML: {cl_path.name}")

        # Cover Letter TXT
        skills_str = ", ".join(matched_skills) if matched_skills else "skills aligned with this position"
        cover_text = f"""{datetime.now().strftime('%d %B %Y')}

Application for {title} position at {company}

Dear Hiring Team,

I am writing to express my interest in the {title} position at {company}. With 6+ years of experience in business and data analytics across multiple industries — including supply chain, financial services, and workforce planning — I am confident in my ability to contribute effectively to your team.

My most relevant experience includes: {best_exp_text}.

Key areas of expertise that align with your requirements: {skills_str}.

I am particularly drawn to this opportunity because of {company}'s reputation for innovation and international presence. I look forward to the possibility of discussing how my background can support your strategic objectives.

Thank you for your time and consideration. I have attached my CV for your review.

Yours sincerely,
{CONTACT['vards']}
{CONTACT['epasts']}
linkedin.com/in/yanush-barila"""
        txt_path = job_folder / f"{cl_filename}.txt"
        txt_path.write_text(cover_text, encoding='utf-8')
        print(f"  📄 Cover Letter TXT: {txt_path.name}")

        # Open URL (optional)
        url = job.get('url')
        if url:
            webbrowser.open(url)
            print(f"  🌐 Atvērts URL: {url}")

    print("✅ HTML un TXT faili izveidoti.")
    return 0

# ============================================================
#  STEP 4: Convert HTML to PDF (with structured naming and clean headers)
# ============================================================

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
    # fallback: use folder name
    folder = html_path.parent.name
    if "_" in folder:
        return folder.split("_", 1)[-1]
    return folder

def get_pdf_name(html_path):
    vacancy = sanitize_filename(extract_vacancy_from_html(html_path), max_len=40)
    if "CV" in html_path.stem or "cv" in html_path.stem.lower():
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
        "--no-pdf-header-footer",          # ← REMOVES file path, page numbers, date
        f"--print-to-pdf={pdf_abs}",
        f"file:///{html_abs.as_posix()}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"  ❌ Kļūda konvertējot {html_path.name}: {result.stderr[:200]}")
            return False
        print(f"  ✅ PDF saglabāts: {pdf_path.name}")
        return True
    except subprocess.TimeoutExpired:
        print(f"  ❌ Taimauts konvertējot {html_path.name}")
        return False
    except Exception as e:
        print(f"  ❌ Kļūda: {e}")
        return False

def convert_all_html_to_pdf():
    print("\n--- STEP 4: Convert HTML to PDF ---")
    browser = find_browser()
    if not browser:
        print("❌ Nav atrasts pārlūks (Edge vai Chrome). Instalē to un mēģini vēlreiz.")
        return 1
    print(f"✅ Izmantots pārlūks: {browser}")

    html_files = list(OUTPUT_DIR.rglob("*.html"))
    if not html_files:
        print("❌ Nav HTML failu, ko konvertēt.")
        return 0

    print(f"Atrasti {len(html_files)} HTML faili.")
    converted = failed = 0
    for html_path in html_files:
        pdf_name = get_pdf_name(html_path)
        pdf_path = html_path.parent / pdf_name
        print(f"Konvertē: {html_path.parent.name}/{html_path.name} -> {pdf_name}")
        if convert_html_to_pdf(html_path, pdf_path, browser):
            converted += 1
        else:
            failed += 1
    print(f"✅ Konvertēti: {converted}, ❌ Neizdevās: {failed}")
    return 0 if failed == 0 else 1

# ============================================================
#  MAIN PIPELINE
# ============================================================

def main():
    print("\n" + "="*60)
    print("  🚀 AUTOMATED CV PIPELINE (Single File)")
    print("="*60)

    steps = [
        ("Kopē CSV", copy_vacancies_csv),
        ("Matching", run_match_cv),
        ("Ģenerē HTML/TXT", generate_all_documents),
        ("Konvertē uz PDF", convert_all_html_to_pdf),
    ]

    for desc, func in steps:
        print(f"\n▶ {desc}...")
        ret = func()
        if ret != 0:
            print(f"❌ Pipeline apstājās pie: {desc}")
            return 1

    print("\n" + "="*60)
    print("  ✅ PIPELINE PILNĪBĀ PABEIGTS!")
    print("="*60)
    print(f"\n📁 PDF faili atrodas mapē: {OUTPUT_DIR}")
    print("📄 Failu formāts: CV_JanussBarila_Vakance_YYYYMMDD.pdf")
    print("   un CoverLetter_JanussBarila_Vakance_YYYYMMDD.pdf")
    print("\n👉 Atver mapi un sāc pieteikties!")
    return 0

if __name__ == "__main__":
    sys.exit(main())