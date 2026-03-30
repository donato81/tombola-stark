"""
Test unitari per le classi E5 di eventi_output_ui_umani.py:
- EventoVisualizzaTutteCartelleSemplice
- EventoVisualizzaTutteCartelleAvanzata
- EventoStatoFocusCorrente

Perimetro: solo E5.
MagicMock usato ESCLUSIVAMENTE nei factory bulk crea_da_cartelle().
EventoStatoFocusCorrente testato senza mock.
Zero import pytest.
"""

import unittest
from unittest.mock import MagicMock
from bingo_game.events.eventi_output_ui_umani import (
    EventoVisualizzaTutteCartelleSemplice,
    EventoVisualizzaTutteCartelleAvanzata,
    EventoStatoFocusCorrente,
)

_GRIGLIA = (
    (1, "-", 21, "-", 41, "-", 61, "-", 81),
    ("-", 12, "-", 32, "-", 52, "-", 72, "-"),
    (3, "-", 23, "-", 43, "-", 63, "-", 83),
)
_STATO = {
    "segnati": 2,
    "mancanti": 13,
    "percentuale": 13.33,
    "numeri_segnati": (1, 12),
}
_SEGNATI_ORDINATI = (1, 12)


class TestEventoVisualizzaTutteCartelleSemplice(unittest.TestCase):

    def _make_mock(self, griglia=_GRIGLIA):
        mock = MagicMock()
        mock.get_griglia_semplice.return_value = griglia
        return mock

    def test_crea_da_cartelle_calcola_totale_cartelle(self):
        mocks = [self._make_mock(), self._make_mock()]
        evento = EventoVisualizzaTutteCartelleSemplice.crea_da_cartelle(cartelle=mocks)
        self.assertEqual(evento.totale_cartelle, 2)

    def test_crea_da_cartelle_numerazione_1based(self):
        mocks = [self._make_mock(), self._make_mock(), self._make_mock()]
        evento = EventoVisualizzaTutteCartelleSemplice.crea_da_cartelle(cartelle=mocks)
        numeri = [elem[0] for elem in evento.cartelle]
        self.assertEqual(numeri, [1, 2, 3])

    def test_crea_da_cartelle_richiama_get_griglia_semplice_per_ogni_cartella(self):
        mock1 = self._make_mock()
        mock2 = self._make_mock()
        EventoVisualizzaTutteCartelleSemplice.crea_da_cartelle(cartelle=[mock1, mock2])
        mock1.get_griglia_semplice.assert_called_once()
        mock2.get_griglia_semplice.assert_called_once()

    def test_crea_da_cartelle_restituisce_tuple_immutabile(self):
        mocks = [self._make_mock()]
        evento = EventoVisualizzaTutteCartelleSemplice.crea_da_cartelle(cartelle=mocks)
        self.assertIsInstance(evento.cartelle, tuple)

    def test_crea_da_cartelle_griglia_preservata(self):
        mocks = [self._make_mock()]
        evento = EventoVisualizzaTutteCartelleSemplice.crea_da_cartelle(cartelle=mocks)
        _, griglia = evento.cartelle[0]
        self.assertEqual(griglia, _GRIGLIA)

    def test_crea_da_cartelle_lista_singola(self):
        mocks = [self._make_mock()]
        evento = EventoVisualizzaTutteCartelleSemplice.crea_da_cartelle(cartelle=mocks)
        self.assertEqual(evento.totale_cartelle, 1)
        self.assertEqual(evento.cartelle[0][0], 1)


