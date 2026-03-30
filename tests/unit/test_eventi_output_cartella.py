"""
Test unitari per le classi E1 di eventi_output_ui_umani.py:
- EventoRiepilogoCartellaCorrente
- EventoLimiteNavigazioneCartelle
- EventoVisualizzaCartellaSemplice
- EventoVisualizzaCartellaAvanzata

Perimetro: solo E1. Zero mock, zero import pytest.
"""

import unittest
from bingo_game.events.eventi_output_ui_umani import (
    EventoRiepilogoCartellaCorrente,
    EventoLimiteNavigazioneCartelle,
    EventoVisualizzaCartellaSemplice,
    EventoVisualizzaCartellaAvanzata,
)


class TestEventoRiepilogoCartellaCorrente(unittest.TestCase):

    def test_crea_da_cartella_converte_indice_0_in_numero_1(self):
        evento = EventoRiepilogoCartellaCorrente.crea_da_cartella(
            id_giocatore=1,
            nome_giocatore="Mario",
            indice_cartella=0,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.3,
            numeri_non_segnati=[10, 20, 30, 40, 50, 60, 70, 80, 90, 11],
        )
        self.assertEqual(evento.numero_cartella, 1)
        self.assertEqual(evento.indice_cartella, 0)

    def test_crea_da_cartella_indice_2_produce_numero_3(self):
        evento = EventoRiepilogoCartellaCorrente.crea_da_cartella(
            id_giocatore=1,
            nome_giocatore="Mario",
            indice_cartella=2,
            numeri_segnati=0,
            totale_numeri=15,
            percentuale=0.0,
            numeri_non_segnati=[],
        )
        self.assertEqual(evento.numero_cartella, 3)

    def test_crea_da_cartella_ordina_numeri_non_segnati(self):
        evento = EventoRiepilogoCartellaCorrente.crea_da_cartella(
            id_giocatore=1,
            nome_giocatore="Mario",
            indice_cartella=0,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.3,
            numeri_non_segnati=[90, 10, 50, 20, 30],
        )
        self.assertEqual(evento.numeri_non_segnati, (10, 20, 30, 50, 90))

    def test_crea_da_cartella_calcola_mancanti_da_lista_ordinata(self):
        evento = EventoRiepilogoCartellaCorrente.crea_da_cartella(
            id_giocatore=1,
            nome_giocatore="Mario",
            indice_cartella=0,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.3,
            numeri_non_segnati=[90, 10, 50, 20, 30, 40, 60, 70, 80, 11],
        )
        self.assertEqual(evento.mancanti, 10)

    def test_crea_da_cartella_mancanti_lista_vuota(self):
        evento = EventoRiepilogoCartellaCorrente.crea_da_cartella(
            id_giocatore=1,
            nome_giocatore="Mario",
            indice_cartella=0,
            numeri_segnati=15,
            totale_numeri=15,
            percentuale=100.0,
            numeri_non_segnati=[],
        )
        self.assertEqual(evento.mancanti, 0)

    def test_crea_da_cartella_preserva_campi_input(self):
        evento = EventoRiepilogoCartellaCorrente.crea_da_cartella(
            id_giocatore=42,
            nome_giocatore="Luigi",
            indice_cartella=1,
            numeri_segnati=7,
            totale_numeri=15,
            percentuale=46.67,
            numeri_non_segnati=[3, 5, 9, 11, 13, 17, 19, 23],
        )
        self.assertEqual(evento.id_giocatore, 42)
        self.assertEqual(evento.nome_giocatore, "Luigi")
        self.assertEqual(evento.numeri_segnati, 7)
        self.assertEqual(evento.totale_numeri, 15)
        self.assertAlmostEqual(evento.percentuale, 46.67)


class TestEventoLimiteNavigazioneCartelle(unittest.TestCase):

    def test_limite_minimo_imposta_limite_e_numero_1(self):
        evento = EventoLimiteNavigazioneCartelle.limite_minimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="precedente",
            totale_cartelle=3,
        )
        self.assertEqual(evento.limite, "minimo")
        self.assertEqual(evento.numero_cartella_corrente, 1)

    def test_limite_massimo_imposta_limite_e_numero_uguale_totale(self):
        evento = EventoLimiteNavigazioneCartelle.limite_massimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="successiva",
            totale_cartelle=5,
        )
        self.assertEqual(evento.limite, "massimo")
        self.assertEqual(evento.numero_cartella_corrente, 5)

    def test_limite_minimo_preserva_campi_input(self):
        evento = EventoLimiteNavigazioneCartelle.limite_minimo(
            id_giocatore=7,
            nome_giocatore="Luigi",
            direzione="precedente",
            totale_cartelle=4,
        )
        self.assertEqual(evento.id_giocatore, 7)
        self.assertEqual(evento.nome_giocatore, "Luigi")
        self.assertEqual(evento.direzione, "precedente")
        self.assertEqual(evento.totale_cartelle, 4)

    def test_limite_massimo_preserva_campi_input(self):
        evento = EventoLimiteNavigazioneCartelle.limite_massimo(
            id_giocatore=7,
            nome_giocatore="Luigi",
            direzione="successiva",
            totale_cartelle=4,
        )
        self.assertEqual(evento.id_giocatore, 7)
        self.assertEqual(evento.nome_giocatore, "Luigi")
        self.assertEqual(evento.direzione, "successiva")
        self.assertEqual(evento.totale_cartelle, 4)
        self.assertEqual(evento.numero_cartella_corrente, 4)


