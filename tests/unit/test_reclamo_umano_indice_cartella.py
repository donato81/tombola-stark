import unittest

from bingo_game.cartella import Cartella
from bingo_game.partita import Partita
from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
from bingo_game.tabellone import Tabellone


class TestReclamoUmanoIndiceCartella(unittest.TestCase):

    def test_annuncia_vittoria_tombola_usa_indice_cartella_1based(self) -> None:
        """
        Verifica che annuncia_vittoria("tombola") costruisca il reclamo con
        indice_cartella 1-based (cartella.indice) e non 0-based
        (_indice_cartella_focus).

        Contesto del bug corretto (fix(domain) 2026-04-01):
        _indice_cartella_focus vale 0 per la prima cartella.
        cartella.indice vale 1 per la prima cartella (assegnato da
        aggiungi_cartella).
        Partita.verifica_premi() cerca la cartella tramite c.indice, quindi
        il reclamo deve contenere il valore 1-based.
        """
        giocatore = GiocatoreUmano("Umano", id_giocatore=1)
        cartella = Cartella()
        giocatore.aggiungi_cartella(cartella)

        # imposta_focus_cartella usa input 1-based (valore "umano")
        esito_focus = giocatore.imposta_focus_cartella(1)
        self.assertTrue(esito_focus.ok, "Il focus sulla cartella 1 deve riuscire.")

        esito_vittoria = giocatore.annuncia_vittoria("tombola", numero_turno=1)
        self.assertTrue(
            esito_vittoria.ok,
            "annuncia_vittoria deve riuscire con focus impostato.",
        )

        self.assertIsNotNone(giocatore.reclamo_turno)

        # Il reclamo deve contenere l'indice 1-based della cartella di dominio
        self.assertEqual(
            giocatore.reclamo_turno.indice_cartella,
            giocatore.cartelle[0].indice,
            "indice_cartella nel reclamo deve coincidere con cartella.indice "
            "(1-based), non con l'indice della lista interna (0-based).",
        )

        # Guardia esplicita: il valore 0 è l'off-by-one che il bug produceva
        self.assertNotEqual(
            giocatore.reclamo_turno.indice_cartella,
            0,
            "indice_cartella non deve essere 0 (indice 0-based della lista).",
        )

    def test_covincita_tombola_umano_e_bot_stesso_turno(self) -> None:
        """
        Verifica che quando il giocatore umano e un bot raggiungono la tombola
        nello stesso turno, verifica_premi() assegni il premio a entrambi.

        Prima del fix, il reclamo umano veniva scartato silenziosamente perché
        indice_cartella era 0 (0-based) mentre la cartella aveva indice 1
        (1-based), rendendo impossibile la co-vincita.
        """
        tabellone = Tabellone()
        umano = GiocatoreUmano("Umano", id_giocatore=1)
        bot = GiocatoreAutomatico("Bot1", id_giocatore=2)
        cartella_umano = Cartella()
        cartella_bot = Cartella()
        umano.aggiungi_cartella(cartella_umano)
        bot.aggiungi_cartella(cartella_bot)
        partita = Partita(tabellone, [umano, bot])

        # Segna tutti i numeri della cartella umano (segnazione manuale:
        # il giocatore umano non riceve aggiornamenti automatici da Partita)
        for numero in list(cartella_umano.numeri_cartella):
            cartella_umano.segna_numero(numero)

        # Aggiorna il bot con tutti i numeri della sua cartella (percorso automatico)
        for numero in list(cartella_bot.numeri_cartella):
            bot.aggiorna_con_numero(numero)

        # Precondizione: entrambe le cartelle devono essere complete
        self.assertTrue(
            cartella_umano.verifica_cartella_completa(),
            "La cartella del giocatore umano deve essere completa.",
        )
        self.assertTrue(
            cartella_bot.verifica_cartella_completa(),
            "La cartella del bot deve essere completa.",
        )

        # Il giocatore umano annuncia tombola attraverso il percorso di produzione
        esito_focus = umano.imposta_focus_cartella(1)
        self.assertTrue(esito_focus.ok)
        esito_vittoria = umano.annuncia_vittoria("tombola", numero_turno=1)
        self.assertTrue(
            esito_vittoria.ok,
            "annuncia_vittoria tombola deve riuscire con focus cartella impostato.",
        )

        # Il bot costruisce il proprio reclamo tramite il percorso normale
        reclamo_bot = bot._valuta_potenziale_reclamo(
            partita.premi_gia_assegnati, partita.premi_tipo_chiusi
        )
        self.assertIsNotNone(reclamo_bot, "Il bot deve produrre un reclamo tombola.")
        bot.reclamo_turno = reclamo_bot

        # Verifica premi: entrambi devono ricevere il premio tombola
        premi = partita.verifica_premi()

        self.assertEqual(
            len(premi),
            2,
            "verifica_premi deve assegnare il premio tombola a entrambi i giocatori.",
        )
        nomi_vincitori = {evento["giocatore"] for evento in premi}
        self.assertIn("Umano", nomi_vincitori, "Il giocatore umano deve ricevere il premio tombola.")
        self.assertIn("Bot1", nomi_vincitori, "Il bot deve ricevere il premio tombola.")
        self.assertTrue(
            all(evento["premio"] == "tombola" for evento in premi),
            "Tutti i premi assegnati devono essere di tipo tombola.",
        )
        self.assertIn("tombola", partita.premi_tipo_chiusi)


if __name__ == "__main__":
    unittest.main()
