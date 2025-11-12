#!/usr/bin/env bash
# config/update_all.sh
# Dynamisches Sanierungs-/Update-Skript für mathlab-thi-env
# - erkennt Repo-Root automatisch
# - räumt __pycache__ auf
# - erzeugt stabilen Alias 'thi_utils' (falls util/dtypes existieren)
# - bereinigt Importe projektweit (relativ profile.*, ufosim3_2_9q, util→thi_utils)
# - findet alle Subprojekte (alle pyproject.toml unter thi/i/ki/**)
# - liest interne Abhängigkeiten, sortiert topologisch
# - installiert alle Subprojekte als Editables in der venv
# - Smoke-Checks

set -euo pipefail

### 0) Repo-Root ermitteln
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if git_root="$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null)"; then
  REPO="$git_root"
elif [[ -d "$script_dir/../thi/i/ki" ]]; then
  REPO="$(cd "$script_dir/.." && pwd)"
elif [[ -d "$PWD/thi/i/ki" ]]; then
  REPO="$PWD"
else
  echo "Fehler: Repo-Root nicht gefunden." >&2
  exit 1
fi
echo "Repo: $REPO"
export REPO

### 1) venv sicherstellen und aktivieren
cd "$REPO"
if [[ ! -d .venv ]]; then python3 -m venv .venv; fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip setuptools wheel

### 2) toml-Parser bereitstellen (Py3.11+ tomllib, sonst tomli)
python -c 'import importlib.util as u; print("tomllib=ok" if u.find_spec("tomllib") else "tomllib=missing")'

if ! python -c 'import importlib.util as u, sys; sys.exit(0 if u.find_spec("tomllib") else 1)'; then
  python -m pip install -q tomli
fi

### 3) Bytecode und verbotene Paketmarker entfernen
find "$REPO/thi/i/ki" -name '__pycache__' -type d -prune -exec rm -rf {} +
find "$REPO/thi/i/ki" -path '*/src/core/__init__.py' -type f -exec rm -f {} +

