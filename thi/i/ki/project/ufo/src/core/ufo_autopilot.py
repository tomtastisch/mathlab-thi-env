from __future__ import annotations

"""
UFO‑Autopilot: Geometrie, Profilsteuerung und High‑Level‑Manöver.

Inhalt
- Geometrie: distance, angle_q1, angle
- Telemetrie/Hilfen: flight_distance, format_flight_data, fac
- Sicherheitsfunktion: _begrenze_neigung_deg (Inklinationsgrenzen)
- Manöver: takeoff, cruise, landing, fly_to

Konventionen
- Winkel [°], Wege [m], Zeiten [s], Geschwindigkeiten [km/h] (Sim‑Signale)
- Funktionen deterministisch, ohne Seiteneffekte
"""

from dataclasses import replace
from math import hypot, factorial
from typing import overload

from core.angel import angel as _angel
from .cfg import AutopilotCfg, DEFAULT_CFG, UfoSimLike
from .profile.h_profil import HProfil as Nav

# ====================== KOORDINATENSYSTEMRELEVANTE FUNKTIONEN ======================

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Euklidische Distanz |P1P2| im xy‑Plan.

    Args:
        x1: x‑Koordinate von P1.
        y1: y‑Koordinate von P1.
        x2: x‑Koordinate von P2.
        y2: y‑Koordinate von P2.
    Returns:
        Distanz in den Einheiten der Eingaben.
    """
    return hypot(x2 - x1, y2 - y1)

def angle_q1(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Basiswinkel φ ∈ [0°, 90°] für |Δx|, |Δy| via `core.angel.angel`.

    Args:
        x1: x‑Koordinate von P1.
        y1: y‑Koordinate von P1.
        x2: x‑Koordinate von P2.
        y2: y‑Koordinate von P2.
    Returns:
        φ in Grad im 1. Quadranten.
    """
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return _angel(0.0, 0.0, dx, dy)


