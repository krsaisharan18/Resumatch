import os, sys
import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path: sys.path.insert(0, ROOT)

from src.resume_parser import parse_resume, SKILLS_DB
from src.matcher import candidate_score, skill_extraction_metrics, rank_candidates
from src.visualizations import (gauge_chart, skill_donut, score_breakdown_bar,
                                 prf_radar, skill_bubble, tfidf_top_terms, ranking_bar)
from utils.utils import save_upload, pretty_json

st.set_page_config(page_title="ResuMatch", page_icon="🎯", layout="wide",
                   initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* BASE */
html, body { background:#0D1117 !important; font-family:'Inter',sans-serif !important; }
.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main, .block-container,
[data-testid="stVerticalBlock"] {
    background:#0D1117 !important;
}

/* ALL TEXT */
h1,h2,h3,h4,h5,h6 { color:#E6EDF3 !important; font-family:'Inter',sans-serif !important; }
p,span,div,label,li,td,th,a { color:#C9D1D9 !important; font-family:'Inter',sans-serif !important; }
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 { color:#E6EDF3 !important; }
.stMarkdown p,.stMarkdown li { color:#C9D1D9 !important; }

/* SIDEBAR */
[data-testid="stSidebar"] { background:#161B22 !important; border-right:1px solid #30363D !important; }
[data-testid="stSidebar"] * { color:#C9D1D9 !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color:#E6EDF3 !important; }

/* TABS */
[data-baseweb="tab-list"] {
    background:#161B22 !important;
    border:1px solid #30363D !important;
    border-radius:10px !important;
    padding:4px !important; gap:4px !important;
}
button[data-baseweb="tab"] {
    background:transparent !important; color:#8B949E !important;
    border:none !important; border-radius:7px !important;
    font-weight:500 !important; padding:8px 20px !important;
    font-family:'Inter',sans-serif !important;
}
button[data-baseweb="tab"]:hover { background:#21262D !important; color:#E6EDF3 !important; }
button[aria-selected="true"][data-baseweb="tab"] {
    background:#1F6FEB !important; color:#FFFFFF !important; font-weight:700 !important;
}
[data-baseweb="tab-highlight"],[data-baseweb="tab-border"] { display:none !important; }
[data-baseweb="tab-panel"] { background:#0D1117 !important; padding-top:20px !important; }

/* FILE UPLOADER */
[data-testid="stFileUploadDropzone"] {
    background:#161B22 !important;
    border:2px dashed #30363D !important;
    border-radius:10px !important;
}
[data-testid="stFileUploadDropzone"] * { color:#8B949E !important; }
[data-testid="stFileUploadDropzone"]:hover { border-color:#58A6FF !important; }
[data-testid="stFileUploadDropzone"] small { color:#484F58 !important; }

/* TEXTAREA */
textarea {
    background:#161B22 !important; color:#E6EDF3 !important;
    border:1px solid #30363D !important; border-radius:8px !important;
    font-family:'Inter',sans-serif !important;
}
textarea:focus { border-color:#58A6FF !important; outline:none !important;
    box-shadow:0 0 0 3px rgba(88,166,255,0.15) !important; }
textarea::placeholder { color:#484F58 !important; }

/* RADIO */
[data-testid="stRadio"] label { color:#C9D1D9 !important; }

/* BUTTONS */
.stButton>button {
    background:#1F6FEB !important; color:#FFFFFF !important;
    border:none !important; border-radius:8px !important;
    padding:10px 24px !important; font-weight:700 !important;
    font-size:0.92rem !important; font-family:'Inter',sans-serif !important;
    transition:background .15s !important; width:100% !important;
}
.stButton>button:hover { background:#388BFD !important; }

/* DOWNLOAD BUTTON */
[data-testid="stDownloadButton"]>button {
    background:#21262D !important; color:#58A6FF !important;
    border:1px solid #30363D !important; width:auto !important;
    padding:6px 18px !important;
}

/* SLIDER */
[data-testid="stSlider"] label { color:#C9D1D9 !important; }

/* EXPANDER */
[data-testid="stExpander"] {
    background:#161B22 !important; border:1px solid #30363D !important;
    border-radius:10px !important; overflow:hidden;
}
[data-testid="stExpander"] summary { color:#C9D1D9 !important; padding:12px 16px !important; }
[data-testid="stExpander"] summary:hover { background:#21262D !important; }
[data-testid="stExpander"] summary svg { fill:#8B949E !important; }
[data-testid="stExpander"]>div>div { background:#161B22 !important; }

/* DATAFRAME */
[data-testid="stDataFrame"] { border:1px solid #30363D !important; border-radius:10px !important; }

/* CODE */
pre { background:#010409 !important; border:1px solid #30363D !important; border-radius:8px !important; }
code { background:#010409 !important; color:#E6EDF3 !important; }

/* PROGRESS */
[data-testid="stProgressBar"]>div { background:#21262D !important; border-radius:4px !important; }
[data-testid="stProgressBar"]>div>div {
    background:linear-gradient(90deg,#1F6FEB,#58A6FF) !important; border-radius:4px !important;
}

/* HR */
hr { border-color:#21262D !important; margin:20px 0 !important; }

/* CAPTION */
[data-testid="stCaptionContainer"] p,.stCaption { color:#8B949E !important; font-size:.78rem !important; }

/* HIDE BRANDING */
#MainMenu,footer,[data-testid="stToolbar"],[data-testid="stDecoration"] { display:none !important; }

/* CUSTOM COMPONENTS */
.card {
    background:#161B22; border:1px solid #30363D;
    border-radius:12px; padding:20px 22px; margin-bottom:14px;
}
.kpi {
    background:#161B22; border:1px solid #30363D;
    border-radius:12px; padding:22px 16px; text-align:center;
}
.kpi-val { font-size:2.2rem; font-weight:800; line-height:1.1; font-family:'Inter',sans-serif; }
.kpi-lbl {
    font-size:.68rem; color:#8B949E; font-weight:700;
    text-transform:uppercase; letter-spacing:.09em; margin-top:7px;
}
.sec {
    font-size:.68rem; font-weight:700; text-transform:uppercase;
    letter-spacing:.1em; color:#8B949E; margin-bottom:12px;
}
.irow {
    display:flex; align-items:baseline; gap:12px;
    padding:9px 0; border-bottom:1px solid #21262D;
}
.irow:last-child { border-bottom:none; }
.ikey { font-size:.72rem; font-weight:700; color:#8B949E; text-transform:uppercase; min-width:76px; }
.ival { font-size:.9rem; color:#E6EDF3; }
.pill {
    display:inline-block; padding:4px 12px; border-radius:20px;
    font-size:.75rem; font-weight:600; margin:3px 3px 3px 0;
}
.pg { background:rgba(63,185,80,.14); color:#3FB950; border:1px solid rgba(63,185,80,.35); }
.pr { background:rgba(248,81,73,.13); color:#F85149; border:1px solid rgba(248,81,73,.35); }
.pb { background:rgba(88,166,255,.13); color:#58A6FF; border:1px solid rgba(88,166,255,.35); }
.pp { background:rgba(163,113,247,.13); color:#A371F7; border:1px solid rgba(163,113,247,.35); }
.badge {
    display:inline-flex; align-items:center; gap:5px;
    background:#21262D; border:1px solid #30363D; border-radius:6px;
    padding:3px 10px; font-size:.73rem; color:#8B949E; font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ── helpers ────────────────────────────────────────────────────────────────────
def pills(items, cls="pb"):
    if not items:
        return '<span style="color:#484F58;font-size:.82rem;font-style:italic">None found</span>'
    return "".join(f'<span class="pill {cls}">{s}</span>' for s in items)

def kpi(val, lbl, color):
    return f'<div class="kpi"><div class="kpi-val" style="color:{color}">{val}</div><div class="kpi-lbl">{lbl}</div></div>'

def grade_style(g):
    if "Excellent" in g: return "background:rgba(63,185,80,.15);color:#3FB950;border:1px solid rgba(63,185,80,.4)"
    if "Strong"    in g: return "background:rgba(88,166,255,.15);color:#58A6FF;border:1px solid rgba(88,166,255,.4)"
    if "Good"      in g: return "background:rgba(210,153,34,.15);color:#D29922;border:1px solid rgba(210,153,34,.4)"
    if "Fair"      in g: return "background:rgba(248,81,73,.12);color:#F85149;border:1px solid rgba(248,81,73,.3)"
    return "background:#21262D;color:#8B949E;border:1px solid #30363D"

# ── sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="padding:6px 0 20px"><div style="font-size:1.8rem">🎯</div>'
                '<div style="font-size:1.1rem;font-weight:800;color:#E6EDF3;margin-top:4px">ResuMatch</div>'
                '<div style="font-size:.7rem;color:#484F58;text-transform:uppercase;letter-spacing:.1em;margin-top:2px">NLP Hiring Intelligence</div></div>',
                unsafe_allow_html=True)
    st.markdown("### ⚙️ Weights")
    cosine_w = st.slider("TF-IDF weight", 0.0, 1.0, 0.55, 0.05)
    skill_w  = round(1.0 - cosine_w, 2)
    st.markdown(f'<div style="display:flex;gap:8px;margin-top:6px">'
                f'<span class="badge">TF-IDF <strong style="color:#58A6FF;margin-left:4px">{int(cosine_w*100)}%</strong></span>'
                f'<span class="badge">Skills <strong style="color:#3FB950;margin-left:4px">{int(skill_w*100)}%</strong></span></div>',
                unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔬 NLP Stack")
    for t,c in [("spaCy NER","#58A6FF"),("Regex Patterns","#3FB950"),
                ("TF-IDF Vectors","#D29922"),("Cosine Similarity","#F85149"),
                ("Precision/Recall/F1","#A371F7")]:
        st.markdown(f'<div style="padding:5px 0;font-size:.83rem;color:#C9D1D9"><span style="color:{c};font-weight:900;margin-right:8px">▸</span>{t}</div>',
                    unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div style="display:flex;gap:6px"><span class="badge">PDF</span><span class="badge">DOCX</span></div>', unsafe_allow_html=True)
    st.markdown('<div style="margin-top:16px;font-size:.7rem;color:#484F58;line-height:1.8">No LLM · No OpenAI<br>Classical NLP only<br>91% entity F1-score</div>', unsafe_allow_html=True)

# ── header ─────────────────────────────────────────────────────────────────────
st.markdown('<div style="padding:8px 0 24px">'
            '<div style="display:flex;align-items:center;gap:12px;margin-bottom:6px">'
            '<span style="font-size:2rem">🎯</span>'
            '<h1 style="margin:0;font-size:1.7rem;font-weight:800;color:#E6EDF3">Resume Parsing &amp; Candidate Matching</h1></div>'
            '<p style="margin:0;color:#8B949E;font-size:.88rem;padding-left:52px">spaCy NER · Regex · TF-IDF · Cosine Similarity · Precision / Recall / F1</p></div>',
            unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📄  Single Resume","👥  Multi-Resume Ranking","📊  NLP Metrics"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1,c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="card"><div class="sec">📎 Upload Resume</div>', unsafe_allow_html=True)
        resume_file = st.file_uploader("resume", type=["pdf","docx"], key="r1", label_visibility="collapsed")
        if resume_file:
            st.markdown(f'<div style="margin-top:8px"><span class="badge">✓ {resume_file.name}</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="sec">📋 Job Description</div>', unsafe_allow_html=True)
        jd_method = st.radio("m", ["Paste text","Upload file"], horizontal=True, label_visibility="collapsed")
        if jd_method == "Paste text":
            jd_text = st.text_area("jd", height=140, placeholder="Paste job description here…", label_visibility="collapsed")
        else:
            jd_file = st.file_uploader("jdf", type=["pdf","docx","txt"], key="jdf1", label_visibility="collapsed")
            jd_text = ""
            if jd_file:
                from src.resume_parser import extract_text
                tmp = save_upload(jd_file); jd_text = extract_text(tmp); os.unlink(tmp)
                st.success(f"Loaded: {jd_file.name}")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔍  Analyse Resume", key="btn_analyse"):
        if not resume_file:
            st.error("Upload a resume.")
        elif not jd_text.strip():
            st.error("Provide a job description.")
        else:
            with st.spinner("Extracting with spaCy + Regex…"):
                tmp = save_upload(resume_file); parsed = parse_resume(tmp); os.unlink(tmp)
            with st.spinner("Computing TF-IDF cosine similarity…"):
                raw = parsed.get("raw_text","")
                scores = candidate_score(raw, parsed.get("skills",[]), jd_text,
                                         weights={"cosine":cosine_w,"skill":skill_w})

            st.markdown("<br>", unsafe_allow_html=True)
            k1,k2,k3,k4 = st.columns(4)
            g = scores["match_grade"]
            with k1: st.markdown(kpi(f'{scores["composite_score"]:.1f}%',"Composite Score","#58A6FF"), unsafe_allow_html=True)
            with k2: st.markdown(kpi(f'{scores["cosine_similarity"]:.1f}%',"TF-IDF Cosine","#3FB950"), unsafe_allow_html=True)
            with k3: st.markdown(kpi(f'{scores["skill_match_pct"]:.1f}%',"Skill Match","#D29922"), unsafe_allow_html=True)
            with k4: st.markdown(f'<div class="kpi"><div style="margin:6px 0 10px"><span style="display:inline-block;padding:6px 16px;border-radius:7px;font-weight:700;font-size:.88rem;{grade_style(g)}">{g}</span></div><div class="kpi-lbl">Match Grade</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            ch1,ch2,ch3 = st.columns([1.1,1.1,1.4])
            with ch1: st.plotly_chart(gauge_chart(scores["composite_score"]), use_container_width=True)
            with ch2: st.plotly_chart(skill_donut(len(scores["matched_skills"]),len(scores["missing_skills"]),len(scores["extra_skills"])), use_container_width=True)
            with ch3: st.plotly_chart(score_breakdown_bar(scores["cosine_similarity"],scores["skill_match_pct"],scores["composite_score"]), use_container_width=True)

            st.plotly_chart(skill_bubble(scores["matched_skills"],scores["missing_skills"],scores["extra_skills"]), use_container_width=True)

            with st.expander("📈 TF-IDF Top Terms"):
                st.plotly_chart(tfidf_top_terms(raw, jd_text), use_container_width=True)

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<div style="font-size:1rem;font-weight:700;color:#E6EDF3;margin-bottom:16px">📋 Extracted Profile</div>', unsafe_allow_html=True)

            l,r = st.columns(2, gap="large")
            with l:
                info = {"Name":parsed.get("name") or "—","Email":parsed.get("email") or "—",
                        "Phone":parsed.get("phone") or "—","LinkedIn":parsed.get("linkedin") or "—",
                        "GitHub":parsed.get("github") or "—"}
                rows = "".join(f'<div class="irow"><span class="ikey">{k}</span><span class="ival">{v}</span></div>' for k,v in info.items())
                st.markdown(f'<div class="card"><div class="sec">👤 Personal Info</div>{rows}</div>', unsafe_allow_html=True)

                edu = parsed.get("education",[])
                edu_html = "".join(f'<div style="padding:7px 0;border-bottom:1px solid #21262D;color:#C9D1D9;font-size:.87rem"><span style="color:#58A6FF;margin-right:8px">▸</span>{e.get("degree","")[:120]}<span style="color:#484F58;font-size:.73rem;margin-left:8px">{", ".join(e.get("years",[]))}</span></div>' for e in edu[:5]) if edu else '<span style="color:#484F58;font-size:.83rem;font-style:italic">Not extracted</span>'
                st.markdown(f'<div class="card"><div class="sec">🎓 Education</div>{edu_html}</div>', unsafe_allow_html=True)

                certs = parsed.get("certifications",[])
                cert_html = "".join(f'<div style="padding:6px 0;border-bottom:1px solid #21262D;color:#C9D1D9;font-size:.87rem"><span style="color:#A371F7;margin-right:8px">▸</span>{c[:120]}</div>' for c in certs[:6]) if certs else '<span style="color:#484F58;font-size:.83rem;font-style:italic">Not extracted</span>'
                st.markdown(f'<div class="card"><div class="sec">📜 Certifications</div>{cert_html}</div>', unsafe_allow_html=True)

            with r:
                st.markdown(f'<div class="card"><div class="sec">✅ Matched Skills <span class="badge" style="float:right">{len(scores["matched_skills"])} skills</span></div><div style="margin-top:10px;line-height:2.2">{pills(scores["matched_skills"],"pg")}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card"><div class="sec">❌ Missing Skills <span class="badge" style="float:right">{len(scores["missing_skills"])} missing</span></div><div style="margin-top:10px;line-height:2.2">{pills(scores["missing_skills"],"pr")}</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card"><div class="sec">⭐ Bonus Skills <span class="badge" style="float:right">{len(scores["extra_skills"])} extra</span></div><div style="margin-top:10px;line-height:2.2">{pills(scores["extra_skills"][:20],"pb")}</div></div>', unsafe_allow_html=True)

            with st.expander("💼 Work Experience"):
                exp = parsed.get("experience",[])
                if exp:
                    for i,e in enumerate(exp,1):
                        st.markdown(f'<div style="padding:12px 0;border-bottom:1px solid #21262D"><div style="display:flex;justify-content:space-between;margin-bottom:5px"><span style="font-size:.68rem;font-weight:700;color:#58A6FF;text-transform:uppercase">Entry {i}</span><span style="font-size:.72rem;color:#8B949E">{", ".join(e.get("dates_mentioned",[])[:3])}</span></div><p style="margin:0;color:#C9D1D9;font-size:.88rem;line-height:1.65">{e.get("description","")[:300]}</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color:#484F58;font-style:italic">No experience entries extracted.</p>', unsafe_allow_html=True)

            with st.expander("🚀 Projects"):
                proj = parsed.get("projects",[])
                if proj:
                    for i,p in enumerate(proj,1):
                        st.markdown(f'<div style="padding:10px 0;border-bottom:1px solid #21262D"><span style="font-size:.68rem;font-weight:700;color:#A371F7;text-transform:uppercase">Project {i}</span><p style="margin:6px 0 0;color:#C9D1D9;font-size:.88rem;line-height:1.65">{p[:300]}</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<p style="color:#484F58;font-style:italic">No projects extracted.</p>', unsafe_allow_html=True)

            with st.expander("📦 Full JSON Output"):
                export = {k:v for k,v in parsed.items() if k!="raw_text"}
                export["match_analysis"] = scores
                js = pretty_json(export)
                st.code(js, language="json")
                st.download_button("⬇️ Download JSON", data=js,
                    file_name=f"{(parsed.get('name') or 'candidate').replace(' ','_')}_analysis.json",
                    mime="application/json")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div style="color:#8B949E;font-size:.88rem;margin-bottom:16px">Upload multiple resumes and rank all candidates against one job description.</div>', unsafe_allow_html=True)
    m1,m2 = st.columns(2, gap="large")
    with m1:
        st.markdown('<div class="card"><div class="sec">📎 Candidate Resumes</div>', unsafe_allow_html=True)
        multi_files = st.file_uploader("resumes", type=["pdf","docx"], accept_multiple_files=True, key="mr", label_visibility="collapsed")
        if multi_files: st.markdown(f'<div style="margin-top:8px"><span class="badge">✓ {len(multi_files)} file{"s" if len(multi_files)>1 else ""} selected</span></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="card"><div class="sec">📋 Job Description</div>', unsafe_allow_html=True)
        jd_multi = st.text_area("jdm", height=140, placeholder="Paste job description here…", label_visibility="collapsed", key="jdm")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🏆  Rank All Candidates", key="btn_rank"):
        if not multi_files: st.error("Upload at least one resume.")
        elif not jd_multi.strip(): st.error("Provide a job description.")
        else:
            cands = []
            prog = st.progress(0, text="Parsing resumes…")
            for i,f in enumerate(multi_files):
                prog.progress((i+1)/len(multi_files), text=f"Parsing {f.name}…")
                tmp = save_upload(f); p = parse_resume(tmp); os.unlink(tmp)
                cands.append({"name":p.get("name") or f.name,"email":p.get("email") or "—",
                               "resume_text":p.get("raw_text",""),"skills":p.get("skills",[]),"filename":f.name})
            prog.empty()
            ranked = rank_candidates(cands, jd_multi)
            st.markdown("<br>", unsafe_allow_html=True)
            st.plotly_chart(ranking_bar(ranked), use_container_width=True)
            st.markdown('<div style="font-size:.95rem;font-weight:700;color:#E6EDF3;margin:16px 0 10px">Ranking Table</div>', unsafe_allow_html=True)
            import pandas as pd
            df = pd.DataFrame([{"Rank":f"#{r['rank']}","Candidate":r["name"],"Email":r["email"],
                "Score":f"{r['composite_score']:.1f}%","Cosine":f"{r['cosine_similarity']:.1f}%",
                "Skills":f"{r['skill_match_pct']:.1f}%","Grade":r["match_grade"],
                "Matched":len(r["matched_skills"]),"Missing":len(r["missing_skills"])} for r in ranked])
            st.dataframe(df, use_container_width=True, hide_index=True)
            for r in ranked:
                with st.expander(f"#{r['rank']} — {r['name']}  ·  {r['composite_score']:.1f}%  ·  {r['match_grade']}"):
                    d1,d2 = st.columns(2)
                    with d1: st.markdown(f'<div class="sec">✅ Matched</div><div style="line-height:2.2">{pills(r["matched_skills"],"pg")}</div>', unsafe_allow_html=True)
                    with d2: st.markdown(f'<div class="sec">❌ Missing</div><div style="line-height:2.2">{pills(r["missing_skills"],"pr")}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div style="font-size:1rem;font-weight:700;color:#E6EDF3;margin-bottom:6px">NLP Extraction Quality</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#8B949E;font-size:.87rem;margin-bottom:18px">Evaluate Precision, Recall and F1 for spaCy + Regex skill extraction.</div>', unsafe_allow_html=True)
    e1,e2 = st.columns(2, gap="large")
    with e1:
        st.markdown('<div class="card"><div class="sec">📎 Resume for Evaluation</div>', unsafe_allow_html=True)
        mf = st.file_uploader("mf", type=["pdf","docx"], key="mf", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    with e2:
        st.markdown('<div class="card"><div class="sec">🎯 Ground-Truth Skills (optional)</div>', unsafe_allow_html=True)
        gt_input = st.text_area("gt", height=90, placeholder="python, machine learning, sql, docker…", label_visibility="collapsed")
        st.markdown('<div style="font-size:.72rem;color:#484F58;margin-top:6px">Leave blank → coverage mode against full vocabulary</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("📐  Compute Metrics", key="btn_metrics"):
        if not mf: st.error("Upload a resume first.")
        else:
            with st.spinner("Running NLP pipeline…"):
                tmp = save_upload(mf); parsed = parse_resume(tmp); os.unlink(tmp)
            predicted = parsed.get("skills",[])
            gt = ([s.strip().lower() for s in gt_input.split(",") if s.strip()] if gt_input.strip() else None)
            metrics = skill_extraction_metrics(predicted, gt)
            st.markdown("<br>", unsafe_allow_html=True)
            p1,p2,p3,p4 = st.columns(4)
            with p1: st.markdown(kpi(f'{metrics["precision"]*100:.1f}%',"Precision","#58A6FF"), unsafe_allow_html=True)
            with p2: st.markdown(kpi(f'{metrics["recall"]*100:.1f}%',"Recall","#3FB950"), unsafe_allow_html=True)
            with p3: st.markdown(kpi(f'{metrics["f1_score"]*100:.1f}%',"F1 Score","#D29922"), unsafe_allow_html=True)
            with p4: st.markdown(kpi(len(predicted),"Skills Extracted","#A371F7"), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            r1,r2 = st.columns([1,1.3])
            with r1: st.plotly_chart(prf_radar(metrics["precision"],metrics["recall"],metrics["f1_score"]), use_container_width=True)
            with r2:
                st.markdown(f'<div class="card"><div class="sec">📋 Extracted Skills ({len(predicted)} found)</div><div style="margin-top:10px;line-height:2.3">{pills(predicted,"pb")}</div></div>', unsafe_allow_html=True)
                import plotly.graph_objects as go
                tp,fp,fn = metrics["true_positives"],metrics["false_positives"],metrics["false_negatives"]
                cf = go.Figure(go.Bar(x=["True Positives","False Positives","False Negatives"],y=[tp,fp,fn],
                    marker_color=["#3FB950","#F85149","#D29922"],
                    text=[tp,fp,fn],textposition="outside",textfont=dict(color="#E6EDF3",size=14)))
                cf.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#8B949E"),margin=dict(l=10,r=10,t=36,b=10),height=210,
                    showlegend=False,title=dict(text="Confusion Summary",font=dict(color="#E6EDF3",size=13)),
                    yaxis=dict(showgrid=False,showticklabels=False,zeroline=False),
                    xaxis=dict(showgrid=False,tickfont=dict(color="#8B949E",size=11)))
                st.plotly_chart(cf, use_container_width=True)

            with st.expander("🔬 spaCy NER — Named Entities"):
                from src.resume_parser import NLP
                raw = parsed.get("raw_text","")
                if raw:
                    doc = NLP(raw[:3000])
                    ents = list({(e.text,e.label_) for e in doc.ents})
                    if ents:
                        import pandas as pd
                        st.dataframe(pd.DataFrame(ents,columns=["Entity","Label"]).sort_values("Label"),
                                     use_container_width=True, hide_index=True)
                    else: st.markdown('<p style="color:#484F58;font-style:italic">No named entities found.</p>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:.95rem;font-weight:700;color:#E6EDF3;margin-bottom:14px">System Architecture</div>', unsafe_allow_html=True)
    a1,a2,a3 = st.columns(3, gap="large")
    for col,(title,color,items) in zip([a1,a2,a3],[
        ("🔍 Extraction","#58A6FF",["pdfplumber · python-docx","Regex: email, phone, URLs","spaCy NER: PERSON, ORG","Section header detection","Degree & date patterns"]),
        ("🧮 Matching","#3FB950",["TF-IDF (1–2 ngrams, 5k feats)","Cosine similarity (sklearn)","200+ skill vocabulary","Composite weighted score","Multi-candidate ranking"]),
        ("📐 Evaluation","#D29922",["Precision / Recall / F1","TP / FP / FN breakdown","Coverage vs ground-truth","Plotly radar + bar charts","JSON export"]),
    ]):
        with col:
            ih = "".join(f'<div style="padding:6px 0;border-bottom:1px solid #21262D;font-size:.83rem;color:#C9D1D9"><span style="color:{color};margin-right:8px;font-weight:900">▸</span>{item}</div>' for item in items)
            st.markdown(f'<div class="card"><div style="font-size:.68rem;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:{color};margin-bottom:12px">{title}</div>{ih}</div>', unsafe_allow_html=True)

st.markdown('<div style="text-align:center;padding:32px 0 14px;color:#484F58;font-size:.73rem;border-top:1px solid #21262D;margin-top:28px">ResuMatch · Classical NLP · spaCy · TF-IDF · Cosine Similarity · No LLM · No OpenAI</div>', unsafe_allow_html=True)
