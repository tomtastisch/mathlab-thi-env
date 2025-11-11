"""
evaluation – Benutzerinteraktionseingaben

ZWECK
-----
Bündelt Funktionen zur validierten Eingabe in Konsolenanwendungen über das
Modul `input_utils`. Stellt die öffentlichen Schnittstellen des Pakets bereit.

INHALT
------
- `read_nat`       Eingabe natürlicher Zahlen
- `read_operator`  Eingabe von Operatoren innerhalb vordefinierter Optionen

MERKMALE
--------
- Zentraler Namensraum für Eingabefunktionen
- Kapselt Implementierungsdetails der Teilmodule
- Erweiterbar um weitere Eingabefunktionen

HINWEIS
-------
Dieses Modul exportiert ausschließlich die für Konsumenten vorgesehenen
Funktionen. Interne Hilfsfunktionen bleiben verborgen.
"""

from .input_utils import read_input
from .type_utils import TypeUtils

# Paket-API: bereitstellen eines funktionsartigen Aliases
eps = TypeUtils.eps

__all__ = ["read_input", "eps"]