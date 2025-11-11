from __future__ import annotations
from typing import overload, final
import numpy as np

__all__ = ["TypeUtils"]

@final
class TypeUtils:
    """
    Numerik‑Utilities
    =================

    Zweck
    -----
    Präzisionsgerechte Hilfsfunktionen für numerische Berechnungen.

    Gestaltungsregeln
    -----------------
    - Reiner Namespace: keine Instanzen, nur `@staticmethod`‑Methoden.
    - Rückgaben sind NumPy‑Skalare mit wohldefiniertem Dtype.
    - Überladungen sichern die statische Typprüfung.
    """

    __slots__ = ()

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        raise TypeError("TypeUtils ist ein reiner Namespace und nicht instanziierbar")

    # ── Überladungen für präzise Rückgabetypen ────────────────────────────────
    @overload
    @staticmethod
    def eps(value: float, *, dtype: type[np.float32]) -> np.float32: ...

    @overload
    @staticmethod
    def eps(value: float, *, dtype: type[np.float64]) -> np.float64: ...

    @overload
    @staticmethod
    def eps(exp10: int, *, dtype: type[np.float32]) -> np.float32: ...

    @overload
    @staticmethod
    def eps(exp10: int, *, dtype: type[np.float64]) -> np.float64: ...

    @overload
    @staticmethod
    def eps(exp10: int, *, dtype: None = ...) -> np.float64 | np.float32: ...

    @staticmethod
    def eps(value: int | float, *, dtype: type[np.floating] | None = None) -> np.floating:
        """
        Liefert 10**(-n) als NumPy‑Skalar mit passender Präzision.

        Parameter
        ---------
        value : int | float
            Entweder der Basis‑10‑Exponent `n` (int, n ≥ 0) oder ein
            Dezimalwert, dessen Nachkommastellenzahl `n` bestimmt.
        dtype : type[np.floating] | None, optional
            Erzwingt einen Ziel‑Dtype (np.float32 oder np.float64). Bei None:
            automatische Wahl auf Basis von `n` (≤6 → float32, sonst float64).

        Rückgabe
        --------
        np.float32 | np.float64
            Wert 10**(-n) im passenden Präzisionstyp.

        Ausnahmen
        ---------
        TypeError
            Falls `value` weder int noch float ist.
        ValueError
            Falls `n < 0` (bei int) oder `value` NaN/±Inf ist.
        """
        # Bestimme n
        if isinstance(value, int):
            n = value
            if n < 0:
                raise ValueError("exp10 darf nicht negativ sein")
        elif isinstance(value, float):
            if not np.isfinite(value):
                raise ValueError("value muss endlich sein")
            # Nachkommastellen anhand einer stabilen Dezimaldarstellung bestimmen
            s = f"{value:.16f}".rstrip("0").rstrip(".")
            n = len(s.split(".")[1]) if "." in s else 0
        else:
            raise TypeError("value muss int oder float sein")

        target_dtype: type[np.floating]
        if dtype is not None:
            target_dtype = dtype
        else:
            target_dtype = np.float32 if n <= 6 else np.float64

        return target_dtype(10.0 ** (-n))