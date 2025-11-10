# thi/i/ki/project/angel/src/core/angel.py

"""
Winkelberechnung mittels Arkustangens-Reihenentwicklung
========================================================

PROGRAMMBESCHREIBUNG
--------------------
Berechnung des Winkels φ [°] zwischen zwei Halbgeraden im kartesischen
Koordinatensystem mittels Taylor-Reihe des Arkustangens.

AUFGABENSTELLUNG
----------------
Gegeben:  P1(x1, y1), P2(x2, y2) mit x2 ≥ x1, y2 ≥ y1
Gesucht:  Winkel φ ∈ [0°, 90°] zwischen h1 (x-Achsenparallele) und h2 (P1→P2)

MATHEMATISCHES VERFAHREN
-------------------------
1. Tangens: tan(φ) = Δy / Δx
2. Arkustangens-Reihe (Taylor-Entwicklung, x = 0):
   arctan(t) = Σ(k=0→∞) [(-1)^k · t^(2k + 1)] / (2k + 1)
             = t - t³/3 + t⁵/5 - t⁷/7 + ...
3. Konvergenzoptimierung für |t| ≥ 1:
   arctan(t) = π/2 - arctan(1/t)
4. Abbruchkriterium: |a_k| < 10^(-6)
5. Umrechnung: φ[°] = φ[rad] · 180/π

IMPLEMENTIERUNGSVORGABEN
-------------------------
• Keine Funktionsdefinitionen (def)
• Exakt eine Schleife (nur für Reihenberechnung)
• Keine Bibliotheksfunktionen (math.atan, math.acos, etc.)
• Erlaubte Operationen: +, -, *, /, math.sqrt
• Namenskonvention: kleinbuchstaben_mit_unterstrich

SONDERFÄLLE
-----------
• Δx = 0 ∧ Δy > 0:  φ = 90°
• Δx = 0 ∧ Δy = 0:  φ = 0° (identische Punkte)

ENTWICKLUNG
-----------
Autor:    Tomtastisch
Version:  3.0

HINWEIS ZU KI-UNTERSTÜTZUNG
----------------------------
Die Programmdokumentation (Kommentare, Docstring) wurde mit Unterstützung
eines KI-Systems (Claude Agent) erstellt. Die algorithmische Implementierung
erfolgte eigenständig.
"""

