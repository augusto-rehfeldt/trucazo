"""Truco battle resolution, AI, and scoring for Trucazo."""
import random
from cards import Card, Palo, Poder, Edition, jerarquia, envido_score, tiene_flor, flor_score, fuerza_mano


class Banca:
    """AI opponent (The House). Skill scales with ante."""

    def __init__(self, skill=0.4, difficulty_cfg=None):
        self.skill = skill
        self._dcfg = difficulty_cfg or {}

    def elegir_carta(self, hand, ronda, mis_bazas, rival_bazas):
        """Pick which card to play."""
        if not hand:
            return None
        ranked = sorted(hand, key=jerarquia)
        if ronda == 0:
            return ranked[len(ranked) // 2]  # middle card
        if mis_bazas >= 1:
            return ranked[0]  # conserve: play weakest
        return ranked[-1]  # losing: play strongest

    def decidir_envido(self, mi_envido, apuesta_actual):
        if mi_envido >= 30:
            return "raise" if random.random() < self.skill * 0.6 else "accept"
        elif mi_envido >= 25:
            return "accept"
        elif mi_envido >= 20:
            return "accept" if random.random() < 0.4 + self.skill * 0.2 else "fold"
        else:
            return "fold" if random.random() < 0.7 else "accept"

    def decidir_truco(self, fuerza, apuesta_actual):
        if fuerza > 0.75:
            if apuesta_actual < 4 and random.random() < self.skill * 0.5:
                return "raise"
            return "accept"
        elif fuerza > 0.5:
            return "accept" if random.random() < 0.55 else "fold"
        elif fuerza > 0.3:
            return "accept" if random.random() < self.skill * 0.25 else "fold"
        else:
            return "fold"

    def quiere_cantar_truco(self, fuerza, apuesta_actual):
        ai_truco_mult = self._dcfg.get("ai_truco_mult", 1.0)
        if apuesta_actual >= 4:
            return False
        if fuerza > 0.8 and random.random() < self.skill * 0.4 * ai_truco_mult:
            return True
        if fuerza > 0.6 and random.random() < self.skill * 0.2 * ai_truco_mult:
            return True
        # Farol (bluff)
        if fuerza < 0.3 and random.random() < self.skill * 0.12 * ai_truco_mult:
            return True
        return False

    def quiere_cantar_envido(self, mi_envido):
        ai_env_mult = self._dcfg.get("ai_envido_mult", 1.0)
        thresh_high = int(28 / ai_env_mult)
        thresh_low = int(24 / ai_env_mult)
        if mi_envido >= thresh_high and random.random() < 0.6:
            return True
        if mi_envido >= thresh_low and random.random() < 0.3:
            return True
        return False


def resolver_baza(card_p, card_h, poder_activo=True):
    """Compare two cards. Returns 'player', 'house', or 'parda' (tie)."""
    p_rank = jerarquia(card_p)
    h_rank = jerarquia(card_h)

    # Poder: Hielo reduces opponent
    if poder_activo and card_p.poder == Poder.HIELO:
        h_rank = max(0, h_rank - 15)

    # Poder: Espejo copies opponent +1
    if poder_activo and card_p.poder == Poder.ESPEJO:
        p_rank = h_rank + 1

    if p_rank == h_rank:
        if poder_activo and card_p.poder == Poder.ESCUDO:
            return "player"
        return "parda"

    return "player" if p_rank > h_rank else "house"


def calcular_puntaje_mano(cards, truco_mult, racha=0, augments=None, levels=None):
    """Calculate score for winning a Truco hand.

    score = base_pts × truco_mult × edition_mult × racha_mult + bonuses
    """
    augments = augments or []
    levels = levels or {}

    base = sum(c.point_value for c in cards)

    # Poder bonuses
    for c in cards:
        if c.poder == Poder.ECO:
            base += c.point_value
        if c.poder == Poder.CADENA:
            base += 8 * racha
        if c.poder == Poder.FUEGO:
            base += 20
        if c.poder == Poder.TORMENTA:
            base += 25
        if c.poder == Poder.REFLEJO:
            base += c.point_value  # doubles like Eco
        if c.poder == Poder.TORNADO:
            base *= 3

    # Edition multipliers
    ed_mult = 1.0
    for c in cards:
        if c.edition == Edition.HOLOGRAFICA:
            ed_mult *= 1.5
        elif c.edition == Edition.PRISMATICA:
            ed_mult *= 2.0
        elif c.edition == Edition.ARCOIRIS:
            ed_mult *= 3.0
    if any(c.edition == Edition.BRILLANTE for c in cards):
        base += 15

    # Poder: Quiebre
    quiebre_mult = 1.0
    for c in cards:
        if c.poder == Poder.QUIEBRE:
            quiebre_mult *= 2.5

    # Racha (cascade combo)
    racha_level = levels.get("racha", 1)
    racha_mult = 1.0
    if racha > 1:
        base_bonuses = {2: 0.25, 3: 0.5, 4: 1.0}
        base_bonus = base_bonuses.get(racha, 1.5 if racha >= 5 else 0)
        bonus = base_bonus + (racha_level - 1) * 0.25 * (racha - 1)
        racha_mult = 1.0 + bonus

    # Augment bonuses
    aug_mult = 1.0
    aug_bonus = 0
    for aug in augments:
        eff = aug.effect
        if eff.get("type") == "palo_bonus":
            for c in cards:
                if c.palo.idx == eff["palo"]:
                    aug_bonus += eff["value"]
        if eff.get("type") == "truco_bonus":
            aug_mult *= eff["value"]

    # Level bonuses (Truquera cards)
    truco_level = levels.get("truco", 1)
    base += (truco_level - 1) * 5

    total = int((base + aug_bonus) * truco_mult * ed_mult * quiebre_mult * racha_mult * aug_mult)
    return max(total, 1)


def calcular_envido_puntaje(ganador_env, perdedor_env, nivel_envido=1):
    """Envido bonus points = base + diff × mult."""
    base = 2 + (nivel_envido - 1) * 2
    diff = abs(ganador_env - perdedor_env)
    return int(base + diff * (3 + (nivel_envido - 1)))


# ── TRUCO CALL LEVELS ──

TRUCO_NIVELES = [
    ("truco", 2, "Truco"),
    ("retruco", 3, "Retruco"),
    ("vale_cuatro", 4, "Vale Cuatro"),
]

ENVIDO_NIVELES = [
    ("envido", 2, "Envido"),
    ("real_envido", 4, "Real Envido"),
    ("falta_envido", 0, "Falta Envido"),  # 0 = all remaining
]