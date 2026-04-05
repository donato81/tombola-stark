import unittest
from unittest.mock import MagicMock

try:
    import wx
    from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
except Exception:  # pragma: no cover - ambiente senza wx
    wx = None
    DialogoRicercaNumero = None


@unittest.skipIf(wx is None or DialogoRicercaNumero is None, "wxPython non disponibile nel test environment")
class TestDialogoRicercaPersistente(unittest.TestCase):
    def _crea_dialog_stub(self) -> "DialogoRicercaNumero":
        dialogo = DialogoRicercaNumero.__new__(DialogoRicercaNumero)
        dialogo._renderer = MagicMock()
        dialogo._renderer._ultimo_annuncio = "Numero 42 trovato in una cartella."
        dialogo._comandi = MagicMock()
        dialogo._input_ctrl = MagicMock()
        dialogo._input_ctrl.GetValue.return_value = "42"
        dialogo._lbl_risultato = MagicMock()
        dialogo.EndModal = MagicMock()
        return dialogo

    def test_on_cerca_non_chiama_end_modal(self) -> None:
        dialogo = self._crea_dialog_stub()

        DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo.EndModal.assert_not_called()

    def test_on_cerca_aggiorna_lbl_risultato(self) -> None:
        dialogo = self._crea_dialog_stub()
        esito_fittizio = MagicMock()
        dialogo._comandi.cerca_numero.return_value = esito_fittizio

        DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo._lbl_risultato.SetLabel.assert_called_once_with("Numero 42 trovato in una cartella.")
