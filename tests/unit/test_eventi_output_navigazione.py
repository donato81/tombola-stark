"""
Test unitari per le classi E2 di eventi_output_ui_umani.py:
- EventoNavigazioneRiga
- EventoNavigazioneRigaAvanzata
- EventoNavigazioneColonna
- EventoNavigazioneColonnaAvanzata
- EventoVaiARigaAvanzata
- EventoVaiAColonnaAvanzata

Perimetro: solo E2. Zero mock, zero import pytest.
"""

import unittest
from bingo_game.events.eventi_output_ui_umani import (
    EventoNavigazioneRiga,
    EventoNavigazioneRigaAvanzata,
    EventoNavigazioneColonna,
    EventoNavigazioneColonnaAvanzata,
    EventoVaiARigaAvanzata,
    EventoVaiAColonnaAvanzata,
)

_RIGA_SEMPLICE = (1, "-", 21, "-", 41, "-", 61, "-", 81)
_STATO_RIGA = {
    "segnati": 1,
    "mancanti": 4,
    "percentuale": 20.0,
    "numeri_segnati": (1,),
}
_NUMERI_SEGNATI_RIGA = (1,)
_DATI_RIGA_AVANZATI = (_RIGA_SEMPLICE, _STATO_RIGA, _NUMERI_SEGNATI_RIGA)

_COLONNA_SEMPLICE = (21, "-", 63)
_STATO_COLONNA = {
    "segnati": 1,
    "mancanti": 1,
    "percentuale": 50.0,
    "numeri_segnati": (21,),
}
_NUMERI_SEGNATI_COLONNA = (21,)
_DATI_COLONNA_AVANZATI = (_COLONNA_SEMPLICE, _STATO_COLONNA, _NUMERI_SEGNATI_COLONNA)


class TestEventoNavigazioneRiga(unittest.TestCase):

    def test_mostra_riga_converte_indice_0_in_numero_1(self):
        evento = EventoNavigazioneRiga.mostra_riga(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="successiva",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
            indice_riga_corrente=0,
            riga_semplice=_RIGA_SEMPLICE,
        )
        self.assertEqual(evento.numero_riga_corrente, 1)

    def test_mostra_riga_indice_2_produce_numero_3(self):
        evento = EventoNavigazioneRiga.mostra_riga(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="successiva",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
            indice_riga_corrente=2,
            riga_semplice=_RIGA_SEMPLICE,
        )
        self.assertEqual(evento.numero_riga_corrente, 3)

    def test_mostra_riga_esito_mostra_con_riga_e_limite_none(self):
        evento = EventoNavigazioneRiga.mostra_riga(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="successiva",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
            indice_riga_corrente=0,
            riga_semplice=_RIGA_SEMPLICE,
        )
        self.assertEqual(evento.esito, "mostra")
        self.assertEqual(evento.riga_semplice, _RIGA_SEMPLICE)
        self.assertIsNone(evento.limite)

    def test_limite_minimo_numero_1_riga_none(self):
        evento = EventoNavigazioneRiga.limite_minimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="precedente",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
        )
        self.assertEqual(evento.esito, "limite")
        self.assertEqual(evento.numero_riga_corrente, 1)
        self.assertEqual(evento.limite, "minimo")
        self.assertIsNone(evento.riga_semplice)

    def test_limite_massimo_numero_uguale_totale_righe(self):
        evento = EventoNavigazioneRiga.limite_massimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="successiva",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
        )
        self.assertEqual(evento.esito, "limite")
        self.assertEqual(evento.numero_riga_corrente, 3)
        self.assertEqual(evento.limite, "massimo")
        self.assertIsNone(evento.riga_semplice)


