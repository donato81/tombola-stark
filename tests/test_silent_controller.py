"""
tests/test_silent_controller.py

Test di non-regressione stdout per game_controller.py.
Verifica che nessuna funzione pubblica del controller emetta su stdout.

Criterio di done: capsys.readouterr().out == "" in tutti i percorsi.
"""
import io
import unittest

from unittest.mock import MagicMock, patch

from bingo_game import game_controller as ctrl
from bingo_game.partita import Partita
from bingo_game.exceptions.partita_exceptions import PartitaException



# ---------------------------------------------------------------------------
# Test stdout — tutti i percorsi
# ---------------------------------------------------------------------------

class TestControllerSilenzioso(unittest.TestCase):
    """Verifica che il controller non emetta nulla su stdout in nessuna condizione."""

    def _build_partita_in_corso(self) -> MagicMock:
        """Factory: mock Partita in stato in_corso."""
        p = MagicMock(spec=Partita)
        p.get_stato_partita.return_value = "in_corso"
        p.get_numero_giocatori.return_value = 2
        p.avvia_partita.return_value = None
        p.is_terminata.return_value = False
        p.tabellone = MagicMock()
        p.esegui_turno.return_value = {
            "numero_estratto": 42,
            "stato_partita_prima": "in_corso",
            "stato_partita_dopo": "in_corso",
            "tombola_rilevata": False,
            "partita_terminata": False,
            "premi_nuovi": [],
        }
        p.get_stato_completo.return_value = {
            "stato_partita": "in_corso",
            "ultimo_numero_estratto": None,
            "numeri_estratti": [],
            "giocatori": [],
            "premi_gia_assegnati": [],
        }
        p.get_stato_sintetico.return_value = {
            "stato_partita": "in_corso",
            "ultimo_numero_estratto": None,
            "numeri_estratti": [],
            "giocatori": [],
            "premi_gia_assegnati": [],
        }
        return p

    def _build_partita_terminata(self) -> MagicMock:
        """Factory: mock Partita in stato terminata."""
        p = MagicMock(spec=Partita)
        p.get_stato_partita.return_value = "terminata"
        p.is_terminata.return_value = True
        return p

    def setUp(self) -> None:
        self.partita_mock = self._build_partita_in_corso()
        self.partita_terminata_mock = self._build_partita_terminata()

    def test_crea_partita_standard_silenzioso(self):
        """crea_partita_standard non deve emettere su stdout."""
        mock_partita = MagicMock(spec=Partita)
        mock_partita.tabellone = MagicMock()
        mock_partita.get_giocatori.return_value = [MagicMock(), MagicMock()]
        fake_out = io.StringIO()
        with patch('sys.stdout', new=fake_out):
            with (
                patch.object(ctrl, "crea_tabellone_standard", return_value=MagicMock()),
                patch.object(ctrl, "crea_giocatore_umano", return_value=MagicMock()),
                patch.object(ctrl, "crea_giocatori_automatici", return_value=[MagicMock()]),
                patch("bingo_game.game_controller.Partita", return_value=mock_partita),
            ):
                ctrl.crea_partita_standard(
                    nome_giocatore_umano="Test",
                    num_bot=1,
                    num_cartelle_umano=1,
                )
        self.assertEqual(fake_out.getvalue(), "")

    def test_avvia_partita_sicura_true_silenzioso(self):
        """avvia_partita_sicura percorso True non deve emettere su stdout."""
        fake_out = io.StringIO()
        with patch('sys.stdout', new=fake_out):
            ctrl.avvia_partita_sicura(self.partita_mock)
        self.assertEqual(fake_out.getvalue(), "")

    def test_avvia_partita_sicura_false_silenzioso(self):
        """avvia_partita_sicura percorso False non deve emettere su stdout."""
        p = self._build_partita_in_corso()
        p.avvia_partita.side_effect = PartitaException("errore simulato")
        fake_out = io.StringIO()
        with patch('sys.stdout', new=fake_out):
            ctrl.avvia_partita_sicura(p)
        self.assertEqual(fake_out.getvalue(), "")

    def test_esegui_turno_sicuro_dict_silenzioso(self):
        """esegui_turno_sicuro percorso dict non deve emettere su stdout."""
        fake_out = io.StringIO()
        with patch('sys.stdout', new=fake_out):
            ctrl.esegui_turno_sicuro(self.partita_mock)
        self.assertEqual(fake_out.getvalue(), "")

    def test_esegui_turno_sicuro_none_silenzioso(self):
        """esegui_turno_sicuro percorso None non deve emettere su stdout."""
        p = self._build_partita_in_corso()
        p.get_stato_partita.return_value = "non_iniziata"
        fake_out = io.StringIO()
        with patch('sys.stdout', new=fake_out):
            ctrl.esegui_turno_sicuro(p)
        self.assertEqual(fake_out.getvalue(), "")

    def test_partita_terminata_false_silenzioso(self):
        """partita_terminata percorso False non deve emettere su stdout."""
        fake_out = io.StringIO()
        with patch('sys.stdout', new=fake_out):
            ctrl.partita_terminata(self.partita_mock)
        self.assertEqual(fake_out.getvalue(), "")

    def test_partita_terminata_true_silenzioso(self):
        """partita_terminata percorso True non deve emettere su stdout."""
        fake_out = io.StringIO()
        with patch('sys.stdout', new=fake_out):
            ctrl.partita_terminata(self.partita_terminata_mock)
        self.assertEqual(fake_out.getvalue(), "")

    def test_ottieni_stato_sintetico_dict_silenzioso(self):
        """ottieni_stato_sintetico percorso dict non deve emettere su stdout."""
        fake_out = io.StringIO()
        with patch('sys.stdout', new=fake_out):
            ctrl.ottieni_stato_sintetico(self.partita_mock)
        self.assertEqual(fake_out.getvalue(), "")


