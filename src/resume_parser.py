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
    # -- generative AI / LLM stack (common in current student resumes) --
    "llm","large language model","generative ai","rag",
    "retrieval augmented generation","langchain","langgraph","mcp",
    "model context protocol","ollama","huggingface","hugging face","faiss",
    "pinecone","chromadb","vector database","vector search","embeddings",
    "prompt engineering","fine-tuning","openai","gemini","mistral","llama",
    "cnn","rnn","lstm","random forest",
    # -- web / backend extras --
    "socket.io","websocket","jwt","oauth","sqlalchemy","orm","pydantic",
    "postman","vs code","figma","vercel","firebase","render","heroku",
    "solidity","hardhat","blockchain","smart contracts","flutter",
    "cosine similarity","tf-idf",
]

# Aliases/synonyms that resolve to a canonical SKILLS_DB entry. This lets a resume
# saying "ML" and a JD saying "Machine Learning" match instead of silently missing
# each other because they used different phrasing for the same skill.
SKILL_ALIASES = {
    "ml": "machine learning",
    "dl": "deep learning",
    "js": "javascript",
    "ts": "typescript",
    "nodejs": "node.js",
    "node": "node.js",
    "expressjs": "express",
    "reactjs": "react",
    "react.js": "react",
    "vuejs": "vue",
    "vue.js": "vue",
    "nextjs": "next.js",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "genai": "generative ai",
    "gen ai": "generative ai",
    "llms": "llm",
    "oops": "oop",
    "object oriented programming": "oop",
    "object-oriented programming": "oop",
    "restful api": "rest",
    "restful apis": "rest",
    "rest api": "rest",
    "rest apis": "rest",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "socket io": "socket.io",
    "websockets": "websocket",
    "vscode": "vs code",
    "hugging face": "huggingface",
}

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

# Words/phrases that show up on line 1-3 of many templates but are NOT a person's name
_NAME_BLACKLIST = {
    "resume","cv","curriculum vitae","bio-data","biodata","profile","portfolio",
    "personal details","contact","contact information","address","summary",
    "objective","career objective","professional summary",
}
_NAME_JUNK_RE = re.compile(r"[@#|•<>\[\]{}]|https?://|www\.|\d{2,}")

def _looks_like_name(candidate):
    if not candidate:
        return False
    c = candidate.strip().strip(":-•").strip()
    if not c or c.lower() in _NAME_BLACKLIST:
        return False
    if _NAME_JUNK_RE.search(c):
        return False
    words = [w for w in c.split() if w]
    if not (1 < len(words) <= 5):
        return False
    # every word should look name-like: starts with a letter, mostly alphabetic
    for w in words:
        core = w.strip(".,")
        if not core or not core[0].isalpha():
            return False
        if not re.match(r"^[A-Za-z][A-Za-z\.\-']*$", core):
            return False
    # avoid picking up an all-lowercase sentence fragment
    if c == c.lower() and len(words) > 2:
        return False
    return True

def extract_name_spacy(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    head_lines = lines[:15]

    # 1) Ask spaCy for PERSON entities near the top of the document, then validate
    #    each candidate so we don't accidentally return a company/section header.
    head_text = "\n".join(head_lines)
    doc = NLP(head_text[:1000])
    persons = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    for p in persons:
        if _looks_like_name(p):
            return p

    # 2) Fallback: scan the first few non-empty lines for something name-shaped.
    #    Most resumes put the candidate's name on line 1-3, before any contact info.
    for line in head_lines[:6]:
        if _looks_like_name(line):
            return line

    # 3) Last resort: return the first (unvalidated) spaCy PERSON hit, if any.
    if persons:
        return persons[0]
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
    "projects":       r"(?i)^\s*(projects?|project\s*work|portfolio|side\s*projects?|personal\s*projects?|academic\s*projects?|key\s*projects?|notable\s*projects?|selected\s*projects?)\s*$",
    "certifications": r"(?i)^\s*(certif\w*(\s*(&|and)\s*accomplishments)?|licenses?|credentials?|courses?|training|achievements?|awards?|honours?|academic\s*and\s*extracurricular\s*achievements?)\s*$",
    "other_headers":  r"(?i)^\s*(extra[\s\-]*curricul\w*(\s*(&|and)?\s*(activities|leadership))?|activities|leadership|languages?\s*known|language\s*proficiency|interests?|hobbies)\s*$",
}

# Strip leading emoji/bullets/numbering and trailing colons/dashes so headers like
# "🚀 Projects:" or "2. TECHNICAL SKILLS -" still match the plain-word patterns below.
_HEADER_STRIP_RE = re.compile(
    r"^[\W_]*\d*[\.\)]?\s*|[\s:\-–—]+$", re.UNICODE)

def _clean_header_line(line):
    cleaned = _HEADER_STRIP_RE.sub("", line)
    return cleaned.strip()

def split_sections(text):
    lines = text.splitlines()
    sections = {k: [] for k in SECTION_HEADERS}
    sections["other"] = []
    current = "other"
    for line in lines:
        matched = False
        stripped = line.strip()
        if stripped and len(stripped) < 60:
            candidate = _clean_header_line(stripped)
            if candidate:
                for sec, pattern in SECTION_HEADERS.items():
                    if re.search(pattern, candidate):
                        current = sec; matched = True; break
        if not matched:
            sections[current].append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}

