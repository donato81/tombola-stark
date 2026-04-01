from __future__ import annotations

import unittest

from bingo_game.cartella import Cartella
from bingo_game.players.helper_focus import GestioneFocusMixin


class StubFocus(GestioneFocusMixin):
    def __init__(self) -> None:
        self.cartelle: list = []
        self._indice_cartella_focus = None
        self._indice_riga_focus = None
        self._indice_colonna_focus = None


class TestGestioneFocusMixin(unittest.TestCase):

    def setUp(self) -> None:
        self.stub = StubFocus()
        self.cartella = Cartella()

    # --- Gruppo 1: Cartella (metodi 2, 3) ---

    def test_esito_focus_cartella_impostato_rigoroso_senza_focus(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = None
        esito = self.stub._esito_focus_cartella_impostato(auto_imposta=False)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_CARTELLA_NON_IMPOSTATO")

    def test_esito_pronto_per_navigazione_senza_focus_cartella(self) -> None:
        # _esito_pronto_per_navigazione usa auto_imposta=False:
        # il focus cartella deve essere impostato esplicitamente dall'utente.
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = None

        esito = self.stub._esito_pronto_per_navigazione()

        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_CARTELLA_NON_IMPOSTATO")
        self.assertIsNone(self.stub._indice_cartella_focus)

    def test_esito_focus_cartella_in_range_fuori_range_superiore(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 5
        esito = self.stub._esito_focus_cartella_in_range()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_CARTELLA_FUORI_RANGE")

    def test_esito_focus_cartella_in_range_indice_negativo(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = -1
        esito = self.stub._esito_focus_cartella_in_range()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_CARTELLA_FUORI_RANGE")

    # --- Gruppo 2: Riga (metodi 5, 6, 7) ---

    def test_esito_focus_riga_impostata_cartella_assente(self) -> None:
        esito = self.stub._esito_focus_riga_impostata()
        self.assertFalse(esito.ok)

    def test_esito_focus_riga_impostata_riga_assente(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        esito = self.stub._esito_focus_riga_impostata()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_RIGA_NON_IMPOSTATA")

    def test_esito_focus_riga_impostata_ok(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_riga_focus = 1
        esito = self.stub._esito_focus_riga_impostata()
        self.assertTrue(esito.ok)

    def test_esito_focus_riga_in_range_fuori_range_superiore(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_riga_focus = 5
        esito = self.stub._esito_focus_riga_in_range()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_RIGA_FUORI_RANGE")

    def test_esito_focus_riga_in_range_indice_negativo(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_riga_focus = -1
        esito = self.stub._esito_focus_riga_in_range()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_RIGA_FUORI_RANGE")

    def test_esito_focus_riga_in_range_ok(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_riga_focus = 1
        esito = self.stub._esito_focus_riga_in_range()
        self.assertTrue(esito.ok)

    def test_esito_focus_riga_valido_riga_fuori_range(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_riga_focus = 5
        esito = self.stub._esito_focus_riga_valido()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_RIGA_FUORI_RANGE")

    # --- Gruppo 3: Colonna (metodi 8, 9, 10) ---

    def test_esito_focus_colonna_impostata_cartella_assente(self) -> None:
        esito = self.stub._esito_focus_colonna_impostata()
        self.assertFalse(esito.ok)

    def test_esito_focus_colonna_impostata_colonna_assente(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        esito = self.stub._esito_focus_colonna_impostata()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_COLONNA_NON_IMPOSTATA")

    def test_esito_focus_colonna_impostata_ok(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_colonna_focus = 4
        esito = self.stub._esito_focus_colonna_impostata()
        self.assertTrue(esito.ok)

    def test_esito_focus_colonna_in_range_fuori_range_superiore(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_colonna_focus = 10
        esito = self.stub._esito_focus_colonna_in_range()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_COLONNA_FUORI_RANGE")

    def test_esito_focus_colonna_in_range_indice_negativo(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_colonna_focus = -1
        esito = self.stub._esito_focus_colonna_in_range()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_COLONNA_FUORI_RANGE")

    def test_esito_focus_colonna_in_range_ok(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_colonna_focus = 4
        esito = self.stub._esito_focus_colonna_in_range()
        self.assertTrue(esito.ok)

    def test_esito_focus_colonna_valido_colonna_assente(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        esito = self.stub._esito_focus_colonna_valido()
        self.assertFalse(esito.ok)

    def test_esito_focus_colonna_valido_colonna_fuori_range(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_colonna_focus = 10
        esito = self.stub._esito_focus_colonna_valido()
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "FOCUS_COLONNA_FUORI_RANGE")

    def test_esito_focus_colonna_valido_ok(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_colonna_focus = 4
        esito = self.stub._esito_focus_colonna_valido()
        self.assertTrue(esito.ok)

    # --- Gruppo 4: Reset (metodo 15) ---

    def test_reset_focus_cartella_riga_e_colonna_azzera_tutto(self) -> None:
        self.stub._reset_focus_cartella_riga_e_colonna()
        self.assertIsNone(self.stub._indice_cartella_focus)
        self.assertIsNone(self.stub._indice_riga_focus)
        self.assertIsNone(self.stub._indice_colonna_focus)

    def test_reset_focus_cartella_riga_e_colonna_da_stato_impostato(self) -> None:
        self.stub.cartelle = [self.cartella]
        self.stub._indice_cartella_focus = 0
        self.stub._indice_riga_focus = 1
        self.stub._indice_colonna_focus = 4
        self.stub._reset_focus_cartella_riga_e_colonna()
        self.assertIsNone(self.stub._indice_cartella_focus)
        self.assertIsNone(self.stub._indice_riga_focus)
        self.assertIsNone(self.stub._indice_colonna_focus)


if __name__ == "__main__":
    unittest.main()
