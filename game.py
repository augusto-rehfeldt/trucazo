"""Main game engine for Trucazo."""
import random, time, os, pickle, re
from cards import Mazo, Poder, Edition, jerarquia, envido_score, tiene_flor, flor_score, fuerza_mano
from hands import Banca, resolver_baza, calcular_puntaje_mano, calcular_envido_puntaje, calcular_racha_mult, TRUCO_NIVELES
from data import (
                  get_blind_target, get_blind_reward, get_random_jefe,
                  get_shop_talismanes, get_shop_poderes, get_shop_ediciones,
                  get_random_truquera, apply_discount)
from collection import Collection
from meta import MetaProgress, calc_prestigio
from display import (center,
                     render_battle, render_baza_result, render_hand_result, render_envido_result,
                     render_flor_result, render_truco_call, render_actions,
                     render_shop, render_game_over, render_blind_intro, render_deck_view,
                     render_levels, render_hierarchy, render_how_to_play, render_collection,
                     render_fogon, render_challenges, render_run_end_prestigio, render_endless_unlock,
                     render_difficulty_select,
                     check_terminal_size,
                     D, R, B, GRN, NRED, NYEL, ORNG, PURP, GOLD, CYAN)
from lang import t, set_lang, get_lang
from difficulty import DIFFICULTY_ORDER, DIFFICULTY_CONFIG, get_difficulty_config

SAVE_FILE = "autosave.pkl"

def save_game(gs, ante, blind_i):
    with open(SAVE_FILE, "wb") as f:
        pickle.dump({"gs": gs, "ante": ante, "blind_i": blind_i}, f)

def delete_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


class GameState:
    def __init__(self, meta=None):
        self.mazo = Mazo()
        self.money = 4
        self.talismanes = []
        self.levels = {"truco": 1, "envido": 1, "flor": 1, "racha": 1}
        self.racha = 0
        self.hands_base = 4
        self.collection = Collection()
        self.jefes_vistos = set()
        self.boss_effect = None
        self.meta = meta or MetaProgress()
        self.cuero_duro_available = False
        self.powers_bought = 0  # Track for asceta challenge
        self.max_money_seen = 4  # Track for millonario challenge
        self.run_manos_ganadas = 0
        self.run_envidos_ganados = 0
        self.run_max_racha = 0
        self._last_breakdown = None  # Score breakdown for display
        self.log = []

        # Difficulty config
        self._difficulty_cfg = get_difficulty_config(self.meta.difficulty)
        self._difficulty_income_bonus = self._difficulty_cfg.get("income_bonus", 0)

        # Apply difficulty starting money bonus
        self.money += self._difficulty_cfg.get("starting_money_bonus", 0)

        # Apply fogón upgrades
        self.money += self.meta.get_upgrade_value("mate_inicial")
        self.hands_base += self.meta.get_upgrade_value("mano_firme")
        self.racha = self.meta.get_upgrade_value("sangre_gaucha")
        if self.meta.get_upgrade_value("cuero_duro"):
            self.cuero_duro_available = True
        corazon = self.meta.get_upgrade_value("corazon_de_leon")
        if corazon:
            self.levels["truco"] = corazon
        # Herencia: start with random talisman
        if self.meta.get_upgrade_value("herencia"):
            from data import get_shop_talismanes
            gift = get_shop_talismanes(1, [], self.meta.unlocked_items())
            if gift:
                self.talismanes.append(gift[0])
                self.collection.discovered_talismanes.add(gift[0].name)

    def add_log(self, text):
        self.log.append(text)
        if len(self.log) > 5:
            self.log.pop(0)

    @property
    def talisman_slots(self):
        return self.meta.max_talisman_slots()

    @property
    def hands_total(self):
        bonus = sum(1 for a in self.talismanes if a.effect.get("type") == "extra_hands")
        return self.hands_base + bonus

    def income(self):
        base = 1
        bonus = sum(a.effect["value"] for a in self.talismanes if a.effect.get("type") == "income")
        meta_bonus = self.meta.get_upgrade_value("billetera_gruesa")
        return base + bonus + meta_bonus + self._difficulty_income_bonus

    def has_effect(self, etype):
        return any(a.effect.get("type") == etype for a in self.talismanes)

    def effect_value(self, etype):
        return sum(a.effect.get("value", 0) for a in self.talismanes if a.effect.get("type") == etype)

    def envido_bonus(self):
        return int(self.effect_value("envido_bonus"))

    def fold_bonus(self):
        return self.effect_value("fold_bonus")

    def power_boost(self):
        return self.effect_value("power_boost")


def _get_racha_mult(gs):
    return calcular_racha_mult(gs.racha, gs.levels.get("racha", 1))


def _score_hand(gs, cards, truco_mult, env_bonus, ante):
    """Calculate total hand score."""
    pts = calcular_puntaje_mano(cards, truco_mult, gs.racha, gs.talismanes, gs.levels)

    # Power boost from Amplificador
    boost = gs.power_boost()
    power_cards = []
    if boost > 0:
        power_cards = [c for c in cards if c.has_poder]
        if power_cards:
            pts = int(pts * (1 + boost))

    env = max(0, env_bonus)
    pts += env

    if gs.collection.best_envido < env_bonus:
        gs.collection.best_envido = env_bonus

    pts = max(pts, 1)

    # Build breakdown for display
    parts = []
    card_base = sum(c.point_value for c in cards)
    parts.append(f"{card_base} base")
    if truco_mult > 1:
        parts.append(f"truco ×{truco_mult}")
        
    racha_mult = _get_racha_mult(gs)
    if racha_mult > 1.0:
        parts.append(f"racha ×{racha_mult:g}")
        
    if boost > 0 and power_cards:
        parts.append(f"amplif. ×{1 + boost:.1f}")
    if env > 0:
        parts.append(f"envido +{env}")
    gs._last_breakdown = " │ ".join(parts)

    return pts

# ── ENVIDO PHASE ──