# ── field extractors ─────────────────────────────────────────────────────────

DEGREE_RE = re.compile(
    r"(?<![A-Za-z0-9\.])"
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
    for alias, canonical in SKILL_ALIASES.items():
        pat = r"(?<![a-zA-Z0-9_\-])" + re.escape(alias) + r"(?![a-zA-Z0-9_\-])"
        if re.search(pat, text_lower): found.add(canonical)
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

_BULLET_RE = re.compile(r"^\s*[•\-\*▸→‣●○–—]\s*")
# A self-contained "Title: description" or "Title | description" bullet, where one
# whole bullet line IS one project (common in dense one-bullet-per-project resumes).
_TITLE_HEAD_RE = re.compile(r"^([A-Z][^:|–—\n]{1,60}?)[:|–—]\s+(.+)$")
_TITLE_HEAD_BLACKLIST = {
    "tech","technologies","tools","stack","tech stack","technology",
    "technology used","skills","impact","note","result","results","outcome",
}
# A short "Project Title | Tech, Stack" style line (used as a fallback signal elsewhere).
_PROJECT_TITLE_RE = re.compile(r"^[A-Z][\w \-/&\.]{1,60}\s*[\|:–—-]\s*.{3,}")
# Inline heading anywhere in the raw resume, e.g. "Projects: Built an X that does Y"
_PROJECT_INLINE_RE = re.compile(
    r"(?im)^\s*(?:projects?|academic\s*projects?|personal\s*projects?)\s*[:\-]\s*(.+)$")

def _is_project_title_head(head):
    h = head.strip().lower()
    if h in _TITLE_HEAD_BLACKLIST:
        return False
    if _ACTION_RE.match(head.strip()):
        return False
    if _is_prose_line(head.strip()):
        return False
    return True

def _is_prose_line(line):
    """A line is 'prose' (i.e. a wrapped sentence fragment, not a project title)
    if it starts lowercase (real titles are always capitalized) or if a large
    fraction of its words are ordinary lowercase words."""
    if not line:
        return False
    if line[0].islower():
        return True
    words = re.findall(r"[A-Za-z][A-Za-z\-']*", line)
    if len(words) < 4:
        return False
    lowercase_words = [w for w in words if w.islower() and len(w) > 1]
    return (len(lowercase_words) / len(words)) > 0.35

def _split_project_blocks(text):
    """Split a projects-section string into candidate project blocks.
    Tries blank-line paragraphs first; if the section is one dense wall of
    bullet points (no blank lines — very common), use bullet/title heuristics
    that distinguish: a new project title, a self-contained one-line bullet
    project, a description bullet belonging to the current project, and a
    wrapped continuation line of the previous bullet."""
    blocks = [b for b in re.split(r"\n{2,}", text) if b.strip()]
    if len(blocks) > 1:
        return blocks

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if not lines:
        return blocks

    n = len(lines)
    new_blocks, current = [], []
    for i, raw_line in enumerate(lines):
        has_bullet = bool(_BULLET_RE.match(raw_line))
        line = _BULLET_RE.sub("", raw_line).strip()
        next_has_bullet = (i + 1 < n) and bool(_BULLET_RE.match(lines[i + 1]))

        m = _TITLE_HEAD_RE.match(line)
        self_contained_title = bool(m) and _is_project_title_head(m.group(1))
        # A non-bulleted line immediately followed by a bullet is a heading —
        # unless it reads like a wrapped sentence (mostly lowercase words),
        # in which case it's a continuation of the previous bullet.
        heading_line = (not has_bullet) and next_has_bullet and not _is_prose_line(line.split(".")[0])

        starts_new = self_contained_title or heading_line or not current
        if starts_new:
            if current:
                new_blocks.append(" ".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        new_blocks.append(" ".join(current))
    return new_blocks if len(new_blocks) > 1 else blocks

def extract_projects(text, full_text=""):
    entries = []
    seen = set()

    def _add(block):
        block = block.strip().lstrip("•-*→▸●○ ")
        if len(block) < 25:
            return
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            return
        full = " ".join(lines)
        key = full[:60].lower()
        if key in seen:
            return
        # Reject if it's a comma/pipe-separated tech list (no sentence verbs)
        if _SKILLS_LIST_RE.match(full) and not _ACTION_RE.search(full):
            return
        # Short bullet-style entries are fine as long as they have an action verb
        # or look like a "Title | description" line; otherwise require more length.
        if len(full) < 40 and not (_ACTION_RE.search(full) or _PROJECT_TITLE_RE.match(full)):
            return
        seen.add(key)
        entries.append(block[:400])

    if text.strip():
        for block in _split_project_blocks(text):
            _add(block)

    # Fallback: section-header detection may have missed an inline "Projects:" line
    # (heading and content on the same line). Scan the full raw text for that pattern.
    if not entries and full_text.strip():
        for m in _PROJECT_INLINE_RE.finditer(full_text):
            _add(m.group(1))

    return entries[:12]

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
        "projects":       extract_projects(sections.get("projects","") or "", raw_text),
        "certifications": extract_certifications(sections.get("certifications","") or ""),
        "summary":        sections.get("summary",""),
        "organisations":  extract_orgs_spacy(raw_text),
    }
