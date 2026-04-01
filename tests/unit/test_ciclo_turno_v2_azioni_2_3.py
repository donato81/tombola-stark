"""
Test unitari — Azione 2 e Azione 3 del Ciclo Turno V2.

Azione 2: quando il timer pausa scade, _on_tick_pausa deve avviare
automaticamente un nuovo turno chiamando _on_pulsante_principale(None).

Azione 3: _ferma_tutti_i_timer() garantisce mutua esclusione tra i due timer.
_avvia_timer_azione e _avvia_pausa_turno devono sempre chiamare
_ferma_tutti_i_timer prima di avviare il proprio timer.

Tecnica: wx non è disponibile in CI. Si usa un fake wx + chiamate
ai metodi non-legati di FinestraGioco su oggetti stub minimali.
"""
from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import MagicMock


def _mock_wx() -> None:
    """Inietta un fake 'wx' in sys.modules se non è già installato."""
    if "wx" in sys.modules:
        return
    wx_mock = types.ModuleType("wx")
    wx_mock.Frame = object
    wx_mock.Panel = object
    wx_mock.Button = MagicMock
    wx_mock.TextCtrl = MagicMock
    wx_mock.StaticText = MagicMock
    wx_mock.SpinCtrl = MagicMock
    wx_mock.Timer = MagicMock
    wx_mock.TimerEvent = object
    wx_mock.BoxSizer = MagicMock
    wx_mock.VERTICAL = 0
    wx_mock.ALL = 1
    wx_mock.EXPAND = 2
    wx_mock.LEFT = 4
    wx_mock.RIGHT = 8
    wx_mock.TOP = 16
    wx_mock.BOTTOM = 32
    wx_mock.ALIGN_CENTER = 64
    wx_mock.TE_MULTILINE = 128
    wx_mock.TE_READONLY = 256
    wx_mock.WANTS_CHARS = 512
    wx_mock.TAB_TRAVERSAL = 1024
    wx_mock.DEFAULT_FRAME_STYLE = 2048
    wx_mock.WXK_ESCAPE = 27
    wx_mock.WXK_UP = 315
    wx_mock.WXK_DOWN = 317
    wx_mock.WXK_LEFT = 314
    wx_mock.WXK_RIGHT = 316
    wx_mock.WXK_SPACE = 32
    wx_mock.WXK_F1 = 340
    wx_mock.WXK_F6 = 345
    wx_mock.EVT_BUTTON = object()
    wx_mock.EVT_CHAR_HOOK = object()
    wx_mock.EVT_TIMER = object()
    wx_mock.EVT_KEY_DOWN = object()
    wx_mock.TIMER_ONE_SHOT = 1
    wx_mock.CallLater = MagicMock
    sys.modules["wx"] = wx_mock


# Deve essere eseguito prima di qualsiasi import che trascini wx.
_mock_wx()


# ---------------------------------------------------------------------------
# Azione 2 — Fine pausa → lancio automatico nuovo turno
# ---------------------------------------------------------------------------


