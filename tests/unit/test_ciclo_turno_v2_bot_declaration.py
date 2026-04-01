"""
Test unitari per GiocatoreAutomatico.dichiara_fine_fase_azione() — Ciclo Turno V2.

Copertura (minimo 4 test):
- B-2a: nessun reclamo (cartella vuota)
- B-2b: ambo disponibile
- B-2c: tombola disponibile
- B-2d: reset corretto tra turni (reclamo, poi reset, poi nuova dichiarazione)
"""
from __future__ import annotations

import unittest

from bingo_game.cartella import Cartella
from bingo_game.players import GiocatoreAutomatico


def _crea_bot_con_cartella() -> tuple[GiocatoreAutomatico, Cartella]:
    bot = GiocatoreAutomatico("BotTest")
    cartella = Cartella()
    bot.aggiungi_cartella(cartella)
    return bot, cartella


class TestDichiaraFineFaseAzione(unittest.TestCase):

    def test_nessun_reclamo_cartella_vuota(self) -> None:
        """Nessun numero segnato: reclamo_turno=None, turno_dichiarato_concluso=True."""
        bot, _ = _crea_bot_con_cartella()

        bot.dichiara_fine_fase_azione(set(), None)

        self.assertIsNone(bot.reclamo_turno)
        self.assertTrue(bot.turno_dichiarato_concluso)

    def test_ambo_disponibile(self) -> None:
        """Con 2 numeri segnati sulla stessa riga: reclamo ambo impostato."""
        bot, cartella = _crea_bot_con_cartella()
        numeri_riga_0 = [n for n in cartella.cartella[0] if n is not None][:2]
        for num in numeri_riga_0:
            cartella.segna_numero(num)

        bot.dichiara_fine_fase_azione(set(), None)

        self.assertIsNotNone(bot.reclamo_turno)
        self.assertEqual(bot.reclamo_turno.tipo, "ambo")
        self.assertTrue(bot.turno_dichiarato_concluso)

    def test_tombola_disponibile(self) -> None:
        """Tutti i 15 numeri segnati: reclamo tombola impostato."""
        bot, cartella = _crea_bot_con_cartella()
        for riga in range(3):
            for num in cartella.cartella[riga]:
                if num is not None:
                    cartella.segna_numero(num)

        bot.dichiara_fine_fase_azione(set(), None)

        self.assertIsNotNone(bot.reclamo_turno)
        self.assertEqual(bot.reclamo_turno.tipo, "tombola")
        self.assertTrue(bot.turno_dichiarato_concluso)

    def test_reset_corretto_tra_turni(self) -> None:
        """Dopo reset_reclamo_turno e turno_dichiarato_concluso=False, il bot può dichiarare nuovamente."""
        bot, cartella = _crea_bot_con_cartella()
        numeri_riga_0 = [n for n in cartella.cartella[0] if n is not None][:2]
        for num in numeri_riga_0:
            cartella.segna_numero(num)

        # Primo turno
        bot.dichiara_fine_fase_azione(set(), None)
        self.assertIsNotNone(bot.reclamo_turno)
        self.assertTrue(bot.turno_dichiarato_concluso)

        # Simula reset tra turni (come fa esegui_fase_verifica)
        bot.reset_reclamo_turno()
        bot.turno_dichiarato_concluso = False

        self.assertIsNone(bot.reclamo_turno)
        self.assertFalse(bot.turno_dichiarato_concluso)

        # Secondo turno: il bot può dichiarare di nuovo
        bot.dichiara_fine_fase_azione(set(), None)
        self.assertIsNotNone(bot.reclamo_turno)
        self.assertTrue(bot.turno_dichiarato_concluso)

    def test_reclamo_non_doppio_se_premio_gia_assegnato(self) -> None:
        """Se il premio è già in premi_gia_assegnati, il bot non reclama."""
        bot, cartella = _crea_bot_con_cartella()
        numeri_riga_0 = [n for n in cartella.cartella[0] if n is not None][:2]
        for num in numeri_riga_0:
            cartella.segna_numero(num)

        # Simula che l'ambo sulla riga 0 sia già stato assegnato
        chiave_ambo = f"cartella_{cartella.indice}_riga_0_ambo"
        bot.dichiara_fine_fase_azione({chiave_ambo}, None)

        self.assertIsNone(bot.reclamo_turno)
        self.assertTrue(bot.turno_dichiarato_concluso)
