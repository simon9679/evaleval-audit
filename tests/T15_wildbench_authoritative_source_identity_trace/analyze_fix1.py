from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent

(HERE / "raw").mkdir(parents=True, exist_ok=True)
(HERE / "results").mkdir(parents=True, exist_ok=True)

runpy.run_path(str(HERE / "analyze.py"), run_name="__main__")
