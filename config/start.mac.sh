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
print("util:", bool(u.find_spec("util")),
      "dtypes:", bool(u.find_spec("dtypes")),
      "core.ufo_main:", bool(u.find_spec("core.ufo_main")))
PY

# 6) Start (headless, um macOS/Tk zu umgehen)
export UFO_HEADLESS=1
ufo
# alternativ:
python -m core.ufo_main