def envido_phase(gs, player_hand, house_hand, banca):
    """Handle envido/real envido/falta envido. Returns bonus points for player."""
    if gs.boss_effect == "no_envido":
        return 0

    p_env = envido_score(player_hand) + gs.envido_bonus()
    h_env = envido_score(house_hand)
    p_flor = tiene_flor(player_hand)
    h_flor = tiene_flor(house_hand)

    # Flor beats envido
    if p_flor and h_flor:
        return flor_phase(gs, player_hand, house_hand, banca)
    if p_flor:
        p_fs = flor_score(player_hand)
        gs.collection.flores += 1
        nivel = gs.levels.get("flor", 1)
        pts = int((3 + (nivel - 1) * 2) + p_fs * 0.5)
        
        racha_mult = _get_racha_mult(gs)
        pts = int(pts * racha_mult)

        render_flor_result("player", p_fs, "-", pts)
        gs.collection.save()
        return pts

    # AI might call envido first
    if banca.quiere_cantar_envido(h_env):
        print(f"\n  {ORNG}{B}La Banca canta: ¡Envido!{R}")
        time.sleep(0.5)
        ch = input(f"  {GRN}[Q]{R}uiero │ {NRED}[N]{R}o quiero │ {ORNG}[S]{R}ubir → ")
        if ch == "n":
            return -1  # lost 1 pt
        elif ch == "s":
            return _envido_showdown(gs, p_env, h_env, mult=2)
        else:
            return _envido_showdown(gs, p_env, h_env, mult=1)

    return 0  # no envido called


def flor_phase(gs, player_hand, house_hand, banca):
    p_fs = flor_score(player_hand)
    h_fs = flor_score(house_hand)
    gs.collection.flores += 1
    # Poder: Perfume
    if any(c.poder == Poder.PERFUME for c in player_hand):
        p_fs *= 2
        print(f"  {PURP}🌸 Perfume: Score de flor duplicado!{R}")
        gs.add_log(f"{PURP}🌸 Perfume: Score de flor duplicado!{R}")
        
    h_fs = flor_score(house_hand)
    gs.collection.flores += 1
    nivel = gs.levels.get("flor", 1)
    pts = int((3 + (nivel - 1) * 2) + abs(p_fs - h_fs) * 0.5)
    
    racha_mult = _get_racha_mult(gs)
    pts = int(pts * racha_mult)

    if p_fs >= h_fs:
        res, log_s = render_flor_result("player", p_fs, h_fs, pts)
        gs.add_log(log_s)
        gs.collection.save()
        return pts
    else:
        res, log_s = render_flor_result("house", p_fs, h_fs, pts)
        gs.add_log(log_s)
        return 0


def _envido_showdown(gs, p_env, h_env, mult=1):
    nivel = gs.levels.get("envido", 1)
    if p_env >= h_env:
        pts = calcular_envido_puntaje(p_env, h_env, nivel) * mult
        
        racha_mult = _get_racha_mult(gs)
        pts = int(pts * racha_mult)

        res, log_s = render_envido_result("player", p_env, h_env, pts)
        gs.add_log(log_s)
        gs.collection.envidos_ganados += 1
        gs.run_envidos_ganados += 1
        gs.collection.save()
        return pts
    else:
        res, log_s = render_envido_result("house", p_env, h_env, 0)
        gs.add_log(log_s)
        return 0


# ── TRUCO HAND ──

