from __future__ import annotations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
T10=ROOT/"tests"/"T10_source_metric_config_heterogeneity"
SUM=T10/"results"/"summary.json"
ROWS=T10/"raw"/"source_metric_configs.jsonl"

problems=[]
s={}
if not SUM.exists():
    problems.append(f"missing T10 summary: {SUM}")
else:
    try: s=json.loads(SUM.read_text(encoding="utf-8"))
    except Exception as e: problems.append(f"cannot parse T10 summary: {type(e).__name__}: {e}")

checks={
 "verdict":"CONFIRMED",
 "affected_group_ids":2,
 "affected_groups_present":2,
 "affected_arithmetic_rows":12,
 "source_rows_complete":12,
 "source_unit_matches":12,
 "source_unit_mismatches":0,
 "affected_groups_with_single_nonunit_signature":0,
 "affected_groups_with_nonunit_metric_config_heterogeneity":2,
 "pointer_or_index_errors":0,
 "evaluation_id_mismatches":0,
 "arithmetic_row_identity_errors":0,
 "integrity_error_records":0,
}
for k,v in checks.items():
    if s and s.get(k)!=v:
        problems.append(f"T10 mismatch {k}: got {s.get(k)!r}, expected {v!r}")

expected_fields=[
 "metric_id","metric_name","metric_kind","metric_parameters",
 "lower_is_better","score_type","min_score","max_score"
]
if s and s.get("primary_signature_fields")!=expected_fields:
    problems.append(f"T10 primary_signature_fields mismatch: {s.get('primary_signature_fields')!r}")

row_count=None
if not ROWS.exists():
    problems.append(f"missing T10 source rows: {ROWS}")
else:
    try:
        rows=[json.loads(line) for line in ROWS.read_text(encoding="utf-8").splitlines() if line.strip()]
        row_count=len(rows)
        if row_count!=12:
            problems.append(f"T10 source row count mismatch: {row_count}")
    except Exception as e:
        problems.append(f"cannot parse T10 source rows: {type(e).__name__}: {e}")

raw=HERE/"raw"; raw.mkdir(exist_ok=True)
(raw/"preflight.json").write_text(json.dumps({
 "test_id":"T11_metric_config_field_decomposition",
 "t10_checks":checks,
 "primary_signature_fields":expected_fields,
 "source_row_count":row_count,
 "problems":problems,
},indent=2,sort_keys=True,ensure_ascii=True)+"\n",encoding="utf-8")

print("T11 PREFLIGHT")
print(f"source_row_count={row_count}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T11 PREFLIGHT OK")
