"""
AUTOPILOT – Vertikale Profilgrenzen (Beschleunigen/Bremsen, Z‑Richtung)
=======================================================================

Zweck
- Gemeinsame Vorberechnung und kinematische Grenzen für Beschleunigen/Abbremsen in Z.

Begriffe
- dv: Geschwindigkeitsänderung je Simulations‑Tick (Konvertierung durch `AutopilotCfg`).

Hinweise
- Deterministische, nebenwirkungsarme Routinen. Keine Nebenwirkungen außerhalb der Rückgaben.
"""
from __future__ import annotations
from typing import NamedTuple

from ..cfg import AutopilotCfg


class ZProfil:
    """
    Vertikales Profil: Grenzen für Beschleunigen und Bremsen in Z‑Richtung.

    Öffentliche API
    - ZProfil.langsam_grenze_kinematik(z, cfg)
    - ZProfil.ende_beschleunigung_kinematik(z, cfg, start_z=0.0)
    """

    class _ZProfilDaten(NamedTuple):
        gesamt_strecke: float
        dv_beschleunigen: float
        dv_abbremsen: float
        brems_strecke: float
        langsam_fenster: float
        brems_beginn: float
        stop_schwelle: float

    @staticmethod
    def _baue_plan(z: float, cfg: AutopilotCfg, start_z: float = 0.0) -> "ZProfil._ZProfilDaten | None":
        """
        Gemeinsame Vorberechnungen für vertikale Profile.

        Zweck:
            Baut aus Zielhöhe, Start und Δv/Tick einen Plan aus:
            verbleibender Strecke, Magnituden für Beschleunigen/Abbremsen, Langsam‑Fenster und Bremsbeginn.

        Args:
            z (float): Zielhöhe [m].
            cfg (AutopilotCfg): Konfiguration inkl. `stop_z`, `slow_z_fallback`, `v_up`, `v_up_to_slow`.
            start_z (float): Starthöhe [m]. Standard: 0.0.

        Returns:
            ZProfil._ZProfilDaten | None: Plan mit kinematischen Größen oder `None`, wenn
            keine Strecke vorliegt (`z ≤ stop_schwelle`) oder Δv/Tick‑Magnituden 0 sind.

        Invarianten:
            - 0 ≤ brems_strecke ≤ gesamt_strecke
            - 0 ≤ langsam_fenster ≤ gesamt_strecke
            - stop_schwelle ≤ brems_beginn ≤ z
        """
        stop_schwelle: float = max(cfg.stop_z, start_z)
        gesamt_strecke: float = max(z - stop_schwelle, 0.0)

        dv_beschleunigen: float = abs(cfg.v_up)
        dv_abbremsen: float = abs(cfg.v_up_to_slow)

        # ein Rückgabepunkt: plan ist optional
        plan: "ZProfil._ZProfilDaten | None" = None

        if gesamt_strecke > 0.0 and dv_beschleunigen > 0.0 and dv_abbremsen > 0.0:

            brems_strecke: float = gesamt_strecke * dv_beschleunigen / (dv_beschleunigen + dv_abbremsen)
            langsam_fenster: float = min(gesamt_strecke, max(brems_strecke, cfg.slow_z_fallback))
            brems_beginn: float = z - langsam_fenster

            plan = ZProfil._ZProfilDaten(
                gesamt_strecke=gesamt_strecke,
                dv_beschleunigen=dv_beschleunigen,
                dv_abbremsen=dv_abbremsen,
                brems_strecke=brems_strecke,
                langsam_fenster=langsam_fenster,
                brems_beginn=brems_beginn,
                stop_schwelle=stop_schwelle,
            )

        return plan

    @staticmethod
    def langsam_grenze_kinematik(z: float, cfg: AutopilotCfg) -> float:
        """
        Höhe, ab der verlangsamt werden soll, um weich anzukommen.

        Args:
            z (float): Zielhöhe [m].
            cfg (AutopilotCfg): Autopilot‑Konfiguration.

        Returns:
            float: Grenze [m] ≥ `cfg.stop_z`, ab der aus kinematischen Gründen verlangsamt wird.
        """
        profil: ZProfil._ZProfilDaten | None = ZProfil._baue_plan(z, cfg)
        grenze: float = cfg.stop_z if profil is None else max(cfg.stop_z, z - profil.langsam_fenster)
        return grenze

    @staticmethod
    def ende_beschleunigung_kinematik(z: float, cfg: AutopilotCfg, start_z: float = 0.0) -> float:
        """
        Kinematisch hergeleiteter Endpunkt der Beschleunigungsphase in Z.
        Ohne explizites v_max ergibt sich ein Dreiecksprofil (accel→decel).

        Args:
            z (float): Zielhöhe [m].
            cfg (AutopilotCfg): Autopilot‑Konfiguration.
            start_z (float): Starthöhe [m]. Standard: 0.0.

        Raises:
            ValueError: Falls `z < start_z`.

        Returns:
            float: Höhe [m] des Beschleunigungsendes. Immer `start_z ≤ return ≤ z`.

        Invarianten:
            - Kandidat wird auf `[start_z, brems_beginn]` gecleant.
        """
        if z < start_z:
            raise ValueError("z muss ≥ start_z sein")

        plan: ZProfil._ZProfilDaten | None = ZProfil._baue_plan(z, cfg, start_z)
        beschleunigungsende: float = start_z

        if plan is not None:
            # Dreiecksprofil ohne v_max: s_acc = gesamt_strecke - brems_strecke
            s_acc: float = max(plan.gesamt_strecke - plan.brems_strecke, 0.0)
            # Strecke bis zum Bremsbeginn (inklusive gegebenenfalls 'Cruise')
            s_pre: float = max(plan.gesamt_strecke - plan.langsam_fenster, 0.0)
            # Geplanter Endpunkt der Beschleunigung
            kandidat: float = start_z + min(s_acc, s_pre)
            # Clamp: nicht hinter Bremsbeginn und nie vor start_z
            beschleunigungsende = max(start_z, min(kandidat, plan.brems_beginn))

        return beschleunigungsende


__all__ = ["ZProfil"]