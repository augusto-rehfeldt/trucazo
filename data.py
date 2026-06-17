"""Game data: augments, bosses, shop, truquera cards for Trucazo."""
import random, math
from cards import Palo, Poder, Edition


class Talisman:
    """Passive augment (max 3 slots). Argentine-themed."""
    def __init__(self, name, desc, cost, effect, emoji="🔷", unlock_id=None):
        self.name = name
        self.desc = desc
        self.cost = cost
        self.effect = effect
        self.emoji = emoji
        self.sell_value = max(1, cost // 2)
        self.unlock_id = unlock_id  # ponytail: collocated; dissolves the name→id map
    def __repr__(self):
        return f"{self.emoji} {self.name}"


class Jefe:
    """Boss blind modifier."""
    def __init__(self, name, desc, effect, emoji="👹"):
        self.name = name
        self.desc = desc
        self.effect = effect
        self.emoji = emoji


ALL_TALISMANES = [
    Talisman("Mate Amargo", "+$2 extras después de cada mesa (ronda)", 4,
             {"type": "income", "value": 2}, "🧉"),
    Talisman("Gaucho", "Agrega +1 mano total para jugar a cada mesa", 6,
             {"type": "extra_hands", "value": 1}, "🤠"),
    Talisman("Compadre", "Suma +3 puntos fijos a todos tus Envidos", 5,
             {"type": "envido_bonus", "value": 3}, "🤝"),
    Talisman("Boleadoras", "Multiplicador de Truco final da +25% de puntos", 6,
             {"type": "truco_bonus", "value": 1.25}, "🪢"),
    Talisman("Poncho", "Si perdés el Envido, conservás un 30% de sus puntos", 4,
             {"type": "envido_shield", "value": 0.3}, "🧥"),
    Talisman("Facón", "Te reparte 1 carta extra (Robás 4 en total y descartás 1)", 5,
             {"type": "extra_draw", "value": 1}, "🔪"),
    Talisman("Bombilla", "Te permite ver el primer hueco de las cartas de la Banca", 5,
             {"type": "peek", "value": 1}, "🥤"),
    Talisman("Racha Gaucha", "Ganás $1 acumulable por cada racha de mano ganada ($2 por racha de 2, etc.)", 4,
             {"type": "cascade_money", "value": 1}, "🍀"),
    Talisman("Farolero", "La Banca se va al mazo un 15% más a menudo", 6,
             {"type": "fold_bonus", "value": 0.15}, "🎭"),
    Talisman("Espadas de Fuego", "Cada carta de ♠ Espadas te da +6 puntos planos al ganar baza", 4,
             {"type": "palo_bonus", "palo": 0, "value": 6}, "⚔️"),
    Talisman("Copas de Oro", "Cada carta de ♥ Copas te da +6 puntos planos al ganar baza", 4,
             {"type": "palo_bonus", "palo": 2, "value": 6}, "🏆"),
    Talisman("Bastos Negros", "Cada carta de ♣ Bastos te da +6 puntos planos al ganar baza", 4,
             {"type": "palo_bonus", "palo": 1, "value": 6}, "🪵"),
    Talisman("Oros Brillantes", "Cada carta de ♦ Oros te da +6 puntos planos al ganar baza", 4,
             {"type": "palo_bonus", "palo": 3, "value": 6}, "🪙"),
    Talisman("Amplificador", "Aumenta la fuerza de los ⚡ Poderes de cartas en un +50%", 7,
             {"type": "power_boost", "value": 0.5}, "📡"),
    Talisman("Fénix", "Revivís y repetís la mano si te quedás sin manos en la mesa por 1era vez", 8,
             {"type": "retry", "value": 1}, "🔥"),
    Talisman("Asador", "+$3 extras después de cada mesa (ronda)", 6,
             {"type": "income", "value": 3}, "🥩"),
    Talisman("Vino Patero", "Suma +4 puntos fijos a todos tus Envidos", 5,
             {"type": "envido_bonus", "value": 4}, "🍷"),
    Talisman("La Guitarra", "La Banca se va al mazo un 20% más a menudo", 6,
             {"type": "fold_bonus", "value": 0.20}, "🎸"),
]


# ── UNLOCKABLE CONTENT (from challenges) ──

UNLOCKABLE_TALISMANES = [
    Talisman("El Gringo", "Suma +5 puntos fijos a todos tus Envidos", 6,
             {"type": "envido_bonus", "value": 5}, "🤠", unlock_id="el_gringo"),
    Talisman("La Yapa", "Multiplica el dinero ganado por Rachas Gauchas x2", 5,
             {"type": "cascade_money", "value": 2}, "🎉", unlock_id="la_yapa"),
    Talisman("El Domador", "Reduce el debuff/efecto de los jefes en un 25%", 7,
             {"type": "boss_weaken", "value": 0.25}, "🦁", unlock_id="el_domador"),
    Talisman("El Purista", "+15 puntos base permanentes sin importar las cartas al ganar cada mano", 6,
             {"type": "base_bonus", "value": 15}, "🧘", unlock_id="el_purista"),
    Talisman("Cicatriz", "Si sobrevives con Cuero Duro pasás de mesa con +2 manos extra", 5,
             {"type": "survival_hands", "value": 2}, "💪", unlock_id="cicatriz"),
    Talisman("El Caudillo", "Agrega +1 mano total y te paga $1 extra de ingreso por mesa", 6,
             {"type": "extra_hands", "value": 1}, "🩸", unlock_id="el_caudillo"),
    Talisman("Las Espuelas", "Tu multiplicador de Racha empieza directamente en x2", 5,
             {"type": "cascade_money", "value": 1.5}, "🐴", unlock_id="las_espuelas"),
    Talisman("El Milagro", "+2 manos extra en la última mesa del Ante", 6,
             {"type": "extra_hands", "value": 2}, "🎲", unlock_id="el_milagro"),
]

UNLOCKABLE_PODERES = [
    # These are added to Poder enum via dynamic entries — we store them as dicts
    {"id": "tornado", "nombre": "Tornado", "desc": "Intercambiá la mejor carta rival",
     "desc_en": "Swap opponent's best card", "cost": 7},
    {"id": "alquimia", "nombre": "Alquimia", "desc": "Cada carta jugada da +$1",
     "desc_en": "Cards give +$1 each", "cost": 5},
    {"id": "perfume", "nombre": "Perfume", "desc": "Flor da ×2 bonus",
     "desc_en": "Flor gives ×2 bonus", "cost": 6},
]

UNLOCKABLE_EDITION = {
    "id": "arcoiris", "nombre": "Arcoíris", "desc": "×3 puntaje",
    "desc_en": "×3 score", "cost": 60,
}


ALL_JEFES = [
    Jefe("La Muerte", "⚔ Espadas tienen 0 jerarquía", "debuff_espadas", "💀"),
    Jefe("El Diablo", "🪵 Bastos tienen 0 jerarquía", "debuff_bastos", "😈"),
    Jefe("La Llorona", "🏆 Copas tienen 0 jerarquía", "debuff_copas", "👻"),
    Jefe("El Gaucho Malo", "🪙 Oros tienen 0 jerarquía", "debuff_oros", "🤠"),
    Jefe("El Muro", "Objetivo ×2", "wall", "🧱"),
    Jefe("El Ojo", "No repetir tipo de mano ganada", "no_repeat", "👁️"),
    Jefe("La Aguja", "Solo 3 manos esta ronda", "few_hands", "🪡"),
    Jefe("El Gancho", "Descarta 1 carta random al empezar", "hook", "🪝"),
    Jefe("La Víbora", "Envido desactivado", "no_envido", "🐍"),
    Jefe("El Espejo", "La Banca copia tus poderes", "mirror", "🪞"),
    Jefe("La Niebla", "No ves cartas de la Banca al jugar", "hidden", "🌫️"),
    Jefe("La Corona", "La Banca siempre juega primero", "crown", "👑"),
    Jefe("La Bruja", "Kiosco cuesta el doble", "expensive_shop", "🧙"),
    Jefe("El Matrero", "Tu racha se reinicia cada mesa", "no_cascade", "🐺"),
]


# ── TRUQUERA CARDS (like Balatro's Planet cards) ──
# Level up your scoring

TRUQUERA_CARDS = [
    {"name": "El Tanteador", "target": "envido", "desc": "Sube nivel Envido",
     "desc_en": "Level up Envido", "cost": 3},
    {"name": "El Matador", "target": "truco", "desc": "Sube nivel Truco",
     "desc_en": "Level up Truco", "cost": 3},
    {"name": "La Florista", "target": "flor", "desc": "Sube nivel Flor",
     "desc_en": "Level up Flor", "cost": 4},
    {"name": "El Encadenado", "target": "racha", "desc": "Sube nivel Racha",
     "desc_en": "Level up Cascade", "cost": 4},
]


def get_blind_target(ante, blind_type, difficulty_mult=1.0):
    base = {
        1: (50, 80, 125),         # intro: learn the ropes
        2: (80, 130, 200),        # need some truco/envido
        3: (130, 200, 325),       # upgrades start helping
        4: (200, 325, 500),       # mid-game: talismanes matter
        5: (325, 500, 800),       # hard: need combos
        6: (500, 800, 1200),      # very hard: full toolkit
        7: (800, 1200, 1800),     # extreme
        8: (1200, 1800, 2500),    # final: all-in
    }
    if ante > 8:
        b = 1200 * (2 ** (ante - 8))
        targets = (b, int(b * 1.5), b * 2)
    else:
        targets = base[ante]
    idx = {"small": 0, "big": 1, "boss": 2}[blind_type]
    return int(targets[idx] * difficulty_mult)


def get_blind_reward(blind_type):
    return {"small": 3, "big": 4, "boss": 5}[blind_type]


def get_random_jefe(exclude=None):
    pool = ALL_JEFES if not exclude else [j for j in ALL_JEFES if j.name not in exclude]
    if not pool:  # Endless mode crash fix if all bosses are exhausted
        pool = ALL_JEFES
        if exclude is not None:
            exclude.clear()
    return random.choice(pool)


def get_shop_talismanes(n=2, owned=None, unlocked=None):
    owned = owned or []
    pool = [t for t in ALL_TALISMANES if t.name not in owned]
    # Add unlockable talismanes if unlocked
    if unlocked:
        for ut in UNLOCKABLE_TALISMANES:
            if ut.unlock_id in unlocked and ut.name not in owned:
                pool.append(ut)
    if not pool:
        return []
    sel = random.sample(pool, min(n, len(pool)))
    return [Talisman(t.name, t.desc, t.cost, t.effect, t.emoji) for t in sel]


def get_shop_poderes(n=3, unlocked=None):
    unlocked = unlocked or set()
    pool = [p for p in Poder if p != Poder.NADA]
    
    # Filter locked unlockables out
    if "tornado" not in unlocked: pool.remove(Poder.TORNADO)
    if "alquimia" not in unlocked: pool.remove(Poder.ALQUIMIA)
    if "perfume" not in unlocked: pool.remove(Poder.PERFUME)
        
    return random.sample(pool, min(n, len(pool)))


def get_shop_ediciones(n=2, unlocked=None):
    unlocked = unlocked or set()
    pool = [e for e in Edition if e != Edition.COMUN]
    
    # Filter locked unlockables out
    if "arcoiris" not in unlocked: pool.remove(Edition.ARCOIRIS)
        
    return random.sample(pool, min(n, len(pool)))


def get_random_truquera():
    return random.choice(TRUQUERA_CARDS).copy()


def apply_discount(cost, discount_pct):
    """Apply discount fraction (0.0-0.3) to a cost. Returns int."""
    if discount_pct <= 0:
        return cost
    return max(1, math.floor(cost * (1.0 - discount_pct)))
