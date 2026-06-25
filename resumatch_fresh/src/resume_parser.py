import re, json, spacy, pdfplumber, docx
from pathlib import Path
from typing import Optional

SKILLS_DB = [
    "python","java","javascript","typescript","c++","c#","c","ruby","go","golang",
    "rust","swift","kotlin","scala","r","matlab","perl","php","bash","shell","dart",
    "html","css","react","angular","vue","svelte","next.js","tailwind","bootstrap",
    "jquery","webpack","sass","node.js","django","flask","fastapi","spring","express",
    "rails","laravel","asp.net","graphql","rest","restful","grpc",
    "machine learning","deep learning","nlp","natural language processing",
    "computer vision","tensorflow","pytorch","keras","scikit-learn","pandas","numpy",
    "scipy","matplotlib","seaborn","plotly","xgboost","lightgbm","spacy","nltk",
    "opencv","transformers","sql","mysql","postgresql","sqlite","mongodb","cassandra",
    "redis","elasticsearch","hadoop","spark","kafka","airflow","dbt","snowflake",
    "bigquery","redshift","databricks","aws","azure","gcp","google cloud","docker",
    "kubernetes","k8s","terraform","ansible","jenkins","ci/cd","github actions",
    "linux","unix","nginx","git","github","gitlab","jira","agile","scrum","devops",
    "microservices","api","tdd","oop","tableau","power bi","looker","grafana",
    "communication","leadership","teamwork","problem solving","project management",
]

def _load_spacy():
    for m in ("en_core_web_lg","en_core_web_md","en_core_web_sm"):
        try: return spacy.load(m)
        except OSError: continue
    raise RuntimeError("No spaCy model found. Run: python -m spacy download en_core_web_sm")

NLP = _load_spacy()

def extract_text_from_pdf(path):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t: text.append(t)
    return "\n".join(text)

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_text(path):
    ext = Path(path).suffix.lower()
    if ext == ".pdf": return extract_text_from_pdf(path)
    elif ext in (".docx",".doc"): return extract_text_from_docx(path)
    else:
        with open(path,"r",errors="ignore") as f: return f.read()

def extract_email(text):
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else None

def extract_phone(text):
    m = re.search(r"(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,4}\)?[\s\-.]?)?\d{3,4}[\s\-.]?\d{4}", text)
    return m.group(0).strip() if m else None

def extract_linkedin(text):
    m = re.search(r"linkedin\.com/in/[\w\-]+", text, re.I)
    return m.group(0) if m else None

def extract_github(text):
    m = re.search(r"github\.com/[\w\-]+", text, re.I)
    return m.group(0) if m else None

def extract_name_spacy(text):
    doc = NLP(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON": return ent.text.strip()
    for line in text.splitlines():
        line = line.strip()
        if line and not re.search(r"[<>@#]", line) and len(line.split()) <= 5:
            return line
    return None

def extract_orgs_spacy(text):
    doc = NLP(text[:3000])
    return list({ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"})

SECTION_HEADERS = {
    "education":      r"(?i)(education|academic|qualification|degree)",
    "experience":     r"(?i)(experience|employment|work history|career)",
    "skills":         r"(?i)(skills?|technical skills?|competencies|technologies)",
    "projects":       r"(?i)(projects?|portfolio|side projects?)",
    "certifications": r"(?i)(certif|licenses?|credentials?)",
    "summary":        r"(?i)(summary|objective|profile|about me)",
}

def split_sections(text):
    lines = text.splitlines()
    sections = {k: [] for k in SECTION_HEADERS}
    sections["other"] = []
    current = "other"
    for line in lines:
        matched = False
        for sec, pattern in SECTION_HEADERS.items():
            if re.search(pattern, line) and len(line.strip()) < 60:
                current = sec; matched = True; break
        if not matched: sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}

DEGREE_RE = re.compile(
    r"(B\.?Tech|B\.?E\.?|B\.?Sc?\.?|M\.?Tech|M\.?Sc?\.?|MBA|Ph\.?D\.?|"
    r"Bachelor|Master|Doctorate|Associate|Diploma|B\.?A\.?|M\.?A\.?|BCA|MCA)[^\n]{0,80}", re.I)
YEAR_RE = re.compile(r"\b((19|20)\d{2})\b")

def extract_skills(text):
    text_lower = text.lower()
    found = set()
    for skill in SKILLS_DB:
        pattern = r"(?<![a-zA-Z0-9_\-])" + re.escape(skill) + r"(?![a-zA-Z0-9_\-])"
        if re.search(pattern, text_lower): found.add(skill)
    return sorted(found)

def extract_education(text):
    entries = []
    for m in DEGREE_RE.finditer(text):
        entry = m.group(0).strip()
        years = [y[0] for y in YEAR_RE.findall(entry)]
        entries.append({"degree": entry, "years": years})
    return entries

def extract_experience(text):
    date_re = re.compile(
        r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|"
        r"Dec(?:ember)?|Present|Current)[,\s]*(\d{4})?", re.I)
    entries = []
    for block in re.split(r"\n{2,}", text):
        block = block.strip()
        if not block: continue
        years = [y[0] for y in YEAR_RE.findall(block)]
        dates = [" ".join(d).strip() for d in date_re.findall(block)]
        entries.append({"description": block[:300], "years": years, "dates_mentioned": dates})
    return entries[:10]

def extract_projects(text):
    entries = []
    for block in re.split(r"\n{2,}|\n(?=[A-Z•\-\*])", text):
        block = block.strip().lstrip("•-* ")
        if len(block) > 20: entries.append(block[:400])
    return entries[:10]

def extract_certifications(text):
    entries = []
    for line in text.splitlines():
        line = line.strip().lstrip("•-* ")
        if len(line) >= 3: entries.append(line)
    return entries[:20]

def parse_resume(file_path):
    raw_text = extract_text(file_path)
    sections = split_sections(raw_text)
    return {
        "raw_text":       raw_text,
        "name":           extract_name_spacy(raw_text),
        "email":          extract_email(raw_text),
        "phone":          extract_phone(raw_text),
        "linkedin":       extract_linkedin(raw_text),
        "github":         extract_github(raw_text),
        "skills":         extract_skills(raw_text),
        "education":      extract_education(sections.get("education","") or raw_text),
        "experience":     extract_experience(sections.get("experience","") or ""),
        "projects":       extract_projects(sections.get("projects","") or ""),
        "certifications": extract_certifications(sections.get("certifications","") or ""),
        "summary":        sections.get("summary",""),
        "organisations":  extract_orgs_spacy(raw_text),
    }
