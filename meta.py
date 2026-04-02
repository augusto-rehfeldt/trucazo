"""Meta-progression system for Trucazo (Hades Mirror of Night style)."""
import json, os

META_FILE = os.path.join(os.path.dirname(__file__), ".meta.json")

# ── FOGÓN UPGRADES ──

FOGON_UPGRADES = [
    {
        "id": "mate_inicial",
        "name": "Mate Inicial",
        "name_en": "Starting Mate",
        "desc": "Empezás con +${v} extra",
        "desc_en": "Start with +${v} extra",
        "emoji": "🧉",
        "max_level": 3,
        "costs": [50, 150, 300],
        "values": [1, 2, 3],
    },
    {
        "id": "mano_firme",
        "name": "Mano Firme",
        "name_en": "Steady Hand",
        "desc": "+{v} manos extra por ronda",
        "desc_en": "+{v} extra hands per blind",
        "emoji": "✋",
        "max_level": 2,
        "costs": [150, 400],
        "values": [1, 2],
    },
    {
        "id": "billetera_gruesa",
        "name": "Billetera Gruesa",
        "name_en": "Fat Wallet",
        "desc": "+${v} ingreso por ronda",
        "desc_en": "+${v} income per blind",
        "emoji": "💰",
        "max_level": 2,
        "costs": [100, 250],
        "values": [1, 2],
    },
    {
        "id": "sangre_gaucha",
        "name": "Sangre Gaucha",
        "name_en": "Gaucho Blood",
        "desc": "Empezás con racha {v}",
        "desc_en": "Start run with cascade {v}",
        "emoji": "🩸",
        "max_level": 2,
        "costs": [100, 300],
        "values": [1, 2],
    },
    {
        "id": "cuero_duro",
        "name": "Cuero Duro",
        "name_en": "Tough Hide",
        "desc": "Sobrevivís 1 ronda fallida por partida",
        "desc_en": "Survive 1 failed blind per run",
        "emoji": "🛡️",
        "max_level": 1,
        "costs": [500],
        "values": [1],
    },
    {
        "id": "descuento",
        "name": "Descuento",
        "name_en": "Discount",
        "desc": "Precios del kiosco -{v}%",
        "desc_en": "Shop prices -{v}%",
        "emoji": "🏷️",
        "max_level": 2,
        "costs": [200, 450],
        "values": [15, 30],
    },
    {
        "id": "herencia",
        "name": "Herencia",
        "name_en": "Inheritance",
        "desc": "Empezás con 1 talismán random",
        "desc_en": "Start run with 1 random talisman",
        "emoji": "🎁",
        "max_level": 1,
        "costs": [600],
        "values": [1],
    },
    {
        "id": "corazon_de_leon",
        "name": "Corazón de León",
        "name_en": "Lion Heart",
        "desc": "Truco empieza en nivel {v}",
        "desc_en": "Truco starts at level {v}",
        "emoji": "🦁",
        "max_level": 2,
        "costs": [250, 600],
        "values": [2, 3],
    },
    {
        "id": "sexto_sentido",
        "name": "Sexto Sentido",
        "name_en": "Sixth Sense",
        "desc": "Ves pista del envido de la Banca",
        "desc_en": "See house envido score hint",
        "emoji": "👁️",
        "max_level": 1,
        "costs": [200],
        "values": [1],
    },
    {
        "id": "repertorio",
        "name": "Repertorio",
        "name_en": "Repertoire",
        "desc": "+{v} slots de talismanes (máx 5)",
        "desc_en": "+{v} extra talisman slots (max 5)",
        "emoji": "🎒",
        "max_level": 2,
        "costs": [300, 750],
        "values": [1, 2],
    },
    {
        "id": "ojo_de_lince",
        "name": "Ojo de Lince",
        "name_en": "Lynx Eye",
        "desc": "+{v}% chance de edición automática",
        "desc_en": "+{v}% auto-edition chance on dealt cards",
        "emoji": "👁️‍🗨️",
        "max_level": 3,
        "costs": [150, 350, 700],
        "values": [3, 6, 10],
    },
]

# ── DESAFÍOS (CHALLENGES) ──

