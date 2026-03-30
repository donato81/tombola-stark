"""
Test unitari per le eccezioni di dominio del Tabellone.
Modulo: tests.unit.test_tabellone_eccezioni
"""

import unittest

from bingo_game.tabellone import Tabellone
from bingo_game.exceptions.tabellone_exceptions import TabelloneNumeriEsauritiException


class TestGestioneErroreNumeriTerminati(unittest.TestCase):
    """Test per il metodo gestione_errore_numeri_terminati() del Tabellone."""

    def setUp(self) -> None:
        self.tabellone = Tabellone()

    def test_solleva_tabellone_numeri_esauriti_exception(self) -> None:
        """gestione_errore_numeri_terminati() deve sollevare TabelloneNumeriEsauritiException."""
        with self.assertRaises(TabelloneNumeriEsauritiException):
            self.tabellone.gestione_errore_numeri_terminati()

    def test_messaggio_eccezione_corretto(self) -> None:
        """Il messaggio dell'eccezione deve corrispondere al testo atteso."""
        messaggio_atteso = (
            "Tutti i numeri sono stati estratti. "
            "Impossibile estrarre un altro numero."
        )
        with self.assertRaises(TabelloneNumeriEsauritiException) as ctx:
            self.tabellone.gestione_errore_numeri_terminati()
        self.assertEqual(str(ctx.exception), messaggio_atteso)


if __name__ == "__main__":
    unittest.main()
