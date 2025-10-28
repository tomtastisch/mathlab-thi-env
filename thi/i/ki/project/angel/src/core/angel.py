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

# ==============================================================================
# KONSTANTEN: Mathematische Konstanten und Grenzwerte
#   [PDF A2: |ak| < 1e-6] : genauigkeit
#   → Umsetzung der Genauigkeit mithilfe von eps
# ==============================================================================
import math
from util.evaluation import read_input, eps

genauigkeit: int = 6
eps: float = eps(genauigkeit)

PI = math.pi
PI_HALBE = PI / 2

# -------------------------  START DER EINGABESCHLEIFE -------------------------
# Dieser Abschnitt dient zur Eingabe der Koordinaten der beiden Punkte und zählt
# nicht zur eigentlichen Berechnung des Winkels. Vorgaben und einzuhaltende
# Regelungen bezüglich der zu verwendenden Inhalte sind erst nachfolgende zu
# diesem Abschnitt einzuhalten.
# ==============================================================================
# EINGABE: Koordinaten der beiden Punkte im kartesischen Koordinatensystem
#   [PDF A1: Ein-/Ausgabe; φ in Grad]
# ==============================================================================
# Eingabe der Koordinaten der jeweiligen Punkte
# Kontrollschleife zur Sicherstellung korrekter Eingabe nach Vorgabe
#   → Diese Schleife dient nicht der Berechnung des Winkels, sondern
#       lediglich der Kontrollierten, fehlerfreien Eingabe der Koordinaten.

# Eingabe der Koordinaten der beiden Punkte
# Direktes casten der Eingaben, welche durch
# Verwendung von float() gesichert und durch Verwendung
# einer Schleife vereinzelt abgefragt wird

# ==============================================================================
# VARIABLEN: Koordinaten der beiden Punkte
# Wiedergabe der einzelnen Koordinaten in der Ausgabe
# ==============================================================================

punkt1_x: float = read_input("x1: ", float)
punkt1_y: float = read_input("y1: ", float)
punkt2_x: float = read_input("x2: ", float)
punkt2_y: float = read_input("y2: ", float)

# Kontrollschleife zur Sicherstellung korrekter Eingaben nach Vorgabe
if punkt2_x < punkt1_x or punkt2_y < punkt1_y:
    raise ValueError("Es muss gelten x2 >= x1 und y2 >= y1")

# --------------------------  ENDE DER EINGABESCHLEIFE -------------------------

# ==============================================================================
# SCHRITT 1: Berechnung der Kathetenlängen (Koordinatendifferenzen)
#   [PDF A2: tan(φ)=b/a]
# ==============================================================================
# delta_x entspricht der Ankathete (horizontal, parallel zur x-Achse)
# delta_y entspricht der Gegenkathete (vertikal, parallel zur y-Achse)
delta_x: float = punkt2_x - punkt1_x
delta_y: float = punkt2_y - punkt1_y

# ==============================================================================
# SCHRITT 2: Sonderfall-Behandlung für vertikale Gerade
#   [PDF Tests: φ=90° Fall]
# ==============================================================================
# Division durch null wird vermieden

winkel_grad: float = 0.0

if delta_x == 0.0:
    # → Sonderfall: Δx = 0
    # → Identische Punkte (Δx = Δy = 0) → φ = 0°
    # → Sonst: vertikale Gerade (Δx = 0, Δy > 0) → φ = 90°
    winkel_grad = 0.0 if delta_y == 0.0 else 90.0

