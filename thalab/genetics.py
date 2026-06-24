from __future__ import annotations

from itertools import product
from typing import Any
import numpy as np
import pandas as pd

ALLELES = [
    {"system":"alpha","target_code":"HBA_WT","common_name":"Normal αα haplotype","gene":"HBA1/HBA2","variant_class":"normal","hgvs":"reference","method":"control PCR","expected_bp":520,"clinical_weight":1,"interpretation":"Normal two-gene α-globin haplotype control."},
    {"system":"alpha","target_code":"SEA_DEL","common_name":"--SEA deletion","gene":"HBA1/HBA2","variant_class":"α0 deletion","hgvs":"chr16p13.3 α-globin cluster deletion","method":"gap-PCR","expected_bp":730,"clinical_weight":4,"interpretation":"Common Southeast Asian α0 deletion; reproductive risk for Hb Bart hydrops when paired with α0 deletion."},
    {"system":"alpha","target_code":"THAI_DEL","common_name":"--THAI deletion","gene":"HBA1/HBA2","variant_class":"α0 deletion","hgvs":"chr16p13.3 α-globin cluster deletion","method":"gap-PCR","expected_bp":1150,"clinical_weight":4,"interpretation":"α0 deletion associated with severe α-thalassemia risk in couples."},
    {"system":"alpha","target_code":"FIL_DEL","common_name":"--FIL deletion","gene":"HBA1/HBA2","variant_class":"α0 deletion","hgvs":"chr16p13.3 α-globin cluster deletion","method":"gap-PCR","expected_bp":930,"clinical_weight":4,"interpretation":"α0 deletion; include in regional carrier panels when indicated."},
    {"system":"alpha","target_code":"A37_DEL","common_name":"-α3.7 deletion","gene":"HBA1/HBA2","variant_class":"α+ deletion","hgvs":"3.7-kb single α-gene deletion","method":"gap-PCR","expected_bp":2020,"clinical_weight":2,"interpretation":"Single α-gene deletion; usually silent carrier or trait depending on zygosity/partner genotype."},
    {"system":"alpha","target_code":"A42_DEL","common_name":"-α4.2 deletion","gene":"HBA1/HBA2","variant_class":"α+ deletion","hgvs":"4.2-kb single α-gene deletion","method":"gap-PCR","expected_bp":1620,"clinical_weight":2,"interpretation":"Single α-gene deletion common in Asian populations."},
    {"system":"alpha","target_code":"CS","common_name":"Hb Constant Spring","gene":"HBA2","variant_class":"nondeletional α","hgvs":"HBA2:c.427T>C","method":"ARMS-PCR / sequencing","expected_bp":310,"clinical_weight":3,"interpretation":"Nondeletional α variant; more severe phenotype when combined with α0 deletion."},
    {"system":"alpha","target_code":"PAKSE","common_name":"Hb Pakse","gene":"HBA2","variant_class":"nondeletional α","hgvs":"HBA2:c.429A>T","method":"ARMS-PCR / sequencing","expected_bp":285,"clinical_weight":3,"interpretation":"Termination-codon α variant; can create HbH-like disease with α0 deletion."},
    {"system":"alpha","target_code":"QS","common_name":"Hb Quong Sze","gene":"HBA2","variant_class":"nondeletional α","hgvs":"HBA2:c.377T>C","method":"ARMS-PCR / sequencing","expected_bp":340,"clinical_weight":3,"interpretation":"Unstable α-globin variant; clinically important when paired with deletional alleles."},
    {"system":"beta","target_code":"HBB_WT","common_name":"Normal βA allele","gene":"HBB","variant_class":"normal","hgvs":"reference","method":"control PCR","expected_bp":430,"clinical_weight":1,"interpretation":"Normal β-globin allele control."},
    {"system":"beta","target_code":"HBE","common_name":"HbE","gene":"HBB","variant_class":"structural β+","hgvs":"HBB:c.79G>A p.Glu27Lys","method":"ARMS-PCR / RFLP / sequencing","expected_bp":398,"clinical_weight":3,"interpretation":"HbE allele; important in HbE/β-thalassemia reproductive risk."},
    {"system":"beta","target_code":"CD41_42","common_name":"CD41/42 -TTCT","gene":"HBB","variant_class":"β0","hgvs":"HBB:c.126_129delCTTT","method":"ARMS-PCR / sequencing","expected_bp":305,"clinical_weight":4,"interpretation":"Frameshift β0 allele common in Southeast Asian panels."},
    {"system":"beta","target_code":"IVS1_5","common_name":"IVS-I-5 G>C","gene":"HBB","variant_class":"β+","hgvs":"HBB:c.92+5G>C","method":"ARMS-PCR / sequencing","expected_bp":281,"clinical_weight":3,"interpretation":"Splice-region β+ allele."},
    {"system":"beta","target_code":"IVS1_1","common_name":"IVS-I-1 G>T","gene":"HBB","variant_class":"β0","hgvs":"HBB:c.92+1G>T","method":"ARMS-PCR / sequencing","expected_bp":267,"clinical_weight":4,"interpretation":"Canonical splice-site β0 allele."},
    {"system":"beta","target_code":"CD17","common_name":"CD17 A>T","gene":"HBB","variant_class":"β0","hgvs":"HBB:c.52A>T p.Lys18Ter","method":"ARMS-PCR / sequencing","expected_bp":238,"clinical_weight":4,"interpretation":"Nonsense β0 allele included in many SEA targeted panels."},
    {"system":"beta","target_code":"CD71_72","common_name":"CD71/72 +A","gene":"HBB","variant_class":"β0","hgvs":"HBB:c.216_217insA","method":"ARMS-PCR / sequencing","expected_bp":356,"clinical_weight":4,"interpretation":"Frameshift β0 allele."},
    {"system":"beta","target_code":"PROM28","common_name":"-28 A>G promoter","gene":"HBB","variant_class":"β+","hgvs":"HBB:c.-78A>G","method":"ARMS-PCR / sequencing","expected_bp":326,"clinical_weight":2,"interpretation":"Promoter β+ allele; typically milder but relevant for compound heterozygosity."},
    {"system":"beta","target_code":"CAP40_43","common_name":"CAP +40 to +43 -AAAC","gene":"HBB","variant_class":"β+","hgvs":"HBB:c.-11_-8delAAAC","method":"ARMS-PCR / sequencing","expected_bp":375,"clinical_weight":2,"interpretation":"β+ allele described in Southeast Asian populations."},
]

