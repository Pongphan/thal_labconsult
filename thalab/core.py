from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np
import pandas as pd

SCREENING_COLUMNS = ["sample_id","age","sex","hb_g_dl","rbc_10e12_l","hct_percent","mcv_fl","mch_pg","mchc_g_dl","rdw_percent","retic_percent","ferritin_ng_ml","hba_percent","hba2_percent","hbf_percent","hbe_percent","oft","dcip","hbh_inclusion","transfusion_recent","pregnant","smear_target_cells","family_history"]
DEFAULT_THRESHOLDS = {"mcv_microcytosis":80.0,"mch_hypochromia":27.0,"hba2_beta_trait":3.5,"hbf_elevated":1.0,"hbe_present":10.0,"ferritin_deficient":15.0,"ferritin_borderline":30.0,"rbc_high":5.0,"mentzer_beta_like":13.0,"rdw_high":15.0,"severe_hb":7.0}

def safe_num(value: Any, default: float = np.nan) -> float:
    try:
        if value is None or value == "": return default
        if isinstance(value, str) and value.strip().lower() in {"nan","na","none","null"}: return default
        return float(value)
    except Exception:
        return default

def yn(value: Any) -> bool:
    if isinstance(value, bool): return value
    if value is None or (isinstance(value, float) and np.isnan(value)): return False
    return str(value).strip().lower() in {"yes","y","true","positive","pos","1","+","detected","present"}

def normalize_call(value: Any) -> str:
    return "Positive" if yn(value) else "Negative"

def anemia_threshold(sex: str | None = None, pregnant: bool = False) -> float:
    if pregnant: return 11.0
    s = (sex or "").strip().lower()
    return 13.0 if s.startswith("m") else 12.0

def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    if np.isnan(value): return lo
    return max(lo, min(hi, float(value)))

def derived_indices(row: dict[str, Any] | pd.Series) -> dict[str, float]:
    hb, rbc, mcv, mch, rdw, hct = [safe_num(row.get(k)) for k in ["hb_g_dl","rbc_10e12_l","mcv_fl","mch_pg","rdw_percent","hct_percent"]]
    mentzer = mcv / rbc if rbc and not np.isnan(mcv) and rbc > 0 else np.nan
    rdwi = (mcv * rdw / rbc) if rbc and not np.isnan(mcv) and not np.isnan(rdw) and rbc > 0 else np.nan
    shine_lal = (mcv ** 2 * mch / 100.0) if not np.isnan(mcv) and not np.isnan(mch) else np.nan
    england_fraser = mcv - rbc - (5 * hb) - 3.4 if not any(np.isnan(x) for x in [mcv, rbc, hb]) else np.nan
    green_king = ((mcv ** 2) * rdw / (100 * hb)) if hb and not any(np.isnan(x) for x in [mcv, rdw]) and hb > 0 else np.nan
    return {"mentzer_index":round(mentzer,2) if not np.isnan(mentzer) else np.nan,"rdwi":round(rdwi,2) if not np.isnan(rdwi) else np.nan,"shine_lal_index":round(shine_lal,2) if not np.isnan(shine_lal) else np.nan,"england_fraser_index":round(england_fraser,2) if not np.isnan(england_fraser) else np.nan,"green_king_index":round(green_king,2) if not np.isnan(green_king) else np.nan,"calculated_mchc":round((hb*100/hct),2) if hct and not np.isnan(hb) and hct > 0 else np.nan}

@dataclass
class ScreeningResult:
    sample_id: str; top_pattern: str; consult_risk: str; consult_score: float
    beta_trait_score: float; alpha_trait_score: float; hbe_score: float; iron_deficiency_score: float
    severe_anemia_flag: bool; microcytosis: bool; hypochromia: bool; anemia: bool
    evidence: list[str]; recommendations: list[str]; caveats: list[str]
    derived: dict[str, float]; normalized: dict[str, Any]
    def to_flat_dict(self) -> dict[str, Any]:
        out = {"sample_id":self.sample_id,"top_pattern":self.top_pattern,"consult_risk":self.consult_risk,"consult_score":self.consult_score,"beta_trait_score":self.beta_trait_score,"alpha_trait_score":self.alpha_trait_score,"hbe_score":self.hbe_score,"iron_deficiency_score":self.iron_deficiency_score,"severe_anemia_flag":self.severe_anemia_flag,"microcytosis":self.microcytosis,"hypochromia":self.hypochromia,"anemia":self.anemia,"evidence":" | ".join(self.evidence),"recommendations":" | ".join(self.recommendations),"caveats":" | ".join(self.caveats)}
        out.update(self.derived); out.update(self.normalized); return out

