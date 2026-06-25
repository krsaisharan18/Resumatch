import plotly.graph_objects as go
import pandas as pd
import math, random

BG      = "rgba(0,0,0,0)"
SURFACE = "#161B22"
BORDER  = "#30363D"
GRID    = "#21262D"
TXT     = "#E6EDF3"
MID     = "#8B949E"
DIM     = "#484F58"
BLUE    = "#58A6FF"
GREEN   = "#3FB950"
AMBER   = "#D29922"
RED     = "#F85149"
PURPLE  = "#A371F7"

BASE = dict(paper_bgcolor=BG, plot_bgcolor=BG,
            font=dict(family="Inter,sans-serif", color=TXT, size=12),
            margin=dict(l=16,r=16,t=44,b=16))

def gauge_chart(score, title="Overall Match"):
    color = GREEN if score>=65 else AMBER if score>=40 else RED
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number=dict(suffix="%", font=dict(size=42, color=color)),
        title=dict(text=f'<span style="color:{MID};font-size:13px">{title}</span>'),
        gauge=dict(
            axis=dict(range=[0,100], tickwidth=1, tickcolor=BORDER,
                      tickfont=dict(color=MID,size=10), tickvals=[0,25,50,75,100]),
            bar=dict(color=color, thickness=0.28),
            bgcolor=SURFACE, borderwidth=1, bordercolor=BORDER,
            steps=[dict(range=[0,100], color="#0D1117")],
            threshold=dict(line=dict(color=BLUE,width=3), thickness=0.85, value=65),
        ),
    ))
    fig.update_layout(**BASE, height=260, margin=dict(l=20,r=20,t=24,b=10))
    return fig

def skill_donut(matched, missing, extra):
    if matched+missing+extra == 0: matched=missing=extra=1
    fig = go.Figure(go.Pie(
        labels=["Matched","Missing","Bonus"], values=[matched,missing,extra],
        hole=0.62,
        marker=dict(colors=[GREEN,RED,BLUE], line=dict(color="#0D1117",width=3)),
        textinfo="label+percent",
        textfont=dict(size=11, color=TXT),
        hovertemplate="<b>%{label}</b><br>%{value} skills<extra></extra>",
    ))
    fig.update_layout(**BASE, height=260,
        title=dict(text="Skill Coverage", font=dict(size=13,color=TXT), x=0),
        showlegend=True,
        legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center",
                    font=dict(color=MID,size=11), bgcolor=BG),
        annotations=[dict(text=f"<b>{matched}</b><br><span style='font-size:11px;color:{MID}'>matched</span>",
                          x=0.5, y=0.5, showarrow=False, font=dict(color=TXT,size=16))],
        margin=dict(l=10,r=10,t=44,b=30))
    return fig

def score_breakdown_bar(cosine, skill_pct, composite):
    cats   = ["TF-IDF Cosine","Skill Match","Composite Score"]
    vals   = [cosine, skill_pct, composite]
    colors = [BLUE, GREEN, AMBER]
    fig = go.Figure()
    for cat,val,col in zip(cats,vals,colors):
        fig.add_trace(go.Bar(
            x=[val], y=[cat], orientation="h",
            marker=dict(color=col, line=dict(color=BG)),
            text=[f"<b>{val:.1f}%</b>"], textposition="outside",
            textfont=dict(size=13,color=TXT), showlegend=False,
            hovertemplate=f"<b>{cat}</b>: {val:.1f}%<extra></extra>",
        ))
    fig.update_layout(**BASE, height=220,
        title=dict(text="Score Breakdown", font=dict(size=13,color=TXT), x=0),
        barmode="overlay", bargap=0.42,
        xaxis=dict(range=[0,120], showgrid=False, zeroline=False,
                   showticklabels=False, showline=False),
        yaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(color=MID,size=12)),
        margin=dict(l=10,r=70,t=44,b=10))
    return fig

def ranking_bar(ranked):
    names  = [c.get("name",f"#{i+1}") for i,c in enumerate(ranked)]
    scores = [c["composite_score"] for c in ranked]
    colors = [GREEN if s>=65 else AMBER if s>=40 else RED for s in scores]
    fig = go.Figure(go.Bar(
        x=names, y=scores,
        marker=dict(color=colors, line=dict(color=BG)),
        text=[f"<b>{s:.1f}%</b>" for s in scores],
        textposition="outside", textfont=dict(size=12,color=TXT),
        hovertemplate="<b>%{x}</b><br>Score: %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(**BASE, height=360,
        title=dict(text="Candidate Ranking", font=dict(size=13,color=TXT), x=0),
        yaxis=dict(range=[0,115], showgrid=True, gridcolor=GRID,
                   tickfont=dict(color=MID,size=11), zeroline=False, showline=False,
                   title=dict(text="Score (%)", font=dict(color=MID,size=11))),
        xaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(color=MID,size=11)), bargap=0.35)
    return fig

