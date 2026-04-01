"""
Test unitari per tutti_hanno_dichiarato_fine() con più bot — Ciclo Turno V2.

Verifica che la nuova semantica includa tutti i giocatori (1 umano + 3 bot).

Task B-4.
"""
from __future__ import annotations

import unittest

from bingo_game.cartella import Cartella
from bingo_game.partita import Partita
from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
from bingo_game.tabellone import Tabellone


class TestTuttiProntiMultiBot(unittest.TestCase):

    def _crea_partita_multi_bot(self) -> tuple[Partita, GiocatoreUmano, list[GiocatoreAutomatico]]:
        tabellone = Tabellone()
        umano = GiocatoreUmano("Mario")
        umano.aggiungi_cartella(Cartella())
        bot1 = GiocatoreAutomatico("Bot1")
        bot1.aggiungi_cartella(Cartella())
        bot2 = GiocatoreAutomatico("Bot2")
        bot2.aggiungi_cartella(Cartella())
        bot3 = GiocatoreAutomatico("Bot3")
        bot3.aggiungi_cartella(Cartella())
        partita = Partita(tabellone, [umano, bot1, bot2, bot3])
        return partita, umano, [bot1, bot2, bot3]

    def test_false_nessuno(self) -> None:
        """Nessuno ha dichiarato → False."""
        partita, _, _ = self._crea_partita_multi_bot()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

    def test_false_solo_umano(self) -> None:
        """Solo umano → False (3 bot in attesa)."""
        partita, umano, _ = self._crea_partita_multi_bot()
        umano.dichiara_fine_turno()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

    def test_false_umano_e_due_bot(self) -> None:
        """Umano + 2 bot → False (1 bot manca ancora)."""
        partita, umano, bots = self._crea_partita_multi_bot()
        umano.dichiara_fine_turno()
        bots[0].dichiara_fine_turno()
        bots[1].dichiara_fine_turno()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

    def test_true_tutti_dichiarano(self) -> None:
        """Umano + tutti e 3 i bot → True."""
        partita, umano, bots = self._crea_partita_multi_bot()
        umano.dichiara_fine_turno()
        for bot in bots:
            bot.dichiara_fine_turno()
        self.assertTrue(partita.tutti_hanno_dichiarato_fine())

    def test_reset_riporta_a_false(self) -> None:
        """Dopo reset del turno (turno_dichiarato_concluso=False per tutti) → False."""
        partita, umano, bots = self._crea_partita_multi_bot()
        umano.dichiara_fine_turno()
        for bot in bots:
            bot.dichiara_fine_turno()
        self.assertTrue(partita.tutti_hanno_dichiarato_fine())

        # Reset come fa esegui_fase_verifica
        for giocatore in partita.giocatori:
            giocatore.turno_dichiarato_concluso = False

        self.assertFalse(partita.tutti_hanno_dichiarato_fine())
