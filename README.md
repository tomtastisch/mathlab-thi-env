# THI KI Praktikum – Modularer Workspace

Dieses Repository bündelt mehrere eigenständige, aber miteinander kompatible Python‑Pakete für das KI‑Studium an der THI. Die Dokumentation ist sachlich strukturiert, einheitenkonsistent \[m], \[s], \[°], \[km/h] und venv‑konform.

---

## Inhaltsverzeichnis
1. Zweck und Geltungsbereich  
2. Systemvoraussetzungen  
3. Verzeichnisstruktur  
4. Installation (Erstsetup)  
5. Aktualisierung bestehender Umgebungen  
6. Ausführung (Angel, UFO)  
7. Validierung der Installation  
8. Fehlerdiagnose (Troubleshooting)  
9. Hinweise zur Paket‑ und Build‑Struktur  
10. Headless‑Modus unter macOS (Tk)  
11. Deinstallation / Neuaufsetzen  
12. Versionierung und Changelogs  
13. Lizenz

---

## 1. Zweck und Geltungsbereich
Ziel ist die reproduzierbare Ausführung der UFO‑Simulation mit profilierter Annäherungslogik (accel → slow → stop) sowie begleitender mathematischer Utilities. Diese Anleitung deckt Einrichtung, Betrieb, Wartung und Fehlersuche ab.

---

## 2. Systemvoraussetzungen
- Betriebssystem: macOS 13+/Linux/Windows 10+ (primär unter macOS auf Apple Silicon getestet)  
- Python: ≥ 3.10 (empfohlen 3.11–3.13)  
- Tools: Git, optional Homebrew (macOS)  
- Rechte: Schreibzugriff im Projektverzeichnis, Internetzugang für `pip`  

Hinweis zu Namespace‑Paketen: Verzeichnisse `src/core` der Submodule **enthalten kein** `__init__.py` (PEP 420).

---

## 3. Verzeichnisstruktur
```
thi/
  i/ki/general/system/        # thi-general-utils → stellt 'util', 'dtypes' bereit
  i/ki/project/angel/         # Winkel-/Geometriemodul (Namespace: core.angel)
  i/ki/project/ufo/           # UFO-Simulation (Namespace: core.*; CLI-Entry 'ufo')
praktikum/
  README.md                   # diese Datei
```

---

## 4. Installation (Erstsetup)
Die Schritte richten eine isolierte virtuelle Umgebung ein und installieren die Submodule in definierter Reihenfolge.

### 4.1 Vorbereitung
Stellen Sie sicher, dass nur **eine** Python‑Installation verwendet wird (virtuelle Umgebung).

### 4.2 Durchführung
```bash
# 1) Zum Repository
REPO="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Projects/PyCharmProjects/mathlab-thi-env"
cd "$REPO" || { echo "Repo nicht gefunden"; exit 1; }

# 2) Virtuelle Umgebung anlegen und aktivieren
python3 -m venv .venv
source .venv/bin/activate

# 3) Build-Werkzeuge aktualisieren
python -m pip install -U pip setuptools wheel

# 4) Submodule als Editables installieren (Reihenfolge ist verbindlich)
python -m pip install -e "thi/i/ki/general/system"   # liefert: util, dtypes
python -m pip install -e "thi/i/ki/project/angel"     # benötigt util/dtypes
python -m pip install -e "thi/i/ki/project/ufo"       # benötigt angel + util/dtypes
```

---

## 5. Aktualisierung bestehender Umgebungen
```bash
cd "$REPO" && source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e "thi/i/ki/general/system"
python -m pip install -e "thi/i/ki/project/angel"
python -m pip install -e "thi/i/ki/project/ufo"
```

---

## 6. Ausführung (Angel, UFO)

### 6.1 Angel
Start als Modul:
```bash
cd "$REPO" && source .venv/bin/activate
python -m core.angel
```

### 6.2 UFO
Unter macOS verlangt Tkinter die GUI‑Initialisierung im Hauptthread. Nutzen Sie standardmäßig den **Headless‑Start**.

```bash
cd "$REPO" && source .venv/bin/activate

# Headless-Start (empfohlen und stabil unter macOS)
export UFO_HEADLESS=1
python -m core.ufo_main

# alternativ über den CLI-Entry-Point der venv:
UFO_HEADLESS=1 ./.venv/bin/ufo
```

