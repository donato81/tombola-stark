"""
tests/test_silent_controller.py

Test di non-regressione stdout per game_controller.py.
Verifica che nessuna funzione pubblica del controller emetta su stdout.

Criterio di done: capsys.readouterr().out == "" in tutti i percorsi.
"""
import pytest
from unittest.mock import MagicMock, patch

from bingo_game import game_controller as ctrl
from bingo_game.partita import Partita
from bingo_game.exceptions.partita_exceptions import PartitaException


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def partita_mock():
    """Mock minimale di un oggetto Partita in stato 'in_corso'."""
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
    return p


@pytest.fixture
def partita_terminata_mock():
    """Mock di Partita in stato 'terminata'."""
    p = MagicMock(spec=Partita)
    p.get_stato_partita.return_value = "terminata"
    p.is_terminata.return_value = True
    return p


# ---------------------------------------------------------------------------
# Test stdout — tutti i percorsi
# ---------------------------------------------------------------------------

class TestControllerSilenzioso:
    """Verifica che il controller non emetta nulla su stdout in nessuna condizione."""

    def test_crea_partita_standard_silenzioso(self, capsys):
        """crea_partita_standard non deve emettere su stdout."""
        mock_partita = MagicMock(spec=Partita)
        mock_partita.tabellone = MagicMock()
        mock_partita.get_giocatori.return_value = [MagicMock(), MagicMock()]
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
        assert capsys.readouterr().out == ""

    def test_avvia_partita_sicura_true_silenzioso(self, capsys, partita_mock):
        """avvia_partita_sicura percorso True non deve emettere su stdout."""
        ctrl.avvia_partita_sicura(partita_mock)
        assert capsys.readouterr().out == ""

    def test_avvia_partita_sicura_false_silenzioso(self, capsys, partita_mock):
        """avvia_partita_sicura percorso False non deve emettere su stdout."""
        partita_mock.avvia_partita.side_effect = PartitaException("errore simulato")
        ctrl.avvia_partita_sicura(partita_mock)
        assert capsys.readouterr().out == ""

    def test_esegui_turno_sicuro_dict_silenzioso(self, capsys, partita_mock):
        """esegui_turno_sicuro percorso dict non deve emettere su stdout."""
        ctrl.esegui_turno_sicuro(partita_mock)
        assert capsys.readouterr().out == ""

    def test_esegui_turno_sicuro_none_silenzioso(self, capsys, partita_mock):
        """esegui_turno_sicuro percorso None non deve emettere su stdout."""
        partita_mock.get_stato_partita.return_value = "non_iniziata"
        ctrl.esegui_turno_sicuro(partita_mock)
        assert capsys.readouterr().out == ""

    def test_partita_terminata_false_silenzioso(self, capsys, partita_mock):
        """partita_terminata percorso False non deve emettere su stdout."""
        ctrl.partita_terminata(partita_mock)
        assert capsys.readouterr().out == ""

    def test_partita_terminata_true_silenzioso(self, capsys, partita_terminata_mock):
        """partita_terminata percorso True non deve emettere su stdout."""
        ctrl.partita_terminata(partita_terminata_mock)
        assert capsys.readouterr().out == ""

    def test_ottieni_stato_sintetico_dict_silenzioso(self, capsys, partita_mock):
        """ottieni_stato_sintetico percorso dict non deve emettere su stdout."""
        ctrl.ottieni_stato_sintetico(partita_mock)
        assert capsys.readouterr().out == ""


# ---------------------------------------------------------------------------
# Test contratti di ritorno
# ---------------------------------------------------------------------------

class TestContrattiRitorno:
    """Verifica che i contratti di ritorno del controller siano rispettati."""

    def test_avvia_partita_sicura_ritorna_true(self, partita_mock):
        assert ctrl.avvia_partita_sicura(partita_mock) is True

    def test_avvia_partita_sicura_ritorna_false_su_eccezione(self, partita_mock):
        partita_mock.avvia_partita.side_effect = PartitaException("errore")
        assert ctrl.avvia_partita_sicura(partita_mock) is False

    def test_ottieni_stato_sintetico_lancia_valueerror_su_non_partita(self):
        with pytest.raises(ValueError):
            ctrl.ottieni_stato_sintetico("non_una_partita")

    def test_esegui_turno_sicuro_ritorna_none_su_partita_non_in_corso(self, partita_mock):
        partita_mock.get_stato_partita.return_value = "non_iniziata"
        assert ctrl.esegui_turno_sicuro(partita_mock) is None


# ---------------------------------------------------------------------------
# Test dizionario localizzazione
# ---------------------------------------------------------------------------

class TestMESSAGGICONTROLLER:
    """Verifica la struttura di MESSAGGI_CONTROLLER in it.py."""

    def test_quattro_chiavi(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        assert len(MESSAGGI_CONTROLLER) == 4

    def test_chiavi_sono_costanti_corrette(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        from bingo_game.events.codici_controller import (
            CTRL_AVVIO_FALLITO_GENERICO,
            CTRL_TURNO_NON_IN_CORSO,
            CTRL_NUMERI_ESAURITI,
            CTRL_TURNO_FALLITO_GENERICO,
        )
        assert CTRL_AVVIO_FALLITO_GENERICO in MESSAGGI_CONTROLLER
        assert CTRL_TURNO_NON_IN_CORSO in MESSAGGI_CONTROLLER
        assert CTRL_NUMERI_ESAURITI in MESSAGGI_CONTROLLER
        assert CTRL_TURNO_FALLITO_GENERICO in MESSAGGI_CONTROLLER

    def test_valori_sono_stringhe_non_vuote(self):
        from bingo_game.ui.locales import MESSAGGI_CONTROLLER
        for chiave, valore in MESSAGGI_CONTROLLER.items():
            assert isinstance(valore, str), f"Valore non stringa per chiave: {chiave}"
            assert len(valore) > 0, f"Valore vuoto per chiave: {chiave}"
