"""Unit tests for Trucazo's rules, scoring, AI and persistence.

Run from this directory: python -B -m unittest -q test_trucazo
"""
import os
import random
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import collection
from cards import (Card, Edition, Mazo, Palo, Poder, envido_score, flor_score,
                   fuerza_mano, jerarquia, maybe_apply_auto_edition, tiene_flor)
from difficulty import DIFFICULTY_ORDER, get_difficulty_config
from hands import (Banca, calcular_envido_puntaje, calcular_puntaje_mano,
                   calcular_racha_mult, resolver_baza)

E, B, C, O = Palo.ESPADAS, Palo.BASTOS, Palo.COPAS, Palo.OROS


class DeckTests(unittest.TestCase):
    def test_deck_has_40_unique_truco_cards(self):
        cards = Mazo().cards
        self.assertEqual(len(cards), 40)
        self.assertEqual(len({(c.rank, c.palo) for c in cards}), 40)
        self.assertFalse({8, 9} & {c.rank for c in cards})

    def test_draw_reshuffles_discard_and_stops_when_empty(self):
        mazo = Mazo()
        drawn = mazo.sacar(40)
        mazo.al_descarte(drawn[:5])
        self.assertEqual(len(mazo.sacar(10)), 5)
        self.assertEqual(mazo.sacar(1), [])

    def test_restaurar_brings_back_every_card(self):
        mazo = Mazo()
        mazo.sacar(12)
        mazo.restaurar()
        self.assertEqual(len(mazo), 40)
        self.assertEqual(mazo.discard, [])


class CardValueTests(unittest.TestCase):
    def test_envido_and_point_values(self):
        self.assertEqual(Card(7, E).envido_val, 7)
        self.assertEqual(Card(12, E).envido_val, 0)
        self.assertEqual([Card(r, E).point_value for r in (1, 10, 11, 12)], [1, 8, 9, 10])

    def test_real_truco_hierarchy(self):
        order = [Card(1, E), Card(1, B), Card(7, E), Card(7, O), Card(3, C), Card(2, C),
                 Card(1, C), Card(12, C), Card(11, C), Card(10, C), Card(7, C),
                 Card(6, C), Card(5, C), Card(4, C)]
        ranks = [jerarquia(c) for c in order]
        self.assertEqual(ranks, sorted(ranks, reverse=True))
        self.assertEqual(len(set(ranks)), len(ranks))

    def test_false_aces_and_same_rank_suits_tie(self):
        self.assertEqual(jerarquia(Card(1, C)), jerarquia(Card(1, O)))
        self.assertEqual(jerarquia(Card(3, E)), jerarquia(Card(3, O)))

    def test_brillante_adds_hierarchy(self):
        self.assertEqual(jerarquia(Card(4, C, Edition.BRILLANTE)), jerarquia(Card(4, C)) + 5)


class EnvidoFlorTests(unittest.TestCase):
    def test_envido_same_suit_uses_two_highest(self):
        self.assertEqual(envido_score([Card(7, E), Card(6, E), Card(5, E)]), 33)
        self.assertEqual(envido_score([Card(7, E), Card(12, E), Card(5, C)]), 27)

    def test_envido_without_pair_is_highest_card(self):
        self.assertEqual(envido_score([Card(4, E), Card(6, B), Card(12, C)]), 6)
        self.assertEqual(envido_score([Card(10, E), Card(11, B), Card(12, C)]), 0)
        self.assertEqual(envido_score([]), 0)

    def test_two_figures_same_suit_score_20(self):
        self.assertEqual(envido_score([Card(10, E), Card(11, E), Card(7, C)]), 20)

    def test_flor(self):
        flor = [Card(1, O), Card(7, O), Card(12, O)]
        self.assertTrue(tiene_flor(flor))
        self.assertEqual(flor_score(flor), 28)
        self.assertFalse(tiene_flor(flor[:2]))
        self.assertFalse(tiene_flor([Card(1, O), Card(7, O), Card(12, C)]))

    def test_hand_strength_bounds(self):
        self.assertEqual(fuerza_mano([Card(1, E), Card(1, B), Card(7, E)]), 1.0)
        self.assertLess(fuerza_mano([Card(4, C), Card(4, B), Card(5, C)]), 0.5)
        self.assertEqual(fuerza_mano([]), 0)


