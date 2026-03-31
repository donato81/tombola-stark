import unittest
from unittest.mock import Mock

try:
    import wx
    from bingo_game.ui.finestra_gioco import FinestraGioco
except Exception:  # pragma: no cover - ambiente senza wx
    wx = None
    FinestraGioco = None


class _EventoTastoFittizio:
    def __init__(self, key_code: int, *, ctrl: bool = False, alt: bool = False, shift: bool = False) -> None:
        self._key_code = key_code
        self._ctrl = ctrl
        self._alt = alt
        self._shift = shift
        self.skip_chiamato = False

    def GetKeyCode(self) -> int:
        return self._key_code

    def ControlDown(self) -> bool:
        return self._ctrl

    def AltDown(self) -> bool:
        return self._alt

    def ShiftDown(self) -> bool:
        return self._shift

    def Skip(self) -> None:
        self.skip_chiamato = True


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestFinestraGiocoShortcuts(unittest.TestCase):
    def _crea_finestra_stub(self) -> FinestraGioco:
        finestra = FinestraGioco.__new__(FinestraGioco)
        finestra._dispatch = Mock()
        finestra._on_pulsante_principale = Mock()
        finestra._apri_ricerca_numero = Mock()
        finestra._consulta_log = Mock()
        finestra._comandi = Mock()
        return finestra

    def test_char_hook_intercetta_shift_freccia_su(self) -> None:
        finestra = self._crea_finestra_stub()
        finestra._comandi.riga_su_avanzata.return_value = "evento-avanzato-riga"
        evento = _EventoTastoFittizio(wx.WXK_UP, shift=True)

        FinestraGioco._on_char_hook(finestra, evento)

        finestra._comandi.riga_su_avanzata.assert_called_once_with()
        finestra._dispatch.assert_called_once_with("evento-avanzato-riga")
        self.assertFalse(evento.skip_chiamato)

    def test_char_hook_intercetta_shift_freccia_destra(self) -> None:
        finestra = self._crea_finestra_stub()
        finestra._comandi.colonna_destra_avanzata.return_value = "evento-avanzato-colonna"
        evento = _EventoTastoFittizio(wx.WXK_RIGHT, shift=True)

        FinestraGioco._on_char_hook(finestra, evento)

        finestra._comandi.colonna_destra_avanzata.assert_called_once_with()
        finestra._dispatch.assert_called_once_with("evento-avanzato-colonna")
        self.assertFalse(evento.skip_chiamato)
