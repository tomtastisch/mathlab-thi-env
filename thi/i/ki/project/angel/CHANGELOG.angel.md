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

## [3.03.000.01] – 2025-11-10
### Added
- Öffentliche Functions-API `angel(x1: float, y1: float, x2: float, y2: float, genauigkeit: int = 14) -> float`
- Konfigurierbare Ausgabepräzision über `genauigkeit` (Rundung im Return)

### Changed
- Argumentreduktion für schnelle Konvergenz:
  - `|t| > 1` ⇒ `arctan(t) = π/2 − arctan(1/t)`
  - `tan(π/8) ≤ t ≤ 1` ⇒ `arctan(t) = π/4 + arctan((t−1)/(t+1))`
- Eingabevalidierung mit `ValueError` bei `x2 < x1` oder `y2 < y1`
- CLI-Ausgabe standardisiert auf 14 Nachkommastellen

### Fixed
- Saubere Behandlung der Sonderfälle:
  - `Δx = 0 ∧ Δy > 0` ⇒ `90.0`
  - `Δx = Δy = 0` ⇒ `0.0`
- Stabilere Abbruchbedingung mittels `eps(genauigkeit)` aus Utils

### Refactor
- Rekurrenz für Reihen-Summanden statt wiederholter Potenzbildung
- Trennung von Berechnung (Funktion) und I/O (CLI-Block)

### Docs
- Docstring überarbeitet nach PEP 257, Hinweis auf `math.atan2` ergänzt

### Packaging
- Vorbereitung für Installation analog `thi-general-utils`  
  Empfehlung: Distributionsname `thi-angel` (Import weiterhin `from angel import angel`)  
- Optionale Deklaration als Abhängigkeit in `ufo` über `[project.dependencies]`

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