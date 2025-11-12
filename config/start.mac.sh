set -euo pipefail
# 1) Zum Repo
REPO="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Projects/PyCharmProjects/mathlab-thi-env"
cd "$REPO" || { echo "Repo nicht gefunden"; exit 1; }

# 2) venv aktivieren (ggf. anlegen)
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate

# 3) Pip sicher aus der venv verwenden
python -m pip install -U pip setuptools wheel

# 4) Editables IN DER VENV installieren
python -m pip install -e "thi/i/ki/general/system"
python -m pip install -e "thi/i/ki/project/angel"
python -m pip install -e "thi/i/ki/project/ufo"

# 5) Sichtprüfung
python - <<'PY'
import importlib.util as u

def check(name: str) -> None:
    spec = u.find_spec(name)
    print(f"{name}: {bool(spec)}", end="")
    if spec:
        try:
            mod = __import__(name, fromlist=["__file__"])
            print(f" -> {getattr(mod, '__file__', spec.origin)}")
        except Exception as e:
            print(f" (import error: {e.__class__.__name__}: {e})")
    else:
        print()

for mod in ("util", "util.evaluation", "dtypes", "core.ufo_main"):
    check(mod)
PY

# 6) Start (headless, um macOS/Tk zu umgehen)
export UFO_HEADLESS=1

# Bevorzugt: Entry-Point verwenden (funktioniert bereits)
ufo

# Optional: Modulstart mit garantiertem PYTHONPATH
# export PYTHONPATH="$REPO/thi/i/ki/general/system/src:$REPO/thi/i/ki/project/ufo/src:${PYTHONPATH:-}"
# python -m core.ufo_main