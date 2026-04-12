import unittest
from unittest.mock import Mock, patch

try:
    import wx
    from bingo_game.ui.finestra_gioco import FinestraGioco, PannelloGriglia
except Exception:  # pragma: no cover - ambiente senza wx
    wx = None
    FinestraGioco = None
    PannelloGriglia = None


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

    def test_key_down_f6_ripete_ultimo_annuncio_sul_renderer_del_frame(self) -> None:
        pannello = PannelloGriglia.__new__(PannelloGriglia)
        pannello._finestra = Mock()
        pannello._finestra._renderer = Mock()
        evento = _EventoTastoFittizio(wx.WXK_F6)

        PannelloGriglia._on_key_down(pannello, evento)

        pannello._finestra._renderer.ripeti_ultimo_annuncio.assert_called_once_with()
        self.assertFalse(evento.skip_chiamato)

    def test_char_hook_ctrl_enter_invoca_pulsante_principale(self) -> None:
        finestra = self._crea_finestra_stub()
        finestra._on_pulsante_principale = Mock()
        # 13 == wx.WXK_RETURN su tutte le versioni wx; intero diretto per
        # robustezza in ambienti con stub wx parziale.
        evento = _EventoTastoFittizio(13, ctrl=True)

        FinestraGioco._on_char_hook(finestra, evento)

        finestra._on_pulsante_principale.assert_called_once_with(None)
        self.assertFalse(evento.skip_chiamato)

    def test_char_hook_ctrl_h_apre_dialog_e_ripristina_focus_griglia(self) -> None:
        finestra = self._crea_finestra_stub()
        finestra._pannello_griglia = Mock()
        evento = _EventoTastoFittizio(ord("H"), ctrl=True)

        with patch("bingo_game.ui.finestra_gioco.FinestraAiutoTastiRapidi") as dialog_cls:
            dialogo = dialog_cls.return_value

            FinestraGioco._on_char_hook(finestra, evento)

        dialog_cls.assert_called_once_with(finestra)
        dialogo.ShowModal.assert_called_once_with()
        dialogo.Destroy.assert_called_once_with()
        finestra._pannello_griglia.SetFocus.assert_called_once_with()
        self.assertFalse(evento.skip_chiamato)


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestFinestraGiocoCtrlEnterAttesaReclami(unittest.TestCase):
    def _crea_finestra_stub(self) -> FinestraGioco:
        finestra = FinestraGioco.__new__(FinestraGioco)
        finestra._comandi_sistema = Mock()
        finestra._comandi_sistema.is_terminata.return_value = False
        finestra._comandi = Mock()
        finestra._renderer = Mock()
        finestra._partita = Mock()
        finestra._fase_turno_ui = "attesa_reclami"
        finestra._in_pausa = False
        finestra._controlla_tutti_pronti = Mock()
        return finestra

    def test_ctrl_enter_attesa_reclami_emette_conferma_prima_dichiarazione(self) -> None:
        finestra = self._crea_finestra_stub()
        finestra._comandi.turno_gia_dichiarato.return_value = False

        FinestraGioco._on_pulsante_principale(finestra, None)

        finestra._comandi.dichiara_fine_turno.assert_called_once_with(finestra._partita)
        args, _ = finestra._renderer.mostra_messaggio_sistema.call_args
        self.assertIn("concluso", args[0])
        finestra._controlla_tutti_pronti.assert_called_once()

    def test_ctrl_enter_attesa_reclami_emette_messaggio_idempotente(self) -> None:
        finestra = self._crea_finestra_stub()
        finestra._comandi.turno_gia_dichiarato.return_value = True

        FinestraGioco._on_pulsante_principale(finestra, None)

        finestra._comandi.dichiara_fine_turno.assert_not_called()
        args, _ = finestra._renderer.mostra_messaggio_sistema.call_args
        self.assertIn("già dichiarato", args[0])
        finestra._controlla_tutti_pronti.assert_called_once()
