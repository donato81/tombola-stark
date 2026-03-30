"""
Test unitari per EsitoAzione - Gruppo D.

Perimetro: costruzione, __str__, __eq__, __contains__.
Libreria: unittest.
"""
import unittest

from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.eventi_ui import (
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
)
from bingo_game.events.eventi_output_ui_umani import (
    EventoSegnazioneNumero,
    RisultatoRicercaNumeroInCartella,
    EventoRicercaNumeroInCartelle,
)


# ---------------------------------------------------------------------------
# Classe 1 — Costruzione
# ---------------------------------------------------------------------------

class TestEsitoAzioneCostruzione(unittest.TestCase):

    def test_successo_senza_evento(self):
        esito = EsitoAzione.successo()
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)
        self.assertIsNone(esito.evento)

    def test_successo_con_evento_valorizzato(self):
        evento = EventoFocusCartellaImpostato(
            id_giocatore=1,
            nome_giocatore="Tester",
            numero_cartella=2,
            indice_cartella=1,
            reset_riga_colonna=False,
        )
        esito = EsitoAzione.successo(evento=evento)
        self.assertTrue(esito.ok)
        self.assertIs(esito.evento, evento)

    def test_fallimento_errore_interno(self):
        esito = EsitoAzione.fallimento("ERRORE_INTERNO")
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "ERRORE_INTERNO")
        self.assertIsNone(esito.evento)


# ---------------------------------------------------------------------------
# Classe 2 — __str__ ramo fallimento
# ---------------------------------------------------------------------------

class TestEsitoAzioneStrFallimento(unittest.TestCase):

    def test_str_cartelle_nessuna_assegnata(self):
        esito = EsitoAzione.fallimento("CARTELLE_NESSUNA_ASSEGNATA")
        self.assertEqual(str(esito), "Errore: Non hai ancora assegnato nessuna cartella.")

    def test_str_focus_cartella_non_impostato(self):
        esito = EsitoAzione.fallimento("FOCUS_CARTELLA_NON_IMPOSTATO")
        self.assertEqual(str(esito), "Non hai selezionato nessuna cartella")

    def test_str_numero_non_valido(self):
        esito = EsitoAzione.fallimento("NUMERO_NON_VALIDO")
        self.assertEqual(str(esito), "Errore: numero non valido. Deve essere tra 1 e 90")

    def test_str_numero_tipo_non_valido(self):
        esito = EsitoAzione.fallimento("NUMERO_TIPO_NON_VALIDO")
        self.assertEqual(str(esito), "Errore: tipo numero non valido")

    def test_str_focus_cartella_fuori_range(self):
        esito = EsitoAzione.fallimento("FOCUS_CARTELLA_FUORI_RANGE")
        self.assertEqual(str(esito), "Errore: focus cartella fuori range")

    def test_str_fallback_errore_interno(self):
        esito = EsitoAzione.fallimento("ERRORE_INTERNO")
        self.assertEqual(str(esito), "Errore: ERRORE_INTERNO")


# ---------------------------------------------------------------------------
# Classe 3 — __str__ ramo successo
# ---------------------------------------------------------------------------