# Mathematische- und Systemseitige Bibliotheken
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
        x1 (float): x-Koordinate von P1.
        y1 (float): y-Koordinate von P1.
        x2 (float): x-Koordinate von P2. Muss ≥ x1 sein.
        y2 (float): y-Koordinate von P2. Muss ≥ y1 sein.
        genauigkeit (int, optional): Dezimalstellen für ε = 10^(-genauigkeit).
            Standard ist (sys.float_info.dig − 1) → 14 Nachkommastellen.

    Returns:
        float: Winkel φ in Grad im Bereich [0.0, 90.0].

    Raises:
        ValueError: Falls x2 < x1 oder y2 < y1.

    Hinweise:
        - Eine Schleife für die Reihenentwicklung; Argumentreduktion für |t| ≥ 1.
        - Sonderfälle: Δx = 0 ∧ Δy > 0 → 90.0; Δx = Δy = 0 → 0.0.
    """

    eps: float = eval_eps(genauigkeit)

    # Kontrollschleife zur Sicherstellung korrekter Eingaben nach Vorgabe
    if x2 < x1 or y2 < y1:
        raise ValueError("Es muss gelten x2 >= x1 und y2 >= y1")

    # delta_x entspricht der Ankathete (horizontal, parallel zur x-Achse)
    # delta_y entspricht der Gegenkathete (vertikal, parallel zur y-Achse)
    delta_x: float = x2 - x1
    delta_y: float = y2 - y1

    # Definition zur eindeutigen Typenzuweisung
    # → Keine zuweisung eines Wertes, da immer gesetzt wird in jedem Ablauf
    winkel_grad: float

    # Division durch null wird vermieden.
    if delta_x == 0.0:
        # → Sonderfall: Δx = 0
        # → Identische Punkte (Δx = Δy = 0) → φ = 0°
        # → Sonst: vertikale Gerade (Δx = 0, Δy > 0) → φ = 90°
        winkel_grad = 0.0 if delta_y == 0.0 else 90.0

    else:
        # tan(phi) = Gegenkathete / Ankathete = delta_y / delta_x
        tangens_wert: float = delta_y / delta_x
        basis_offset : float = 0.0
        schwelle: float = math.sqrt(2.0) - 1.0

        # Die Reihe konvergiert schnell für |t| ≤ 1, langsam für |t| > 1
        # Nutze Identität: arctan(t) = π/2 - arctan(1/t) für t >= 1
        # Dies transformiert grosse Argumente in kleine (bessere Konvergenz)
        argument_invertiert: bool = False

        if abs(tangens_wert) > 1.0:
            tangens_wert = 1.0 / tangens_wert
            argument_invertiert = True


        # π/4-Argumentreduktion zur Beschleunigung der Reihe nahe t≈1.
        # Schwelle: schwelle = tan(π/8) = √2 − 1. Für schwelle ≤ t ≤ 1 gilt
        # arctan(t) = π/4 + arctan((t−1)/(t+1)), wobei |(t−1)/(t+1)| ≤ √2 − 1 ⇒ schnelle Konvergenz.
        elif schwelle <= tangens_wert <= 1.0:
            basis_offset = PI_HALBE / 2  # π/4 als Basis-Offset für die spätere Rücktransformation
            # u = tan(φ−π/4); stabil (t+1 ≥ 1+schwelle) und konvergenzfördernd
            tangens_wert = (tangens_wert - 1.0) / (tangens_wert + 1.0)

        # Taylor-Reihe: arctan(t) = Σ [(-1)^k · t^(2k + 1)] / (2k + 1)
        # Startwerte für iterative Berechnung
        reihen_summe: float = 0.0  # akkumulierte Partialsumme S_n
        aktueller_summand: float = tangens_wert  # Startwert a_0 = t^1/1 = t
        reihen_index: int = 0  # Laufindex k (zählt Summanden)
        tangens_quadrat: float = tangens_wert * tangens_wert  # t² (Effizienz: nur 1x berechnen)

        # Abbruch: wenn Beitrag des nächsten Summanden vernachlässigbar klein ist
        while abs(aktueller_summand) > eps:

            reihen_summe += aktueller_summand

            # Mathematische Herleitung der Rekurrenz:
            #   a_k     = (-1)^k · t^(2k+1) / (2k+1)
            #   a_(k+1) = (-1)^(k+1) · t^(2k + 3) / (2k + 3)
            #           = (-1) · a_k · t² · (2k + 1) / (2k + 3)
            #
            # Vorteil: Vermeidet wiederholte Potenzberechnung t^(2k + 1)
            # und macht sich die Struktur aufeinanderfolgender Glieder zunutze
            koeffizient_aktuell: float = 2.0 * reihen_index + 1.0  # Nenner des aktuellen Glieds (2k + 1)
            koeffizient_naechster: float = 2.0 * reihen_index + 3.0  # Nenner des nächsten Glieds (2k + 3)
            korrektur_faktor: float = koeffizient_aktuell / koeffizient_naechster
            aktueller_summand: float = -aktueller_summand * tangens_quadrat * korrektur_faktor

            reihen_index += 1

        winkel_bogenmass = (PI_HALBE - (basis_offset + reihen_summe)) \
            if argument_invertiert else (basis_offset + reihen_summe)

        # Umrechnungsfaktor: 180° = π rad → 1 rad = 180°/π
        winkel_grad = winkel_bogenmass * 180.0 / PI

    # Anpassung der Ausgabe an die vorgegebene Genauigkeitsgrenze
    print(f"Berechneter Winkel: {winkel_grad:.{genauigkeit}f}")

    # Nachtrag zur verwendung als Methode: Return statement
    return winkel_grad


# - - - MAIN METHODE ZUM EINSTIEG / ALS STARTPUNKT - - -
if __name__ == "__main__":
    # Startpunkt für CLI-Aufruf
    print("Angel-Modul Ausführung")
    # Hauptlogik (bereits im Skript vorhanden)
    x1point: float = read_input("x1: ", float)
    y1point: float = read_input("y1: ", float)
    x2point: float = read_input("x2: ", float)
    y2point: float = read_input("y2: ", float)

    # Aufruf der Funktion (angepasst als eigenständige Funktion)
    angel(x1point, y1point, x2point, y2point)
