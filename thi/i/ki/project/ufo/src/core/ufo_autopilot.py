# src/core/ufo_autopilot.py
from __future__ import annotations
from math import hypot, factorial
from core.angel import angel as _angel
from util.cfg.simulation import AutopilotCfg, DEFAULT_CFG, NavOps as Nav, UfoSimLike


# ================== KOORDINATENSYSTEMRELEVANTE FUNKTIONEN ==================

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Euklidische Distanz zwischen zwei Punkten P1(x1, y1) und P2(x2, y2).

    Args:
        x1: x-Koordinate von P1.
        y1: y-Koordinate von P1.
        x2: x-Koordinate von P2.
        y2: y-Koordinate von P2.

    Returns:
        Float-Wert der Strecke |P1P2| in denselben Einheiten wie die Eingaben.

    Hinweise:
        Verwendet `math.hypot`, das numerisch stabil ist und Überläufe/Unterläufe
        gegenüber naiver Wurzelberechnung reduziert.

    Beispiele:
        >>> round(distance(0.0, 0.0, 3.0, 4.0), 6)
        5.0
        >>> distance(1.0, 2.0, 1.0, 2.0)
        0.0
    """
    return hypot(x2 - x1, y2 - y1)

def angle_q1(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Q1-Basiswinkel φ ∈ [0°, 90°] zwischen der +x-Achse durch P1 und der Strecke P1→P2.
    Reduziert auf den 1. Quadranten und delegiert die Berechnung an `core.angel.angel`.

    Args:
        x1: x-Koordinate von P1.
        y1: y-Koordinate von P1.
        x2: x-Koordinate von P2.
        y2: y-Koordinate von P2.

    Returns:
        φ in Grad im Bereich [0.0, 90.0].
    """

    delta_abs_x = abs(x2 - x1)
    delta_abs_y = abs(y2 - y1)

    return _angel(0.0, 0.0, delta_abs_x, delta_abs_y)

