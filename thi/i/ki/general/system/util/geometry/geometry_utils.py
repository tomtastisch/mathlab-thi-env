from __future__ import annotations
from typing import Optional

class GeometryUtil:
    """
    Physikalische Hilfsfunktionen für Bremsweg und Bremsbeginn.

    Annahmen:
        - konstante Verzögerung (a_neg) während der Bremsphase
        - konsistente SI-Einheiten: v in m/s, a in m/s², Strecken in m
        - Beschleunigungszeichen: `a_neg` ist als negative Größe gedacht; intern wird mit `abs()` gearbeitet.
    Ziel:
        - realitätsnahe, deterministische Berechnung ohne fest kodierte Faktoren
        - optionale Heuristik-Variante nur, wenn keine Kinematik-parameter vorliegen
    """

    KMH2MPS: float = 1000.0 / 3600.0

    @staticmethod
    def _to_mps(v: float, v_unit: str) -> float:
        """Konvertiert Geschwindigkeit in m/s. `v_unit` ∈ {"mps", "kmh", "km/h"}."""
        if v_unit == "mps":
            return v
        if v_unit in ("kmh", "km/h"):
            return v * GeometryUtil.KMH2MPS
        raise ValueError("v_unit muss 'mps' oder 'kmh' sein")

    @staticmethod
    def bremsbeginn(
        s_total: float,
        stop_window: float,
        *,
        v0: Optional[float] = None,
        v1: Optional[float] = None,
        a: Optional[float] = None,
        rel: Optional[float] = None,
        fallback: Optional[float] = None,
        v_unit: str = "mps"
    ) -> float:
        """
        Bestimmt den Startpunkt der Langsamphase entlang einer Strecke. Wenn v0, v1 und
        a gesetzt sind, überwiegt die kinematische Herleitung; andernfalls werden optionale
        Heuristiken (rel, fallback) berücksichtigt.

        Args:
            s_total:        Gesamtdistanz bis zum Ziel. Negative Eingaben werden auf 0 geklemmt.
            stop_window:    Brems-/Haltefenster. Negative Eingaben werden auf 0 geklemmt.
                            Unterhalb dessen wird nicht weiter angenähert.
            v0:             Ausgangsgeschwindigkeit. Optional.
            v1:             Zielgeschwindigkeit für die Langsamphase. Optional.
            a:              Konstante (negative) Beschleunigung in m/s². Interpretation: a ≤ 0.
                            Intern wird `abs(a)` verwendet. Optional.
            rel:            Relativer Heuristikfaktor ∈ [0, 1], interpretiert als rel · s_total.
                            Werte außerhalb werden auf [0, 1] geklemmt. Optional.
            fallback:       Absoluter Heuristikabzug: s_total − fallback. Optional.
            v_unit:         Geschwindigkeiten per `v_unit` in m/s oder km/h.

        Returns:
            Startpunkt der Langsamphase, geklemmt in [stop_window, s_total].
        """
        # Eingangswerte validieren
        s_total = max(0.0, s_total)
        stop_window = max(0.0, stop_window)

        if s_total <= stop_window:
            return float(stop_window)

        candidates: list[float] = []

        # Kinematischer Kandidat, wenn vollständig spezifiziert
        if v0 is not None and v1 is not None and a is not None and a != 0.0:
            v0_mps = GeometryUtil._to_mps(v0, v_unit)
            v1_mps = GeometryUtil._to_mps(v1, v_unit)
            decel = max(0.0, (v0_mps * v0_mps - v1_mps * v1_mps) / (2.0 * abs(a)))  # s = (v0² − v1²) / (2|a|)
            candidates.append(s_total - decel)

        # Relativer Kandidat (rel in [0, 1])
        if rel is not None:
            rel_c = min(1.0, max(0.0, rel))
            candidates.append(rel_c * s_total)

        # Absoluter Fallback-Kandidat
        if fallback is not None:
            candidates.append(s_total - fallback)

        start = max(candidates) if candidates else stop_window
        start = min(s_total, max(stop_window, start))  # Clamp auf gültigen Bereich
        return float(start)

    @staticmethod
    def bremsweg(
            v0: float,
            v1: float,
            a_neg: float,
            *,
            v_unit: str = "mps"
    ) -> float:
        """
        Berechnet den Bremsweg s bei konstanter negativer Verzögerung. Geschwindigkeiten können in m/s (Standard) oder km/h übergeben werden (`v_unit`).

        Formel: s = max(0, (v0² − v1²) / (2·|a_neg|))
        Interpretation: a_neg ≤ 0 (negatives Vorzeichen für Bremsen). Intern wird `abs(a_neg)` verwendet.
        Hinweis: Falls a_neg == 0 → Rückgabe `inf` (kein Bremsen möglich gemäß Modell).
        """
        from math import inf
        a = abs(a_neg)
        if a == 0.0:
            return inf
        v0_mps = GeometryUtil._to_mps(v0, v_unit)
        v1_mps = GeometryUtil._to_mps(v1, v_unit)
        return max(0.0, (v0_mps * v0_mps - v1_mps * v1_mps) / (2.0 * a))

    @staticmethod
    def muss_bremsen_rest(
            rest: float,
            v0: float,
            v1: float,
            a_neg: float,
            stop_window: float = 0.0,
            *,
            v_unit: str = "mps"
    ) -> bool:
        """
        Prüft, ob Bremsen jetzt erforderlich ist.

        Kriterium: rest ≤ bremsweg(v0, v1, a_neg) + stop_window.
        Geschwindigkeiten per
        `v_unit` in m/s oder km/h.
        """
        return rest <= GeometryUtil.bremsweg(v0, v1, a_neg, v_unit=v_unit) + max(0.0, stop_window)

    @staticmethod
    def bremsbeginn_kinematik(
        s_total: float,
        stop_window: float,
        *,
        v0: float,
        v1: float,
        a_neg: float,
        v_unit: str = "mps"
    ) -> float:
        """
        Startpunkt der Langsamphase aus s_total, v0, v1 und konstanter Verzögerung.

        Verfahren: start = s_total − bremsweg(v0, v1, a_neg),
        anschließend Klemmen auf [stop_window, s_total].

        Interpretation: a_neg ≤ 0 (Bremsen). Intern wird `abs(a_neg)` verwendet.
        `v_unit` steuert die Einheit der Geschwindigkeiten.
        """
        s = GeometryUtil.bremsweg(v0, v1, a_neg, v_unit=v_unit)
        start = s_total - s
        return min(s_total, max(stop_window, start))

    @staticmethod
    def verlangsamen_vertikal(
            s_total: float,
            stop_window: float,
            *,
            v0: float,
            v1: float,
            a_neg: float,
            v_unit: str = "mps",
    ) -> float:
        """
        Startpunkt der Langsamphase in z-Richtung. Klemmt auf [stop_window, s_total].
        """
        return GeometryUtil.bremsbeginn_kinematik(
            s_total=s_total,
            stop_window=stop_window,
            v0=v0,
            v1=v1,
            a_neg=a_neg,
            v_unit=v_unit,
        )

    @staticmethod
    def stoppen_vertikal(stop_window: float) -> float:
        """Validated Stoppschwelle in z-Richtung (nicht negativ)."""
        return max(0.0, stop_window)