### 4) Stabilen Alias 'thi_utils' erzeugen, falls util/dtypes existieren
create_thi_utils() {
  local utils_src=""
  # locate a general/* src that contains util/ or dtypes.py
  while IFS= read -r -d '' cand; do
    if [[ -d "$cand/src/util" || -f "$cand/src/dtypes.py" ]]; then
      utils_src="$cand/src"
      break
    fi
  done < <(find "$REPO/thi/i/ki/general" -mindepth 1 -maxdepth 3 -type d -name src -print0 2>/dev/null || true)

  [[ -n "$utils_src" ]] || { echo "Hinweis: kein util/dtypes gefunden, überspringe thi_utils."; return 0; }

  local util_root="$utils_src/util"
  local thi_root="$utils_src/thi_utils"
  rm -rf "$thi_root"
  mkdir -p "$thi_root"

  # __init__.py mit dynamischem Fallback auf util.*
  cat > "$thi_root/__init__.py" <<'PY'
"""Stabiler Namensraum, spiegelt 'util' dynamisch."""
import importlib as _il

def __getattr__(name: str):
    try:
        return _il.import_module(f"util.{name}")
    except Exception as e:  # pragma: no cover
        raise AttributeError(name) from e
PY

  # dtypes-Bridge, falls vorhanden
  if [[ -f "$utils_src/dtypes.py" ]]; then
    cat > "$thi_root/dtypes.py" <<'PY'
"""Alias zu 'dtypes'."""
from dtypes import *  # noqa: F401,F403
PY
  fi

  # Alle Module/Unterpakete aus util spiegeln
  if [[ -d "$util_root" ]]; then
    (
      cd "$util_root" || exit 0
      # Dateien
      find . -type f -name '*.py' ! -name '__init__.py' | while read -r f; do
        local_out="$thi_root/${f#./}"
        mkdir -p "$(dirname "$local_out")"
        # f ohne .py
        mod="${f%.py}"
        cat > "$local_out" <<PY
# Auto-generiert: Alias zu util.${mod#./}
from util.${mod#./} import *  # noqa: F401,F403
PY
      done
      # Pakete
      find . -mindepth 1 -type d | while read -r d; do
        mkdir -p "$thi_root/$d"
        cat > "$thi_root/$d/__init__.py" <<PY
# Auto-generiert: Paket-Alias zu util.${d#./}
from util.${d#./} import *  # noqa: F401,F403
PY
      done
    )
  fi
  echo "thi_utils erzeugt unter: $thi_root"
}
create_thi_utils

### 5) Projektweite Import-Fixes (nur unter src/core)
fix_imports() {
  while IFS= read -r -d '' py; do
    if [[ "$OSTYPE" == darwin* ]]; then SED_INPLACE=(sed -i ''); else SED_INPLACE=(sed -i); fi

    # 1) ufosim relativ
    if grep -qE '^[[:space:]]*from[[:space:]]+ufosim3_2_9q[[:space:]]+import[[:space:]]+UfoSim' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)from[[:space:]]+ufosim3_2_9q[[:space:]]+import[[:space:]]+UfoSim@\1from .ufosim3_2_9q import UfoSim@' "$py"
    fi

    # 2) profile.* relativ
    if grep -qE '^[[:space:]]*from[[:space:]]+profile\.' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)from[[:space:]]+profile\.@\1from .profile.@' "$py"
    fi
    if grep -qE '^[[:space:]]*import[[:space:]]+profile\.[A-Za-z0-9_]+' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)import[[:space:]]+profile\.([A-Za-z0-9_]+)@\1from .profile import \2@' "$py"
    fi

    # 3) util → thi_utils (generisch)
    #   a) from util.something import X
    if grep -qE '^[[:space:]]*from[[:space:]]+util\.' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)from[[:space:]]+util\.@\1from thi_utils.@' "$py"
    fi
    #   b) from util import X
    if grep -qE '^[[:space:]]*from[[:space:]]+util[[:space:]]+import[[:space:]]+' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)from[[:space:]]+util[[:space:]]+import[[:space:]]+@\1from thi_utils import @' "$py"
    fi
    #   c) import util as U  |  import util
    if grep -qE '^[[:space:]]*import[[:space:]]+util([[:space:]]|$)' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)import[[:space:]]+util([[:space:]]|$)@\1import thi_utils\2@' "$py"
    fi
    #   d) import util.something [as alias]
    if grep -qE '^[[:space:]]*import[[:space:]]+util\.[A-Za-z0-9_.]+' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)import[[:space:]]+util(\.[A-Za-z0-9_.]+)@\1import thi_utils\2@' "$py"
    fi

    # 4) system.util → thi_utils (falls Altcode)
    if grep -qE '^[[:space:]]*from[[:space:]]+system\.util[[:space:]]+import[[:space:]]+' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)from[[:space:]]+system\.util[[:space:]]+import[[:space:]]+@\1from thi_utils.evaluation import @' "$py"
    fi
    if grep -qE '^[[:space:]]*import[[:space:]]+system\.util([[:space:]]|\.|$)' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)import[[:space:]]+system\.util(\.[A-Za-z0-9_.]+)?@\1import thi_utils\2@' "$py"
    fi

    # 5) dtypes → thi_utils.dtypes
    if grep -qE '^[[:space:]]*from[[:space:]]+dtypes[[:space:]]+import[[:space:]]+' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)from[[:space:]]+dtypes[[:space:]]+import[[:space:]]+@\1from thi_utils.dtypes import @' "$py"
    fi
    if grep -qE '^[[:space:]]*import[[:space:]]+dtypes([[:space:]]|$)' "$py"; then
      "${SED_INPLACE[@]}" -E 's@^([[:space:]]*)import[[:space:]]+dtypes([[:space:]]|$)@\1import thi_utils.dtypes as dtypes\2@' "$py"
    fi

  done < <(find "$REPO/thi/i/ki" -path '*/src/core' -type d -print0 2>/dev/null | \
           xargs -0 -I{} find {} -type f -name '*.py' -print0)
}
fix_imports

### 6) Subprojekte automatisch finden und topologisch sortieren
# Liefert in korrekter Install-Reihenfolge: "name|abs_path"
_scan_py="$(mktemp "${TMPDIR:-/tmp}/projscan.XXXXXX.py")"
cat >"$_scan_py" <<'PY'
import os, sys, json, pathlib
# toml loader
try:
    import tomllib as tomli
except Exception:
    import tomli  # type: ignore

REPO = pathlib.Path(os.environ.get("REPO", ".")).resolve()
roots = list(REPO.joinpath("thi","i","ki").rglob("pyproject.toml"))

projects = {}   # name -> {"path":str, "deps":[names], "group":"general"/"project"/"other"}
name_by_path = {}

