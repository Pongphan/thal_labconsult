from __future__ import annotations

import json
from datetime import datetime
from typing import Any

def screening_report_markdown(result: Any) -> str:
    lines = [
        "# Thalassemia Laboratory Consult Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"## Sample: {result.sample_id}",
        f"- Top interpretive pattern: **{result.top_pattern}**",
        f"- Consult risk: **{result.consult_risk}**",
        f"- Consult score: **{result.consult_score}/100**",
        "",
        "## Phenotype scores",
        f"- β-thalassemia trait/HBB pattern: {result.beta_trait_score}/100",
        f"- α-thalassemia/HbH-spectrum pattern: {result.alpha_trait_score}/100",
        f"- HbE/β-globin structural variant pattern: {result.hbe_score}/100",
        f"- Iron deficiency/mixed microcytosis pattern: {result.iron_deficiency_score}/100",
        "",
        "## Evidence",
    ]
    lines += [f"- {x}" for x in result.evidence]
    lines += ["", "## Recommendations"] + [f"- {x}" for x in result.recommendations]
    if result.caveats:
        lines += ["", "## Caveats"] + [f"- {x}" for x in result.caveats]
    lines += ["", "---", "This report is laboratory decision support and requires professional review."]
    return "\n".join(lines)

def to_json_bytes(obj: Any) -> bytes:
    if hasattr(obj, "to_flat_dict"):
        obj = obj.to_flat_dict()
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str).encode("utf-8")
