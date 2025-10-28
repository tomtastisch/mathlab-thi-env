# CHANGELOG – THI KI Praktikum

Dieses Dokument führt alle Änderungen am Gesamtprojekt auf und verweist bei Modul-Updates auf deren jeweilige CHANGELOG-Dateien.  
Format: **X.XX.XXX.XX**

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