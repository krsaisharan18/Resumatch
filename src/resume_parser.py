import re, spacy, pdfplumber, docx
from pathlib import Path

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
    raise RuntimeError("No spaCy model found.")

NLP = _load_spacy()

# ── text extraction ──────────────────────────────────────────────────────────

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
    if ext == ".pdf":   return extract_text_from_pdf(path)
    if ext in (".docx",".doc"): return extract_text_from_docx(path)
    with open(path,"r",errors="ignore") as f: return f.read()

# ── hyperlink extraction (URLs embedded as clickable links, not visible text) ─

def extract_hyperlinks_from_pdf(path):
    """pdfplumber text extraction misses hyperlinks that show as icons/buttons.
    Pull them directly from page annotations."""
    links = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                for annot in (page.annots or []):
                    uri = annot.get("uri") or annot.get("URI") or ""
                    if uri and uri.startswith("http"):
                        links.append(uri)
    except Exception:
        pass
    return links

def extract_hyperlinks_from_docx(path):
    """DOCX stores hyperlinks in document relationships, not paragraph text."""
    links = []
    try:
        doc = docx.Document(path)
        for rel in doc.part.rels.values():
            if "hyperlink" in rel.reltype.lower():
                target = rel._target
                if isinstance(target, str) and target.startswith("http"):
                    links.append(target)
    except Exception:
        pass
    return links

def get_extra_urls(path):
    ext = Path(path).suffix.lower()
    if ext == ".pdf":           return extract_hyperlinks_from_pdf(path)
    if ext in (".docx",".doc"): return extract_hyperlinks_from_docx(path)
    return []

# ── contact extractors ───────────────────────────────────────────────────────

def extract_email(text):
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else None

def extract_phone(text):
    m = re.search(
        r"(?:\+?\d{1,3}[\s\-.]?)?(?:\(?\d{2,4}\)?[\s\-.]?)?\d{3,4}[\s\-.]?\d{4}", text)
    return m.group(0).strip() if m else None

# Non-profile GitHub paths to ignore (org pages, feature pages, etc.)
_GH_IGNORE = {"features","marketplace","topics","explore","pricing","about",
               "contact","team","organizations","orgs","settings","pulls",
               "issues","sponsors","readme"}

def extract_linkedin(text):
    """Match linkedin.com/in/username in any URL format, including hyperlinks."""
    # Normalise backslashes that sometimes appear after PDF text extraction
    text = text.replace("\\", "/")
    # Match http://linkedin.com/in/user, www.linkedin.com/in/user, linkedin.com/in/user
    m = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/([\w\-\.%]{2,60})/?",
        text, re.I)
    if m:
        return "linkedin.com/in/" + m.group(1).rstrip("/")
    return None

def extract_github(text):
    """Match github.com/username, skipping non-profile paths."""
    text = text.replace("\\", "/")
    m = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/([\w\-]{1,39})(?:/[\w\-\.]*)?(?:\s|$|[,;\)])",
        text, re.I)
    if m:
        user = m.group(1)
        if user.lower() not in _GH_IGNORE:
            return "github.com/" + user
    # Fallback: simpler pattern without trailing context requirement
    m = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/([\w\-]{1,39})",
        text, re.I)
    if m:
        user = m.group(1)
        if user.lower() not in _GH_IGNORE:
            return "github.com/" + user
    return None

