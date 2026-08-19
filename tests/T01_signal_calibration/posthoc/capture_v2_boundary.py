from __future__ import annotations
import json, sys
from pathlib import Path

here = Path(__file__).resolve().parent
audit_root = here.parents[2]
backend = audit_root / "freeze" / "repos" / "eval_cards_backend_pipeline"
sys.path.insert(0, str(backend / "src"))

from eval_card_backend.signals.comparability import compute_variant_divergence_py

def row(eid, score, temp):
    return {
        "fact_id": eid,
        "evaluation_id": eid,
        "score": score,
        "generation_args": {"temperature": temp, "max_tokens": 100},
        "evaluator_relationship": "third_party",
        "source_organization_name": "Org A",
    }

points = [(0.5, 0.55), (0.5, 0.5499999999999999), (0.5, 0.5500000000000002)]
out = []
for a, b in points:
    r = compute_variant_divergence_py(
        [row("a", a, 0.0), row("b", b, 1.0)],
        {"metric_unit": "proportion"},
    )
    out.append({
        "score_a_repr": repr(a),
        "score_b_repr": repr(b),
        "divergence_repr": repr(r["divergence_magnitude"]),
        "threshold_repr": repr(r["threshold_used"]),
        "flag": r["has_variant_divergence"],
    })

path = here / "V2_BOUNDARY_DIAGNOSTIC.json"
path.write_text(json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
print("T01 POSTHOC CAPTURED")
for x in out:
    print(x)
print(f"output={path}")