DESAFIOS = [
    {
        "id": "envido_master",
        "name": "Envido Master",
        "desc": "Ganá 20 envidos en total",
        "desc_en": "Win 20 envidos total",
        "condition_key": "envidos_ganados",
        "condition_value": 20,
        "unlock_type": "talisman",
        "unlock_id": "el_gringo",
        "emoji": "🎯",
    },
    {
        "id": "racha_infinita",
        "name": "Racha Infinita",
        "name_en": "Infinite Cascade",
        "desc": "Llegá a racha 7 en una partida",
        "desc_en": "Reach cascade 7 in a run",
        "condition_key": "best_racha",
        "condition_value": 7,
        "unlock_type": "talisman",
        "unlock_id": "la_yapa",
        "emoji": "🔥",
    },
    {
        "id": "trucazo_perfecto",
        "name": "Trucazo Perfecto",
        "name_en": "Perfect Trucazo",
        "desc": "Ganá una mano con Vale Cuatro",
        "desc_en": "Win a hand at Vale Cuatro",
        "condition_key": "vale_cuatro_wins",
        "condition_value": 1,
        "unlock_type": "poder",
        "unlock_id": "tornado",
        "emoji": "⚡",
    },
    {
        "id": "matador",
        "name": "Matador",
        "desc": "Vencé 8 jefes diferentes",
        "desc_en": "Beat 8 different bosses",
        "condition_key": "jefes_vencidos",
        "condition_value": 8,
        "unlock_type": "talisman",
        "unlock_id": "el_domador",
        "emoji": "🗡️",
    },
    {
        "id": "coleccionista",
        "name": "Coleccionista",
        "name_en": "Collector",
        "desc": "Descubrí 75% de los ítems",
        "desc_en": "Discover 75% of items",
        "condition_key": "completion_pct",
        "condition_value": 75,
        "unlock_type": "edition",
        "unlock_id": "arcoiris",
        "emoji": "🏅",
    },
    {
        "id": "asceta",
        "name": "Asceta",
        "name_en": "Ascetic",
        "desc": "Ganá una partida sin comprar poderes",
        "desc_en": "Win a run without buying powers",
        "condition_key": "ascetic_wins",
        "condition_value": 1,
        "unlock_type": "talisman",
        "unlock_id": "el_purista",
        "emoji": "🧘",
    },
    {
        "id": "millonario",
        "name": "Millonario",
        "name_en": "Millionaire",
        "desc": "Acumulá $50 en una partida",
        "desc_en": "Accumulate $50 in one run",
        "condition_key": "max_money",
        "condition_value": 50,
        "unlock_type": "poder",
        "unlock_id": "alquimia",
        "emoji": "💎",
    },
    {
        "id": "sobreviviente",
        "name": "Sobreviviente",
        "name_en": "Survivor",
        "desc": "Sobreviví con Cuero Duro",
        "desc_en": "Survive with Cuero Duro",
        "condition_key": "cuero_duro_used",
        "condition_value": 1,
        "unlock_type": "talisman",
        "unlock_id": "cicatriz",
        "emoji": "💪",
    },
    {
        "id": "rey_del_truco",
        "name": "Rey del Truco",
        "name_en": "King of Truco",
        "desc": "Ganá 5 partidas",
        "desc_en": "Win 5 runs",
        "condition_key": "wins",
        "condition_value": 5,
        "unlock_type": "mode",
        "unlock_id": "endless",
        "emoji": "👑",
    },
    {
        "id": "flor_imperial",
        "name": "Flor Imperial",
        "name_en": "Imperial Flor",
        "desc": "Cantá flor 10 veces",
        "desc_en": "Score flor 10 times",
        "condition_key": "flores",
        "condition_value": 10,
        "unlock_type": "poder",
        "unlock_id": "perfume",
        "emoji": "🌸",
    },
    {
        "id": "primer_sangre",
        "name": "Primera Sangre",
        "name_en": "First Blood",
        "desc": "Ganá la primera mano con Truco",
        "desc_en": "Win the first hand with Truco",
        "condition_key": "first_hand_truco_wins",
        "condition_value": 1,
        "unlock_type": "talisman",
        "unlock_id": "el_caudillo",
        "emoji": "🩸",
    },
    {
        "id": "gaucho_errante",
        "name": "Gaucho Errante",
        "name_en": "Wandering Gaucho",
        "desc": "Llegá al pueblo 8",
        "desc_en": "Reach town 8",
        "condition_key": "max_ante",
        "condition_value": 8,
        "unlock_type": "talisman",
        "unlock_id": "las_espuelas",
        "emoji": "🐴",
    },
    {
        "id": "mano_de_hierro",
        "name": "Mano de Hierro",
        "name_en": "Iron Hand",
        "desc": "Ganá 3 manos seguidas con Truco ×3+",
        "desc_en": "Win 3 hands in a row at Truco ×3+",
        "condition_key": "high_truco_streak",
        "condition_value": 3,
        "unlock_type": "poder",
        "unlock_id": "terremoto",
        "emoji": "🦾",
    },
    {
        "id": "diez_de_ultimo",
        "name": "Diez de Último",
        "name_en": "Last Stand",
        "desc": "Ganá una mesa con la última mano",
        "desc_en": "Clear a table on your last hand",
        "condition_key": "last_hand_wins",
        "condition_value": 1,
        "unlock_type": "talisman",
        "unlock_id": "el_milagro",
        "emoji": "🎲",
    },
    {
        "id": "triple_corona",
        "name": "Triple Corona",
        "name_en": "Triple Crown",
        "desc": "Ganá Envido, Flor y Truco en la misma mano",
        "desc_en": "Win Envido, Flor, and Truco in the same hand",
        "condition_key": "triple_crown",
        "condition_value": 1,
        "unlock_type": "edition",
        "unlock_id": "legendaria",
        "emoji": "🏅",
    },
]


