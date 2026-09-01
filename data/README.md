# Job Application Pipeline 🚀

Automated CV and cover letter generator tailored to job vacancies.

This pipeline takes your CV, a list of job vacancies, and generates **personalised CVs and cover letters** for each selected role – all with a single command. It produces clean, professional PDFs ready for submission.

---

## ✨ Features

- **Automated matching** – compares your CV to each vacancy and highlights the most relevant experience
- **Personalised documents** – generates a custom CV and cover letter per job
- **Clean PDF output** – no browser headers, page numbers, or file paths
- **Professional naming** – `CV_YourName_Vacancy_YYYYMMDD.pdf`
- **Auto‑anonymisation** – replaces client/project names with generic placeholders
- **Typo correction** – automatically fixes common spelling errors (e.g., `RESEBA` → `RISEBA`)
- **One‑click batch processing** – run the entire pipeline with a single command or double‑click

---

## 📁 Project Structure

```
Python Job Applications/
├── data/
│   ├── base_cv.json          # Your structured CV (not included in repo)
│   └── vacancies_live.csv    # Job listings (not included in repo)
├── applications_ai_optimized/   # Generated outputs (local only)
├── pipeline.py               # Main pipeline script
├── match_cv.py               # Matching logic
├── run_pipeline.bat          # One‑click launcher (Windows)
├── convert_html_to_pdf.py    # PDF converter
├── generate_*.py             # Generation scripts
└── .gitignore                # Excludes personal data
```

---

## 🛠️ Requirements

- **Python 3.10+** (tested with portable Python)
- **Microsoft Edge** or **Google Chrome** (for PDF conversion)
- **Git** (optional – for version control)

No external packages are required – all dependencies are from Python’s standard library.

---

## 📦 Setup

### 1. Clone or download this repository

```bash
git clone https://github.com/JanussBarila/job-application-pipeline.git
cd job-application-pipeline
```

### 2. Prepare your CV

Create a `data/base_cv.json` file with your structured CV.  
Use the following format:

```json
{
  "contact": {...},
  "summary": "...",
  "core_expertise": [...],
  "experience": [
    {
      "company": "Company Name",
      "title": "Job Title",
      "period": "Jan 2020 - Dec 2022",
      "keywords": ["skill1", "skill2"],
      "achievements": ["Achievement 1", "Achievement 2"]
    }
  ],
  "education": [...],
  "skills": {...},
  "languages": {...}
}
```

### 3. Add job vacancies

Place your `vacancies_live.csv` in the `data/` folder.  
The CSV must contain at least these columns:
- `ad_id` – unique identifier
- `company` – employer name
- `title` – job title
- `city` – location
- `url` – link to the full vacancy

### 4. Configure your target vacancies

In `pipeline.py`, update the `SELECTED_IDS` list with the `ad_id` values of the jobs you want to apply for:

```python
SELECTED_IDS = [
    "1635673",
    "1643199",
    # add your IDs here
]
```

### 5. Update your contact details

Replace the placeholder values in `CONTACT` inside `pipeline.py`:

```python
CONTACT = {
    "vards": "Your Name",
    "telefons": "+371 12 345 678",
    "epasts": "your.email@example.com",
    "linkedin": "linkedin.com/in/your-profile",
    "github": "github.com/your-profile"
}
```

---

## 🚀 Running the pipeline

### Option A – Double‑click (Windows)

Just double‑click **`run_pipeline.bat`** – it will:
1. Copy the latest vacancies CSV (from a sibling project, if available)
2. Run the matching logic
3. Generate HTML and TXT files
4. Convert everything to clean PDFs

### Option B – Command line

```bash
python pipeline.py
```

Or with your portable Python:

```bash
"C:\Users\YourName\PythonPortable\python.exe" pipeline.py
```

### Option C – Run individual steps (advanced)

If you want to run steps separately:

```bash
python match_cv.py                 # Step 1: matching
python generate_ai_optimized_cv.py # Step 2: generate HTML/TXT
python convert_html_to_pdf.py      # Step 3: convert to PDF
```

---

## 📂 Output

All generated files are saved in `applications_ai_optimized/`:

```
applications_ai_optimized/
├── 1635673_CompanyName/
│   ├── CV_YourName_Vacancy_20260901.html
│   ├── CV_YourName_Vacancy_20260901.pdf    ← ready to send
│   ├── CoverLetter_YourName_Vacancy_20260901.html
│   ├── CoverLetter_YourName_Vacancy_20260901.pdf  ← ready to send
│   └── CoverLetter_YourName_Vacancy_20260901.txt
└── ...
```

- **PDFs** are clean – no file paths, no page numbers, no extra headers.
- **HTML** files are for reference.
- **TXT** files contain the cover letter text for easy copying into web forms.

---

## 🧠 How the matching works

1. The script loads your CV (`base_cv.json`).
2. For each vacancy, it compares the job title and company name with your work experience keywords.
3. It assigns a **score** to each experience entry.
4. The **highest‑scoring** experience is marked as "most relevant" and highlighted in the generated CV.
5. If no explicit match is found, the script falls back to using the first experience entry.

---

## 🔧 Customisation

### Change the filename structure

In `pipeline.py`, update these variables:

```python
NAME_PART = "YourName"          # appears in filenames
DATE_STR = datetime.now().strftime('%Y%m%d')  # format: 20260901
```

### Anonymise client names

Add or remove patterns in `CLIENT_ANONYMIZATION`:

```python
CLIENT_ANONYMIZATION = {
    r'\bERDA\b': 'SIA ERDA',
    r'\bBuvdizains\b': 'SIA Buvdizains',
}
```

### Auto‑fix typos

Extend the `TYPO_FIX` dictionary to correct common spelling errors automatically:

```python
TYPO_FIX = {
    r'\bEDISOFIT\b': 'EDISOFT',
    r'\bRESEBA\b': 'RISEBA',
    r'\bGrūga\b': 'Grupa',
}
```

---

## ⚠️ Important notes

- **Personal data is excluded from version control** – your `base_cv.json`, `vacancies_live.csv`, and all generated output stay local.
- **The pipeline expects a specific folder structure** – keep `data/` and `pipeline.py` in the same directory.
- **PDF conversion requires a browser** – Edge or Chrome must be installed.

---

## 🤝 Contributing

Found a bug or have an improvement? Feel free to open an issue or submit a pull request.

---

## 📜 License

MIT – use, modify, and share freely.

---

## 🧑‍💻 Author

Built by [Januss Barila](https://github.com/JanussBarila) – Business & Data Analyst with a passion for automation and practical AI.

---

**Happy applying!** 🎯