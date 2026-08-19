from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FACT = ROOT / "tests" / "T03_corpus_boundary_impact" / "raw" / "fact_results_stage_f.parquet"
BACKEND = ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"
SOURCE_ROOT_FILE = HERE / "raw" / "source_root.json"

EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
EXPECTED_SHA = "e9edc3bf8c6c07f968ff4fb556ceb75a55219ca11076a0130cde419fab5f7196"
EXPECTED_GROUPS = 1234

ROW_TRACE = HERE / "raw" / "row_trace.jsonl"
ROW_MISMATCH = HERE / "raw" / "row_mismatches.jsonl"
GROUP_TRACE = HERE / "raw" / "group_trace.jsonl"
GROUP_MISMATCH = HERE / "raw" / "group_mismatches.jsonl"
INTEGRITY = HERE / "raw" / "integrity_errors.jsonl"
SUMMARY = HERE / "results" / "summary.json"
ANALYSIS = HERE / "results" / "RESULT_ANALYSIS.md"

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def normalize_source_unit(value: Any) -> Any:
    if isinstance(value, str) and value.lower() == "percentage":
        return "percent"
    return value

def hard_error(msg: str):
    SUMMARY.parent.mkdir(exist_ok=True)
    SUMMARY.write_text(
        json.dumps(
            {"test_id": "T06_eee_source_unit_trace", "verdict": "ERROR", "error": msg},
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    print("T06 ERROR")
    print(msg)
    raise SystemExit(2)

if not (HERE / "raw" / "preflight.json").exists():
    hard_error("Missing T06 preflight evidence.")
if not SOURCE_ROOT_FILE.exists():
    hard_error("Missing source_root.json.")

head = subprocess.check_output(
    ["git", "-C", str(BACKEND), "rev-parse", "HEAD"], text=True
).strip()
if head != EXPECTED_COMMIT:
    hard_error(f"Backend HEAD mismatch: {head}")
if not FACT.exists():
    hard_error("Missing T03 Stage F parquet.")
if sha256(FACT) != EXPECTED_SHA:
    hard_error("T03 Stage F parquet SHA mismatch.")

root_payload = json.loads(SOURCE_ROOT_FILE.read_text(encoding="utf-8"))
eee_root_value = root_payload.get("selected_root")
if not eee_root_value:
    hard_error("EEE root was not uniquely resolved by preflight.")
EEE_ROOT = Path(eee_root_value)
if not EEE_ROOT.is_dir():
    hard_error(f"EEE root does not exist: {EEE_ROOT}")

import duckdb
con = duckdb.connect()
p = FACT.as_posix().replace("'", "''")

required = {
    "comparability_group_id",
    "fact_id",
    "evaluation_id",
    "evaluation_result_id",
    "result_idx",
    "source_record_path",
    "metric_unit",
    "metric_unit_provenance",
}
cols = {
    r[0]
    for r in con.execute(
        f"DESCRIBE SELECT * FROM read_parquet('{p}')"
    ).fetchall()
}
missing = sorted(required - cols)
if missing:
    hard_error(f"Stage F schema missing required columns: {missing}")

fact_rows_scanned = con.execute(
    f"SELECT COUNT(*) FROM read_parquet('{p}')"
).fetchone()[0]
comparability_groups_scanned = con.execute(
    f"""
    SELECT COUNT(DISTINCT comparability_group_id)
    FROM read_parquet('{p}')
    WHERE comparability_group_id IS NOT NULL
    """
).fetchone()[0]

mixed_ids = [
    r[0]
    for r in con.execute(
        f"""
        SELECT comparability_group_id
        FROM read_parquet('{p}')
        WHERE comparability_group_id IS NOT NULL
        GROUP BY comparability_group_id
        HAVING COUNT(DISTINCT metric_unit)
               FILTER (WHERE metric_unit IS NOT NULL) > 1
        ORDER BY comparability_group_id
        """
    ).fetchall()
]
integrity_errors = []
if len(mixed_ids) != EXPECTED_GROUPS:
    integrity_errors.append(
        {"type": "mixed_group_count", "got": len(mixed_ids), "expected": EXPECTED_GROUPS}
    )

con.execute("CREATE TEMP TABLE _mixed_ids(id VARCHAR)")
con.executemany("INSERT INTO _mixed_ids VALUES (?)", [(x,) for x in mixed_ids])

rows = con.execute(
    f"""
    SELECT
      fr.comparability_group_id,
      fr.fact_id,
      fr.evaluation_id,
      fr.evaluation_result_id,
      fr.result_idx,
      fr.source_record_path,
      fr.metric_unit,
      fr.metric_unit_provenance
    FROM read_parquet('{p}') fr
    JOIN _mixed_ids m ON m.id = fr.comparability_group_id
    ORDER BY fr.comparability_group_id, fr.fact_id
    """
).fetchall()
names = [d[0] for d in con.description]
stage_rows = [dict(zip(names, r)) for r in rows]

counts = Counter()
counts["mixed_unit_groups"] = len(mixed_ids)
counts["mixed_unit_rows"] = len(stage_rows)
source_file_paths = {
    r["source_record_path"] for r in stage_rows if r["source_record_path"]
}
counts["source_files_referenced"] = len(source_file_paths)

cache = {}
source_units_by_group = defaultdict(set)
stage_units_by_group = defaultdict(set)
row_mismatch_records = []
pointer_errors = []
evaluation_id_mismatch_records = []
source_unit_patterns = Counter()

def load_record(rel: str):
    if rel in cache:
        return cache[rel]
    path = EEE_ROOT / rel
    if not path.exists():
        raise FileNotFoundError(str(path))
    obj = json.loads(path.read_text(encoding="utf-8"))
    cache[rel] = obj
    return obj

with ROW_TRACE.open("w", encoding="utf-8", newline="\n") as ft:
    for row in stage_rows:
        gid = row["comparability_group_id"]
        if row["metric_unit"] is not None:
            stage_units_by_group[gid].add(row["metric_unit"])

        trace = dict(row)
        trace.update(
            {
                "source_unit_raw": None,
                "source_unit_normalized": None,
                "match": None,
                "trace_error": None,
            }
        )

        rel = row["source_record_path"]
        idx = row["result_idx"]
        try:
            if not rel:
                raise ValueError("source_record_path is null/empty")
            rec = load_record(rel)
            if not isinstance(rec, dict):
                raise TypeError("source record is not a JSON object")

            rec_eval_id = rec.get("evaluation_id")
            if rec_eval_id is not None and rec_eval_id != row["evaluation_id"]:
                counts["evaluation_id_mismatches"] += 1
                evaluation_id_mismatch_records.append(
                    {
                        "comparability_group_id": gid,
                        "fact_id": row["fact_id"],
                        "source_record_path": rel,
                        "stage_evaluation_id": row["evaluation_id"],
                        "source_evaluation_id": rec_eval_id,
                    }
                )

            ers = rec.get("evaluation_results")
            if not isinstance(ers, list):
                raise TypeError("evaluation_results is not a list")
            if not isinstance(idx, int):
                idx = int(idx)
            if idx < 0 or idx >= len(ers):
                raise IndexError(
                    f"result_idx {idx} outside evaluation_results length {len(ers)}"
                )
            source_row = ers[idx]
            if not isinstance(source_row, dict):
                raise TypeError("evaluation_results[result_idx] is not an object")
            metric_config = source_row.get("metric_config")
            if metric_config is None:
                metric_config = {}
            if not isinstance(metric_config, dict):
                raise TypeError("metric_config is not an object")

            raw_unit = metric_config.get("metric_unit")
            norm_unit = normalize_source_unit(raw_unit)
            trace["source_unit_raw"] = raw_unit
            trace["source_unit_normalized"] = norm_unit
            trace["match"] = norm_unit == row["metric_unit"]
            counts["row_traces_complete"] += 1

            if norm_unit is not None:
                source_units_by_group[gid].add(norm_unit)
                source_unit_patterns[repr(norm_unit)] += 1

            if trace["match"]:
                counts["row_unit_matches"] += 1
            else:
                counts["row_unit_mismatches"] += 1
                row_mismatch_records.append(dict(trace))
        except Exception as exc:
            counts["pointer_or_index_errors"] += 1
            trace["trace_error"] = f"{type(exc).__name__}: {exc}"
            pointer_errors.append(dict(trace))

        ft.write(json.dumps(trace, ensure_ascii=True, sort_keys=True) + "\n")

counts["source_files_opened"] = len(cache)

with ROW_MISMATCH.open("w", encoding="utf-8", newline="\n") as f:
    for r in row_mismatch_records:
        f.write(json.dumps(r, ensure_ascii=True, sort_keys=True) + "\n")

group_mismatch_records = []
with GROUP_TRACE.open("w", encoding="utf-8", newline="\n") as f:
    for gid in mixed_ids:
        stage_set = sorted(stage_units_by_group.get(gid, set()))
        source_set = sorted(source_units_by_group.get(gid, set()))
        match = stage_set == source_set
        record = {
            "comparability_group_id": gid,
            "stage_units": stage_set,
            "source_units_normalized": source_set,
            "match": match,
        }
        if match:
            counts["group_unit_set_matches"] += 1
        else:
            counts["group_unit_set_mismatches"] += 1
            group_mismatch_records.append(record)
        f.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")

with GROUP_MISMATCH.open("w", encoding="utf-8", newline="\n") as f:
    for r in group_mismatch_records:
        f.write(json.dumps(r, ensure_ascii=True, sort_keys=True) + "\n")

# Global provenance invariant from T05 should still hold row-wise.
bad_prov = [
    r for r in stage_rows if r["metric_unit_provenance"] != "eee_record"
]
if bad_prov:
    integrity_errors.append(
        {
            "type": "unexpected_metric_unit_provenance",
            "count": len(bad_prov),
        }
    )

if counts["evaluation_id_mismatches"]:
    integrity_errors.append(
        {
            "type": "evaluation_id_mismatch",
            "count": counts["evaluation_id_mismatches"],
            "examples": evaluation_id_mismatch_records[:10],
        }
    )

if counts["pointer_or_index_errors"]:
    integrity_errors.append(
        {
            "type": "pointer_or_index_errors",
            "count": counts["pointer_or_index_errors"],
            "examples": pointer_errors[:10],
        }
    )

with INTEGRITY.open("w", encoding="utf-8", newline="\n") as f:
    for e in integrity_errors:
        f.write(json.dumps(e, ensure_ascii=True, sort_keys=True) + "\n")

if counts["pointer_or_index_errors"] > 0 or len(mixed_ids) != EXPECTED_GROUPS:
    verdict = "INCONCLUSIVE"
elif len(integrity_errors) > 0:
    verdict = "INCONCLUSIVE"
elif counts["row_unit_mismatches"] > 0 or counts["group_unit_set_mismatches"] > 0:
    verdict = "REFUTED"
else:
    verdict = "CONFIRMED"

summary = {
    "test_id": "T06_eee_source_unit_trace",
    "verdict": verdict,
    "backend_commit": head,
    "fact_rows_scanned": fact_rows_scanned,
    "comparability_groups_scanned": comparability_groups_scanned,
    "mixed_unit_groups": counts["mixed_unit_groups"],
    "mixed_unit_rows": counts["mixed_unit_rows"],
    "source_files_referenced": counts["source_files_referenced"],
    "source_files_opened": counts["source_files_opened"],
    "row_traces_complete": counts["row_traces_complete"],
    "row_unit_matches": counts["row_unit_matches"],
    "row_unit_mismatches": counts["row_unit_mismatches"],
    "group_unit_set_matches": counts["group_unit_set_matches"],
    "group_unit_set_mismatches": counts["group_unit_set_mismatches"],
    "pointer_or_index_errors": counts["pointer_or_index_errors"],
    "evaluation_id_mismatches": counts["evaluation_id_mismatches"],
    "integrity_error_records": len(integrity_errors),
    "source_unit_patterns": dict(sorted(source_unit_patterns.items())),
    "competing_predictions": {
        "P1": (
            "row_unit_mismatches = 0; group_unit_set_mismatches = 0; "
            "pointer_or_index_errors = 0"
        ),
        "P2": (
            "row_unit_mismatches >= 1 or group_unit_set_mismatches >= 1 "
            "on otherwise valid traces"
        ),
    },
    "limitations": [
        "T06 verifies the frozen EEE datastore, not the original publisher or leaderboard.",
        "Source-record agreement does not establish semantic correctness of the unit.",
        "T06 does not test whether EvalEval should normalize or reject mixed-unit groups.",
        "T06 does not test final comparability boolean impact; T04 tested that separately.",
    ],
    "evidence": {
        "input_fact_sha256": sha256(FACT),
        "row_trace_sha256": sha256(ROW_TRACE),
        "row_mismatches_sha256": sha256(ROW_MISMATCH),
        "group_trace_sha256": sha256(GROUP_TRACE),
        "group_mismatches_sha256": sha256(GROUP_MISMATCH),
        "integrity_errors_sha256": sha256(INTEGRITY),
    },
}
SUMMARY.write_text(
    json.dumps(summary, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
    encoding="utf-8",
)

lines = [
    "# RESULT_ANALYSIS — T06 Frozen EEE Source Unit Trace",
    "",
    "Status: generated after execution from the frozen T06 summary.",
    "",
    f"Primary verdict: `{verdict}`.",
    "",
    "## Raw counts",
    "",
]
for key in [
    "fact_rows_scanned",
    "comparability_groups_scanned",
    "mixed_unit_groups",
    "mixed_unit_rows",
    "source_files_referenced",
    "source_files_opened",
    "row_traces_complete",
    "row_unit_matches",
    "row_unit_mismatches",
    "group_unit_set_matches",
    "group_unit_set_mismatches",
    "pointer_or_index_errors",
    "evaluation_id_mismatches",
    "integrity_error_records",
]:
    lines.append(f"- `{key}` = {summary[key]}")

lines += ["", "## Interpretation", ""]
if verdict == "CONFIRMED":
    lines += [
        "P1 was observed across the complete mixed-unit population.",
        "",
        "The Stage F unit values and unit sets are directly reproduced from the referenced frozen EEE aggregate records after only the documented percentage-to-percent synonym normalization.",
        "",
        "This verifies the pipeline's `eee_record` provenance label at the frozen EEE datastore boundary.",
        "",
        "It does not establish that the original publisher emitted the value or that the value is semantically correct.",
    ]
elif verdict == "REFUTED":
    lines += [
        "P2 was observed: at least one valid source trace disagrees with the Stage F unit value or group unit set.",
        "",
        "The mismatching traces must be inspected before assigning the transformation to EEE, EvalEval, or another component.",
    ]
else:
    lines += [
        "Neither source-faithfulness prediction can be interpreted for the full population because an evidence-integrity condition failed.",
        "",
        "No source-vs-EvalEval attribution is permitted until the trace measurement is repaired.",
    ]

lines += [
    "",
    "## Scope limits",
    "",
    "- Frozen EEE datastore agreement is not original-publisher agreement.",
    "- Agreement is not semantic correctness.",
    "- This test does not establish public product impact.",
    "- This test does not reopen the T04 boolean-impact verdict.",
    "",
    "## Evidence",
    "",
    "- `raw/source_root.json`",
    "- `raw/row_trace.jsonl`",
    "- `raw/row_mismatches.jsonl`",
    "- `raw/group_trace.jsonl`",
    "- `raw/group_mismatches.jsonl`",
    "- `raw/integrity_errors.jsonl`",
    "- `results/summary.json`",
]
ANALYSIS.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("T06 COMPLETE")
for key in [
    "verdict",
    "fact_rows_scanned",
    "comparability_groups_scanned",
    "mixed_unit_groups",
    "mixed_unit_rows",
    "source_files_referenced",
    "source_files_opened",
    "row_traces_complete",
    "row_unit_matches",
    "row_unit_mismatches",
    "group_unit_set_matches",
    "group_unit_set_mismatches",
    "pointer_or_index_errors",
    "evaluation_id_mismatches",
    "integrity_error_records",
]:
    print(f"{key}={summary[key]}")
print("source_unit_patterns=" + json.dumps(summary["source_unit_patterns"], ensure_ascii=True, sort_keys=True))
print(r"summary=tests\T06_eee_source_unit_trace\results\summary.json")
print(r"analysis=tests\T06_eee_source_unit_trace\results\RESULT_ANALYSIS.md")