def calc_prestigio(ante, won, wins, envidos, rachas, prestigio_mult=1.0):
    """Calculate prestigio earned at end of run."""
    base = ante * 10 + wins * 2 + envidos * 2 + rachas * 3 + (50 if won else 0)
    return int(base * prestigio_mult)


class MetaProgress:
    """Persistent meta-progression: fogón upgrades, challenges, prestigio."""

    def __init__(self):
        self.prestigio = 0
        self.fogon_levels = {}  # {upgrade_id: current_level}
        self.completed_challenges = set()
        self.difficulty = "normal"
        # Per-run tracking for challenge conditions
        self.run_stats = {}
        self.load()

    def load(self):
        if os.path.exists(META_FILE):
            try:
                with open(META_FILE) as f:
                    d = json.load(f)
                self.prestigio = d.get("prestigio", 0)
                self.fogon_levels = d.get("fogon_levels", {})
                self.completed_challenges = set(d.get("completed_challenges", []))
                self.difficulty = d.get("difficulty", "normal")
                self.run_stats = d.get("run_stats", {})
            except (json.JSONDecodeError, KeyError):
                pass

    def save(self):
        d = {
            "prestigio": self.prestigio,
            "fogon_levels": self.fogon_levels,
            "completed_challenges": sorted(self.completed_challenges),
            "difficulty": self.difficulty,
            "run_stats": self.run_stats,
        }
        with open(META_FILE, "w") as f:
            json.dump(d, f, indent=2)

    def get_upgrade_level(self, upgrade_id):
        return self.fogon_levels.get(upgrade_id, 0)

    def buy_upgrade(self, upgrade_id):
        """Buy next level of upgrade. Returns True if successful."""
        upg = next((u for u in FOGON_UPGRADES if u["id"] == upgrade_id), None)
        if not upg:
            return False
        current = self.get_upgrade_level(upgrade_id)
        if current >= upg["max_level"]:
            return False
        cost = upg["costs"][current]
        if self.prestigio < cost:
            return False
        self.prestigio -= cost
        self.fogon_levels[upgrade_id] = current + 1
        self.save()
        return True

    def get_upgrade_value(self, upgrade_id):
        """Get current effect value for an upgrade (0 if not bought)."""
        upg = next((u for u in FOGON_UPGRADES if u["id"] == upgrade_id), None)
        if not upg:
            return 0
        level = self.get_upgrade_level(upgrade_id)
        if level == 0:
            return 0
        return upg["values"][level - 1]

    def unlocked_items(self):
        """Return set of unlock_ids from completed challenges."""
        unlocked = set()
        for ch in DESAFIOS:
            if ch["id"] in self.completed_challenges:
                unlocked.add(ch["unlock_id"])
        return unlocked

    def endless_unlocked(self):
        return "endless" in self.unlocked_items()

    def max_talisman_slots(self):
        return 3 + self.get_upgrade_value("repertorio")

    def set_difficulty(self, tier):
        from difficulty import DIFFICULTY_ORDER
        if tier in DIFFICULTY_ORDER:
            self.difficulty = tier
            self.save()

    def get_difficulty_config(self):
        from difficulty import get_difficulty_config
        return get_difficulty_config(self.difficulty)

    def shop_discount(self):
        """Return discount fraction (0.0 to 0.30)."""
        val = self.get_upgrade_value("descuento")
        return val / 100.0 if val else 0.0

    def update_run_stat(self, key, value):
        """Update a run stat, keeping the max."""
        current = self.run_stats.get(key, 0)
        if isinstance(value, (int, float)) and value > current:
            self.run_stats[key] = value
        elif not isinstance(value, (int, float)):
            self.run_stats[key] = value

    def increment_run_stat(self, key, amount=1):
        """Increment a cumulative run stat."""
        self.run_stats[key] = self.run_stats.get(key, 0) + amount

    def check_challenges(self, collection):
        """Check all challenges against collection + run_stats. Returns newly completed."""
        newly_completed = []
        for ch in DESAFIOS:
            if ch["id"] in self.completed_challenges:
                continue
            key = ch["condition_key"]
            target = ch["condition_value"]
            # Check both collection and run_stats
            val = self.run_stats.get(key, 0)
            if hasattr(collection, key):
                attr = getattr(collection, key)
                if callable(attr):
                    val = max(val, attr)
                elif isinstance(attr, (int, float)):
                    val = max(val, attr)
                elif isinstance(attr, set):
                    val = max(val, len(attr))
            if val >= target:
                self.completed_challenges.add(ch["id"])
                newly_completed.append(ch)
        if newly_completed:
            self.save()
        return newly_completed
