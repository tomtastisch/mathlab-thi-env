from __future__ import annotations

from util.geometry import GeometryUtil
from dataclasses import replace
from math import hypot
from typing import overload, final

from core.angel import angel as _angel
from .ufosim3_2_9q import UfoSim
from .cfg import AutopilotCfg, DEFAULT_CFG, UfoSimLike
from .profile.h_profil import HProfil as Nav

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
    return MathFunctions.fac(m, n)

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
@final
class _Autopilot:
    """
    Autopilot als Orchestrierungsschicht zur Steuerung des Ufos.
    Nutzt ZProfil/HProfil und die Konfigurationsfiles für
        z → hoch / runter
        h → Bewegung.
    """

    @staticmethod
    def _bremsberechnung(
            conf: AutopilotCfg,
            rest:float,
            use_heuristic: bool = False
    ) -> tuple[float, float]:
        """
        Ermittelt (slow_at, stop_at) für Reststrecke `rest`.
        Kinematik, sonst heuristischer Fallback.
        Garantien: stop_at ≤ slow_at ≤ rest; stop_at ≥ 0.
        """
        def _fallback() -> tuple[float, float]:
            # Heuristik-Fallback ohne Kinematik:
            # Beginne die Langsamphase bei 80 % der Reststrecke.
            # Begründung: ≥20 % Reserve für Feinanflug + Stop-Fenster verhindert Überschwingen
            # bei diskreten Geschwindigkeitsstufen; ersetzt wird dies durch eine kinematische
            # Berechnung, sobald v0/v1/a vorliegen.

            slow: float = max(conf.stop_z, max(0.8 * rest, rest - conf.slow_z_fallback))
            slow = min(rest, slow)

            stop: float = max(0.0, conf.stop_z)
            return slow, stop

        slow_at: float
        stop_at: float

        kin: tuple[float, float] | None = None

        if use_heuristic:
            try:
                slow_at: float = GeometryUtil.bremsbeginn(
                    s_total=rest,
                    stop_window=conf.stop_z,
                    v0=conf.v_cruise_kmh,  # ggf. an Cfg-Namen anpassen
                    v1=conf.v_slow_kmh,     # Zielgeschwindigkeit der Langsamphase
                    a=conf.a_slow_mps2,     # konstante negative Beschleunigung
                    v_unit="kmh",
                )
                stop_at: float = GeometryUtil.stoppen_vertikal(conf.stop_z)

                kin = slow_at, stop_at
            except ValueError:
                pass # Fallback durch Funktionsaufruf -> _fallback()

        return kin if kin is not None else _fallback()

    @overload
    @staticmethod
    def takeoff(sim: UfoSimLike, z: float) -> None: ...

    @overload
    @staticmethod
    def takeoff(sim: UfoSimLike, z: float, cfg: AutopilotCfg) -> None: ...

    @staticmethod
    def takeoff(
            sim: UfoSimLike,
            z: float,
            cfg: AutopilotCfg | None = None,
            use_heuristic: bool = False
    ) -> None:
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
            use_heuristic: Heuristik-Berechnung als Möglichkeit für realitätsnahe Berechnungen
        """
        conf: AutopilotCfg = replace(DEFAULT_CFG) if cfg is None else cfg

        rest: float = max(z - sim.get_z(), 0.0)
        if rest <= conf.stop_z:
            _set_neigung(sim, conf, conf.neigung_neutral_deg)

        else:
            _set_neigung(sim, conf, conf.neigung_steigen_deg)

            slow_at, stop_at = _Autopilot._bremsberechnung(
                conf=conf,
                rest=rest,
                use_heuristic=use_heuristic
            )

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

    @staticmethod
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
        sim.set_d(grad)

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

    @staticmethod
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

# ====================== EXPORTE ZUR SICHEREN TESTABDECKUNG =====================

def fly_to(
    sim: UfoSimLike | UfoSim,
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

    _Autopilot.takeoff(sim, z, conf)
    _Autopilot.cruise(sim, x, y, conf)
    _Autopilot.landing(sim, conf)

def takeoff(sim, z: float) -> None:
    _Autopilot.takeoff(sim, z, DEFAULT_CFG)

def cruise(sim, x: float, y: float) -> None:
    _Autopilot.cruise(sim, x, y, DEFAULT_CFG)

def landing(sim) -> None:
    _Autopilot.landing(sim, DEFAULT_CFG)