def play_truco_hand(gs, ante, blind_type, blind_name, target, score, hands_left=0):
    """Play one Truco hand (3-round card battle). Returns points earned."""
    gs.mazo.mezclar()

    # Deal 3 cards each
    extra = 1 if gs.has_effect("extra_draw") else 0
    p_draw = gs.mazo.sacar(3 + extra)
    if extra:
        # Show all, player picks 3
        msg_choose = "elegí 3 de" if get_lang() == "es" else "choose 3 of"
        msg_cards = "cartas" if get_lang() == "es" else "cards"
        hint = "(ej: 1 2 3)" if get_lang() == "es" else "(ex: 1 2 3)"
        
        print(f"\n  {PURP}Facón: {msg_choose} {len(p_draw)} {msg_cards} {D}{hint}{R}")
        from display import render_cards
        for ln in render_cards(p_draw, show_idx=True):
            print(f"  {ln}")
        chosen = set()
        while len(chosen) < 3:
            prompt_str = "Cartas elegidas" if get_lang() == "es" else "Chosen cards"
            ch = input(f"\n  {prompt_str} ({len(chosen)}/3) → ")
            nums = re.findall(r'\d+', ch)
            if nums:
                for n in nums:
                    try:
                        idx = int(n) - 1
                        if 0 <= idx < len(p_draw) and idx not in chosen:
                            chosen.add(idx)
                        if len(chosen) == 3:
                            break
                    except ValueError:
                        pass
        player_hand = [p_draw[i] for i in sorted(chosen)]
        leftovers = [p_draw[i] for i in range(len(p_draw)) if i not in chosen]
        gs.mazo.devolver(leftovers)
    else:
        player_hand = p_draw

    house_hand = gs.mazo.sacar(3)

    # Auto-editions: rare chance for dealt cards to spawn with an edition
    from cards import maybe_apply_auto_edition
    edition_bonus = gs.meta.get_upgrade_value("ojo_de_lince") / 100.0 if hasattr(gs, 'meta') else 0.0
    maybe_apply_auto_edition(player_hand, edition_bonus)

    # Boss: El Gancho discards 1
    if gs.boss_effect == "hook" and player_hand:
        discarded = random.choice(player_hand)
        player_hand.remove(discarded)
        print(f"\n  {NRED}🪝 El Gancho descarta tu {discarded.label}!{R}")
        time.sleep(0.5)

    banca_skill = min(0.3 + ante * 0.08, 0.9) + gs._difficulty_cfg.get("ai_skill_offset", 0.0)
    banca_skill = max(0.05, min(banca_skill, 0.95))
    banca = Banca(skill=banca_skill, difficulty_cfg=gs._difficulty_cfg)

    # Truco stake
    truco_idx = 0  # 0=normal(×1), 1=truco(×2), 2=retruco(×3), 3=vale4(×4)
    stake_mult = 1
    stake_name = t("play")

    # Peek (Bombilla talisman)
    peek_idx = None
    if gs.has_effect("peek"):
        peek_idx = 0  # show first house card slot

    # Sexto Sentido: show house envido hint
    if gs.meta.get_upgrade_value("sexto_sentido"):
        h_env_hint = envido_score(house_hand)
        bracket = "≤20" if h_env_hint <= 20 else ("21-27" if h_env_hint <= 27 else "28+")
        print(f"  {D}👁️ Sexto Sentido: envido rival ~{bracket}{R}")

    # Envido phase (only in round 0, before cards are played)
    p_env_score = envido_score(player_hand) + gs.envido_bonus()
    h_env_score = envido_score(house_hand)
    p_flor = tiene_flor(player_hand)

    player_played = []
    house_played = []
    p_wins = 0
    h_wins = 0
    env_bonus = 0
    env_done = False
    truco_called = False

    battle_kw = dict(
        score=score, target=target, hands_left=hands_left,
        tals=gs.talismanes, tal_slots=gs.talisman_slots,
        ante=ante, blind_type=blind_type, blind_name=blind_name,
        env_bonus=0, event_log=gs.log)

    for ronda in range(3):
        if not player_hand or len([c for c in player_hand if c not in player_played]) == 0:
            break

        remaining = [c for c in player_hand if c not in player_played]
        h_remaining = [c for c in house_hand if c not in house_played]
        if not remaining or not h_remaining:
            break

        # Render battle state
        battle_kw['money'] = gs.money
        render_battle(player_hand, house_played, player_played, ronda, p_wins, h_wins,
                     stake_name, stake_mult, envido_p=p_env_score if ronda == 0 else None,
                     flor_flag=p_flor if ronda == 0 else False,
                     peek_idx=peek_idx if ronda == 0 else None, **battle_kw)

        # Boss: La Corona → house plays first
        house_first = gs.boss_effect == "crown"

        # AI might call truco
        h_fuerza = fuerza_mano(h_remaining)
        if not truco_called and truco_idx < 3 and banca.quiere_cantar_truco(h_fuerza, stake_mult):
            nxt = TRUCO_NIVELES[min(truco_idx, len(TRUCO_NIVELES)-1)]
            render_truco_call("house", nxt[2])
            time.sleep(0.3)
            ch = input(f"  {GRN}[Q]{R}uiero │ {NRED}[N]{R}o quiero │ {ORNG}[S]{R}ubir → ")
            if ch == "n":
                return 0  # fold, house wins hand
            elif ch == "s" and truco_idx + 1 < len(TRUCO_NIVELES):
                truco_idx += 1
                nxt2 = TRUCO_NIVELES[truco_idx]
                render_truco_call("player", nxt2[2])
                time.sleep(0.3)
                dec = banca.decidir_truco(h_fuerza, nxt2[1])
                if dec == "fold":
                    # House folds on our raise
                    prev = TRUCO_NIVELES[truco_idx - 1]
                    stake_mult = prev[1]
                    stake_name = prev[2]
                    truco_called = True
                    print(f"  {GRN}La Banca no quiso. {stake_name} ×{stake_mult}{R}")
                    time.sleep(0.3)
                else:
                    stake_mult = nxt2[1]
                    stake_name = nxt2[2]
                    truco_called = True
            else:
                stake_mult = nxt[1]
                stake_name = nxt[2]
                truco_called = True
            # Re-render after truco resolution to clear banners
            battle_kw['money'] = gs.money
            render_battle(player_hand, house_played, player_played, ronda, p_wins, h_wins,
                         stake_name, stake_mult,
                         envido_p=p_env_score if ronda == 0 and not env_done else None,
                         flor_flag=p_flor if ronda == 0 and not env_done else False,
                         peek_idx=peek_idx if ronda == 0 else None, **battle_kw)

        # Show actions
        can_env = ronda == 0 and not env_done and gs.boss_effect != "no_envido"
        can_truco = not truco_called and truco_idx < len(TRUCO_NIVELES)
        n_remaining = len(remaining)
        render_actions(can_env=can_env, can_truco=can_truco, flor=p_flor and ronda == 0 and not env_done, n_cards=n_remaining)

        # Player input loop
        card_idx = None
        while card_idx is None:
            ch = input(f"\n  {t('choose')}: ")
            if ch == "q":
                return -999  # quit signal
            elif ch == "a":
                print(f"\n  {PURP}{B}─── Aumentos Equipados ───{R}")
                for a in gs.talismanes:
                    print(f"  {a.emoji} {a.name}: {a.desc}")
                print(f"\n  {CYAN}{B}─── Poderes de tus cartas ({len([c for c in player_hand if c.has_poder])}) ───{R}")
                for c in player_hand:
                    if c.has_poder:
                        print(f"  {c.label}: ⚡ {c.poder.nombre} - {c.poder.desc}")
                if not any(c.has_poder for c in player_hand):
                    print(f"  {D}(Sin poderes esta mano){R}")

                from display import ED_C
                eds = [c for c in player_hand if c.has_edition]
                print(f"\n  {PURP}{B}─── Ediciones de tus cartas ({len(eds)}) ───{R}")
                for c in eds:
                    ec = ED_C.get(c.edition.nombre, PURP)
                    print(f"  {c.label}: {ec}{c.edition.nombre}{R} - {c.edition.desc}")
                if not eds:
                    print(f"  {D}(Sin ediciones esta mano){R}")

                input(center(f"\n  {D}{t('press_enter_back')}{R}"))
                battle_kw['money'] = gs.money
                render_battle(player_hand, house_played, player_played, ronda, p_wins, h_wins,
                             stake_name, stake_mult, envido_p=p_env_score if ronda == 0 else None,
                             flor_flag=p_flor if ronda == 0 else False, **battle_kw)
                render_actions(can_env=can_env, can_truco=can_truco, flor=p_flor and ronda == 0 and not env_done, n_cards=n_remaining)
            elif ch == "i":
                render_hierarchy()
                render_levels(gs.levels)
                input(center(f"\n  {D}{t('press_enter_back')}{R}"))
                # Re-render
                battle_kw['money'] = gs.money
                render_battle(player_hand, house_played, player_played, ronda, p_wins, h_wins,
                             stake_name, stake_mult, envido_p=p_env_score if ronda == 0 else None,
                             flor_flag=p_flor if ronda == 0 else False, **battle_kw)
                render_actions(can_env=can_env, can_truco=can_truco, flor=p_flor and ronda == 0 and not env_done, n_cards=n_remaining)
            elif ch == "e" and can_env:
                env_bonus = _player_envido(gs, p_env_score, h_env_score, banca)
                env_done = True
                can_env = False
                battle_kw['env_bonus'] = env_bonus
                time.sleep(0.5)
                battle_kw['money'] = gs.money
                render_battle(player_hand, house_played, player_played, ronda, p_wins, h_wins,
                             stake_name, stake_mult, **battle_kw)
                can_truco = not truco_called and truco_idx < len(TRUCO_NIVELES)
                render_actions(can_env=False, can_truco=can_truco, flor=False, n_cards=n_remaining)
            elif ch == "f" and p_flor and ronda == 0 and not env_done:
                env_bonus = flor_phase(gs, player_hand, house_hand, banca)
                env_done = True
                can_env = False
                battle_kw['env_bonus'] = env_bonus
                time.sleep(0.5)
                battle_kw['money'] = gs.money
                render_battle(player_hand, house_played, player_played, ronda, p_wins, h_wins,
                             stake_name, stake_mult, **battle_kw)
                can_truco = not truco_called and truco_idx < len(TRUCO_NIVELES)
                render_actions(can_env=False, can_truco=can_truco, flor=False, n_cards=n_remaining)
            elif ch == "t" and can_truco:
                nxt_idx = truco_idx
                nxt = TRUCO_NIVELES[nxt_idx]
                render_truco_call("player", nxt[2])
                time.sleep(0.3)
                dec = banca.decidir_truco(h_fuerza, nxt[1])
                fold_chance = gs.fold_bonus()
                if dec == "fold" or (dec != "raise" and random.random() < fold_chance):
                    print(f"  {GRN}{B}La Banca no quiso!{R}")
                    # Win with previous stake
                    if truco_idx > 0:
                        prev = TRUCO_NIVELES[truco_idx - 1]
                        return _score_hand(gs, player_hand, prev[1], env_bonus, ante)
                    return _score_hand(gs, player_hand, 1, env_bonus, ante)
                elif dec == "raise" and nxt_idx + 1 < len(TRUCO_NIVELES):
                    truco_idx = nxt_idx + 1
                    nxt2 = TRUCO_NIVELES[truco_idx]
                    render_truco_call("house", nxt2[2])
                    time.sleep(0.3)
                    rch = input(f"  {GRN}[Q]{R}uiero │ {NRED}[N]{R}o quiero → ")
                    if rch == "n":
                        return 0
                    stake_mult = nxt2[1]
                    stake_name = nxt2[2]
                else:
                    truco_idx = nxt_idx + 1
                    stake_mult = nxt[1]
                    stake_name = nxt[2]
                truco_called = True
                # Re-render after truco resolution
                battle_kw['money'] = gs.money
                render_battle(player_hand, house_played, player_played, ronda, p_wins, h_wins,
                             stake_name, stake_mult,
                             envido_p=p_env_score if ronda == 0 and not env_done else None,
                             flor_flag=p_flor if ronda == 0 and not env_done else False, **battle_kw)
                can_truco = False
                render_actions(can_env=can_env, can_truco=False, flor=p_flor and ronda == 0 and not env_done, n_cards=n_remaining)
            else:
                try:
                    idx = int(ch) - 1
                    if 0 <= idx < n_remaining:
                        card_idx = idx
                except ValueError:
                    pass

        player_card = remaining[card_idx]
        player_played.append(player_card)

        # House plays
        house_card = banca.elegir_carta(h_remaining, ronda, h_wins, p_wins)
        house_played.append(house_card)

        # Resolve
        winner = resolver_baza(player_card, house_card)

        # Boss: debuff palos
        if gs.boss_effect and gs.boss_effect.startswith("debuff_"):
            debuff_palo = {"debuff_espadas": 0, "debuff_bastos": 1, "debuff_copas": 2, "debuff_oros": 3}
            dp = debuff_palo.get(gs.boss_effect)
            if dp is not None:
                if player_card.palo.idx == dp:
                    winner = "house" if winner == "player" else winner

        p_rank = jerarquia(player_card)
        h_rank = jerarquia(house_card)
        baza_res = render_baza_result(winner, player_card, house_card, p_rank, h_rank)
        gs.add_log(baza_res)

        if winner == "player":
            p_wins += 1
            # Poder: Rayo bonus
            if player_card.poder == Poder.RAYO:
                print(f"    {NYEL}⚡ Rayo: ×1.5 esta baza!{R}")
                gs.add_log(f"{NYEL}⚡ Rayo: ×1.5 esta baza!{R}")
            # Poder: Oro
            if player_card.poder == Poder.ORO:
                gs.money += 2
                print(f"    {GOLD}💰 Oro: +$2{R}")
                gs.add_log(f"{GOLD}💰 Oro: +$2{R}")
            if player_card.poder == Poder.CUCHILLO:
                gs.money += 3
                print(f"    {GOLD}🔪 Cuchillo: +$3{R}")
                gs.add_log(f"{GOLD}🔪 Cuchillo: +$3{R}")
            # Poder: Alquimia
            if player_card.poder == Poder.ALQUIMIA:
                gs.money += 1
                print(f"    {GOLD}⚗️ Alquimia: +$1{R}")
                gs.add_log(f"{GOLD}⚗️ Alquimia: +$1{R}")
            # Poder: Reflejo
            if player_card.poder == Poder.REFLEJO:
                print(f"    {CYAN}🪞 Reflejo: ×2 pts esta baza!{R}")
                gs.add_log(f"{CYAN}🪞 Reflejo: ×2 pts esta baza!{R}")
        elif winner == "house":
            h_wins += 1
            # Poder: Veneno — consolation points when you lose baza
            if player_card.poder == Poder.VENENO:
                veneno_pts = 10
                env_bonus += veneno_pts
                print(f"    {PURP}☠ Veneno: +{veneno_pts} pts de consuelo{R}")
                gs.add_log(f"{PURP}☠ Veneno: +{veneno_pts} pts de consuelo{R}")
        # parda: small consolation to incentivize playing
        if winner == "parda":
            parda_pts = 1
            env_bonus += parda_pts
            print(f"    {D}Parda: +{parda_pts} pt{R}")
            gs.add_log(f"{D}Parda: +{parda_pts} pt{R}")

        time.sleep(0.8)

        # Check for hand winner
        if p_wins >= 2:
            break
        if h_wins >= 2:
            break
        # Parda logic: if round 3, most wins or first baza winner
        if ronda == 2 and p_wins == h_wins:
            # First baza winner takes it (real Truco rule)
            break

    if p_wins > h_wins:
        hand_winner = "player"
    elif h_wins > p_wins:
        hand_winner = "house"
    else:
        # Tie: first baza winner wins (real Truco rule for parda)
        hand_winner = "player" if p_wins > 0 else "house"

    if hand_winner == "player":
        gs.racha += 1
        gs.collection.manos_ganadas += 1
        gs.run_manos_ganadas += 1
        if gs.collection.rachas < gs.racha:
            gs.collection.rachas = gs.racha
        if gs.racha > gs.run_max_racha:
            gs.run_max_racha = gs.racha
        # Track vale cuatro wins for challenge
        if stake_mult >= 4 and hasattr(gs, 'meta'):
            gs.meta.increment_run_stat("vale_cuatro_wins")
        pts = _score_hand(gs, player_played, stake_mult, env_bonus, ante)
        render_hand_result("player", pts, gs.racha, getattr(gs, '_last_breakdown', None))

        # Cascade money from talisman
        if gs.has_effect("cascade_money") and gs.racha > 1:
            cm = int(gs.effect_value("cascade_money") * gs.racha)
            gs.money += cm
            print(f"    {GOLD}🍀 Racha Gaucha: +${cm}{R}")

        # Poder: Fantasma returns to hand (for next hand)
        for c in player_played:
            if c.poder == Poder.FANTASMA:
                print(f"    {CYAN}👻 Fantasma: vuelve al mazo{R}")
                gs.mazo.devolver([c])

        # Edition: Dorada gives money
        for c in player_played:
            if c.edition == Edition.DORADA:
                gs.money += 2
                print(f"    {GOLD}✦ Dorada: +$2{R}")

        # Update best hand
        if pts > gs.collection.best_hand:
            gs.collection.best_hand = pts

        # Discover items
        for c in player_played:
            if c.has_poder:
                gs.collection.discovered_poderes.add(c.poder.nombre)
            if c.has_edition:
                gs.collection.discovered_ediciones.add(c.edition.nombre)
        gs.collection.save()

        # Update lists of played vs unplayed
        unplayed_p = [c for c in player_hand if c not in player_played]
        unplayed_h = [c for c in house_hand if c not in house_played]
        
        # Return Fantasmas properly (even if you lose the hand, returning below applies to both)
        fantasmas = [c for c in player_played if c.poder == Poder.FANTASMA]
        if fantasmas:
            print(f"    {CYAN}👻 Fantasma: {len(fantasmas)} carta(s) vuelve(n) al mazo{R}")
            gs.mazo.devolver(fantasmas)

        discarded = [c for c in player_played + house_played if c not in fantasmas]
        gs.mazo.al_descarte(discarded + unplayed_p + unplayed_h)

        time.sleep(0.5)
        return pts
    else:
        gs.racha = 0
        gs.collection.manos_perdidas += 1
        gs.collection.save()

        # Consolation: score partial points for bazas won
        consolation = 0
        if p_wins > 0:
            winning_cards = [player_played[i] for i in range(len(player_played))
                            if i < len(house_played) and resolver_baza(player_played[i], house_played[i]) == "player"]
            consolation = sum(c.point_value for c in winning_cards)
            consolation += max(0, env_bonus)

        render_hand_result("house", consolation, 0)

        if consolation > 0:
            print(f"  {D}  ({p_wins} baza{'s' if p_wins > 1 else ''} ganada{'s' if p_wins > 1 else ''} → +{consolation} pts){R}")

        # Fénix retry
        if gs.has_effect("retry"):
            for a in gs.talismanes:
                if a.effect.get("type") == "retry" and a.effect.get("value", 0) > 0:
                    a.effect["value"] = 0
                    print(f"  {NRED}🔥 Fénix: ¡Segunda oportunidad!{R}")
                    time.sleep(0.5)
                    gs.mazo.al_descarte(player_played + house_played + [c for c in player_hand if c not in player_played] + [c for c in house_hand if c not in house_played])
                    return play_truco_hand(gs, ante, blind_type, blind_name, target, score)

        # Update lists of played vs unplayed for loss logic
        unplayed_p = [c for c in player_hand if c not in player_played]
        unplayed_h = [c for c in house_hand if c not in house_played]
        
        # Return Fantasmas on loss too
        fantasmas = [c for c in player_played if c.poder == Poder.FANTASMA]
        if fantasmas:
            print(f"    {CYAN}👻 Fantasma: {len(fantasmas)} carta(s) vuelve(n) al mazo{R}")
            gs.mazo.devolver(fantasmas)

        discarded = [c for c in player_played + house_played if c not in fantasmas]
        gs.mazo.al_descarte(discarded + unplayed_p + unplayed_h)

        time.sleep(0.5)
        return consolation