def load(path: pathlib.Path):
    with open(path, "rb") as f:
        data = tomli.load(f)
    name = data.get("project", {}).get("name")
    deps = data.get("project", {}).get("dependencies", []) or []
    # normalisieren
    deps_norm = []
    for d in deps:
        if isinstance(d, str):
            deps_norm.append(d.split(" ",1)[0])  # "pkg>=x" -> "pkg"
    pstr = str(path.parent)
    if "/general/" in pstr:
        group = "general"
    elif "/project/" in pstr:
        group = "project"
    else:
        group = "other"
    return name, deps_norm, path.parent, group

# Kandidaten laden
for toml in roots:
    try:
        name, deps, modroot, group = load(toml)
    except Exception:
        continue
    if not name:
        continue
    projects[name] = {"path": str(modroot), "deps": deps, "group": group}
    name_by_path[str(modroot)] = name

# interne Namenmenge
internal = set(projects.keys())

# Kanten nur für interne Abhängigkeiten
graph = {n:set() for n in internal}
indeg = {n:0 for n in internal}
for n, info in projects.items():
    for d in info["deps"]:
        if d in internal:
            graph[d].add(n)     # d -> n
            indeg[n] += 1

# Heuristischer Bonus: general vor project installieren
priority = {"general": 0, "other": 1, "project": 2}

# Kahn-Toposort mit Gruppen-Priorität
import heapq
heap = []
for n, deg in indeg.items():
    if deg == 0:
        heapq.heappush(heap, (priority[projects[n]["group"]], n))

order = []
seen = set()
while heap:
    _, n = heapq.heappop(heap)
    if n in seen: continue
    seen.add(n)
    order.append(n)
    for m in graph[n]:
        indeg[m] -= 1
        if indeg[m] == 0:
            heapq.heappush(heap, (priority[projects[m]["group"]], m))

# Zyklen auffangen: hänge Reste nach Gruppen-Priorität an
if len(order) != len(internal):
    rest = [n for n in internal if n not in seen]
    rest.sort(key=lambda n: priority[projects[n]["group"]])
    order.extend(rest)

# Ausgabe: name|path pro Zeile
for n in order:
    print(n+"|"+projects[n]["path"])
PY
ORDERED_LIST="$(python "$_scan_py")"
rm -f "$_scan_py"

if [[ -z "$ORDERED_LIST" ]]; then
  echo "Keine Subprojekte gefunden." >&2
  exit 1
fi

echo "Install-Reihenfolge:"
echo "$ORDERED_LIST" | sed 's/^/  - /'

### 7) Editables frisch installieren
# zuerst versuchen, bekannte interne Pakete zu deinstallieren (best effort)
while IFS= read -r line; do
  pkg="${line%%|*}"
  python -m pip uninstall -y "$pkg" >/dev/null 2>&1 || true
done <<< "$ORDERED_LIST"

# dann installieren
while IFS= read -r line; do
  path="${line##*|}"
  python -m pip install -e "$path"
done <<< "$ORDERED_LIST"

### 8) Sichtbarkeits-/Smoke-Checks
python - <<'PY'
import importlib.util as u
import sys, os, glob, pathlib

def has(mod: str) -> bool:
    try:
        return bool(u.find_spec(mod))
    except Exception:
        return False

print("CHECK util            :", has("util"))
print("CHECK dtypes          :", has("dtypes"))
print("CHECK thi_utils.eval  :", has("thi_utils.evaluation"))
print("CHECK core            :", has("core"))

# toml loader (tomllib>=3.11, sonst tomli)
try:
    import tomllib as _toml
except Exception:  # pragma: no cover
    import tomli as _toml  # type: ignore

roots = glob.glob("thi/i/ki/**/pyproject.toml", recursive=True)
names = []
for t in roots:
    try:
        with open(t, "rb") as f:
            d = _toml.load(f)
        n = d.get("project", {}).get("name")
        if n:
            names.append(n)
    except Exception:
        pass

for n in sorted(set(names)):
    mod = f"core.{n}_main"
    if has(mod):
        try:
            m = __import__(mod, fromlist=['*'])
            print(f"SMOKE {mod:20} -> main: {hasattr(m, 'main')}")
        except Exception as e:
            print(f"SMOKE {mod:20} -> FEHLER: {e}")
PY

echo
echo "Fertig. Startbeispiele:"
echo "  source .venv/bin/activate"
echo "  UFO_HEADLESS=1 ufo            # falls Script-Entry existiert"
echo "  UFO_HEADLESS=1 python -m core.ufo_main  # falls Modul vorhanden"