else:
    # ==========================================================================
    # SCHRITT 3: Berechnung des Tangens-Wertes
    #   [PDF A2: arctan-Fall]
    # ==========================================================================
    # tan(phi) = Gegenkathete / Ankathete = delta_y / delta_x
    tangens_wert: float = delta_y / delta_x

    # ==========================================================================
    # SCHRITT 4: Konvergenz-Optimierung durch Argument-Reduktion
    #   [PDF A2: π/2 − arctan(1/t)] → Transformation
    # ==========================================================================
    # Die Reihe konvergiert schnell für |t| ≤ 1, langsam für |t| > 1
    # Nutze Identität: arctan(t) = π/2 - arctan(1/t) für t >= 1
    # Dies transformiert grosse Argumente in kleine (bessere Konvergenz)
    argument_invertiert: bool = False
    if abs(tangens_wert) > 1.0:
        tangens_wert = 1.0 / tangens_wert
        argument_invertiert = True

    # ==========================================================================
    # SCHRITT 5: Initialisierung der Reihenentwicklung
    #   [PDF A2: effiziente Rekurrenz ak+1 = p·ak] → Tangens-Reihe
    # ==========================================================================
    # Taylor-Reihe: arctan(t) = Σ [(-1)^k · t^(2k + 1)] / (2k + 1)
    # Startwerte für iterative Berechnung
    reihen_summe: float = 0.0  # akkumulierte Partialsumme S_n
    aktueller_summand: float = tangens_wert  # Startwert a_0 = t^1/1 = t
    reihen_index: int = 0  # Laufindex k (zählt Summanden)
    tangens_quadrat: float = tangens_wert * tangens_wert  # t² (Effizienz: nur 1x berechnen)

    # ==========================================================================
    # SCHRITT 6: Iterative Berechnung der Reihe
    #   [PDF: genau eine Schleife]
    # ==========================================================================
    # Abbruch: wenn Beitrag des nächsten Summanden vernachlässigbar klein
    while abs(aktueller_summand) > eps:
        # ----------------------------------------------------------------------
        # 6.1: Addition des aktuellen Reihenglieds zur Partialsumme
        # ----------------------------------------------------------------------
        reihen_summe += aktueller_summand

        # ----------------------------------------------------------------------
        # 6.2: Berechnung des nächsten Summanden via Rekurrenzformel
        #   [PDF Hinweis p-Faktor] → Aktueller Summand
        # ----------------------------------------------------------------------
        # Mathematische Herleitung der Rekurrenz:
        #   a_k     = (-1)^k · t^(2k+1) / (2k+1)
        #   a_(k+1) = (-1)^(k+1) · t^(2k + 3) / (2k + 3)
        #           = (-1) · a_k · t² · (2k + 1) / (2k+3)
        #
        # Vorteil: Vermeidet wiederholte Potenzberechnung t^(2k+1)
        # und macht sich die Struktur aufeinanderfolgender Glieder zunutze
        koeffizient_aktuell: float = 2.0 * reihen_index + 1.0  # Nenner des aktuellen Glieds (2k+1)
        koeffizient_naechster: float = 2.0 * reihen_index + 3.0  # Nenner des nächsten Glieds (2k+3)
        korrektur_faktor: float = koeffizient_aktuell / koeffizient_naechster
        aktueller_summand: float = -aktueller_summand * tangens_quadrat * korrektur_faktor

        # ----------------------------------------------------------------------
        # 6.3: Inkrement des Laufindex (nächste Iteration)
        # ----------------------------------------------------------------------
        reihen_index += 1

    # ==========================================================================
    # SCHRITT 7: Rücktransformation bei invertiertem Argument
    #   [PDF A2: π/2 − arctan(1/t)] → Rücktransformation
    # ==========================================================================
    # Falls ursprünglich t >= 1 wurde t durch 1/t ersetzt
    # Rücktransformation: arctan(t_original) = π/2 - arctan(1/t_original)
    # Andernfalls: Ergebnis ist bereits arctan(t_original)
    if argument_invertiert:
        winkel_bogenmass = PI_HALBE - reihen_summe
    else:
        winkel_bogenmass = reihen_summe

    # ==========================================================================
    # SCHRITT 8: Einheitenumrechnung von Radiant (rad) zu Grad (°)
    #   [PDF A1: Ausgabe in Grad]
    # ==========================================================================
    # Umrechnungsfaktor: 180° = π rad → 1 rad = 180°/π
    winkel_grad = winkel_bogenmass * 180.0 / PI

# ==============================================================================
# AUSGABE:  Berechneter Winkel in Grad → Angepasste Ausgabe zur Darstellung
#           in der vorgegebenen Genauigkeitsgrenze
#
#   [PDF A2: |ak| < 1e-6]
# ==============================================================================
# Anpassung der Ausgabe an die vorgegebene Genauigkeitsgrenze
print(f"Winkel: {winkel_grad:.{genauigkeit}f}")

if __name__ == "__main__":
    # Startpunkt für CLI-Aufruf
    print("Starte Angel-Modul ...")
    # Hauptlogik (bereits im Skript vorhanden)