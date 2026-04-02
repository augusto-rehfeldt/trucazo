"""Terminal display for Trucazo."""
import os, sys, re, unicodedata
from lang import t, get_lang

R = "\033[0m"
B = "\033[1m"
D = "\033[2m"
IT = "\033[3m"
RV = "\033[7m"
BR_RED = "\033[91m"; BR_GRN = "\033[92m"; BR_YEL = "\033[93m"
BR_BLU = "\033[94m"; BR_MAG = "\033[95m"; BR_CYN = "\033[96m"; BR_WHT = "\033[97m"
WHITE = "\033[37m"; RED = "\033[31m"; GREEN = "\033[32m"; YELLOW = "\033[33m"

def rgb(r, g, b): return f"\033[38;2;{r};{g};{b}m"

PINK = rgb(255, 50, 150); BLUE = rgb(50, 150, 255); GRN = rgb(50, 255, 150)
PURP = rgb(180, 80, 255); ORNG = rgb(255, 150, 50); CYAN = rgb(50, 255, 255)
NYEL = rgb(255, 255, 50); NRED = rgb(255, 60, 60); GOLD = rgb(255, 215, 0)
SILV = rgb(192, 192, 192)

CBRD = rgb(90, 90, 100)  # subtle gray for card borders (replaces dim)
PALO_C = {0: rgb(220, 230, 255), 1: rgb(80, 255, 120), 2: rgb(255, 80, 90), 3: GOLD}  # Espadas, Bastos, Copas, Oros
ED_C = {"": WHITE, "Dorada": GOLD + B, "Brillante": BR_CYN + B,
        "Holo": PURP + B, "Prismática": PINK + B}

TW = min(os.get_terminal_size().columns, 120) if sys.stdout.isatty() else 100

MIN_TW = 76
MIN_TH = 28
CARD_IW = 9  # inner width between card │ borders

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
def strip_ansi(s): return re.sub(r'\033\[[0-9;]*m', '', s)

def _get_size_issues():
    """Return list of terminal size issues, or empty if OK."""
    try:
        sz = os.get_terminal_size()
    except OSError:
        return []
    issues = []
    lang = get_lang()
    if sz.columns < MIN_TW:
        msg = f"Ancho: {sz.columns} (mín. {MIN_TW})" if lang == "es" else f"Width: {sz.columns} (min. {MIN_TW})"
        issues.append(msg)
    if sz.lines < MIN_TH:
        msg = f"Alto: {sz.lines} (mín. {MIN_TH})" if lang == "es" else f"Height: {sz.lines} (min. {MIN_TH})"
        issues.append(msg)
    return issues


def check_terminal_size():
    """Check terminal meets minimum size. Live-updates as user resizes."""
    import select, signal
    
    if not sys.stdout.isatty():
        return True
    
    issues = _get_size_issues()
    if not issues:
        return True

    lang = get_lang()
    warn = "⚠ Terminal muy chica" if lang == "es" else "⚠ Terminal too small"
    fix = "Agrandá la ventana..." if lang == "es" else "Resize the window..."

    resized = [False]
    old_handler = signal.getsignal(signal.SIGWINCH)
    def on_resize(signum, frame):
        resized[0] = True
    signal.signal(signal.SIGWINCH, on_resize)

    try:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        try:
            while True:
                # Display current status
                clear()
                issues = _get_size_issues()
                if not issues:
                    break
                print(f"\n  {NYEL}{B}{warn}{R}")
                for m in issues:
                    print(f"  {NYEL}  · {m}{R}")
                print(f"  {D}{fix}{R}")
                resized[0] = False
                # Wait for resize signal or keypress
                while not resized[0]:
                    if select.select([sys.stdin], [], [], 0.3)[0]:
                        sys.stdin.read(1)  # consume keypress
                        break
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except (ImportError, termios.error, OSError):
        # Fallback: simple input-based check
        print(f"\n  {NYEL}{B}{warn}{R}")
        for m in issues:
            print(f"  {NYEL}  · {m}{R}")
        print(f"  {D}{fix}{R}")
        input()
        return not _get_size_issues()
    finally:
        signal.signal(signal.SIGWINCH, old_handler if old_handler else signal.SIG_DFL)

    return True

def vwidth(s):
    """Visible width in terminal (strips ANSI, wide chars count as 2)."""
    clean = strip_ansi(s)
    w = 0
    chars = list(clean)
    is_windows = (os.name == 'nt')
    for i, ch in enumerate(chars):
        cp = ord(ch)
        if cp in (0xFE0F, 0x200D):
            continue
            
        eaw = unicodedata.east_asian_width(ch)
        
        # On Windows, only true CJK chars ('W', 'F') are natively 2-unit wide. 
        # Standard emojis are squished into 1 unit wide blocks!
        if eaw in ('W', 'F'):
            w += 2
        elif cp >= 0x1F000 and not is_windows:
            w += 2
        else:
            if not is_windows:
                # If followed by emoji variation selector, it's rendered as wide emoji on Unix/Mac
                if i + 1 < len(chars) and ord(chars[i+1]) == 0xFE0F:
                    w += 2
                    continue
                # Explicitly catch commonly wide-rendered symbols that are in the base plane (Unix/Mac)
                elif cp in (0x2694, 0x26A1, 0x2620):  # ⚔, ⚡, ☠
                    w += 2
                    continue
            w += 1
    return w

