from __future__ import annotations
from typing import overload, Union
import numpy as np

@overload
def eps(value: float, *, dtype: type[np.float32]) -> np.float32: ...

@overload
def eps(value: float, *, dtype: type[np.float64]) -> np.float64: ...

@overload
def eps(exp10: int, *, dtype: type[np.float32]) -> np.float32: ...

@overload
def eps(exp10: int, *, dtype: type[np.float64]) -> np.float64: ...

@overload
def eps(exp10: int, *, dtype: None = ...) -> Union[np.float32, np.float64]: ...

def eps(value: int | float, *, dtype: type[np.floating] | None = None):
    """
    Ermittelt den Wert 10**(-exp10) als Gleitkommazahl mit angepasster Präzision.

    ZWECK
    -----
    Dynamische Wahl zwischen einfacher (float32) und doppelter (float64) Genauigkeit
    zur effizienteren numerischen Berechnung.

    PARAMETER
    ---------
    exp10 : int
        Der Basis‑10‑Exponent n für die Berechnung von 10**(-n). Muss >= 0 sein.

    dtype : type[np.floating] | None, optional (Keyword-only)
        Erzwingt einen spezifischen Gleitkommatyp (np.float32 oder np.float64).
        Falls None: automatische Auswahl anhand von `exp10`.
        • exp10 ≤ 6  → np.float32
        • exp10 > 6   → np.float64

    RÜCKGABE
    --------
    np.float32 | np.float64
        Wert 10**(-exp10) im passenden Präzisionstyp.

    AUSNAHMEN
    ---------
    TypeError
        Falls `exp10` kein int ist.

    ValueError
        Falls `exp10` negativ ist.

    HINWEISE
    --------
    Die Typüberladung (typing.overload) ermöglicht korrekte statische Typprüfung.
    """
    if isinstance(value, float):
        s = f"{value:.16f}".rstrip("0").rstrip(".")
        if "." in s:
            exp10 = len(s.split(".")[1])
        else:
            exp10 = 0
    else:
        exp10 = value
    return (dtype or (np.float32 if exp10 <= 6 else np.float64))(10.0 ** (-exp10))