import unittest

from bingo_game.partita import Partita
from bingo_game.tabellone import Tabellone
from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
from bingo_game.cartella import Cartella


class TestFaseEstrazione(unittest.TestCase):
    def test_esegui_fase_estrazione_aggiorna_numero_e_fase(self) -> None:
        tabellone = Tabellone()
        umano = GiocatoreUmano("Mario")
        bot = GiocatoreAutomatico("Bot1")
        umano.aggiungi_cartella(Cartella())
        bot.aggiungi_cartella(Cartella())

        partita = Partita(tabellone, [umano, bot])
        partita.avvia_partita()

        risultato = partita.esegui_fase_estrazione()

        self.assertIsInstance(risultato, dict)
        self.assertIn("numero_estratto", risultato)
        self.assertEqual(risultato["fase"], "attesa_reclami")
        self.assertEqual(partita.fase_turno_corrente, "attesa_reclami")
        self.assertEqual(partita.tabellone.get_conteggio_estratti(), 1)