class TestEventoVisualizzaTutteCartelleAvanzata(unittest.TestCase):

    def _make_mock(self, griglia=_GRIGLIA, stato=_STATO, segnati=_SEGNATI_ORDINATI):
        mock = MagicMock()
        mock.get_dati_visualizzazione_avanzata.return_value = (griglia, stato, segnati)
        return mock

    def test_crea_da_cartelle_calcola_totale_cartelle(self):
        mocks = [self._make_mock(), self._make_mock()]
        evento = EventoVisualizzaTutteCartelleAvanzata.crea_da_cartelle(cartelle=mocks)
        self.assertEqual(evento.totale_cartelle, 2)

    def test_crea_da_cartelle_numerazione_1based(self):
        mocks = [self._make_mock(), self._make_mock()]
        evento = EventoVisualizzaTutteCartelleAvanzata.crea_da_cartelle(cartelle=mocks)
        numeri = [elem[0] for elem in evento.cartelle]
        self.assertEqual(numeri, [1, 2])

    def test_crea_da_cartelle_richiama_get_dati_visualizzazione_avanzata(self):
        mock1 = self._make_mock()
        EventoVisualizzaTutteCartelleAvanzata.crea_da_cartelle(cartelle=[mock1])
        mock1.get_dati_visualizzazione_avanzata.assert_called_once()

    def test_crea_da_cartelle_scompone_pacchetto_avanzato(self):
        mock1 = self._make_mock()
        evento = EventoVisualizzaTutteCartelleAvanzata.crea_da_cartelle(cartelle=[mock1])
        pacchetto = evento.cartelle[0]
        self.assertEqual(pacchetto[0], 1)
        self.assertEqual(pacchetto[1], _GRIGLIA)
        self.assertEqual(pacchetto[2], _STATO)
        self.assertEqual(pacchetto[3], _SEGNATI_ORDINATI)

    def test_crea_da_cartelle_restituisce_tuple_di_tuple(self):
        mocks = [self._make_mock(), self._make_mock()]
        evento = EventoVisualizzaTutteCartelleAvanzata.crea_da_cartelle(cartelle=mocks)
        self.assertIsInstance(evento.cartelle, tuple)
        for elem in evento.cartelle:
            self.assertIsInstance(elem, tuple)

    def test_crea_da_cartelle_ordine_naturale(self):
        mocks = [self._make_mock(), self._make_mock(), self._make_mock()]
        evento = EventoVisualizzaTutteCartelleAvanzata.crea_da_cartelle(cartelle=mocks)
        numeri = [elem[0] for elem in evento.cartelle]
        self.assertEqual(numeri, [1, 2, 3])


class TestEventoStatoFocusCorrente(unittest.TestCase):

    def test_tutti_indici_none_restituisce_tutti_none(self):
        evento = EventoStatoFocusCorrente.crea_da_indici(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_cartelle=3,
            indice_cartella=None,
            indice_riga=None,
            indice_colonna=None,
        )
        self.assertIsNone(evento.numero_cartella)
        self.assertIsNone(evento.numero_riga)
        self.assertIsNone(evento.numero_colonna)

    def test_solo_indice_cartella_converte_e_altri_restano_none(self):
        evento = EventoStatoFocusCorrente.crea_da_indici(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_cartelle=3,
            indice_cartella=0,
            indice_riga=None,
            indice_colonna=None,
        )
        self.assertEqual(evento.numero_cartella, 1)
        self.assertIsNone(evento.numero_riga)
        self.assertIsNone(evento.numero_colonna)

    def test_tutti_indici_valorizzati_conversione_1based(self):
        evento = EventoStatoFocusCorrente.crea_da_indici(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_cartelle=3,
            indice_cartella=2,
            indice_riga=1,
            indice_colonna=5,
        )
        self.assertEqual(evento.numero_cartella, 3)
        self.assertEqual(evento.numero_riga, 2)
        self.assertEqual(evento.numero_colonna, 6)

    def test_indice_0_produce_numero_1_per_ogni_focus(self):
        evento = EventoStatoFocusCorrente.crea_da_indici(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_cartelle=6,
            indice_cartella=0,
            indice_riga=0,
            indice_colonna=0,
        )
        self.assertEqual(evento.numero_cartella, 1)
        self.assertEqual(evento.numero_riga, 1)
        self.assertEqual(evento.numero_colonna, 1)

    def test_preserva_totale_cartelle(self):
        evento = EventoStatoFocusCorrente.crea_da_indici(
            id_giocatore=1,
            nome_giocatore="Mario",
            totale_cartelle=6,
            indice_cartella=None,
            indice_riga=None,
            indice_colonna=None,
        )
        self.assertEqual(evento.totale_cartelle, 6)


if __name__ == "__main__":
    unittest.main()
