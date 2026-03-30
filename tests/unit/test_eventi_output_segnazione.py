"""
Test unitari per le classi E4 di eventi_output_ui_umani.py:
- EventoSegnazioneNumero
- RisultatoRicercaNumeroInCartella
- EventoRicercaNumeroInCartelle

Perimetro: solo E4. Zero mock, zero import pytest.
"""

import unittest
from bingo_game.events.eventi_output_ui_umani import (
    EventoSegnazioneNumero,
    RisultatoRicercaNumeroInCartella,
    EventoRicercaNumeroInCartelle,
)


class TestEventoSegnazioneNumero(unittest.TestCase):

    def test_segnato_valorizza_coordinate_e_numero_1based(self):
        evento = EventoSegnazioneNumero.segnato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=25,
            indice_cartella=0,
            totale_cartelle=3,
            indice_riga=1,
            indice_colonna=4,
            numeri_segnati=6,
            totale_numeri=15,
            percentuale=40.0,
        )
        self.assertEqual(evento.esito, "segnato")
        self.assertEqual(evento.numero_cartella, 1)
        self.assertEqual(evento.indice_riga, 1)
        self.assertEqual(evento.indice_colonna, 4)
        self.assertEqual(evento.mancanti, 9)

    def test_segnato_indice_cartella_2_produce_numero_3(self):
        evento = EventoSegnazioneNumero.segnato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=25,
            indice_cartella=2,
            totale_cartelle=3,
            indice_riga=0,
            indice_colonna=0,
            numeri_segnati=1,
            totale_numeri=15,
            percentuale=6.67,
        )
        self.assertEqual(evento.numero_cartella, 3)

    def test_segnato_calcola_mancanti(self):
        evento = EventoSegnazioneNumero.segnato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=7,
            indice_cartella=0,
            totale_cartelle=1,
            indice_riga=0,
            indice_colonna=0,
            numeri_segnati=10,
            totale_numeri=15,
            percentuale=66.67,
        )
        self.assertEqual(evento.mancanti, 5)

    def test_gia_segnato_valorizza_coordinate_e_numero_1based(self):
        evento = EventoSegnazioneNumero.gia_segnato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=7,
            indice_cartella=0,
            totale_cartelle=1,
            indice_riga=0,
            indice_colonna=0,
            numeri_segnati=3,
            totale_numeri=15,
            percentuale=20.0,
        )
        self.assertEqual(evento.esito, "gia_segnato")
        self.assertEqual(evento.numero_cartella, 1)
        self.assertEqual(evento.indice_riga, 0)
        self.assertEqual(evento.indice_colonna, 0)
        self.assertEqual(evento.mancanti, 12)

    def test_gia_segnato_calcola_mancanti(self):
        evento = EventoSegnazioneNumero.gia_segnato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=7,
            indice_cartella=0,
            totale_cartelle=1,
            indice_riga=0,
            indice_colonna=0,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.33,
        )
        self.assertEqual(evento.mancanti, 10)

    def test_non_presente_lascia_coordinate_a_none(self):
        evento = EventoSegnazioneNumero.non_presente(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=99,
            indice_cartella=0,
            totale_cartelle=1,
            numeri_segnati=2,
            totale_numeri=15,
            percentuale=13.33,
        )
        self.assertEqual(evento.esito, "non_presente")
        self.assertIsNone(evento.indice_riga)
        self.assertIsNone(evento.indice_colonna)

    def test_non_presente_preserva_progresso(self):
        evento = EventoSegnazioneNumero.non_presente(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=99,
            indice_cartella=0,
            totale_cartelle=1,
            numeri_segnati=2,
            totale_numeri=15,
            percentuale=13.33,
        )
        self.assertEqual(evento.mancanti, 13)
        self.assertEqual(evento.numero_cartella, 1)

    def test_non_estratto_lascia_coordinate_a_none(self):
        evento = EventoSegnazioneNumero.non_estratto(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=44,
            indice_cartella=1,
            totale_cartelle=2,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.33,
        )
        self.assertEqual(evento.esito, "non_estratto")
        self.assertIsNone(evento.indice_riga)
        self.assertIsNone(evento.indice_colonna)

    def test_non_estratto_preserva_progresso(self):
        evento = EventoSegnazioneNumero.non_estratto(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=44,
            indice_cartella=1,
            totale_cartelle=2,
            numeri_segnati=5,
            totale_numeri=15,
            percentuale=33.33,
        )
        self.assertEqual(evento.numero_cartella, 2)
        self.assertEqual(evento.mancanti, 10)


