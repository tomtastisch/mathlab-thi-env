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

import argparse
from typing import Collection, Callable, TypeVar, Final, Any, cast

T = TypeVar("T")

# Hilfsparser für bool-Konvertierung
_bool_parser = argparse.ArgumentParser(add_help=False)
_bool_parser.add_argument('--flag', action=argparse.BooleanOptionalAction)

def _bool_converter(s: str) -> bool:
    """
    Konvertiert einen String in einen booleschen Wert unter Verwendung von argparse.
    Erlaubt typische boolesche Eingaben wie 'true', 'false', 'yes', 'no', '1', '0'.
    """
    try:
        # argparse erwartet Argumente in Listenform, daher '--flag' mit Wert s
        parsed = _bool_parser.parse_args(['--flag', s])
        return parsed.flag
    except Exception:
        raise ValueError(f"Ungültiger boolescher Wert: {s}")

# Zuordnung Eingabetyp → Konverterfunktion
DATA_TYPES: Final[dict[type[Any], Callable[[str], Any]]] = {
    str: str,
    int: int,
    float: float,
    bool: _bool_converter,
}

# Prüft Element in Collection unter optionaler Groß-/Kleinbuschreibungsignorierung
def _contains(haystack: Collection[str], needle: str, case_insensitive: bool = True) -> bool:
    """
    Prüft, ob ein Element in einer Menge erlaubt ist.

    ZWECK
    -----
    Unterstützung case-insensitiver Whitelist-Abgleiche.

    PARAMETER
    ---------
    haystack : Collection[str]
        Menge der erlaubten Einträge.
    needle : str
        Zu prüfender Wert.
    case_insensitive : bool
        Aktiviert Groß-/Kleinschreibungsunabhängigkeit.

    RÜCKGABE
    --------
    bool
        True, wenn needle in haystack enthalten ist.
    """
    if case_insensitive and isinstance(needle, str):
        return needle.casefold() in {h.casefold() for h in haystack}

    return needle in haystack


# Generische validated Eingabe aus der Konsole
def read_input(
        prompt: str,
        typ: type[T],
        allowed: Collection[T] | None = None,
        case_insensitive: bool = True
) -> T:
    """
    Typ-basiertes generisches Einlesen aus der Konsole.

    PARAMETER
    ---------
    prompt : str
        Auszugebender Eingabetext.
    typ : type[T]
        Erwarteter Datentyp. Zulässige Typen siehe DATA_TYPES.
    allowed : Collection[T] | None, optional
        Whitelist erlaubter Werte. Ohne Angabe ist jede gültige Eingabe
        des gewünschten Typs zulässig.

    RÜCKGABE
    --------
    T
        Der erfolgreich validierte Wert im gewünschten Typ.

    AUSNAHMEN
    ---------
    ValueError,
        Wenn `allowed` nicht None und leer ist.
    Eingabefehler
        Wenn Eingabe nicht in erlaubter Whitelist ist.
        Wenn Eingabe nicht in den Datentyp transformiert werden kann.

    DESIGN
    ------
    - Konvertierung erfolgt durch vordefinierte Konverter in DATA_TYPES.
    - DATA_TYPES definiert die erlaubten Eingabetypen und zugehörigen Konverter.
    - Falls keine Whitelist vorliegt, wird die Eingabe dynamisch akzeptiert.
    - Fehlertypen werden per Logger ausgegeben.
    - Boolesche Eingaben werden mit argparse-konformen Konvertern verarbeitet.
    """

    # Leere Whitelist ist logisch ungültig → frühzeitiger Fehler
    if allowed is not None and len(allowed) == 0:
        raise ValueError("allowed darf nicht leer sein")

    # Konverter anhand des gewünschten Typs bestimmen
    conv    : Callable[[str], T] = cast(Callable[[str], T], DATA_TYPES.get(typ, typ))
    # Whitelist für schnelleren Lookup in set-Form
    allowed_set: set[T] | None = set(allowed) if allowed is not None else None

    # Eingabeschleife: bis gültiger Wert vorliegt
    while True:

        # Rohwert erfassen
        raw = input(prompt)

        # Konvertierungsversuch
        try:
            value: T = conv(raw)
        except (ValueError, TypeError):
            type_name : str = getattr(typ, "__name__", str(typ))
            print(f"Ungültige Eingabe. Erwarteter Typ: {type_name}")
            continue

        # Bestimmen erlaubter Zielwerte
        approved: set[T] = allowed_set if allowed_set is not None else {value}

        # Prüfung, ob value enthalten ist, mithilfe der funktion unter beachtung
        # der Vorgabe
        # → case-sensitive beachten [Ja/Nein]
        if _contains(
                haystack=approved,
                needle=value,
                case_insensitive=case_insensitive
        ):
            # Gültiger Wert gefunden
            return value

        display = ", ".join(map(str, sorted(approved, key=lambda x: str(x))))
        print(f"Ungültige Eingabe. Erlaubt: {display}")
