import json
import sys
from pathlib import Path
from datetime import datetime
import webbrowser
import os

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "applications"
THRESHOLD_SCORE = 0

# --- Tavs CV profils (no Januss_Barila_Standard_CV.pdf) ---
CONTACT = {
    "vards": "Januss Barila",
    "telefons": "+371 25 512 631",
    "epasts": "yanushbarila@inbox.lv",
    "linkedin": "linkedin.com/in/yanush-barila"
}

PROFESSIONAL_SUMMARY = (
    "Business and data analytics professional with 6+ years of experience across "
    "management reporting, process improvement, financial and workforce analysis, "
    "supply chain, forecasting and systems delivery. Skilled at turning fragmented "
    "operational data into reliable KPIs, dashboards, forecasts and recommendations. "
    "Hands-on with Power BI, DAX, Power Query, SQL, Python, Excel, HORIZON, IFS ERP and SAP."
)

# --- Funkcijas HTML ģenerēšanai ---
def generate_cv_html(job, match):
    title = job.get('title', '')
    company = job.get('company', '')
    best_exp = match.get('best_experience', 'Nav specifiskas atbilstības.')
    skills = match.get('matched_skills', [])
    skills_list = "".join(f"<li>{s}</li>" for s in skills) if skills else "<li>Prasmes atbilstoši amata aprakstam</li>"

    html = f"""<!DOCTYPE html>
<html lang="lv">
<head>
    <meta charset="UTF-8">
    <title>CV - {CONTACT['vards']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; max-width: 800px; margin: 40px auto; line-height: 1.5; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #2980b9; margin-top: 24px; }}
        .header {{ text-align: center; }}
        .contact {{ font-size: 14px; color: #7f8c8d; }}
        .section {{ margin-bottom: 20px; }}
        ul {{ list-style-type: square; }}
        .footer {{ margin-top: 30px; font-size: 12px; color: #bdc3c7; text-align: center; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{CONTACT['vards']}</h1>
        <div class="contact">📞 {CONTACT['telefons']} | ✉ {CONTACT['epasts']} | 🔗 {CONTACT['linkedin']}</div>
    </div>
    
    <div class="section">
        <h2>Profesionālais profils</h2>
        <p><strong>Business & Data Analyst | Process & Operations Improvement</strong></p>
        <p>{PROFESSIONAL_SUMMARY}</p>
    </div>
    
    <div class="section">
        <h2>Atbilstošā darba pieredze</h2>
        <p><strong>{best_exp}</strong></p>
    </div>
    
    <div class="section">
        <h2>Atslēgas prasmes</h2>
        <ul>{skills_list}</ul>
    </div>
    
    <div class="section">
        <h2>Papildus informācija</h2>
        <p><strong>Valodas:</strong> krievu (dzimtā), latviešu (teicami), angļu (profesionāli).</p>
        <p><strong>Sertifikāti:</strong> Certified Internal ISO Auditor.</p>
    </div>
    
    <div class="footer">Ģenerēts {datetime.now().strftime('%d.%m.%Y')} — pielāgots vakancei {title} @ {company}</div>
</body>
</html>"""
    return html

def generate_cover_letter_html(job, match):
    title = job.get('title', '')
    company = job.get('company', '')
    best_exp = match.get('best_experience', '')
    skills = match.get('matched_skills', [])
    skills_str = ", ".join(skills) if skills else "prasmes, kas atbilst amata prasībām"

    html = f"""<!DOCTYPE html>
<html lang="lv">
<head>
    <meta charset="UTF-8">
    <title>Pavadvēstule - {CONTACT['vards']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; max-width: 700px; margin: 40px auto; line-height: 1.6; }}
        .date {{ text-align: right; }}
        .subject {{ font-weight: bold; margin-top: 20px; }}
        .signature {{ margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="date">Rīgā, {datetime.now().strftime('%d.%m.%Y')}</div>
    
    <div class="subject">Pieteikums vakancei: {title} @ {company}</div>
    
    <p>Sveiki! Uzzināju par <strong>{title}</strong> amata vietu uzņēmumā <strong>{company}</strong> un vēlos pieteikties.</p>
    
    <p>Man ir pieredze šādā amatā: <strong>{best_exp}</strong>.</p>
    
    <p>Manas prasmes, kas atbilst Jūsu prasībām: <strong>{skills_str}</strong>.</p>
    
    <p>Esmu pārliecināts, ka spēšu sniegt nozīmīgu ieguldījumu Jūsu komandā. Tāpēc lūdzu izskatīt manu pieteikumu un CV.</p>
    
    <p>Ar cieņu,</p>
    <div class="signature">{CONTACT['vards']}</div>
</body>
</html>"""
    return html

