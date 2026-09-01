import json
import sys
from pathlib import Path
from datetime import datetime
import webbrowser

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "applications_selected"  # jauna mape, lai nesajauc

# ------------------------------------------------------------
# ŠEIT IERAKSTI SAVU 6 VAKANČU AD_ID (no vacancy_matches.csv)
SELECTED_IDS = [
    "1635673",  # Vecākais datu arhitekts
    "1643199",  # Vecākais datu inženieris
    "1646879",  # Biznesa virziena vadītājs
    "1647683",  # Projekta plānošanas direktors
    "1647714",  # Loģistikas direktors
    "1643162",  # Vecākais datu inženieris
]
# ------------------------------------------------------------

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

def generate_cv_html(job, best_exp, matched_skills):
    title = job.get('title', '')
    company = job.get('company', '')
    skills_list = "".join(f"<li>{s}</li>" for s in matched_skills) if matched_skills else "<li>Prasmes atbilstoši amata aprakstam</li>"
    
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

def generate_cover_letter_html(job, best_exp, matched_skills):
    title = job.get('title', '')
    company = job.get('company', '')
    skills_str = ", ".join(matched_skills) if matched_skills else "prasmes, kas atbilst amata prasībām"
    
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
    print("=== ĢENERĒ TIKAI 6 ATLASĪTĀS VAKANCES ===\n")
    
    matches_file = DATA_DIR / "vacancy_matches.json"
    if not matches_file.exists():
        print(f"KĻŪDA: Nav atrasts {matches_file}")
        return 1
    
    with open(matches_file, 'r', encoding='utf-8') as f:
        all_matches = json.load(f)
    
    # Filtrē tikai tās, kas ir SELECTED_IDS
    selected = []
    for entry in all_matches:
        if entry.get('ad_id') in SELECTED_IDS:
            selected.append(entry)
    
    print(f"Atrastas {len(selected)} no {len(SELECTED_IDS)} atlasītajām vakancēm.")
    
    if len(selected) != len(SELECTED_IDS):
        print("BRĪDINĀJUMS: Dažas vakances netika atrastas. Pārbaudi ad_id.")
        found_ids = [e.get('ad_id') for e in selected]
        missing = [id for id in SELECTED_IDS if id not in found_ids]
        print(f"Trūkst: {missing}")
    
    if not selected:
        print("Nav nevienas vakances. Pabeidzu.")
        return 0
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for idx, entry in enumerate(selected, 1):
        job = entry
        ranked = entry.get('ranked_experience', [])
        
        # Paņem labāko pieredzi (pirmo no saraksta)
        best_exp_obj = ranked[0] if ranked else None
        if best_exp_obj:
            best_exp_text = f"{best_exp_obj.get('title')} @ {best_exp_obj.get('company')} ({best_exp_obj.get('period')})"
            if best_exp_obj.get('achievements'):
                best_exp_text += " — " + "; ".join(best_exp_obj['achievements'][:2])
        else:
            best_exp_text = "Pieredze atbilstoši amata aprakstam"
        
        matched_skills = entry.get('matched_skills', [])
        
        job_id = entry.get('ad_id', f"vakance_{idx}")
        company_clean = entry.get('company', '').replace(' ', '_').replace('/', '_')
        job_folder = OUTPUT_DIR / f"{job_id}_{company_clean}"
        job_folder.mkdir(parents=True, exist_ok=True)
        
        print(f"\n[{idx}/{len(selected)}] Apstrādā: {entry.get('title')} @ {entry.get('company')}")
        
        # Ģenerē CV
        cv_html = generate_cv_html(entry, best_exp_text, matched_skills)
        cv_path = job_folder / "CV_pielagots.html"
        cv_path.write_text(cv_html, encoding='utf-8')
        print(f"  ✅ CV saglabāts: {cv_path}")
        
        # Ģenerē pavadvēstuli
        cl_html = generate_cover_letter_html(entry, best_exp_text, matched_skills)
        cl_path = job_folder / "Pavadvēstule.html"
        cl_path.write_text(cl_html, encoding='utf-8')
        print(f"  ✅ Pavadvēstule saglabāta: {cl_path}")
        
        # Saglabā pavadvēstules tekstu
        cover_text = f"""Rīgā, {datetime.now().strftime('%d.%m.%Y')}

Pieteikums vakancei: {entry.get('title')} @ {entry.get('company')}

Sveiki! Uzzināju par {entry.get('title')} amata vietu uzņēmumā {entry.get('company')} un vēlos pieteikties.

Man ir pieredze šādā amatā: {best_exp_text}.

Manas prasmes, kas atbilst Jūsu prasībām: {', '.join(matched_skills) if matched_skills else 'prasmes, kas atbilst amata prasībām'}.

Esmu pārliecināts, ka spēšu sniegt nozīmīgu ieguldījumu Jūsu komandā. Tāpēc lūdzu izskatīt manu pieteikumu un CV.

Ar cieņu,
{CONTACT['vards']}"""
        
        txt_path = job_folder / "Pavadvēstule.txt"
        txt_path.write_text(cover_text, encoding='utf-8')
        print(f"  📄 Pavadvēstules teksts saglabāts: {txt_path}")
        
        # Atver URL
        url = entry.get('url')
        if url:
            webbrowser.open(url)
            print(f"  🌐 Atvērts URL: {url}")
        else:
            print(f"  ⚠️ Vakancei nav URL")
    
    print(f"\n=== GATAVS! ===")
    print(f"Mapes saglabātas: {OUTPUT_DIR}")
    return 0

if __name__ == "__main__":
    sys.exit(main())