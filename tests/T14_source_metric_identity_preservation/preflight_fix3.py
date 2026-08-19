from __future__ import annotations
import json, hashlib, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

FIX2=HERE/"results"/"summary_fix2.json"
ERR2=HERE/"raw"/"integrity_errors_fix2.jsonl"
FACT=ROOT/"tests"/"T03_corpus_boundary_impact"/"raw"/"fact_results_stage_f.parquet"
T06ROOT=ROOT/"tests"/"T06_eee_source_unit_trace"/"raw"/"source_root.json"
BACKEND=ROOT/"freeze"/"repos"/"eval_cards_backend_pipeline"

EXPECTED_SHA="e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_COMMIT="9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()

def git_head(p):
    try:
        return subprocess.check_output(["git","-C",str(p),"rev-parse","HEAD"],text=True,stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None

problems=[]

if git_head(BACKEND)!=EXPECTED_COMMIT:
    problems.append(f"backend HEAD mismatch: {git_head(BACKEND)}")

if not FACT.exists():
    problems.append(f"missing Stage F: {FACT}")
elif sha256(FACT)!=EXPECTED_SHA:
    problems.append(f"Stage F SHA mismatch: {sha256(FACT)}")

fix2={}
if not FIX2.exists():
    problems.append(f"missing Fix2 summary: {FIX2}")
else:
    try:
        fix2=json.loads(FIX2.read_text(encoding="utf-8"))
        expected={
          "fix_id":"HARNESS_FIX_02",
          "verdict":"INCONCLUSIVE",
          "affected_production_groups":2,
          "affected_rows":12,
          "generation_args_source_rows_complete":12,
          "generation_args_source_errors":0,
          "production_groups_replayed_exact":1,
          "production_replay_errors":1,
          "source_id_subgroups_total":0,
          "row_identity_errors":0,
          "integrity_error_records":1,
        }
        for k,v in expected.items():
            if fix2.get(k)!=v:
                problems.append(f"Fix2 mismatch {k}: got {fix2.get(k)!r}, expected {v!r}")
    except Exception as e:
        problems.append(f"cannot parse Fix2 summary: {type(e).__name__}: {e}")

single_representation_only=False
if not ERR2.exists():
    problems.append(f"missing Fix2 integrity error file: {ERR2}")
else:
    try:
        errs=[json.loads(x) for x in ERR2.read_text(encoding="utf-8").splitlines() if x.strip()]
        if len(errs)!=1:
            problems.append(f"expected exactly one Fix2 integrity error, got {len(errs)}")
        else:
            e=errs[0]
            if e.get("type")!="production_replay_mismatch":
                problems.append(f"unexpected Fix2 error type: {e.get('type')!r}")
            else:
                fr=e.get("frozen") or {}
                rp=e.get("replay") or {}
                scalar_equal=(
                    fr.get("has_variant_divergence")==rp.get("has_variant_divergence")
                    and fr.get("divergence_magnitude")==rp.get("divergence_magnitude")
                    and fr.get("threshold_used")==rp.get("threshold_used")
                    and fr.get("threshold_basis")==rp.get("threshold_basis")
                )
                differing_only=(fr.get("differing_setup_fields")!=rp.get("differing_setup_fields"))
                single_representation_only=bool(scalar_equal and differing_only)
                if not single_representation_only:
                    problems.append("Fix2 remaining mismatch is not representation-only")
    except Exception as e:
        problems.append(f"cannot parse Fix2 integrity error: {type(e).__name__}: {e}")

eee_root=None
if not T06ROOT.exists():
    problems.append(f"missing T06 source root: {T06ROOT}")
else:
    try:
        x=json.loads(T06ROOT.read_text(encoding="utf-8"))
        eee_root=x.get("selected_root")
        if not eee_root or not Path(eee_root).is_dir():
            problems.append(f"invalid EEE root: {eee_root!r}")
    except Exception as e:
        problems.append(f"cannot parse EEE root: {type(e).__name__}: {e}")

try:
    import pyarrow as pa
    pyarrow_version=pa.__version__
except Exception as e:
    pyarrow_version=None
    problems.append(f"missing pyarrow: {type(e).__name__}: {e}")

# Verify frozen typed-loader imports are readable.
try:
    import sys
    sys.path.insert(0,str(BACKEND/"src"))
    from eval_card_backend.schemas.eee_arrow import derive_pyarrow_schema, pad_record_for_cast
    from eval_card_backend.schemas.eee_types import EvaluationLog
    schema=derive_pyarrow_schema()
    schema_fields=len(schema)
except Exception as e:
    schema_fields=None
    problems.append(f"cannot load frozen Stage-A schema tools: {type(e).__name__}: {e}")

payload={
 "test_id":"T14_source_metric_identity_preservation",
 "fix_id":"HARNESS_FIX_03",
 "fact_sha256":sha256(FACT) if FACT.exists() else None,
 "eee_root":eee_root,
 "fix2_representation_only_mismatch":single_representation_only,
 "pyarrow":pyarrow_version,
 "schema_fields":schema_fields,
 "problems":problems,
}
(HERE/"raw"/"preflight_fix3.json").parent.mkdir(exist_ok=True)
(HERE/"raw"/"preflight_fix3.json").write_text(
    json.dumps(payload,indent=2,sort_keys=True,ensure_ascii=True)+"\n",
    encoding="utf-8"
)

print("T14 FIX3 PREFLIGHT")
print(f"fact_sha256={payload['fact_sha256']}")
print(f"eee_root={eee_root}")
print(f"fix2_representation_only_mismatch={single_representation_only}")
print(f"pyarrow={pyarrow_version}")
print(f"schema_fields={schema_fields}")
print(f"problems={len(problems)}")
for p in problems: print(f"PROBLEM {p}")
if problems: raise SystemExit(2)
print("T14 FIX3 PREFLIGHT OK")
