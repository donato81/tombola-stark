"""
Test unitari CI-safe per FinestraAiutoTastiRapidi.

Pattern: wx.App(False) condiviso a livello di classe.
Ogni test crea e distrugge dialog + parent frame in setUp/tearDown.
Nessun ShowModal viene chiamato: i test verificano solo la struttura
del dialog senza interazione event loop.

path: tests/ui/test_finestra_aiuto_tasti_rapidi.py
"""
import unittest
from unittest.mock import Mock

try:
    import wx
    from bingo_game.ui.finestra_aiuto_tasti_rapidi import FinestraAiutoTastiRapidi

    _WX_DISPONIBILE = True
except Exception:  # pragma: no cover — ambiente senza wx o senza display
    wx = None  # type: ignore[assignment]
    FinestraAiutoTastiRapidi = None  # type: ignore[assignment, misc]
    _WX_DISPONIBILE = False


@unittest.skipUnless(_WX_DISPONIBILE, "wx non disponibile in questo ambiente")
class TestFinestraAiutoTastiRapidi(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = wx.App(False)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.Destroy()

    def setUp(self) -> None:
        self.parent = wx.Frame(None)
        self.dlg = FinestraAiutoTastiRapidi(self.parent)

    def tearDown(self) -> None:
        self.dlg.Destroy()
        self.parent.Destroy()

    # ------------------------------------------------------------------
    # T1 — istanziazione senza eccezioni
    # ------------------------------------------------------------------

    def test_dialog_istanziazione_senza_eccezioni(self) -> None:
        """Il dialog viene creato senza sollevare eccezioni."""
        self.assertIsNotNone(self.dlg)

    # ------------------------------------------------------------------
    # T2 — titolo corretto
    # ------------------------------------------------------------------

    def test_dialog_titolo_corretto(self) -> None:
        """Il titolo del dialog deve essere 'Tasti rapidi'."""
        self.assertEqual(self.dlg.GetTitle(), "Tasti rapidi")

    # ------------------------------------------------------------------
    # T3 — TextCtrl multilinea read-only presente
    # ------------------------------------------------------------------

    def test_dialog_contiene_text_ctrl_readonly(self) -> None:
        """Il dialog deve contenere almeno un wx.TextCtrl con stile TE_READONLY."""
        trovato = False
        for child in self.dlg.GetChildren():
            if isinstance(child, wx.TextCtrl):
                style = child.GetWindowStyleFlag()
                if style & wx.TE_READONLY:
                    trovato = True
                    break
        self.assertTrue(trovato, "Nessun wx.TextCtrl read-only trovato nel dialog")

    # ------------------------------------------------------------------
    # T4 — pulsante Chiudi con id wx.ID_CANCEL presente
    # ------------------------------------------------------------------

    def test_dialog_contiene_pulsante_chiudi(self) -> None:
        """Il dialog deve contenere un wx.Button con id wx.ID_CANCEL."""
        trovato = False
        for child in self.dlg.GetChildren():
            if isinstance(child, wx.Button) and child.GetId() == wx.ID_CANCEL:
                trovato = True
                break
        self.assertTrue(trovato, "Nessun pulsante con id wx.ID_CANCEL trovato nel dialog")

    # ------------------------------------------------------------------
    # T5 — contenuto non vuoto e parole chiave presenti
    # ------------------------------------------------------------------

    def test_dialog_contenuto_testo_non_vuoto(self) -> None:
        """Il TextCtrl deve contenere testo non vuoto con parole chiave attese."""
        testo_ctrl: wx.TextCtrl | None = None
        for child in self.dlg.GetChildren():
            if isinstance(child, wx.TextCtrl):
                testo_ctrl = child
                break
        self.assertIsNotNone(testo_ctrl, "wx.TextCtrl non trovato")
        assert testo_ctrl is not None
        testo = testo_ctrl.GetValue()
        self.assertTrue(len(testo) > 0, "Il contenuto del TextCtrl e vuoto")
        for parola in ("Ctrl", "Escape", "Categoria"):
            self.assertIn(
                parola,
                testo,
                f"Parola chiave '{parola}' non trovata nel contenuto",
            )

    # ------------------------------------------------------------------
    # T6 — stile DEFAULT_DIALOG_STYLE
    # ------------------------------------------------------------------

    def test_dialog_stile_default_dialog(self) -> None:
        """Lo stile del dialog deve includere wx.DEFAULT_DIALOG_STYLE."""
        style = self.dlg.GetWindowStyleFlag()
        self.assertTrue(
            style & wx.DEFAULT_DIALOG_STYLE,
            "Lo stile del dialog non include wx.DEFAULT_DIALOG_STYLE",
        )

    def test_on_show_imposta_focus_sul_text_ctrl(self) -> None:
        """Quando il dialog viene mostrato, il focus deve andare al TextCtrl."""
        evento = Mock()
        evento.IsShown.return_value = True
        evento.Skip = Mock()
        self.dlg._testo = Mock()

        self.dlg._on_show(evento)

        self.dlg._testo.SetFocus.assert_called_once_with()
        evento.Skip.assert_called_once_with()

    def test_on_chiudi_termina_dialog_con_id_cancel(self) -> None:
        """Il pulsante Chiudi deve chiudere il dialog con wx.ID_CANCEL."""
        evento = Mock()
        self.dlg.EndModal = Mock()

        self.dlg._on_chiudi(evento)

        self.dlg.EndModal.assert_called_once_with(wx.ID_CANCEL)


if __name__ == "__main__":
    unittest.main()
