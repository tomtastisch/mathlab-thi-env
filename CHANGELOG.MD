# CHANGELOG – THI KI Praktikum

Dieses Dokument führt alle Änderungen am Gesamtprojekt auf und verweist bei Modul-Updates auf deren jeweilige CHANGELOG-Dateien.  
Format: **X.XX.XXX.XX**

---

## [2.00.002.01] – 2025-11-11
### Docs
- Einheiten vereinheitlicht ([m], [s], [°], [km/h]). Projekt-README zu Headless-Start ergänzt.

### Submodule
- `ufo v2.00.002.01`
- `angel v4.00.001.01`
- `thi-general-utils v1.01.000.01`

## [2.00.002.00] – 2025-11-11
### Added
- Headless-Ausführung als Workaround für macOS/Tk: `UFO_HEADLESS=1`.

### Changed
- Konsistente Fallback-Imports für Utilities (`util.evaluation` ↔ `system.util`).

## [2.00.001.00] – 2025-11-11
### Fixed
- `ImportError: attempted relative import with no known parent package` in `ufo` durch `cli:main` und konsistente Paketstruktur behoben.
- `ModuleNotFoundError: profile.h_profil` durch korrekten Paketpfad `core.profile.h_profil` behoben.

## [2.00.000.00] – 2025-11-11
### Added
- Neues Subprojekt `ufo` integriert. CLI-Entry-Point `ufo` via `src/cli.py` (`[project.scripts] ufo = "cli:main"`).

### Changed
- BREAKING: Umstellung auf Namespace-Pakete (PEP 420) für alle Submodule (`src/core` ohne `__init__.py`).
- Setuptools-Konfiguration vereinheitlicht:
  - `[tool.setuptools] package-dir = {"" = "src"}`
  - `[tool.setuptools.packages.find] where=["src"], include=["core*"], namespaces=true`
- Paket-relative Importe korrigiert:
  - `from .ufosim3_2_9q import UfoSim`
  - `from .profile.h_profil import HProfil as Nav`

---

## [1.02.001.03] – 2025-10-28
### Changed
- Migration auf Python 3.13  
- Konsolidierung der Git-basierten Paketstruktur  
- Modularisierung abgeschlossen: `angel` und `thi-general-utils` integriert  
- Finales Build-Setup mit `pip install -e`

### Submodule
- `thi-general-utils v1.01.000.01`  
- `angel v3.02.001.01`  
*(siehe jeweilige CHANGELOG-Dateien für Details)*

---

## [1.02.000.01] – 2025-10-25
### Changed
- Code- und Modulstruktur im Projektverzeichnis refaktoriert  
- Einführung modularer Namespace-Trennung `thi/i/ki/...`  
- Aufbau automatischer Importlogik für Submodule

---

## [1.01.000.01] – 2025-10-21
### Added
- Neues Subprojekt `thi-general-utils` angelegt  
- Initiale Tool-Module erstellt (`input_utils`, `type_utils`)

---

## [1.00.000.01] – 2025-10-15
### Added
- Subprojekt `angel` integriert  
- Grundlegende Funktion zur Winkelberechnung implementiert  
- Lokales Build- und Testsetup erstellt

---

## [0.01.000.01] – 2025-10-02
### Added
- Initiales Projekt „praktikum“ angelegt  
- Ordnerstruktur: `thi/i/ki/project` & `thi/i/ki/general/system`  
- Basis-Setup mit Python 3.12.9  
- Erste Dokumentationsrichtlinien und Formatvorgaben