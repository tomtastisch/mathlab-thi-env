# thi/i/ki/project/ufo/src/core/ufo_main.py
# Vorgabe wie angel: keine Funktionsdefinitionen
from util.evaluation import read_input, eps
from core.angel import angel

eingabe: float = read_input("test eingabe (int): ", int)
print(eingabe)
a = angel(eingabe, eingabe, eingabe, eingabe)
print(a)

# Platzhalter-Ausgabe für den Start
if __name__ == "__main__":
    # Startpunkt für CLI-Aufruf
    print("Ufo-Modul Ausführung")
    # Hauptlogik (bereits im Skript vorhanden)