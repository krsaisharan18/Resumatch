import plotly.graph_objects as go
import pandas as pd
import math, random

# Light palette shared with the app's CSS tokens (see app.py).
BG      = "rgba(0,0,0,0)"
INK     = "#141A3C"
MID     = "#4A5175"
DIM     = "#636B8F"
GRID    = "#E9E6DE"
LINE    = "#E6E3DA"
ACCENT  = "#3B3FD8"
OK      = "#1F9D63"
BAD     = "#D9534F"
WARN    = "#D89A1E"
SOFT    = "#AEB3D6"
# legacy names kept so older imports keep working
SURFACE, BORDER, TXT = "#FFFFFF", LINE, INK
BLUE, GREEN, AMBER, RED, PURPLE = ACCENT, OK, WARN, BAD, ACCENT

FONT = "Onest, Segoe UI, Helvetica, Arial, sans-serif"
DISPLAY = "Schibsted Grotesk, Onest, Segoe UI, sans-serif"

BASE = dict(paper_bgcolor=BG, plot_bgcolor=BG, font=dict(family=FONT, color=INK, size=13))

_LIGHT = dict(INK="#141A3C", MID="#4A5175", DIM="#636B8F", GRID="#E9E6DE", LINE="#E6E3DA", ACCENT="#3B3FD8",
              OK="#1F9D63", BAD="#D9534F", WARN="#D89A1E", SOFT="#AEB3D6", PANEL="#F1F0EA", RING="#FFFFFF")
_DARK = dict(INK="#ECEEFB", MID="#B3B9D9", DIM="#8C93B8", GRID="#2A3050", LINE="#2A3050", ACCENT="#8B8EF5",
             OK="#4CC38A", BAD="#F0766B", WARN="#E5B25D", SOFT="#5A6290", PANEL="#232842", RING="#171B2E")
PANEL, RING = _LIGHT["PANEL"], _LIGHT["RING"]


def set_theme(dark=False):
    """Switch the chart palette between light and dark (call before building figures)."""
    global INK, MID, DIM, GRID, LINE, ACCENT, OK, BAD, WARN, SOFT, PANEL, RING, BASE, SURFACE, BORDER, TXT
    t = _DARK if dark else _LIGHT
    INK, MID, DIM, GRID, LINE, ACCENT = t["INK"], t["MID"], t["DIM"], t["GRID"], t["LINE"], t["ACCENT"]
    OK, BAD, WARN, SOFT, PANEL, RING = t["OK"], t["BAD"], t["WARN"], t["SOFT"], t["PANEL"], t["RING"]
    SURFACE, BORDER, TXT = RING, LINE, INK
    BASE = dict(paper_bgcolor=BG, plot_bgcolor=BG, font=dict(family=FONT, color=INK, size=13))


def _score_color(score):
    return OK if score >= 65 else ACCENT if score >= 50 else WARN if score >= 35 else BAD

def _title(text):
    return dict(text=text, font=dict(size=16, color=INK, family=DISPLAY), x=0, xanchor="left")

def gauge_chart(score, title="Overall match"):
    color = _score_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number=dict(suffix="%", font=dict(size=42, color=color, family=DISPLAY)),
        title=dict(text=f'<span style="color:{MID};font-size:13px">{title}</span>'),
        gauge=dict(axis=dict(range=[0, 100], tickcolor=LINE, tickfont=dict(color=DIM, size=10),
                             tickvals=[0, 25, 50, 75, 100]),
                   bar=dict(color=color, thickness=0.28), bgcolor=PANEL, borderwidth=0,
                   threshold=dict(line=dict(color=INK, width=2), thickness=0.85, value=65))))
    fig.update_layout(**BASE, height=260, margin=dict(l=20, r=20, t=24, b=10))
    return fig