class TestRisultatoRicercaNumeroInCartella(unittest.TestCase):

    def test_crea_converte_indice_0_in_numero_1(self):
        risultato = RisultatoRicercaNumeroInCartella.crea(
            indice_cartella=0,
            indice_riga=1,
            indice_colonna=3,
            segnato=True,
        )
        self.assertEqual(risultato.numero_cartella, 1)
        self.assertEqual(risultato.indice_cartella, 0)

    def test_crea_indice_2_produce_numero_3(self):
        risultato = RisultatoRicercaNumeroInCartella.crea(
            indice_cartella=2,
            indice_riga=0,
            indice_colonna=5,
            segnato=False,
        )
        self.assertEqual(risultato.numero_cartella, 3)

    def test_crea_preserva_coordinate_e_segnato(self):
        risultato = RisultatoRicercaNumeroInCartella.crea(
            indice_cartella=1,
            indice_riga=2,
            indice_colonna=7,
            segnato=False,
        )
        self.assertEqual(risultato.indice_riga, 2)
        self.assertEqual(risultato.indice_colonna, 7)
        self.assertFalse(risultato.segnato)

    def test_crea_segnato_true(self):
        risultato = RisultatoRicercaNumeroInCartella.crea(
            indice_cartella=0,
            indice_riga=0,
            indice_colonna=0,
            segnato=True,
        )
        self.assertTrue(risultato.segnato)


class TestEventoRicercaNumeroInCartelle(unittest.TestCase):

    def test_non_trovato_esito_e_risultati_vuoti(self):
        evento = EventoRicercaNumeroInCartelle.non_trovato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=55,
            totale_cartelle=3,
        )
        self.assertEqual(evento.esito, "non_trovato")
        self.assertEqual(evento.risultati, ())

    def test_trovato_converte_in_tuple_e_ordina_per_indice_cartella(self):
        r1 = RisultatoRicercaNumeroInCartella.crea(
            indice_cartella=2, indice_riga=0, indice_colonna=5, segnato=False
        )
        r2 = RisultatoRicercaNumeroInCartella.crea(
            indice_cartella=0, indice_riga=1, indice_colonna=3, segnato=True
        )
        evento = EventoRicercaNumeroInCartelle.trovato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=10,
            totale_cartelle=3,
            risultati=[r1, r2],
        )
        self.assertEqual(evento.esito, "trovato")
        self.assertIsInstance(evento.risultati, tuple)
        self.assertEqual(evento.risultati[0].indice_cartella, 0)
        self.assertEqual(evento.risultati[1].indice_cartella, 2)

    def test_trovato_preserva_numero_totale_cartelle_giocatore(self):
        r1 = RisultatoRicercaNumeroInCartella.crea(
            indice_cartella=0, indice_riga=0, indice_colonna=0, segnato=True
        )
        evento = EventoRicercaNumeroInCartelle.trovato(
            id_giocatore=42,
            nome_giocatore="Luigi",
            numero=77,
            totale_cartelle=5,
            risultati=[r1],
        )
        self.assertEqual(evento.numero, 77)
        self.assertEqual(evento.totale_cartelle, 5)
        self.assertEqual(evento.id_giocatore, 42)
        self.assertEqual(evento.nome_giocatore, "Luigi")

    def test_non_trovato_preserva_numero_e_totale_cartelle(self):
        evento = EventoRicercaNumeroInCartelle.non_trovato(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero=88,
            totale_cartelle=4,
        )
        self.assertEqual(evento.numero, 88)
        self.assertEqual(evento.totale_cartelle, 4)


if __name__ == "__main__":
    unittest.main()
