# math_utils.py
from __future__ import annotations

from typing import Final, final

__all__: Final[tuple[str, ...]] = ("MathFunctions", "math_functions")

@final
class MathFunctions:
    """
    Sammlung elementarer, projektweit nutzbarer Mathematik-Funktionen
    in Eigenregie zur zentralen Implementierung von mathematischen
    Hilfsfunktionen.
    """

    @staticmethod
    def fac(m: int = 1, n: int = 1) -> int:
        """
        Produkt ∏_{k=n}^{m} k ohne `math.factorial`.

        Konventionen:
            - m < n → 1 (leeres Produkt)
            - n ≤ 0 ≤ m → 0 (Faktor 0 enthalten)

        Schaltlogik:
            - Enthält das Intervall 0 → sofort 0.
            - Reines Negativintervall → in positives Intervall abbilden, Vorzeichen per Parität.
            - Sonst balanciertes Divide-&-Conquer ohne feste Grenzwerte.

        Beispiele:
            >>> MathFunctions.fac(5, 3)   # 3 · 4 · 5
            60
            >>> MathFunctions.fac(3, 5)   # m < n → 1
            1
            >>> MathFunctions.fac(2, -2)  # enthält 0 → 0
            0
            >>> MathFunctions.fac(-1, -3) # (-3)·(-2)·(-1) = -6
        """
        # Triviale Konventionen und dynamische Behandlung
        result: int
        if m < n:  # leeres Produkt
            result = 1

        elif n <= 0 <= m:  # 0 im Intervall
            result = 0

        elif m < 0:  # Reines Negativintervall: n ≤ m < 0
            a: int = -m            # kleinster positiver Betrag
            b: int = -n            # größter positiver Betrag
            width: int = m - n + 1 # Anzahl Faktoren im Intervall
            sign: int = -1 if (width & 1) else 1  # Vorzeichen aus Parität
            result = sign * MathFunctions._prod_interval(a, b)

        else:  # Reines Positivintervall
            result = MathFunctions._prod_interval(n, m)

        return result

    @staticmethod
    def _prod_interval(a: int, b: int) -> int:
        """
        Produkt der Folge a..b über balanciertes Divide-&-Conquer.

        Keine festen Schwellwerte: immer rekursiv balancieren. Liefert stabile
        Zwischenwertgrößen und gute Performance auch für große Intervalle.
        """
        result: int
        if a > b:
            result = 1
        else:
            result = MathFunctions._prod_dc(a, b)
        return result

    @staticmethod
    def _prod_dc(a: int, b: int) -> int:
        """
        Divide-and-Conquer-Produkt auf [a,b] (inkl.).
        """
        result: int
        if a == b:
            result = a

        else:
            mid: int = (a + b) // 2
            left: int = MathFunctions._prod_dc(a, mid)
            right: int = MathFunctions._prod_dc(mid + 1, b)
            result = left * right
        return result


math_functions: type[MathFunctions] = MathFunctions