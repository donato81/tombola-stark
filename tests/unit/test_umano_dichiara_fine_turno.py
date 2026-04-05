import unittest

from bingo_game.cartella import Cartella
from bingo_game.comandi_partita import ComandiGiocatoreUmano
from bingo_game.game_controller import crea_partita_standard
from bingo_game.partita import Partita
from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
from bingo_game.tabellone import Tabellone


class TestUmanoDichiaraFineTurno(unittest.TestCase):
    def test_dichiara_fine_turno_imposta_flag_sul_giocatore(self) -> None:
        giocatore = GiocatoreUmano("Mario")

        self.assertFalse(giocatore.turno_dichiarato_concluso)
        giocatore.dichiara_fine_turno()
        self.assertTrue(giocatore.turno_dichiarato_concluso)

    def test_tutti_hanno_dichiarato_fine_include_bot(self) -> None:
        # V2: tutti_hanno_dichiarato_fine() include anche i giocatori automatici.
        tabellone = Tabellone()
        umano = GiocatoreUmano("Mario")
        bot = GiocatoreAutomatico("Bot1")
        umano.aggiungi_cartella(Cartella())
        bot.aggiungi_cartella(Cartella())
        partita = Partita(tabellone, [umano, bot])

        # All'inizio nessuno ha dichiarato fine.
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

        # Solo l'umano dichiara: il bot non ha ancora dichiarato → False.
        umano.dichiara_fine_turno()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

        # Anche il bot dichiara → True.
        bot.dichiara_fine_turno()
        self.assertTrue(partita.tutti_hanno_dichiarato_fine())


class TestComandiGiocatoreUmanoDichiarazioneTurno(unittest.TestCase):
    def _crea_partita_con_umano(self) -> Partita:
        return crea_partita_standard(
            nome_giocatore_umano="Mario",
            num_cartelle_umano=1,
            num_bot=1,
        )

    def test_turno_gia_dichiarato_false_prima_di_dichiarare(self) -> None:
        partita = self._crea_partita_con_umano()
        comandi = ComandiGiocatoreUmano(partita)
        self.assertFalse(comandi.turno_gia_dichiarato())

    def test_turno_gia_dichiarato_true_dopo_dichiarare(self) -> None:
        partita = self._crea_partita_con_umano()
        comandi = ComandiGiocatoreUmano(partita)
        comandi.dichiara_fine_turno(partita)
        self.assertTrue(comandi.turno_gia_dichiarato())

    def test_turno_gia_dichiarato_senza_giocatore_ritorna_false(self) -> None:
        tabellone = Tabellone()
        bot = GiocatoreAutomatico("Bot1")
        bot.aggiungi_cartella(Cartella())
        partita = Partita(tabellone, [bot])
        comandi = ComandiGiocatoreUmano(partita)
        self.assertFalse(comandi.turno_gia_dichiarato())
