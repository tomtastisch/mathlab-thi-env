# CHANGELOG – thi-general-utils

Dieses Dokument folgt **Keep a Changelog** und **Semantic Versioning (X.XX.XXX.XX)**.  
Das Paket bietet allgemeine System- und Utility-Komponenten zur Wiederverwendung.

---

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