class TestOnTickPausaAzione2(unittest.TestCase):
    """_on_tick_pausa deve chiamare _on_pulsante_principale al termine della pausa."""

    def test_tick_pausa_chiama_pulsante_principale(self) -> None:
        """Fine pausa → _on_pulsante_principale chiamato esattamente una volta."""
        from bingo_game.ui.finestra_gioco import FinestraGioco

        chiamate: list[object] = []

        class _Stub:
            _timer_pausa: object = MagicMock()
            _fase_turno_ui: str = "pausa_turno"

            def _aggiorna_stato_pulsante(self) -> None:
                pass

            def _on_pulsante_principale(self, event: object) -> None:
                chiamate.append(event)

        stub = _Stub()
        FinestraGioco._on_tick_pausa(stub, None)  # type: ignore[arg-type]

        self.assertEqual(len(chiamate), 1)

    def test_tick_pausa_passa_none_a_pulsante_principale(self) -> None:
        """Il parametro event passato a _on_pulsante_principale deve essere None."""
        from bingo_game.ui.finestra_gioco import FinestraGioco

        eventi_ricevuti: list[object] = []

        class _Stub:
            _timer_pausa: object = MagicMock()
            _fase_turno_ui: str = "pausa_turno"

            def _aggiorna_stato_pulsante(self) -> None:
                pass

            def _on_pulsante_principale(self, event: object) -> None:
                eventi_ricevuti.append(event)

        stub = _Stub()
        FinestraGioco._on_tick_pausa(stub, None)  # type: ignore[arg-type]

        self.assertIsNone(eventi_ricevuti[0])

    def test_tick_pausa_timer_nullo_prima_della_chiamata(self) -> None:
        """_timer_pausa è già None quando _on_pulsante_principale viene invocato."""
        from bingo_game.ui.finestra_gioco import FinestraGioco

        stato_timer: list[object] = []

        class _Stub:
            _timer_pausa: object = MagicMock()
            _fase_turno_ui: str = "pausa_turno"

            def _aggiorna_stato_pulsante(self) -> None:
                pass

            def _on_pulsante_principale(self, event: object) -> None:
                stato_timer.append(self._timer_pausa)

        stub = _Stub()
        FinestraGioco._on_tick_pausa(stub, None)  # type: ignore[arg-type]

        self.assertIsNone(stato_timer[0])

    def test_tick_pausa_imposta_stato_attesa_estrazione(self) -> None:
        """_fase_turno_ui diventa 'attesa_estrazione' dopo il tick pausa."""
        from bingo_game.ui.finestra_gioco import FinestraGioco

        class _Stub:
            _timer_pausa: object = MagicMock()
            _fase_turno_ui: str = "pausa_turno"

            def _aggiorna_stato_pulsante(self) -> None:
                pass

            def _on_pulsante_principale(self, event: object) -> None:
                pass

        stub = _Stub()
        FinestraGioco._on_tick_pausa(stub, None)  # type: ignore[arg-type]

        self.assertEqual(stub._fase_turno_ui, "attesa_estrazione")


# ---------------------------------------------------------------------------
# Azione 3 — Mutua esclusione tra i due timer
# ---------------------------------------------------------------------------


class TestFermaTuttiITimer(unittest.TestCase):
    """_ferma_tutti_i_timer deve fermare e azzerare entrambi i timer."""

    def test_ferma_entrambi_quando_entrambi_attivi(self) -> None:
        from bingo_game.ui.finestra_gioco import FinestraGioco

        t_azione = MagicMock()
        t_pausa = MagicMock()

        class _Stub:
            _timer_azione = t_azione
            _timer_pausa = t_pausa

        stub = _Stub()
        FinestraGioco._ferma_tutti_i_timer(stub)  # type: ignore[arg-type]

        t_azione.Stop.assert_called_once()
        t_pausa.Stop.assert_called_once()
        self.assertIsNone(stub._timer_azione)
        self.assertIsNone(stub._timer_pausa)

    def test_ferma_solo_azione_se_pausa_none(self) -> None:
        from bingo_game.ui.finestra_gioco import FinestraGioco

        t_azione = MagicMock()

        class _Stub:
            _timer_azione = t_azione
            _timer_pausa = None

        stub = _Stub()
        FinestraGioco._ferma_tutti_i_timer(stub)  # type: ignore[arg-type]

        t_azione.Stop.assert_called_once()
        self.assertIsNone(stub._timer_azione)
        self.assertIsNone(stub._timer_pausa)

    def test_ferma_solo_pausa_se_azione_none(self) -> None:
        from bingo_game.ui.finestra_gioco import FinestraGioco

        t_pausa = MagicMock()

        class _Stub:
            _timer_azione = None
            _timer_pausa = t_pausa

        stub = _Stub()
        FinestraGioco._ferma_tutti_i_timer(stub)  # type: ignore[arg-type]

        t_pausa.Stop.assert_called_once()
        self.assertIsNone(stub._timer_azione)
        self.assertIsNone(stub._timer_pausa)

    def test_nessuna_eccezione_se_entrambi_none(self) -> None:
        from bingo_game.ui.finestra_gioco import FinestraGioco

        class _Stub:
            _timer_azione = None
            _timer_pausa = None

        stub = _Stub()
        FinestraGioco._ferma_tutti_i_timer(stub)  # type: ignore[arg-type]

        self.assertIsNone(stub._timer_azione)
        self.assertIsNone(stub._timer_pausa)