class BazaTests(unittest.TestCase):
    def test_higher_card_wins_and_equal_is_parda(self):
        self.assertEqual(resolver_baza(Card(1, E), Card(3, C)), "player")
        self.assertEqual(resolver_baza(Card(4, C), Card(3, C)), "house")
        self.assertEqual(resolver_baza(Card(3, O), Card(3, C)), "parda")

    def test_poderes(self):
        self.assertEqual(resolver_baza(Card(3, C, poder=Poder.ESCUDO), Card(3, O)), "player")
        self.assertEqual(resolver_baza(Card(4, C, poder=Poder.ESPEJO), Card(1, E)), "player")
        # Hielo: 2 (85) beats 3 (90 - 15 = 75)
        self.assertEqual(resolver_baza(Card(2, C, poder=Poder.HIELO), Card(3, O)), "player")

    def test_poderes_can_be_disabled(self):
        card = Card(3, C, poder=Poder.ESCUDO)
        self.assertEqual(resolver_baza(card, Card(3, O), poder_activo=False), "parda")


class ScoringTests(unittest.TestCase):
    def test_racha_multiplier(self):
        self.assertEqual(calcular_racha_mult(0), 1.0)
        self.assertEqual(calcular_racha_mult(1), 1.0)
        self.assertEqual(calcular_racha_mult(2), 1.25)
        self.assertEqual(calcular_racha_mult(3), 1.5)
        self.assertEqual(calcular_racha_mult(4), 2.0)
        self.assertEqual(calcular_racha_mult(7), 2.5)
        self.assertEqual(calcular_racha_mult(3, racha_level=2), 2.0)

    def test_plain_hand_score(self):
        cards = [Card(1, E), Card(12, C), Card(5, O)]  # 1 + 10 + 5
        self.assertEqual(calcular_puntaje_mano(cards, 1), 16)
        self.assertEqual(calcular_puntaje_mano(cards, 2), 32)

    def test_score_is_at_least_one(self):
        self.assertEqual(calcular_puntaje_mano([], 1), 1)

    def test_poder_and_edition_bonuses(self):
        self.assertEqual(calcular_puntaje_mano([Card(5, C, poder=Poder.ECO)], 1), 10)
        self.assertEqual(calcular_puntaje_mano([Card(5, C, poder=Poder.FUEGO)], 1), 25)
        self.assertEqual(calcular_puntaje_mano([Card(5, C, Edition.PRISMATICA)], 1), 10)
        self.assertEqual(calcular_puntaje_mano([Card(5, C, Edition.BRILLANTE)], 1), 20)
        self.assertEqual(calcular_puntaje_mano([Card(4, C, poder=Poder.QUIEBRE)], 1), 10)
        self.assertEqual(calcular_puntaje_mano([Card(5, C, poder=Poder.CADENA)], 1, racha=1), 13)

    def test_augments_and_levels(self):
        cards = [Card(5, E), Card(4, C)]
        palo = SimpleNamespace(effect={"type": "palo_bonus", "palo": 0, "value": 10})
        mult = SimpleNamespace(effect={"type": "truco_bonus", "value": 2})
        self.assertEqual(calcular_puntaje_mano(cards, 1, augments=[palo]), 19)
        self.assertEqual(calcular_puntaje_mano(cards, 1, augments=[mult]), 18)
        self.assertEqual(calcular_puntaje_mano(cards, 1, levels={"truco": 3}), 19)

    def test_envido_points(self):
        self.assertEqual(calcular_envido_puntaje(33, 27), 20)
        self.assertEqual(calcular_envido_puntaje(27, 33), 20)
        self.assertEqual(calcular_envido_puntaje(30, 30, nivel_envido=2), 4)


