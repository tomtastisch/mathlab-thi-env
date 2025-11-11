from dataclasses import dataclass, field
from typing import Callable

@dataclass(slots=True)
class ProgressCheck:
    """
    Fortschrittsprüfung für Annäherungsprozesse.

    Zweck:
        Bei Aufruf liefert das Objekt (Callable) True, wenn das Ziel erreicht ist
        oder keine nennenswerte Annäherung mehr messbar ist.

    Parameter:
        rest: Funktion, die den aktuellen Restwert (z.B.: Restweg) liefert.
        ziel: Zielschwelle; bei rest() ≤ ziel gilt „erreicht“.
        eps_abs: minimale absolute Verbesserung pro Messung.
        eps_rel: minimale relative Verbesserung pro Messung
                 (bezogen auf den letzten Restwert).

    Rückgabe (__call__):
        True = „fertig“ (Ziel erreicht oder Stagnation), sonst False.
    """

    rest: Callable[[], float]
    ziel: float
    eps_abs: float = 1e-3
    eps_rel: float = 1e-3
    rest_alt: float = field(init=False)

    def __post_init__(self) -> None:
        """Initialisiert den Vergleichswert aus der ersten Messung."""
        self.rest_alt = self.rest()

    def __call__(self) -> bool:
        """
        Prüft den Zustand.
        True, wenn `rest() ≤ ziel` oder der Fortschritt kleiner ist als
        max(eps_abs, eps_rel · max(rest_alt, 1.0)).
        """
        rest_neu = self.rest()
        # Mindestfortschritt: absolut oder relativ zum letzten Restwert
        min_fortschritt = max(self.eps_abs, self.eps_rel * max(self.rest_alt, 1.0))
        stagniert = (self.rest_alt - rest_neu) <= min_fortschritt
        self.rest_alt = rest_neu
        return (rest_neu <= self.ziel) or stagniert