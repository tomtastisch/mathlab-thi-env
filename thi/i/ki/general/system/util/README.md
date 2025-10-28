# thi-general-utils

Typisierte Hilfsfunktionen für Konsolenprogramme.

## Features
- `read_input(prompt, typ, allowed=None, case_insensitive=True)`  
  Typsichere Eingabe mit Whitelist und argparse-basierter Bool-Konvertierung.
- `eps(value|exp10, *, dtype=None)`  
  Liefert \(10^{-n}\) mit automatischer Wahl `float32/float64`.

## Installation (VCS)
```bash
pip install "git+https://github.com/tomtastisch/praktikum@v0.1.0#subdirectory=thi/i/ki/general/system"