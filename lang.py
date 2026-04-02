"""Internationalization for Trucazo."""

LANGS = {
    "es": {
        "title_sub": "El Camino del Truquero",
        "new_run": "Nueva Partida",
        "continue_run": "Continuar Partida",
        "collection": "Colección",
        "how_to_play": "Cómo Jugar",
        "language": "English",
        "language_label": "Idioma",
        "quit": "Salir",
        "ante": "Pueblo",
        "small_blind": "Mesa de Entrada",
        "big_blind": "Mesa de Fondo",
        "boss_blind": "Mesa del Patrón",
        "target": "Objetivo",
        "hands": "Manos restantes",
        "score": "Puntos",
        "money": "Plata",
        "your_hand": "TU MANO",
        "the_house": "LA BANCA",
        "round_of": "Ronda {n} de 3",
        "envido": "Envido",
        "real_envido": "Real Envido",
        "falta_envido": "Falta Envido",
        "truco": "Truco",
        "retruco": "Retruco",
        "vale_cuatro": "Vale Cuatro",
        "quiero": "Quiero",
        "no_quiero": "No Quiero",
        "flor": "Flor",
        "contraflor": "Contraflor",
        "play_card": "Jugar carta",
        "you_win": "¡GANASTE!",
        "house_wins": "GANA LA BANCA",
        "tie": "PARDA",
        "hand_won": "¡Mano Ganada!",
        "hand_lost": "Mano Perdida",
        "blind_cleared": "¡MESA GANADA!",
        "blind_failed": "MESA PERDIDA",
        "game_over": "FIN DEL JUEGO",
        "victory": "¡VICTORIA!",
        "shop": "KIOSCO",
        "augments": "Talismanes",
        "powers": "Poderes",
        "editions": "Ediciones",
        "buy": "Comprar",
        "sell": "Vender",
        "reroll": "Cambiar",
        "next_round": "Siguiente",
        "press_enter": "[ Presioná Enter ]",
        "press_enter_back": "[ Presioná Enter para volver al juego ]",
        "press_enter_return": "[ Presioná Enter para volver ]",
        "deck": "Mazo",
        "info": "Info",
        "cards_remaining": "{n} cartas",
        "fold": "Te fuiste",
        "house_folds": "¡La Banca no quiso!",
        "accepts": "¡Quiero!",
        "declines": "No quiero",
        "cascade_combo": "Racha",
        "income": "Ingreso",
        "interest": "Interés",
        "reward": "Premio",
        "run_stats": "Estadísticas",
        "total_runs": "Partidas",
        "wins": "Victorias",
        "best_ante": "Mejor Pueblo",
        "discovered": "Descubiertos",
        "select_lang": "Idioma",
        "not_enough": "¡No alcanza la plata!",
        "not_enough_money": "¡No alcanza la plata!",
        "slots_full": "¡Sin espacio!",
        "max_augments": "¡Máximo 3 talismanes!",
        "confirm_play": "¿Jugás esta carta? [s/n]",
        "choose": "Elegí",
        "play": "Jugar",
        "invalid": "Opción inválida",
        "cancel": "Cancelar",
        "nothing_to_sell": "Nada para vender",
        "no_eligible_cards": "No hay cartas elegibles",
        "income_label": "ingreso",
        "thanks": "¡Gracias por jugar Trucazo!",
        # Meta-progression
        "fogon": "El Fogón",
        "desafios": "Desafíos",
        "prestigio": "Prestigio",
        "fogon_title": "EL FOGÓN",
        "fogon_subtitle": "Mejoras permanentes",
        "desafios_title": "DESAFÍOS",
        "desafios_subtitle": "Completá retos para desbloquear contenido",
        "upgrade": "Mejorar",
        "max_level": "MÁX",
        "locked": "Bloqueado",
        "unlocked": "Desbloqueado",
        "completed": "Completado",
        "new_challenge": "¡NUEVO DESAFÍO COMPLETADO!",
        "prestigio_earned": "Prestigio ganado",
        "run_summary": "Resumen de partida",
        "ante_reached": "Pueblo alcanzado",
        "buy_upgrade": "Comprar mejora",
        "back": "Volver",
        "endless_mode": "Modo Infinito",
        "endless_unlocked": "¡MODO INFINITO DESBLOQUEADO!",
        "endless_desc": "Jugá más allá del pueblo 8",
        "not_enough_prestigio": "¡No alcanza el prestigio!",
        "level": "Nivel",
        "cost_label": "Costo",
        "effect_label": "Efecto",
        "unlocks": "Desbloquea",
        "progress": "Progreso",
        "cuero_duro_saved": "¡Cuero Duro te salvó!",
        # Difficulty
        "difficulty_title": "DIFICULTAD",
        "difficulty_label": "Dificultad",
        "diff_desc_easy": "Objetivos bajos, Banca tranquila, plata extra",
        "diff_desc_normal": "La experiencia estándar",
        "diff_desc_hard": "Objetivos altos, Banca agresiva, más prestigio",
        "current": "actual",
        "settings": "Configuración",
        # Card names
        "espadas": "Espadas",
        "bastos": "Bastos",
        "copas": "Copas",
        "oros": "Oros",
        "sota": "Sota",
        "caballo": "Caballo",
        "rey": "Rey",
        "as": "As",
        # How to play
        "htp_title": "CÓMO JUGAR",
        "htp_text": """
  {b}TRUCAZO{r} {d}— El Camino del Truquero{d}
  Viajá como un truquero por 8 pueblos argentinos.
  En cada pueblo, enfrentá 3 mesas cada vez más bravas:
  Mesa de Entrada, Mesa de Fondo y la Mesa del Patrón.

  {b}CADA MESA:{r}
  Vos y La Banca reciben 3 cartas de la baraja española (40 cartas).
  Se juega al mejor de 3 bazas. En cada baza, jugás 1 carta.
  La carta con mayor jerarquía gana. Superá el puntaje objetivo
  para avanzar. Si te quedás sin manos, perdés.

  {b}JERARQUÍA DE CARTAS:{r} {d}(como el Truco real){d}
  1⚔ > 1🪵 > 7⚔ > 7🪙 > 3 > 2 > 1🏆 1🪙 > 12 > 11 > 10 > 7🏆 7🪵 > 6 > 5 > 4

  {b}ENVIDO:{r} {d}(apuesta de puntos){d}
  Antes de jugar cartas, podés cantar {o}Envido{r}.
  Puntos = 20 + suma de valores del mismo palo (1-7; 10,11,12 = 0).
  Máximo: 33. El que gana suma puntos bonus.

  {b}FLOR:{r} {d}(3 cartas del mismo palo){d}
  Si tus 3 cartas son del mismo palo, tenés {p}Flor{r}!
  Cantala para un bonus grande. La Flor mata al Envido.

  {b}TRUCO:{r} {d}(subir la apuesta){d}
  Cantá {rr}Truco{r} para multiplicar los puntos en juego.
  Truco(×2) → Retruco(×3) → Vale Cuatro(×4)
  La Banca puede aceptar, irse, o redoblar.

  {b}RACHA:{r} {d}(combo gaucho){d}
  Ganar manos seguidas multiplica tus puntos:
  2 seguidas: {g}×1.25{r}  3: {y}×1.5{r}  4: {o}×2.0{r}  5+: {rr}×2.5{r}

  {b}ENTRE MESAS:{r}
  Visitá el {go}Kiosco{r}: comprá Talismanes (buffs pasivos, máx 3),
  Poderes para tus cartas, y Ediciones especiales.
  Cartas Truqueras suben de nivel tus envidos/trucos.

  {b}EDICIONES:{r} {d}(estilo visual + bonus){d}
  {go}Dorada{r}: +$2 al ganar  │  {b}Brillante{r}: +15 pts
  {p}Holográfica{r}: ×1.5 puntaje  │  {rr}Prismática{r}: ×2 puntaje

  {b}PODERES:{r} {d}(efecto al jugar la carta){d}
  Comprá poderes en el Kiosco. Se aplican a una carta
  random de tu mazo. Cada carta puede tener 1 poder.
  Ej: ⚡Fuego (+20 pts), ⚡Hielo (-15 rival), ⚡Rayo (×1.5)

  {b}EL FOGÓN:{r} {d}(progresión permanente){d}
  Ganás {go}Prestigio{r} al final de cada partida.
  Usalo en El Fogón para comprar mejoras que persisten
  entre partidas. Completá Desafíos para desbloquear contenido.

  {b}COMANDOS:{r}
  {d}1/2/3{d} Jugar carta  │  {d}e{d} Envido  │  {d}f{d} Flor
  {d}t{d} Truco          │  {d}i{d} Info     │  {d}q{d} Salir
""",
    },
    "en": {
        "title_sub": "The Truquero's Road",
        "new_run": "New Run",
        "continue_run": "Continue Run",
        "collection": "Collection",
        "how_to_play": "How to Play",
        "language": "Español",
        "language_label": "Language",
        "quit": "Quit",
        "ante": "Town",
        "small_blind": "Entry Table",
        "big_blind": "Back Table",
        "boss_blind": "Patrón's Table",
        "target": "Target",
        "hands": "Hands left",
        "score": "Score",
        "money": "Money",
        "your_hand": "YOUR HAND",
        "the_house": "THE HOUSE",
        "round_of": "Round {n} of 3",
        "envido": "Envido",
        "real_envido": "Real Envido",
        "falta_envido": "Falta Envido",
        "truco": "Truco",
        "retruco": "Retruco",
        "vale_cuatro": "Vale Cuatro",
        "quiero": "Quiero (Accept)",
        "no_quiero": "No Quiero (Fold)",
        "flor": "Flor",
        "contraflor": "Contraflor",
        "play_card": "Play card",
        "you_win": "YOU WIN!",
        "house_wins": "HOUSE WINS",
        "tie": "TIE",
        "hand_won": "Hand Won!",
        "hand_lost": "Hand Lost",
        "blind_cleared": "TABLE CLEARED!",
        "blind_failed": "TABLE FAILED",
        "game_over": "GAME OVER",
        "victory": "VICTORY!",
        "shop": "SHOP",
        "augments": "Augments",
        "powers": "Powers",
        "editions": "Editions",
        "buy": "Buy",
        "sell": "Sell",
        "reroll": "Reroll",
        "next_round": "Next",
        "press_enter": "[ Press Enter ]",
        "press_enter_back": "[ Press Enter to return to game ]",
        "press_enter_return": "[ Press Enter to return ]",
        "deck": "Deck",
        "info": "Info",
        "cards_remaining": "{n} cards",
        "fold": "You fold",
        "house_folds": "House folds!",
        "accepts": "Quiero!",
        "declines": "No quiero",
        "cascade_combo": "Cascade",
        "income": "Income",
        "interest": "Interest",
        "reward": "Reward",
        "run_stats": "Run Stats",
        "total_runs": "Total Runs",
        "wins": "Wins",
        "best_ante": "Best Town",
        "discovered": "Discovered",
        "select_lang": "Language",
        "not_enough": "Not enough money!",
        "not_enough_money": "Not enough money!",
        "slots_full": "Slots full!",
        "max_augments": "Max 3 augments!",
        "confirm_play": "Play this card? [y/n]",
        "choose": "Choose",
        "play": "Play",
        "invalid": "Invalid option",
        "cancel": "Cancel",
        "nothing_to_sell": "Nothing to sell",
        "no_eligible_cards": "No eligible cards",
        "income_label": "income",
        "thanks": "Thanks for playing Trucazo!",
        # Meta-progression
        "fogon": "The Campfire",
        "desafios": "Challenges",
        "prestigio": "Prestige",
        "fogon_title": "THE CAMPFIRE",
        "fogon_subtitle": "Permanent upgrades",
        "desafios_title": "CHALLENGES",
        "desafios_subtitle": "Complete challenges to unlock new content",
        "upgrade": "Upgrade",
        "max_level": "MAX",
        "locked": "Locked",
        "unlocked": "Unlocked",
        "completed": "Completed",
        "new_challenge": "NEW CHALLENGE COMPLETED!",
        "prestigio_earned": "Prestige earned",
        "run_summary": "Run summary",
        "ante_reached": "Town reached",
        "buy_upgrade": "Buy upgrade",
        "back": "Back",
        "endless_mode": "Endless Mode",
        "endless_unlocked": "ENDLESS MODE UNLOCKED!",
        "endless_desc": "Play beyond town 8",
        "not_enough_prestigio": "Not enough prestige!",
        "level": "Level",
        "cost_label": "Cost",
        "effect_label": "Effect",
        "unlocks": "Unlocks",
        "progress": "Progress",
        "cuero_duro_saved": "Tough Hide saved you!",
        # Difficulty
        "difficulty_title": "DIFFICULTY",
        "difficulty_label": "Difficulty",
        "diff_desc_easy": "Lower targets, calmer House, extra money",
        "diff_desc_normal": "The standard experience",
        "diff_desc_hard": "Higher targets, aggressive House, more prestige",
        "current": "current",
        "settings": "Settings",
        "espadas": "Swords",
        "bastos": "Clubs",
        "copas": "Cups",
        "oros": "Coins",
        "sota": "Jack",
        "caballo": "Knight",
        "rey": "King",
        "as": "Ace",
        "htp_title": "HOW TO PLAY",
        "htp_text": """
  {b}TRUCAZO{r} {d}— The Truquero's Road{d}
  Travel as a card sharp through 8 Argentine towns.
  At each town, face 3 increasingly tough tables:
  Entry Table, Back Table, and the Patrón's Table.

  {b}EACH TABLE:{r}
  You and The House each get 3 cards from a 40-card Spanish deck.
  Play best-of-3 rounds. Each round: play 1 card vs The House.
  Higher battle rank wins. Reach the score target to advance.
  Run out of hands and you lose.

  {b}CARD HIERARCHY:{r} {d}(real Argentine Truco){d}
  1⚔ > 1🪵 > 7⚔ > 7🪙 > 3 > 2 > 1🏆 1🪙 > 12 > 11 > 10 > 7🏆 7🪵 > 6 > 5 > 4

  {b}ENVIDO:{r} {d}(point bet){d}
  Before playing cards, call {o}Envido{r} to bet on point values.
  Score = 20 + sum of same-suit card values (1-7 only; 10,11,12 = 0).
  Max: 33. Winner gets bonus points.

  {b}FLOR:{r} {d}(3 cards, same suit){d}
  If all 3 cards share a suit, you have {p}Flor{r}!
  Call it for a big bonus. Flor trumps Envido.

  {b}TRUCO:{r} {d}(raise the stakes){d}
  Call {rr}Truco{r} to multiply the points at stake!
  Truco(×2) → Retruco(×3) → Vale Cuatro(×4)
  Opponent can accept, fold, or re-raise.

  {b}CASCADE:{r} {d}(gaucho combo){d}
  Win consecutive hands for increasing multipliers:
  2 in a row: {g}×1.25{r}  3: {y}×1.5{r}  4: {o}×2.0{r}  5+: {rr}×2.5{r}

  {b}BETWEEN TABLES:{r}
  Visit the {go}Shop{r}: buy Augments (passive buffs, max 3),
  card Powers, and Editions. Truquera cards level up your plays.

  {b}EDITIONS:{r} {d}(visual flair + bonuses){d}
  {go}Golden{r}: +$2 on win  │  {b}Shiny{r}: +15 pts
  {p}Holographic{r}: ×1.5 score  │  {rr}Prismatic{r}: ×2 score

  {b}POWERS:{r} {d}(effect when card is played){d}
  Buy powers at the Shop. Applied to a random card in
  your deck. Each card can have 1 power.
  E.g.: ⚡Fire (+20 pts), ⚡Ice (-15 rival), ⚡Lightning (×1.5)

  {b}THE CAMPFIRE:{r} {d}(permanent progression){d}
  Earn {go}Prestige{r} at the end of each run.
  Spend it at The Campfire for upgrades that persist
  between runs. Complete Challenges to unlock new content.

  {b}COMMANDS:{r}
  {d}1/2/3{d} Play card  │  {d}e{d} Envido  │  {d}f{d} Flor
  {d}t{d} Truco         │  {d}i{d} Info     │  {d}q{d} Quit
""",
    },
}

# Active language (default Spanish since it's a Truco game)
_lang = "es"


def set_lang(lang_code):
    global _lang
    _lang = lang_code


def get_lang():
    return _lang


def t(key, **kwargs):
    """Get translated string."""
    text = LANGS.get(_lang, LANGS["es"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