class TestEsitoAzioneStrSuccesso(unittest.TestCase):

    def test_str_evento_none(self):
        esito = EsitoAzione.successo()
        self.assertEqual(str(esito), "Ok")

    def test_str_focus_cartella_impostato(self):
        evento = EventoFocusCartellaImpostato(
            id_giocatore=None,
            nome_giocatore="Tester",
            numero_cartella=3,
            indice_cartella=2,
        )
        esito = EsitoAzione.successo(evento=evento)
        self.assertEqual(str(esito), "Focus impostato sulla cartella 3.")

    def test_str_focus_auto_impostato(self):
        evento = EventoFocusAutoImpostato(tipo_focus="cartella", indice=0)
        esito = EsitoAzione.successo(evento=evento)
        self.assertEqual(str(esito), "Focus auto-impostato su cartella 0.")

    def test_str_segnazione_segnato(self):
        evento = EventoSegnazioneNumero.segnato(
            id_giocatore=None,
            nome_giocatore="Tester",
            numero=42,
            indice_cartella=0,
            totale_cartelle=1,
            indice_riga=1,
            indice_colonna=3,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.3,
        )
        esito = EsitoAzione.successo(evento=evento)
        self.assertEqual(str(esito), "Fatto! Segnato numero 42")

    def test_str_segnazione_gia_segnato(self):
        evento = EventoSegnazioneNumero.gia_segnato(
            id_giocatore=None,
            nome_giocatore="Tester",
            numero=42,
            indice_cartella=0,
            totale_cartelle=1,
            indice_riga=1,
            indice_colonna=3,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.3,
        )
        esito = EsitoAzione.successo(evento=evento)
        self.assertEqual(str(esito), "Numero 42 è già stato segnato")

    def test_str_segnazione_non_presente(self):
        evento = EventoSegnazioneNumero.non_presente(
            id_giocatore=None,
            nome_giocatore="Tester",
            numero=42,
            indice_cartella=0,
            totale_cartelle=1,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.3,
        )
        esito = EsitoAzione.successo(evento=evento)
        self.assertEqual(str(esito), "Numero 42 non è presente nella Cartella 1")

    def test_str_segnazione_non_estratto(self):
        evento = EventoSegnazioneNumero.non_estratto(
            id_giocatore=None,
            nome_giocatore="Tester",
            numero=42,
            indice_cartella=0,
            totale_cartelle=1,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.3,
        )
        esito = EsitoAzione.successo(evento=evento)
        self.assertEqual(str(esito), "Numero 42 non è ancora stato estratto")

    def test_str_ricerca_non_trovato(self):
        evento = EventoRicercaNumeroInCartelle.non_trovato(
            id_giocatore=None,
            nome_giocatore="Tester",
            numero=7,
            totale_cartelle=2,
        )
        esito = EsitoAzione.successo(evento=evento)
        self.assertEqual(str(esito), "Il numero 7 non è presente nelle tue cartelle")

    def test_str_ricerca_trovato_multiriga(self):
        risultato = RisultatoRicercaNumeroInCartella.crea(
            indice_cartella=0,
            indice_riga=1,
            indice_colonna=2,
            segnato=False,
        )
        evento = EventoRicercaNumeroInCartelle.trovato(
            id_giocatore=None,
            nome_giocatore="Tester",
            numero=7,
            totale_cartelle=1,
            risultati=[risultato],
        )
        esito = EsitoAzione.successo(evento=evento)
        testo = str(esito)
        self.assertIn("Trovato 7 in:", testo)
        self.assertIn("Cartella 1:", testo)
        self.assertIn("Riga 2", testo)
        self.assertIn("Colonna 3", testo)

    def test_str_evento_non_riconosciuto_fallback(self):
        class _FakeEvent:
            def __str__(self) -> str:
                return "evento_sconosciuto_42"

        evento = _FakeEvent()
        esito = EsitoAzione(ok=True, errore=None, evento=evento)  # type: ignore[arg-type]
        self.assertEqual(str(esito), str(evento))


# ---------------------------------------------------------------------------
# Classe 4 — __eq__ e __contains__
# ---------------------------------------------------------------------------

class TestEsitoAzioneEqContains(unittest.TestCase):

    def test_eq_stessa_istanza_successo(self):
        a = EsitoAzione.successo()
        self.assertEqual(a, a)

    def test_eq_due_successi_distinti_stessi_campi_false(self):
        a = EsitoAzione.successo()
        b = EsitoAzione.successo()
        self.assertNotEqual(a, b)

    def test_eq_successo_vs_fallimento(self):
        a = EsitoAzione.successo()
        b = EsitoAzione.fallimento("ERRORE_INTERNO")
        self.assertNotEqual(a, b)

    def test_eq_stessa_istanza_fallimento(self):
        a = EsitoAzione.fallimento("NUMERO_NON_VALIDO")
        self.assertEqual(a, a)

    def test_eq_due_fallimenti_distinti_stesso_codice_false(self):
        a = EsitoAzione.fallimento("NUMERO_NON_VALIDO")
        b = EsitoAzione.fallimento("NUMERO_NON_VALIDO")
        self.assertNotEqual(a, b)

    def test_contains_stringa_presente(self):
        esito = EsitoAzione.fallimento("NUMERO_NON_VALIDO")
        self.assertIn("numero non valido", esito)

    def test_contains_stringa_assente(self):
        esito = EsitoAzione.fallimento("NUMERO_NON_VALIDO")
        self.assertNotIn("FOCUS", esito)

    def test_eq_stringa_cartelle_nessuna_assegnata(self):
        esito = EsitoAzione.fallimento("CARTELLE_NESSUNA_ASSEGNATA")
        self.assertEqual(esito, "Non hai selezionato nessuna cartella")
        self.assertEqual(esito, "Errore: Non hai ancora assegnato nessuna cartella.")

    def test_eq_stringa_focus_cartella_non_impostato(self):
        esito = EsitoAzione.fallimento("FOCUS_CARTELLA_NON_IMPOSTATO")
        self.assertEqual(esito, "Non hai selezionato nessuna cartella")
        self.assertEqual(esito, "Errore: Seleziona prima una cartella su cui segnare il numero.")


if __name__ == "__main__":
    unittest.main()
