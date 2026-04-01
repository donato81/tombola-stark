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

        # Azzera l'intera riga 0 di entrambe le cartelle prima di impostare i
        # valori controllati. Senza questo step la Cartella generata casualmente
        # potrebbe avere 11 o 22 già in altre colonne della riga 0: dopo la
        # marcatura verifica_ambo_riga conterebbe quei duplicati e rileverebbe
        # terno (o un premio più alto) invece di ambo, rendendo il test flaky.
        for col in range(cartella_1.colonne):
            cartella_1.cartella[0][col] = None
            cartella_2.cartella[0][col] = None

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

    def test_verifica_premi_solo_un_primo_vincitore_riceve_se_reclami_diversi(self) -> None:
        """
        Verifica che con reclami su tipi diversi entrambi i giocatori ricevano
        il proprio premio: G1 ottiene ambo, G2 ottiene ambo su riga diversa.
        Il tipo 'ambo' viene chiuso dopo l'assegnazione collettiva.
        """
        tabellone = Tabellone()
        giocatore_1 = GiocatoreBase("G1", id_giocatore=1)
        giocatore_2 = GiocatoreBase("G2", id_giocatore=2)
        cartella_1 = Cartella()
        cartella_2 = Cartella()
        giocatore_1.aggiungi_cartella(cartella_1)
        giocatore_2.aggiungi_cartella(cartella_2)
        partita = Partita(tabellone, [giocatore_1, giocatore_2])

        # Azzeramento deterministico: riga 0 per g1, riga 1 per g2.
        for col in range(cartella_1.colonne):
            cartella_1.cartella[0][col] = None
        for col in range(cartella_2.colonne):
            cartella_2.cartella[1][col] = None

        # G1: ambo su riga 0 (numeri 11, 22)
        cartella_1.cartella[0][0] = 11
        cartella_1.cartella[0][1] = 22
        # G2: ambo su riga 1 (numeri 33, 44)
        cartella_2.cartella[1][0] = 33
        cartella_2.cartella[1][1] = 44

        cartella_1.numeri_cartella = cartella_1._estrai_numeri_set()
        cartella_2.numeri_cartella = cartella_2._estrai_numeri_set()

        for numero in (11, 22):
            giocatore_1.aggiorna_con_numero(numero)
        for numero in (33, 44):
            giocatore_2.aggiorna_con_numero(numero)

        giocatore_1.reclamo_turno = ReclamoVittoria.vittoria_di_riga(
            tipo="ambo",
            indice_cartella=cartella_1.indice,
            indice_riga=0,
        )
        giocatore_2.reclamo_turno = ReclamoVittoria.vittoria_di_riga(
            tipo="ambo",
            indice_cartella=cartella_2.indice,
            indice_riga=1,
        )

        premi = partita.verifica_premi()

        self.assertEqual(len(premi), 2)
        self.assertTrue(all(evento["premio"] == "ambo" for evento in premi))
        self.assertEqual({evento["giocatore"] for evento in premi}, {"G1", "G2"})
        self.assertIn("ambo", partita.premi_tipo_chiusi)

    def test_verifica_premi_senza_reclami_restituisce_lista_vuota(self) -> None:
        """
        Verifica che senza reclami aperti verifica_premi restituisca una lista
        vuota e non modifichi premi_tipo_chiusi.
        """
        tabellone = Tabellone()
        giocatore_1 = GiocatoreBase("G1", id_giocatore=1)
        cartella_1 = Cartella()
        giocatore_1.aggiungi_cartella(cartella_1)
        partita = Partita(tabellone, [giocatore_1])

        # Nessun reclamo impostato: reclamo_turno è None di default.
        premi = partita.verifica_premi()

        self.assertEqual(premi, [])
        self.assertEqual(len(partita.premi_tipo_chiusi), 0)