def analyze_screening(row: dict[str, Any] | pd.Series, thresholds: dict[str, float] | None = None) -> ScreeningResult:
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    n = {c: row.get(c, np.nan) for c in SCREENING_COLUMNS}
    n["sample_id"] = str(n.get("sample_id") if n.get("sample_id") not in [None, ""] else "CASE-001")
    n["sex"] = str(n.get("sex") if n.get("sex") not in [None, ""] else "Not specified")
    for k in ["oft","dcip","hbh_inclusion"]: n[k] = normalize_call(n.get(k))
    for k in ["transfusion_recent","pregnant","smear_target_cells","family_history"]: n[k] = yn(n.get(k))
    for k in ["age","hb_g_dl","rbc_10e12_l","hct_percent","mcv_fl","mch_pg","mchc_g_dl","rdw_percent","retic_percent","ferritin_ng_ml","hba_percent","hba2_percent","hbf_percent","hbe_percent"]: n[k] = safe_num(n.get(k))
    d = derived_indices(n)
    hb, rbc, mcv, mch, rdw, ferritin = n["hb_g_dl"], n["rbc_10e12_l"], n["mcv_fl"], n["mch_pg"], n["rdw_percent"], n["ferritin_ng_ml"]
    hba2, hbf, hbe = n["hba2_percent"], n["hbf_percent"], n["hbe_percent"]
    anemia = not np.isnan(hb) and hb < anemia_threshold(n["sex"], n["pregnant"])
    micro = not np.isnan(mcv) and mcv < t["mcv_microcytosis"]
    hypo = not np.isnan(mch) and mch < t["mch_hypochromia"]
    high_rbc = not np.isnan(rbc) and rbc >= t["rbc_high"]
    mentzer_beta_like = not np.isnan(d["mentzer_index"]) and d["mentzer_index"] < t["mentzer_beta_like"]
    rdw_high = not np.isnan(rdw) and rdw > t["rdw_high"]
    ferritin_low = not np.isnan(ferritin) and ferritin < t["ferritin_deficient"]
    ferritin_border = not np.isnan(ferritin) and ferritin < t["ferritin_borderline"]
    hba2_high = not np.isnan(hba2) and hba2 >= t["hba2_beta_trait"]
    hbf_high = not np.isnan(hbf) and hbf > t["hbf_elevated"]
    hbe_present = not np.isnan(hbe) and hbe >= t["hbe_present"]
    of_pos, dcip_pos, hbh_pos = n["oft"] == "Positive", n["dcip"] == "Positive", n["hbh_inclusion"] == "Positive"
    beta = clamp((38 if hba2_high else 0)+(14 if micro else 0)+(10 if hypo else 0)+(10 if high_rbc else 0)+(10 if mentzer_beta_like else 0)+(6 if hbf_high else 0)+(6 if of_pos else 0)+(4 if n["family_history"] else 0)+(-15 if ferritin_low else 0))
    alpha = clamp((20 if micro else 0)+(12 if hypo else 0)+(12 if high_rbc else 0)+(12 if mentzer_beta_like else 0)+(18 if (not hba2_high and not np.isnan(hba2)) else 0)+(24 if hbh_pos else 0)+(8 if of_pos else 0)+(6 if n["family_history"] else 0)+(-12 if ferritin_low else 0))
    hbe_score = clamp((46 if hbe_present else 0)+(34 if dcip_pos else 0)+(8 if micro else 0)+(6 if hba2_high else 0)+(6 if n["family_history"] else 0))
    iron = clamp((44 if ferritin_low else 0)+(20 if ferritin_border and not ferritin_low else 0)+(12 if micro else 0)+(10 if hypo else 0)+(10 if rdw_high else 0)+(8 if (not high_rbc and not np.isnan(rbc)) else 0)+(8 if (not np.isnan(d["mentzer_index"]) and d["mentzer_index"] >= t["mentzer_beta_like"]) else 0)+(-12 if hba2_high else 0))
    score_map = {"β-thalassemia trait / HBB variant pattern":beta,"α-thalassemia carrier / HbH-spectrum pattern":alpha,"HbE / β-globin structural variant pattern":hbe_score,"Iron deficiency or mixed microcytosis pattern":iron}
    top_pattern = max(score_map, key=score_map.get); consult_score = round(score_map[top_pattern],1)
    risk = "Critical review" if (not np.isnan(hb) and hb < t["severe_hb"]) else "High" if consult_score >= 75 else "Moderate" if consult_score >= 45 else "Low / inconclusive"
    evidence=[]
    if anemia: evidence.append(f"Hb below sex/pregnancy-adjusted anemia threshold ({hb:g} g/dL).")
    if micro: evidence.append(f"Microcytosis: MCV {mcv:g} fL < {t['mcv_microcytosis']:g} fL.")
    if hypo: evidence.append(f"Hypochromia: MCH {mch:g} pg < {t['mch_hypochromia']:g} pg.")
    if high_rbc: evidence.append(f"Relatively high RBC count ({rbc:g} ×10¹²/L), supportive of thalassemia carrier physiology when microcytosis is present.")
    if hba2_high: evidence.append(f"HbA2 is elevated ({hba2:g}%), supporting β-thalassemia trait in the appropriate context.")
    if hbf_high: evidence.append(f"HbF is increased ({hbf:g}%), which can accompany β-thalassemia/HBB variants.")
    if hbe_present: evidence.append(f"HbE fraction is present/increased ({hbe:g}%).")
    if dcip_pos: evidence.append("DCIP screening is positive, supporting HbE or unstable Hb reflex workup.")
    if of_pos: evidence.append("Osmotic fragility screening is positive, consistent with microcytic/hypochromic red-cell phenotype.")
    if hbh_pos: evidence.append("HbH inclusion body is positive, raising concern for HbH disease or α-thalassemia spectrum.")
    if ferritin_low: evidence.append(f"Ferritin is low ({ferritin:g} ng/mL), favoring iron deficiency or mixed thalassemia + iron deficiency.")
    if not evidence: evidence.append("No strong abnormal screening pattern was detected from the supplied values.")
    recommendations=[]
    if risk in {"High","Critical review"} or hba2_high or hbe_present or hbh_pos: recommendations.append("Proceed to confirmatory hemoglobin analysis review and molecular testing aligned with the suspected globin system.")
    if hba2_high: recommendations.append("Reflex to HBB mutation panel/sequencing if β-thalassemia carrier confirmation is clinically or reproductively relevant.")
    if alpha >= 45 or hbh_pos: recommendations.append("Reflex to HBA1/HBA2 deletion-duplication analysis; add nondeletional α-globin variant testing when HbH/Constant Spring is suspected.")
    if hbe_score >= 45: recommendations.append("Confirm HbE by Hb analysis and targeted HBB c.79G>A testing if genotype documentation is required.")
    if iron >= 45: recommendations.append("Evaluate iron status and inflammatory context; repeat HbA2 interpretation after iron repletion if values are borderline.")
    if n["pregnant"] or n["family_history"]: recommendations.append("Recommend partner testing and genetic counseling pathway if a carrier state is confirmed or strongly suspected.")
    if n["transfusion_recent"]: recommendations.append("Interpret Hb fractions with caution; recent transfusion may mask endogenous Hb patterns.")
    if not recommendations: recommendations.append("Review smear and clinical context; repeat screening or order Hb analysis if population/family risk is high.")
    caveats=[]
    if n["transfusion_recent"]: caveats.append("Recent transfusion can invalidate Hb fraction interpretation.")
    if ferritin_low: caveats.append("Iron deficiency can modify red-cell indices and may reduce or obscure HbA2 elevation.")
    if hba2_high and hbe_present: caveats.append("HbE can co-elute or alter HbA2-region interpretation depending on the analytical platform.")
    if risk == "Low / inconclusive": caveats.append("Low score does not exclude silent α-thalassemia or rare globin variants.")
    return ScreeningResult(n["sample_id"], top_pattern, risk, consult_score, round(beta,1), round(alpha,1), round(hbe_score,1), round(iron,1), risk == "Critical review", micro, hypo, anemia, evidence, recommendations, caveats, d, n)