class TestEventoVisualizzaCartellaSemplice(unittest.TestCase):

    def setUp(self):
        self.griglia = (
            (1, "-", 21, "-", 41, "-", 61, "-", 81),
            ("-", 12, "-", 32, "-", 52, "-", 72, "-"),
            (3, "-", 23, "-", 43, "-", 63, "-", 83),
        )

    def test_crea_da_cartella_converte_indice_0_in_numero_1(self):
        evento = EventoVisualizzaCartellaSemplice.crea_da_cartella(
            indice_cartella=0,
            totale_cartelle=3,
            griglia_semplice=self.griglia,
        )
        self.assertEqual(evento.numero_cartella, 1)
        self.assertEqual(evento.indice_cartella, 0)

    def test_crea_da_cartella_indice_2_produce_numero_3(self):
        evento = EventoVisualizzaCartellaSemplice.crea_da_cartella(
            indice_cartella=2,
            totale_cartelle=3,
            griglia_semplice=self.griglia,
        )
        self.assertEqual(evento.numero_cartella, 3)

    def test_crea_da_cartella_preserva_totale_cartelle(self):
        evento = EventoVisualizzaCartellaSemplice.crea_da_cartella(
            indice_cartella=0,
            totale_cartelle=6,
            griglia_semplice=self.griglia,
        )
        self.assertEqual(evento.totale_cartelle, 6)

    def test_crea_da_cartella_griglia_e_righe_sono_tuple(self):
        evento = EventoVisualizzaCartellaSemplice.crea_da_cartella(
            indice_cartella=0,
            totale_cartelle=3,
            griglia_semplice=self.griglia,
        )
        self.assertIsInstance(evento.griglia_semplice, tuple)
        for riga in evento.griglia_semplice:
            self.assertIsInstance(riga, tuple)

    def test_crea_da_cartella_preserva_contenuto_griglia(self):
        evento = EventoVisualizzaCartellaSemplice.crea_da_cartella(
            indice_cartella=0,
            totale_cartelle=3,
            griglia_semplice=self.griglia,
        )
        self.assertEqual(evento.griglia_semplice, self.griglia)


class TestEventoVisualizzaCartellaAvanzata(unittest.TestCase):

    def setUp(self):
        self.griglia = (
            (1, "-", 21, "-", 41, "-", 61, "-", 81),
            ("-", 12, "-", 32, "-", 52, "-", 72, "-"),
            (3, "-", 23, "-", 43, "-", 63, "-", 83),
        )
        self.stato = {
            "segnati": 3,
            "mancanti": 12,
            "percentuale": 20.0,
            "numeri_segnati": (1, 3, 12),
        }
        self.numeri_segnati = (1, 3, 12)
        self.dati_avanzati = (self.griglia, self.stato, self.numeri_segnati)

    def test_costruzione_diretta_campi_completi(self):
        evento = EventoVisualizzaCartellaAvanzata(
            indice_cartella=0,
            numero_cartella=1,
            totale_cartelle=3,
            griglia_semplice=self.griglia,
            stato_cartella=self.stato,
            numeri_segnati_ordinati=self.numeri_segnati,
        )
        self.assertEqual(evento.indice_cartella, 0)
        self.assertEqual(evento.numero_cartella, 1)
        self.assertEqual(evento.totale_cartelle, 3)
        self.assertEqual(evento.griglia_semplice, self.griglia)
        self.assertEqual(evento.stato_cartella, self.stato)
        self.assertEqual(evento.numeri_segnati_ordinati, self.numeri_segnati)

    def test_crea_da_dati_avanzati_converte_indice_0_in_numero_1(self):
        evento = EventoVisualizzaCartellaAvanzata.crea_da_dati_avanzati(
            indice_cartella=0,
            totale_cartelle=3,
            dati_avanzati=self.dati_avanzati,
        )
        self.assertEqual(evento.numero_cartella, 1)
        self.assertEqual(evento.indice_cartella, 0)

    def test_crea_da_dati_avanzati_indice_1_produce_numero_2(self):
        evento = EventoVisualizzaCartellaAvanzata.crea_da_dati_avanzati(
            indice_cartella=1,
            totale_cartelle=3,
            dati_avanzati=self.dati_avanzati,
        )
        self.assertEqual(evento.numero_cartella, 2)

    def test_crea_da_dati_avanzati_scompone_griglia_stato_segnati(self):
        evento = EventoVisualizzaCartellaAvanzata.crea_da_dati_avanzati(
            indice_cartella=0,
            totale_cartelle=3,
            dati_avanzati=self.dati_avanzati,
        )
        self.assertEqual(evento.griglia_semplice, self.griglia)
        self.assertEqual(evento.stato_cartella, self.stato)
        self.assertEqual(evento.numeri_segnati_ordinati, self.numeri_segnati)

    def test_crea_da_dati_avanzati_preserva_totale_cartelle(self):
        evento = EventoVisualizzaCartellaAvanzata.crea_da_dati_avanzati(
            indice_cartella=0,
            totale_cartelle=5,
            dati_avanzati=self.dati_avanzati,
        )
        self.assertEqual(evento.totale_cartelle, 5)


if __name__ == "__main__":
    unittest.main()
