from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Protocol

"""
Autopilot-Konfiguration und Simulator-Protokoll
==============================================

Zweck
- Zentrale Definition des Minimal-Protokolls `UfoSimLike` für den Simulator.
- Unveränderliche Konfiguration `AutopilotCfg` mit wohldefinierten Einheiten.

Normative Hinweise (DIN-orientiert)
- Einheiten in eckigen Klammern: Weg [m], Zeit [s], Winkel [°], Geschwindigkeit [km/h].
- Werte sind eindeutig, deterministisch und nebenwirkungsarm zu verwenden.
- Schwellwerte konsistent wählen (slow_at ≥ stop_at ≥ 0).
"""

class UfoSimLike(Protocol):
    """
    Mindest-Schnittstelle für den UFO-Simulator.

    - get_x/get_y/get_z()  → Position [m]
    - get_dist()           → Restweg/Zielentfernung [m]
    - get_ftime()          → verstrichene Simulationszeit [s]
    - set_d(deg)           → Kursrichtung [°] (0…359)
    - set_i(deg)           → Nick/Neigung [°]
    - request_delta_v(dv)  → Geschwindigkeitsänderung [km/h-Schritt]

    Nutzen dieses Aufbaus:
    - Aufrufer prüft Wertebereiche; Methoden blockieren nicht.
    """

    def get_x(self) -> float: ...
    def get_y(self) -> float: ...
    def get_z(self) -> float: ...
    def get_dist(self) -> float: ...
    def get_ftime(self) -> float: ...
    def set_d(self, deg: int) -> None: ...
    def set_i(self, deg: int) -> None: ...
    def request_delta_v(self, dv: int) -> None: ...


@dataclass(slots=True, frozen=True)
class AutopilotCfg:
    """
    Konstante Profilparameter mit festen Einheiten.

    Felder
    - slow_h [m]            : Distanz, ab der auf Langsamfahrt gewechselt wird.
    - stop_h [m]            : Horizontaler Stoppbereich.
    - slow_z_fallback [m]   : Vertikale Fallback-Schwelle (ohne Zielhöhe).
    - stop_z [m]            : Vertikaler Stoppbereich.
    - landing_slow_z [m]    : Abbremsbeginn vor Aufsetzen.
    - poll_s [s]            : Poll-Intervall für Wartebedingungen.
    - v_up [Δv km/h]        : 0 → 10.
    - v_up_to_slow [Δv km/h]: 10 → 1.
    - v_cruise [Δv km/h]    : 0 → 15.
    - v_cruise_to_slow [Δv km/h]: 15 → 1.
    - v_stop [Δv km/h]      : 1 → 0.

    Hinweise
    - Werte sind simulatorabhängig; keine Umrechnung im Code.
    - Unveränderlich (frozen) für deterministisches Verhalten.
    """

    slow_h: float = 4.0           # Bremsbeginn horizontal [m]
    stop_h: float = 0.05          # Stoppfenster horizontal [m]
    slow_z_fallback: float = 2.0  # z-2.0 als Fallback
    stop_z: float = 0.05          # Stoppfenster vertikal [m]
    landing_slow_z: float = 3.0   # vor Aufsetzen abbremsen
    poll_s: float = 0.01
    v_up: int = 10                # 0  → 10 km/h
    v_up_to_slow: int = -9        # 10 → 1 km/h
    v_cruise: int = 15            # 0  → 15 km/h
    v_cruise_to_slow: int = -14   # 15 → 1 km/h
    v_stop: int = -1              # 1  → 0 km/h


DEFAULT_CFG: Final[AutopilotCfg] = AutopilotCfg()


__all__ = ["UfoSimLike", "AutopilotCfg", "DEFAULT_CFG"]