Beispiel für interaktive Eingaben:
```
X- Koordinate eingeben: 33
Y- Koordinate eingeben: 44
Z- Koordinate eingeben: 55
```

---

## 7. Validierung der Installation
```bash
cd "$REPO" && source .venv/bin/activate
python - <<'PY'
import importlib.util as u
checks = {
  "util": "util",
  "dtypes": "dtypes",
  "core.ufo_main": "core.ufo_main",
  "core.ufosim3_2_9q": "core.ufosim3_2_9q",
  "core.profile.h_profil": "core.profile.h_profil",
}
for name, mod in checks.items():
    print(f"{name:<20}", bool(u.find_spec(mod)))
PY
```
Erwartung: Alle Einträge geben `True` zurück.

---

## 8. Fehlerdiagnose (Troubleshooting)

**8.1 `ModuleNotFoundError: util` oder `dtypes`**  
Ursache: Utilities nicht installiert oder falscher Interpreter.  
Abhilfe:
```bash
cd "$REPO" && source .venv/bin/activate
python -m pip install -e "thi/i/ki/general/system"
```

**8.2 `No module named 'core'` beim Start**  
Ursache: `ufo` nicht in der aktiven venv installiert oder falscher Interpreter.  
Abhilfe:
```bash
cd "$REPO" && source .venv/bin/activate
python -m pip install -e "thi/i/ki/project/ufo"
```

**8.3 `profile.h_profil is not a package`**  
Ursache: Falscher Import (`from profile...`).  
Soll: Paket‑relativ importieren, z. B. `from .profile.h_profil import HProfil as Nav` in Dateien unter `core/`.

**8.4 macOS/Tkinter: `NSWindow should only be instantiated on the main thread!`**  
Ursache: Tk‑Fenster werden nicht im Main‑Thread erstellt.  
Abhilfe: Headless ausführen:
```bash
export UFO_HEADLESS=1
python -m core.ufo_main
```

**8.5 Prüfung der aktiven venv**  
```bash
python - <<'PY'
import sys, sysconfig
print("exe :", sys.executable)
print("site:", sysconfig.get_paths()['purelib'])
PY
```
Der Pfad muss in `…/mathlab-thi-env/.venv/...` liegen.

**8.6 Stale Bytecode**  
Bei Struktur‑/Importwechseln Bytecode entfernen:
```bash
find thi/i/ki -name '__pycache__' -type d -exec rm -rf {} +
```

---

## 9. Hinweise zur Paket‑ und Build‑Struktur
- **Namespace‑Pakete (PEP 420):** In `src/core` liegt kein `__init__.py`.  
- **Setuptools‑Konfiguration pro Subprojekt (Auszug):**
  ```toml
  [tool.setuptools]
  package-dir = {"" = "src"}

  [tool.setuptools.packages.find]
  where = ["src"]
  include = ["core*"]
  namespaces = true
  ```
- **CLI‑Entry‑Point (ufo):**
  ```toml
  [project.scripts]
  ufo = "cli:main"
  ```

---

## 10. Headless‑Modus unter macOS (Tk)
- Setzen Sie `UFO_HEADLESS=1`, um jegliche GUI‑Erzeugung zu unterbinden.  
- Zweck: Stabile Ausführung ohne Tk‑Main‑Thread‑Abhängigkeiten.  
- Gilt für beide Startvarianten (`ufo` und `python -m core.ufo_main`).

---

## 11. Deinstallation / Neuaufsetzen
```bash
cd "$REPO"
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip setuptools wheel
python -m pip install -e "thi/i/ki/general/system"
python -m pip install -e "thi/i/ki/project/angel"
python -m pip install -e "thi/i/ki/project/ufo"
```

---

## 12. Versionierung und Changelogs
- Versionierung: SemVer (X.XX.XXX.XX) mit **Keep a Changelog**  
- Changelogs:
  - Gesamtprojekt: `praktikum/CHANGELOG.md`
  - UFO‑Modul: `thi/i/ki/project/ufo/CHANGELOG.md`
  - ANGEL‑Modul: `thi/i/ki/project/angel/CHANGELOG.md`
  - Utils: `thi/i/ki/general/system/CHANGELOG.md`

---

## 13. Lizenz
Interne Lehr‑ und Studienzwecke. Sofern nicht anders angegeben, keine Gewährleistung. Nutzung auf eigenes Risiko.