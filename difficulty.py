"""Difficulty tiers for Trucazo."""

DIFFICULTY_ORDER = ["easy", "normal", "hard"]

DIFFICULTY_CONFIG = {
    "easy": {
        "label": "Fácil",
        "label_en": "Easy",
        "emoji": "\U0001f33f",
        "desc": "Objetivos bajos, Banca tranquila, plata extra",
        "desc_en": "Lower targets, calmer House, extra money",
        "blind_mult": 0.75,
        "ai_skill_offset": -0.15,
        "ai_envido_mult": 0.75,
        "ai_truco_mult": 0.70,
        "starting_money_bonus": 1,
        "income_bonus": 1,
        "prestigio_mult": 0.65,
    },
    "normal": {
        "label": "Normal",
        "label_en": "Normal",
        "emoji": "\u2696\ufe0f",
        "desc": "La experiencia estándar",
        "desc_en": "The standard experience",
        "blind_mult": 1.0,
        "ai_skill_offset": 0.0,
        "ai_envido_mult": 1.0,
        "ai_truco_mult": 1.0,
        "starting_money_bonus": 0,
        "income_bonus": 0,
        "prestigio_mult": 1.0,
    },
    "hard": {
        "label": "Difícil",
        "label_en": "Hard",
        "emoji": "\U0001f525",
        "desc": "Objetivos altos, Banca agresiva, más prestigio",
        "desc_en": "Higher targets, aggressive House, more prestige",
        "blind_mult": 1.30,
        "ai_skill_offset": 0.15,
        "ai_envido_mult": 1.30,
        "ai_truco_mult": 1.30,
        "starting_money_bonus": 0,
        "income_bonus": 0,
        "prestigio_mult": 1.50,
    },
}


def get_difficulty_config(tier):
    """Return config dict for a difficulty tier."""
    return DIFFICULTY_CONFIG.get(tier, DIFFICULTY_CONFIG["normal"])
