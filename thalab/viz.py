from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from thalab.styles import current_theme_type

BLOOD="#B11226"; DANGER="#C91832"; GOLD="#F7B801"; TEAL="#0E8F68"; BLUE="#11A8CD"; VIOLET="#6D40D8"; INK="#24131A"

def _layout(fig: go.Figure, title: str | None = None, height: int = 420) -> go.Figure:
    dark = current_theme_type() == "dark"
    text = "#F5FAFC" if dark else "#17212B"
    grid = "rgba(255,255,255,.12)" if dark else "rgba(36,48,63,.12)"
    plot_bg = "rgba(255,255,255,.04)" if dark else "rgba(255,255,255,.22)"
    fig.update_layout(
        template="plotly_dark" if dark else "plotly_white",
        height=height,
        title={"text": title or "", "x":0.02, "xanchor":"left", "font":{"size":20,"color":text}},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=plot_bg,
        margin=dict(l=42,r=28,t=64 if title else 30,b=42),
        font=dict(family="Inter, Arial", color=text),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(
            bgcolor="rgba(16,24,32,.92)" if dark else "rgba(255,255,255,.92)",
            bordercolor="rgba(255,255,255,.18)" if dark else "rgba(36,48,63,.16)",
            font=dict(color=text),
        ),
    )
    fig.update_xaxes(gridcolor=grid, zerolinecolor=grid)
    fig.update_yaxes(gridcolor=grid, zerolinecolor=grid)
    if "polar" in fig.layout:
        fig.update_layout(polar=dict(bgcolor=plot_bg))
    return fig

def risk_gauge(score: float, title: str = "Consult score") -> go.Figure:
    dark = current_theme_type() == "dark"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=float(score),
            number={"suffix":" / 100", "font":{"size":42}},
            delta={"reference":45, "increasing":{"color":DANGER}, "decreasing":{"color":TEAL}},
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":BLOOD},
                "bgcolor":"#241018" if dark else "white",
                "borderwidth":1,
                "bordercolor":"rgba(255,244,246,.16)" if dark else "rgba(177,18,38,.18)",
                "steps":[
                    {"range":[0,45],"color":"#174C3D" if dark else "#DFF7EF"},
                    {"range":[45,75],"color":"#55410E" if dark else "#FFF0C6"},
                    {"range":[75,100],"color":"#5A1A27" if dark else "#FFDDE4"},
                ],
                "threshold":{"line":{"color":DANGER,"width":5},"thickness":.78,"value":75},
            },
        )
    )
    return _layout(fig, title, 360)

def score_radar(scores: dict[str, float]) -> go.Figure:
    labels=list(scores.keys()); values=[float(scores[k]) for k in labels]
    fig=go.Figure(go.Scatterpolar(r=values+[values[0]], theta=labels+[labels[0]], fill="toself", name="Phenotype score", line=dict(width=4, color=BLOOD)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100], gridcolor="rgba(177,18,38,.15)")), showlegend=False)
    return _layout(fig, "Phenotype score radar", 430)

def hb_fraction_donut(hba: float, hba2: float, hbf: float, hbe: float) -> go.Figure:
    values=[max(0,float(x or 0)) for x in [hba,hba2,hbf,hbe]]; labels=["HbA","HbA2","HbF","HbE/variant"]
    other=max(0,100-sum(values))
    if other>.3: values.append(other); labels.append("Other/unassigned")
    fig=go.Figure(go.Pie(labels=labels, values=values, hole=.62, sort=False, textinfo="label+percent")); fig.update_traces(marker=dict(line=dict(color="white", width=2)))
    return _layout(fig, "Hemoglobin fraction composition", 390)

def hplc_chromatogram(hba: float, hba2: float, hbf: float, hbe: float) -> go.Figure:
    x=np.linspace(.5,6.5,900); peaks=[("HbF",1.15,.09,max(.3,hbf or 0),BLUE),("HbA",2.72,.13,max(.3,hba or 0),BLOOD),("HbA2",3.72,.085,max(.3,hba2 or 0),GOLD),("HbE/variant",4.05,.095,max(.2,hbe or 0),VIOLET)]
    fig=go.Figure(); total=np.zeros_like(x)
    for name,mu,sig,area,color in peaks:
        y=area*np.exp(-.5*((x-mu)/sig)**2); total+=y
        fig.add_trace(go.Scatter(x=x,y=y,mode="lines",fill="tozeroy",name=name,line=dict(width=2.5,color=color),opacity=.78))
    fig.add_trace(go.Scatter(x=x,y=total,mode="lines",name="Composite signal",line=dict(width=3.5,color=INK)))
    fig.update_xaxes(title="Retention time / analytical window", showgrid=False); fig.update_yaxes(title="Relative absorbance", showticklabels=False)
    return _layout(fig, "HPLC-like hemoglobin chromatogram simulator", 430)

