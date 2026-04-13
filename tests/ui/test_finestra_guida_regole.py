"""tests/ui/test_finestra_guida_regole.py

Test unitari per FinestraGuidaRegole.
Marker: gui — esclusi dalla suite CI non-GUI.
"""
from __future__ import annotations

import unittest

try:
    import wx
    from bingo_game.ui.finestra_guida_regole import FinestraGuidaRegole
    from bingo_game.ui.locales.it_guida import GUIDA_CAPITOLI, GUIDA_UI

    _WX_DISPONIBILE = True
except Exception:  # pragma: no cover — ambiente senza wx o senza display
    wx = None  # type: ignore[assignment]
    FinestraGuidaRegole = None  # type: ignore[assignment, misc]
    GUIDA_CAPITOLI = ()  # type: ignore[assignment]
    GUIDA_UI = {}  # type: ignore[assignment]
    _WX_DISPONIBILE = False


@unittest.skipUnless(_WX_DISPONIBILE, "wx non disponibile in questo ambiente")
class TestFinestraGuidaRegole(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = wx.App(False)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.Destroy()

    def setUp(self) -> None:
        self.parent = wx.Frame(None)
        self.dlg = FinestraGuidaRegole(self.parent)

    def tearDown(self) -> None:
        self.dlg.Destroy()
        self.parent.Destroy()

    def test_dialog_istanziazione_senza_eccezioni(self) -> None:
        self.assertIsInstance(self.dlg, wx.Dialog)

    def test_dialog_titolo_corretto(self) -> None:
        self.assertEqual(self.dlg.GetTitle(), GUIDA_UI["TITOLO_FINESTRA"])

    def test_dialog_contiene_text_ctrl_readonly(self) -> None:
        self.assertTrue(self.dlg._testo.HasFlag(wx.TE_READONLY))

    def test_dialog_contiene_pulsante_chiudi(self) -> None:
        self.assertEqual(self.dlg._btn_chiudi.GetLabel(), GUIDA_UI["BTN_CHIUDI"])

    def test_dialog_contiene_pulsante_precedente(self) -> None:
        self.assertEqual(
            self.dlg._btn_precedente.GetLabel(), GUIDA_UI["BTN_PRECEDENTE"]
        )

    def test_dialog_contiene_pulsante_successivo(self) -> None:
        self.assertEqual(
            self.dlg._btn_successivo.GetLabel(), GUIDA_UI["BTN_SUCCESSIVO"]
        )

    def test_dialog_precedente_disabilitato_prima_pagina(self) -> None:
        self.assertFalse(self.dlg._btn_precedente.IsEnabled())

    def test_dialog_successivo_abilitato_prima_pagina(self) -> None:
        self.assertTrue(self.dlg._btn_successivo.IsEnabled())

    def test_dialog_capitolo_1_visibile_all_apertura(self) -> None:
        titolo_atteso, righe_attese = GUIDA_CAPITOLI[0]
        self.assertEqual(self.dlg._lbl_titolo.GetLabel(), titolo_atteso)
        self.assertEqual(self.dlg._testo.GetValue(), "\n".join(righe_attese))

    def test_dialog_navigazione_successivo(self) -> None:
        evento = wx.CommandEvent(wx.wxEVT_BUTTON)
        self.dlg._vai_pagina_successiva(evento)
        titolo_atteso, righe_attese = GUIDA_CAPITOLI[1]
        self.assertEqual(self.dlg._lbl_titolo.GetLabel(), titolo_atteso)
        self.assertEqual(self.dlg._testo.GetValue(), "\n".join(righe_attese))

    def test_dialog_cinque_capitoli_disponibili(self) -> None:
        self.assertEqual(len(GUIDA_CAPITOLI), 5)

    def test_dialog_successivo_disabilitato_ultima_pagina(self) -> None:
        for _ in range(len(GUIDA_CAPITOLI) - 1):
            evento = wx.CommandEvent(wx.wxEVT_BUTTON)
            self.dlg._vai_pagina_successiva(evento)
        self.assertFalse(self.dlg._btn_successivo.IsEnabled())


if __name__ == "__main__":
    unittest.main()
