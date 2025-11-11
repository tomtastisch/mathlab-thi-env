# CHANGELOG – UFO-Modul

## [2.00.000.00] – 2025-11-11
### Added
- CLI-Entry-Point `ufo` via `src/cli.py` ([project.scripts] `ufo = "cli:main"`).

### Changed
- BREAKING: Umstellung auf Namespace-Pakete (PEP 420). `src/core` ohne `__init__.py`.
- Setuptools-Konfiguration vereinheitlicht:
  - `[tool.setuptools] package-dir = {"" = "src"}`
  - `[tool.setuptools.packages.find] where=["src"], include=["core*"], namespaces=true`
- Paket-relative Importe korrigiert:
  - `from .ufosim3_2_9q import UfoSim`
  - `from .profile.h_profil import HProfil as Nav`

## [2.00.001.00] – 2025-11-11
### Fixed
- `ImportError: attempted relative import with no known parent package` durch konsistente Paketstruktur und `cli:main` behoben.
- `ModuleNotFoundError: profile.h_profil` durch korrekten Paketpfad `core.profile.h_profil` behoben.

### Changed
- Fallback-Imports für Utilities robust implementiert: `util.evaluation` ↔ `system.util` (Kompatibilität zu `thi-general-utils`).

## [2.00.002.00] – 2025-11-11
### Added
- Headless-Ausführung via `UFO_HEADLESS=1` als Workaround für macOS/Tk (`NSWindow ... only on the main thread`).

## [2.00.002.01] – 2025-11-11
### Docs
- Docstrings aktualisiert; Einheiten vereinheitlicht ([m], [s], [°], [km/h]).

## [0.01.001.00] – 2025-11-11
### Added
- `src/core/ufo_autopilot.py`: Autopilot-Logik für horizontal/vertikal profiliertes Annähern (accel → slow → stop).
- `src/core/profile/h_profil.py`: Navigationsprofil (zweistufiges Annähern).
- `src/core/ufosim3_2_9q.py`: Lehrstuhl‑Simulator übernommen.

### Docs
- Erste DIN‑Docstrings in Autopilot und Profil.

## [0.01.000.01] – 2025-11-10
### Added
- Projektinitialisierung (src/core, CLI, __main__, Packaging)