def main():
    print("=== PIETEIKUMU SAGATAVOŠANAS AUTOMATIZĀCIJA ===\n")
    
    matches_file = DATA_DIR / "vacancy_matches.json"
    if not matches_file.exists():
        print(f"KĻŪDA: Nav atrasts {matches_file}")
        print("Vispirms palaid match_cv.py")
        return 1
    
    with open(matches_file, 'r', encoding='utf-8') as f:
        all_matches = json.load(f)
    
    print(f"Atrastas {len(all_matches)} vakances datubāzē.")
    
    # Filtrē pēc sliekšņa
    top_matches = []
    for item in all_matches:
        best = item.get('best_match', {})
        score = best.get('score', 0)
        if score >= THRESHOLD_SCORE:
            top_matches.append(item)
    
    print(f"Atlasītas {len(top_matches)} vakances ar punktu skaitu >= {THRESHOLD_SCORE}.")
    
    if not top_matches:
        print("Nav nevienas vakances, kas atbilst slieksnim. Pabeidzu.")
        return 0
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for idx, item in enumerate(top_matches, 1):
        job = item.get('job', {})
        best_match = item.get('best_match', {})
        job_id = job.get('id', f"vakance_{idx}")
        company_clean = job.get('company', '').replace(' ', '_').replace('/', '_')
        job_folder = OUTPUT_DIR / f"{job_id}_{company_clean}"
        job_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[{idx}/{len(top_matches)}] Apstrādā: {job.get('title')} @ {job.get('company')}")
        
        # Saglabā CV HTML
        cv_html = generate_cv_html(job, best_match)
        cv_path = job_folder / "CV_pielagots.html"
        cv_path.write_text(cv_html, encoding='utf-8')
        print(f"  ✅ CV saglabāts: {cv_path}")
        
        # Saglabā pavadvēstuli HTML
        cl_html = generate_cover_letter_html(job, best_match)
        cl_path = job_folder / "Pavadvēstule.html"
        cl_path.write_text(cl_html, encoding='utf-8')
        print(f"  ✅ Pavadvēstule saglabāta: {cl_path}")
        
        # Saglabā pavadvēstules tekstu atsevišķā .txt failā (viegli kopēt)
        cover_text = f"""Rīgā, {datetime.now().strftime('%d.%m.%Y')}

Pieteikums vakancei: {job.get('title')} @ {job.get('company')}

Sveiki! Uzzināju par {job.get('title')} amata vietu uzņēmumā {job.get('company')} un vēlos pieteikties.

Man ir pieredze šādā amatā: {best_match.get('best_experience', '')}.

Manas prasmes, kas atbilst Jūsu prasībām: {', '.join(best_match.get('matched_skills', []))}.

Esmu pārliecināts, ka spēšu sniegt nozīmīgu ieguldījumu Jūsu komandā. Tāpēc lūdzu izskatīt manu pieteikumu un CV.

Ar cieņu,
{CONTACT['vards']}"""
        
        txt_path = job_folder / "Pavadvēstule.txt"
        txt_path.write_text(cover_text, encoding='utf-8')
        print(f"  📄 Pavadvēstules teksts saglabāts: {txt_path}")
        
        # Atver vakances URL
        url = job.get('url', '')
        if url:
            webbrowser.open(url)
            print(f"  🌐 Atvērts vakances URL: {url}")
        else:
            print(f"  ⚠️ Vakancei nav URL")
    
    print("\n=== GATAVS! ===")
    print(f"Visas pieteikumu mapes atrodas: {OUTPUT_DIR}")
    print("\nKā rīkoties tālāk:")
    print("1. Atver mapīti ar konkrēto vakanci.")
    print("2. Atver .html failu pārlūkā un saglabā kā PDF (Ctrl+P → Saglabāt kā PDF).")
    print("3. Atver .txt failu, nokopē pavadvēstules tekstu.")
    print("4. Pārlūkā jau atvērta vakance – ielīmē pavadvēstuli, pievieno PDF un nosūti.")
    return 0

if __name__ == "__main__":
    sys.exit(main())