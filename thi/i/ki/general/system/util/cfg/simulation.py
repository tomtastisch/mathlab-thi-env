"""
Autopilot‑Hilfsroutinen für die UFO‑Simulation
=============================================

Zweck
- Definition des Minimal‑Protokolls `UfoSimLike` für den Simulator.
- Bereitstellung der Konfiguration `AutopilotCfg` mit wohldefinierten Einheiten.
- Hilfsfunktionen in `Utilities` für Wartebedingungen, Kursnormalisierung und ein
  Geschwindigkeitsprofiliertes Annähern.

Normative Hinweise (DIN‑orientiert)
- Einheiten werden in eckigen Klammern angegeben: Weg [m], Zeit [s], Winkel [°],
  Geschwindigkeit [km/h].
- Alle Angaben sind eindeutig, deterministisch und nebenwirkungsarm zu verwenden.
- Schwellwerte müssen konsistent gewählt werden (slow_at ≥ stop_at ≥ 0).

Begriffe und Abkürzungen
- dv: Geschwindigkeitsänderung in Simulations‑Schrittgröße; Abbildung auf [km/h]
  durch die Werte in `AutopilotCfg`.

Sicherheitsrelevante Annahmen
- `remainder()` in `profiled_approach` ist monoton fallend und terminiert, sonst
  blockiert die Wartebedingung.
- Der Simulator erfüllt das Protokoll vollständig; Methoden sind nicht blockierend,
  außer wo dokumentiert.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Final, Protocol, Callable
import time

class UfoSimLike(Protocol):
    """
    Mindest‑Schnittstelle für den UFO‑Simulator.

    Vertrag
    - Koordinatenrückgaben: `get_x/get_y/get_z` liefern Position [m].
    - `get_dist()` liefert Restweg oder Zielentfernung [m] gemäß Simulation.
    - `get_ftime()` liefert die verstrichene Simulationszeit [s] (floating point).
    - `set_d(deg)` setzt Kursrichtung [°] im mathematischen Sinn (0° … 359°).
    - `set_i(deg)` setzt Nick/Neigung [°], falls simuliert.
    - `request_delta_v(dv)` fordert eine Geschwindigkeitsänderung in Schrittgröße an.

    Nebenbedingungen
    - Alle Methoden sind nicht blockierend, außer der Simulator dokumentiert anderes.
    - Wertebereiche sind gültig und sinnvoll skaliert; Validierung erfolgt im Aufrufer.
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
    Konfigurationswerte für das Ansteuerungsprofil.

    Attribute
    - slow_h [m]: Horizontale Distanz, ab der von Reise‑ auf Langsamfahrt gewechselt wird.
    - stop_h [m]: Horizontales Stoppfenster, in dem auf Stillstand gebremst wird.
    - slow_z_fallback [m]: Vertikale Fallback‑Schwelle, falls keine explizite Zielhöhe vorliegt.
    - stop_z [m]: Vertikales Stoppfenster.
    - landing_slow_z [m]: Höhe, ab der vor dem Aufsetzen sanft abgebremst wird.
    - poll_s [s]: Abfrageintervall für Wartebedingungen.
    - v_up [dv→km/h]: Anfahrbefehl von 0 auf 10 km/h.
    - v_up_to_slow [dv→km/h]: Abbremsbefehl von 10 auf 1 km/h.
    - v_cruise [dv→km/h]: Anfahrbefehl von 0 auf 15 km/h.
    - v_cruise_to_slow [dv→km/h]: Abbremsbefehl von 15 auf 1 km/h.
    - v_stop [dv→km/h]: Endabbremsung von 1 auf 0 km/h.

    Hinweise
    - Werte müssen zur Kinematik des Simulators passen; keine Einheitenumrechnung im Code.
    - Unveränderlich (`frozen=True`) für deterministische Abläufe.
    """
    slow_h: float = 4.0          # Bremsbeginn horizontal [m]
    stop_h: float = 0.05         # Stoppfenster horizontal [m]
    slow_z_fallback: float = 2.0 # z-2.0 als Fallback
    stop_z: float = 0.05         # Stoppfenster vertikal [m]
    landing_slow_z: float = 3.0  # vor Aufsetzen abbremsen
    poll_s: float = 0.01
    v_up: int = 10               # 0  → 10 km/h
    v_up_to_slow: int = -9       # 10 → 1 km/h
    v_cruise: int = 15           # 0  → 15 km/h
    v_cruise_to_slow: int = -14  # 15 → 1 km/h
    v_stop: int = -1             # 1  → 0 km/h

DEFAULT_CFG: Final[AutopilotCfg] = AutopilotCfg()

class NavOps:
    """
    Sammelklasse für deterministische Hilfsfunktionen.

    Bereiche
    - Warten auf Bedingungen mit fester Poll‑Periode.
    - Normalisierung von Winkeln auf ganzzahlige Grad.
    - Geschwindigkeitsprofiliertes Annähern an ein Ziel nach zwei Schwellwerten.
    """
    @staticmethod
    def wait_until(pred: Callable[[], bool], poll_s: float) -> None:
        """
        Blockiert, bis `pred()` True liefert.

        Parameter
        - pred: Nullargument‑Funktion → bool. Muss nebenwirkungsarm und schnell sein.
        - poll_s [s]: Abfrageintervall. Zu kleine Werte erhöhen CPU‑Last.

        Verhalten
        - Ruft `pred()` wiederholt auf und schläft dazwischen `poll_s` Sekunden.
        - Keine Timeout‑Logik; Termination liegt in der Verantwortung des Aufrufers.

        Ausnahmen
        - Keine eigenen Ausnahmen. Exceptions aus `pred()` propagieren nach außen.
        """
        while not pred():
            time.sleep(poll_s)

    @staticmethod
    def dir_to_int(deg: float) -> int:
        """
        Normalisiert einen Winkel in Grad auf eine ganzzahlige Richtung 0…359.

        Parameter
        - deg [°]: Beliebiger reeller Winkel.

        Rückgabe
        - int in [0, 359]. Rundung erfolgt mit Python‑Regel „round half to even“,
          anschließend Modulo 360.

        Beispiel
        - deg = 359.6 → 0; deg = -0.4 → 0; deg = 180.5 → 180.
        """
        return int(round(deg)) % 360

    @staticmethod
    def profiled_approach(
        sim: UfoSimLike,
        remainder: Callable[[], float],
        slow_at: float,
        stop_at: float,
        accel_dv: int,
        slow_dv: int,
        cfg: AutopilotCfg,

    ) -> None:
        """
        Fährt ein zweistufiges Geschwindigkeitsprofil zum Ziel:
        1) Beschleunigen (`accel_dv`) bis Restgröße ≤ `slow_at`.
        2) Abbremsen (`slow_dv`) bis Restgröße ≤ `stop_at`, dann Stop‑Befehl.

        Parameter
        - sim: Objekt, das `UfoSimLike` erfüllt.
        - remainder → float: Liefert die verbleibende Restgröße [m] oder analog.
        - slow_at [Einheit von remainder]: Schwelle für Wechsel auf Langsamfahrt.
        - stop_at [Einheit von remainder]: Schwelle für Endabbremsung.
        - accel_dv: Geschwindigkeitsänderung für die Anfahrt.
        - slow_dv: Geschwindigkeitsänderung für den Übergang auf langsam.
        - cfg: Konfiguration, insbesondere `poll_s` und `v_stop`.

        Voraussetzungen
        - `slow_at ≥ stop_at ≥ 0`.
        - `remainder()` ist monoton fallend und terminiert.

        Nebenwirkungen
        - Ruft `sim.request_delta_v(...)` mehrfach auf.
        - Blockiert in Wartephasen gemäß `cfg.poll_s`.

        Rückgabe
        - None.

        Ausnahmen
        - Keine eigenen Ausnahmen. Exceptions aus `remainder()` propagieren nach außen.
        """
        sim.request_delta_v(accel_dv)
        NavOps.wait_until(lambda: remainder() <= slow_at, cfg.poll_s)
        sim.request_delta_v(slow_dv)
        NavOps.wait_until(lambda: remainder() <= stop_at, cfg.poll_s)
        sim.request_delta_v(cfg.v_stop)