class TestEventoNavigazioneRigaAvanzata(unittest.TestCase):

    def test_mostra_riga_scompone_dati_avanzati(self):
        evento = EventoNavigazioneRigaAvanzata.mostra_riga(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="successiva",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
            indice_riga_corrente=0,
            dati_riga_avanzati=_DATI_RIGA_AVANZATI,
        )
        self.assertEqual(evento.riga_semplice, _RIGA_SEMPLICE)
        self.assertEqual(evento.stato_riga, _STATO_RIGA)
        self.assertEqual(evento.numeri_segnati_riga_ordinati, _NUMERI_SEGNATI_RIGA)

    def test_mostra_riga_converte_indice_1_in_numero_2(self):
        evento = EventoNavigazioneRigaAvanzata.mostra_riga(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="successiva",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
            indice_riga_corrente=1,
            dati_riga_avanzati=_DATI_RIGA_AVANZATI,
        )
        self.assertEqual(evento.numero_riga_corrente, 2)

    def test_limite_minimo_azzera_rami_avanzati(self):
        evento = EventoNavigazioneRigaAvanzata.limite_minimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="precedente",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
        )
        self.assertEqual(evento.esito, "limite")
        self.assertEqual(evento.numero_riga_corrente, 1)
        self.assertEqual(evento.limite, "minimo")
        self.assertIsNone(evento.riga_semplice)
        self.assertIsNone(evento.stato_riga)
        self.assertIsNone(evento.numeri_segnati_riga_ordinati)

    def test_limite_massimo_azzera_rami_avanzati(self):
        evento = EventoNavigazioneRigaAvanzata.limite_massimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="successiva",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_righe=3,
        )
        self.assertEqual(evento.esito, "limite")
        self.assertEqual(evento.numero_riga_corrente, 3)
        self.assertEqual(evento.limite, "massimo")
        self.assertIsNone(evento.riga_semplice)
        self.assertIsNone(evento.stato_riga)
        self.assertIsNone(evento.numeri_segnati_riga_ordinati)


class TestEventoNavigazioneColonna(unittest.TestCase):

    def test_mostra_colonna_converte_indice_0_in_numero_1(self):
        evento = EventoNavigazioneColonna.mostra_colonna(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="destra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
            indice_colonna_corrente=0,
            colonna_semplice=_COLONNA_SEMPLICE,
        )
        self.assertEqual(evento.numero_colonna_corrente, 1)

    def test_mostra_colonna_indice_8_produce_numero_9(self):
        evento = EventoNavigazioneColonna.mostra_colonna(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="destra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
            indice_colonna_corrente=8,
            colonna_semplice=_COLONNA_SEMPLICE,
        )
        self.assertEqual(evento.numero_colonna_corrente, 9)

    def test_mostra_colonna_esito_mostra_con_colonna_e_limite_none(self):
        evento = EventoNavigazioneColonna.mostra_colonna(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="destra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
            indice_colonna_corrente=0,
            colonna_semplice=_COLONNA_SEMPLICE,
        )
        self.assertEqual(evento.esito, "mostra")
        self.assertEqual(evento.colonna_semplice, _COLONNA_SEMPLICE)
        self.assertIsNone(evento.limite)

    def test_limite_minimo_numero_1_colonna_none(self):
        evento = EventoNavigazioneColonna.limite_minimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="sinistra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
        )
        self.assertEqual(evento.esito, "limite")
        self.assertEqual(evento.numero_colonna_corrente, 1)
        self.assertEqual(evento.limite, "minimo")
        self.assertIsNone(evento.colonna_semplice)

    def test_limite_massimo_numero_uguale_totale_colonne(self):
        evento = EventoNavigazioneColonna.limite_massimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="destra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
        )
        self.assertEqual(evento.esito, "limite")
        self.assertEqual(evento.numero_colonna_corrente, 9)
        self.assertEqual(evento.limite, "massimo")
        self.assertIsNone(evento.colonna_semplice)