def thalassemia_spectrum_chart() -> go.Figure:
    dark = current_theme_type() == "dark"
    band_label = "rgba(245,250,252,.86)" if dark else "rgba(23,33,43,.78)"
    critical_color = "#F5FAFC" if dark else "#24131A"
    band_fill = {
        "Minimal": "#0E8F68",
        "Carrier": "#D99A1E",
        "Moderate": "#E8890C",
        "High": "#C91832",
        "Critical": critical_color,
    }
    colors = {
        "Normal (minimal/none)": "#0E8F68",
        "Carrier / low risk": "#D99A1E",
        "Moderate risk": "#E8890C",
        "High risk": "#C91832",
        "Critical risk": critical_color,
    }
    df = pd.DataFrame(
        [
            ("Normal genotype", "Balanced", "Normal (minimal/none)", 0.45, 0.9, 20, "Reference CBC and Hb fractions", "top center"),
            ("Silent α carrier", "α-globin", "Carrier / low risk", 1.05, 1.35, 24, "Often subtle or borderline microcytosis", "bottom center"),
            ("α-thal carrier", "α-globin", "Carrier / low risk", 1.35, 2.05, 27, "Microcytosis with normal or low-normal HbA2", "top left"),
            ("β-thal trait", "β-globin", "Carrier / low risk", 1.58, 3.35, 30, "Low MCV/MCH with elevated HbA2", "top center"),
            ("HbE trait", "β-globin variant", "Carrier / low risk", 1.45, 2.72, 28, "HbE/A2 fraction with positive DCIP pattern", "bottom right"),
            ("Trait phenotype", "α or β-globin", "Moderate risk", 2.12, 2.35, 30, "Carrier pattern that needs partner-context interpretation", "bottom center"),
            ("Homozygous HbE", "β-globin variant", "Moderate risk", 2.48, 3.08, 34, "High HbE fraction; usually moderate clinical burden", "top right"),
            ("HbH disease", "α-globin", "High risk", 3.28, 3.78, 38, "HbH inclusion and chronic hemolytic phenotype", "bottom left"),
            ("β-thal intermedia", "β-globin", "High risk", 3.82, 3.22, 38, "Raised HbF and anemia with variable transfusion need", "bottom right"),
            ("HbH-Constant Spring", "α-globin", "High risk", 3.76, 4.36, 42, "Nondeletional α variant with more severe HbH phenotype", "top center"),
            ("Homozygous β-thal", "β-globin", "Critical risk", 4.55, 3.78, 44, "Severe β-globin production failure", "bottom center"),
            ("HbE/β0-thal", "β-globin variant", "Critical risk", 4.72, 4.43, 46, "Compound HbE and β0-thalassemia genotype", "top left"),
            ("Hb Bart's hydrops", "α-globin", "Critical risk", 4.95, 4.95, 48, "Absent α-globin production; fetal hydrops risk", "top center"),
        ],
        columns=["label", "system", "risk", "severity", "signal", "bubble", "cue", "textposition"],
    )

    fig = go.Figure()
    bands = [
        (0.0, 1.0, "Minimal", "Minimal / none"),
        (1.0, 2.0, "Carrier", "Carrier"),
        (2.0, 3.0, "Moderate", "Moderate"),
        (3.0, 4.2, "High", "High"),
        (4.2, 5.25, "Critical", "Critical"),
    ]
    for x0, x1, key, label in bands:
        fig.add_vrect(x0=x0, x1=x1, fillcolor=band_fill[key], opacity=0.12, line_width=0, layer="below")
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=5.22,
            text=label,
            showarrow=False,
            font=dict(size=12, color=band_label),
            yanchor="top",
        )

    alpha = df[df["system"].str.contains("α", regex=False)]
    beta = df[df["system"].str.contains("β", regex=False)]
    fig.add_trace(
        go.Scatter(
            x=alpha["severity"],
            y=alpha["signal"],
            mode="lines",
            line=dict(width=5, color="rgba(14,143,104,.38)", shape="spline"),
            name="α-globin pathway",
            hoverinfo="skip",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=beta["severity"],
            y=beta["signal"],
            mode="lines",
            line=dict(width=5, color="rgba(109,64,216,.36)", shape="spline"),
            name="β/HbE pathway",
            hoverinfo="skip",
        )
    )

    for risk, group in df.groupby("risk", sort=False):
        fig.add_trace(
            go.Scatter(
                x=group["severity"],
                y=group["signal"],
                mode="markers+text",
                text=group["label"],
                textposition=group["textposition"].tolist(),
                customdata=group[["system", "cue", "risk"]].to_numpy(),
                marker=dict(
                    size=group["bubble"].tolist(),
                    color=colors[risk],
                    opacity=0.9,
                    line=dict(width=2.5, color="rgba(255,255,255,.92)"),
                ),
                name=risk,
                hovertemplate="<b>%{text}</b><br>System: %{customdata[0]}<br>Primary cue: %{customdata[1]}<br>Band: %{customdata[2]}<extra></extra>",
            )
        )

    fig.add_annotation(
        x=3.7,
        y=1.05,
        text="Confirmatory testing turns a screening signal into a reproductive-risk answer.",
        showarrow=False,
        align="left",
        font=dict(size=13, color=band_label),
        bgcolor="rgba(255,255,255,.08)" if dark else "rgba(255,255,255,.52)",
        bordercolor="rgba(255,255,255,.20)" if dark else "rgba(23,33,43,.10)",
        borderpad=8,
    )
    fig.update_xaxes(
        title="Qualitative clinical severity and reproductive urgency",
        range=[0, 5.25],
        tickvals=[0.5, 1.5, 2.5, 3.55, 4.7],
        ticktext=["Minimal", "Carrier", "Moderate", "High", "Critical"],
        showgrid=False,
    )
    fig.update_yaxes(
        title="Typical laboratory signal strength",
        range=[0.55, 5.35],
        tickvals=[1, 2, 3, 4, 5],
        ticktext=["Subtle", "Microcytosis", "Hb fraction cue", "Hemolysis / inclusion", "Fetal risk"],
    )
    fig.update_layout(hovermode="closest", legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1))
    return _layout(fig, "Thalassemia phenotype spectrum map", 560)