def analyze_dataframe(df: pd.DataFrame, thresholds: dict[str, float] | None = None) -> pd.DataFrame:
    work = df.copy()
    for col in SCREENING_COLUMNS:
        if col not in work.columns: work[col] = np.nan
    return pd.DataFrame([analyze_screening(row, thresholds).to_flat_dict() for _, row in work.iterrows()])

def example_screening_dataframe() -> pd.DataFrame:
    return pd.DataFrame([
        {"sample_id":"CASE-BTT-001","age":24,"sex":"Female","hb_g_dl":11.2,"rbc_10e12_l":5.8,"hct_percent":35,"mcv_fl":67,"mch_pg":20.5,"mchc_g_dl":31.2,"rdw_percent":14.2,"retic_percent":1.2,"ferritin_ng_ml":85,"hba_percent":94,"hba2_percent":5.1,"hbf_percent":1.2,"hbe_percent":0,"oft":"Positive","dcip":"Negative","hbh_inclusion":"Negative","transfusion_recent":False,"pregnant":False,"smear_target_cells":True,"family_history":True},
        {"sample_id":"CASE-HBE-002","age":29,"sex":"Male","hb_g_dl":12.4,"rbc_10e12_l":5.2,"hct_percent":38,"mcv_fl":74,"mch_pg":23,"mchc_g_dl":31,"rdw_percent":14,"retic_percent":1.0,"ferritin_ng_ml":90,"hba_percent":72,"hba2_percent":3.8,"hbf_percent":0.8,"hbe_percent":23.5,"oft":"Positive","dcip":"Positive","hbh_inclusion":"Negative","transfusion_recent":False,"pregnant":False,"smear_target_cells":True,"family_history":False},
        {"sample_id":"CASE-ALPHA-003","age":19,"sex":"Female","hb_g_dl":11.8,"rbc_10e12_l":5.7,"hct_percent":36,"mcv_fl":69,"mch_pg":21,"mchc_g_dl":32,"rdw_percent":13.7,"retic_percent":1.3,"ferritin_ng_ml":110,"hba_percent":96.7,"hba2_percent":2.5,"hbf_percent":0.4,"hbe_percent":0,"oft":"Positive","dcip":"Negative","hbh_inclusion":"Negative","transfusion_recent":False,"pregnant":False,"smear_target_cells":False,"family_history":True},
        {"sample_id":"CASE-HBH-004","age":33,"sex":"Female","hb_g_dl":8.8,"rbc_10e12_l":5.9,"hct_percent":30,"mcv_fl":58,"mch_pg":18,"mchc_g_dl":30,"rdw_percent":18.5,"retic_percent":3.2,"ferritin_ng_ml":135,"hba_percent":88,"hba2_percent":1.8,"hbf_percent":0.9,"hbe_percent":0,"oft":"Positive","dcip":"Negative","hbh_inclusion":"Positive","transfusion_recent":False,"pregnant":False,"smear_target_cells":True,"family_history":True},
        {"sample_id":"CASE-IDA-005","age":38,"sex":"Female","hb_g_dl":9.7,"rbc_10e12_l":4.2,"hct_percent":31,"mcv_fl":72,"mch_pg":22,"mchc_g_dl":30.6,"rdw_percent":18.2,"retic_percent":0.9,"ferritin_ng_ml":8,"hba_percent":97,"hba2_percent":2.6,"hbf_percent":0.3,"hbe_percent":0,"oft":"Negative","dcip":"Negative","hbh_inclusion":"Negative","transfusion_recent":False,"pregnant":False,"smear_target_cells":False,"family_history":False},
        {"sample_id":"CASE-BORDER-006","age":30,"sex":"Male","hb_g_dl":13.5,"rbc_10e12_l":5.4,"hct_percent":41,"mcv_fl":79,"mch_pg":26,"mchc_g_dl":32,"rdw_percent":14.8,"retic_percent":1.0,"ferritin_ng_ml":34,"hba_percent":95.8,"hba2_percent":3.4,"hbf_percent":0.9,"hbe_percent":0,"oft":"Positive","dcip":"Negative","hbh_inclusion":"Negative","transfusion_recent":False,"pregnant":False,"smear_target_cells":False,"family_history":False},
    ])
