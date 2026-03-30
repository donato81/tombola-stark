"""
Test unitari per bingo_game/validations/validazione_oggetti.py.

Libreria: unittest (standard library) + unittest.mock.
Nessun pytest, nessun framework esterno.
"""
import unittest
from unittest.mock import MagicMock

from bingo_game.validations.validazione_oggetti import (
    esito_tabellone_disponibile,
    esito_coordinate_numero_coerenti,
)
from bingo_game.tabellone import Tabellone


# ---------------------------------------------------------------------------
# Classe 1 — esito_tabellone_disponibile
# ---------------------------------------------------------------------------

class TestEsitoTabelloneDisponibile(unittest.TestCase):

    def test_esito_tabellone_disponibile_none_restituisce_tabellone_non_disponibile(self):
        esito = esito_tabellone_disponibile(None)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "TABELLONE_NON_DISPONIBILE")

    def test_esito_tabellone_disponibile_tabellone_reale_restituisce_ok(self):
        tabellone = Tabellone()
        esito = esito_tabellone_disponibile(tabellone)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_tabellone_disponibile_stub_con_get_numeri_estratti_restituisce_ok(self):
        # Stub con solo get_numeri_estratti: il duck-typing del codice lo accetta
        stub = MagicMock(spec=["get_numeri_estratti"])
        esito = esito_tabellone_disponibile(stub)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_tabellone_disponibile_stub_con_is_numero_estratto_restituisce_ok(self):
        # Stub con solo is_numero_estratto: il duck-typing del codice lo accetta
        stub = MagicMock(spec=["is_numero_estratto"])
        esito = esito_tabellone_disponibile(stub)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_tabellone_disponibile_oggetto_incompatibile_restituisce_tabellone_non_disponibile(self):
        # Oggetto senza nessuno dei metodi attesi
        esito = esito_tabellone_disponibile(object())
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "TABELLONE_NON_DISPONIBILE")


# ---------------------------------------------------------------------------
# Classe 2 — esito_coordinate_numero_coerenti
# ---------------------------------------------------------------------------

class TestEsitoCoordinateNumeroCoerenti(unittest.TestCase):

    def test_esito_coordinate_numero_coerenti_coordinate_presenti_restituisce_ok(self):
        # Cartella stub che restituisce coordinate valide
        cartella = MagicMock()
        cartella.get_coordinate_numero.return_value = (1, 3)
        esito = esito_coordinate_numero_coerenti(cartella, 42)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)
        cartella.get_coordinate_numero.assert_called_once_with(42)

    def test_esito_coordinate_numero_coerenti_coordinate_none_restituisce_cartella_stato_incoerente(self):
        # Cartella stub che restituisce None: dati interni incoerenti
        cartella = MagicMock()
        cartella.get_coordinate_numero.return_value = None
        esito = esito_coordinate_numero_coerenti(cartella, 42)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "CARTELLA_STATO_INCOERENTE")

    def test_esito_coordinate_numero_coerenti_numero_non_int_restituisce_inputnonvalido(self):
        # Numero non int: il codice usa "INPUT_NON_VALIDO" (comportamento reale)
        cartella = MagicMock()
        esito = esito_coordinate_numero_coerenti(cartella, "42")
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "INPUT_NON_VALIDO")
        # Il metodo cartella non deve essere chiamato: la funzione esce prima
        cartella.get_coordinate_numero.assert_not_called()

    def test_esito_coordinate_numero_coerenti_eccezione_del_metodo_cartella_viene_propagata(self):
        # Se get_coordinate_numero solleva ValueError, la funzione lo propaga
        cartella = MagicMock()
        cartella.get_coordinate_numero.side_effect = ValueError("numero non in cartella")
        with self.assertRaises(ValueError):
            esito_coordinate_numero_coerenti(cartella, 42)


if __name__ == "__main__":
    unittest.main()