class TestAvvioTimerConMutuaEsclusione(unittest.TestCase):
    """_avvia_timer_azione e _avvia_pausa_turno chiamano _ferma_tutti_i_timer."""

    def test_avvia_timer_azione_ferma_il_timer_pausa(self) -> None:
        """Se _timer_pausa è attivo, deve essere fermato da _avvia_timer_azione."""
        from bingo_game.ui.finestra_gioco import FinestraGioco
        from unittest.mock import patch
        import sys

        fermate: list[str] = []
        timer_nuovo = MagicMock()

        class _Stub:
            _timer_azione = None
            _timer_pausa = MagicMock()
            _durata_finestra_corrente_ms: int = 0
            _ms_trascorsi_azione: int = 0
            _avvisi_emessi: set = set()
            _tick_ms: int = 500

            def _ferma_tutti_i_timer(self) -> None:
                fermate.append("ferma")
                self._timer_azione = None
                self._timer_pausa = None

            def _on_tick_azione(self, event: object) -> None:
                pass

            def Bind(self, *args: object, **kwargs: object) -> None:
                pass

        stub = _Stub()
        with patch.object(sys.modules["wx"], "Timer", return_value=timer_nuovo):
            FinestraGioco._avvia_timer_azione(stub, 60000)  # type: ignore[arg-type]

        self.assertIn("ferma", fermate, "_ferma_tutti_i_timer non è stato chiamato")
        self.assertIsNone(stub._timer_pausa)

    def test_avvia_pausa_turno_ferma_il_timer_azione(self) -> None:
        """Se _timer_azione è attivo, deve essere fermato da _avvia_pausa_turno."""
        from bingo_game.ui.finestra_gioco import FinestraGioco
        from unittest.mock import patch
        import sys

        fermate: list[str] = []
        timer_nuovo = MagicMock()

        class _FakeRenderer:
            def annuncia_avvio_pausa_turno(self, secondi: int) -> None:
                pass

        class _Stub:
            _timer_azione = MagicMock()  # Timer azione attivo
            _timer_pausa = None
            _renderer = _FakeRenderer()

            def _ferma_tutti_i_timer(self) -> None:
                fermate.append("ferma")
                self._timer_azione = None
                self._timer_pausa = None

            def _on_tick_pausa(self, event: object) -> None:
                pass

            def Bind(self, *args: object, **kwargs: object) -> None:
                pass

        stub = _Stub()
        with patch.object(sys.modules["wx"], "Timer", return_value=timer_nuovo):
            FinestraGioco._avvia_pausa_turno(stub, 5000)  # type: ignore[arg-type]

        self.assertIn("ferma", fermate, "_ferma_tutti_i_timer non è stato chiamato")
        self.assertIsNone(stub._timer_azione)

    def test_timeout_azione_usa_ferma_tutti(self) -> None:
        """_on_timeout_azione usa _ferma_tutti_i_timer (non solo quello d'azione)."""
        from bingo_game.ui.finestra_gioco import FinestraGioco

        fermate: list[str] = []
        verifiche_avanzate: list[str] = []

        class _Stub:
            _timer_azione = MagicMock()
            _timer_pausa = MagicMock()
            _fase_turno_ui: str = "attesa_reclami"

            def _ferma_tutti_i_timer(self) -> None:
                fermate.append("ferma")
                self._timer_azione = None
                self._timer_pausa = None

            def _esegui_verifica_premi(self) -> None:
                verifiche_avanzate.append("verifica")

        stub = _Stub()
        FinestraGioco._on_timeout_azione(stub)  # type: ignore[arg-type]

        self.assertIn("ferma", fermate)
        self.assertIn("verifica", verifiche_avanzate)
        self.assertIsNone(stub._timer_pausa)

    def test_on_all_ready_usa_ferma_tutti(self) -> None:
        """_on_all_ready usa _ferma_tutti_i_timer (non solo quello d'azione)."""
        from bingo_game.ui.finestra_gioco import FinestraGioco

        fermate: list[str] = []

        class _FakeRenderer:
            def annuncia_tutti_pronti(self) -> None:
                pass

        class _Stub:
            _timer_azione = MagicMock()
            _timer_pausa = MagicMock()
            _fase_turno_ui: str = "attesa_reclami"
            _renderer = _FakeRenderer()

            def _ferma_tutti_i_timer(self) -> None:
                fermate.append("ferma")
                self._timer_azione = None
                self._timer_pausa = None

            def _esegui_verifica_premi(self) -> None:
                pass

        stub = _Stub()
        FinestraGioco._on_all_ready(stub)  # type: ignore[arg-type]

        self.assertIn("ferma", fermate)
        self.assertIsNone(stub._timer_azione)
        self.assertIsNone(stub._timer_pausa)


if __name__ == "__main__":
    unittest.main()
