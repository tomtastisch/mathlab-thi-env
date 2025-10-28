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