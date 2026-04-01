import unittest

from bingo_game.cartella import Cartella
from bingo_game.events.eventi_partita import ReclamoVittoria
from bingo_game.partita import Partita
from bingo_game.players.giocatore_base import GiocatoreBase
from bingo_game.tabellone import Tabellone


class TestFaseVerificaCoVincita(unittest.TestCase):
    def test_verifica_premi_assegna_ambo_a_due_giocatori_nello_stesso_turno(self) -> None:
        tabellone = Tabellone()
        giocatore_1 = GiocatoreBase("G1", id_giocatore=1)
        giocatore_2 = GiocatoreBase("G2", id_giocatore=2)
        cartella_1 = Cartella()
        cartella_2 = Cartella()
        giocatore_1.aggiungi_cartella(cartella_1)
        giocatore_2.aggiungi_cartella(cartella_2)
        partita = Partita(tabellone, [giocatore_1, giocatore_2])

        numeri_comuni = [11, 22]
        cartella_1.cartella[0][0] = numeri_comuni[0]
        cartella_1.cartella[0][1] = numeri_comuni[1]
        cartella_2.cartella[0][0] = numeri_comuni[0]
        cartella_2.cartella[0][1] = numeri_comuni[1]
        cartella_1.numeri_cartella = cartella_1._estrai_numeri_set()
        cartella_2.numeri_cartella = cartella_2._estrai_numeri_set()

        for numero in numeri_comuni:
            giocatore_1.aggiorna_con_numero(numero)
            giocatore_2.aggiorna_con_numero(numero)

        giocatore_1.reclamo_turno = ReclamoVittoria.vittoria_di_riga(
            tipo="ambo",
            indice_cartella=cartella_1.indice,
            indice_riga=0,
        )
        giocatore_2.reclamo_turno = ReclamoVittoria.vittoria_di_riga(
            tipo="ambo",
            indice_cartella=cartella_2.indice,
            indice_riga=0,
        )

        premi = partita.verifica_premi()

        self.assertEqual(len(premi), 2)
        self.assertTrue(all(evento["premio"] == "ambo" for evento in premi))
        self.assertEqual({evento["giocatore"] for evento in premi}, {"G1", "G2"})
        self.assertIn("ambo", partita.premi_tipo_chiusi)
