import json
import sys
from pathlib import Path
from datetime import datetime
import webbrowser
import re

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "applications_ai_optimized"

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

# ------------------------------------------------------------
# ANONIMIZĀCIJA – aizstāj klientu nosaukumus ar anonimizētiem variantiem
CLIENT_ANONYMIZATION = {
    r'\bERDA\b': 'SIA ERDA',
    r'\bBuvdizains\b': 'SIA Būvdizains',
}
# ------------------------------------------------------------

def anonymize_text(text):
    for pattern, replacement in CLIENT_ANONYMIZATION.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def load_base_cv():
    with open(DATA_DIR / "base_cv.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def load_vacancy_matches():
    with open(DATA_DIR / "vacancy_matches.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def format_education(education_list):
    html = ""
    for edu in education_list:
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

def generate_ai_optimized_cv(job, base_cv, ranked_experience, matched_skills):
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
        exp_achievements = exp.get('achievements', [])
        exp_achievements = [anonymize_text(ach) for ach in exp_achievements]
        
        # Izcelta atbilstošākā pieredze
        if idx == 0:
            highlight = "background-color: #f0f4f8; border-left: 4px solid #1a5276; border-radius: 0 6px 6px 0; padding: 12px 12px 8px 12px;"
        else:
            highlight = "padding: 8px 0 4px 0;"
        
        experience_html += f"""
        <div style="{highlight} margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap;">
                <span style="font-weight: 700; font-size: 15px; color: #1a1a1a;">{exp_title}</span>
                <span style="font-size: 13px; color: #1a5276; font-weight: 500;">{exp_period}</span>
            </div>
            <div style="font-size: 13.5px; color: #2c3e50; margin-bottom: 2px;">{exp_company}</div>
            <ul style="margin: 4px 0 0 0; padding-left: 18px; font-size: 13px; line-height: 1.5; color: #333;">
                {''.join(f'<li>{ach}</li>' for ach in exp_achievements[:3])}
            </ul>
        </div>
        """

    skills = base_cv.get('skills', {})
    skills_html = ""
    for category, items in skills.items():
        category_label = category.replace('_', ' ').title()
        skills_html += f"""
        <div style="margin-bottom: 4px; font-size: 13px;">
            <span style="font-weight: 700; color: #1a5276; text-transform: uppercase; letter-spacing: 0.5px;">{category_label}:</span>
            <span style="color: #1a1a1a;">{', '.join(items)}</span>
        </div>
        """

    # Pašreizējās mācības – tīrs, neuzkrītošs
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

    # Valodas – jaunā secība
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

def generate_cover_letter(job, best_exp_text, base_cv, matched_skills):
    title = job.get('title', '')
    company = job.get('company', '')
    
    if not matched_skills:
        all_skills = []
        for category, items in base_cv.get('skills', {}).items():
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
        
        matched = []
        for skill in all_skills:
            skill_lower = skill.lower()
            if any(kw in skill_lower for kw in keywords):
                matched.append(skill)
        
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

def main():
    print("=== GENERATING CVs & COVER LETTERS ===\n")
    
    try:
        base_cv = load_base_cv()
        matches = load_vacancy_matches()
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("Make sure base_cv.json and vacancy_matches.json exist in data/ folder.")
        return 1
    
    selected = [m for m in matches if m.get('ad_id') in SELECTED_IDS]
    print(f"Found {len(selected)} of {len(SELECTED_IDS)} selected vacancies.")
    
    if len(selected) != len(SELECTED_IDS):
        found_ids = [m.get('ad_id') for m in selected]
        missing = [id for id in SELECTED_IDS if id not in found_ids]
        print(f"WARNING: Missing IDs: {missing}")
    
    if not selected:
        print("No vacancies to process.")
        return 0
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for idx, job in enumerate(selected, 1):
        title = job.get('title', '')
        company = job.get('company', '')
        ad_id = job.get('ad_id', f'vakance_{idx}')
        ranked_experience = job.get('ranked_experience', [])
        matched_skills = job.get('matched_skills', [])
        
        print(f"\n[{idx}/{len(selected)}] Processing: {title} @ {company}")
        
        cv_html = generate_ai_optimized_cv(job, base_cv, ranked_experience, matched_skills)
        company_clean = company.replace(' ', '_').replace('/', '_').replace('\\', '_')
        job_folder = OUTPUT_DIR / f"{ad_id}_{company_clean}"
        job_folder.mkdir(parents=True, exist_ok=True)
        
        cv_path = job_folder / "CV_optimized.html"
        cv_path.write_text(cv_html, encoding='utf-8')
        print(f"  ✅ CV saved: {cv_path}")
        
        best_exp_obj = ranked_experience[0] if ranked_experience else None
        if best_exp_obj:
            best_exp_text = f"{best_exp_obj.get('title')} @ {best_exp_obj.get('company')} ({best_exp_obj.get('period')})"
        else:
            best_exp_text = "Relevant professional experience"
        
        cl_html = generate_cover_letter(job, best_exp_text, base_cv, matched_skills)
        cl_path = job_folder / "Cover_Letter.html"
        cl_path.write_text(cl_html, encoding='utf-8')
        print(f"  ✅ Cover letter saved: {cl_path}")
        
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
        
        txt_path = job_folder / "Cover_Letter.txt"
        txt_path.write_text(cover_text, encoding='utf-8')
        print(f"  📄 Cover letter text saved: {txt_path}")
        
        url = job.get('url')
        if url:
            webbrowser.open(url)
            print(f"  🌐 Opened URL: {url}")
        else:
            print(f"  ⚠️ No URL for this vacancy")
    
    print(f"\n=== ALL DONE! ===")
    print(f"Output folder: {OUTPUT_DIR}")
    return 0

if __name__ == "__main__":
    sys.exit(main())