def _player_envido(gs, p_env, h_env, banca):
    """Player calls envido."""
    print(f"\n  {ORNG}{B}¡Envido!{R}")
    gs.add_log(f"{ORNG}¡Envido!{R}")
    dec = banca.decidir_envido(h_env, 2)
    if dec == "fold":
        nivel_envido = gs.levels.get("envido", 1)
        pts = 1 + (nivel_envido - 1)
        racha_mult = _get_racha_mult(gs)
        pts = int(pts * racha_mult)
        print(f"  {GRN}La Banca no quiso. +{pts} pt{'s' if pts!=1 else ''}{R}")
        gs.add_log(f"{GRN}La Banca no quiso. +{pts} pt{'s' if pts!=1 else ''}{R}")
        gs.collection.envidos_ganados += 1
        gs.run_envidos_ganados += 1
        gs.collection.save()
        return pts
    elif dec == "raise":
        print(f"  {ORNG}{B}La Banca: ¡Real Envido!{R}")
        gs.add_log(f"{ORNG}La Banca: ¡Real Envido!{R}")
        ch = input(f"  {GRN}[Q]{R}uiero │ {NRED}[N]{R}o quiero → ")
        if ch == "n":
            return -1
        return _envido_showdown(gs, p_env, h_env, mult=2)
    else:
        return _envido_showdown(gs, p_env, h_env, mult=1)