def angle(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Absolutwinkel φ ∈ [0°, 360°) von P1→P2 relativ zur +x-Achse (mathematisch positiv, CCW).

    Algorithmus:
        1) Δx, Δy berechnen.
        2) φ_q1 = angle_q1(0,0, |Δx|, |Δy|) liefert Basiswinkel im 1. Quadranten.
        3) Quadrant aus den Vorzeichen von Δx und Δy ableiten und Grundwinkel `base`
           bestimmen. Bei sx==sy addieren wir φ_q1, sonst subtrahieren wir φ_q1.
        4) Ergebnis nach 360° normalisieren.

    Args:
        x1: x-Koordinate von P1.
        y1: y-Koordinate von P1.
        x2: x-Koordinate von P2.
        y2: y-Koordinate von P2.

    Returns:
        φ in Grad im Bereich [0.0, 360.0).

    Konventionen:
        - 0° entlang +x, 90° entlang +y, 180° entlang −x, 270° entlang −y.
        - Eingabepunkte sollten verschieden sein; für P1==P2 ist der Winkel
          innerhalb der eingebetteten Funktion angel aus core.angel zu verwenden.
          Info: Aufgrund dieser Situation wurde angel.py aktualisiert (Argumentreduktionserweiterung)


    Beispiele:
        >>> angle(0.0, 0.0, 1.0, 0.0)
        0.0
        >>> angle(0.0, 0.0, 0.0, 1.0)
        90.0
        >>> angle(0.0, 0.0, -1.0, 0.0)
        180.0
        >>> angle(0.0, 0.0, 0.0, -1.0)
        270.0
        >>> angle(0.0, 0.0, 1.0, 1.0)
        45.0
        >>> angle(0.0, 0.0, -1.0, 1.0)
        135.0
        >>> angle(0.0, 0.0, -1.0, -1.0)
        225.0
        >>> angle(0.0, 0.0, 1.0, -1.0)
        315.0
    """
    delta_x: float = x2 - x1
    delta_y: float = y2 - y1
    circle: float = 360.0

    # Quadrant aus Vorzeichenpaar (sx, sy) bestimmen und Basiswinkel setzen
    phi = angle_q1(0.0, 0.0, abs(delta_x), abs(delta_y))

    # Quadranten logik zur Ableitung des Absolutwinkels aus φ_q1
    # Zweck:
    #   Aus den Vorzeichen von Δx und Δy wird der globale Winkel φ ∈ [0°, 360°)
    #   aus dem Basiswinkel φ_q1 ∈ [0°, 90°] hergeleitet.
    # Eingaben:
    #   delta_x, delta_y  – Differenzen der Koordinaten
    #   phi               – φ_q1 aus angle_q1 (1. Quadrant)
    #   circle            – Kreisumfang in Grad (360.0)
    # Verfahren:
    #   1) Vorzeichen bestimmen: sx := (Δx ≥ 0), sy := (Δy ≥ 0)
    #   2) Basiswinkel base setzen:
    #        Δx < 0            → +180°  (linke Halbebene)
    #        Δx ≥ 0 ∧ Δy < 0   → +360°  (4. Quadrant Wrap)
    #        sonst              → +0°
    #      Formal: base = 180°*(¬sx) + 360°*(sx ∧ ¬sy)
    #   3) Korrekturrichtung für φ:
    #        sx == sy  → +φ    (Quadranten 1 und 3)
    #        sonst     → −φ    (Quadranten 2 und 4)
    #   4) Normierung: (base ± φ) mod 360° ergibt φ ∈ [0°, 360°)

    sx, sy = (delta_x >= 0.0), (delta_y >= 0.0)
    base = (circle / 2) * (not sx) + circle * (sx and not sy)
    return (base + (phi if sx == sy else -phi)) % circle

def flight_distance(x1: float, y1: float, x2: float, y2: float, z: float) -> float:
    """
    Gesamtflugstrecke als Summe aus horizontaler Distanz und doppeltem Höhenweg.
    return 2.0 * abs(z) + distance(x1, y1, x2, y2)
    Definition:
        Strecke = hypot(x2−x1, y2−y1)  +  2·|z|

    Begründung:
        Start auf z=0 → Steigflug bis z → Sinkflug zurück auf 0. Vertikalkomponente
        addiert sich daher als 2·|z|. Die horizontale Komponente nutzt `math.hypot`
        für numerisch stabile euklidische Distanz im xy.

    Args:
        x1: x-Koordinate Startpunkt.
        y1: y-Koordinate Startpunkt.
        x2: x-Koordinate Zielpunkt.
        y2: y-Koordinate Zielpunkt.
        z:  Zieldistanz in z-Richtung (positiv aufwärts, negativ abwärts).

    Returns:
        Gesamtstrecke in gleichen Einheiten wie die Eingaben.

    Beispiele:
        >>> flight_distance(0,0,3,4, 10)
        5.0 + 20.0
        25.0
    """
    return hypot(x2 - x1, y2 - y1) + 2.0 * abs(z)

def format_flight_data(sim: UfoSimLike, w : int = 10) -> str:
    """
    Kompakte Telemetrie-Zeile mit fester Spaltenbreite.
    Ruft Zeit und Position einmalig ab (konsistente Snapshot‑Werte, weniger
    Method-Dispatch-Overhead) und formatiert sie mit fixer Breite.

    Args:
        sim: Simulator-Objekt mit `get_ftime/get_x/get_y/get_z`.
        w: Feldbreite für x, y und z in Zeichen. Standard 10.

    Returns:
        Zeichenkette im Format:
            "{t:>5.1f} s: {x:>w.1f} {y:>w.1f} {z:>w.1f}"
                – t in Sekunden, Breite 5, 1 Dezimalstelle, rechtsbündig.
                – x, y, z in Breite w, 1 Dezimalstelle, rechtsbündig.
    """
    t = sim.get_ftime()
    x = sim.get_x()
    y = sim.get_y()
    z = sim.get_z()

    # Anpassungen der Zahlen zur einheitlichen wiedergabe bei output
    # Standardisiert durch parameter w
    return f"{t:>5.1f} s: {x:>{w}.1f} {y:>{w}.1f} {z:>{w}.1f}"

def fac(n: int = 1, m: int = 1) -> int:
    """
    Zweck
    -----
    Liefert das ganzzahlige Produkt der aufeinanderfolgenden Zahlen im inklusiven Intervall [n, m].

    Definition
    ----------
    ∏_{k=n}^{m} k, mit Konvention: leeres Produkt = 1; 0 ∈ [n, m] ⇒ Ergebnis = 0.

    Parameter
    ---------
    n: int
        Untere Intervallgrenze.
    m: int
        Obere Intervallgrenze.

    Rückgabe
    --------
    int
        Produkt als ganze Zahl.

    Spezialfälle
    ------------
    - m < n → 1
    - n ≤ 0 ≤ m → 0

    Mathematische Grundlage
    -----------------------
    Für n ≥ 1: ∏_{k=n}^{m} k = m! / (n - 1)!.
    Für n ≤ m < 0: ∏_{k=n}^{m} k = (-1)^K · b! / (a - 1)!,
      mit a = -m, b = -n, K = m - n + 1.

    Begründung für Ganzzahldivision "//"
    ------------------------------------
    Die Quotienten sind per Definition ganzzahlig. "//" erzwingt exakte
    Integerarithmetik, vermeidet Float-Konvertierung und Rundungsfehler.

    Beispiele (Doctest)
    -------------------
    >>> fac(1, 5)
    120
    >>> fac(6, 2)
    1
    >>> fac(-2, 2)
    0
    >>> fac(-5, -2)
    120
    """
    if m < n:
        return 1

    if n <= 0 <= m:
        return 0

    if n > 0:
        # m! / (n - 1)! ist ganzzahlig → exakte Auswertung mit "//" ohne Float.
        return factorial(m) // factorial(n - 1)

    # n ≤ m < 0
    a, b = -m, -n          # 1 ≤ a ≤ b
    k = m - n + 1          # Anzahl Faktoren (für das Vorzeichen)

    # Betrag: b! / (a - 1)! ist ganzzahlig
    # Vorzeichen separat über (-1)^k.
    return (-1) ** k * (factorial(b) // factorial(a - 1))





# ── Eigentlicher Autopilot  Nachfolgend ─────────────────────────────────────────────────────────────────
def fly_to(sim: UfoSimLike, x: float, y: float, z: float, cfg: AutopilotCfg | None = None) -> None:
    cfg = DEFAULT_CFG if cfg is None else cfg
    takeoff(sim, z, cfg)
    cruise(sim, x, y, cfg)
    landing(sim, cfg)

def takeoff(sim: UfoSimLike, z: float, cfg: AutopilotCfg | None = None) -> None:
    cfg = DEFAULT_CFG if cfg is None else cfg
    sim.set_i(90)
    slow_at = max(cfg.stop_z, max(0.8 * z, z - cfg.slow_z_fallback))
    stop_at = cfg.stop_z
    Nav.profiled_approach(
        sim,
        remainder=lambda: max(z - sim.get_z(), 0.0),
        slow_at=slow_at,
        stop_at=stop_at,
        accel_dv=cfg.v_up,
        slow_dv=cfg.v_up_to_slow,
        cfg=cfg,
    )
    sim.set_i(0)

def cruise(sim: UfoSimLike, x: float, y: float, cfg: AutopilotCfg | None = None) -> None:
    cfg = DEFAULT_CFG if cfg is None else cfg
    sx, sy = sim.get_x(), sim.get_y()
    sim.set_d(Nav.dir_to_int(angle(sx, sy, x, y)))
    target_sum = sim.get_dist() + distance(sx, sy, x, y)
    Nav.profiled_approach(
        sim,
        remainder=lambda: max(target_sum - sim.get_dist(), 0.0),
        slow_at=cfg.slow_h,
        stop_at=cfg.stop_h,
        accel_dv=cfg.v_cruise,
        slow_dv=cfg.v_cruise_to_slow,
        cfg=cfg,
    )

def landing(sim: UfoSimLike, cfg: AutopilotCfg | None = None) -> None:
    cfg = DEFAULT_CFG if cfg is None else cfg
    sim.set_i(-90)
    Nav.profiled_approach(
        sim,
        remainder=lambda: max(sim.get_z() - 0.0, 0.0),
        slow_at=cfg.landing_slow_z,
        stop_at=0.0,
        accel_dv=cfg.v_up,
        slow_dv=cfg.v_up_to_slow,
        cfg=cfg,
    )