class TestEventoNavigazioneColonnaAvanzata(unittest.TestCase):

    def test_mostra_colonna_scompone_dati_avanzati(self):
        evento = EventoNavigazioneColonnaAvanzata.mostra_colonna(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="destra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
            indice_colonna_corrente=2,
            dati_colonna_avanzati=_DATI_COLONNA_AVANZATI,
        )
        self.assertEqual(evento.colonna_semplice, _COLONNA_SEMPLICE)
        self.assertEqual(evento.stato_colonna, _STATO_COLONNA)
        self.assertEqual(evento.numeri_segnati_colonna_ordinati, _NUMERI_SEGNATI_COLONNA)

    def test_mostra_colonna_converte_indice_2_in_numero_3(self):
        evento = EventoNavigazioneColonnaAvanzata.mostra_colonna(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="destra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
            indice_colonna_corrente=2,
            dati_colonna_avanzati=_DATI_COLONNA_AVANZATI,
        )
        self.assertEqual(evento.numero_colonna_corrente, 3)

    def test_limite_minimo_azzera_rami_avanzati(self):
        evento = EventoNavigazioneColonnaAvanzata.limite_minimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="sinistra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
        )
        self.assertEqual(evento.esito, "limite")
        self.assertEqual(evento.numero_colonna_corrente, 1)
        self.assertEqual(evento.limite, "minimo")
        self.assertIsNone(evento.colonna_semplice)
        self.assertIsNone(evento.stato_colonna)
        self.assertIsNone(evento.numeri_segnati_colonna_ordinati)

    def test_limite_massimo_azzera_rami_avanzati(self):
        evento = EventoNavigazioneColonnaAvanzata.limite_massimo(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="destra",
            totale_cartelle=3,
            numero_cartella_corrente=1,
            totale_colonne=9,
        )
        self.assertEqual(evento.esito, "limite")
        self.assertEqual(evento.numero_colonna_corrente, 9)
        self.assertEqual(evento.limite, "massimo")
        self.assertIsNone(evento.colonna_semplice)
        self.assertIsNone(evento.stato_colonna)
        self.assertIsNone(evento.numeri_segnati_colonna_ordinati)


class TestEventoVaiARigaAvanzata(unittest.TestCase):

    def test_preserva_numero_riga_umano(self):
        evento = EventoVaiARigaAvanzata.crea_da_dati_riga_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_riga=2,
            dati_riga_avanzati=_DATI_RIGA_AVANZATI,
        )
        self.assertEqual(evento.numero_riga, 2)

    def test_forza_riga_semplice_a_tuple(self):
        evento = EventoVaiARigaAvanzata.crea_da_dati_riga_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_riga=1,
            dati_riga_avanzati=_DATI_RIGA_AVANZATI,
        )
        self.assertIsInstance(evento.riga_semplice, tuple)
        self.assertEqual(evento.riga_semplice, _RIGA_SEMPLICE)

    def test_forza_numeri_segnati_a_tuple(self):
        evento = EventoVaiARigaAvanzata.crea_da_dati_riga_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_riga=1,
            dati_riga_avanzati=_DATI_RIGA_AVANZATI,
        )
        self.assertIsInstance(evento.numeri_segnati_riga_ordinati, tuple)
        self.assertEqual(evento.numeri_segnati_riga_ordinati, _NUMERI_SEGNATI_RIGA)

    def test_preserva_stato_riga_senza_trasformazioni(self):
        evento = EventoVaiARigaAvanzata.crea_da_dati_riga_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_riga=1,
            dati_riga_avanzati=_DATI_RIGA_AVANZATI,
        )
        self.assertEqual(evento.stato_riga, _STATO_RIGA)


class TestEventoVaiAColonnaAvanzata(unittest.TestCase):

    def test_preserva_numero_colonna_umano(self):
        evento = EventoVaiAColonnaAvanzata.crea_da_dati_colonna_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_colonna=3,
            dati_colonna_avanzati=_DATI_COLONNA_AVANZATI,
        )
        self.assertEqual(evento.numero_colonna, 3)

    def test_forza_colonna_semplice_a_tuple(self):
        evento = EventoVaiAColonnaAvanzata.crea_da_dati_colonna_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_colonna=3,
            dati_colonna_avanzati=_DATI_COLONNA_AVANZATI,
        )
        self.assertIsInstance(evento.colonna_semplice, tuple)
        self.assertEqual(evento.colonna_semplice, _COLONNA_SEMPLICE)

    def test_forza_numeri_segnati_a_tuple(self):
        evento = EventoVaiAColonnaAvanzata.crea_da_dati_colonna_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_colonna=3,
            dati_colonna_avanzati=_DATI_COLONNA_AVANZATI,
        )
        self.assertIsInstance(evento.numeri_segnati_colonna_ordinati, tuple)
        self.assertEqual(evento.numeri_segnati_colonna_ordinati, _NUMERI_SEGNATI_COLONNA)

    def test_preserva_stato_colonna_senza_trasformazioni(self):
        evento = EventoVaiAColonnaAvanzata.crea_da_dati_colonna_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_colonna=3,
            dati_colonna_avanzati=_DATI_COLONNA_AVANZATI,
        )
        self.assertEqual(evento.stato_colonna, _STATO_COLONNA)


if __name__ == "__main__":
    unittest.main()
