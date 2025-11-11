# CHANGELOG – thi-general-utils

Dieses Dokument folgt **Keep a Changelog** und **Semantic Versioning (X.XX.XXX.XX)**.  
Das Paket bietet allgemeine System- und Utility-Komponenten zur Wiederverwendung.

---

## [1.02.000.01] – 2025-11-11
### Added
- `SimUtils` (Alias `NavOps`) – Utility-Klasse für das UFO‑Projekt: Warten auf Bedingungen, Richtungsnormalisierung (`dir_to_int`), profiliertes Annähern (`profiled_approach`).
- `InputUtils.bool_converter()` – öffentlicher Bool‑Konverter auf argparse‑Basis.

### Changed
- `input_utils.py` als finaler Namespace `InputUtils` (`@final`, `__slots__`, nicht instanziierbar); Logik unverändert. Wrapper `_contains()` und `read_input()` für Abwärtskompatibilität beibehalten.
- `type_utils.py` zu finalem Namespace `TypeUtils` mit `@final` und `__slots__`; Logik unverändert.
- `DATA_TYPES` nutzt den öffentlichen Bool‑Konverter.
- Paket‑API: `evaluation/__init__.py` exportiert `eps` nun über `TypeUtils.eps`.

### Fixed
- Import‑Kompatibilität: Legacy‑Symbol `eps` wieder verfügbar (`__all__` ergänzt, funktionsartiger Alias), verhindert 
  `ImportError` in abhängigen Modulen wie `angel`.

### Docs
- Klassen-Docstrings nach DIN 5008 für `InputUtils`; Paketdokumentation aktualisiert.

## [1.01.000.01] – 2025-10-28
### Added
- `read_input()` – generische Eingabe mit argparse-Bool-Parser
- `_contains()` – case-insensitive Collection-Abgleich
- `DATA_TYPES` – Mapping unterstützter Konvertierungen
- `eps()` – Präzisionsfunktion mit dynamischem Typ (float32 / float64)

### Changed
- Nutzung von argparse anstelle von distutils.strtobool  
- Verbesserte Fehlerbehandlung bei ungültigen Eingaben
- Integration in `angel` als Abhängigkeit

### Docs
- Vollständige Modulbeschreibung nach DIN 5008  
- README ergänzt, interne Docstrings vereinheitlicht

---

## [1.00.000.01] – 2025-10-21
### Added
- Projektstruktur und Grundmodule `input_utils.py` & `type_utils.py`
- Setup der `pyproject.toml`-Basis  
- Erste Integrationstests erfolgreich durchgeführt