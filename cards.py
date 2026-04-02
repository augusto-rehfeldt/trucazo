"""Spanish baraja cards for Trucazo.

40-card deck: 4 suits × 10 ranks (1-7, 10, 11, 12).
No 8s or 9s, just like the real Truco deck.
"""
import random
from enum import Enum


class Palo(Enum):
    """Spanish card suits (palos)."""
    ESPADAS = (0, "⚔", "Espadas", "⚔")    # Swords
    BASTOS = (1, "🪵", "Bastos", "🪵")      # Clubs/Sticks
    COPAS = (2, "🏆", "Copas", "🏆")       # Cups
    OROS = (3, "🪙", "Oros", "🪙")          # Coins/Gold

    @property
    def idx(self):
        return self.value[0]

    @property
    def symbol(self):
        return self.value[1]

    @property
    def nombre(self):
        return self.value[2]

    @property
    def icon(self):
        """Emoji icon for expanded displays (hierarchy, collection)."""
        return self.value[3]


# The 10 ranks in a Spanish Truco deck
TRUCO_RANKS = (1, 2, 3, 4, 5, 6, 7, 10, 11, 12)


class Edition(Enum):
    """Card editions (Balatro-style visual flair + bonuses)."""
    COMUN = ("", "", 0)
    DORADA = ("Dorada", "+$2 al ganar", 20)
    BRILLANTE = ("Brillante", "+15 pts", 25)
    HOLOGRAFICA = ("Holo", "×1.5 puntaje", 35)
    PRISMATICA = ("Prismática", "×2 puntaje", 50)
    ARCOIRIS = ("Arcoíris", "×3 puntaje", 60)

    @property
    def nombre(self):
        return self.value[0]

    @property
    def desc(self):
        return self.value[1]

    @property
    def cost(self):
        return self.value[2]


class Poder(Enum):
    """Card powers (special effects when played)."""
    NADA = ("", "", 0)
    FUEGO = ("Fuego", "+20 pts al ganar", 4)
    HIELO = ("Hielo", "Rival -15 jerarquía", 5)
    RAYO = ("Rayo", "×1.5 si gana baza", 6)
    ESCUDO = ("Escudo", "Gana empates (pardas)", 4)
    FANTASMA = ("Fantasma", "Vuelve a la mano", 6)
    ESPEJO = ("Espejo", "Copia jerarquía rival +1", 7)
    ECO = ("Eco", "Puntúa valor ×2", 5)
    QUIEBRE = ("Quiebre", "×2.5 pts, carta destruida", 8)
    ORO = ("Oro", "+$2 al jugarla", 3)
    VENENO = ("Veneno", "+10 pts si perdés baza", 5)
    SOMBRA = ("Sombra", "Rival no ve tu palo", 4)
    CADENA = ("Cadena", "+8 pts por racha", 4)
    TORMENTA = ("Tormenta", "+25 pts si ganás la mano", 6)
    REFLEJO = ("Reflejo", "Duplica pts de la baza", 6)
    CUCHILLO = ("Cuchillo", "+$3 al ganar baza", 4)
    # Unlockables
    TORNADO = ("Tornado", "×3 pts al ganar la mano", 7)
    ALQUIMIA = ("Alquimia", "+$1 al jugarla", 5)
    PERFUME = ("Perfume", "Multiplica score de Flor ×2", 6)

    @property
    def nombre(self):
        return self.value[0]

    @property
    def desc(self):
        return self.value[1]

    @property
    def cost(self):
        return self.value[2]


class Card:
    _next_id = 0

    def __init__(self, rank, palo, edition=Edition.COMUN, poder=Poder.NADA):
        self.rank = rank       # int: 1-7, 10, 11, 12
        self.palo = palo       # Palo enum
        self.edition = edition
        self.poder = poder
        Card._next_id += 1
        self.id = Card._next_id

    @property
    def rank_label(self):
        return str(self.rank)

    @property
    def label(self):
        return f"{self.rank_label}{self.palo.symbol}"

    @property
    def envido_val(self):
        """Envido face value: 1-7 = face value, 10/11/12 = 0."""
        return self.rank if self.rank <= 7 else 0

    @property
    def point_value(self):
        """Base point value for scoring."""
        return self.rank if self.rank <= 7 else {10: 8, 11: 9, 12: 10}[self.rank]

    @property
    def has_poder(self):
        return self.poder != Poder.NADA

    @property
    def has_edition(self):
        return self.edition != Edition.COMUN

    def __repr__(self):
        parts = [self.label]
        if self.has_edition:
            parts.append(f"[{self.edition.nombre}]")
        if self.has_poder:
            parts.append(f"({self.poder.nombre})")
        return " ".join(parts)


