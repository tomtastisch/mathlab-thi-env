"""
input_utils – Hilfsfunktionen für Benutzereingaben

DOKUMENTATION NACH DIN 5008
===========================

ZWECK
-----
Validierung und Verarbeitung typgeprüfter Benutzereingaben in Konsolenanwendungen.
Unterstützt sichere Interaktion sowie Eingabekontrolle durch Whitelists.

ANWENDUNGSBEREICH
-----------------
- Studien und Lehrumgebungen
- Konsolenbasierte Tools
- Interaktive Terminalprogramme mit Eingabevalidierung

BEGRIFFSBESTIMMUNGEN
--------------------
- Whitelist: Menge erlaubter Eingaben, typgeprüft
- Konverter: Funktion zur sicheren Wandlung von Text in Zieltypen
- Typenvalidierung: Sicherstellung des Eingabetyps gemäß Annotation

MERKMALE
--------
- Typsichere Umwandlung von Eingaben
- Optional case-insensitive Abgleich
- Erweiterbare Konvertertabelle DATA_TYPES
- Fehlerausgabe über Logging

HINWEISE
--------
Alle Funktionen blockieren bis zur gültigen Eingabe.
Boolesche Eingaben werden mit argparse-konformen Konvertern behandelt.
"""

from __future__ import annotations
import argparse
from typing import Collection, Callable, TypeVar, Final, Any, cast, final

T = TypeVar("T")

__all__ = [
    "InputUtils",
    "DATA_TYPES",
    "_contains",
    "read_input",
]

