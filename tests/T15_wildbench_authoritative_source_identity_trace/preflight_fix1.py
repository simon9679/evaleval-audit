from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent

(HERE / "raw").mkdir(parents=True, exist_ok=True)
(HERE / "results").mkdir(parents=True, exist_ok=True)

print("T15 HARNESS FIX1")
print("runtime_directories_ready=True")
runpy.run_path(str(HERE / "preflight.py"), run_name="__main__")
