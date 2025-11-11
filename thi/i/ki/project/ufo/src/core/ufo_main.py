# thi/i/ki/project/ufo/src/core/ufo_main.py
from .ufosim3_2_9q import UfoSim
from util.evaluation import read_input  # Fallback, falls util nicht installiert ist
from .ufo_autopilot import flight_distance, fly_to
import os


def main() -> None:
    # Eingabe: Ziel und Flughöhe
    x: float = read_input("X- Koordinate eingeben: ", float)
    y: float = read_input("Y- Koordinate eingeben: ", float)
    z: float = read_input("Z- Koordinate eingeben: ", float)

    # Geplante Distanz (2 Nachkommastellen)
    planned: float = flight_distance(0.0, 0.0, x, y, z)
    print(f"{planned:.2f}")

    headless: bool = os.getenv("UFO_HEADLESS", "0") == "1"
    if headless:
        # Nur Planung ausgeben, keine GUI/Simulation
        return

    # Simulation starten (ganze Zahlen gefordert)
    sim = UfoSim()
    speedup: int = 5
    scaling: int = 10
    sim.start(speedup, scaling, [(x, y)])

    # Flug ausführen
    fly_to(sim, x, y, z)

    # Tatsächlich geflogene Distanz (2 Nachkommastellen)
    actual: float = sim.get_dist()
    print(f"{actual:.2f}")

    sim.terminate()

if __name__ == "__main__":
    main()