def skill_donut(matched, missing, extra):
    if matched + missing + extra == 0: matched = missing = extra = 1
    fig = go.Figure(go.Pie(
        labels=["Matched", "Missing", "Bonus"], values=[matched, missing, extra],
        hole=0.66, sort=False, direction="clockwise",
        marker=dict(colors=[OK, BAD, SOFT], line=dict(color=RING, width=3)),
        textinfo="percent", textfont=dict(size=12, color="#FFFFFF", family=FONT),
        hovertemplate="<b>%{label}</b><br>%{value} skills<extra></extra>"))
    fig.update_layout(**BASE, height=300, title=_title("Skill coverage"), showlegend=True,
        legend=dict(orientation="h", y=-0.04, x=0.5, xanchor="center", font=dict(color=MID, size=12), bgcolor=BG),
        annotations=[dict(text=f"<b>{matched}</b><br><span style='font-size:12px;color:{DIM}'>matched</span>",
                          x=0.5, y=0.5, showarrow=False, font=dict(color=INK, size=24, family=DISPLAY))],
        margin=dict(l=10, r=10, t=52, b=40))
    return fig

def score_breakdown_bar(cosine, skill_pct, composite):
    cats, vals, colors = ["Overall", "Skill match", "Text similarity"], [composite, skill_pct, cosine], [ACCENT, OK, SOFT]
    fig = go.Figure()
    for cat, val, col in zip(cats, vals, colors):
        fig.add_trace(go.Bar(x=[val], y=[cat], orientation="h", marker=dict(color=col), showlegend=False,
            text=[f"<b>{val:.1f}%</b>"], textposition="outside", textfont=dict(size=13, color=INK, family=DISPLAY),
            hovertemplate=f"<b>{cat}</b>: {val:.1f}%<extra></extra>"))
    fig.update_layout(**BASE, height=280, title=_title("How the score adds up"), barmode="overlay", bargap=0.46,
        xaxis=dict(range=[0, 125], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color=MID, size=13)),
        margin=dict(l=10, r=60, t=52, b=20))
    return fig

def ranking_bar(ranked):
    names = [c.get("name", f"#{i+1}") for i, c in enumerate(ranked)]
    scores = [c["composite_score"] for c in ranked]
    fig = go.Figure(go.Bar(x=names, y=scores, marker=dict(color=[_score_color(s) for s in scores], cornerradius=6),
        text=[f"<b>{s:.1f}%</b>" for s in scores], textposition="outside",
        textfont=dict(size=13, color=INK, family=DISPLAY),
        hovertemplate="<b>%{x}</b><br>Score: %{y:.1f}%<extra></extra>"))
    fig.update_layout(**BASE, height=340, title=_title("Candidate scores"), bargap=0.45,
        yaxis=dict(range=[0, 115], showgrid=True, gridcolor=GRID, tickfont=dict(color=DIM, size=12), zeroline=False),
        xaxis=dict(showgrid=False, tickfont=dict(color=MID, size=12)), margin=dict(l=10, r=10, t=52, b=20))
    return fig

def prf_radar(precision, recall, f1):
    vals, cats = [precision * 100, recall * 100, f1 * 100], ["Precision", "Recall", "F1 score"]
    fig = go.Figure(go.Scatterpolar(r=vals + [vals[0]], theta=cats + [cats[0]], fill="toself",
        fillcolor="rgba(110,114,240,0.18)", line=dict(color=ACCENT, width=2.5),
        marker=dict(size=8, color=ACCENT), hovertemplate="<b>%{theta}</b>: %{r:.1f}%<extra></extra>"))
    fig.update_layout(**BASE, height=320, title=_title("Precision, recall and F1"), showlegend=False,
        polar=dict(bgcolor=BG,
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10, color=DIM), gridcolor=GRID,
                            linecolor=GRID, tickvals=[25, 50, 75, 100]),
            angularaxis=dict(tickfont=dict(size=13, color=MID), gridcolor=GRID, linecolor=GRID)),
        margin=dict(l=40, r=40, t=56, b=24))
    return fig

def confusion_bar(tp, fp, fn):
    fig = go.Figure(go.Bar(x=["Correct", "Extra", "Missed"], y=[tp, fp, fn],
        marker=dict(color=[OK, WARN, BAD], cornerradius=6), text=[tp, fp, fn], textposition="outside",
        textfont=dict(color=INK, size=15, family=DISPLAY), hovertemplate="<b>%{x}</b>: %{y}<extra></extra>"))
    fig.update_layout(**BASE, height=260, showlegend=False, title=_title("Confusion summary"), bargap=0.5,
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        xaxis=dict(showgrid=False, tickfont=dict(color=MID, size=13)), margin=dict(l=10, r=10, t=52, b=10))
    return fig