def allele_dataframe() -> pd.DataFrame:
    return pd.DataFrame(ALLELES)

def pcr_template() -> pd.DataFrame:
    return pd.DataFrame([
        {"sample_id":"PARENT-A","target_code":"SEA_DEL","observed_bp":728,"result":"Positive","lane":"A1"},
        {"sample_id":"PARENT-A","target_code":"A37_DEL","observed_bp":"","result":"Negative","lane":"A2"},
        {"sample_id":"PARENT-A","target_code":"CS","observed_bp":"","result":"Negative","lane":"A3"},
        {"sample_id":"PARENT-A","target_code":"HBE","observed_bp":399,"result":"Positive","lane":"B1"},
        {"sample_id":"PARENT-B","target_code":"SEA_DEL","observed_bp":"","result":"Negative","lane":"A4"},
        {"sample_id":"PARENT-B","target_code":"A37_DEL","observed_bp":2026,"result":"Positive","lane":"A5"},
        {"sample_id":"PARENT-B","target_code":"CD41_42","observed_bp":302,"result":"Positive","lane":"B2"},
        {"sample_id":"PARENT-B","target_code":"HBE","observed_bp":"","result":"Negative","lane":"B3"},
    ])

def _to_float(value: Any) -> float:
    try:
        if value in [None, ""]: return np.nan
        return float(value)
    except Exception:
        return np.nan

def _is_positive(value: Any) -> bool:
    if value is None or (isinstance(value, float) and np.isnan(value)): return False
    return str(value).strip().lower() in {"positive","pos","+","detected","present","yes","y","true","1"}

def match_pcr_bands(pcr_df: pd.DataFrame, tolerance_bp: int = 25) -> pd.DataFrame:
    missing = {"sample_id","target_code"} - set(pcr_df.columns)
    if missing: raise ValueError(f"PCR table is missing required columns: {sorted(missing)}")
    work = pcr_df.copy()
    if "observed_bp" not in work.columns: work["observed_bp"] = np.nan
    if "result" not in work.columns: work["result"] = ""
    if "lane" not in work.columns: work["lane"] = [f"L{i+1}" for i in range(len(work))]
    db = allele_dataframe(); out = []
    for _, r in work.iterrows():
        code = str(r["target_code"]).strip(); candidate = db[db["target_code"].str.upper() == code.upper()]
        observed = _to_float(r.get("observed_bp")); operator_pos = _is_positive(r.get("result"))
        if candidate.empty:
            row = r.to_dict(); row.update({"match_status":"Unknown target","confidence":0.0,"expected_bp":np.nan,"common_name":"Unmapped target","system":"unknown","variant_class":"unknown","delta_bp":np.nan,"interpretation":"Target code not found in the allele database.","detected":False}); out.append(row); continue
        c = candidate.iloc[0].to_dict(); expected = float(c["expected_bp"]); delta = abs(observed - expected) if not np.isnan(observed) else np.nan
        band_match = not np.isnan(delta) and delta <= tolerance_bp; detected = operator_pos or band_match
        if detected and band_match: confidence, status = max(0.55, 1 - (delta / max(tolerance_bp, 1))), "Detected: band-size matched"
        elif detected and operator_pos: confidence, status = 0.72, "Detected: operator-positive"
        else: confidence, status = 0.05, "Not detected"
        row = r.to_dict(); row.update(c); row.update({"match_status":status,"confidence":round(float(confidence),3),"delta_bp":round(float(delta),1) if not np.isnan(delta) else np.nan,"detected":bool(detected)}); out.append(row)
    return pd.DataFrame(out)

