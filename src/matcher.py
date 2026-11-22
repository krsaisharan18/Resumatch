import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.resume_parser import extract_skills, SKILLS_DB, canonicalize_skill

def clean_text(text):
    text = re.sub(r"[^\w\s]"," ",text.lower())
    return re.sub(r"\s+"," ",text).strip()

def tfidf_cosine_score(resume_text, jd_text):
    vectorizer = TfidfVectorizer(ngram_range=(1,2), stop_words="english",
                                  max_features=5000, sublinear_tf=True)
    try:
        matrix = vectorizer.fit_transform([clean_text(resume_text), clean_text(jd_text)])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except: return 0.0

def match_skills(resume_skills, jd_text):
    jd_skills   = extract_skills(jd_text)
    resume_set  = set(s.lower() for s in resume_skills)
    jd_set      = set(s.lower() for s in jd_skills)
    matched     = sorted(resume_set & jd_set)
    missing     = sorted(jd_set - resume_set)
    extra       = sorted(resume_set - jd_set)
    return {"jd_skills": sorted(jd_set), "resume_skills": sorted(resume_set),
            "matched_skills": matched, "missing_skills": missing,
            "extra_skills": extra, "skill_match_ratio": len(matched)/max(len(jd_set),1)}

def compute_prf(predicted, ground_truth):
    # Canonicalize both sides through SKILL_ALIASES so e.g. a ground-truth "cpp"
    # matches a predicted "c++", and "ReactJS" matches "react", instead of being
    # scored as a false negative purely because of wording.
    pred_set = set(canonicalize_skill(x) for x in predicted)
    gt_set   = set(canonicalize_skill(x) for x in ground_truth)
    tp = len(pred_set & gt_set)
    fp = len(pred_set - gt_set)
    fn = len(gt_set - pred_set)
    p  = tp/(tp+fp) if (tp+fp)>0 else 0.0
    r  = tp/(tp+fn) if (tp+fn)>0 else 0.0
    f1 = 2*p*r/(p+r) if (p+r)>0 else 0.0
    return {"precision":round(p,4),"recall":round(r,4),"f1_score":round(f1,4),
            "true_positives":tp,"false_positives":fp,"false_negatives":fn}

def skill_extraction_metrics(predicted_skills, ground_truth_skills=None):
    if ground_truth_skills is None: ground_truth_skills = SKILLS_DB
    return compute_prf(predicted_skills, ground_truth_skills)

def _grade(score):
    # 75% is the target Jobscan recommends for a match rate, so that is where "Excellent" starts
    if score>=0.75: return "Excellent"
    elif score>=0.60: return "Strong"
    elif score>=0.45: return "Good"
    elif score>=0.30: return "Fair"
    return "Weak"

# ── ATS-style match rate ─────────────────────────────────────────────────────
# There is no single "real" ATS score: Workday, Greenhouse, Lever, Taleo and iCIMS do not publish one,
# and each ranks candidates its own way (parse the resume, match keywords against the job, rank).
# The closest public standard is the "match rate" used by resume scanners such as Jobscan. It is
# built from these categories, in this order of importance (Jobscan publishes the order, not the numbers):
#   hard skills  >  job title  >  soft skills  >  other keywords,  plus education only when the job asks for an advanced degree.
# The weights below are our own choice that follows that order. Formatting is checked separately
# (ATS readability) and is NOT part of the match rate, same as in those tools. Recommended target: 75%.
# Weights follow the project spec: quantitative (experience, skill coverage, certifications) = 40, qualitative (skill relevance, domain, job alignment) = 60
MATCH_WEIGHTS = {"experience": 15, "coverage": 20, "certs": 5, "relevance": 25, "domain": 15, "job": 20}
TARGET = 75
# Soft skills are people skills that every resume claims, so they get a small weight.
# Project / product / program / stakeholder / risk management are NOT in this set: for a manager role they are
# the core of the job, so they are scored as hard skills like Python or SQL.
SOFT_SKILLS = {"communication", "leadership", "teamwork", "collaboration", "problem solving", "critical thinking",
               "time management", "adaptability", "creativity", "customer service", "negotiation", "presentation",
               "decision making", "mentoring", "interpersonal", "organization", "organisation", "multitasking",
               "attention to detail", "strategic thinking", "initiative", "work ethic", "flexibility", "conflict resolution"}

