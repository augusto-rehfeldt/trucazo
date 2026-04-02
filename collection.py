"""Persistent collection for Trucazo."""
import json, os

COLLECTION_FILE = os.path.join(os.path.dirname(__file__), ".collection.json")


class Collection:
    def __init__(self):
        self.discovered_poderes = set()
        self.discovered_ediciones = set()
        self.discovered_talismanes = set()
        self.discovered_jefes = set()
        self.best_hand = 0
        self.best_envido = 0
        self.total_runs = 0
        self.best_ante = 0
        self.wins = 0
        self.rachas = 0
        self.envidos_ganados = 0
        self.flores = 0
        self.manos_ganadas = 0
        self.manos_perdidas = 0
        self.load()

    def load(self):
        if os.path.exists(COLLECTION_FILE):
            try:
                with open(COLLECTION_FILE) as f:
                    d = json.load(f)
                for k, v in d.items():
                    if hasattr(self, k):
                        setattr(self, k, set(v) if isinstance(v, list) else v)
            except (json.JSONDecodeError, KeyError):
                pass

    def save(self):
        d = {}
        for k, v in self.__dict__.items():
            d[k] = sorted(v) if isinstance(v, set) else v
        with open(COLLECTION_FILE, "w") as f:
            json.dump(d, f, indent=2)

    def record_run_end(self, ante, won):
        self.total_runs += 1
        if ante > self.best_ante:
            self.best_ante = ante
        if won:
            self.wins += 1
        self.save()

    @property
    def completion_pct(self):
        from data import ALL_TALISMANES
        from cards import Poder, Edition
        total = len(ALL_TALISMANES) + len([p for p in Poder if p != Poder.NADA]) + len([e for e in Edition if e != Edition.COMUN])
        found = len(self.discovered_talismanes) + len(self.discovered_poderes) + len(self.discovered_ediciones)
        return int(found / total * 100) if total else 0