def angle(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Absolutwinkel φ ∈ [0°, 360°) von P1→P2 relativ +x.

    Verfahren:
        φ_q1 = angle_q1(|Δx|, |Δy|); Quadrant aus Vorzeichen von Δx, Δy;
        Basiswinkel setzen (180° bei Δx<0, 360° bei Δx≥0∧Δy<0); Korrektur ±φ_q1; mod 360.

    Args:
        x1: x‑Koordinate von P1.
        y1: y‑Koordinate von P1.
        x2: x‑Koordinate von P2.
        y2: y‑Koordinate von P2.
    Returns:
        φ in Grad im Bereich [0.0, 360.0).
    """
    dx = x2 - x1
    dy = y2 - y1

    circle = 360.0
    phi = _angel(0.0, 0.0, abs(dx), abs(dy))

    # Quadrant bestimmen und globalen Winkel ableiten
    sx, sy = (dx >= 0.0), (dy >= 0.0)
    base = (circle / 2.0) * (not sx) + circle * (sx and not sy)
    return (base + (phi if sx == sy else -phi)) % circle


def flight_distance(x1: float, y1: float, x2: float, y2: float, z: float) -> float:
    """
    Gesamtstrecke: horizontale Distanz + doppelter Höhenweg.

    Definition: hypot(Δx, Δy) + 2·|z|.

    Args:
        x1: x‑Koordinate Startpunkt.
        y1: y‑Koordinate Startpunkt.
        x2: x‑Koordinate Zielpunkt.
        y2: y‑Koordinate Zielpunkt.
        z:  Zielhöhe [m] (positiv aufwärts, negativ abwärts).
    Returns:
        Gesamtstrecke in Einheiten der Eingaben.
    """
    return hypot(x2 - x1, y2 - y1) + 2.0 * abs(z)


def format_flight_data(sim: UfoSimLike, w: int = 10) -> str:
    """
    Formatiert eine Telemetrie‑Zeile.

    Format: "{t:>5.1f} s: {x:>w.1f} {y:>w.1f} {z:>w.1f}".

    Args:
        sim: Simulator mit `get_ftime/get_x/get_y/get_z`.
        w: Feldbreite für x, y, z.
    Returns:
        Formatierte Zeile.
    """
    t = sim.get_ftime()
    x = sim.get_x()
    y = sim.get_y()
    z = sim.get_z()

    return f"{t:>5.1f} s: {x:>{w}.1f} {y:>{w}.1f} {z:>{w}.1f}"

def fac(m: int = 1, n: int = 1) -> int:
    """
    Produkt ∏_{k=n}^{m} k.

    Konventionen: m < n → 1, n ≤ 0 ≤ m → 0.
    """

    i_grenze: int = 1
    match True:
        case _ if m < n:
            i_grenze = 1

        case _ if n <= 0 <= m:
            i_grenze = 0

        case _ if n > 0:
            i_grenze = factorial(m) // factorial(n - 1)

        case _:
            # n ≤ m < 0
            a, b = -m, -n  # 1 ≤ a ≤ b
            k = m - n + 1
            i_grenze = (-1) ** k * (factorial(b) // factorial(a - 1))

    return i_grenze

# ================ SICHERHEITSFUNKTIONEN DETERMINISTISCHE SICHERSTELLUNG ================

def _begrenze_neigung_deg(cfg: AutopilotCfg, deg: int) -> int:
    """
    Begrenzt `deg` auf [cfg.neigung_sinken_deg, cfg.neigung_steigen_deg].

    Args:
        cfg: Konfiguration mit Grenzwerten.
        deg: gewünschter Winkel [°].

    Returns:
        Geklemmter Winkel [°].

    """
    return max(cfg.neigung_sinken_deg, min(cfg.neigung_steigen_deg, deg))

def _set_neigung(
        sim: UfoSimLike,
        cfg: AutopilotCfg,
        neigung_deg: int
) -> int:
    """
    Klemmt `neigung_deg` auf die in `cfg` erlaubten Grenzen und setzt sie am Sim.
    Returns: tatsächlich gesetzter Winkel [°].
    """
    wert = _begrenze_neigung_deg(cfg, neigung_deg)
    sim.set_i(wert)
    return wert

# ====================== AUTOPILOT ANGEHÖRIGE STANDARD FUNKTIONEN =====================

@overload
def takeoff(sim: UfoSimLike, z: float) -> None: ...
@overload
def takeoff(sim: UfoSimLike, z: float, cfg: AutopilotCfg) -> None: ...

def takeoff(sim: UfoSimLike, z: float, cfg: AutopilotCfg | None = None) -> None:
    """
    Abheben: Steigflug bis Zielhöhe `z` mit zweistufigem Profil.

    Ablauf:
        Inklination setzen
        → kinematischen Umschaltpunkt bestimmen
        → schrittweise bis `z` mit Langsam-/Stop‑Fenstern
        → Inklination neutralisieren.

    Args:
        sim: Simulator.
        z: Zielhöhe [m].
        cfg: Konfiguration.
    """
    conf: AutopilotCfg = replace(DEFAULT_CFG) if cfg is None else cfg

    rest: float = max(z - sim.get_z(), 0.0)
    if rest <= conf.stop_z:
        _set_neigung(sim, conf, conf.neigung_neutral_deg)

    else:
        _set_neigung(sim, conf, conf.neigung_steigen_deg)

        # Heuristik-Fallback ohne Kinematik:
        # Beginne die Langsamphase bei 80 % der Reststrecke.
        # Begründung: ≥20 % Reserve für Feinanflug + Stop-Fenster verhindert Überschwingen
        # bei diskreten Geschwindigkeitsstufen; ersetzt wird dies durch eine kinematische
        # Berechnung, sobald v0/v1/a vorliegen.
        slow_at: float = max(conf.stop_z, max(0.8 * rest, rest - conf.slow_z_fallback))
        stop_at: float = conf.stop_z

        Nav.schrittweise_bis(
            sim,
            lambda: max(z - sim.get_z(), 0.0),
            slow_at,
            stop_at,
            conf.v_up,
            conf.v_up_to_slow,
            conf,
        )

        _set_neigung(sim, conf, conf.neigung_neutral_deg)


def cruise(
    sim: UfoSimLike,
    x: float,
    y: float,
    cfg: AutopilotCfg | None = None,
) -> None:
    """
    Streckenflug zu (x, y) mit zweistufiger Geschwindigkeitsführung.

    Ablauf:
        Kurs aus Absolutwinkel setzen → Ziel‑Gesamtdistanz bestimmen → schrittweise bis Ziel.

    Args:
        sim: Simulator.
        x: Ziel‑x [m].
        y: Ziel‑y [m].
        cfg: Konfiguration.
    """
    conf = replace(DEFAULT_CFG) if cfg is None else cfg

    sx = sim.get_x()
    sy = sim.get_y()

    a: float = angle(sx, sy, x, y)
    grad: int = Nav.richtung_als_int(a)
    sim.set_kurs(grad)

    distanz: float = sim.get_dist() + distance(sx, sy, x, y)

    Nav.schrittweise_bis(
        sim,
        lambda: max(distanz - sim.get_dist(), 0.0),
        conf.slow_h,
        conf.stop_h,
        conf.v_cruise,
        conf.v_cruise_to_slow,
        conf,
    )


def landing(
        sim: UfoSimLike,
        cfg: AutopilotCfg | None = None
) -> None:
    """
    Landen: Sinkflug auf z = 0 mit zweistufigem Profil.

    Args:
        sim: Simulator.
        cfg: Konfiguration.
    """
    conf = replace(DEFAULT_CFG) if cfg is None else cfg

    _set_neigung(sim, conf, conf.neigung_sinken_deg)

    Nav.schrittweise_bis(
        sim,
        lambda: max(sim.get_z() - 0.0, 0.0),
        conf.landing_slow_z,
        0.0,
        conf.v_up,
        conf.v_up_to_slow,
        conf,
    )

    _set_neigung(sim, conf, conf.neigung_neutral_deg)


def fly_to(
    sim: UfoSimLike,
    x: float,
    y: float,
    z: float,
    cfg: AutopilotCfg | None = None,
) -> None:
    """
    Kombiniertes Manöver: takeoff → cruise → landing.

    Args:
        sim: Simulator.
        x: Ziel ‑ x [m].
        y: Ziel ‑ y [m].
        z: Zielhöhe [m].
        cfg: Konfiguration.
    """
    conf = replace(DEFAULT_CFG) if cfg is None else cfg

    takeoff(sim, z, conf)
    cruise(sim, x, y, conf)
    landing(sim, conf)