# ── BLIND / ROUND ──

def run_blind(gs, ante, blind_type, boss=None):
    """Run a single blind (small/big/boss). Returns True if target reached."""
    target = get_blind_target(ante, blind_type, gs._difficulty_cfg.get("blind_mult", 1.0))
    blind_name = ""

    if boss and blind_type == "boss":
        gs.boss_effect = boss.effect
        blind_name = f"{boss.emoji} {boss.name}"
        gs.collection.discovered_jefes.add(boss.name)
        # Boss: El Muro doubles target
        if boss.effect == "wall":
            target *= 2
        # Boss: La Aguja limits hands
        if boss.effect == "few_hands":
            hands_left = 3
        # Boss: El Matrero resets cascade
        elif boss.effect == "no_cascade":
            gs.racha = 0
            hands_left = gs.hands_total
        else:
            hands_left = gs.hands_total
    else:
        gs.boss_effect = None
        hands_left = gs.hands_total

    render_blind_intro(ante, blind_type, target, boss if blind_type == "boss" else None)
    input("")

    score = 0

    while hands_left > 0 and score < target:
        pts = play_truco_hand(gs, ante, blind_type, blind_name, target, score, hands_left)

        if pts == -999:
            return None  # quit

        score += pts
        hands_left -= 1

        if score >= target:
            print(f"\n  {GRN}{B}┏{'━' * 38}┓{R}")
            title = f"★ {t('blind_cleared')} ★".upper()
            score_str = f"{score:,} / {target:,} pts"
            print(f"  {GRN}{B}┃{title:^38}┃{R}")
            print(f"  {GRN}{B}┃{score_str:^38}┃{R}")
            print(f"  {GRN}{B}┗{'━' * 38}┛{R}")
            reward = get_blind_reward(blind_type)
            gs.money += reward + gs.income()
            print(f"    {GOLD}💰 +${reward} {t('reward')}  │  +${gs.income()} {t('income_label')}{R}")
            time.sleep(0.5)
            input(f"\n{center(f'{D}{t('press_enter')}{R}')}")
            return True

        if hands_left > 0 and score < target:
            input(f"\n{center(f'{D}{t('press_enter')}{R}')}")

    if score < target:
        print(f"\n  {NRED}{B}┏{'━' * 38}┓{R}")
        title = f"✗ {t('blind_failed')} ✗".upper()
        score_str = f"{score:,} / {target:,} pts"
        print(f"  {NRED}{B}┃{title:^38}┃{R}")
        print(f"  {NRED}{B}┃{score_str:^38}┃{R}")
        print(f"  {NRED}{B}┗{'━' * 38}┛{R}")
        time.sleep(0.5)
        # Cuero Duro second chance
        if gs.cuero_duro_available:
            gs.cuero_duro_available = False
            gs.meta.increment_run_stat("cuero_duro_used")
            print(f"  {GOLD}{B}🛡️ {t('cuero_duro_saved')}{R}")
            # Survival hands bonus from Cicatriz talisman
            survival_bonus = int(gs.effect_value("survival_hands"))
            if survival_bonus:
                print(f"  {PURP}💪 Cicatriz: +{survival_bonus} manos{R}")
            time.sleep(0.5)
            input(f"\n{center(f'{D}{t('press_enter')}{R}')}")
            return True
        input(f"\n  {D}{t('press_enter')}{R}")
        return False

    return True