def mcv_hba2_quadrant(mcv: float, hba2: float, background: pd.DataFrame | None = None) -> go.Figure:
    if background is None:
        rng=np.random.default_rng(42); background=pd.DataFrame({"mcv_fl":np.concatenate([rng.normal(88,5,80),rng.normal(68,5,65),rng.normal(72,6,55)]),"hba2_percent":np.concatenate([rng.normal(2.6,.25,80),rng.normal(4.8,.55,65),rng.normal(2.5,.35,55)]),"pattern":["reference-like"]*80+["β-thal trait-like"]*65+["α/iron-like microcytosis"]*55})
    fig=px.scatter(background,x="mcv_fl",y="hba2_percent",color="pattern",opacity=.62,labels={"mcv_fl":"MCV (fL)","hba2_percent":"HbA2 (%)"})
    fig.add_vline(x=80,line_width=2,line_dash="dash",line_color="rgba(36,19,26,.55)"); fig.add_hline(y=3.5,line_width=2,line_dash="dash",line_color="rgba(36,19,26,.55)")
    fig.add_trace(go.Scatter(x=[mcv],y=[hba2],mode="markers+text",text=["Patient"],textposition="top center",marker=dict(size=18,color=DANGER,line=dict(color="white",width=3)),name="Current sample"))
    fig.add_annotation(x=67,y=5.4,text="β-thal trait-like zone",showarrow=False,font=dict(color=BLOOD,size=13)); fig.add_annotation(x=67,y=2.2,text="α-thal / iron-like microcytosis",showarrow=False,font=dict(color=TEAL,size=13))
    return _layout(fig, "MCV–HbA2 diagnostic quadrant", 470)

