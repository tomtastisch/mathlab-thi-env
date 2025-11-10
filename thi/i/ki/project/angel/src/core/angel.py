# thi/i/ki/project/angel/src/core/angel.py
import math
import sys

from util.evaluation import read_input, eps as eval_eps

PI = math.pi
PI_HALBE = PI / 2

def angel(
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        genauigkeit: int = (sys.float_info.dig - 1)
) -> float:
    """
    Berechnet den Winkel φ in Grad zwischen der x-Achse durch P1 und der Strecke P1→P2.

    Args:
        x1: x-Koordinate von P1.
        y1: y-Koordinate von P1.
        x2: x-Koordinate von P2. Muss ≥ x1 sein.
        y2: y-Koordinate von P2. Muss ≥ y1 sein.
        genauigkeit: Dezimalstellen; ε = 10^(−genauigkeit). Standard: 14.

    Returns:
        Winkel φ in Grad im Bereich [0.0, 90.0].

    Raises:
        ValueError: Falls x2 < x1 oder y2 < y1.

    Notes:
        - Reihenentwicklung von arctan(t) mit Argumentreduktion.
        - Für |t| > 1: arctan(t) = π/2 − arctan(1/t).
        - Für t nahe 1: arctan(t) = π/4 + arctan((t−1)/(t+1)).
        - Sonderfälle: Δx = 0 ∧ Δy > 0 → 90.0; Δx = Δy = 0 → 0.0.
        - Für Produktion wäre math.atan2(Δy, Δx) ausreichend; hier bewusst nicht genutzt.
    """

    eps: float = eval_eps(genauigkeit)

    # Eingabevalidierung
    if x2 < x1 or y2 < y1:
        raise ValueError("Es muss gelten x2 >= x1 und y2 >= y1")

    # Berechnung der Ankatheten
    delta_x: float = x2 - x1
    delta_y: float = y2 - y1

    # Definition zur eindeutigen Typenzuweisung
    # → Keine zuweisung eines Wertes, da immer gesetzt wird in jedem Ablauf
    winkel_grad: float

    # Sonderfälle ohne notwendigkeit einer Division
    if delta_x == 0.0:
        winkel_grad = 0.0 if delta_y == 0.0 else 90.0

    # t = tan(φ)
    else:
        # tan(phi) = Gegenkathete / Ankathete = delta_y / delta_x
        tangens_wert: float = delta_y / delta_x
        basis_offset : float = 0.0
        schwellwert: float = math.sqrt(2.0) - 1.0

        # Argumentenreduktion (bessere Konvergenz)
        argument_invertiert: bool = False

        if abs(tangens_wert) > 1.0:
            tangens_wert = 1.0 / tangens_wert
            argument_invertiert = True

        # π/4-Argumentreduktion zur Beschleunigung der Reihe nahe t ≈ 1.
        # Schwelle: schwellwert = tan(π/8) = √2 − 1. Für schwellwert ≤ t ≤ 1 gilt
        # arctan(t) = π/4 + arctan((t−1)/(t+1)), wobei |(t−1)/(t+1)| ≤ √2 − 1 ⇒ schnelle Konvergenz.
        elif schwellwert <= tangens_wert <= 1.0:
            # π/4 als Basis-Offset für die spätere Rücktransformation
            basis_offset = PI_HALBE / 2
            # u = tan(φ−π/4); stabil (t+1 ≥ 1+schwellwert) und Konvergenz fördernd
            tangens_wert = (tangens_wert - 1.0) / (tangens_wert + 1.0)

        # Reihe: arctan(t) = Σ (-1)^k * t ^ (2k + 1) / (2k + 1)
        reihen_summe: float = 0.0
        aktueller_summand: float = tangens_wert
        reihen_index: int = 0
        tangens_quadrat: float = tangens_wert * tangens_wert

        while abs(aktueller_summand) > eps:

            reihen_summe += aktueller_summand

            # Mathematische Herleitung der Rekurrenz:
            koeffizient_aktuell: float = 2.0 * reihen_index + 1.0
            koeffizient_naechster: float = 2.0 * reihen_index + 3.0
            korrektur_faktor: float = koeffizient_aktuell / koeffizient_naechster
            aktueller_summand: float = -aktueller_summand * tangens_quadrat * korrektur_faktor

            reihen_index += 1

        winkel_bogenmass = (
            PI_HALBE - (basis_offset + reihen_summe)
            if argument_invertiert
            else (basis_offset + reihen_summe)
        )

        # Gradmaß
        winkel_grad = winkel_bogenmass * 180.0 / PI

    # Nachtrag zur verwendung als Methode: Return statement
    return round(winkel_grad, genauigkeit)


# - - - MAIN METHODE ZUM EINSTIEG / ALS STARTPUNKT - - -
if __name__ == "__main__":
    # Startpunkt für CLI-Aufruf
    print("Angel-Modul Ausführung")

    # Hauptlogik (bereits im Skript vorhanden gewesen)
    # → durch Umbau in Funktion hierher verschoben)
    x1point: float = read_input("x1: ", float)
    y1point: float = read_input("y1: ", float)
    x2point: float = read_input("x2: ", float)
    y2point: float = read_input("y2: ", float)

    # Aufruf der Funktion (angepasst als eigenständige Funktion)
    ergebnis : float = angel(x1point, y1point, x2point, y2point)

    # Anpassung der Ausgabe an die vorgegebene Genauigkeitsgrenze
    print(f"Berechneter Winkel: {ergebnis:.{6}f}")