def prf_radar(precision, recall, f1):
    vals = [precision*100, recall*100, f1*100]
    cats = ["Precision","Recall","F1 Score"]
    fig = go.Figure(go.Scatterpolar(
        r=vals+[vals[0]], theta=cats+[cats[0]],
        fill="toself", fillcolor="rgba(88,166,255,0.15)",
        line=dict(color=BLUE,width=2.5),
        marker=dict(size=8,color=BLUE,line=dict(color="#0D1117",width=2)),
        hovertemplate="<b>%{theta}</b>: %{r:.1f}%<extra></extra>",
    ))
    fig.update_layout(**BASE, height=300,
        title=dict(text="P / R / F1 Quality", font=dict(size=13,color=TXT), x=0),
        polar=dict(bgcolor=SURFACE,
            radialaxis=dict(visible=True, range=[0,100],
                tickfont=dict(size=9,color=DIM), gridcolor=BORDER,
                linecolor=BORDER, tickvals=[25,50,75,100]),
            angularaxis=dict(tickfont=dict(size=12,color=MID), gridcolor=BORDER, linecolor=BORDER)),
        showlegend=False, margin=dict(l=30,r=30,t=50,b=20))
    return fig

def skill_bubble(matched, missing, extra):
    groups = ([(s,"Matched",GREEN,"✓") for s in matched]+
              [(s,"Missing",RED,"✗") for s in missing]+
              [(s,"Bonus",BLUE,"★") for s in extra[:15]])
    if not groups:
        fig = go.Figure()
        fig.update_layout(**BASE, height=300,
            title=dict(text="Skill Map",font=dict(size=13,color=TXT),x=0))
        return fig
    random.seed(42)
    n = len(groups)
    angles = [2*math.pi*i/n for i in range(n)]
    radii  = [random.uniform(0.35,1.0) for _ in range(n)]
    xs = [r*math.cos(a) for r,a in zip(radii,angles)]
    ys = [r*math.sin(a) for r,a in zip(radii,angles)]
    traces = {}
    for (skill,grp,col,icon),x,y in zip(groups,xs,ys):
        if grp not in traces: traces[grp] = dict(x=[],y=[],text=[],hov=[],color=col)
        traces[grp]["x"].append(x); traces[grp]["y"].append(y)
        traces[grp]["text"].append(f"{icon} {skill}")
        traces[grp]["hov"].append(f"<b>{skill}</b><br>{grp}")
    fig = go.Figure()
    for grp,d in traces.items():
        fig.add_trace(go.Scatter(
            x=d["x"],y=d["y"], mode="markers+text", name=grp,
            text=d["text"], textposition="top center",
            textfont=dict(size=10,color=TXT),
            marker=dict(size=20,color=d["color"],opacity=0.9,
                        line=dict(color="#0D1117",width=2)),
            hovertext=d["hov"], hoverinfo="text",
        ))
    fig.update_layout(**BASE, height=400,
        title=dict(text="Skill Map",font=dict(size=13,color=TXT),x=0),
        xaxis=dict(showticklabels=False,showgrid=False,zeroline=False,showline=False),
        yaxis=dict(showticklabels=False,showgrid=False,zeroline=False,showline=False),
        legend=dict(orientation="h",y=-0.05,x=0.5,xanchor="center",
                    font=dict(color=MID,size=11),bgcolor=BG),
        margin=dict(l=10,r=10,t=44,b=40))
    return fig

def tfidf_top_terms(resume_text, jd_text, top_n=14):
    import re as _re
    from sklearn.feature_extraction.text import TfidfVectorizer
    def clean(t): return _re.sub(r"[^\w\s]"," ",t.lower())
    try:
        vec = TfidfVectorizer(ngram_range=(1,2),stop_words="english",
                              max_features=3000,sublinear_tf=True)
        mat   = vec.fit_transform([clean(resume_text),clean(jd_text)])
        terms = vec.get_feature_names_out()
        r_sc  = mat[0].toarray()[0]
        j_sc  = mat[1].toarray()[0]
        idx   = list(set(r_sc.argsort()[::-1][:top_n].tolist()+j_sc.argsort()[::-1][:top_n].tolist()))
        df    = pd.DataFrame({"term":[terms[i] for i in idx],
                              "resume":[r_sc[i]*100 for i in idx],
                              "jd":[j_sc[i]*100 for i in idx]
                             }).sort_values("jd",ascending=False).head(top_n)
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Job Description",x=df["term"],y=df["jd"],
            marker=dict(color=AMBER,line=dict(color=BG)),
            hovertemplate="<b>%{x}</b><br>JD: %{y:.2f}<extra></extra>"))
        fig.add_trace(go.Bar(name="Resume",x=df["term"],y=df["resume"],
            marker=dict(color=BLUE,line=dict(color=BG)),
            hovertemplate="<b>%{x}</b><br>Resume: %{y:.2f}<extra></extra>"))
        fig.update_layout(**BASE, height=360,
            title=dict(text=f"Top {top_n} TF-IDF Terms",font=dict(size=13,color=TXT),x=0),
            barmode="group", bargap=0.25, bargroupgap=0.06,
            xaxis=dict(tickangle=-35,showgrid=False,zeroline=False,showline=False,
                       tickfont=dict(color=MID,size=10)),
            yaxis=dict(title=dict(text="TF-IDF ×100",font=dict(color=MID,size=11)),
                       showgrid=True,gridcolor=GRID,zeroline=False,showline=False,
                       tickfont=dict(color=MID,size=10)),
            legend=dict(orientation="h",y=1.12,x=1,xanchor="right",
                        font=dict(color=MID,size=11),bgcolor=BG))
        return fig
    except:
        fig = go.Figure()
        fig.update_layout(**BASE, height=300,
            title=dict(text="TF-IDF Terms",font=dict(size=13,color=TXT),x=0))
        return fig