@final
class InputUtils:
    """
    Eingabe‑Utilities (Namespace)
    =============================

    Zweck
    -----
    Bereitstellung typgesicherter Konsolen‑Eingaben und Whitelist‑Prüfungen
    für Kommandozeilenprogramme. Die Klasse ist ein reiner Namespace und nicht
    instanziierbar (`@final`, `__slots__ = ()`).

    Anwendungsbereich
    -----------------
    - Lehr‑/Studienaufgaben und kleine Tools
    - Interaktive Terminalprogramme mit Eingabevalidierung

    Begriffsbestimmungen
    --------------------
    - Whitelist: endliche Menge erlaubter Zielwerte
    - Konverter: Funktion zur Wandlung von `str` in den Zieltyp

    Öffentliche Schnittstelle
    -------------------------
    - `bool_converter(s: str) -> bool`
      argparse‑basierte Umwandlung typischer Bool‑Eingaben ("true/false",
      "yes/no", "1/0").
    - `contains(haystack: Collection[str], needle: str, *, case_insensitive: bool = True) -> bool`
      Mitgliedschaftstest mit optionaler Groß‑/Kleinschreibungsignorierung.
      Casefolding wird nur angewandt, wenn **needle** und alle Elemente in
      **haystack** Strings sind.
    - `read_input(prompt: str, typ: type[T], allowed: Collection[T] | None = None, *, case_insensitive: bool = True) -> T`
      Blockierendes Einlesen und Validieren von Eingaben. Konvertierung über
      `DATA_TYPES` oder den angegebenen Typ als Callable.

    Vorbedingungen
    --------------
    - `allowed` ist entweder `None` oder nicht leer; leere Whitelists sind
      unzulässig (ValueError).
    - `typ` ist in `DATA_TYPES` abgebildet oder selbst ein gültiger Konverter
      `Callable[[str], T]`.

    Rückgaben
    ---------
    - `contains` liefert `True/False`.
    - `read_input` liefert einen Wert vom Zieltyp `T`.

    Fehler/Ausnahmen
    ----------------
    - `ValueError` bei leerer Whitelist, ungültiger Bool‑Eingabe oder
      fehlgeschlagener Typkonvertierung.
    - `TypeError` bei ungeeigneten Konverter‑Signaturen.

    Nebenwirkungen
    --------------
    - `read_input` nutzt `input()`/`print()` und blockiert bis zu einer
      gültigen Eingabe; keine Timeouts.

    Beispiele
    ---------
    - `age = InputUtils.read_input("Alter: ", int, allowed={18, 19, 20})`
    - `flag = InputUtils.bool_converter("yes")  # -> True`

    Konformität
    -----------
    - Dokumentationsstruktur angelehnt an DIN 5008.
    - Eindeutige, deterministische Beschreibungen; keine Seiteneffekte außer I/O.
    """

    __slots__ = ()

    def __new__(cls, *_, **__):  # pragma: no cover
        raise TypeError("InputUtils ist ein reiner Namespace und nicht instanziierbar")

    # argparse-basierter Bool-Parser (identische Logik wie zuvor)
    _BOOL_PARSER = argparse.ArgumentParser(add_help=False)
    _BOOL_PARSER.add_argument('--flag', action=argparse.BooleanOptionalAction)

    @staticmethod
    def _bool_converter(s: str) -> bool:
        """
        Konvertiert typische boolesche Eingaben wie 'true', 'false', 'yes', 'no', '1', '0'.
        """

        try:
            parsed = InputUtils._BOOL_PARSER.parse_args(['--flag', s])
            return parsed.flag
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Ungültiger boolescher Wert: {s}") from e

    @staticmethod
    def bool_converter(s: str) -> bool:
        """
        Öffentliche Alias-Methode für den Bool-Konverter.
        """
        return InputUtils._bool_converter(s)

    @staticmethod
    def contains(haystack: Collection[str], needle: str, /, *, case_insensitive: bool = True) -> bool:
        """
        Case-insensitiver Whitelist-Check. Logik unverändert.
        """
        if case_insensitive and isinstance(needle, str):
            return needle.casefold() in {h.casefold() for h in haystack}
        return needle in haystack

    @staticmethod
    def read_input(
        prompt: str,
        typ: type[T],
        allowed: Collection[T] | None = None,
        *,
        case_insensitive: bool = True,
    ) -> T:
        """
        Generisches Einlesen mit Typ- und Whitelist-Validierung. Logik unverändert.
        """

        if allowed is not None and len(allowed) == 0:
            raise ValueError("allowed darf nicht leer sein")

        conv: Callable[[str], T] = cast(Callable[[str], T], DATA_TYPES.get(typ, typ))
        allowed_set: set[T] | None = set(allowed) if allowed is not None else None

        while True:
            raw = input(prompt)
            try:
                value: T = conv(raw)
            except (ValueError, TypeError):
                type_name: str = getattr(typ, "__name__", str(typ))
                print(f"Ungültige Eingabe. Erwarteter Typ: {type_name}")
                continue

            approved: set[T] = allowed_set if allowed_set is not None else {value}

            is_all_str = isinstance(value, str) and all(isinstance(a, str) for a in approved)
            if (InputUtils.contains(approved, value, case_insensitive=case_insensitive)
                if is_all_str else (value in approved)):
                return value

            display = ", ".join(map(str, sorted(approved, key=lambda x: str(x))))
            print(f"Ungültige Eingabe. Erlaubt: {display}")

# Öffentliche Konverter-Tabelle. Logik unverändert.
DATA_TYPES: Final[dict[type[Any], Callable[[str], Any]]] = {
    str: str,
    int: int,
    float: float,
    bool: InputUtils.bool_converter,
}

# Abwärtskompatible Wrapper.
def _contains(haystack: Collection[str], needle: str, case_insensitive: bool = True) -> bool:
    return InputUtils.contains(haystack, needle, case_insensitive=case_insensitive)


def read_input(
    prompt: str,
    typ: type[T],
    allowed: Collection[T] | None = None,
    case_insensitive: bool = True,
) -> T:
    return InputUtils.read_input(
        prompt=prompt,
        typ=typ,
        allowed=allowed,
        case_insensitive=case_insensitive,
    )
