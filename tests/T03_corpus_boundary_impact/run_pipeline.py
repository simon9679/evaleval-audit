from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIT_ROOT = HERE.parents[1]
BACKEND = AUDIT_ROOT / "freeze" / "repos" / "eval_cards_backend_pipeline"
REGISTRY_REPO_CANDIDATES = [
    AUDIT_ROOT / "freeze" / "repos" / "eval-card-registry",
    AUDIT_ROOT / "freeze" / "repos" / "evalcard-registry",
]
EEE = AUDIT_ROOT / "freeze" / "hf" / "EEE_datastore"
CARDS = AUDIT_ROOT / "freeze" / "hf" / "auto-benchmarkcards"
REGISTRY_DATA = AUDIT_ROOT / "freeze" / "hf" / "entity-registry-data"
EXPECTED_COMMIT = "9c16ab3f93a4ba02a5b44590858bbdf824ed09d3"
SNAPSHOT_ID = "2026-08-19T02:46:43Z"

RAW = HERE / "raw"
RESULTS = HERE / "results"
RAW.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)
FACT_OUT = RAW / "fact_results_stage_f.parquet"
CAPTURE_OUT = RAW / "pipeline_capture.json"

def fail(msg: str):
    payload = {"test_id": "T03_corpus_boundary_impact", "phase": "pipeline", "status": "ERROR", "error": msg}
    (RESULTS / "pipeline_status.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    print("T03 PIPELINE ERROR")
    print(msg)
    raise SystemExit(2)

def long_path(path: Path) -> str:
    s = str(path.resolve())
    if os.name == "nt" and not s.startswith("\\\\?\\"):
        return "\\\\?\\" + s
    return s

try:
    head = subprocess.check_output(["git","-C",str(BACKEND),"rev-parse","HEAD"], text=True).strip()
except Exception as exc:
    fail(f"Cannot resolve backend HEAD: {exc}")
if head != EXPECTED_COMMIT:
    fail(f"Backend HEAD mismatch: {head}")

preflight = RAW / "preflight.json"
if not preflight.exists():
    fail("Missing raw/preflight.json; run preflight.py first.")
pf = json.loads(preflight.read_text(encoding="utf-8"))
if pf.get("problems"):
    fail("Preflight recorded problems; refusing corpus run.")

registry_repo = next((p for p in REGISTRY_REPO_CANDIDATES if p.exists()), None)
if registry_repo is None:
    fail("Frozen eval-card-registry checkout not found.")

resolver_src = registry_repo / "packages" / "eval-entity-resolver" / "src"
sys.path.insert(0, str(resolver_src))
sys.path.insert(0, str(BACKEND / "src"))

# Force default threshold and disable all refresh/pin variables.
for var in [
    "EEE_REFRESH_SNAPSHOT",
    "BENCHMARK_METADATA_REFRESH",
    "ENTITY_REGISTRY_REFRESH",
    "EEE_REVISION",
    "BENCHMARK_METADATA_REVISION",
    "ENTITY_REGISTRY_REVISION",
    "DIVERGENCE_THRESHOLD_FACTOR",
]:
    os.environ.pop(var, None)

try:
    from eval_card_backend.config import Settings
    from eval_card_backend.canonicalise import pipeline, stages
    from eval_card_backend.sources import eee, benchmark_cards, registry as registry_src
except Exception as exc:
    fail(f"Cannot import frozen production pipeline: {type(exc).__name__}: {exc}")

# Network guard. A valid T03 must reuse the frozen local snapshots.
def forbidden_network(*args, **kwargs):
    raise RuntimeError("T03 network access forbidden: frozen local source was not reusable")

class ForbiddenHfApi:
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        return forbidden_network

benchmark_cards.snapshot_download = forbidden_network
registry_src.snapshot_download = forbidden_network
eee.HfApi = ForbiddenHfApi

# Capture only Stage F evidence. Production computation is unchanged.
original_stage_f = stages.stage_f_group_signals
capture_meta = {}

def stage_f_with_capture(con, snapshot_id):
    result = original_stage_f(con, snapshot_id)
    if FACT_OUT.exists():
        FACT_OUT.unlink()
    out_sql = FACT_OUT.as_posix().replace("'", "''")
    con.execute(
        f"COPY (SELECT * FROM fact_results) TO '{out_sql}' "
        "(FORMAT PARQUET, COMPRESSION ZSTD)"
    )
    row_count = con.execute("SELECT COUNT(*) FROM fact_results").fetchone()[0]
    group_count = con.execute(
        "SELECT COUNT(DISTINCT comparability_group_id) "
        "FROM fact_results WHERE comparability_group_id IS NOT NULL"
    ).fetchone()[0]
    capture_meta.update({
        "snapshot_id": snapshot_id,
        "fact_rows": row_count,
        "comparability_groups": group_count,
        "stage_f_unit_inconsistent_groups": result,
    })
    return result

stages.stage_f_group_signals = stage_f_with_capture

settings = Settings(
    hf_token=None,
    eee_local_dir=long_path(EEE),
    benchmark_metadata_local_dir=long_path(CARDS),
    registry_local_dir=long_path(REGISTRY_DATA),
    warehouse_dir=str(HERE / "unused_warehouse"),
    refresh_eee=False,
    refresh_benchmark_metadata=False,
    refresh_registry=False,
    eee_revision=None,
    benchmark_metadata_revision=None,
    registry_revision=None,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

try:
    pipeline.run(
        settings,
        configs=None,
        config_limit=None,
        snapshot_id=SNAPSHOT_ID,
        warehouse_dir=str(HERE / "unused_warehouse"),
        registry_local_dir=long_path(REGISTRY_DATA),
        skip_preflight=False,
        cache_root=HERE / "unused_cache",
        no_cache=True,
        from_stage=None,
        to_stage="F",
        taxonomy_seed_dir=registry_repo / "seed",
    )
except BaseException as exc:
    fail(f"Production Stage A-F run failed: {type(exc).__name__}: {exc}")
finally:
    stages.stage_f_group_signals = original_stage_f

if not FACT_OUT.exists():
    fail("Stage F completed without captured fact_results Parquet.")

capture_meta["backend_commit"] = head
capture_meta["fact_results_sha256"] = hashlib.sha256(FACT_OUT.read_bytes()).hexdigest()
capture_meta["fact_results_bytes"] = FACT_OUT.stat().st_size
capture_meta["network_allowed"] = False
capture_meta["refresh_enabled"] = False
capture_meta["eee_local_dir"] = str(EEE)
capture_meta["cards_local_dir"] = str(CARDS)
capture_meta["registry_local_dir"] = str(REGISTRY_DATA)
capture_meta["taxonomy_seed_dir"] = str(registry_repo / "seed")

CAPTURE_OUT.write_text(
    json.dumps(capture_meta, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
    encoding="utf-8",
)
(RESULTS / "pipeline_status.json").write_text(
    json.dumps({
        "test_id": "T03_corpus_boundary_impact",
        "phase": "pipeline",
        "status": "COMPLETE",
        **capture_meta,
    }, indent=2, ensure_ascii=True, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("T03 PIPELINE COMPLETE")
print(f"fact_rows={capture_meta.get('fact_rows')}")
print(f"comparability_groups={capture_meta.get('comparability_groups')}")
print(f"stage_f_unit_inconsistent_groups={capture_meta.get('stage_f_unit_inconsistent_groups')}")
print(f"fact_results_bytes={capture_meta.get('fact_results_bytes')}")
print(f"fact_results_sha256={capture_meta.get('fact_results_sha256')}")
print(r"output=tests\T03_corpus_boundary_impact\raw\fact_results_stage_f.parquet")