# ── SHOP ──

def run_shop(gs, ante):
    """Between-round shop."""
    reroll_cost = 3
    owned_names = [a.name for a in gs.talismanes]
    unlocked = gs.meta.unlocked_items()
    discount = gs.meta.shop_discount()

    # Boss: La Bruja makes shop more expensive
    if gs.boss_effect == "expensive_shop":
        discount = max(0, discount - 0.5)  # Effectively doubles prices

    tals = get_shop_talismanes(2, owned_names, unlocked)
    pods = get_shop_poderes(3, unlocked)
    eds = get_shop_ediciones(2, unlocked)
    truqs = [get_random_truquera()]

    # Apply discount to items
    if discount > 0:
        for a in tals:
            a.cost = apply_discount(a.cost, discount)
            a.sell_value = max(1, a.cost // 2)
        for tr in truqs:
            tr["cost"] = apply_discount(tr["cost"], discount)

    while True:
        render_shop(tals, pods, eds, truqs, gs.money, reroll_cost, gs.talismanes, gs.talisman_slots)
        ch = input(f"  {t('choose')}: ")

        if ch == "q":
            return None
        elif ch == "n":
            return True
        elif ch == "d":
            render_deck_view(gs.mazo.cards)
            input(center(f"{D}{t('press_enter')}{R}"))
        elif ch == "r":
            if gs.money >= reroll_cost:
                gs.money -= reroll_cost
                reroll_cost += 1
                tals = get_shop_talismanes(2, owned_names, unlocked)
                pods = get_shop_poderes(3, unlocked)
                eds = get_shop_ediciones(2, unlocked)
                truqs = [get_random_truquera()]
                if discount > 0:
                    for a in tals:
                        a.cost = apply_discount(a.cost, discount)
                        a.sell_value = max(1, a.cost // 2)
                    for tr in truqs:
                        tr["cost"] = apply_discount(tr["cost"], discount)
            else:
                print(f"  {NRED}{t('not_enough_money')}{R}")
                time.sleep(0.3)
        elif ch == "v":
            _sell_menu(gs)
        else:
            try:
                idx = int(ch)
                items = list(tals) + list(pods) + list(eds) + list(truqs)
                if 1 <= idx <= len(items):
                    item = items[idx - 1]
                    if _buy_item(gs, item, idx, tals, pods, eds, truqs):
                        owned_names = [a.name for a in gs.talismanes]
                else:
                    print(f"  {D}{t('invalid')}{R}")
            except ValueError:
                pass


def _buy_item(gs, item, idx, tals, pods, eds, truqs):
    """Buy a shop item. Returns True if purchased."""
    # Determine type
    tal_count = len(tals)
    pod_count = len(pods)
    ed_count = len(eds)

    if idx <= tal_count:
        # Talisman
        tal = tals[idx - 1]
        if gs.money < tal.cost:
            print(f"  {NRED}{t('not_enough_money')}{R}"); time.sleep(0.3); return False
        if len(gs.talismanes) >= gs.talisman_slots:
            print(f"  {NRED}{t('max_augments')}{R}"); time.sleep(0.3); return False
        gs.money -= tal.cost
        gs.talismanes.append(tal)
        gs.collection.discovered_talismanes.add(tal.name)
        gs.collection.save()
        print(f"  {GRN}✓ {tal.emoji} {tal.name}{R}")
        tals.pop(idx - 1)
        time.sleep(0.3)
        return True

    elif idx <= tal_count + pod_count:
        # Poder
        pidx = idx - tal_count - 1
        pod = pods[pidx]
        if gs.money < pod.cost:
            print(f"  {NRED}{t('not_enough_money')}{R}"); time.sleep(0.3); return False
        gs.money -= pod.cost
        gs.powers_bought += 1
        # Apply to random card in deck
        eligible = [c for c in gs.mazo.cards if c.poder == Poder.NADA]
        if eligible:
            target = random.choice(eligible)
            target.poder = pod
            print(f"  {GRN}✓ ⚡{pod.nombre} → {target.label}{R}")
            gs.collection.discovered_poderes.add(pod.nombre)
        else:
            print(f"  {NYEL}{t('no_eligible_cards')}{R}")
        gs.collection.save()
        pods.pop(pidx)
        time.sleep(0.3)
        return True

    elif idx <= tal_count + pod_count + ed_count:
        # Edition
        eidx = idx - tal_count - pod_count - 1
        ed = eds[eidx]
        if gs.money < ed.cost:
            print(f"  {NRED}{t('not_enough_money')}{R}"); time.sleep(0.3); return False
        gs.money -= ed.cost
        eligible = [c for c in gs.mazo.cards if c.edition == Edition.COMUN]
        if eligible:
            target = random.choice(eligible)
            target.edition = ed
            print(f"  {GRN}✓ {ed.nombre} → {target.label}{R}")
            gs.collection.discovered_ediciones.add(ed.nombre)
        else:
            print(f"  {NYEL}{t('no_eligible_cards')}{R}")
        gs.collection.save()
        eds.pop(eidx)
        time.sleep(0.3)
        return True

    else:
        # Truquera
        tidx = idx - tal_count - pod_count - ed_count - 1
        if tidx < len(truqs):
            tr = truqs[tidx]
            if gs.money < tr["cost"]:
                print(f"  {NRED}{t('not_enough_money')}{R}"); time.sleep(0.3); return False
            gs.money -= tr["cost"]
            key = tr["target"]
            gs.levels[key] = gs.levels.get(key, 1) + 1
            print(f"  {GRN}✓ 🃏 {tr['name']} → {key} nivel {gs.levels[key]}{R}")
            truqs.pop(tidx)
            time.sleep(0.3)
            return True

    return False


def _sell_menu(gs):
    if not gs.talismanes:
        print(f"  {D}{t('nothing_to_sell')}{R}")
        time.sleep(0.3)
        return
    print(f"\n  {ORNG}{B}─── {t('sell')} ───{R}")
    for i, a in enumerate(gs.talismanes):
        print(f"  [{i+1}] {a.emoji} {a.name} → ${a.sell_value}")
    print(f"  [0] {t('cancel')}")
    ch = input(f"  {t('choose')}: ")
    try:
        idx = int(ch)
        if 1 <= idx <= len(gs.talismanes):
            sold = gs.talismanes.pop(idx - 1)
            gs.money += sold.sell_value
            print(f"  {GOLD}Vendido {sold.name} por ${sold.sell_value}{R}")
            time.sleep(0.3)
    except ValueError:
        pass


# ── MAIN GAME LOOP ──

def run_game(meta=None, load_save=False):
    """Run a full Trucazo game (8 antes × 3 blinds each)."""
    if meta is None:
        meta = MetaProgress()

    start_ante = 1
    start_blind_i = 0

    if load_save and os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "rb") as f:
                data = pickle.load(f)
                gs = data["gs"]
                # Backward compatibility for saves without log
                if not hasattr(gs, "log"):
                    gs.log = []
                start_ante = data["ante"]
                start_blind_i = data["blind_i"]
                # merge saved gs.collection with local .collection.json to not lose global progress
                gs.collection.load()
                # make sure meta is shared
                gs.meta = meta
        except Exception:
            gs = GameState(meta)
            gs.collection.total_runs += 1
    else:
        gs = GameState(meta)
        gs.collection.total_runs += 1

    max_ante = 8

    # Endless mode: if unlocked, go beyond 8
    if meta.endless_unlocked():
        max_ante = 99

    for ante in range(start_ante, max_ante + 1):
        gs.mazo.restaurar()
        # Apply editions/poderes that persist on deck cards
        # (they stay on the Card objects between rounds)

        blinds = ["small", "big", "boss"]
        for blind_i in range(start_blind_i, len(blinds)):
            blind_type = blinds[blind_i]
            
            save_game(gs, ante, blind_i)
            
            gs.mazo.mezclar()

            boss = None
            if blind_type == "boss":
                boss = get_random_jefe(gs.jefes_vistos)
                gs.jefes_vistos.add(boss.name)

            result = run_blind(gs, ante, blind_type, boss)

            if result is None:
                return  # quit
            if not result:
                # Failed blind = game over
                _end_run(gs, ante, False)
                return

            # Track max money for millonario challenge
            gs.max_money_seen = max(gs.max_money_seen, gs.money)

            # Shop after each blind (except last boss if not endless)
            if max_ante == 99 or not (ante == 8 and blind_type == "boss"):
                shop_result = run_shop(gs, ante)
                if shop_result is None:
                    _end_run(gs, ante, False)
                    return

            # Track max money after shop
            gs.max_money_seen = max(gs.max_money_seen, gs.money)

    # Won the game!
    _end_run(gs, max_ante if max_ante <= 8 else gs.collection.best_ante, True)


def _end_run(gs, ante, won):
    """Handle end-of-run: collection, prestigio, challenges."""
    gs.collection.record_run_end(ante, won)

    # Update meta run_stats from collection
    gs.meta.update_run_stat("best_racha", gs.racha)
    gs.meta.update_run_stat("max_money", gs.max_money_seen)
    gs.meta.update_run_stat("jefes_vencidos", len(gs.collection.discovered_jefes))
    gs.meta.update_run_stat("wins", gs.collection.wins)
    gs.meta.update_run_stat("envidos_ganados", gs.collection.envidos_ganados)
    gs.meta.update_run_stat("flores", gs.collection.flores)
    gs.meta.update_run_stat("completion_pct", gs.collection.completion_pct)
    gs.meta.update_run_stat("max_ante", ante)
    if won and gs.powers_bought == 0:
        gs.meta.increment_run_stat("ascetic_wins")

    # Calculate prestigio
    earned = calc_prestigio(
        ante, won,
        gs.run_manos_ganadas,
        gs.run_envidos_ganados,
        gs.run_max_racha,
        prestigio_mult=gs._difficulty_cfg.get("prestigio_mult", 1.0),
    )
    gs.meta.prestigio += earned

    # Check challenges
    new_challenges = gs.meta.check_challenges(gs.collection)
    gs.meta.save()

    # Render
    render_game_over(won, ante, gs.collection)
    input("")
    render_run_end_prestigio(earned, ante, won, new_challenges)
    input("")

    # Check if endless was just unlocked
    if any(ch["unlock_id"] == "endless" for ch in new_challenges):
        render_endless_unlock()
        input("")


# ── FOGÓN & CHALLENGES MENUS ──

def run_fogon(meta):
    """El Fogón: permanent upgrades menu."""
    from meta import FOGON_UPGRADES
    while True:
        render_fogon(meta)
        ch = input(f"  {t('choose')}: ")
        if ch == "0" or ch == "q":
            return
        try:
            idx = int(ch) - 1
            if 0 <= idx < len(FOGON_UPGRADES):
                upg = FOGON_UPGRADES[idx]
                if meta.buy_upgrade(upg["id"]):
                    print(f"  {GRN}{B}✓ {upg['emoji']} {upg['name']} mejorado!{R}")
                    time.sleep(0.5)
                else:
                    level = meta.get_upgrade_level(upg["id"])
                    if level >= upg["max_level"]:
                        print(f"  {NYEL}{t('max_level')}{R}")
                    else:
                        print(f"  {NRED}{t('not_enough_prestigio')}{R}")
                    time.sleep(0.3)
        except ValueError:
            pass


def run_challenges(meta):
    """Desafíos: challenges view."""
    render_challenges(meta)
    input("")


# ── DIFFICULTY SELECTION ──

def select_difficulty(meta):
    """Show difficulty select before a new run. Returns True if selected, False if back."""
    while True:
        render_difficulty_select(meta, DIFFICULTY_ORDER, DIFFICULTY_CONFIG)
        ch = input(f"  {t('choose')}: ")
        if ch == "0" or ch == "q":
            return False
        try:
            idx = int(ch) - 1
            if 0 <= idx < len(DIFFICULTY_ORDER):
                meta.set_difficulty(DIFFICULTY_ORDER[idx])
                return True
        except ValueError:
            pass


def run_difficulty_menu(meta):
    """Standalone difficulty change from main menu."""
    while True:
        render_difficulty_select(meta, DIFFICULTY_ORDER, DIFFICULTY_CONFIG, standalone=True)
        ch = input(f"  {t('choose')}: ")
        if ch == "0" or ch == "q":
            return
        try:
            idx = int(ch) - 1
            if 0 <= idx < len(DIFFICULTY_ORDER):
                meta.set_difficulty(DIFFICULTY_ORDER[idx])
                cfg = get_difficulty_config(DIFFICULTY_ORDER[idx])
                print(f"  {GRN}{B}→ {cfg['emoji']} {cfg['label']}{R}")
                time.sleep(0.5)
                return
        except ValueError:
            pass


def run_settings(meta):
    """Settings menu."""
    from display import render_settings
    while True:
        render_settings(meta)
        ch = input(f"  {t('choose')}: ")
        if ch == "0" or ch == "q":
            return
        elif ch == "1":
            lang = get_lang()
            new_lang = "en" if lang == "es" else "es"
            set_lang(new_lang)
            print(f"  {GRN}→ {new_lang.upper()}{R}")
            time.sleep(0.3)
        elif ch == "2":
            run_difficulty_menu(meta)


# ── TITLE MENU ──

def main_menu():
    """Title screen menu loop."""
    meta = MetaProgress()
    while True:
        if not check_terminal_size():
            continue
            
        has_save = os.path.exists(SAVE_FILE)
        from display import render_title
        render_title(has_save=has_save)
        
        ch = input(f"  {t('choose')}: ").lower()

        if ch == "c" and has_save:
            run_game(meta, load_save=True)
            meta.load()
            continue

        if ch == "1":
            run_game(meta)
            meta.load()  # Reload in case it changed
        elif ch == "2":
            col = Collection()
            render_collection(col)
            input("")
        elif ch == "3":
            render_how_to_play()
            input("")
        elif ch == "4":
            run_fogon(meta)
        elif ch == "5":
            run_challenges(meta)
        elif ch == "6":
            run_settings(meta)
        elif ch == "7" or ch == "q":
            print(f"\n  {D}{t('thanks')}{R}\n")
            break