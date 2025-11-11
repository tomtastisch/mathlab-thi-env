#!/usr/bin/env bash
set -euo pipefail

# ==== Konfiguration ====
NAME="projectname"  # <— nur hier anpassen: lowercase, [a-z0-9_-]

# ==== Repo-Erkennung (auto) ====
# 1) REPO aus Umgebung hat Vorrang
REPO="${REPO:-}"

# 2) Falls leer: Git-Wurzel bestimmen
if [[ -z "$REPO" ]] && command -v git >/dev/null 2>&1; then
  REPO="$(git rev-parse --show-toplevel 2>/dev/null || true)"
fi

# 3) Falls weiter leer: vom Skriptverzeichnis und CWD nach oben suchen
if [[ -z "$REPO" ]]; then
  here="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
  for cand in "$PWD" "$here" "$here/.." "$here/../.." "$here/../../.."; do
    if [[ -d "$cand/thi/i/ki/project" ]]; then
      REPO="$(cd "$cand" && pwd -P)"
      break
    fi
    if [[ "$(basename "$cand")" == "mathlab-thi-env" ]]; then
      REPO="$(cd "$cand" && pwd -P)"
      break
    fi
  done
fi

# 4) Letzter Versuch: bis zur Wurzel laufen und auf Verzeichnisnamen prüfen
if [[ -z "$REPO" ]]; then
  cand="$PWD"
  while [[ "$cand" != "/" ]]; do
    if [[ "$(basename "$cand")" == "mathlab-thi-env" ]]; then
      REPO="$cand"
      break
    fi
    cand="$(dirname "$cand")"
  done
fi

# 5) Validierung
if [[ -z "$REPO" ]] || [[ ! -d "$REPO" ]]; then
  echo "Repo-Wurzel nicht gefunden. Starte das Skript im mathlab-thi-env-Repo oder setzen Sie REPO=/pfad/zum/repo." >&2
  exit 1
fi

ROOT="$REPO/thi/i/ki/project/$NAME"
DATE="$(date +%F)"
TITLE="$(printf '%s' "$NAME" | awk '{print toupper(substr($0,1,1)) substr($0,2)}')"

# ==== Vorprüfung ====
if [[ ! "$NAME" =~ ^[a-z][a-z0-9_-]*$ ]]; then
  echo "NAME ungültig. Erlaubt: lowercase, Ziffern, _ und -." >&2
  exit 1
fi
if [[ ! -d "$REPO" ]]; then
  echo "Repo nicht gefunden: $REPO" >&2
  exit 1
fi

# ==== Neu aufsetzen ====
rm -rf "$ROOT"
mkdir -p "$ROOT/src/core" "$ROOT/pa"

# WICHTIG: PEP-420 Namespace-Pakete => KEINE __init__.py in src/ oder src/core/

# core/<name>.py – minimaler Startpunkt mit Utils-Import
cat > "$ROOT/src/core/$NAME.py" <<'PY'
"""
Modulstartpunkt.

Hinweise:
- Namespace-Paket (PEP 420): kein __init__.py in src/ oder src/core/.
- Abhängigkeit auf thi-general-utils (stellt util.evaluation, dtypes bereit).
"""
from __future__ import annotations

try:
    # bevorzugt: aktuelles Utils-Paket
    from util.evaluation import read_input, eps
except ModuleNotFoundError:
    # Legacy-Fallback (falls altes Layout vorhanden ist)
    from system.util import read_input, eps  # type: ignore

def _demo() -> None:
    """Einfacher Konsolenlauf zur Sichtprüfung."""
    x: int = read_input("Test-Eingabe (int): ", int)
    print(f"Eingabe = {x}, eps = {eps()}")

if __name__ == "__main__":
    print("Start:", __name__)
    _demo()
PY

# Optionaler CLI-Wrapper (für Konsolenkommando $NAME)
cat > "$ROOT/src/cli.py" <<'PY'
def main() -> int:
    # Einstieg für [project.scripts]
    from core import __dict__ as _ns  # Namespace sichtbar machen
    # Versuche core/<name>.py als Hauptmodul zu finden und laufen zu lassen:
    # Hinweis: Der eigentliche Modulname ersetzt <NAME> beim Aufruf; hier keine hart verdrahtete Logik nötig.
    print("CLI gestartet – verwenden Sie 'python -m core.<name>' für das Modul.")
    return 0
PY

# README (kurzer Platzhalter – Projekt-README im Hauptrepo ist führend)
cat > "$ROOT/README.md" <<EOF
# ${TITLE}
Subprojekt innerhalb des THI-Praktikum-Workspaces.

## Installation (aus Repo-Wurzel)
python -m pip install -e "thi/i/ki/general/system"
python -m pip install -e "thi/i/ki/project/angel"   # falls benötigt
python -m pip install -e "thi/i/ki/project/${NAME}"

## Ausführung
python -m core.${NAME}
# oder via CLI (falls sinnvoll):
${NAME}
EOF

# CHANGELOG
cat > "$ROOT/CHANGELOG.${NAME}.md" <<EOF
# CHANGELOG – ${TITLE}-Modul
## [0.01.000.01] – ${DATE}
### Added
- Projektinitialisierung (src/core, CLI, Ordner pa/)
- PEP-420 Namespace (keine __init__.py in src/ und src/core)
- Abhängigkeit auf thi-general-utils (util.evaluation, dtypes)
EOF

# pa/AUFGABEN.md (Platzhalter)
cat > "$ROOT/pa/AUFGABEN.md" <<EOF
# Aufgabenstellungen – ${TITLE}
Hier manuell Aufgaben, PDFs oder Hinweise ablegen.
Strukturvorschlag: YYYY-MM-DD_<kurzbeschreibung>.md
EOF

# pyproject.toml – Namespace-Pakete, CLI, Abhängigkeiten
cat > "$ROOT/pyproject.toml" <<TOML
[build-system]
requires = ["setuptools>=75", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "${NAME}"
version = "0.1.0"
description = "${NAME} – CLI"
readme = "README.md"
requires-python = ">=3.10"
authors = [{ name = "Tom Werner" }]
dependencies = [
  "numpy>=1.26",
  "thi-general-utils>=0.1.0"
]

[project.scripts]
${NAME} = "cli:main"

[tool.setuptools]
package-dir = {"" = "src"}
py-modules = ["cli"]

[tool.setuptools.packages.find]
where = ["src"]
include = ["core*"]
namespaces = true
TOML

# Kurzer Abschluss-Hinweis
cat <<MSG
Neu aufgesetzt: $ROOT

Nächste Schritte (aus Repo-Wurzel, venv aktiv):
  python -m pip install -e "thi/i/ki/general/system"
  python -m pip install -e "thi/i/ki/project/${NAME}"

Start:
  python -m core.${NAME}
  # optional:
  ${NAME}