# ---------------------------------------------------------------------------
# Test contratti di ritorno
# ---------------------------------------------------------------------------

class TestContrattiRitorno(unittest.TestCase):
    """Verifica che i contratti di ritorno del controller siano rispettati."""

    def _build_partita_in_corso(self) -> MagicMock:
        """Factory: mock Partita in stato in_corso."""
        p = MagicMock(spec=Partita)
        p.get_stato_partita.return_value = "in_corso"
        p.get_numero_giocatori.return_value = 2
        p.avvia_partita.return_value = None
        p.is_terminata.return_value = False
        p.tabellone = MagicMock()
        p.esegui_turno.return_value = {
            "numero_estratto": 42,
            "stato_partita_prima": "in_corso",
            "stato_partita_dopo": "in_corso",
            "tombola_rilevata": False,
            "partita_terminata": False,
            "premi_nuovi": [],
        }
        p.get_stato_completo.return_value = {
            "stato_partita": "in_corso",
            "ultimo_numero_estratto": None,
            "numeri_estratti": [],
            "giocatori": [],
            "premi_gia_assegnati": [],
        }
        p.get_stato_sintetico.return_value = {
            "stato_partita": "in_corso",
            "ultimo_numero_estratto": None,
            "numeri_estratti": [],
            "giocatori": [],
            "premi_gia_assegnati": [],
        }
        return p

    def _build_partita_terminata(self) -> MagicMock:
        """Factory: mock Partita in stato terminata."""
        p = MagicMock(spec=Partita)
        p.get_stato_partita.return_value = "terminata"
        p.is_terminata.return_value = True
        return p

    def setUp(self) -> None:
        self.partita_mock = self._build_partita_in_corso()
        self.partita_terminata_mock = self._build_partita_terminata()

    def test_avvia_partita_sicura_ritorna_true(self) -> None:
        self.assertTrue(ctrl.avvia_partita_sicura(self.partita_mock))

    def test_avvia_partita_sicura_ritorna_false_su_eccezione(self) -> None:
        p = self._build_partita_in_corso()
        p.avvia_partita.side_effect = PartitaException("errore")
        self.assertFalse(ctrl.avvia_partita_sicura(p))

    def test_ottieni_stato_sintetico_lancia_valueerror_su_non_partita(self) -> None:
        with self.assertRaises(ValueError):
            ctrl.ottieni_stato_sintetico("non_una_partita")

    def test_esegui_turno_sicuro_ritorna_none_su_partita_non_in_corso(self) -> None:
        p = self._build_partita_in_corso()
        p.get_stato_partita.return_value = "non_iniziata"
        self.assertIsNone(ctrl.esegui_turno_sicuro(p))


# ---------------------------------------------------------------------------
# Test dizionario localizzazione
# ---------------------------------------------------------------------------

class TestMESSAGGICONTROLLER(unittest.TestCase):
    """Verifica la struttura di MESSAGGI_CONTROLLER in it.py."""

    def test_quattro_chiavi(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        self.assertEqual(len(MESSAGGI_CONTROLLER), 4)

    def test_chiavi_sono_costanti_corrette(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        from bingo_game.events.codici_controller import (
            CTRL_AVVIO_FALLITO_GENERICO,
            CTRL_TURNO_NON_IN_CORSO,
            CTRL_NUMERI_ESAURITI,
            CTRL_TURNO_FALLITO_GENERICO,
        )
        self.assertIn(CTRL_AVVIO_FALLITO_GENERICO, MESSAGGI_CONTROLLER)
        self.assertIn(CTRL_TURNO_NON_IN_CORSO, MESSAGGI_CONTROLLER)
        self.assertIn(CTRL_NUMERI_ESAURITI, MESSAGGI_CONTROLLER)
        self.assertIn(CTRL_TURNO_FALLITO_GENERICO, MESSAGGI_CONTROLLER)

    def test_valori_sono_stringhe_non_vuote(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        for chiave, valore in MESSAGGI_CONTROLLER.items():
            with self.subTest(chiave=chiave):
                self.assertIsInstance(valore, str, f"Valore non stringa per chiave: {chiave}")
                self.assertGreater(len(valore), 0, f"Valore vuoto per chiave: {chiave}")
