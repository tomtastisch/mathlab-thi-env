# CHANGELOG – Angel-Modul

Dieses Dokument folgt den Konventionen von **Keep a Changelog** und **Semantic Versioning** im Format **X.XX.XXX.XX**.

Kategorien:
- **Added** – neue Funktionen
- **Changed** – Änderungen ohne Bugfix-Charakter
- **Fixed** – Fehlerbehebungen
- **Removed** – entfernte Elemente
- **Docs** – Dokumentationsänderungen
- **Refactor** – interne Restrukturierungen

---

## [3.02.001.01] – 2025-10-28
### Changed
- Anpassung an `thi-general-utils v1.01.000.01` (argparse-basierte Eingabeverarbeitung)
- Integration mit `pyproject.toml` für Git-basiertes Packaging
- Migration auf Python 3.13  
- Strukturangleichung für `pip install -e`-Entwicklung

### Docs
- README, Projekt- und Moduldokumentation überarbeitet
- Struktur und Formatierung DIN-konform ergänzt

---

## [3.01.000.01] – 2025-10-27
### Added
- Migration der Eingabe-Logik auf `read_input()` aus Utils-Paket  
- Nutzung von `eps()` für konfigurierbare Genauigkeit
- Konfigurierbare Case-Sensitivity beim Bool-Parsing

### Docs
- Vollständige Neufassung des Modul-Docstrings nach PEP 257

---

## [2.02.001.01] – 2025-10-25
### Changed
- Schwellwertkorrektur bei `abs(tangens_wert)` → `> 1.0`
- Verbesserte Berechnungskonvergenz  
- Leichte Performance-Optimierung

### Docs
- Formulierungen im Dokumentationsblock präzisiert

---

## [2.01.000.01] – 2025-10-24
### Fixed
- Codeformatierung und fehlerhafte Klammern korrigiert
- Prüfbedingungen im Delta-Block bereinigt

---

## [2.00.000.01] – 2025-10-23
### Removed
- Entfernte alte Imports und redundante Hilfsfunktionen
### Changed
- Nutzung von `math.pi` statt statischer Konstanten
- Stabilisierung der Eingabe durch kontrollierte Schleifen
- Modul aus Multi-Language-Setup extrahiert

---

## [1.03.000.01] – 2025-10-21
### Docs
- Aufgabenbeschreibung ergänzt
### Changed
- Caching für Potenzberechnung integriert
- Variablennamen vereinheitlicht

---

## [1.02.000.01] – 2025-10-18
### Changed
- Nutzung von `abs()` für präzisere Abbruchkriterien
- Scope-Reduktion unnötiger Variablen
### Docs
- Kommentare erweitert

---

## [1.01.000.01] – 2025-10-17
### Changed
- Entfernung externer `math.*`-Funktionen zugunsten Eigenlogik
- Strukturelle Code-Aufteilung nach logischen Blöcken

---

## [1.00.000.01] – 2025-10-15
### Added
- Erste Version der Arkustangens-Winkelberechnung  
- Implementierung des mathematischen Grundverfahrens  
- Konsolenbasierte Eingabeprüfung