ALPHA_GENOTYPES = {"αα/αα normal":["αα","αα"],"-α/αα silent carrier":["-α","αα"],"-α/-α α+ trait":["-α","-α"],"--SEA/αα α0 trait":["--SEA","αα"],"--THAI/αα α0 trait":["--THAI","αα"],"--SEA/-α HbH risk genotype":["--SEA","-α"],"αCSα/αα Constant Spring carrier":["αCSα","αα"],"--SEA/αCSα HbH-CS genotype":["--SEA","αCSα"]}
BETA_GENOTYPES = {"βA/βA normal":["βA","βA"],"βA/βE HbE trait":["βA","βE"],"βA/β0 β-thal trait":["βA","β0"],"βA/β+ β-thal trait":["βA","β+"],"βE/βE homozygous HbE":["βE","βE"],"β0/βE HbE/β0-thalassemia":["β0","βE"],"β+/βE HbE/β+-thalassemia":["β+","βE"],"β0/β0 β-thalassemia major genotype":["β0","β0"],"β+/β+ β-thalassemia intermedia-like genotype":["β+","β+"]}

def _alpha_loss(hap: str) -> int:
    if hap == "αα": return 0
    if hap in {"-α","αCSα"}: return 1
    if hap.startswith("--"): return 2
    return 0

def classify_alpha(h1: str, h2: str) -> tuple[str, str, int]:
    loss = _alpha_loss(h1) + _alpha_loss(h2); nondeletional = "CS" in h1 or "CS" in h2
    if loss >= 4: return "Hb Bart hydrops fetalis risk", "critical", loss
    if loss == 3 and nondeletional: return "HbH disease / HbH-Constant Spring risk", "high", loss
    if loss == 3: return "HbH disease risk", "high", loss
    if loss == 2: return "α-thalassemia trait", "moderate", loss
    if loss == 1: return "Silent α-thalassemia carrier", "low", loss
    return "Unaffected α genotype", "minimal", loss

def classify_beta(a1: str, a2: str) -> tuple[str, str]:
    alleles = sorted([a1, a2]); s = set(alleles)
    if s in [{"β0","β0"},{"β0","βE"}]: return "Transfusion-dependent / severe β-globin disease risk", "critical"
    if s in [{"β+","βE"},{"β+","β0"},{"β+","β+"}]: return "β-thalassemia intermedia or HbE/β+-thalassemia risk", "high"
    if alleles == ["βE","βE"]: return "Homozygous HbE genotype", "moderate"
    if "β0" in alleles or "β+" in alleles or "βE" in alleles: return "Carrier / mild β-globin variant genotype", "low"
    return "Unaffected β genotype", "minimal"

def punnett(parent1: list[str], parent2: list[str], system: str) -> pd.DataFrame:
    rows = []
    for g1, g2 in product(parent1, parent2):
        if system == "alpha":
            phenotype, severity, burden = classify_alpha(g1, g2); rows.append({"parent1_gamete":g1,"parent2_gamete":g2,"offspring_genotype":f"{g1}/{g2}","phenotype":phenotype,"severity":severity,"allele_burden":burden,"probability":25.0})
        else:
            phenotype, severity = classify_beta(g1, g2); rows.append({"parent1_gamete":g1,"parent2_gamete":g2,"offspring_genotype":f"{g1}/{g2}","phenotype":phenotype,"severity":severity,"allele_burden":np.nan,"probability":25.0})
    df = pd.DataFrame(rows)
    return df.groupby(["offspring_genotype","phenotype","severity","allele_burden"], dropna=False, as_index=False)["probability"].sum()

def summarize_risk(punnett_df: pd.DataFrame) -> dict[str, float]:
    return {str(r["severity"]): float(r["probability"]) for _, r in punnett_df.groupby("severity", as_index=False)["probability"].sum().iterrows()}
