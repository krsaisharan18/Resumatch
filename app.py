import os, sys, re, hashlib
from html import escape as esc
import pandas as pd
import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path: sys.path.insert(0, ROOT)

from src.resume_parser import (parse_resume, SKILLS_DB, extract_job_role, extract_resume_entities,
                               extract_text, canonicalize_skill)
from src.matcher import candidate_score, skill_extraction_metrics, rank_candidates
from src import structure as _struct
from src.visualizations import set_theme as set_chart_theme
from src.visualizations import (skill_donut, prf_radar, skill_bubble, tfidf_top_terms,
                                ranking_bar, confusion_bar)
from utils.utils import save_upload, pretty_json

st.set_page_config(page_title="ResuMatch", page_icon="🎯", layout="wide",
                   initial_sidebar_state="collapsed")

# ═════════════════════════════════════════════════════════════════════════════
# Design system: warm paper, white surfaces, indigo accent, navy ink.
# Green and rose are reserved for "matched" and "missing"; nothing else uses them.
# ═════════════════════════════════════════════════════════════════════════════
LOGO = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
        "%3Crect width='32' height='32' rx='9' fill='%233B3FD8'/%3E"
        "%3Cpath d='M10 9.5h7.2l4.8 4.8V22a1.5 1.5 0 0 1-1.5 1.5h-10.5A1.5 1.5 0 0 1 8.5 22V11A1.5 1.5 0 0 1 10 9.5Z' "
        "fill='none' stroke='white' stroke-width='1.8' stroke-linejoin='round'/%3E"
        "%3Cpath d='m12.2 17.4 2.4 2.4 4.4-4.6' fill='none' stroke='white' stroke-width='1.9' "
        "stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Onest:wght@400..700&family=Schibsted+Grotesk:wght@500..800&display=swap');

:root{
  --paper:#F6F5F1; --card:#FFFFFF; --field:#FBFAF7;
  --ink:#141A3C; --ink-2:#4A5175; --ink-3:#636B8F;
  --line:#E6E3DA; --line-2:#EFEDE6;
  --accent:#3B3FD8; --accent-h:#2F33C2; --accent-soft:#ECEDFD; --accent-line:#C4C7F5;
  --ok:#137A4B; --ok-bg:#E3F5EC; --bad:#B3382A; --bad-bg:#FDECE9; --warn:#8F5206; --warn-bg:#FCF0D9;
  --surface:#FFFFFF; --chip:#F0EFEA; --track:#EEECE5; --code:#F3F1EA; --line-3:#D8D5CB; --dz:rgba(255,255,255,.55);
  --bar:rgba(255,255,255,.94); --ok-line:#CFEBDD; --ok-bg2:#F3FBF7; --btn:#3B3FD8; --btn-h:#2F33C2; --warn-line:#EBD9B4;
  --shadow-1:0 1px 2px rgba(20,26,60,.05);
  --shadow-2:0 1px 2px rgba(20,26,60,.04), 0 18px 36px -20px rgba(20,26,60,.22);
  --head:'Schibsted Grotesk','Onest','Segoe UI',system-ui,sans-serif;
  --body:'Onest','Segoe UI',system-ui,-apple-system,sans-serif;
}
html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"], [data-testid="stMain"]{
  background:var(--paper) !important; color:var(--ink); font-family:var(--body) !important; }
[data-testid="stApp"] p, [data-testid="stApp"] li, [data-testid="stApp"] label,
[data-testid="stApp"] textarea, [data-testid="stApp"] input { font-family:var(--body); }
[data-testid="stIconMaterial"], .material-symbols-rounded { font-family:'Material Symbols Rounded' !important; }
h1,h2,h3,h4 { font-family:var(--head) !important; color:var(--ink) !important; }

[data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="stExpandSidebarButton"], [data-testid="stToolbar"], [data-testid="stDecoration"],
#MainMenu, footer { display:none !important; }
[data-testid="stMainBlockContainer"] { max-width:none !important; padding:0 !important; }
[data-testid="stMarkdownContainer"] { margin-bottom:0 !important; }
[data-testid="stMarkdownContainer"] p { margin:0 0 .4rem; }
.ic { flex:none; }

button:focus-visible, textarea:focus-visible, input:focus-visible, [role="tab"]:focus-visible,
summary:focus-visible, [data-baseweb="select"]:focus-within { outline:2px solid var(--accent) !important; outline-offset:2px !important; }

/* ── top bar: brand, tabs, status ───────────────────────────────────── */
[role="tablist"]{
  position:sticky; top:0; z-index:100; display:flex !important; align-items:center; gap:2px; height:66px;
  padding:0 max(1.5rem, calc((100% - 1160px) / 2 + 1.5rem)) !important;
  background:var(--bar) !important; backdrop-filter:saturate(1.4) blur(12px);
  border-bottom:1px solid var(--line) !important; overflow-x:auto; scrollbar-width:none; }
[role="tablist"]::-webkit-scrollbar{ display:none; }
[role="tablist"]::before{
  content:"ResuMatch"; flex:none; display:flex; align-items:center; height:34px; padding-left:44px;
  margin-right:2.4rem; font:700 1.3rem/1 var(--head); letter-spacing:-.025em; color:var(--ink);
  background:url("__LOGO__") no-repeat left center / 34px 34px; }
