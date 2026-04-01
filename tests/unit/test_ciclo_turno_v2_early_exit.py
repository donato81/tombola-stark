"""
Test unitari per terminazione anticipata (early exit) del ciclo V2.

Verifica che tutti_hanno_dichiarato_fine() torni True quando
umano + bot hanno entrambi dichiarato fine.

Task B-3.
"""
from __future__ import annotations

import unittest

from bingo_game.cartella import Cartella
from bingo_game.partita import Partita
from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
from bingo_game.tabellone import Tabellone


class TestEarlyExit(unittest.TestCase):

    def _crea_partita(self) -> tuple[Partita, GiocatoreUmano, GiocatoreAutomatico]:
        tabellone = Tabellone()
        umano = GiocatoreUmano("Mario")
        bot = GiocatoreAutomatico("Bot1")
        umano.aggiungi_cartella(Cartella())
        bot.aggiungi_cartella(Cartella())
        partita = Partita(tabellone, [umano, bot])
        return partita, umano, bot

    def test_early_exit_false_nessuno_ha_dichiarato(self) -> None:
        """All'inizio nessuno ha dichiarato: tutti_hanno_dichiarato_fine() == False."""
        partita, _, _ = self._crea_partita()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

    def test_early_exit_false_solo_umano(self) -> None:
        """Solo umano ha dichiarato: bot ancora in attesa → False."""
        partita, umano, _ = self._crea_partita()
        umano.dichiara_fine_turno()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

    def test_early_exit_false_solo_bot(self) -> None:
        """Solo bot ha dichiarato: umano ancora in attesa → False."""
        partita, _, bot = self._crea_partita()
        bot.dichiara_fine_turno()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

    def test_early_exit_true_entrambi_dichiarano(self) -> None:
        """Quando entrambi dichiarano fine: tutti_hanno_dichiarato_fine() == True."""
        partita, umano, bot = self._crea_partita()
        umano.dichiara_fine_turno()
        bot.dichiara_fine_turno()
        self.assertTrue(partita.tutti_hanno_dichiarato_fine())

    def test_early_exit_ordine_non_influenza(self) -> None:
        """Il risultato dipende dallo stato di tutti, non dall'ordine di dichiarazione."""
        partita, umano, bot = self._crea_partita()
        bot.dichiara_fine_turno()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())
        umano.dichiara_fine_turno()
        self.assertTrue(partita.tutti_hanno_dichiarato_fine())
