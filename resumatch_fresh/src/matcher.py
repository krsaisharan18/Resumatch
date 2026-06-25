import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.resume_parser import extract_skills, SKILLS_DB

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
    pred_set = set(str(x).lower().strip() for x in predicted)
    gt_set   = set(str(x).lower().strip() for x in ground_truth)
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
    if score>=0.80: return "Excellent"
    elif score>=0.65: return "Strong"
    elif score>=0.50: return "Good"
    elif score>=0.35: return "Fair"
    return "Weak"

def candidate_score(resume_text, resume_skills, jd_text, weights=None):
    if weights is None: weights = {"cosine":0.55,"skill":0.45}
    cosine     = tfidf_cosine_score(resume_text, jd_text)
    skill_data = match_skills(resume_skills, jd_text)
    skill_r    = skill_data["skill_match_ratio"]
    composite  = weights["cosine"]*cosine + weights["skill"]*skill_r
    return {"cosine_similarity":round(cosine*100,2),
            "skill_match_pct":round(skill_r*100,2),
            "composite_score":round(composite*100,2),
            "match_grade":_grade(composite), **skill_data}

def rank_candidates(candidates, jd_text):
    ranked = []
    for c in candidates:
        s = candidate_score(c.get("resume_text",""), c.get("skills",[]), jd_text)
        ranked.append({**c, **s})
    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    for i,r in enumerate(ranked,1): r["rank"] = i
    return ranked