# ── TRUCO CARD HIERARCHY ──
# Exact real Argentine Truco hierarchy

def jerarquia(card):
    """Battle rank - higher wins. Real Argentine Truco hierarchy."""
    r, p = card.rank, card.palo.idx

    # Los 4 mejores (the big 4)
    if r == 1 and p == 0:   return 100  # 1 de Espadas (Ancho de Espadas)
    if r == 1 and p == 1:   return 99   # 1 de Bastos (Ancho de Bastos)
    if r == 7 and p == 0:   return 98   # 7 de Espadas
    if r == 7 and p == 3:   return 97   # 7 de Oros

    # Cartas por grupo
    bases = {
        3: 90,    # Tres
        2: 85,    # Dos
        1: 80,    # Ancho falso (1 de Copas / 1 de Oros)
        12: 75,   # Rey
        11: 70,   # Caballo
        10: 65,   # Sota
        7: 55,    # 7 de Copas / 7 de Bastos
        6: 50,
        5: 45,
        4: 40,
    }

    base = bases.get(r, 20)

    # Edition bonus
    if card.edition == Edition.BRILLANTE:
        base += 5

    return base


# ── ENVIDO SCORING ──

def envido_valor(card):
    """Envido value of a single card."""
    return card.envido_val


def envido_score(cards):
    """Calculate envido for a 3-card hand (real Truco rules).

    - 2+ cards same suit: 20 + sum of two highest envido values
    - No same-suit pair: highest single envido value
    """
    by_palo = {}
    for c in cards:
        by_palo.setdefault(c.palo, []).append(c)

    best = 0
    for palo, palo_cards in by_palo.items():
        if len(palo_cards) >= 2:
            vals = sorted([envido_valor(c) for c in palo_cards], reverse=True)
            score = 20 + vals[0] + vals[1]
            best = max(best, score)

    if best == 0:
        if not cards:
            return 0
        best = max(envido_valor(c) for c in cards)

    return best


def tiene_flor(cards):
    """Check for Flor (3 cards same suit)."""
    if len(cards) != 3:
        return False
    return len(set(c.palo for c in cards)) == 1


def flor_score(cards):
    """Flor score (like envido: 20 + two highest same-suit values)."""
    vals = sorted([envido_valor(c) for c in cards], reverse=True)
    return 20 + vals[0] + vals[1]


def fuerza_mano(cards):
    """Hand strength 0-1 for AI decisions."""
    avg = sum(jerarquia(c) for c in cards) / max(len(cards), 1)
    return min(avg / 95.0, 1.0)


class Mazo:
    """40-card Spanish Truco deck."""

    def __init__(self):
        self.all_cards = []
        self.cards = []
        self.discard = []
        self.init_deck()

    def init_deck(self):
        self.all_cards = [Card(r, p) for r in TRUCO_RANKS for p in Palo]
        self.restaurar()

    def restaurar(self):
        self.cards = self.all_cards.copy()
        self.discard = []
        self.mezclar()

    def mezclar(self):
        random.shuffle(self.cards)
        
    def reshuffle_discard(self):
        self.cards.extend(self.discard)
        self.discard = []
        self.mezclar()

    def sacar(self, n=1):
        drawn = []
        while len(drawn) < n:
            if not self.cards:
                self.reshuffle_discard()
                if not self.cards:
                    break
            drawn.append(self.cards.pop(0))
        return drawn

    def devolver(self, cards):
        self.cards.extend(cards)
        random.shuffle(self.cards)
        
    def al_descarte(self, cards):
        self.discard.extend(cards)

    def __len__(self):
        return len(self.cards)


# ── AUTO-EDITION (rare random editions on dealt cards) ──

# Base chance per card to get a random edition (2%)
AUTO_EDITION_BASE_CHANCE = 0.02

# Weighted rarity: lower = rarer
AUTO_EDITION_WEIGHTS = {
    Edition.DORADA: 40,
    Edition.BRILLANTE: 30,
    Edition.HOLOGRAFICA: 20,
    Edition.PRISMATICA: 10,
}


def maybe_apply_auto_edition(cards, bonus_chance=0.0):
    """Roll for auto-editions on freshly dealt cards.

    Args:
        cards: list of Card objects (mutated in-place).
        bonus_chance: extra chance from fogón upgrade (e.g. 0.03 for +3%).
    """
    chance = AUTO_EDITION_BASE_CHANCE + bonus_chance
    editions = list(AUTO_EDITION_WEIGHTS.keys())
    weights = list(AUTO_EDITION_WEIGHTS.values())
    for c in cards:
        if c.edition != Edition.COMUN:
            continue  # already has an edition
        if random.random() < chance:
            c.edition = random.choices(editions, weights=weights, k=1)[0]