def cbc_reference_bars(row: dict) -> go.Figure:
    metrics=[("Hb",row.get("hb_g_dl",np.nan),12,16,"g/dL"),("RBC",row.get("rbc_10e12_l",np.nan),4,5.5,"10¹²/L"),("MCV",row.get("mcv_fl",np.nan),80,100,"fL"),("MCH",row.get("mch_pg",np.nan),27,33,"pg"),("RDW",row.get("rdw_percent",np.nan),11.5,14.5,"%"),("Ferritin",row.get("ferritin_ng_ml",np.nan),30,300,"ng/mL")]
    fig=go.Figure()
    for i,(name,value,low,high,unit) in enumerate(metrics):
        if value is None or np.isnan(float(value)): continue
        axis_max=max(high*1.35,float(value)*1.15,1); fig.add_trace(go.Bar(y=[name],x=[axis_max],orientation="h",marker_color="rgba(177,18,38,.08)",hoverinfo="skip",showlegend=False)); fig.add_trace(go.Bar(y=[name],x=[high-low],base=[low],orientation="h",marker_color="rgba(14,143,104,.35)",name="Reference interval" if i==0 else None,showlegend=i==0)); fig.add_trace(go.Scatter(y=[name],x=[value],mode="markers+text",text=[f"{value:g} {unit}"],textposition="middle right",marker=dict(size=15,color=BLOOD,line=dict(color="white",width=2)),name="Observed" if i==0 else None,showlegend=i==0))
    fig.update_layout(barmode="overlay"); fig.update_xaxes(title="Observed value against reference interval")
    return _layout(fig,"CBC and iron profile against reference bands",430)

def diagnostic_waterfall(result) -> go.Figure:
    # แก้ไขลดจำนวนข้อมูลลง ไม่ให้ดึงค่า consult_score มาแสดงยอดรวมขวาสุด
    measures=["relative"]*5
    labels=["Microcytosis","Hypochromia","HbA2/HbE","RBC pattern","Iron modifier"]
    vals=[15 if result.microcytosis else 0,10 if result.hypochromia else 0,max(0,min(40,result.beta_trait_score*.45+result.hbe_score*.35)),10 if result.derived.get("mentzer_index",99)<13 else 0,-12 if result.iron_deficiency_score>=45 and result.beta_trait_score>=30 else 0]
    fig=go.Figure(go.Waterfall(name="score",orientation="v",measure=measures,x=labels,y=vals,connector={"line":{"color":"rgba(36,19,26,.25)"}},increasing={"marker":{"color":BLOOD}},decreasing={"marker":{"color":TEAL}},totals={"marker":{"color":GOLD}})); fig.update_yaxes(title="Score contribution")
    return _layout(fig,"Rule-evidence contribution waterfall",410)

def reflex_sankey(result) -> go.Figure:
    labels=["CBC + smear","Microcytosis","Hb analysis","Iron studies","HBB testing","HBA testing","HbE confirmation","Partner testing","Report consult"]; idx={x:i for i,x in enumerate(labels)}; sources=[idx["CBC + smear"]]; targets=[idx["Microcytosis"] if result.microcytosis else idx["Report consult"]]; values=[1]
    if result.microcytosis:
        for target in ["Hb analysis","Iron studies"]: sources.append(idx["Microcytosis"]); targets.append(idx[target]); values.append(.8)
    if result.beta_trait_score>=45: sources.append(idx["Hb analysis"]); targets.append(idx["HBB testing"]); values.append(result.beta_trait_score/100)
    if result.alpha_trait_score>=45: sources.append(idx["Hb analysis"]); targets.append(idx["HBA testing"]); values.append(result.alpha_trait_score/100)
    if result.hbe_score>=45: sources.append(idx["Hb analysis"]); targets.append(idx["HbE confirmation"]); values.append(result.hbe_score/100)
    for source in ["HBB testing","HBA testing","HbE confirmation"]:
        if source in [labels[t] for t in targets]: sources.append(idx[source]); targets.append(idx["Partner testing"]); values.append(.5)
    for source in ["Iron studies","Partner testing","Hb analysis"]: sources.append(idx[source]); targets.append(idx["Report consult"]); values.append(.35)
    fig=go.Figure(go.Sankey(arrangement="snap",node=dict(label=labels,pad=18,thickness=18,line=dict(color="rgba(63,2,8,.25)",width=1),color=[BLOOD,GOLD,VIOLET,TEAL,DANGER,BLUE,"#9B5DE5","#F15BB5",INK]),link=dict(source=sources,target=targets,value=values,color="rgba(177,18,38,.22)")))
    return _layout(fig,"Reflex testing workflow map",430)

def batch_risk_distribution(df: pd.DataFrame) -> go.Figure:
    order=["Critical review","High","Moderate","Low / inconclusive"]; counts=df["consult_risk"].value_counts().reindex(order).fillna(0).reset_index(); counts.columns=["risk","count"]
    fig=px.bar(counts,x="risk",y="count",text="count",labels={"risk":"Consult risk","count":"Number of samples"}); fig.update_traces(marker_line_color="white",marker_line_width=2,textposition="outside")
    return _layout(fig,"Batch consult risk distribution",420)