def extract_name_spacy(text):
    doc = NLP(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON": return ent.text.strip()
    for line in text.splitlines():
        line = line.strip()
        if line and not re.search(r"[<>@#|•]", line) and 1 < len(line.split()) <= 5:
            return line
    return None

def extract_orgs_spacy(text):
    doc = NLP(text[:3000])
    return list({ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"})

# ── section splitting ────────────────────────────────────────────────────────

SECTION_HEADERS = {
    "summary":        r"(?i)^\s*(summary|objective|profile|about\s*me|introduction|overview)\s*$",
    "education":      r"(?i)^\s*(education|academic|qualification|degree|schooling)\s*$",
    "experience":     r"(?i)^\s*(experience|employment|work\s*history|career|internship|positions?|roles?|professional\s*background)\s*$",
    "skills":         r"(?i)^\s*(skills?|technical\s*skills?|competencies|technologies|tools|languages|frameworks?|core\s*skills?)\s*$",
    "projects":       r"(?i)^\s*(projects?|portfolio|side\s*projects?|personal\s*projects?|academic\s*projects?|key\s*projects?|notable\s*projects?|selected\s*projects?)\s*$",
    "certifications": r"(?i)^\s*(certif\w*|licenses?|credentials?|courses?|training|achievements?|awards?|honours?)\s*$",
}

def split_sections(text):
    lines = text.splitlines()
    sections = {k: [] for k in SECTION_HEADERS}
    sections["other"] = []
    current = "other"
    for line in lines:
        matched = False
        stripped = line.strip()
        if stripped and len(stripped) < 60:
            for sec, pattern in SECTION_HEADERS.items():
                if re.search(pattern, stripped):
                    current = sec; matched = True; break
        if not matched:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}

# ── field extractors ─────────────────────────────────────────────────────────

DEGREE_RE = re.compile(
    r"(B\.?Tech|B\.?E\.?|B\.?Sc?\.?|M\.?Tech|M\.?Sc?\.?|MBA|Ph\.?D\.?|"
    r"Bachelor|Master|Doctorate|Associate|Diploma|B\.?A\.?|M\.?A\.?|BCA|MCA)"
    r"[^\n]{0,80}", re.I)
YEAR_RE = re.compile(r"\b((19|20)\d{2})\b")

def extract_skills(text):
    text_lower = text.lower()
    found = set()
    for skill in SKILLS_DB:
        pat = r"(?<![a-zA-Z0-9_\-])" + re.escape(skill) + r"(?![a-zA-Z0-9_\-])"
        if re.search(pat, text_lower): found.add(skill)
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
        years  = [y[0] for y in YEAR_RE.findall(block)]
        dates  = [" ".join(d).strip() for d in date_re.findall(block)]
        entries.append({"description": block[:300], "years": years, "dates_mentioned": dates})
    return entries[:10]

# Action verbs that signal a real project description
_ACTION_RE = re.compile(
    r"\b(built|developed|created|designed|implemented|deployed|integrated|"
    r"engineered|architected|automated|optimized|improved|reduced|increased|"
    r"led|managed|researched|analyzed|trained|fine.tuned|scraped|parsed|"
    r"extracted|visualized|published|launched|delivered|produced|generated|"
    r"trained|evaluated|benchmarked|contributed|collaborated|maintained)\b", re.I)

# Patterns that indicate a line is a skills list, NOT a project
_SKILLS_LIST_RE = re.compile(
    r"^[\w\s\.\+\#\/\-\,\|&]+$")   # only alphanum + punctuation, no sentence structure

def extract_projects(text):
    if not text.strip():
        return []
    entries = []
    # Split ONLY on blank lines — consecutive lines belong to the same project block.
    # Splitting on \n(?=[A-Z]) was breaking multi-line descriptions into fragments.
    blocks = re.split(r"\n{2,}", text)
    for block in blocks:
        block = block.strip().lstrip("•-*→▸ ")
        if len(block) < 40:
            continue
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        full = " ".join(lines)

        # Reject if it's a comma/pipe-separated tech list (no sentence verbs)
        if _SKILLS_LIST_RE.match(full) and not _ACTION_RE.search(full):
            continue
        # Reject very short entries with no action verb (likely a heading or skill row)
        if len(full) < 80 and not _ACTION_RE.search(full):
            continue
        entries.append(block[:400])
    return entries[:10]

def extract_certifications(text):
    entries = []
    for line in text.splitlines():
        line = line.strip().lstrip("•-* ")
        if len(line) >= 6:
            entries.append(line)
    return entries[:20]

# ── main ─────────────────────────────────────────────────────────────────────

def parse_resume(file_path):
    raw_text  = extract_text(file_path)
    # Pull hyperlinks that may not appear as plain text (clickable icons in PDFs/DOCX)
    hyperlinks = get_extra_urls(file_path)
    # Append hyperlink URLs to the search corpus for contact field extraction
    contact_corpus = raw_text + "\n" + "\n".join(hyperlinks)

    sections  = split_sections(raw_text)
    return {
        "raw_text":       raw_text,
        "name":           extract_name_spacy(raw_text),
        "email":          extract_email(contact_corpus),
        "phone":          extract_phone(contact_corpus),
        "linkedin":       extract_linkedin(contact_corpus),
        "github":         extract_github(contact_corpus),
        "skills":         extract_skills(raw_text),
        "education":      extract_education(sections.get("education","") or raw_text),
        "experience":     extract_experience(sections.get("experience","") or ""),
        "projects":       extract_projects(sections.get("projects","") or ""),
        "certifications": extract_certifications(sections.get("certifications","") or ""),
        "summary":        sections.get("summary",""),
        "organisations":  extract_orgs_spacy(raw_text),
    }