# Skills that are not the same word but tell an ATS (and a recruiter) the candidate can do the job.
# If the job asks for X and the resume has a related skill from the same group, X gets partial credit.
RELATED_GROUPS = [
    ({"machine learning", "deep learning", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn", "xgboost", "ai", "data science"}, 0.6),
    ({"natural language processing", "nlp", "spacy", "nltk", "transformers", "bert", "hugging face", "gpt", "llm", "openai"}, 0.7),
    ({"sql", "mysql", "postgresql", "postgres", "sqlite", "oracle", "sql server", "mariadb", "database"}, 0.7),
    ({"aws", "azure", "gcp", "google cloud", "cloud", "ec2", "s3", "lambda", "sagemaker"}, 0.6),
    ({"docker", "kubernetes", "containers", "helm"}, 0.6),
    ({"javascript", "typescript", "react", "angular", "vue", "node.js", "nodejs", "html", "css"}, 0.5),
    ({"python", "pandas", "numpy", "scipy", "flask", "django", "fastapi"}, 0.5),
    ({"java", "spring", "spring boot", "kotlin", "scala"}, 0.5),
    ({"agile", "scrum", "kanban", "jira", "sprint planning"}, 0.7),
    ({"project management", "program management", "product management", "stakeholder management", "roadmap", "jira", "confluence"}, 0.6),
    ({"data analysis", "data analytics", "excel", "tableau", "power bi", "looker", "statistics", "data visualization"}, 0.6),
    ({"git", "github", "gitlab", "version control", "bitbucket"}, 0.8),
    ({"ci/cd", "jenkins", "github actions", "gitlab ci", "devops"}, 0.7),
]
_ROLE_SYN = {"developer": "engineer", "programmer": "engineer", "swe": "engineer", "sde": "engineer", "trainee": "intern",
             "analytics": "analyst", "management": "manager", "scientist": "scientist"}

_GENERIC = set("""experience work team ability strong skills skill responsibilities requirements requirement years year
looking role job candidate candidates join company position preferred required including include etc must will can
good great excellent knowledge understanding working use using used help support within across new well also plus
opportunity opportunities apply please resume detail benefits equal employer description qualifications qualification
about this that with from your you our their they have has are for and the who what when where while able need needs
based related similar least minimum bachelor master degree intern internship full time part remote location salary""".split())

def _stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w

def _words(text):
    return [w for w in re.findall(r"[a-z][a-z+#.]{2,}", text.lower())]

def _jd_keywords(jd_text, limit=25):
    counts = {}
    for w in _words(jd_text):
        w = w.strip(".")
        if len(w) < 3 or w in _GENERIC:
            continue
        st = _stem(w)
        counts[st] = counts.get(st, 0) + 1
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    items = [(k, v) for k, v in counts.items() if k not in ENGLISH_STOP_WORDS]
    items.sort(key=lambda kv: (-kv[1], kv[0]))
    return items[:limit]

def _keyword_score(resume_text, jd_text):
    kws = _jd_keywords(jd_text)
    if len(kws) < 4:
        return None, ""
    have = {_stem(w.strip(".")) for w in _words(resume_text)}
    tot = sum(v for _, v in kws)
    hit = sum(v for k, v in kws if k in have)
    n_hit = sum(1 for k, _ in kws if k in have)
    return hit / tot, f"{n_hit} of {len(kws)} key terms from the job description"

def _role_score(resume_text, jd_text):
    try:
        from src.resume_parser import extract_job_role
        role = extract_job_role(jd_text)
    except Exception:
        role = None
    if not role:
        return None, ""
    toks = [_ROLE_SYN.get(_stem(w), _stem(w)) for w in _words(role) if w not in {"intern", "internship", "trainee", "senior", "junior", "lead",
                                                          "associate", "and", "the", "for", "ii", "iii"}]
    if not toks:
        return None, ""
    low = [_ROLE_SYN.get(_stem(w), _stem(w)) for w in _words(resume_text)]
    head = set(low[:60])
    body = set(low)
    present = sum(t in body for t in toks) / len(toks)
    top = sum(t in head for t in toks) / len(toks)
    return min(1.0, 0.6 * present + 0.4 * max(top, present * 0.5)), f"Role: {role}"

_YEARS_RE = re.compile(r"(\d{1,2})\s*\+?\s*(?:-|to)?\s*(?:\d{1,2})?\s*\+?\s*years?", re.I)

def _resume_years(text):
    import datetime
    now = datetime.date.today().year
    spans = []
    for m in re.finditer(r"((?:19|20)\d{2})\s*(?:-|–|to)\s*((?:19|20)\d{2}|present|current|now|pursuing)", text, re.I):
        a = int(m.group(1)); e = m.group(2).lower()
        b = now if not e[0].isdigit() else int(e)
        if 0 <= b - a <= 15:
            spans.append((a, b))
    if not spans:
        return 0.0
    spans.sort()
    total, cur_a, cur_b = 0, spans[0][0], spans[0][1]
    for a, b in spans[1:]:
        if a <= cur_b:
            cur_b = max(cur_b, b)
        else:
            total += cur_b - cur_a; cur_a, cur_b = a, b
    return total + cur_b - cur_a

def _fit_score(resume_text, jd_text):
    parts, notes = [], []
    entry = re.search(r"(?i)\b(intern|internship|fresher|entry[- ]level|trainee|graduate|new grad)", jd_text)
    ym = _YEARS_RE.findall(jd_text)
    need = min((int(x[0]) for x in ym if 0 < int(x[0]) <= 15), default=0) if ym else 0
    if need and not entry:
        have = _resume_years(resume_text)
        parts.append(min(1.0, have / need)); notes.append(f"{have:.0f} of {need}+ years")
    degree_req = re.search(r"(?i)\b(bachelor|master|b\.?\s?tech|m\.?\s?tech|b\.?\s?e\b|b\.?\s?sc|m\.?\s?sc|mba|degree|phd)", jd_text)
    if degree_req:
        has = re.search(r"(?i)\b(bachelor|master|b\.?\s?tech|m\.?\s?tech|b\.?\s?e\b|b\.?\s?sc|m\.?\s?sc|b\.?\s?s\b|m\.?\s?s\b|mba|phd|diploma|degree|university|college|engineering)", resume_text)
        parts.append(1.0 if has else 0.0); notes.append("education listed" if has else "no degree found")
    if not parts:
        return None, ""
    return sum(parts) / len(parts), ", ".join(notes)

def _quality_score(resume_text):
    t = resume_text
    checks = {
        "email": bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", t)),
        "phone": bool(re.search(r"\+?\d[\d\s().-]{8,}\d", t)),
        "education section": bool(re.search(r"(?im)^\s*(education|academic)", t)),
        "experience or projects": bool(re.search(r"(?im)^\s*(work experience|experience|employment|projects?|internships?)", t)),
        "skills section": bool(re.search(r"(?im)^\s*(technical\s+)?skills", t)),
        "measurable results": len(re.findall(r"\d+\s*%|\$\s?\d|\b\d{2,}\+?\s+(?:users|customers|students|projects|members|records)", t)) >= 1,
        "sensible length": 150 <= len(t.split()) <= 1600,
    }
    ok = sum(checks.values())
    missing = [k for k, v in checks.items() if not v]
    return ok / len(checks), ("Missing: " + ", ".join(missing)) if missing else "All standard parts present"

def _education_score(resume_text, jd_text):
    """Counted only when the job asks for an advanced degree (master's / PhD), like Jobscan."""
    if not re.search(r"(?i)\b(master'?s?|m\.?\s?tech|m\.?\s?sc|m\.?\s?s\b|mba|ph\.?d|doctorate|postgraduate)\b", jd_text):
        return None, ""
    need_phd = re.search(r"(?i)ph\.?d|doctorate", jd_text)
    if need_phd:
        ok = re.search(r"(?i)ph\.?d|doctorate", resume_text)
        return (1.0 if ok else 0.0), "PhD found" if ok else "PhD asked for, not found"
    ok = re.search(r"(?i)\b(master'?s?|m\.?\s?tech|m\.?\s?sc|m\.?\s?s\b|mba|ph\.?d|doctorate|postgraduate)\b", resume_text)
    return (1.0 if ok else 0.0), "Master's or higher found" if ok else "Master's asked for, not found"


def ats_readability(resume_text, parsed=None):
    """Can an ATS read this resume? Checked separately; it is not part of the match rate."""
    t = resume_text
    parsed = parsed or {}
    checks = [
        ("Name found", bool(parsed.get("name")) if parsed else bool(t.strip())),
        ("Email found", bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", t))),
        ("Phone found", bool(re.search(r"\+?\d[\d\s().-]{8,}\d", t))),
        ("Education section", bool(re.search(r"(?im)^\s*(education|academic)", t))),
        ("Experience or projects section", bool(re.search(r"(?im)^\s*(work experience|experience|employment|projects?|internships?|professional)", t))),
        ("Skills section", bool(re.search(r"(?im)^\s*(technical\s+|key\s+|core\s+)?skills", t))),
        ("Text can be selected (not a scanned image)", not parsed.get("ocr", False)),
    ]
    ok = sum(1 for _, v in checks if v)
    return {"score": round(ok / len(checks) * 100), "checks": [{"label": l, "ok": bool(v)} for l, v in checks]}


_PREFERRED_RE = re.compile(r"(?i)\b(plus|preferred|nice to have|bonus|good to have|desirable|a plus|an advantage|familiarity|exposure|optionally?)\b")


def _skill_weights(jd_text, skills):
    """Required skills count 1.0, ones the job calls a 'plus / preferred' count 0.5,
    and a skill the job repeats is more important (up to 1.5)."""
    w = {}
    chunks = [c for c in re.split(r"(?<=[.!?])\s+|\n+", jd_text) if c.strip()]
    for k in skills:
        pat = r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])"
        hits = [c for c in chunks if re.search(pat, c.lower())]
        pref = bool(hits) and all(_PREFERRED_RE.search(c) for c in hits)
        base = 0.5 if pref else 1.0
        if len(hits) >= 2 and not pref:
            base = 1.5
        w[k] = base
    return w


def _credit(skill, have):
    """1.0 for the skill itself, partial credit for a related one, else 0. Returns (credit, via)."""
    if skill in have:
        return 1.0, None
    best, via = 0.0, None
    for group, c in RELATED_GROUPS:
        if skill in group:
            for other in group:
                if other != skill and other in have and c > best:
                    best, via = c, other
    return best, via


def _years_part(resume_text, jd_text):
    entry = re.search(r"(?i)\b(intern|internship|fresher|entry[- ]level|trainee|graduate|new grad)", jd_text)
    ym = _YEARS_RE.findall(jd_text)
    need = min((int(x[0]) for x in ym if 0 < int(x[0]) <= 15), default=0) if ym else 0
    if need and not entry:
        have = _resume_years(resume_text)
        return min(1.0, have / need), f"{have:.0f} of {need}+ years of experience"
    return None, ""


def _n_certs(parsed):
    parsed = parsed or {}
    if "n_certs" in parsed: return int(parsed["n_certs"])
    return len(parsed.get("certifications") or [])


def _band_word(x):
    return "High" if x >= 0.70 else ("Medium" if x >= 0.40 else "Low")


def candidate_score(resume_text, resume_skills, jd_text, weights=None, parsed=None):
    """Score built from the project spec: quantitative metrics (years of experience, skill coverage,
    certifications) plus qualitative metrics (skill relevance, domain alignment, job alignment).
    Every part is 0-100, the weights are in MATCH_WEIGHTS, and the final score is their weighted mean."""
    cosine     = tfidf_cosine_score(resume_text, jd_text)
    skill_data = match_skills(resume_skills, jd_text)
    jd_sk      = skill_data["jd_skills"]
    have       = set(skill_data["resume_skills"])
    wts        = _skill_weights(jd_text, jd_sk)

    # quantitative 1: experience (years found in dated roles vs the years the job asks for)
    years = _resume_years(resume_text)
    ym = _YEARS_RE.findall(jd_text)
    need = min((int(x[0]) for x in ym if 0 < int(x[0]) <= 15), default=0) if ym else 0
    entry = bool(re.search(r"(?i)\b(intern|internship|fresher|entry[- ]level|trainee|graduate|new grad)", jd_text))
    if not need:
        need = 1 if entry else 3
    exp_sc = min(1.0, years / need)
    exp_note = f"{years:.0f} year{'s' if years != 1 else ''} found, job needs about {need}"

    # quantitative 2: skill coverage (share of the job's technical skills the candidate has, related skills count partly)
    hard_names = [k for k in jd_sk if k not in SOFT_SKILLS] or list(jd_sk)
    tot = sum(wts[k] for k in hard_names)
    got, found, related, missing = 0.0, [], [], []
    for k in hard_names:
        c, via = _credit(k, have)
        got += wts[k] * c
        if c == 1.0: found.append(k)
        elif c > 0: related.append((k, via))
        else: missing.append(k)
    cov_sc = (got / tot) if tot else None
    cov_note = (f"{len(found)} of {len(hard_names)} required skills found"
                + (f", {len(related)} covered by a related skill" if related else "")) if hard_names else ""

    # quantitative 3: certifications (2 or more is full marks)
    nc = _n_certs(parsed)
    cert_sc = min(nc, 2) / 2
    cert_note = f"{nc} certification{'s' if nc != 1 else ''} found"

    # qualitative 1: skill relevance (TF-IDF cosine between the candidate's skills and the job description)
    skills_cos = tfidf_cosine_score(" ".join(resume_skills), jd_text) if resume_skills else 0.0
    rel_sc = min(1.0, max(skills_cos, cosine * 0.8) / 0.35)
    rel_note = f"TF-IDF similarity: skills {skills_cos*100:.0f}%, whole resume {cosine*100:.0f}%"

    # qualitative 2: domain alignment
    jd_dom, _ = detect_domain(list(jd_sk))
    c_dom, _ = detect_domain(list(have))
    if jd_dom is None or c_dom is None:
        dom_sc, dom_note = None, ""
    elif jd_dom == c_dom:
        dom_sc, dom_note = 1.0, f"Same domain: {jd_dom}"
    elif len(have & DOMAINS[jd_dom]) >= 2:
        dom_sc, dom_note = 0.5, f"Mostly {c_dom}, but covers part of {jd_dom}"
    else:
        dom_sc, dom_note = 0.0, f"{c_dom} candidate, job is {jd_dom}"

    # qualitative 3: job alignment (resume vs the job title in the description)
    job_sc, job_note = _role_score(resume_text, jd_text)
    if job_sc is None:
        job_sc, job_note = min(1.0, cosine / 0.30), "No job title found, using wording overlap"

    comps = {"experience": (exp_sc, exp_note), "coverage": (cov_sc, cov_note), "certs": (cert_sc, cert_note),
             "relevance": (rel_sc, rel_note), "domain": (dom_sc, dom_note), "job": (job_sc, job_note)}
    labels = {"experience": "Years of experience", "coverage": "Skill coverage", "certs": "Certifications",
              "relevance": "Skill relevance", "domain": "Domain alignment", "job": "Job alignment"}
    group = {"experience": "Quantitative", "coverage": "Quantitative", "certs": "Quantitative",
             "relevance": "Qualitative", "domain": "Qualitative", "job": "Qualitative"}
    active = {k: v for k, v in comps.items() if v[0] is not None}
    wsum = sum(MATCH_WEIGHTS[k] for k in active) or 1
    composite = sum(MATCH_WEIGHTS[k] * v[0] for k, v in active.items()) / wsum
    breakdown = [{"key": k, "label": labels[k], "group": group[k], "score": round(v[0] * 100, 1), "note": v[1],
                  "weight": round(MATCH_WEIGHTS[k] / wsum * 100), "band": _band_word(v[0])} for k, v in active.items()]

    reasons, improve = [], []
    if found: reasons.append("Has " + ", ".join(found[:6]) + (" and more" if len(found) > 6 else "") + " from the job description.")
    for k, via in related[:4]:
        reasons.append(f"Does not list {k}, but has {via}, which is closely related.")
    if missing:
        improve = [k for k in sorted(missing, key=lambda x: -wts[x])][:6]
        reasons.append("Missing: " + ", ".join(improve) + ".")
    if exp_sc >= 1: reasons.append(f"Meets the experience level ({years:.0f} years found).")
    elif years: reasons.append(f"Experience is below what the job asks for ({years:.0f} of about {need} years).")
    if dom_sc == 1.0: reasons.append(dom_note + ".")
    elif dom_sc == 0.0: reasons.append("Skills point to a different domain than the job.")

    strong = sum([cosine >= 0.22, (cov_sc or 0) >= 0.4, bool(related) and len(found) + len(related) >= max(1, len(hard_names)) * 0.6,
                  (job_sc or 0) >= 0.8])
    worth = bool(composite < TARGET / 100 and strong >= 2)

    return {"cosine_similarity": round(cosine*100, 2),
            "skill_match_pct": round(skill_data["skill_match_ratio"]*100, 2),
            "composite_score": round(composite*100, 2),
            "match_grade": _grade(composite), "breakdown": breakdown, "target": TARGET,
            "reasons": reasons, "improve": improve, "worth_a_look": worth,
            "related_skills": [{"skill": k, "via": v} for k, v in related],
            "readability": ats_readability(resume_text, parsed), **skill_data}

def rank_candidates(candidates, jd_text):
    ranked = []
    for c in candidates:
        s = candidate_score(c.get("resume_text",""), c.get("skills",[]), jd_text, parsed=c.get("parsed"))
        ranked.append({**c, **s})
    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    for i,r in enumerate(ranked,1): r["rank"] = i
    return ranked


# ── Candidate comparison: quantitative + qualitative metrics ─────────────────
# Quantitative = things you can count (years of experience, skills, certifications, projects, education level).
# Qualitative  = how well the candidate fits THIS job (skill relevance, domain alignment, job alignment), shown
#                as High / Medium / Low with the reason. Both feed the score (see MATCH_WEIGHTS); the recommendation
#                is the candidate with the highest score, ties broken by skill relevance, domain, then years.
DOMAINS = {
    "Data Science and ML": {"machine learning", "deep learning", "tensorflow", "pytorch", "keras", "scikit-learn", "nlp",
                            "natural language processing", "pandas", "numpy", "statistics", "data science", "computer vision", "xgboost"},
    "Data Engineering and Analytics": {"sql", "spark", "hadoop", "airflow", "etl", "kafka", "tableau", "power bi", "data warehouse",
                                       "snowflake", "bigquery", "data analysis", "excel", "data visualization", "dbt"},
    "Software Development": {"java", "python", "c++", "c#", "javascript", "typescript", "go", "rust", "spring", "django", "flask",
                             "node.js", "git", "rest api", "api", "microservices", "oop", "data structures", "algorithms"},
    "Web and Frontend": {"html", "css", "react", "angular", "vue", "next.js", "tailwind", "bootstrap", "frontend", "ui", "ux", "figma"},
    "Cloud and DevOps": {"aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform", "jenkins", "ci/cd", "linux", "devops", "ansible"},
    "Product and Project Management": {"project management", "product management", "program management", "agile", "scrum", "jira",
                                       "roadmap", "stakeholder management", "product strategy", "okr", "kanban", "confluence"},
    "Business and Marketing": {"seo", "marketing", "sales", "crm", "salesforce", "google analytics", "content", "branding", "social media"},
}
_EDU_LEVELS = [("PhD", 4, r"ph\.?d|doctorate"), ("Master's", 3, r"master|m\.?\s?tech|m\.?\s?sc|m\.?\s?s\b|mba|postgraduate"),
               ("Bachelor's", 2, r"bachelor|b\.?\s?tech|b\.?\s?e\b|b\.?\s?sc|b\.?\s?s\b|b\.?\s?a\b|b\.?\s?com|bca"),
               ("Diploma", 1, r"diploma|associate")]


def detect_domain(skills):
    """Domain a set of skills points to, and how strongly (share of the skills that belong to it)."""
    have = {k.lower() for k in skills}
    scores = {d: len(have & ks) for d, ks in DOMAINS.items()}
    best = max(scores, key=scores.get) if scores else None
    if not best or scores[best] == 0:
        return None, 0.0
    return best, scores[best] / max(1, sum(scores.values()))


def education_level(parsed):
    texts = " ".join((e.get("degree") or "") for e in (parsed.get("education") or []) if isinstance(e, dict)) if parsed else ""
    best = ("Not found", 0)
    for name, lvl, pat in _EDU_LEVELS:
        if re.search(r"(?i)\b(" + pat + r")\b", texts) and lvl > best[1]:
            best = (name, lvl)
    return best


def _band(x, hi, mid):
    return "High" if x >= hi else ("Medium" if x >= mid else "Low")


def candidate_profile(c, jd_text):
    """Metrics for one ranked candidate (c = a rank_candidates() row that also carries c['parsed'])."""
    parsed = c.get("parsed") or {}
    text = c.get("resume_text", "")
    years = _resume_years(text)
    edu_name, edu_lvl = education_level(parsed)
    comp = {b["key"]: b["score"] for b in c.get("breakdown", [])}
    jd_domain, _ = detect_domain(c.get("jd_skills", []))
    cand_domain, share = detect_domain(c.get("resume_skills", []))
    if jd_domain is None or cand_domain is None:
        dom_fit = "Not clear"
    elif jd_domain == cand_domain:
        dom_fit = "Same domain"
    else:
        # a candidate whose skills also cover the job's domain is "Partly aligned"
        ov = len({k.lower() for k in c.get("resume_skills", [])} & DOMAINS[jd_domain])
        dom_fit = "Partly aligned" if ov >= 2 else "Different domain"
    skill_rel = _band(comp.get("relevance", 0), 70, 40)
    title_fit = _band(comp.get("job", 0), 70, 40) if "job" in comp else "Not asked"
    return {
        "name": c.get("name"), "filename": c.get("filename"),
        "quant": {"Years of experience": round(years, 1), "Skills listed": len(c.get("resume_skills", [])),
                  "Required skills matched": len(c.get("matched_skills", [])),
                  "Certifications": int(parsed.get("n_certs", 0)), "Projects": int(parsed.get("n_projects", 0)),
                  "Education": edu_name, "_edu_lvl": edu_lvl},
        "qual": {"Skill relevance": skill_rel, "Domain alignment": dom_fit, "Job alignment": title_fit},
        "domain": cand_domain, "jd_domain": jd_domain, "score": c.get("composite_score", 0), "rank": c.get("rank"),
    }


def compare_candidates(ranked, jd_text, names=None):
    """Side-by-side comparison of 2-4 candidates plus a final recommendation with reasons."""
    pool = [r for r in ranked if (names is None or r["name"] in names)]
    profs = [candidate_profile(r, jd_text) for r in pool]
    if not profs:
        return {"profiles": [], "winners": {}, "recommendation": None}
    numeric = ["Years of experience", "Required skills matched", "Certifications", "Projects", "Skills listed"]
    winners = {}
    for k in numeric:
        top = max(p["quant"][k] for p in profs)
        winners[k] = [p["name"] for p in profs if p["quant"][k] == top and top > 0]
    top = max(p["quant"]["_edu_lvl"] for p in profs)
    winners["Education"] = [p["name"] for p in profs if p["quant"]["_edu_lvl"] == top and top > 0]
    order = {"High": 2, "Medium": 1, "Low": 0, "Same domain": 2, "Partly aligned": 1, "Different domain": 0, "Not clear": 1, "Not asked": 1}

    def key(p):
        return (p["score"], order[p["qual"]["Skill relevance"]], order[p["qual"]["Domain alignment"]], p["quant"]["Years of experience"])
    best = max(profs, key=key)
    others = [p for p in profs if p is not best]
    why = [f'Highest overall score for this job: {best["score"]:.1f}%.']
    if best["qual"]["Skill relevance"] == "High":
        why.append("Skill relevance is high: the skills and wording closely match the job description.")
    if best["qual"]["Domain alignment"] == "Same domain":
        why.append(f'Works in the same domain as the job ({best["jd_domain"]}).')
    if others:
        r = max(others, key=key)
        gap = best["score"] - r["score"]
        if gap < 5:
            why.append(f'Very close to {r["name"]} ({gap:.1f} points apart), so read both resumes before deciding.')
        extra = [k for k in ("Years of experience", "Certifications") if r["quant"][k] > best["quant"][k]]
        if extra:
            why.append(f'{r["name"]} has more: ' + ", ".join(e.lower() for e in extra) + ".")
    return {"profiles": profs, "winners": winners, "recommendation": {"name": best["name"], "score": best["score"], "why": why}}