def batch_mcv_hba2_scatter(df: pd.DataFrame) -> go.Figure:
    # ลบ size="consult_score" ออก เพื่อไม่ให้ขนาดจุดแปรผันตามคะแนน
    fig=px.scatter(df,x="mcv_fl",y="hba2_percent",color="top_pattern",hover_name="sample_id",hover_data=["consult_risk","ferritin_ng_ml","mentzer_index"],labels={"mcv_fl":"MCV (fL)","hba2_percent":"HbA2 (%)"})
    fig.add_vline(x=80,line_dash="dash",line_color="rgba(36,19,26,.5)"); fig.add_hline(y=3.5,line_dash="dash",line_color="rgba(36,19,26,.5)")
    return _layout(fig,"Batch MCV–HbA2 phenotype map",500)

def score_heatmap(df: pd.DataFrame) -> go.Figure:
    cols=["beta_trait_score","alpha_trait_score","hbe_score","iron_deficiency_score"]; z=df[cols].fillna(0).to_numpy().T
    fig=go.Figure(go.Heatmap(z=z,x=df["sample_id"].astype(str),y=["β-thal","α-thal","HbE","Iron"],colorscale="Reds",colorbar=dict(title="score"))); fig.update_xaxes(tickangle=45)
    return _layout(fig,"Per-sample phenotype score heatmap",470)

def population_sankey(df: pd.DataFrame) -> go.Figure:
    risk_order=list(df["consult_risk"].dropna().unique()); pattern_order=list(df["top_pattern"].dropna().unique()); labels=["All samples"]+risk_order+pattern_order+["Molecular reflex","Routine review"]; idx={x:i for i,x in enumerate(labels)}; sources=[]; targets=[]; values=[]
    for risk in risk_order: sources.append(idx["All samples"]); targets.append(idx[risk]); values.append(int((df["consult_risk"]==risk).sum()))
    for risk in risk_order:
        sub=df[df["consult_risk"]==risk]
        for pat,n in sub["top_pattern"].value_counts().items(): sources.append(idx[risk]); targets.append(idx[pat]); values.append(int(n))
    for pat in pattern_order:
        sub=df[df["top_pattern"]==pat]; n_reflex=int((sub["consult_score"]>=45).sum()); n_review=max(0,len(sub)-n_reflex)
        if n_reflex: sources.append(idx[pat]); targets.append(idx["Molecular reflex"]); values.append(n_reflex)
        if n_review: sources.append(idx[pat]); targets.append(idx["Routine review"]); values.append(n_review)
    fig=go.Figure(go.Sankey(node=dict(label=labels,pad=18,thickness=17),link=dict(source=sources,target=targets,value=values,color="rgba(177,18,38,.22)")))
    return _layout(fig,"Population reflex-flow Sankey",480)

def allele_sunburst(db: pd.DataFrame) -> go.Figure:
    fig=px.sunburst(db,path=["system","variant_class","common_name"],values="clinical_weight",color="system",hover_data=["gene","method","expected_bp"])
    return _layout(fig,"Allele knowledge-base sunburst",520)

def allele_method_bar(db: pd.DataFrame) -> go.Figure:
    counts=db.groupby(["method","system"],as_index=False).size(); fig=px.bar(counts,x="method",y="size",color="system",barmode="group",labels={"size":"Number of targets","method":"Molecular method"}); fig.update_xaxes(tickangle=25)
    return _layout(fig,"PCR panel composition by method",430)