def center(s, w=None):
    w = w or TW
    return " " * max(0, (w - vwidth(s)) // 2) + s

def rpad(s, target_w):
    """Right-pad string to target visible width."""
    return s + " " * max(0, target_w - vwidth(s))

def card_color(card):
    if card.has_edition: return ED_C.get(card.edition.nombre, WHITE)
    return PALO_C.get(card.palo.idx, WHITE)

def render_cards(cards, show_idx=True, hl=None, face_down=False):
    hl = hl or set()
    CW = CARD_IW
    TW_C = CW + 2  # total card width including borders
    l1, l2, l3, l4, l5, l6, l7, idxs = [], [], [], [], [], [], [], []
    for i, c in enumerate(cards):
        sel = i in hl
        brd = NYEL + B if sel else CBRD
        top = f"{brd}╭{'─' * CW}╮{R}"
        bot = f"{brd}╰{'─' * CW}╯{R}"
        blank = f"{brd}│{' ' * CW}│{R}"
        if face_down:
            # Inner frame back design
            diamond = f"{GOLD}{B}◆{R}"
            inner_w = CW - 2  # inside the inner frame
            dv = 1; dlp = (inner_w - dv) // 2; drp = inner_w - dv - dlp
            l1.append(top)
            l2.append(f"{brd}│{CBRD}┌{'─' * inner_w}┐{R}{brd}│{R}")
            l3.append(blank)
            l4.append(f"{brd}│{CBRD}│{' ' * dlp}{R}{diamond}{CBRD}{' ' * drp}│{R}{brd}│{R}")
            l5.append(blank)
            l6.append(f"{brd}│{CBRD}└{'─' * inner_w}┘{R}{brd}│{R}")
            l7.append(bot)
        else:
            cc = card_color(c)
            # Only rank in corners, icon in center!
            rl = c.rank_label; icon = c.palo.icon
            
            # Top left: rank only
            l1.append(top)
            l2.append(f"{brd}│ {cc}{B}{rl:<{CW-1}}{R}{brd}│{R}")
            l3.append(blank)
            
            # Center symbol (big icon)
            if c.has_poder:
                ctr = f"{cc}{B}{icon}{R} ⚡"
            else:
                ctr = f"{cc}{B}{icon}{R}"
            cv = vwidth(ctr)
            clp = (CW - cv) // 2
            crp = CW - cv - clp
            # Optical correction for ⚔ which tends to render heavily right-skewed in terminal cells
            if "⚔" in icon:
                clp -= 1
                crp += 1
            l4.append(f"{brd}│{' ' * clp}{ctr}{' ' * crp}{brd}│{R}")
            l5.append(blank)
            
            # Bottom right: rank only
            l6.append(f"{brd}│{cc}{B}{rl:>{CW-1}}{R} {brd}│{R}")
            l7.append(bot)
        if show_idx:
            n = str(i + 1)
            nw = len(n)
            nlp = (TW_C - nw) // 2; nrp = TW_C - nw - nlp
            idxs.append(f"{' ' * nlp}{CYAN}{B}{n}{R}{' ' * nrp}")
    lines = []
    if hl:
        sls = []
        for i in range(len(cards)):
            if i in hl:
                hlp = (TW_C - 1) // 2; hrp = TW_C - 1 - hlp
                sls.append(f"{' ' * hlp}{NYEL}▲{R}{' ' * hrp}")
            else:
                sls.append(" " * TW_C)
        lines.append(" ".join(sls))
    lines += [" ".join(l1), " ".join(l2), " ".join(l3), " ".join(l4), " ".join(l5), " ".join(l6), " ".join(l7)]
    if show_idx: lines.append(" ".join(idxs))
    return lines


TITLE_LINES = [
    f"{CYAN}{B}███████╗██████╗ ██╗   ██╗ ██████╗ █████╗ ███████╗ ██████╗ {R}",
    f"{BLUE}{B}╚══██╔══╝██╔══██╗██║   ██║██╔════╝██╔══██╗╚══███╔╝██╔═══██╗{R}",
    f"{NYEL}{B}   ██║   ██████╔╝██║   ██║██║     ███████║  ███╔╝ ██║   ██║{R}",
    f"{ORNG}{B}   ██║   ██╔══██╗██║   ██║██║     ██╔══██║ ███╔╝  ██║   ██║{R}",
    f"{NRED}{B}   ██║   ██║  ██║╚██████╔╝╚██████╗██║  ██║███████╗╚██████╔╝{R}",
    f"{GOLD}{B}   ╚═╝   ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝ {R}"
]

def render_title(has_save=False):
    clear()
    print()
    for ln in TITLE_LINES:
        print(center(ln))
    print()
    print(center(f"{NYEL}⚔{R}  {GRN}🪵{R}    {D}{B}{t('title_sub')}{R}    {NRED}🏆{R}  {GOLD}🪙{R}"))
    print()
    print(center(f"{D}{'─' * 40}{R}"))
    print()
    if has_save:
        print(center(f"{NYEL}{B}[C]{R} {NYEL}{t('continue_run')}{R}"))
    print(center(f"{GRN}[1]{R} {t('new_run')}"))
    print(center(f"{BLUE}[2]{R} {t('collection')}"))
    print(center(f"{PURP}[3]{R} {t('how_to_play')}"))
    print(center(f"{GOLD}[4]{R} {t('fogon')}"))
    print(center(f"{NYEL}[5]{R} {t('desafios')}"))
    print(center(f"{CYAN}[6]{R} {t('settings')}"))
    print(center(f"{NRED}[7]{R} {t('quit')}"))
    print()
    print(center(f"{D}{'─' * 40}{R}"))
    print()


def render_settings(meta):
    clear()
    lang = get_lang()
    from difficulty import get_difficulty_config
    diff_cfg = get_difficulty_config(meta.difficulty)
    diff_label = diff_cfg.get("label_en", diff_cfg["label"]) if lang == "en" else diff_cfg["label"]
    lang_label = "ES ↔ EN" if lang == "es" else "EN ↔ ES"

    print(f"\n{center(f'{CYAN}{B}✦ {t('settings')} ✦{R}')}")
    print(center(f"{D}{'─' * 40}{R}\n"))

    print(center(f"{ORNG}[1]{R} {t('language_label')}: {lang_label}"))
    print(center(f"{CYAN}[2]{R} {t('difficulty_label')}: {diff_cfg['emoji']} {diff_label}"))
    print()
    print(center(f"{D}[0] {t('back')}{R}\n"))


def render_difficulty_select(meta, order, config, standalone=False):
    """Render difficulty selection screen."""
    clear()
    lang = get_lang()
    print(f"\n{center(f'{CYAN}{B}✦ {t(chr(100)+chr(105)+chr(102)+chr(102)+chr(105)+chr(99)+chr(117)+chr(108)+chr(116)+chr(121)+chr(95)+chr(116)+chr(105)+chr(116)+chr(108)+chr(101))} ✦{R}')}")
    print(center(f"{D}{'─' * 40}{R}\n"))

    tier_colors = {"easy": GRN, "normal": NYEL, "hard": NRED}
    for i, tier in enumerate(order):
        cfg = config[tier]
        tc = tier_colors.get(tier, CYAN)
        label = cfg.get("label_en", cfg["label"]) if lang == "en" else cfg["label"]
        desc = cfg.get("desc_en", cfg["desc"]) if lang == "en" else cfg["desc"]
        emoji = cfg["emoji"]
        current = " ◄" if meta.difficulty == tier else ""
        cur_tag = f"  {D}({t('current')}){R}" if meta.difficulty == tier else ""
        prest = f"×{cfg['prestigio_mult']:.2g}" if cfg["prestigio_mult"] != 1.0 else ""
        prest_str = f"  {GOLD}{t('prestigio')} {prest}{R}" if prest else ""
        print(center(f"{tc}{B}[{i+1}]{R} {emoji} {tc}{B}{label}{R}{cur_tag}{prest_str}"))
        print(center(f"    {D}{desc}{R}"))
        print()

    print(center(f"{D}[0] {t('back')}{R}\n"))


def render_header(ante, blind_type, blind_name, target, score, hands_left, money):
    bc = {"small": GRN, "big": NYEL, "boss": NRED}[blind_type]
    bl = {"small": t("small_blind"), "big": t("big_blind"), "boss": blind_name}[blind_type]
    print()
    print(f"  {CYAN}{B}{'═' * (TW - 4)}{R}")
    left = f"  {PURP}{B}{t('ante')} {ante}{R}  │  {bc}{B}{bl}{R}"
    right = f"{GOLD}{B}${money}{R}  "
    pad = max(1, TW - vwidth(left) - vwidth(right))
    print(f"{left}{' ' * pad}{right}")
    print(f"  {CYAN}{B}{'═' * (TW - 4)}{R}")
    pct = min(score / target, 1.0) if target > 0 else 0
    bw = 40; filled = int(pct * bw)
    barc = GRN if pct >= 1.0 else (NYEL if pct >= 0.5 else NRED)
    bar = f"{barc}{'█' * filled}{D}{'░' * (bw - filled)}{R}"
    print(f"  {bar}  {B}{score:,}{R} {D}/ {target:,}{R}")
    print(f"  {BLUE}{B}{t('hands')}: {hands_left}{R}")
    print()

def render_talismanes(tals, mx=3):
    if not tals: print(f"  {D}{t('augments')}: (vacío){R}"); return
    parts = [f"{a.emoji}  {a.name}" for a in tals] + [f"{D}[   ]{R}"] * max(0, mx - len(tals))
    print(f"  {t('augments')}:  {' │ '.join(parts)}")


def _render_house_slots(house_played, peek_idx=None):
    """Render 3 house card slots: face-down with red backs, or revealed."""
    CW = CARD_IW
    l1, l2, l3, l4, l5, l6, l7 = [], [], [], [], [], [], []
    for i in range(3):
        if i < len(house_played):
            c = house_played[i]; cc = card_color(c)
            rl = c.rank_label; icon = c.palo.icon
            brd = NRED
            
            ctr = f"{cc}{B}{icon}{R}"
            cv = vwidth(ctr); clp = (CW - cv) // 2; crp = CW - cv - clp
            blank = f"{brd}│{' ' * CW}│{R}"
            
            l1.append(f"{brd}╭{'─' * CW}╮{R}")
            l2.append(f"{brd}│ {cc}{B}{rl:<{CW-1}}{R}{brd}│{R}")
            l3.append(blank)
            l4.append(f"{brd}│{' ' * clp}{ctr}{' ' * crp}{brd}│{R}")
            l5.append(blank)
            l6.append(f"{brd}│{cc}{B}{rl:>{CW-1}}{R} {brd}│{R}")
            l7.append(f"{brd}╰{'─' * CW}╯{R}")
        elif peek_idx is not None and i == peek_idx:
            brd = NYEL
            q = f"{NYEL}{B}?{R}"
            ql = f" {q}"; qr = f"{q} "
            qv = 1; qclp = (CW - qv) // 2; qcrp = CW - qv - qclp
            blank = f"{brd}│{' ' * CW}│{R}"
            l1.append(f"{brd}╭{'─' * CW}╮{R}")
            l2.append(f"{brd}│{ql}{' ' * max(0, CW - vwidth(ql))}{brd}│{R}")
            l3.append(blank)
            l4.append(f"{brd}│{' ' * qclp}{q}{' ' * qcrp}{brd}│{R}")
            l5.append(blank)
            l6.append(f"{brd}│{' ' * max(0, CW - vwidth(qr))}{qr}{brd}│{R}")
            l7.append(f"{brd}╰{'─' * CW}╯{R}")
        else:
            # Inner frame back design
            brd = NRED
            inner_w = CW - 2
            diamond = f"{GOLD}{B}◆{R}"
            dv = 1; dlp = (inner_w - dv) // 2; drp = inner_w - dv - dlp
            blank = f"{brd}│{' ' * CW}│{R}"
            l1.append(f"{brd}╭{'─' * CW}╮{R}")
            l2.append(f"{brd}│{CBRD}┌{'─' * inner_w}┐{R}{brd}│{R}")
            l3.append(blank)
            l4.append(f"{brd}│{CBRD}│{' ' * dlp}{R}{diamond}{CBRD}{' ' * drp}│{R}{brd}│{R}")
            l5.append(blank)
            l6.append(f"{brd}│{CBRD}└{'─' * inner_w}┘{R}{brd}│{R}")
            l7.append(f"{brd}╰{'─' * CW}╯{R}")
    return [" ".join(l1), " ".join(l2), " ".join(l3), " ".join(l4), " ".join(l5), " ".join(l6), " ".join(l7)]


def _build_info_panel(ronda, p_wins, h_wins, stake_name, stake_mult,
                      score=0, target=0, hands_left=0, money=0,
                      tals=None, tal_slots=3, envido_p=None, flor_flag=False,
                      ante=0, blind_type="small", blind_name="", hand_est=None):
    """Build right-side info panel as list of lines."""
    PW = 25  # inner visible content width
    IW = PW + 1  # total between │ chars (leading space + content)

    def pline(content=""):
        s = f" {content}"
        pad = max(0, IW - vwidth(s))
        return f"{CYAN}│{R}{s}{' ' * pad}{CYAN}│{R}"

    def sep():
        return f"{CYAN}│{D}{'─' * IW}{R}{CYAN}│{R}"

    lines = []
    bc = {"small": GRN, "big": NYEL, "boss": NRED}.get(blind_type, CYAN)
    bl = {"small": t("small_blind"), "big": t("big_blind"), "boss": blind_name or t("boss_blind")}.get(blind_type, "")
    title = f" P{ante} · {bl} "
    tw_t = vwidth(title)
    if tw_t > IW:
        # Truncate blind name to fit
        title = f" P{ante} "
        tw_t = vwidth(title)
    dl = max(0, (IW - tw_t) // 2); dr = max(0, IW - tw_t - dl)
    lines.append(f"{CYAN}┌{'─' * dl}{R}{bc}{B}{title}{R}{CYAN}{'─' * dr}┐{R}")

    lines.append(pline())

    # Round + dots
    remaining = max(0, 3 - p_wins - h_wins)
    dot_parts = ([f"{GRN}●{R}"] * p_wins) + ([f"{NRED}●{R}"] * h_wins) + ([f"{D}○{R}"] * remaining)
    dots = "  ".join(dot_parts)
    lines.append(pline(f"{B}{t('round_of', n=ronda+1)}{R}"))
    lines.append(pline(dots))

    # Stake
    if stake_mult > 1:
        sc = GRN if stake_mult <= 2 else (NYEL if stake_mult <= 3 else NRED)
        lines.append(pline(f"{sc}{B}{stake_name} (×{stake_mult}){R}"))

    lines.append(sep())

    # Score bar
    if target > 0:
        pct = min(score / target, 1.0)
        bw = 18; filled = int(pct * bw)
        barc = GRN if pct >= 1.0 else (NYEL if pct >= 0.5 else NRED)
        bar = f"{barc}{'█' * filled}{D}{'░' * (bw - filled)}{R}"
        lines.append(pline(bar))
        lines.append(pline(f"{B}{score:,}{R} {D}/ {target:,}{R}"))
        if hand_est is not None:
            lines.append(pline(f"{D}esta mano: ~{hand_est:,}{R}"))
    else:
        lines.append(pline(f"{D}---{R}"))

    lines.append(sep())

    # Hands + money
    lines.append(pline(f"{BLUE}{B}{t('hands')}: {hands_left}{R}"))
    lines.append(pline(f"{GOLD}{B}${money}{R}"))

    # Envido
    if envido_p is not None:
        lines.append(sep())
        fl = f" {PURP}★ FLOR{R}" if flor_flag else ""
        lines.append(pline(f"{ORNG}Envido: {B}{envido_p}{R}{fl}"))

    # Talismanes
    lines.append(sep())
    tals = tals or []
    if tals:
        for a in tals:
            lines.append(pline(f"{a.emoji} {D}{a.name}{R}"))
        for _ in range(max(0, tal_slots - len(tals))):
            lines.append(pline(f"{D}[     ]{R}"))
    else:
        lines.append(pline(f"{D}{t('augments')}: ─{R}"))

    lines.append(f"{CYAN}└{'─' * IW}┘{R}")
    return lines


def _merge_panels(left_lines, right_lines, gap=4):
    """Merge two line arrays side by side, padding left to max width."""
    lw = max((vwidth(l) for l in left_lines), default=0)
    n = max(len(left_lines), len(right_lines))
    out = []
    for i in range(n):
        l = left_lines[i] if i < len(left_lines) else ""
        r = right_lines[i] if i < len(right_lines) else ""
        pad = max(0, lw - vwidth(l)) + gap
        out.append(f"{l}{' ' * pad}{r}")
    return out


def render_battle(player_hand, house_played, player_played, ronda, p_wins, h_wins,
                  stake_name, stake_mult, envido_p=None, flor_flag=False, peek_idx=None,
                  score=0, target=0, hands_left=0, money=0, tals=None, tal_slots=3,
                  ante=0, blind_type="small", blind_name="", env_bonus=0, event_log=None):
    clear()

    # ── Build left panel: house cards + player cards ──
    left = []
    left.append(f"  {NRED}{B}{t('the_house')}{R}")
    left.append("")
    for hl in _render_house_slots(house_played, peek_idx):
        left.append(f"  {hl}")
    left.append("")

    left.append(f"  {CYAN}{B}{t('your_hand')}{R}")
    left.append("")
    remaining = [c for c in player_hand if c not in player_played]
    if remaining:
        for cl in render_cards(remaining, show_idx=True):
            left.append(f"  {cl}")
    else:
        left.append(f"  {D}(sin cartas){R}")

    # ── Build right panel: game info ──
    # Estimate current hand pts from played cards + envido/flor bonus
    card_pts = sum(c.point_value for c in player_played) * stake_mult if player_played else 0
    bonus_pts = max(0, env_bonus)
    hand_est = card_pts + bonus_pts
    show_est = player_played or bonus_pts > 0

    right = _build_info_panel(
        ronda, p_wins, h_wins, stake_name, stake_mult,
        score=score, target=target, hands_left=hands_left, money=money,
        tals=tals, tal_slots=tal_slots, envido_p=envido_p, flor_flag=flor_flag,
        ante=ante, blind_type=blind_type, blind_name=blind_name,
        hand_est=hand_est if show_est else None)

    # ── Merge and print ──
    print()
    merged = _merge_panels(left, right, gap=3)
    if event_log:
        merged = _merge_panels(merged, render_log_panel(event_log), gap=3)
    
    for line in merged:
        print(line)
    print()

def render_log_panel(log):
    if not log:
        return []
    
    PW = 46  # panel width
    IW = PW + 1
    
    def pline(content=""):
        s = f" {content}"
        pad = max(0, IW - vwidth(s))
        return f"{CYAN}│{R}{s}{' ' * pad}{CYAN}│{R}"

    lines = []
    title = f" {t('history')} " if get_lang() == "en" else " Historial "
    tw_t = vwidth(title)
    dl = max(0, (IW - tw_t) // 2); dr = max(0, IW - tw_t - dl)
    lines.append(f"{CYAN}┌{'─' * dl}{R}{B}{title}{R}{CYAN}{'─' * dr}┐{R}")
    
    for item in log:
        lines.append(pline(item))
        
    lines.append(f"{CYAN}└{'─' * IW}┘{R}")
    return lines

def render_baza_result(winner, pc, hc, pr, hr):
    pcc = card_color(pc); hcc = card_color(hc)
    
    # Pad the labels so they align perfectly regardless of digits (e.g. 10⚔ vs 3🏆)
    pl_clean = rpad(pc.label, 4)
    hl_clean = rpad(hc.label, 4)
    
    pl = f"{pcc}{B}{pl_clean}{R}"
    hl = f"{hcc}{B}{hl_clean}{R}"
    
    if winner == "player": res = f"{GRN}{B}★ {t('you_win')}{R}"; sym = f" {GRN}>{R} "
    elif winner == "house": res = f"{NRED}{B}✗ {t('house_wins')}{R}"; sym = f" {NRED}<{R} "
    else: res = f"{NYEL}{t('tie')}{R}"; sym = f" {NYEL}={R} "
    
    # Pad rank values to 3 digits to keep the arrows perfectly aligned
    s = f"  {pl} {D}({pr:>3}){R}{sym}{hl} {D}({hr:>3}){R}  →  {res}"
    print(f"\n{s}")
    return s.strip()

def render_hand_result(winner, score, racha, breakdown=None):
    print()
    if winner == "player":
        rc = f"    {PURP}{B}¡{t('cascade_combo')} {racha}!{R}" if racha > 1 else ""
        print(f"  {GRN}{B}★ {t('hand_won')}  +{score:,} pts{R}")
        if breakdown:
            print(f"    {D}└─ {breakdown}{R}")
        if rc: print(rc)
    elif winner == "house":
        if score > 0:
            print(f"  {NRED}{B}✗ {t('hand_lost')}  {NYEL}+{score:,} pts{R}")
        else:
            print(f"  {NRED}{B}✗ {t('hand_lost')}{R}")
    else:
        print(f"  {NYEL}═ {t('tie')}{R}")

def render_envido_result(winner, ps, hs, pts):
    print()
    if winner == "player":
        s = f"  {GRN}{B}★ Envido ganado!{R}  Vos: {B}{ps}{R}  vs  Banca: {hs}  →  {GOLD}{B}+{pts} pts{R}"
        log_s = f"{GRN}{B}★ Envido: {ps}v{hs} → +{pts} pts{R}"
    else: 
        s = f"  {NRED}{B}✗ Envido perdido.{R}  Vos: {ps}  vs  Banca: {B}{hs}{R}"
        log_s = f"{NRED}{B}✗ Envido: {ps}v{hs}{R}"
    print(s)
    return s.strip(), log_s

def render_flor_result(winner, ps, hs, pts):
    print()
    if winner == "player":
        s = f"  {PURP}{B}★★ ¡Flor ganada!{R}  Vos: {B}{ps}{R}  vs  Banca: {hs}  →  {GOLD}{B}+{pts} pts{R}"
        log_s = f"{PURP}{B}★★ Flor: {ps}v{hs} → +{pts} pts{R}"
    else: 
        s = f"  {NRED}{B}✗ Flor perdida.{R}  Vos: {ps}  vs  Banca: {B}{hs}{R}"
        log_s = f"{NRED}{B}✗ Flor: {ps}v{hs}{R}"
    print(s)
    return s.strip(), log_s

def render_truco_call(caller, name):
    cs = {"Truco": NYEL, "Retruco": ORNG, "Vale Cuatro": NRED}
    c = cs.get(name, CYAN)
    who = "VOS" if caller == "player" else "LA BANCA"
    w = len(who) + len(name) + 5
    pad = max(0, (40 - w) // 2)
    print(f"\n  {c}{B}{'═' * 40}{R}")
    print(f"  {c}{B}{' ' * pad}{who}: ¡{name}!{R}")
    print(f"  {c}{B}{'═' * 40}{R}")

def render_accept_decline(what, caller):
    who = "La Banca" if caller == "house" else "Vos"
    print(f"\n  {NYEL}{B}{who} canta: ¡{what}!{R}")
    print(f"  {GRN}{B}[Q]{R}uiero  │  {NRED}{B}[N]{R}o quiero  │  {ORNG}{B}[S]{R}ubir")

def render_actions(can_env=True, can_truco=True, flor=False, n_cards=0):
    acts = []
    if n_cards > 0: acts.append(f"{GRN}{B}[1-{n_cards}]{R} {t('play_card')}")
    if can_env: acts.append(f"{ORNG}{B}[E]{R}nvido")
    if flor: acts.append(f"{PURP}{B}[F]{R}lor")
    if can_truco: acts.append(f"{NRED}{B}[T]{R}ruco")
    acts += [f"{PURP}[A]umentos{R}", f"{D}[I]nfo{R}", f"{D}[Q]{t('quit')}{R}"]
    print(f"  {' │ '.join(acts)}")

def render_shop(tals, pods, eds, truqs, money, reroll_cost, owned_tals, max_slots=3):
    clear()
    print(f"\n  {GOLD}{B}{'═' * (TW - 4)}{R}")
    print(center(f"{GOLD}{B}✦ {t('shop')} ✦{R}"))
    print(f"  {GOLD}{B}{'═' * (TW - 4)}{R}")
    print(f"  {GOLD}{t('money')}: ${money}{R}\n")
    
    print(f"  {NYEL}[R] 🎲 {t('reroll')} Kiosco - ${reroll_cost}{R}\n")
    
    idx = 1
    print(f"  {PURP}{B}─── {t('augments')} ───{R}")
    for a in tals:
        aff = "" if a.cost <= money else D
        print(f"  {aff}[{idx}] {a.emoji} {a.name}{R} {aff}${a.cost} - {a.desc}{R}"); idx += 1
    print()
    print(f"  {ORNG}{B}─── {t('powers')} ───{R} {D}(aplicado a carta random){R}")
    for p in pods:
        aff = "" if p.cost <= money else D
        print(f"  {aff}[{idx}] ⚡ {p.nombre}{R} {aff}${p.cost} - {p.desc}{R}"); idx += 1
    print()
    print(f"  {CYAN}{B}─── {t('editions')} ───{R}")
    for e in eds:
        aff = "" if e.cost <= money else D
        ec = ED_C.get(e.nombre, WHITE)
        print(f"  {aff}[{idx}] {ec}{e.nombre}{R} {aff}${e.cost} - {e.desc}{R}"); idx += 1
    print()
    print(f"  {BLUE}{B}─── Truqueras ───{R} {D}(suben nivel de jugadas){R}")
    for tr in truqs:
        aff = "" if tr["cost"] <= money else D
        desc = tr["desc"] if get_lang() == "es" else tr["desc_en"]
        print(f"  {aff}[{idx}] 🃏 {tr['name']}{R} {aff}${tr['cost']} - {desc}{R}"); idx += 1
    print()
    render_talismanes(owned_tals, max_slots)
    print(f"\n  {D}[V] {t('sell')} │ [D] {t('deck')} │ [N] Siguiente │ [Q] Volver al menú{R}\n")

def render_hierarchy():
    from cards import Palo
    lang = get_lang()
    title = "JERARQUÍA DE CARTAS" if lang == "es" else "CARD HIERARCHY"
    subtitle = "(como el Truco real)" if lang == "es" else "(real Argentine Truco)"
    print(f"\n  {CYAN}{B}─── {title} ───{R}  {D}{subtitle}{R}")
    rows = [
        (f"{BR_WHT}1{Palo.ESPADAS.symbol}{R}", "Ancho de Espadas", "100"),
        (f"{GRN}1{Palo.BASTOS.symbol}{R}", "Ancho de Bastos", "99"),
        (f"{BR_WHT}7{Palo.ESPADAS.symbol}{R}", "Siete de Espadas", "98"),
        (f"{GOLD}7{Palo.OROS.symbol}{R}", "Siete de Oros", "97"),
        (f"{WHITE}3x{R}", "Tres", "90"),
        (f"{WHITE}2x{R}", "Dos", "85"),
        (f"{BR_RED}1{Palo.COPAS.symbol}{R} {GOLD}1{Palo.OROS.symbol}{R}", "Ancho falso", "80"),
        (f"{WHITE}12x{R}", "Rey", "75"),
        (f"{WHITE}11x{R}", "Caballo", "70"),
        (f"{WHITE}10x{R}", "Sota", "65"),
        (f"{BR_RED}7{Palo.COPAS.symbol}{R} {GRN}7{Palo.BASTOS.symbol}{R}", "Siete falso", "55"),
        (f"{D}6x{R}", "Seis", "50"),
        (f"{D}5x{R}", "Cinco", "45"),
        (f"{D}4x{R}", "Cuatro (peor)", "40"),
    ]
    for card, name, rank in rows:
        padded_card = rpad(card, 8)
        print(f"  {padded_card} {name:<22} {D}rank {rank:>3}{R}")
    print()

def render_how_to_play():
    clear()
    print(f"\n{center(f'{CYAN}{B}✦ {t(chr(104)+chr(116)+chr(112)+chr(95)+chr(116)+chr(105)+chr(116)+chr(108)+chr(101))} ✦{R}')}")
    txt = t("htp_text")
    txt = txt.replace("{b}", B).replace("{r}", R).replace("{d}", D)
    txt = txt.replace("{o}", ORNG).replace("{p}", PURP).replace("{rr}", NRED)
    txt = txt.replace("{g}", GRN).replace("{y}", NYEL).replace("{go}", GOLD)
    print(txt)
    render_hierarchy()
    print(center(f"{D}{t('press_enter_return')}{R}"))

def render_collection(col):
    from data import ALL_TALISMANES
    from cards import Poder, Edition
    clear()
    print(f"\n{center(f'{GOLD}{B}✦ {t(chr(99)+chr(111)+chr(108)+chr(108)+chr(101)+chr(99)+chr(116)+chr(105)+chr(111)+chr(110))} ✦{R}')}")
    print(center(f"{D}{'─' * 50}{R}\n"))
    print(center(f"{CYAN}{t('total_runs')}: {col.total_runs} │ {t('wins')}: {col.wins} │ {t('best_ante')}: {col.best_ante}{R}"))
    print(center(f"{GRN}Manos: W{col.manos_ganadas} L{col.manos_perdidas}{R}"))
    print(center(f"{ORNG}Envidos: {col.envidos_ganados} │ Flores: {col.flores} │ Rachas: {col.rachas}{R}"))
    if col.best_hand: print(center(f"{GOLD}Mejor mano: {col.best_hand:,}{R}"))
    print()
    print(center(f"{PURP}{B}─── Talismanes ({len(col.discovered_talismanes)}/{len(ALL_TALISMANES)}) ───{R}"))
    for a in ALL_TALISMANES:
        if a.name in col.discovered_talismanes: print(f"  {a.emoji} {a.name} - {a.desc}")
        else: print(f"  {D}?? ????????????????{R}")
    print()
    all_p = [p for p in Poder if p != Poder.NADA]
    print(center(f"{ORNG}{B}─── Poderes ({len(col.discovered_poderes)}/{len(all_p)}) ───{R}"))
    for p in all_p:
        if p.nombre in col.discovered_poderes: print(f"  ⚡ {p.nombre} - {p.desc}")
        else: print(f"  {D}?? ????????????{R}")
    print(f"\n{center(f'{t(chr(100)+chr(105)+chr(115)+chr(99)+chr(111)+chr(118)+chr(101)+chr(114)+chr(101)+chr(100))}: {col.completion_pct}%')}\n")
    print(center(f"{D}{t('press_enter_return')}{R}"))

def render_game_over(won, ante, col):
    clear(); print()
    if won:
        print(center(f"{GRN}{B}╔{'═' * 27}╗{R}"))
        text = f"★ {t('victory')} ★"
        print(center(f"{GRN}{B}║{text:^27}║{R}"))
        print(center(f"{GRN}{B}╚{'═' * 27}╝{R}"))
    else:
        print(center(f"{NRED}{B}╔{'═' * 27}╗{R}"))
        text = t('game_over')
        print(center(f"{NRED}{B}║{text:^27}║{R}"))
        print(center(f"{NRED}{B}╚{'═' * 27}╝{R}"))
    print(f"\n{center(f'{t(chr(97)+chr(110)+chr(116)+chr(101))} {ante}')}")
    print(center(f"{t('total_runs')}: {col.total_runs} │ {t('wins')}: {col.wins} │ {col.completion_pct}%"))
    print(f"\n{center(f'{D}{t('press_enter_return')}{R}')}")

def render_blind_intro(ante, blind_type, target, boss=None):
    clear()
    bc = {"small": GRN, "big": NYEL, "boss": NRED}[blind_type]
    bl = {"small": t("small_blind"), "big": t("big_blind"), "boss": t("boss_blind")}[blind_type]
    print(f"\n{center(f'{bc}{B}{chr(9552) * 40}{R}')}")
    print(center(f"{bc}{B}{t('ante')} {ante} — {bl}{R}"))
    print(f"{center(f'{bc}{B}{chr(9552) * 40}{R}')}")
    print(center(f"{t('target')}: {GOLD}{B}{target:,}{R}"))
    if boss and blind_type == "boss":
        print(f"\n{center(f'{NRED}{B}{boss.emoji} {boss.name}{R}')}")
        print(center(f"{NRED}{boss.desc}{R}"))
    print(f"\n{center(f'{D}{t(chr(112)+chr(114)+chr(101)+chr(115)+chr(115)+chr(95)+chr(101)+chr(110)+chr(116)+chr(101)+chr(114))}{R}')}")

def render_deck_view(cards):
    from cards import Palo
    print(f"\n  {CYAN}{B}─── {t('deck')} ({t('cards_remaining', n=len(cards))}) ───{R}")
    by_p = {}
    for c in cards: by_p.setdefault(c.palo, []).append(c)
    for p in Palo:
        if p in by_p:
            cs = sorted(by_p[p], key=lambda c: c.rank)
            pc = PALO_C.get(p.idx, WHITE)
            lbls = []
            for c in cs:
                color = card_color(c)
                ind = "⚡" if c.has_poder else ""
                lbls.append(f"{color}{B}{c.rank_label}{ind}{R}")
            line = " ".join(lbls)
            n_str = f"{p.symbol} {p.nombre}"
            pad = " " * max(1, 12 - vwidth(n_str))
            print(f"  {pc}{n_str}{pad}│{R} {line}")

    specials = [c for c in cards if c.has_poder or c.has_edition]
    if specials:
        print(f"\n  {PURP}─── Especiales ───{R}")
        for c in sorted(specials, key=lambda x: (x.palo.idx, x.rank)):
            pw_str = f"⚡ {c.poder.nombre}" if c.has_poder else ""
            ed_str = f"✨ {c.edition.nombre}" if c.has_edition else ""
            cc = card_color(c)
            info = "  ".join(filter(None, [pw_str, ed_str]))
            n_str = f"{c.rank_label}{c.palo.symbol}"
            pad = " " * max(1, 6 - vwidth(n_str))
            print(f"  {cc}{B}{n_str}{pad}│{R} {info}")
    print()

def render_levels(levels):
    print(f"\n  {CYAN}{B}─── Niveles ───{R}")
    names = {"truco": "Truco", "envido": "Envido", "flor": "Flor", "racha": "Racha"}
    for key, name in names.items():
        lvl = levels.get(key, 1)
        c = GRN if lvl > 1 else D
        print(f"  {c}{name:<12} Nivel {lvl}{R}")
    print()


def render_fogon(meta):
    """Render El Fogón (permanent upgrades) screen."""
    from meta import FOGON_UPGRADES
    clear()
    lang = get_lang()
    print(f"\n{center(f'{GOLD}{B}🔥 {t(chr(102)+chr(111)+chr(103)+chr(111)+chr(110)+chr(95)+chr(116)+chr(105)+chr(116)+chr(108)+chr(101))} 🔥{R}')}")
    print(center(f"{D}{t('fogon_subtitle')}{R}"))
    print(center(f"{GOLD}{t('prestigio')}: {B}{meta.prestigio}{R}"))
    print(center(f"{D}{'─' * 50}{R}\n"))

    for i, upg in enumerate(FOGON_UPGRADES):
        level = meta.get_upgrade_level(upg["id"])
        max_lvl = upg["max_level"]
        name = upg.get("name_en", upg["name"]) if lang == "en" else upg["name"]
        desc = upg.get("desc_en", upg["desc"]) if lang == "en" else upg["desc"]

        # Fill in value placeholder
        if level > 0:
            val = upg["values"][level - 1]
            desc = desc.replace("{v}", str(val))
        elif upg["values"]:
            desc = desc.replace("{v}", str(upg["values"][0]))

        # Level bar
        bar = ""
        for lv in range(max_lvl):
            if lv < level:
                bar += f"{GRN}●{R}"
            else:
                bar += f"{D}○{R}"

        if level >= max_lvl:
            cost_str = f"{GRN}{t('max_level')}{R}"
            idx_str = f"{D}[{i+1}]{R}"
        else:
            cost = upg["costs"][level]
            affordable = meta.prestigio >= cost
            cc = GOLD if affordable else NRED
            cost_str = f"{cc}{cost} {t('prestigio').lower()}{R}"
            idx_str = f"{GRN}[{i+1}]{R}" if affordable else f"{D}[{i+1}]{R}"

        print(f"  {idx_str} {upg['emoji']} {B}{name}{R} {bar}  {D}{desc}{R}  {cost_str}")

    print(f"\n  {D}[0] {t('back')}{R}\n")


def render_challenges(meta):
    """Render Desafíos (challenges) screen."""
    from meta import DESAFIOS
    clear()
    lang = get_lang()
    print(f"\n{center(f'{NYEL}{B}🏆 {t(chr(100)+chr(101)+chr(115)+chr(97)+chr(102)+chr(105)+chr(111)+chr(115)+chr(95)+chr(116)+chr(105)+chr(116)+chr(108)+chr(101))} 🏆{R}')}")
    print(center(f"{D}{t('desafios_subtitle')}{R}"))
    print(center(f"{D}{'─' * 50}{R}\n"))

    for ch in DESAFIOS:
        completed = ch["id"] in meta.completed_challenges
        name = ch.get("name_en", ch["name"]) if lang == "en" else ch["name"]
        desc = ch.get("desc_en", ch["desc"]) if lang == "en" else ch["desc"]

        # Get progress info
        key = ch["condition_key"]
        target = ch["condition_value"]
        current = meta.run_stats.get(key, 0)

        if completed:
            status = f"{GRN}{B}✓ {t('completed')}{R}"
            utype = ch["unlock_type"]
            uid = ch["unlock_id"]
            unlock_str = f"{D}→ {uid}{R}"
            print(f"  {ch['emoji']}  {GRN}{B}{name:<24}{R} {status}  {unlock_str}")
        else:
            pct = min(current / target, 1.0) if target > 0 else 0
            bw = 15
            filled = int(pct * bw)
            bar = f"{NYEL}{'█' * filled}{D}{'░' * (bw - filled)}{R}"
            print(f"  {ch['emoji']}  {B}{name:<24}{R} {D}{desc}{R}")
            print(f"      {bar} {D}{current}/{target}{R}")

    print(f"\n{center(f'{D}{t('press_enter_return')}{R}')}")


def render_run_end_prestigio(earned, ante, won, new_challenges):
    """Render end-of-run prestigio summary."""
    print(f"\n  {GOLD}{B}{'═' * 40}{R}")
    print(f"  {GOLD}{B}✦ {t('run_summary')} ✦{R}")
    print(f"  {GOLD}{B}{'═' * 40}{R}")
    print(f"  {t('ante_reached')}: {B}{ante}{R}")
    result_str = f"{GRN}{B}{t('victory')}{R}" if won else f"{NRED}{t('game_over')}{R}"
    print(f"  {result_str}")
    print(f"\n  {GOLD}+{earned} {t('prestigio')}{R}")

    if new_challenges:
        print(f"\n  {NYEL}{B}{'─' * 30}{R}")
        for ch in new_challenges:
            lang = get_lang()
            name = ch.get("name_en", ch["name"]) if lang == "en" else ch["name"]
            print(f"  {NYEL}{B}🏆 {t('new_challenge')}{R}")
            print(f"  {ch['emoji']} {B}{name}{R} → {D}{ch['unlock_id']}{R}")
    print()
    print(center(f"{D}{t('press_enter_return')}{R}"))


def render_endless_unlock():
    """Special screen when endless mode is unlocked."""
    clear()
    print(f"\n\n{center(f'{GOLD}{B}{'═' * 40}{R}')}")
    print(center(f"{GOLD}{B}👑 {t('endless_unlocked')} 👑{R}"))
    print(center(f"{GOLD}{B}{'═' * 40}{R}"))
    print(center(f"{D}{t('endless_desc')}{R}"))
    print(f"\n{center(f'{D}{t(chr(112)+chr(114)+chr(101)+chr(115)+chr(115)+chr(95)+chr(101)+chr(110)+chr(116)+chr(101)+chr(114))}{R}')}")