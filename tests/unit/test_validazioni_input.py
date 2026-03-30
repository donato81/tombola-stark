"""
Test unitari per bingo_game/validations/validazioni_input.py.

Libreria: unittest (standard library).
Nessun pytest, nessun framework esterno.
"""
import unittest

from bingo_game.validations.validazioni_input import (
    esito_numero_intero,
    esito_numero_in_range_1_90,
    esito_numero_riga_in_range_1_3,
    esito_numero_colonna_in_range_1_9,
    esito_reclamo_turno_libero,
    esito_tipo_vittoria_supportato,
)


# ---------------------------------------------------------------------------
# Classe 1 — esito_numero_intero
# ---------------------------------------------------------------------------

class TestEsitoNumeroIntero(unittest.TestCase):

    def test_esito_numero_intero_int_valido_restituisce_ok(self):
        esito = esito_numero_intero(5)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_numero_intero_bool_restituisce_tipo_non_valido(self):
        # bool è sottoclasse di int ma type(True) is not int, quindi viene rifiutato
        esito = esito_numero_intero(True)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_TIPO_NON_VALIDO")

    def test_esito_numero_intero_float_restituisce_tipo_non_valido(self):
        esito = esito_numero_intero(3.14)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_TIPO_NON_VALIDO")

    def test_esito_numero_intero_none_restituisce_tipo_non_valido(self):
        esito = esito_numero_intero(None)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_TIPO_NON_VALIDO")


# ---------------------------------------------------------------------------
# Classe 2 — esito_numero_in_range_1_90
# ---------------------------------------------------------------------------

class TestEsitoNumeroInRange190(unittest.TestCase):

    def test_esito_numero_in_range_1_90_con_1_restituisce_ok(self):
        esito = esito_numero_in_range_1_90(1)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_numero_in_range_1_90_con_90_restituisce_ok(self):
        esito = esito_numero_in_range_1_90(90)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_numero_in_range_1_90_con_0_restituisce_numero_non_valido(self):
        esito = esito_numero_in_range_1_90(0)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_NON_VALIDO")

    def test_esito_numero_in_range_1_90_con_91_restituisce_numero_non_valido(self):
        esito = esito_numero_in_range_1_90(91)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_NON_VALIDO")

    def test_esito_numero_in_range_1_90_con_tipo_errato_restituisce_tipo_non_valido(self):
        esito = esito_numero_in_range_1_90("45")
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_TIPO_NON_VALIDO")


# ---------------------------------------------------------------------------
# Classe 3 — esito_numero_riga_in_range_1_3
# ---------------------------------------------------------------------------

class TestEsitoNumeroRigaInRange13(unittest.TestCase):

    def test_esito_numero_riga_in_range_1_3_con_1_restituisce_ok(self):
        esito = esito_numero_riga_in_range_1_3(1)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_numero_riga_in_range_1_3_con_3_restituisce_ok(self):
        esito = esito_numero_riga_in_range_1_3(3)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_numero_riga_in_range_1_3_con_0_restituisce_numero_riga_fuori_range(self):
        esito = esito_numero_riga_in_range_1_3(0)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_RIGA_FUORI_RANGE")

    def test_esito_numero_riga_in_range_1_3_con_4_restituisce_numero_riga_fuori_range(self):
        esito = esito_numero_riga_in_range_1_3(4)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_RIGA_FUORI_RANGE")

    def test_esito_numero_riga_in_range_1_3_con_tipo_errato_restituisce_tipo_non_valido(self):
        esito = esito_numero_riga_in_range_1_3(2.5)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_TIPO_NON_VALIDO")


# ---------------------------------------------------------------------------
# Classe 4 — esito_numero_colonna_in_range_1_9
# ---------------------------------------------------------------------------

class TestEsitoNumeroColonnaInRange19(unittest.TestCase):

    def test_esito_numero_colonna_in_range_1_9_con_1_restituisce_ok(self):
        esito = esito_numero_colonna_in_range_1_9(1)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_numero_colonna_in_range_1_9_con_9_restituisce_ok(self):
        esito = esito_numero_colonna_in_range_1_9(9)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_numero_colonna_in_range_1_9_con_0_restituisce_numero_colonna_fuori_range(self):
        esito = esito_numero_colonna_in_range_1_9(0)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_COLONNA_FUORI_RANGE")

    def test_esito_numero_colonna_in_range_1_9_con_10_restituisce_numero_colonna_fuori_range(self):
        esito = esito_numero_colonna_in_range_1_9(10)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_COLONNA_FUORI_RANGE")

    def test_esito_numero_colonna_in_range_1_9_con_tipo_errato_restituisce_tipo_non_valido(self):
        esito = esito_numero_colonna_in_range_1_9(None)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "NUMERO_TIPO_NON_VALIDO")


# ---------------------------------------------------------------------------
# Classe 5 — esito_reclamo_turno_libero
# ---------------------------------------------------------------------------

class TestEsitoReclamoTurnoLibero(unittest.TestCase):

    def test_esito_reclamo_turno_libero_con_none_restituisce_ok(self):
        esito = esito_reclamo_turno_libero(None)
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_reclamo_turno_libero_con_oggetto_restituisce_reclamo_gia_presente(self):
        esito = esito_reclamo_turno_libero(object())
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "RECLAMO_GIA_PRESENTE")


# ---------------------------------------------------------------------------
# Classe 6 — esito_tipo_vittoria_supportato
# ---------------------------------------------------------------------------

class TestEsitoTipoVittoriaSupportato(unittest.TestCase):

    def test_esito_tipo_vittoria_supportato_tombola_restituisce_ok(self):
        esito = esito_tipo_vittoria_supportato("tombola")
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_tipo_vittoria_supportato_ambo_restituisce_ok(self):
        esito = esito_tipo_vittoria_supportato("ambo")
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_tipo_vittoria_supportato_terno_restituisce_ok(self):
        esito = esito_tipo_vittoria_supportato("terno")
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_tipo_vittoria_supportato_quaterna_restituisce_ok(self):
        esito = esito_tipo_vittoria_supportato("quaterna")
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_tipo_vittoria_supportato_cinquina_restituisce_ok(self):
        esito = esito_tipo_vittoria_supportato("cinquina")
        self.assertTrue(esito.ok)
        self.assertIsNone(esito.errore)

    def test_esito_tipo_vittoria_supportato_valore_sconosciuto_restituisce_tipo_vittoria_non_valido(self):
        esito = esito_tipo_vittoria_supportato("bingo")
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "TIPO_VITTORIA_NON_VALIDO")

    def test_esito_tipo_vittoria_supportato_maiuscolo_restituisce_tipo_vittoria_non_valido(self):
        esito = esito_tipo_vittoria_supportato("Tombola")
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "TIPO_VITTORIA_NON_VALIDO")

    def test_esito_tipo_vittoria_supportato_none_restituisce_tipo_vittoria_non_valido(self):
        esito = esito_tipo_vittoria_supportato(None)
        self.assertFalse(esito.ok)
        self.assertEqual(esito.errore, "TIPO_VITTORIA_NON_VALIDO")


if __name__ == "__main__":
    unittest.main()
