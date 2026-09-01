"""
match_cv.py
-----------
Salīdzina base_cv.json (pamata CV, strukturēts) ar vacancies_live.csv
(aktuālo vakanču sarakstu) un katrai vakancei sagatavo:

  1. atbilstības punktu skaitu (match_score) katrai darba pieredzes
     pozīcijai no CV;
  2. sarindotu pieredzes sarakstu (visatbilstošākā -> mazāk atbilstošā),
     ko vēlāk izmantos, gatavojot pielāgotu CV;
  3. sarakstu ar prasmēm/atslēgvārdiem, kas sakrīt ar vakances nosaukumu.

PIEZĪME par datiem: vacancies_live.csv kolonnās NAV pilna vakances
apraksta (tikai title, company, city u.c.), tāpēc šī versija salīdzina
CV ar vakances NOSAUKUMU un UZŅĒMUMU. Tas ir labs pirmais filtrs, bet
precīzāku atbilstību (pēc pilna apraksta) varēs pievienot vēlāk, ja
skripts lasīs arī vakances 'url' saturu (nākamais solis).

Ieejas faili (relatīvi pret šo skriptu vai norādīti ar argumentiem):
  data/base_cv.json
  data/vacancies_live.csv

Izejas faili:
  data/vacancy_matches.csv   -- pārskata tabula (viena rinda / vakance)
  data/vacancy_matches.json  -- pilna sarindotā informācija katrai vakancei
                                 (izmantos nākamajā solī, ģenerējot
                                 pielāgotos CV)
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# -----------------------------------------------------------------
# Palīgfunkcijas
# -----------------------------------------------------------------

STOPWORDS = {
    "and", "the", "for", "with", "of", "a", "an", "un", "ar", "no", "uz",
    "in", "on", "to", "at", "or", "as", "is", "are", "&",
}


def tokenize(text: str) -> set:
    """Sadala tekstu vārdos (mazie burti, bez pieturzīmēm, bez stopvārdiem)."""
    if not text:
        return set()
    words = re.findall(r"[a-zA-ZāčēģīķļņōŗšūžĀČĒĢĪĶĻŅŌŖŠŪŽ0-9\+\-]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 1}


def load_base_cv(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_experience_keyword_sets(cv: dict) -> list:
    """
    Katrai darba pieredzes pozīcijai izveido atslēgvārdu kopu no:
    title + keywords lauka. Atgriež sarakstu ar vārdnīcām.
    """
    experiences = []
    for exp in cv.get("experience", []):
        kw_text = " ".join(exp.get("keywords", [])) + " " + exp.get("title", "")
        experiences.append({
            "company": exp.get("company"),
            "title": exp.get("title"),
            "period": exp.get("period"),
            "keywords": set(k.lower() for k in exp.get("keywords", [])),
            "tokens": tokenize(kw_text),
            "achievements": exp.get("achievements", []),
        })
    return experiences


def build_skill_pool(cv: dict) -> set:
    """Apvieno visas prasmes no skills sadaļas vienā kopā (mazie burti)."""
    pool = set()
    skills = cv.get("skills", {})
    for _, items in skills.items():
        for item in items:
            pool.add(item.lower())
    return pool


def score_experience_for_vacancy(exp: dict, vacancy_tokens: set) -> int:
    """
    Vienkāršs punktu skaits: cik CV pieredzes atslēgvārdu/tokenu
    sakrīt ar vakances nosaukuma tokeniem (tieša sakritība vai
    daļēja sakritība - viens vārds ietverts otrā).
    """
    score = 0
    for vt in vacancy_tokens:
        for et in exp["tokens"]:
            if vt == et or vt in et or et in vt:
                score += 1
                break
    return score


def matched_skills_for_vacancy(skill_pool: set, vacancy_tokens: set) -> list:
    matched = []
    for skill in skill_pool:
        skill_tokens = tokenize(skill)
        if skill_tokens & vacancy_tokens:
            matched.append(skill)
    return sorted(matched)


# -----------------------------------------------------------------
# Galvenā loģika
# -----------------------------------------------------------------

def process(base_cv_path: Path, vacancies_csv_path: Path,
            out_csv_path: Path, out_json_path: Path) -> None:

    if not base_cv_path.exists():
        sys.exit(f"KĻŪDA: nav atrasts {base_cv_path}")
    if not vacancies_csv_path.exists():
        sys.exit(f"KĻŪDA: nav atrasts {vacancies_csv_path}")

    cv = load_base_cv(base_cv_path)
    experiences = build_experience_keyword_sets(cv)
    skill_pool = build_skill_pool(cv)

    results_full = []      # pilnai JSON izejai
    results_summary = []   # CSV pārskatam

    with open(vacancies_csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            title = row.get("title", "") or ""
            company = row.get("company", "") or ""
            vacancy_tokens = tokenize(title) | tokenize(company)

            # sarindo visas pieredzes pozīcijas pēc atbilstības
            ranked = []
            for exp in experiences:
                score = score_experience_for_vacancy(exp, vacancy_tokens)
                ranked.append({
                    "company": exp["company"],
                    "title": exp["title"],
                    "period": exp["period"],
                    "score": score,
                    "achievements": exp["achievements"],
                })
            ranked.sort(key=lambda x: x["score"], reverse=True)

            matched_skills = matched_skills_for_vacancy(skill_pool, vacancy_tokens)

            entry = {
                "ad_id": row.get("ad_id"),
                "company": company,
                "title": title,
                "city": row.get("city"),
                "url": row.get("url"),
                "matched_skills": matched_skills,
                "ranked_experience": ranked,
            }
            results_full.append(entry)

            top_exp = ranked[0] if ranked else {}
            results_summary.append({
                "ad_id": row.get("ad_id"),
                "company": company,
                "title": title,
                "city": row.get("city"),
                "top_match_experience": (
                    f"{top_exp.get('title', '')} @ {top_exp.get('company', '')}"
                    if top_exp else ""
                ),
                "top_match_score": top_exp.get("score", 0),
                "matched_skills": "; ".join(matched_skills),
                "url": row.get("url"),
            })

    # CSV izeja
    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["ad_id", "company", "title", "city",
                      "top_match_experience", "top_match_score",
                      "matched_skills", "url"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results_summary)

    # JSON izeja (izmantos, gatavojot pielāgotos CV)
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(results_full, f, ensure_ascii=False, indent=2)

    print(f"Apstrādātas {len(results_summary)} vakances.")
    print(f"CSV pārskats saglabāts: {out_csv_path}")
    print(f"Pilnā JSON informācija saglabāta: {out_json_path}")


def main():
    parser = argparse.ArgumentParser(description="Salīdzina base_cv.json ar vacancies_live.csv")
    parser.add_argument("--cv", default="data/base_cv.json", help="Ceļš uz base_cv.json")
    parser.add_argument("--vacancies", default="data/vacancies_live.csv", help="Ceļš uz vacancies_live.csv")
    parser.add_argument("--out-csv", default="data/vacancy_matches.csv", help="Izejas CSV ceļš")
    parser.add_argument("--out-json", default="data/vacancy_matches.json", help="Izejas JSON ceļš")
    args = parser.parse_args()

    process(Path(args.cv), Path(args.vacancies), Path(args.out_csv), Path(args.out_json))


if __name__ == "__main__":
    main()
