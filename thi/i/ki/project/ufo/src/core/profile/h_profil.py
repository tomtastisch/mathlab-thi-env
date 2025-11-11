from __future__ import annotations


import time
from typing import Callable
from ..cfg import AutopilotCfg, UfoSimLike

try:
    from system.dtypes import ProgressCheck
except ModuleNotFoundError:
    from dtypes import ProgressCheck

"""
Profil-Operationen für die UFO‑Simulation
===================================================================

Voraussetzungen
- Schwellwerte: slow_at ≥ stop_at ≥ 0.
- remainder() ist monoton fallend und terminiert.

Öffentliche API
- HProfil.warte_bis(bedingung, abfrage_s)
- HProfil.richtung_als_int(grad)
- HProfil._profil_schritt_bis(sim, rest, schwelle_langsam, schwelle_stop, dv_beschleunigen, dv_abbremsen, konfig)
"""

class HProfil:
    """
    Profil-Klasse für deterministische Abläufe.

    Bereiche
    - Warten auf Bedingungen mit fester Abfrageperiode.
    - Normalisierung von Winkeln auf ganzzahlige Grad.
    - Profilierte Geschwindigkeit zur Annäherung an ein Ziel (zweistufiges Profil).
    """

    @staticmethod
    def warte_bis(
            bedingung: Callable[[], bool],
            abfrage_s: float,
    ) -> None:
        """
        Blockiert, bis `bedingung()` True liefert. Kein Timeout.
        """
        while not bedingung():
            time.sleep(abfrage_s)

    @staticmethod
    def richtung_als_int(grad: float) -> int:
        """
        Normalisiert einen Gradwinkel auf eine ganzzahlige Richtung 0 … 359.
        """
        return int(round(grad)) % 360

    @staticmethod
    def _profil_schritt_bis (
        sim: UfoSimLike,
        rest: Callable[[], float],
        ziel: float,
        dv: int,
        abfrage_s: float,
    ) -> None:
        """
        Ein Schritt des Annäherungsprofils: Geschwindigkeit anpassen und warten,
        bis `rest()` ≤ `ziel` oder Stagnation erkannt wird.

        Args:
            sim: Implementierung des Simulators.
            rest: Funktion, die den aktuellen Restwert liefert.
            ziel: Zielschwelle, die erreicht oder unterschritten werden soll.
            dv: Geschwindigkeitsinkrement in Schrittgröße (km/h pro Tick).
            abfrage_s: Abfrageperiode für die Bedingungsprüfung.
        """
        prog_check : ProgressCheck = ProgressCheck(rest=rest, ziel=ziel)

        sim.request_delta_v(dv)
        HProfil.warte_bis(prog_check, abfrage_s)

    @staticmethod
    def schrittweise_bis(
        sim: UfoSimLike,
        rest: Callable[[], float],
        schwelle_langsam: float,
        schwelle_stop: float,
        dv_beschleunigen: int,
        dv_abbremsen: int,
        konfig: AutopilotCfg,
    ) -> None:
        """
        Zweistufiges Geschwindigkeitsprofil zum Ziel:
        1) Beschleunigen bis Restgröße ≤ `schwelle_langsam`.
        2) Abbremsen bis Restgröße ≤ `schwelle_stop`, danach Stop-Befehl.

        Zweistufig sichert Tempo und Genauigkeit zugleich.
        Stufe 1 bringt das System schnell nahe ans Ziel, bis der verbleibende
        Weg klein genug für sicheres Bremsen ist. Stufe 2 bremst fein, verhindert
        Überlauf und hält im gewünschten Stop-Fenster.
        """
        # Phase 1: Beschleunigen
        HProfil._profil_schritt_bis(sim, rest, schwelle_langsam, dv_beschleunigen, konfig.poll_s)
        # Phase 2: Abbremsen
        HProfil._profil_schritt_bis(sim, rest, schwelle_stop, dv_abbremsen, konfig.poll_s)
        # Stop
        sim.request_delta_v(konfig.v_stop)


__all__ = ["HProfil"]