def virtual_gel(matched: pd.DataFrame) -> go.Figure:
    lanes=list(matched["lane"].astype(str)) if "lane" in matched.columns else [f"L{i+1}" for i in range(len(matched))]; height,lane_width=560,28; gel=np.zeros((height,len(lanes)*lane_width+20))+.08; rng=np.random.default_rng(11); gel+=rng.normal(0,.008,gel.shape); max_bp=max(2500,float(pd.to_numeric(matched.get("expected_bp",pd.Series([2500])),errors="coerce").max())+200); min_bp=100
    for i,(_,r) in enumerate(matched.iterrows()):
        observed=pd.to_numeric(pd.Series([r.get("observed_bp",np.nan)]),errors="coerce").iloc[0]; expected=pd.to_numeric(pd.Series([r.get("expected_bp",np.nan)]),errors="coerce").iloc[0]; bp=observed if not np.isnan(observed) else expected
        if np.isnan(bp): continue
        detected=bool(r.get("detected",False)); y=int((np.log(max_bp)-np.log(bp))/(np.log(max_bp)-np.log(min_bp))*(height-60)+30); x0=10+i*lane_width+6; x1=x0+lane_width-12; intensity=.95 if detected else .25
        for dy in range(-3,4):
            if 0<=y+dy<height: gel[y+dy,x0:x1]+=intensity*np.exp(-(dy**2)/6)
        gel[40:44,x0:x1]+=.38
    gel=np.clip(gel,0,1); fig=go.Figure(go.Heatmap(z=gel,colorscale=[[0,"#17040A"],[.25,"#4B0611"],[.55,"#B11226"],[1,"#FFE8A3"]],showscale=False)); tickvals=[10+i*lane_width+lane_width/2 for i in range(len(lanes))]
    fig.update_xaxes(tickmode="array",tickvals=tickvals,ticktext=lanes,title="PCR lane",showgrid=False,zeroline=False); fig.update_yaxes(showticklabels=False,showgrid=False,zeroline=False,autorange="reversed")
    return _layout(fig,"Virtual PCR gel viewer",560)

def pcr_confidence_lollipop(matched: pd.DataFrame) -> go.Figure:
    m=matched.copy(); m["label"]=m["sample_id"].astype(str)+" • "+m["target_code"].astype(str); m=m.sort_values("confidence"); fig=go.Figure(); fig.add_trace(go.Scatter(x=m["confidence"]*100,y=m["label"],mode="markers",marker=dict(size=15,color=np.where(m["detected"],DANGER,TEAL),line=dict(width=2,color="white")),name="Confidence"))
    for _,r in m.iterrows(): fig.add_shape(type="line",x0=0,x1=float(r["confidence"])*100,y0=r["label"],y1=r["label"],line=dict(color="rgba(177,18,38,.22)",width=4))
    fig.update_xaxes(range=[0,100],title="Match confidence (%)")
    return _layout(fig,"PCR allele-call confidence lollipop",max(380,70+len(m)*34))

def punnett_heatmap(punnett_df: pd.DataFrame, parent1: list[str], parent2: list[str], system: str) -> go.Figure:
    from thalab.genetics import classify_alpha, classify_beta
    cell_text=[]; z=[]; sevmap={"minimal":0,"low":1,"moderate":2,"high":3,"critical":4}
    for g1 in parent1:
        row_text=[]; row_z=[]
        for g2 in parent2:
            if system=="alpha": ph,sev,_=classify_alpha(g1,g2)
            else: ph,sev=classify_beta(g1,g2)
            row_text.append(f"{g1}/{g2}<br>{ph}"); row_z.append(sevmap.get(sev,0))
        cell_text.append(row_text); z.append(row_z)
    fig=go.Figure(go.Heatmap(z=z,x=parent2,y=parent1,text=cell_text,texttemplate="%{text}",colorscale=[[0,"#E8F8F1"],[.25,"#FFF0C6"],[.5,"#FFD6A5"],[.75,"#FF99AC"],[1,"#8D0718"]],showscale=True,colorbar=dict(title="severity"))); fig.update_xaxes(title="Parent 2 gamete"); fig.update_yaxes(title="Parent 1 gamete")
    return _layout(fig,f"{system.capitalize()}-globin Punnett risk matrix",510)

def punnett_sunburst(punnett_df: pd.DataFrame) -> go.Figure:
    fig=px.sunburst(punnett_df,path=["severity","phenotype","offspring_genotype"],values="probability",color="severity")
    return _layout(fig,"Offspring genotype probability sunburst",500)

def risk_probability_bar(punnett_df: pd.DataFrame) -> go.Figure:
    d=punnett_df.groupby(["severity"],as_index=False)["probability"].sum(); order=["critical","high","moderate","low","minimal"]; d["severity"]=pd.Categorical(d["severity"],categories=order,ordered=True); d=d.sort_values("severity")
    fig=px.bar(d,x="severity",y="probability",text="probability",labels={"severity":"Severity class","probability":"Offspring probability (%)"}); fig.update_traces(texttemplate="%{text:.0f}%",textposition="outside"); fig.update_yaxes(range=[0,100])
    return _layout(fig,"Reproductive-risk probability by severity",420)