class BancaTests(unittest.TestCase):
    hand = [Card(4, C), Card(3, C), Card(1, E)]

    def test_card_choice_strategy(self):
        banca = Banca()
        self.assertIsNone(banca.elegir_carta([], 0, 0, 0))
        self.assertEqual(banca.elegir_carta(self.hand, 0, 0, 0).rank, 3)
        self.assertEqual(banca.elegir_carta(self.hand, 1, 1, 0).rank, 4)
        self.assertEqual(banca.elegir_carta(self.hand, 1, 0, 1).rank, 1)

    def test_deterministic_decisions(self):
        banca = Banca(skill=0.5)
        self.assertEqual(banca.decidir_envido(27, 2), "accept")
        self.assertEqual(banca.decidir_truco(0.2, 2), "fold")
        self.assertFalse(banca.quiere_cantar_truco(1.0, 4))

    def test_random_decisions_follow_probabilities(self):
        banca = Banca(skill=1.0)
        with mock.patch("hands.random.random", return_value=0.0):
            self.assertEqual(banca.decidir_envido(31, 2), "raise")
            self.assertEqual(banca.decidir_truco(0.9, 2), "raise")
            self.assertTrue(banca.quiere_cantar_envido(28))
        with mock.patch("hands.random.random", return_value=0.99):
            self.assertEqual(banca.decidir_envido(31, 2), "accept")
            self.assertEqual(banca.decidir_truco(0.9, 4), "accept")
            self.assertFalse(banca.quiere_cantar_truco(0.9, 2))


class DifficultyTests(unittest.TestCase):
    def test_tiers_scale_monotonically(self):
        mults = [get_difficulty_config(t)["blind_mult"] for t in DIFFICULTY_ORDER]
        self.assertEqual(mults, sorted(mults))

    def test_unknown_tier_falls_back_to_normal(self):
        self.assertIs(get_difficulty_config("nope"), get_difficulty_config("normal"))


class AutoEditionTests(unittest.TestCase):
    def test_never_replaces_existing_edition(self):
        cards = [Card(5, C, Edition.ARCOIRIS)]
        maybe_apply_auto_edition(cards, bonus_chance=1.0)
        self.assertIs(cards[0].edition, Edition.ARCOIRIS)

    def test_certain_roll_applies_weighted_edition(self):
        random.seed(1)
        cards = [Card(5, C) for _ in range(20)]
        maybe_apply_auto_edition(cards, bonus_chance=1.0)
        self.assertTrue(all(c.edition in {Edition.DORADA, Edition.BRILLANTE,
                                          Edition.HOLOGRAFICA, Edition.PRISMATICA} for c in cards))


class CollectionTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.object(collection, "COLLECTION_FILE", os.path.join(tmp.name, "c.json"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_round_trip_keeps_sets_and_records(self):
        col = collection.Collection()
        col.discovered_poderes.add("FUEGO")
        col.record_run_end(ante=4, won=True)
        col.record_run_end(ante=2, won=False)
        loaded = collection.Collection()
        self.assertEqual(loaded.discovered_poderes, {"FUEGO"})
        self.assertEqual((loaded.total_runs, loaded.best_ante, loaded.wins), (2, 4, 1))

    def test_corrupt_file_is_ignored(self):
        with open(collection.COLLECTION_FILE, "w") as f:
            f.write("{broken")
        self.assertEqual(collection.Collection().total_runs, 0)

    def test_completion_percentage(self):
        col = collection.Collection()
        self.assertEqual(col.completion_pct, 0)
        col.discovered_poderes = {p.name for p in Poder if p != Poder.NADA}
        self.assertGreater(col.completion_pct, 0)
        self.assertLess(col.completion_pct, 100)


if __name__ == "__main__":
    unittest.main()
