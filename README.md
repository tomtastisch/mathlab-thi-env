# THI KI Praktikum – Modularer Workspace

Dieses Repository bündelt mehrere eigenständige, aber miteinander kompatible Python-Pakete für das KI-Studium an der THI.

## Struktur
| Paket | Zweck |
|-------|--------|
| `thi-general-utils` | Allgemeine Utility-Funktionen für typisierte Konsoleneingaben und numerische Hilfsfunktionen |
| `angel` | Konsolenprogramm zur Winkelberechnung über Taylor-Reihenentwicklung |
| `praktikum` | Projekt-Workspace und VCS-Verwaltung aller Submodule |

## Installation (lokal)
```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -e thi/i/ki/general/system     # Utilities
pip install -e thi/i/ki/project/angel      # Hauptprogramm
# THI KI Praktikum – Modularer Workspace

Dieses Repository bündelt mehrere eigenständige, aber miteinander kompatible Python‑Pakete für das KI‑Studium an der THI. Die Dokumentation folgt einer sachlichen, normgerechten Struktur. Einheiten sind konsistent angegeben: [m], [s], [°], [km/h].

## Übersicht
| Paket | Zweck |
|---|---|
| `thi-general-utils` | Allgemeine Utility‑Funktionen (typisierte Konsoleneingaben, numerische Hilfen) |
| `angel` | Konsolenprogramm zur Winkelberechnung über Reihenentwicklung |
| `ufo` | UFO‑Simulation mit Autopilot‑Profilen (accel → slow → stop) |
| `praktikum` | Projekt‑Workspace und VCS‑Verwaltung der Submodule |

## Systemvoraussetzungen
- Betriebssystem: macOS 13+/Linux/Windows 10+ (getestet primär unter macOS auf Apple Silicon)
- Python: ≥ 3.10 (empfohlen 3.13)
- Tools: Git, optional Homebrew (macOS)
- Hinweis Namespace‑Pakete: Die Verzeichnisse `src/core` der Submodule **enthalten kein** `__init__.py` (PEP 420). 

## Installation (lokale Entwicklungsumgebung)
Die folgenden Schritte richten eine isolierte virtuelle Umgebung ein und installieren die Submodule in definierter Reihenfolge.

### 1. Schritt: Umgebung anlegen
**Vorbereitung**
- Stellen Sie sicher, dass nur **eine** Python‑Version aktiv verwendet wird (virtuelle Umgebung).

**Durchführung**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

### 2. Schritt: Submodule als Editable installieren
**Durchführung**
```bash
# 1) Utilities (stellt u.a. util.evaluation, dtypes bereit)
pip install -e thi/i/ki/general/system
# 2) Angel (benötigt Utilities)
pip install -e thi/i/ki/project/angel
# 3) UFO (benötigt Utilities + Angel)
pip install -e thi/i/ki/project/ufo
```

**Prüfung**
```bash
python - <<'PY'
import importlib.util as u
for m in ("core.ufo_main","core.ufosim3_2_9q","core.profile.h_profil","util","dtypes"):
    print(f"{m:<22}", bool(u.find_spec(m)))
PY
```
Erwartet: alle Einträge `True`.

## Ausführung
### Angel
```bash
# Start als Modul
python -m core.angel
```

### UFO
Auf macOS kann Tkinter eine GUI im Hauptthread verlangen. Nutzen Sie daher standardmäßig den **Headless‑Start**.

```bash
# Headless‑Start (empfohlen, stabil auf macOS)
export UFO_HEADLESS=1
python -m core.ufo_main
# alternativ über CLI‑Entry‑Point der venv
UFO_HEADLESS=1 ./.venv/bin/ufo
```
Interaktive Eingaben (Beispiel):
```
X- Koordinate eingeben: 33
Y- Koordinate eingeben: 44
Z- Koordinate eingeben: 55
```

## Troubleshooting
- **`NSWindow should only be instantiated on the main thread!` (macOS/Tkinter)**  
  Ursache: GUI‑Initialisierung nicht im Hauptthread. Workaround: `UFO_HEADLESS=1` setzen und ohne GUI starten. Optional kann unter manchen Python‑Distributionen `pythonw` genutzt werden.

- **`ModuleNotFoundError: core.*`**  
  Ursachen: falsche Installationsreihenfolge, venv nicht aktiv oder PEP‑420 verletzt. Maßnahmen:
  1) venv aktivieren: `source .venv/bin/activate`  
  2) sicherstellen, dass in `src/core` **kein** `__init__.py` liegt  
  3) Installationsreihenfolge erneut ausführen (Utilities → Angel → UFO)

- **`ModuleNotFoundError: util` oder `dtypes`**  
  Utilities zuerst installieren: `pip install -e thi/i/ki/general/system`.

- **Mehrere Python‑Installationen**  
  Prüfen: `which -a python python3` und `python -c "import sys; print(sys.executable)"`. Nutzen Sie konsequent die Interpreter aus `.venv`.

- **PEP 668 „externally‑managed‑environment“**  
  Installationen stets innerhalb der venv ausführen.

- **Stale Bytecode**  
  Bei Strukturänderungen Bytecode entfernen:  
  `find thi/i/ki -name '__pycache__' -type d -exec rm -rf {} +`

## Entwicklungsnotizen
- Namespaces (PEP 420): Keine `__init__.py` in `src/core`.
- Relative Importe im `ufo`‑Paket:  
  `from .ufosim3_2_9q import UfoSim`,  
  `from .profile.h_profil import HProfil as Nav`.
- CLI‑Entry‑Point: `[project.scripts] ufo = "cli:main"` (Datei `src/cli.py`).

## Versionierung und Changelog
- Semantic Versioning (X.XX.XXX.XX)
- Changelog: *Keep a Changelog*
- Aktuelle Projekt‑Releases: siehe `README.md – Editor 2` bzw. Projekt‑CHANGELOG.

## Lizenz und Nutzung
Interne Lehr‑ und Studienzwecke. Sofern nicht anders angegeben, keine Gewährleistung. Nutzung auf eigenes Risiko.