[role="tablist"]::after{
  content:"Classical NLP · No LLM"; position:static !important; width:auto !important; height:auto !important; inset:auto !important; flex:none; margin-left:auto; margin-right:128px; white-space:nowrap;
  font:500 .86rem/1 var(--body); color:var(--ink-2); padding:8px 14px 8px 30px; border:1px solid var(--line);
  border-radius:99px; background:radial-gradient(circle at 15px 50%, #1F9D63 0 4px, transparent 5px) no-repeat, var(--surface); }
[data-testid="stTab"]{
  height:66px; padding:0 14px !important; border-radius:0 !important; background:transparent !important;
  color:var(--ink-2) !important; display:flex; align-items:center; gap:8px; flex:none;
  border-bottom:2px solid transparent; transition:color .15s, border-color .15s; }
[data-testid="stTab"] p{ font:560 .97rem/1 var(--body) !important; margin:0 !important; color:inherit !important; }
[data-testid="stTab"]:hover{ color:var(--ink) !important; }
[data-testid="stTab"][aria-selected="true"]{ color:var(--accent) !important; border-bottom-color:var(--accent); }
.react-aria-SelectionIndicator, [data-baseweb="tab-highlight"], [data-baseweb="tab-border"]{ display:none !important; }
[data-testid="stMainBlockContainer"], .block-container{ padding-top:0 !important; max-width:none !important; padding-left:0 !important; padding-right:0 !important; }

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"]{ gap:0 !important; }
[data-testid="stTabPanel"]{ width:100% !important; box-sizing:border-box; }
[data-testid="stHorizontalBlock"]{ align-items:stretch; }
[data-testid="stColumn"] > [data-testid="stVerticalBlock"], [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"]:has(> [class*="st-key-card-"]){ height:100%; }
[class*="st-key-card-"]{ height:100%; box-sizing:border-box; }
[data-testid="stFileUploaderDropzone"]:has([data-testid="stFileChips"]){ border-style:solid !important; border-color:var(--ok-line) !important; background:var(--ok-bg2) !important; }
[data-testid="stFileChips"]{ width:100%; }
[data-testid="stFileChip"]{ background:var(--surface) !important; border:1px solid var(--ok-line) !important; border-radius:14px !important; padding:.85rem 1rem !important; gap:12px !important; box-shadow:var(--shadow-1); width:100%; box-sizing:border-box; }
[data-testid="stFileChip"] > div:first-child{ background:var(--ok-bg) !important; color:var(--ok) !important; border-radius:10px !important; padding:6px; display:grid; place-items:center; }
[data-testid="stFileChip"] svg{ width:22px; height:22px; }
[data-testid="stFileChipName"]{ font-size:1rem !important; font-weight:620 !important; color:var(--ink) !important; }
[data-testid="stFileChipDeleteBtn"] button{ color:var(--ink-3) !important; }

[class*="st-key-rk-"] [data-testid="stExpander"]{ border:0 !important; border-top:1px solid var(--line) !important; border-radius:0 !important; box-shadow:none !important; background:transparent !important; margin-top:.6rem; }
[class*="st-key-rk-"] [data-testid="stExpander"] details{ border:0 !important; border-radius:0 !important; background:transparent !important; box-shadow:none !important; }
[class*="st-key-rk-"] [data-testid="stExpander"] details summary p{ font:600 .96rem var(--body) !important; color:var(--accent) !important; }
[data-testid="stFileUploaderDropzone"]:has([data-testid="stFileChips"]){ height:auto !important; align-items:stretch; justify-content:center; }
[data-testid="stFileChips"], [data-testid="stFileChips"] > div{ max-height:none !important; overflow:visible !important; height:auto !important; }
[data-testid="stFileChips"] > div > div{ margin-bottom:8px; }
[data-testid="stTabPanel"]{ max-width:1160px; margin:0 auto; padding:3rem 1.5rem 4rem !important; }
[data-testid="stTabPanel"] > div > [data-testid="stVerticalBlock"]{ gap:1.4rem; }

/* ── headings ────────────────────────────────────────────────────────── */
.hero{ text-align:center; max-width:780px; margin:0 auto .6rem; }
.hero h1{ font:760 clamp(2.5rem,5.4vw,3.8rem)/1.03 var(--head) !important; letter-spacing:-.04em; margin:0 0 1.1rem; text-wrap:balance; }
.hero p{ font-size:1.18rem; line-height:1.6; color:var(--ink-2); margin:0 auto; max-width:60ch; text-wrap:balance; }
.hero.sm h1{ font-size:clamp(2rem,4vw,2.7rem) !important; }
.sec-h{ font:700 1.5rem/1.2 var(--head); letter-spacing:-.02em; margin:.8rem 0 0; }
.sec-p{ color:var(--ink-2); font-size:1.02rem; margin:.3rem 0 0; }

/* ── input cards ─────────────────────────────────────────────────────── */
[class*="st-key-card-"]{
  background:var(--card); border:1px solid var(--line); border-radius:22px;
  padding:1.7rem 1.8rem 1.9rem; box-shadow:var(--shadow-2); gap:1rem; }
.ch{ display:flex; align-items:center; gap:14px; margin-bottom:.3rem; }
.ch-ic{ width:46px; height:46px; border-radius:14px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; flex:none; }
.ch-t{ font:680 1.3rem/1.2 var(--head); letter-spacing:-.015em; }
.ch-s{ color:var(--ink-3); font-size:.98rem; margin-top:2px; }

[data-testid="stFileUploaderDropzone"]{
  background:var(--field) !important; border:1.8px dashed var(--accent-line) !important; border-radius:18px !important;
  min-height:214px; padding:1.6rem 1.2rem !important; display:flex; flex-direction:column !important;
  align-items:center; justify-content:center; gap:1rem; text-align:center; transition:border-color .15s, background .15s; }
[data-testid="stFileUploaderDropzone"]:hover{ border-color:var(--accent) !important; background:var(--accent-soft) !important; }
[data-testid="stFileUploaderDropzoneInstructions"]{ flex-direction:column; align-items:center; justify-content:center; text-align:center; gap:.3rem; height:auto !important; min-height:0 !important; flex:0 0 auto !important; width:100%; }
[data-testid="stFileUploaderDropzoneInstructions"] > div{ display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; height:auto !important; width:100%; }
[data-testid="stFileUploaderDropzone"] > span{ display:flex; justify-content:center; width:100%; }
[data-testid="stFileUploaderDropzone"]{ justify-content:center !important; align-items:center !important; }
/* the upload box grows to fill its card so both cards line up */
[class*="st-key-card-"] > [data-testid="stElementContainer"]:has([data-testid="stFileUploader"]){ flex:1 1 auto; display:flex; flex-direction:column; }
[class*="st-key-card-"] [data-testid="stFileUploader"]{ flex:1 1 auto; display:flex; flex-direction:column; }
[class*="st-key-card-"] [data-testid="stFileUploader"] > section, [class*="st-key-card-"] [data-testid="stFileUploader"] > div{ flex:1 1 auto; }
[class*="st-key-card-"] [data-testid="stFileUploaderDropzone"]{ height:100% !important; }
[data-testid="stFileUploaderDropzoneInstructions"] span{ font-size:1.02rem !important; color:var(--ink) !important; font-weight:560; }
[data-testid="stFileUploaderDropzoneInstructions"] small{ color:var(--ink-3) !important; font-size:.9rem !important; }
[data-testid="stFileUploaderDropzoneInstructions"] [data-testid="stIconMaterial"]{ color:var(--accent) !important; font-size:2.4rem !important; }
[data-testid="stFileUploaderFile"]{
  background:var(--surface); border:1px solid var(--accent-line); border-radius:14px; padding:.7rem .9rem; margin-top:.5rem;
  box-shadow:var(--shadow-1); }
[data-testid="stFileUploaderFile"] [data-testid="stIconMaterial"]{ color:var(--accent); }
[data-testid="stFileUploaderFileName"]{ font-weight:600; color:var(--ink); }

textarea{
  background:var(--field) !important; color:var(--ink) !important; border-radius:16px !important;
  font:400 1.02rem/1.6 var(--body) !important; padding:1.05rem 1.15rem !important; }
[data-baseweb="textarea"], [data-baseweb="base-input"]{ background:var(--field) !important; border-radius:16px !important; }
[data-baseweb="textarea"]{ border:1.5px solid var(--line) !important; transition:border-color .15s, box-shadow .15s, background .15s; }
[data-baseweb="textarea"]:focus-within{ border-color:var(--accent) !important; background:var(--surface) !important; box-shadow:0 0 0 4px rgba(59,63,216,.12); }
textarea::placeholder{ color:var(--ink-3) !important; }

[data-testid="stButtonGroup"] button{ border-radius:10px !important; font:560 .94rem var(--body) !important; }

/* ── buttons ─────────────────────────────────────────────────────────── */
[data-testid="stBaseButton-primary"]{
  background:var(--btn) !important; border:0 !important; border-radius:15px !important; min-height:3.5rem;
  box-shadow:0 1px 0 rgba(255,255,255,.22) inset, 0 12px 26px -12px rgba(59,63,216,.7);
  transition:background .15s, transform .15s, box-shadow .15s; }
[data-testid="stBaseButton-primary"] p{ font:650 1.08rem var(--head) !important; color:#fff !important; letter-spacing:-.005em; }
[data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"]{ color:#fff !important; }
[data-testid="stBaseButton-primary"]:hover{ background:var(--btn-h) !important; transform:translateY(-1px); box-shadow:0 1px 0 rgba(255,255,255,.22) inset, 0 16px 30px -12px rgba(59,63,216,.75); }
[data-testid="stBaseButton-primary"]:active{ transform:translateY(0); }
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-popover"]{
  background:var(--surface) !important; border:1px solid var(--line) !important; border-radius:12px !important; color:var(--ink) !important;
  transition:border-color .15s, background .15s; }
[data-testid="stBaseButton-secondary"]:hover, [data-testid="stBaseButton-popover"]:hover{ border-color:var(--accent) !important; background:var(--accent-soft) !important; }
[data-testid="stBaseButton-secondary"] p, [data-testid="stBaseButton-popover"] p{ font-weight:560 !important; color:var(--ink) !important; }

/* ── connector thread, role pill ─────────────────────────────────────── */
.thread{ position:relative; height:56px; margin-top:-.2rem; }
.thread i{ position:absolute; display:block; border:0 solid var(--accent-line); }
.thread .l{ left:23.6%; width:26.4%; top:0; height:28px; border-left-width:2px; border-bottom-width:2px; border-bottom-left-radius:16px; }
.thread .r{ left:50%; width:26.4%; top:0; height:28px; border-right-width:2px; border-bottom-width:2px; border-bottom-right-radius:16px; }
.thread .m{ left:50%; top:28px; height:28px; margin-left:-1px; border-left-width:2px; }
.role{ display:flex; justify-content:center; margin-top:-.3rem; }
.role-in{ display:inline-flex; align-items:center; gap:12px; background:var(--surface); border:1px solid var(--accent-line);
  border-radius:99px; padding:9px 22px 9px 10px; box-shadow:var(--shadow-1); max-width:100%; }
.role-ic{ width:32px; height:32px; border-radius:50%; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; flex:none; }
.role-k{ color:var(--ink-3); font-size:.95rem; }
.role-v{ font:680 1.1rem/1.2 var(--head); letter-spacing:-.01em; }
.role-in.none{ border-color:var(--warn-line); } .role-in.none .role-ic{ background:var(--warn-bg); color:var(--warn); }

/* ── panels, chips, bars ─────────────────────────────────────────────── */
.panel{ background:var(--card); border:1px solid var(--line); border-radius:22px; padding:1.8rem 2rem; box-shadow:var(--shadow-1); }
.panel-h{ display:flex; align-items:baseline; justify-content:space-between; gap:1rem; flex-wrap:wrap; margin-bottom:1.2rem; }
.panel-t{ font:700 1.3rem var(--head); letter-spacing:-.015em; }
.panel-s{ color:var(--ink-2); font-size:.98rem; }
.chips{ display:flex; flex-wrap:wrap; gap:8px; }
.chip{ display:inline-flex; align-items:center; gap:6px; border-radius:99px; padding:6px 13px 6px 10px; font:540 .92rem/1.2 var(--body); }
.chip .ic{ width:15px; height:15px; }
.chip.ok{ background:var(--ok-bg); color:var(--ok); } .chip.bad{ background:var(--bad-bg); color:var(--bad); }
.chip.neutral{ background:var(--chip); color:var(--ink-2); } .chip.accent{ background:var(--accent-soft); color:var(--accent); }
.chip.warn{ background:var(--warn-bg); color:var(--warn); }
.chip.plain{ padding-left:13px; }
.nf{ color:var(--ink-3); font-size:.95rem; }
.t-ok{ --c:#1F9D63; } .t-accent{ --c:var(--accent); } .t-warn{ --c:#D89A1E; } .t-bad{ --c:#D9534F; } .t-soft{ --c:#AEB3D6; }
.bar{ height:10px; border-radius:99px; background:var(--track); overflow:hidden; }
.bar i{ display:block; height:100%; width:var(--w); border-radius:99px; background:var(--c); animation:grow .9s cubic-bezier(.2,.8,.2,1) both; }
@keyframes grow{ from{ width:0; } }
.bar-h{ display:flex; justify-content:space-between; align-items:baseline; margin-bottom:9px; font-size:.98rem; color:var(--ink-2); }
.bar-h b{ font:680 1.1rem var(--head); color:var(--ink); }
.bar-n{ color:var(--ink-3); font-size:.88rem; margin-top:7px; }

/* ── candidate summary ───────────────────────────────────────────────── */
.cand{ display:grid; grid-template-columns:minmax(0,1fr) auto; gap:2rem 2.5rem; align-items:center; }
.cand-id{ display:flex; gap:1.3rem; align-items:center; min-width:0; }
.av{ border-radius:50%; display:grid; place-items:center; font:700 1rem var(--head); flex:none; letter-spacing:.01em; }
.av.lg{ width:76px; height:76px; font-size:1.6rem; }
.av.md{ width:46px; height:46px; font-size:1.02rem; }
.av-0{ background:#E8E9FD; color:#3B3FD8; } .av-1{ background:#E3F2EF; color:#17695A; } .av-2{ background:#FBEBDD; color:#9A4B12; }
.av-3{ background:#F3E8F7; color:#7A3A93; } .av-4{ background:#E6EEF9; color:#24569A; } .av-5{ background:#F6EEDC; color:#7A5A0E; }
.cand-sub{ color:var(--ink-2); font-size:1.08rem; margin-top:.35rem; }
.cand-name{ font:720 2rem/1.1 var(--head); letter-spacing:-.03em; overflow-wrap:anywhere; }
.contact{ display:flex; flex-wrap:wrap; gap:.55rem 1.4rem; margin-top:.8rem; color:var(--ink-2); font-size:1rem; }
.contact span{ display:inline-flex; align-items:center; gap:8px; overflow-wrap:anywhere; }
.contact .ic{ color:var(--ink-3); }
.cand-score{ display:flex; align-items:center; gap:1.4rem; }
@property --p{ syntax:'<number>'; inherits:false; initial-value:0; }
.ring{ --p:0; position:relative; width:128px; height:128px; border-radius:50%; flex:none;
  background:conic-gradient(var(--c) calc(var(--p) * 1%), var(--track) 0); display:grid; place-items:center;
  animation:ringin 1.1s cubic-bezier(.2,.8,.2,1) both; }
@keyframes ringin{ from{ --p:0; } }
.ring::before{ content:""; position:absolute; inset:11px; background:var(--card); border-radius:50%; }
.ring b{ position:relative; font:740 1.7rem var(--head); letter-spacing:-.03em; }
.verdict-k{ color:var(--ink-3); font-size:.95rem; margin-bottom:6px; }
.verdict{ font:700 1.35rem/1.2 var(--head); letter-spacing:-.02em; margin-top:10px; max-width:15ch; }
.bars{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:2rem; margin-top:1.8rem; padding-top:1.6rem; border-top:1px solid var(--line-2); }
.formula{ color:var(--ink-3); font-size:.9rem; margin-top:1.2rem; }

.sg + .sg{ margin-top:1.6rem; }
.sg-h{ display:flex; align-items:center; gap:10px; font:660 1.05rem var(--head); margin-bottom:.8rem; }
.count{ background:var(--chip); border-radius:99px; padding:2px 10px; font:560 .85rem var(--body); color:var(--ink-2); }
.cover{ margin-bottom:1.6rem; }

.xc{ display:flex; flex-wrap:wrap; gap:8px; }
.fr{ display:grid; grid-template-columns:210px minmax(0,1fr); gap:1rem 1.5rem; padding:1.15rem 0; border-top:1px solid var(--line-2); }
.fr-k{ display:flex; align-items:flex-start; gap:11px; color:var(--ink); font-weight:600; }
.fr-k .ic{ color:var(--accent); margin-top:2px; }
.vl{ display:flex; flex-direction:column; gap:7px; }
.vl div{ line-height:1.5; overflow-wrap:anywhere; }
.vl small{ color:var(--ink-3); margin-left:8px; }
.entry{ padding:1rem 0; border-bottom:1px solid var(--line-2); }
.entry:last-child{ border-bottom:0; }
.entry-h{ display:flex; justify-content:space-between; gap:1rem; color:var(--ink-3); font-size:.9rem; font-weight:560; margin-bottom:6px; }
.entry-p{ line-height:1.65; margin:0; }
.entry-t{ color:var(--ink); font:650 1.05rem var(--head); }
.entry-l{ margin:.2rem 0 0 1.1rem; padding:0; line-height:1.6; color:var(--ink-2); }
.vl .sub{ color:var(--ink-3); font-size:.94rem; margin:1px 0 6px; }

/* ── ranking ─────────────────────────────────────────────────────────── */
.sumline{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:1.5rem; }
.sumline > div + div{ border-left:1px solid var(--line-2); padding-left:1.5rem; }
.sum-k{ color:var(--ink-3); font-size:.95rem; }
.sum-v{ font:720 1.9rem/1.15 var(--head); letter-spacing:-.025em; margin-top:4px; overflow-wrap:anywhere; }
.sum-v small{ font:500 1rem var(--body); color:var(--ink-2); letter-spacing:0; margin-left:6px; }
[class*="st-key-toolbar"]{ background:var(--card); border:1px solid var(--line); border-radius:18px; padding:.9rem 1rem; box-shadow:var(--shadow-1); }
[class*="st-key-rk-"]{ background:var(--card); border:1px solid var(--line); border-radius:20px; padding:1.2rem 1.5rem .7rem;
  box-shadow:var(--shadow-1); gap:.6rem; transition:border-color .15s, box-shadow .15s; }
[class*="st-key-rk-"]:hover{ border-color:var(--line-3); box-shadow:var(--shadow-2); }
.rk{ display:grid; grid-template-columns:34px 46px minmax(0,1.4fr) minmax(190px,1.1fr) 92px 176px; gap:1.1rem; align-items:center; }
.rk-rank{ font:700 1.05rem var(--head); color:var(--ink-3); }
.rk-rank.top{ width:32px; height:32px; border-radius:50%; background:var(--btn); color:#fff; display:grid; place-items:center; font-size:.95rem; }
.rk-name{ font:660 1.12rem/1.25 var(--head); letter-spacing:-.01em; overflow-wrap:anywhere; }
.rk-mail{ color:var(--ink-3); font-size:.92rem; overflow-wrap:anywhere; }
.rk-pct{ font:700 1.05rem var(--head); }
.rk-skills{ display:flex; gap:12px; font-size:.95rem; font-weight:560; }
.rk-skills span{ white-space:nowrap; display:inline-flex; align-items:center; gap:5px; }
.rk-skills .ok{ color:var(--ok); } .rk-skills .bad{ color:var(--bad); }
[class*="st-key-rk-"] [data-testid="stExpander"]{ border:0 !important; background:transparent !important; box-shadow:none !important; }
[class*="st-key-rk-"] [data-testid="stExpander"] details summary{ padding:.5rem 0 !important; color:var(--accent); }
[class*="st-key-rk-"] [data-testid="stExpander"] details > div{ padding:.4rem 0 1rem !important; }

/* ── metrics ─────────────────────────────────────────────────────────── */
.mc{ background:var(--card); border:1px solid var(--line); border-radius:22px; padding:1.6rem 1.7rem 1.7rem; box-shadow:var(--shadow-1); height:100%; }
.mc-h{ display:flex; align-items:center; gap:10px; font:650 1.1rem var(--head); color:var(--ink-2); }
.mc-ic{ width:34px; height:34px; border-radius:10px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; }
.mc-v{ font:750 3.1rem/1 var(--head); letter-spacing:-.045em; margin:1.2rem 0 .5rem; font-variant-numeric:proportional-nums; }
.mc-d{ color:var(--ink-2); font-size:.98rem; line-height:1.5; margin-bottom:1.1rem; min-height:3em; }
.cf{ display:grid; grid-template-columns:64px minmax(0,1fr); gap:1.2rem; padding:1.3rem 0; border-top:1px solid var(--line-2); align-items:start; }
.cf:first-of-type{ border-top:0; padding-top:0; }
.cf-n{ width:56px; height:56px; border-radius:16px; display:grid; place-items:center; font:740 1.5rem var(--head); }
.cf-n.ok{ background:var(--ok-bg); color:var(--ok); } .cf-n.warn{ background:var(--warn-bg); color:var(--warn); } .cf-n.bad{ background:var(--bad-bg); color:var(--bad); }
.cf-t{ font:660 1.1rem var(--head); margin-bottom:3px; } .cf-d{ color:var(--ink-2); margin-bottom:.8rem; line-height:1.5; }

/* ── states ──────────────────────────────────────────────────────────── */
.es{ display:flex; flex-direction:column; align-items:center; text-align:center; padding:3.2rem 1.5rem;
  border:1.8px dashed var(--line-3); border-radius:22px; background:var(--dz); }
.es-ic{ width:60px; height:60px; border-radius:18px; background:var(--accent-soft); color:var(--accent); display:grid; place-items:center; margin-bottom:1.1rem; }
.es-t{ font:680 1.35rem var(--head); letter-spacing:-.015em; margin-bottom:.4rem; }
.es-p{ color:var(--ink-2); font-size:1.02rem; line-height:1.6; max-width:50ch; }
.nt{ display:flex; gap:12px; align-items:flex-start; padding:14px 18px; border-radius:16px; border:1px solid; line-height:1.5; }
.nt b{ display:block; font:660 1rem var(--head); }
.nt.err{ background:var(--bad-bg); border-color:#F3C6BF; color:var(--bad); }
.nt.warn{ background:var(--warn-bg); border-color:#EBD9B4; color:var(--warn); }
.nt.ok{ background:var(--ok-bg); border-color:#BFE3D0; color:var(--ok); }
.nt span{ color:var(--ink); font-size:.96rem; }
.nt .ic{ margin-top:2px; }

/* ── native widgets ──────────────────────────────────────────────────── */
[data-testid="stExpander"]{ background:var(--card) !important; border:1px solid var(--line) !important; border-radius:18px !important; overflow:hidden; box-shadow:var(--shadow-1); }
[data-testid="stExpander"] details summary{ padding:1.05rem 1.4rem !important; transition:background .15s; }
[data-testid="stExpander"] details summary:hover{ background:var(--field); }
[data-testid="stExpander"] details summary p{ font:650 1.05rem var(--head) !important; }
[data-testid="stExpander"] details > div{ padding:.3rem 1.4rem 1.3rem !important; }
/* centered text: expander titles and the Paste text / Upload file toggle */
[data-testid="stExpander"] details summary{ justify-content:center !important; text-align:center !important; }
[data-testid="stExpander"] details summary > div{ justify-content:center !important; text-align:center !important; width:100%; }
[data-testid="stExpander"] details summary p{ text-align:center !important; }
[data-testid="stButtonGroup"]{ justify-content:center !important; }
[data-testid="stButtonGroup"]{ margin-top:.7rem !important; margin-bottom:.4rem !important; }
[data-testid="stButtonGroup"] button, [data-testid="stButtonGroup"] button p{ justify-content:center !important; text-align:center !important; }
[data-testid="stDataFrame"]{ border:1px solid var(--line); border-radius:14px; overflow:hidden; }
[data-baseweb="select"] > div, [data-testid="stTextInput"] [data-baseweb="base-input"]{
  background:var(--field) !important; border:1.5px solid var(--line) !important; border-radius:12px !important; min-height:2.8rem; }
[data-testid="stTextInput"] input{ font-size:1rem !important; }
[data-testid="stTextInput"] [data-baseweb="base-input"]:focus-within{ border-color:var(--accent) !important; background:var(--surface) !important; }
[data-baseweb="tag"]{ background:var(--accent-soft) !important; color:var(--accent) !important; border-radius:99px !important; }
[data-baseweb="tag"] span{ color:var(--accent) !important; }
[data-testid="stCaptionContainer"]{ color:var(--ink-3); }
[data-testid="stProgress"] > div > div > div{ background:var(--accent) !important; }
[data-testid="stCode"] pre, pre{ background:var(--code) !important; border:1px solid var(--line) !important; border-radius:14px !important; }
[data-testid="stPlotlyChart"]{ background:var(--card); border:1px solid var(--line); border-radius:20px; padding:.6rem .9rem; box-shadow:var(--shadow-1); }
.foot{ text-align:center; color:var(--ink-3); font-size:.92rem; padding:1.6rem 1rem 2.4rem; border-top:1px solid var(--line); max-width:1160px; margin:0 auto; }

/* ── tablet and phone ────────────────────────────────────────────────── */
@media (max-width:1000px){
  .rk{ grid-template-columns:34px 46px minmax(0,1fr) auto; row-gap:.9rem; }
  .rk-score{ grid-column:1 / -1; order:5; }
  .rk-skills{ grid-column:1 / -1; order:6; }
  [role="tablist"]::after{ display:none; }
  .cand{ grid-template-columns:1fr; }
}
@media (max-width:760px){
  [data-testid="stTabPanel"]{ padding:2rem 1rem 3rem !important; }
  [role="tablist"]{ padding:0 .8rem !important; height:60px; }
  [role="tablist"]::before{ content:""; padding-left:34px; margin-right:.8rem; }
  [data-testid="stTab"]{ height:60px; padding:0 9px !important; gap:5px; }
  [data-testid="stTab"] p{ font-size:.88rem !important; }
  .thread{ display:none; } .role{ margin-top:0; }
  [class*="st-key-card-"]{ padding:1.3rem 1.2rem 1.4rem; }
  .panel{ padding:1.4rem 1.2rem; }
  .bars, .sumline{ grid-template-columns:1fr; gap:1.4rem; }
  .sumline > div + div{ border-left:0; padding-left:0; border-top:1px solid var(--line-2); padding-top:1.2rem; }
  .fr{ grid-template-columns:1fr; gap:.6rem; }
  .cand-id{ flex-direction:column; align-items:flex-start; }
  .cand-score{ flex-direction:column; align-items:flex-start; }
  .cand-name{ font-size:1.65rem; }
  .cf{ grid-template-columns:48px minmax(0,1fr); gap:.9rem; } .cf-n{ width:48px; height:48px; font-size:1.25rem; }
  [class*="st-key-rk-"]{ padding:1rem 1rem .5rem; }
}
@media (prefers-reduced-motion:reduce){
  .bar i, .ring{ animation:none !important; }
  [data-testid="stBaseButton-primary"]{ transition:none; }
}
</style>
""".replace("__LOGO__", LOGO)
st.markdown(CSS, unsafe_allow_html=True)

DARK_CSS = """
<style>
:root{
  color-scheme:dark;
  --paper:#0E1120; --card:#161A2C; --field:#1A1F35; --surface:#1D2240;
  --ink:#ECEEFB; --ink-2:#B6BCDB; --ink-3:#8E95BA;
  --line:#2A3050; --line-2:#222845; --line-3:#3A416B;
  --accent:#9A9DF8; --accent-h:#B3B5FA; --accent-soft:#242858; --accent-line:#3E4490;
  --ok:#4CC38A; --ok-bg:#12302A; --bad:#F0766B; --bad-bg:#3A1E22; --warn:#E5B25D; --warn-bg:#33290F;
  --chip:#262B4A; --track:#2B3152; --code:#10142A; --dz:rgba(22,26,44,.65); --bar:rgba(14,17,32,.92);
  --ok-line:#215345; --ok-bg2:#10261F; --btn:#4F53E8; --btn-h:#6468F0; --warn-line:#5A4720;
  --shadow-1:0 1px 2px rgba(0,0,0,.35);
  --shadow-2:0 1px 2px rgba(0,0,0,.4), 0 18px 36px -20px rgba(0,0,0,.7);
}
.t-ok{ --c:#4CC38A; } .t-warn{ --c:#E5B25D; } .t-bad{ --c:#F0766B; } .t-soft{ --c:#5A6290; }
.av-0{ background:#25285A; color:#B5B8FB; } .av-1{ background:#143A33; color:#74D6BE; } .av-2{ background:#40281A; color:#F0B27F; }
.av-3{ background:#3A2548; color:#D9A8EE; } .av-4{ background:#1D3358; color:#94BDF3; } .av-5{ background:#3B3216; color:#E6C877; }
.nt.err{ border-color:#6A2F36; } .nt.ok{ border-color:#23604A; }
[data-testid="stApp"], [data-testid="stApp"] p, [data-testid="stApp"] span, [data-testid="stApp"] label{ color:var(--ink); }
[data-testid="stApp"] .ch-s, [data-testid="stApp"] .nf, [data-testid="stApp"] .sec-p, [data-testid="stApp"] .bar-n{ color:var(--ink-3); }
[data-testid="stApp"] .hero p, [data-testid="stApp"] .panel-s, [data-testid="stApp"] .cand-sub{ color:var(--ink-2); }
[data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"]{ color:#fff !important; }
[data-baseweb="textarea"], [data-baseweb="textarea"] textarea, [data-baseweb="base-input"], [data-baseweb="base-input"] input,
[data-baseweb="select"] > div{ background:var(--field) !important; color:var(--ink) !important; border-color:var(--line) !important; }
[data-baseweb="popover"] > div, [data-baseweb="menu"], [data-testid="stPopoverBody"], [data-baseweb="popover"] ul{ background:var(--surface) !important; color:var(--ink) !important; }
[data-testid="stExpander"] details, [data-testid="stExpander"] summary{ background:transparent !important; color:var(--ink) !important; }
[data-testid="stExpander"], [data-testid="stExpander"] details{ border-color:var(--line) !important; }
[data-testid="stExpander"] details{ border:1px solid var(--line) !important; }
[data-testid="stExpanderDetails"], [data-testid="stExpander"] summary{ border-color:var(--line) !important; }
[data-testid="stButtonGroup"] button{ background:var(--surface) !important; color:var(--ink) !important; border-color:var(--line) !important; }
[data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[aria-pressed="true"],
[data-testid="stButtonGroup"] button[data-testid*="Active"]{ background:var(--accent-soft) !important; color:var(--accent) !important; border-color:var(--accent-line) !important; }
[data-testid="stTextAreaRootElement"], [data-testid="stTextInputRootElement"]{ background:var(--field) !important; border-color:var(--line) !important; }
[data-testid="stTextAreaRootElement"]:focus-within{ border-color:var(--accent) !important; }
[data-testid="stPopoverButton"]{ background:var(--surface) !important; color:var(--ink) !important; border-color:var(--line) !important; }
[data-testid="stPopoverButton"] p, [data-testid="stPopoverButton"] span{ color:var(--ink) !important; }
[data-testid="stCode"] pre, pre, code{ color:var(--ink) !important; }
[data-testid="stSlider"] [role="slider"]{ background:var(--accent) !important; }
</style>
"""
dark = bool(st.session_state.get("theme_dark", False))
if dark:
    st.markdown(DARK_CSS, unsafe_allow_html=True)
set_chart_theme(dark)

THEME_CSS = """
<style>
.st-key-themebox{ position:fixed; top:0; height:66px; display:flex; align-items:center; z-index:101; width:auto !important;
  right:max(0.5rem, calc((100% - 1160px) / 2 + 0.5rem)); padding-top:6px; }
.st-key-themebox, .st-key-themebox > div, .st-key-themebox [data-testid="stElementContainer"], .st-key-themebox [data-testid="stVerticalBlock"]{ margin:0 !important; padding:0 !important; gap:0 !important; height:66px; display:flex !important; align-items:center !important; justify-content:center; }
.st-key-themebox [data-testid="stCheckbox"], .st-key-themebox label{ align-items:center; }
.st-key-themebox [data-testid="stCheckbox"], .st-key-themebox [data-testid="stToggle"]{ margin:0; }
.st-key-themebox label p{ font:560 .86rem var(--body) !important; color:var(--ink-2) !important; }
@media (max-width:900px){ .st-key-themebox{ right:1rem; } [role="tablist"]::after{ margin-right:0; } }
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)
with st.container(key="themebox"):
    st.toggle("Dark mode", key="theme_dark")

# ── icons (one stroke style throughout) ─────────────────────────────────────
ICONS = {
 "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
 "briefcase": '<rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>',
 "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
 "minus": '<path d="M5 12h14"/>',
 "mail": '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
 "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
 "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
 "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/>',
 "cap": '<path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/>',
 "calendar": '<path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/>',
 "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
 "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
 "award": '<circle cx="12" cy="8" r="6"/><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"/>',
 "alert": '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
 "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
 "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
 "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
 "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
 "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
 "user": '<path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
}
def icon(name, size=18):
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

# ── small view helpers ──────────────────────────────────────────────────────
GRADE_TONE = {"Excellent": "ok", "Strong": "ok", "Good": "accent", "Fair": "warn", "Weak": "bad"}
GRADE_CHIP = {"Excellent": "ok", "Strong": "ok", "Good": "accent", "Fair": "warn", "Weak": "bad"}

def md(html):
    # Markdown turns a blank line or a 4-space indent into a code block, so flatten the HTML first.
    flat = "\n".join(l.strip() for l in html.splitlines() if l.strip())
    st.markdown(flat, unsafe_allow_html=True)

def chip(text, tone="neutral", ic=None):
    return f'<span class="chip {tone}{"" if ic else " plain"}">{icon(ic, 15) if ic else ""}{esc(str(text))}</span>'

def chips(items, tone, ic=None, empty="None"):
    if not items: return f'<span class="nf">{esc(empty)}</span>'
    return '<div class="chips">' + "".join(chip(i, tone, ic) for i in items) + '</div>'

def bar(label, pct, tone, note=""):
    pct = max(0.0, min(100.0, float(pct)))
    n = f'<div class="bar-n">{esc(note)}</div>' if note else ""
    return (f'<div class="t-{tone}"><div class="bar-h"><span>{esc(label)}</span><b>{pct:.1f}%</b></div>'
            f'<div class="bar" role="img" aria-label="{esc(label)} {pct:.1f} percent"><i style="--w:{pct}%"></i></div>{n}</div>')

def avatar(name, size="md"):
    parts = re.findall(r"[A-Za-z]+", name or "")
    ini = ((parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()) if parts else "?"
    k = int(hashlib.md5((name or "").encode()).hexdigest()[:2], 16) % 6
    return f'<div class="av {size} av-{k}" aria-hidden="true">{esc(ini)}</div>'

def card_head(ic, title, sub):
    md(f'<div class="ch"><span class="ch-ic">{icon(ic, 22)}</span><div><div class="ch-t">{esc(title)}</div>'
       f'<div class="ch-s">{esc(sub)}</div></div></div>')

def hero(title, lead, small=False):
    md(f'<div class="hero{" sm" if small else ""}"><h1>{esc(title)}</h1><p>{esc(lead)}</p></div>')

def notice(kind, title, body=""):
    ic = {"err": "alert", "warn": "alert", "ok": "check"}[kind]
    b = f'<span>{esc(body)}</span>' if body else ""
    md(f'<div class="nt {kind}" role="alert">{icon(ic, 20)}<div><b>{esc(title)}</b>{b}</div></div>')

def empty_state(ic, title, body):
    md(f'<div class="es"><div class="es-ic">{icon(ic, 28)}</div><div class="es-t">{esc(title)}</div>'
       f'<div class="es-p">{esc(body)}</div></div>')

def panel(title, body, sub=""):
    s = f'<span class="panel-s">{esc(sub)}</span>' if sub else ""
    return f'<div class="panel"><div class="panel-h"><span class="panel-t">{esc(title)}</span>{s}</div>{body}</div>'

def role_pill(jd_text):
    """Job role detected in the JD, shown just under the resume/JD inputs."""
    if not (jd_text or "").strip():
        md('<div class="thread" aria-hidden="true"><i class="l"></i><i class="r"></i><i class="m"></i></div>')
        return
    role = extract_job_role(jd_text)
    md('<div class="thread" aria-hidden="true"><i class="l"></i><i class="r"></i><i class="m"></i></div>')
    if role:
        md(f'<div class="role"><div class="role-in"><span class="role-ic">{icon("target", 17)}</span>'
           f'<span class="role-k">Job role found</span><span class="role-v">{esc(role)}</span></div></div>')
    else:
        md(f'<div class="role"><div class="role-in none"><span class="role-ic">{icon("alert", 17)}</span>'
           f'<span class="role-k">No job role found. Add a line like “Job Title: Data Analyst”.</span></div></div>')

def jd_input(key):
    """Job description input: paste text or upload a file. Returns the text."""
    mode = st.segmented_control("Job description source", ["Paste text", "Upload file"], default="Paste text",
                                key=f"{key}_mode", label_visibility="collapsed") or "Paste text"
    if mode == "Paste text":
        return st.text_area("Job description", height=214, placeholder="Paste the job description here…",
                            label_visibility="collapsed", key=f"{key}_text")
    text = ""
    f = st.file_uploader("Job description file", type=["pdf", "docx", "txt"], key=f"{key}_file",
                         label_visibility="collapsed")
    if f:
        tmp = save_upload(f); text = extract_text(tmp); os.unlink(tmp)
    return text

@st.cache_data(show_spinner=False, max_entries=24)
def get_entities(raw):
    return extract_resume_entities(raw) if raw else []

def ents_of(ents, *labels):
    seen, out = set(), []
    for e in ents:
        if e["label"] in labels and e["entity"].lower() not in seen:
            seen.add(e["entity"].lower()); out.append(e["entity"])
    return out

def fmt_phone(v):
    return v or ""

# ── header ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([":material/description: Single Resume",
                            ":material/groups: Multi-Resume Ranking",
                            ":material/analytics: NLP Metrics"])

# ═════════════════════════════════════════════════════════════════════════════
# SINGLE RESUME
# ═════════════════════════════════════════════════════════════════════════════
def run_single(resume_file, jd_text):
    w = st.session_state.get("w_cos", 0.55)
    with st.spinner("Reading the resume…"):
        tmp = save_upload(resume_file); parsed = parse_resume(tmp); os.unlink(tmp)
    with st.spinner("Scoring it against the job description…"):
        raw = parsed.get("raw_text", "")
        scores = candidate_score(raw, parsed.get("skills", []), jd_text,
                                 weights={"cosine": w, "skill": round(1 - w, 2)})
        ents = get_entities(raw)
    st.session_state["single"] = dict(parsed=parsed, scores=scores, ents=ents, raw=raw, jd=jd_text, w=w,
                                      role=extract_job_role(jd_text), fname=resume_file.name)

def render_single(res):
    p, s, ents, role = res["parsed"], res["scores"], res["ents"], res["role"]
    if not (res.get("raw") or "").strip():
        notice("err", "No text could be read from this file",
               "It looks like a scanned image and the OCR add-on could not start. Run: pip install rapidocr-onnxruntime"
               + (f" (reason: {esc(_struct.OCR_ERROR)})" if _struct.OCR_ERROR else ""))
        return
    if p.get("ocr"):
        notice("warn", "Scanned PDF, read with OCR",
               "Text was recognised from an image, so check the email, phone and numbers for small reading errors.")
    name = p.get("name") or os.path.splitext(res["fname"])[0]
    g = s["match_grade"]; tone = GRADE_TONE[g]
    n_match, n_miss = len(s["matched_skills"]), len(s["missing_skills"]); n_req = n_match + n_miss

    locs = ents_of(ents, "LOCATION"); orgs = ents_of(ents, "ORGANIZATION")
    insts = ents_of(ents, "INSTITUTION"); degrees = ents_of(ents, "DEGREE"); dates = ents_of(ents, "DATE")
    edu_fallback = [e.get("degree", "")[:110] for e in p.get("education", [])[:4] if e.get("degree")]

    contact = []
    if p.get("email"): contact.append(("mail", p["email"]))
    if p.get("phone"): contact.append(("phone", p["phone"]))
    if p.get("linkedin"): contact.append(("link", p["linkedin"]))
    if p.get("github"): contact.append(("link", p["github"]))
    loc_txt = p.get("location") or ", ".join(locs[:2])
    if loc_txt: contact.append(("pin", loc_txt))
    contact_html = "".join(f'<span>{icon(i, 17)}{esc(t)}</span>' for i, t in contact) or \
                   '<span class="nf">No contact details found</span>'

    md(f'''<div class="panel"><div class="cand">
      <div class="cand-id">{avatar(name, "lg")}<div style="min-width:0"><div class="cand-name">{esc(name)}</div>
      {('<div class="cand-sub">' + esc(p["headline"]) + '</div>') if p.get("headline") else ""}
      <div class="contact">{contact_html}</div></div></div>
      <div class="cand-score t-{tone}"><div class="ring" style="--p:{s["composite_score"]:.1f}" role="img"
        aria-label="Overall match {s["composite_score"]:.1f} percent"><b>{s["composite_score"]:.0f}%</b></div>
        <div><div class="verdict-k">Overall job match</div>{chip(g + " match", GRADE_CHIP[g])}
        <div class="verdict">{esc("for " + role) if role else "for this job description"}</div></div></div></div>
      <div class="bars">
        {bar("Overall score", s["composite_score"], tone, g)}
        {bar("Skill match", s["skill_match_pct"], "ok", f"{n_match} of {n_req} required skills")}
        {bar("Text similarity", s["cosine_similarity"], "soft", "TF-IDF cosine similarity")}
      </div>
      <div class="formula">Overall score is {int(res["w"]*100)}% text similarity and {int(round((1-res["w"])*100))}% skill match.
      Change the split under Scoring weights.</div></div>''')

    cover = (f'<div class="cover t-ok">{bar("Required skills found", (n_match / n_req * 100) if n_req else 0, "ok", f"{n_match} of {n_req} skills from the job description")}</div>'
             if n_req else '<div class="nf cover">No known skills were found in the job description.</div>')
    groups = (f'<div class="sg"><div class="sg-h">Matched<span class="count">{n_match}</span></div>{chips(s["matched_skills"], "ok", "check", "No matching skills")}</div>'
              f'<div class="sg"><div class="sg-h">Missing<span class="count">{n_miss}</span></div>{chips(s["missing_skills"], "bad", "x", "Nothing missing")}</div>'
              f'<div class="sg"><div class="sg-h">Extra skills not in the job description<span class="count">{len(s["extra_skills"])}</span></div>'
              f'{chips(s["extra_skills"][:24], "neutral", None, "None")}</div>')
    md(panel("Skills", cover + groups, "Green skills are on the resume. Red ones are asked for but not found."))

    # extraction checklist: what was found at all
    found = [("Name", bool(p.get("name"))), ("Email", bool(p.get("email"))), ("Phone", bool(p.get("phone"))),
             ("Skills", bool(p.get("skills"))), ("Education", bool(insts or degrees or edu_fallback)),
             ("Experience", bool(p.get("experience"))), ("Organizations", bool(orgs)),
             ("Location", bool(locs or p.get("location"))), ("Dates", bool(dates))]
    n_found = sum(1 for _, ok in found if ok)
    xc = '<div class="xc">' + "".join(chip(n, "ok", "check") if ok else chip(n + " not found", "neutral", "minus")
                                      for n, ok in found) + '</div>'

    def row(ic, label, inner):
        return f'<div class="fr"><div class="fr-k">{icon(ic, 19)}{esc(label)}</div><div>{inner}</div></div>'
    def lines(items, empty="Not found in this resume"):
        return ('<div class="vl">' + "".join(f'<div>{x}</div>' for x in items) + '</div>') if items else f'<span class="nf">{empty}</span>'
    edu_lines = []
    for e in p.get("education", [])[:5]:
        if not isinstance(e, dict): continue
        top = e.get("institution") or e.get("degree") or ""
        sub = " · ".join(x for x in [e.get("degree") if e.get("institution") else None, e.get("dates") or ", ".join(e.get("years", [])),
                                      ("GPA " + e["gpa"]) if e.get("gpa") else None] if x)
        if top:
            edu_lines.append(f'<b>{esc(top)}</b>' + (f'<div class="sub">{esc(sub)}</div>' if sub else ""))
    edu_lines = edu_lines or [f'<b>{esc(i)}</b>' for i in insts[:3]] + [esc(d) for d in degrees[:3]] or [esc(x) for x in edu_fallback]
    known = {x.lower() for x in s["matched_skills"] + s["missing_skills"] + s["extra_skills"]}
    other_sk = [x for x in p.get("listed_skills", []) if x.lower() not in known][:24]
    langs = p.get("languages", [])
    certs = [esc(c[:120]) for c in p.get("certifications", [])[:6]]
    ach = [esc(a[:120]) for a in p.get("achievements", [])[:6]]
    details = (f'<div style="margin-bottom:1.3rem"><div class="panel-s" style="margin-bottom:.8rem">{n_found} of {len(found)} fields extracted</div>{xc}</div>'
               + row("building", "Organizations", chips(orgs[:10], "accent", None, "Not found in this resume"))
               + row("cap", "Education", lines(edu_lines))
               + row("pin", "Location", chips(locs[:6], "neutral", None, "Not found in this resume"))
               + row("calendar", "Dates", chips(dates[:10], "neutral", None, "Not found in this resume"))
               + (row("code", "Other listed skills", chips(other_sk, "neutral", None, "")) if other_sk else "")
               + (row("users", "Languages", chips(langs, "neutral", None, "")) if langs else "")
               + row("award", "Certifications", lines(certs))
               + row("award", "Achievements", lines(ach)))
    md(panel("Extracted details", details, "Pulled from the resume text"))

    with st.expander("Work experience"):
        exp = p.get("experience", [])
        if exp:
            for e in exp:
                if e.get("title") or e.get("company"):
                    head = " · ".join(x for x in [e.get("title"), e.get("company")] if x)
                    meta = " · ".join(x for x in [e.get("dates"), e.get("location")] if x)
                    bl = "".join(f"<li>{esc(b)}</li>" for b in e.get("bullets", [])[:8])
                    md(f'<div class="entry"><div class="entry-h"><span class="entry-t">{esc(head)}</span><span>{esc(meta)}</span></div>'
                       + (f'<ul class="entry-l">{bl}</ul>' if bl else "") + '</div>')
                else:
                    md(f'<div class="entry"><div class="entry-h"><span>Entry</span><span>{esc(", ".join(e.get("dates_mentioned", [])[:3]))}</span></div>'
                       f'<p class="entry-p">{esc(e.get("description", "")[:300])}</p></div>')
        else:
            md('<span class="nf">No experience entries found.</span>')
    with st.expander("Projects"):
        proj = p.get("projects", [])
        if proj:
            for i, x in enumerate(proj, 1):
                md(f'<div class="entry"><div class="entry-h"><span>Project {i}</span></div><p class="entry-p">{esc(x[:300])}</p></div>')
        else:
            md('<span class="nf">No projects found.</span>')
    with st.expander("Advanced analysis"):
        a, b = st.columns(2, gap="large")
        with a: st.plotly_chart(skill_donut(n_match, n_miss, len(s["extra_skills"])), use_container_width=True)
        with b: st.plotly_chart(tfidf_top_terms(res["raw"], res["jd"]), use_container_width=True)
        st.plotly_chart(skill_bubble(s["matched_skills"], s["missing_skills"], s["extra_skills"]), use_container_width=True)
    with st.expander("Full JSON output"):
        export = {k: v for k, v in p.items() if k != "raw_text"}
        export["job_role"] = role
        export["match_analysis"] = s
        js = pretty_json(export)
        st.code(js, language="json")
        st.download_button("Download JSON", data=js, icon=":material/download:", key="dl_single",
                           file_name=f"{name.replace(' ', '_')}_analysis.json", mime="application/json")

with tab1:
    hero("Find the right match for every role.",
         "Extract candidate information, identify relevant skills, and evaluate resume-to-job fit.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.container(key="card-resume"):
            card_head("file", "Resume", "PDF or DOCX, up to 200 MB")
            resume_file = st.file_uploader("Resume", type=["pdf", "docx"], key="r1", label_visibility="collapsed")
    with c2:
        with st.container(key="card-jd"):
            card_head("briefcase", "Job description", "Paste the text or upload a file")
            jd_text = jd_input("single")
    role_pill(jd_text)
    _, mid, _ = st.columns([1, 1.15, 1])
    with mid:
        go = st.button("Analyse resume", key="btn_analyse", type="primary", icon=":material/search:", use_container_width=True)
        with st.popover("Scoring weights", icon=":material/tune:"):
            st.markdown("Choose how much text similarity counts against skill match.")
            st.slider("Text similarity (TF-IDF) weight", 0.0, 1.0, 0.55, 0.05, key="w_cos")
            st.caption(f"Skill match gets the remaining {int(round((1 - st.session_state.get('w_cos', 0.55)) * 100))}%.")
        if go:
            if not resume_file:
                notice("err", "Add a resume first", "Upload a PDF or DOCX file to analyse.")
            elif not jd_text.strip():
                notice("err", "Add a job description first", "Paste the text or upload a file to compare against.")
            else:
                run_single(resume_file, jd_text)
    res = st.session_state.get("single")
    if res:
        render_single(res)
    else:
        empty_state("file", "Your match report will appear here",
                    "Add a resume and a job description, then select Analyse resume. You get a match score, the skills that match or are missing, and the details found in the resume.")

# ═════════════════════════════════════════════════════════════════════════════
# MULTI-RESUME RANKING
# ═════════════════════════════════════════════════════════════════════════════
def run_rank(files, jd):
    cands = []
    prog = st.progress(0, text="Reading resumes…")
    for i, f in enumerate(files):
        prog.progress((i + 1) / len(files), text=f"Reading {f.name} ({i + 1} of {len(files)})…")
        tmp = save_upload(f); p = parse_resume(tmp); os.unlink(tmp)
        cands.append({"name": p.get("name") or os.path.splitext(f.name)[0], "email": p.get("email") or "",
                      "resume_text": p.get("raw_text", ""), "skills": p.get("skills", []), "filename": f.name})
    prog.empty()
    st.session_state["rank"] = dict(ranked=rank_candidates(cands, jd), role=extract_job_role(jd), jd=jd)

SORTS = {"Overall score": "composite_score", "Skill match": "skill_match_pct",
         "Text similarity": "cosine_similarity", "Name (A to Z)": "name"}

def render_rank(res):
    ranked, role = res["ranked"], res["role"]
    top = ranked[0]
    avg = sum(r["composite_score"] for r in ranked) / len(ranked)
    md(panel(f"Ranking for {role}" if role else "Ranking",
             f'<div class="sumline"><div><div class="sum-k">Candidates ranked</div><div class="sum-v">{len(ranked)}</div></div>'
             f'<div><div class="sum-k">Best match</div><div class="sum-v">{esc(top["name"])}<small>{top["composite_score"]:.1f}%</small></div></div>'
             f'<div><div class="sum-k">Average score</div><div class="sum-v">{avg:.1f}%</div></div></div>'))

    with st.container(key="toolbar"):
        t1, t2, t3, t4 = st.columns([2.3, 1.4, 1.7, 1.15], gap="small", vertical_alignment="center")
        with t1: q = st.text_input("Search candidates", placeholder="Search by name, email or skill", key="rk_q",
                                   label_visibility="collapsed", icon=":material/search:")
        with t2: sort = st.selectbox("Sort by", list(SORTS), key="rk_sort", label_visibility="collapsed")
        with t3: grades = st.multiselect("Filter by grade", list(GRADE_TONE), key="rk_grade",
                                         placeholder="All grades", label_visibility="collapsed")
        with t4:
            df = pd.DataFrame([{"Rank": r["rank"], "Candidate": r["name"], "Email": r["email"],
                                "Score %": r["composite_score"], "Skill match %": r["skill_match_pct"],
                                "Text similarity %": r["cosine_similarity"], "Grade": r["match_grade"],
                                "Matched skills": ", ".join(r["matched_skills"]),
                                "Missing skills": ", ".join(r["missing_skills"])} for r in ranked])
            st.download_button("Export CSV", data=df.to_csv(index=False), file_name="ranking.csv", mime="text/csv",
                               icon=":material/download:", use_container_width=True, key="dl_rank_csv")

    rows = ranked
    if q.strip():
        ql = q.strip().lower()
        rows = [r for r in rows if ql in r["name"].lower() or ql in (r["email"] or "").lower()
                or any(ql in sk for sk in r["matched_skills"] + r["missing_skills"] + r["extra_skills"])]
    if grades:
        rows = [r for r in rows if r["match_grade"] in grades]
    key = SORTS[sort]
    rows = sorted(rows, key=(lambda r: r["name"].lower()) if key == "name" else (lambda r: -r[key]))

    if not rows:
        empty_state("search", "No candidates match these filters", "Clear the search box or remove a grade filter to see everyone again.")
    for r in rows:
        tone = GRADE_TONE[r["match_grade"]]
        rank_cls = "rk-rank top" if r["rank"] == 1 else "rk-rank"
        with st.container(key=f"rk-{r['rank']}"):
            md(f'''<div class="rk"><div class="{rank_cls}">{r["rank"]}</div>{avatar(r["name"])}
              <div><div class="rk-name">{esc(r["name"])}</div><div class="rk-mail">{esc(r["email"]) if r["email"] else "No email found"}</div></div>
              <div class="rk-score t-{tone}"><div class="bar-h" style="margin-bottom:7px"><span>Overall score</span><span class="rk-pct">{r["composite_score"]:.1f}%</span></div>
                <div class="bar"><i style="--w:{r["composite_score"]}%"></i></div></div>
              <div>{chip(r["match_grade"], GRADE_CHIP[r["match_grade"]])}</div>
              <div class="rk-skills"><span class="ok">{icon("check", 16)}{len(r["matched_skills"])} matched</span><span class="bad">{icon("x", 16)}{len(r["missing_skills"])} missing</span></div></div>''')
            with st.expander("Skills and details"):
                md(f'<div class="sg"><div class="sg-h">Matched<span class="count">{len(r["matched_skills"])}</span></div>{chips(r["matched_skills"], "ok", "check", "No matching skills")}</div>'
                   f'<div class="sg"><div class="sg-h">Missing<span class="count">{len(r["missing_skills"])}</span></div>{chips(r["missing_skills"], "bad", "x", "Nothing missing")}</div>'
                   f'<div class="sg"><div class="sg-h">Skill match {r["skill_match_pct"]:.1f}% · Text similarity {r["cosine_similarity"]:.1f}%</div></div>')
                report = {k: v for k, v in r.items() if k != "resume_text"}
                st.download_button("Download candidate report", data=pretty_json(report), icon=":material/download:",
                                   file_name=f"{r['name'].replace(' ', '_')}_match.json", mime="application/json",
                                   key=f"dl_c_{r['rank']}")
    with st.expander("Compare scores"):
        st.plotly_chart(ranking_bar(ranked), use_container_width=True)

with tab2:
    hero("Rank candidates for one role.",
         "Add several resumes and one job description. Each resume is scored and the best fits come first.", small=True)
    m1, m2 = st.columns(2, gap="large")
    with m1:
        with st.container(key="card-multi"):
            card_head("users", "Candidate resumes", "Add as many PDF or DOCX files as you need")
            multi_files = st.file_uploader("Candidate resumes", type=["pdf", "docx"], accept_multiple_files=True,
                                           key="mr", label_visibility="collapsed")
    with m2:
        with st.container(key="card-jd-multi"):
            card_head("briefcase", "Job description", "Paste the text or upload a file")
            jd_multi = jd_input("multi")
    role_pill(jd_multi)
    _, mid2, _ = st.columns([1, 1.15, 1])
    with mid2:
        go_rank = st.button("Rank candidates", key="btn_rank", type="primary", icon=":material/leaderboard:", use_container_width=True)
        if go_rank:
            if not multi_files:
                notice("err", "Add at least one resume", "Upload PDF or DOCX files to rank.")
            elif not jd_multi.strip():
                notice("err", "Add a job description first", "Paste the text or upload a file to compare against.")
            else:
                run_rank(multi_files, jd_multi)
    rres = st.session_state.get("rank")
    if rres:
        render_rank(rres)
    else:
        empty_state("users", "Your ranking will appear here",
                    "Add two or more resumes and a job description, then select Rank candidates. You can search, sort and filter the results.")

# ═════════════════════════════════════════════════════════════════════════════
# NLP METRICS
# ═════════════════════════════════════════════════════════════════════════════
def run_metrics(mf, gt_input):
    with st.spinner("Running the extraction…"):
        tmp = save_upload(mf); parsed = parse_resume(tmp); os.unlink(tmp)
        raw = parsed.get("raw_text", "")
        ents = get_entities(raw)
    predicted = parsed.get("skills", [])
    gt = [s.strip().lower() for s in gt_input.split(",") if s.strip()] if gt_input.strip() else None
    metrics = skill_extraction_metrics(predicted, gt)
    pred_set = {canonicalize_skill(x) for x in predicted}
    truth_set = {canonicalize_skill(x) for x in gt} if gt else None
    st.session_state["metrics"] = dict(
        metrics=metrics, predicted=predicted, ents=ents, coverage=gt is None, n_vocab=len(SKILLS_DB),
        tp=sorted(pred_set & truth_set) if truth_set is not None else [],
        fp=sorted(pred_set - truth_set) if truth_set is not None else [],
        fn=sorted(truth_set - pred_set) if truth_set is not None else [])

def render_metrics(res):
    m = res["metrics"]
    if res["coverage"]:
        notice("warn", "Comparing against the full skill vocabulary",
               f"You didn't list the correct skills, so recall is measured against all {res['n_vocab']} skills we know. "
               "It will look low. List the skills the resume really contains for a fair score.")
    cards = [("Precision", m["precision"], "target", "ok",
              "Of the skills we found, how many are correct."),
             ("Recall", m["recall"], "search", "accent",
              "Of the skills that should be found, how many we found."),
             ("F1 score", m["f1_score"], "activity", "accent",
              "One number that balances precision and recall.")]
    cols = st.columns(3, gap="large")
    for col, (label, v, ic, tone, desc) in zip(cols, cards):
        with col:
            md(f'<div class="mc t-{tone}"><div class="mc-h"><span class="mc-ic">{icon(ic, 18)}</span>{label}</div>'
               f'<div class="mc-v">{v*100:.1f}%</div><div class="mc-d">{desc}</div>'
               f'<div class="bar"><i style="--w:{v*100}%"></i></div></div>')

    tp, fp, fn = m["true_positives"], m["false_positives"], m["false_negatives"]
    lists = res["coverage"]
    def cf(cls, n, title, desc, items, tone, ic):
        body = "" if lists else chips(items, tone, ic, "None")
        return f'<div class="cf"><div class="cf-n {cls}">{n}</div><div><div class="cf-t">{title}</div><div class="cf-d">{desc}</div>{body}</div></div>'
    md(panel("What the counts mean",
             cf("ok", tp, "Correct", "Skills we found that are on the correct list.", res["tp"], "ok", "check")
             + cf("warn", fp, "Extra", "Skills we found that are not on the correct list.", res["fp"], "warn", "minus")
             + cf("bad", fn, "Missed", "Skills on the correct list that we did not find.", res["fn"], "bad", "x"),
             "Counts of skills, not of mentions"))
    md(panel("Skills found", chips(res["predicted"], "accent", None, "No skills found"), f'{len(res["predicted"])} skills'))

    with st.expander("Extracted entities"):
        ents = res["ents"]
        if ents:
            df_ent = pd.DataFrame(ents).rename(columns={"entity": "Entity", "label": "Label", "source": "Detected by"})
            counts = df_ent["Label"].value_counts()
            md('<div class="chips" style="margin-bottom:1rem">' + "".join(chip(f"{l} · {n}", "accent") for l, n in counts.items()) + '</div>')
            st.dataframe(df_ent, use_container_width=True, hide_index=True)
            st.caption("Email, phone and dates come from regex rules. Names, organisations, locations, institutions, degrees, "
                       "job titles and URLs come from GLiNER, with spaCy and regex rules as a fallback. Skills come from the skill vocabulary.")
        else:
            md('<span class="nf">No entities found.</span>')
    with st.expander("Charts"):
        a, b = st.columns(2, gap="large")
        with a: st.plotly_chart(prf_radar(m["precision"], m["recall"], m["f1_score"]), use_container_width=True)
        with b: st.plotly_chart(confusion_bar(tp, fp, fn), use_container_width=True)
    with st.expander("How the pipeline works"):
        x, y, z = st.columns(3, gap="large")
        for col, (t, items) in zip((x, y, z), [
            ("Extraction", ["pdfplumber and python-docx read the file", "Regex finds email, phone and dates",
                            "GLiNER finds names, organisations and locations", "Rules detect sections and degrees"]),
            ("Matching", ["TF-IDF on 1 to 2 word phrases", "Cosine similarity with scikit-learn",
                          f"A vocabulary of {len(SKILLS_DB)}+ skills plus aliases", "Weighted score you can adjust"]),
            ("Evaluation", ["Precision, recall and F1", "Correct, extra and missed skills",
                            "Compared to your list or the vocabulary", "Aliases like cpp and c++ count as one skill"])]):
            with col:
                md(f'<div class="sg-h">{t}</div><div class="vl">' + "".join(f'<div>{esc(i)}</div>' for i in items) + '</div>')

with tab3:
    hero("Check how well skills are extracted.",
         "Upload a resume and, if you like, list the skills it should contain. We report precision, recall and F1.", small=True)
    e1, e2 = st.columns(2, gap="large")
    with e1:
        with st.container(key="card-eval"):
            card_head("file", "Resume to evaluate", "PDF or DOCX, up to 200 MB")
            mf = st.file_uploader("Resume to evaluate", type=["pdf", "docx"], key="mf", label_visibility="collapsed")
    with e2:
        with st.container(key="card-truth"):
            card_head("check", "Correct skills (optional)", "Separate them with commas")
            gt_input = st.text_area("Correct skills", height=214, placeholder="python, machine learning, sql, docker…",
                                    label_visibility="collapsed", key="gt")
            st.caption("Leave this empty to compare against the full skill vocabulary.")
    _, mid3, _ = st.columns([1, 1.15, 1])
    with mid3:
        go_m = st.button("Compute metrics", key="btn_metrics", type="primary", icon=":material/analytics:", use_container_width=True)
        if go_m:
            if not mf:
                notice("err", "Add a resume first", "Upload a PDF or DOCX file to evaluate.")
            else:
                run_metrics(mf, gt_input)
    mres = st.session_state.get("metrics")
    if mres:
        render_metrics(mres)
    else:
        empty_state("activity", "Your metrics will appear here",
                    "Add a resume, optionally list the skills it should contain, then select Compute metrics.")

md('<div class="foot">ResuMatch · GLiNER · spaCy · TF-IDF · Cosine similarity · No LLM · No OpenAI</div>')