def skill_bubble(matched, missing, extra):
    groups = ([(s, "Matched", OK, "✓") for s in matched] + [(s, "Missing", BAD, "✗") for s in missing] +
              [(s, "Bonus", SOFT, "★") for s in extra[:15]])
    if not groups:
        fig = go.Figure(); fig.update_layout(**BASE, height=300, title=_title("Skill map")); return fig
    random.seed(42)
    n = len(groups)
    angles = [2 * math.pi * i / n for i in range(n)]
    radii = [random.uniform(0.35, 1.0) for _ in range(n)]
    xs = [r * math.cos(a) for r, a in zip(radii, angles)]
    ys = [r * math.sin(a) for r, a in zip(radii, angles)]
    traces = {}
    for (skill, grp, col, icon), x, y in zip(groups, xs, ys):
        t = traces.setdefault(grp, dict(x=[], y=[], text=[], hov=[], color=col))
        t["x"].append(x); t["y"].append(y); t["text"].append(f"{icon} {skill}"); t["hov"].append(f"<b>{skill}</b><br>{grp}")
    fig = go.Figure()
    for grp, d in traces.items():
        fig.add_trace(go.Scatter(x=d["x"], y=d["y"], mode="markers+text", name=grp, text=d["text"],
            textposition="top center", textfont=dict(size=11, color=INK),
            marker=dict(size=16, color=d["color"], line=dict(color=RING, width=2)),
            hovertext=d["hov"], hoverinfo="text"))
    fig.update_layout(**BASE, height=420, title=_title("Skill map"),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        legend=dict(orientation="h", y=-0.04, x=0.5, xanchor="center", font=dict(color=MID, size=12), bgcolor=BG),
        margin=dict(l=10, r=10, t=52, b=44))
    return fig

def tfidf_top_terms(resume_text, jd_text, top_n=14):
    import re as _re
    from sklearn.feature_extraction.text import TfidfVectorizer
    def clean(t): return _re.sub(r"[^\w\s]", " ", t.lower())
    try:
        vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english", max_features=3000, sublinear_tf=True)
        mat = vec.fit_transform([clean(resume_text), clean(jd_text)])
        terms = vec.get_feature_names_out()
        r_sc, j_sc = mat[0].toarray()[0], mat[1].toarray()[0]
        idx = list(set(r_sc.argsort()[::-1][:top_n].tolist() + j_sc.argsort()[::-1][:top_n].tolist()))
        df = pd.DataFrame({"term": [terms[i] for i in idx], "resume": [r_sc[i] * 100 for i in idx],
                           "jd": [j_sc[i] * 100 for i in idx]}).sort_values("jd", ascending=False).head(top_n)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Job description", x=df["term"], y=df["jd"], marker=dict(color=SOFT, cornerradius=4),
            hovertemplate="<b>%{x}</b><br>JD: %{y:.2f}<extra></extra>"))
        fig.add_trace(go.Bar(name="Resume", x=df["term"], y=df["resume"], marker=dict(color=ACCENT, cornerradius=4),
            hovertemplate="<b>%{x}</b><br>Resume: %{y:.2f}<extra></extra>"))
        fig.update_layout(**BASE, height=380, title=_title(f"Top {top_n} TF-IDF terms"), barmode="group",
            bargap=0.25, bargroupgap=0.06,
            xaxis=dict(tickangle=-35, showgrid=False, zeroline=False, tickfont=dict(color=MID, size=11)),
            yaxis=dict(title=dict(text="TF-IDF ×100", font=dict(color=MID, size=12)), showgrid=True,
                       gridcolor=GRID, zeroline=False, tickfont=dict(color=DIM, size=11)),
            legend=dict(orientation="h", y=1.12, x=1, xanchor="right", font=dict(color=MID, size=12), bgcolor=BG),
            margin=dict(l=10, r=10, t=60, b=10))
        return fig
    except Exception:
        fig = go.Figure(); fig.update_layout(**BASE, height=300, title=_title("TF-IDF terms")); return fig
