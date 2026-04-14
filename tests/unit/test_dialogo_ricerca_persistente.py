import unittest
from unittest.mock import MagicMock

try:
    import wx
    from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
    from bingo_game.events.eventi_output_ui_umani import (
        EventoRicercaNumeroInCartelle,
        RisultatoRicercaNumeroInCartella,
    )
    # Costanti wxPython non disponibili in ambiente headless (senza wx.App).
    # Impostazione dei valori standard per permettere al test di girare.
    _WX_CONST_FALLBACK = {
        "WXK_RETURN": 13,
        "WXK_ESCAPE": 27,
        "ID_OK": 5100,
        "ID_CANCEL": 5101,
    }
    for _nome, _valore in _WX_CONST_FALLBACK.items():
        if not hasattr(wx, _nome):
            setattr(wx, _nome, _valore)
except Exception:  # pragma: no cover - ambiente senza wx
    wx = None
    DialogoRicercaNumero = None
    EventoRicercaNumeroInCartelle = None
    RisultatoRicercaNumeroInCartella = None


def _crea_risultato(
    indice_cartella: int = 0,
    indice_riga: int = 1,
    indice_colonna: int = 2,
) -> "RisultatoRicercaNumeroInCartella":
    return RisultatoRicercaNumeroInCartella.crea(
        indice_cartella=indice_cartella,
        indice_riga=indice_riga,
        indice_colonna=indice_colonna,
        segnato=False,
    )


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
        dialogo._btn_vai = MagicMock()
        dialogo.EndModal = MagicMock()
        dialogo.FindFocus = MagicMock(return_value=None)
        dialogo._primo_risultato = None
        dialogo._risultato_pronto_per_conferma = False
        dialogo._no_risultati = False
        dialogo._ultimo_numero_cercato = ""
        return dialogo

    def _esito_trovato(self, risultati: list) -> MagicMock:
        evento = EventoRicercaNumeroInCartelle.trovato(
            id_giocatore=1,
            nome_giocatore="Umano",
            numero=42,
            totale_cartelle=1,
            risultati=risultati,
        )
        esito = MagicMock()
        esito.evento = evento
        return esito

    def _esito_non_trovato(self) -> MagicMock:
        evento = EventoRicercaNumeroInCartelle.non_trovato(
            id_giocatore=1,
            nome_giocatore="Umano",
            numero=42,
            totale_cartelle=1,
        )
        esito = MagicMock()
        esito.evento = evento
        return esito

    # ------------------------------------------------------------------
    # Test portato avanti: aggiornamento label risultato
    # ------------------------------------------------------------------

    def test_on_cerca_aggiorna_lbl_risultato(self) -> None:
        dialogo = self._crea_dialog_stub()
        esito_fittizio = MagicMock()
        dialogo._comandi.cerca_numero.return_value = esito_fittizio

        DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo._lbl_risultato.SetLabel.assert_called_once_with("Numero 42 trovato in una cartella.")

    # ------------------------------------------------------------------
    # Test: EndModal non chiamata su non trovato
    # ------------------------------------------------------------------

    def test_on_cerca_non_chiama_end_modal_se_non_trovato(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_non_trovato()

        DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo.EndModal.assert_not_called()

    def test_on_cerca_non_chiama_end_modal_se_trovato(self) -> None:
        """Il dialog NON chiude automaticamente dopo un esito trovato."""
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato([_crea_risultato()])

        DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo.EndModal.assert_not_called()

    # ------------------------------------------------------------------
    # Test: attributo _primo_risultato
    # ------------------------------------------------------------------

    def test_primo_risultato_impostato_se_trovato(self) -> None:
        dialogo = self._crea_dialog_stub()
        r = _crea_risultato()
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato([r])

        DialogoRicercaNumero._on_cerca(dialogo, None)

        self.assertIs(dialogo._primo_risultato, r)

    def test_primo_risultato_none_se_non_trovato(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_non_trovato()

        DialogoRicercaNumero._on_cerca(dialogo, None)

        self.assertIsNone(dialogo._primo_risultato)

    # ------------------------------------------------------------------
    # Test: guardia difensiva risultati vuoti con esito trovato
    # ------------------------------------------------------------------

    def test_on_cerca_non_chiama_end_modal_se_trovato_risultati_vuoti(self) -> None:
        """Se esito==trovato ma risultati è vuoto (edge case), la guardia
        difensiva blocca EndModal e lascia _primo_risultato a None."""
        dialogo = self._crea_dialog_stub()
        evento_vuoto = EventoRicercaNumeroInCartelle.trovato(
            id_giocatore=1,
            nome_giocatore="Umano",
            numero=42,
            totale_cartelle=1,
            risultati=[],
        )
        esito = MagicMock()
        esito.evento = evento_vuoto
        dialogo._comandi.cerca_numero.return_value = esito

        DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo.EndModal.assert_not_called()
        self.assertIsNone(dialogo._primo_risultato)

    # ------------------------------------------------------------------
    # Test: stato di conferma dopo esito trovato
    # ------------------------------------------------------------------

    def test_trovato_abilita_btn_vai(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato([_crea_risultato()])

        DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo._btn_vai.Enable.assert_called_once()

    def test_trovato_imposta_risultato_pronto_per_conferma(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato([_crea_risultato()])

        DialogoRicercaNumero._on_cerca(dialogo, None)

        self.assertTrue(dialogo._risultato_pronto_per_conferma)

    # ------------------------------------------------------------------
    # Test: reset stato dopo esito non trovato
    # ------------------------------------------------------------------

    def test_non_trovato_resetta_stato(self) -> None:
        dialogo = self._crea_dialog_stub()
        # Simula stato precedente da una ricerca trovato
        dialogo._primo_risultato = _crea_risultato()
        dialogo._risultato_pronto_per_conferma = True
        dialogo._comandi.cerca_numero.return_value = self._esito_non_trovato()

        DialogoRicercaNumero._on_cerca(dialogo, None)

        self.assertIsNone(dialogo._primo_risultato)
        self.assertFalse(dialogo._risultato_pronto_per_conferma)
        dialogo._btn_vai.Disable.assert_called()

    # ------------------------------------------------------------------
    # Test: conferma chiude con ID_OK
    # ------------------------------------------------------------------

    def test_on_vai_al_risultato_chiude_con_id_ok(self) -> None:
        dialogo = self._crea_dialog_stub()

        DialogoRicercaNumero._on_vai_al_risultato(dialogo, None)

        dialogo.EndModal.assert_called_once_with(wx.ID_OK)

    # ------------------------------------------------------------------
    # Test: Escape chiude con ID_CANCEL
    # ------------------------------------------------------------------

    def test_escape_chiude_con_id_cancel(self) -> None:
        dialogo = self._crea_dialog_stub()
        evento = MagicMock()
        evento.GetKeyCode.return_value = wx.WXK_ESCAPE

        DialogoRicercaNumero._on_char_hook(dialogo, evento)

        dialogo.EndModal.assert_called_once_with(wx.ID_CANCEL)

    # ------------------------------------------------------------------
    # Test: Invio su btn_vai con stato confermato chiude con ID_OK
    # ------------------------------------------------------------------

    def test_invio_su_btn_vai_chiude_con_id_ok(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._risultato_pronto_per_conferma = True
        dialogo.FindFocus.return_value = dialogo._btn_vai
        evento = MagicMock()
        evento.GetKeyCode.return_value = wx.WXK_RETURN

        DialogoRicercaNumero._on_char_hook(dialogo, evento)

        dialogo.EndModal.assert_called_once_with(wx.ID_OK)

    # ------------------------------------------------------------------
    # Test: ricerca fallita dopo successo non riusa il risultato precedente
    # ------------------------------------------------------------------

    def test_ricerca_fallita_dopo_successo_non_riusa_risultato(self) -> None:
        dialogo = self._crea_dialog_stub()
        r = _crea_risultato()
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato([r])
        DialogoRicercaNumero._on_cerca(dialogo, None)
        self.assertIs(dialogo._primo_risultato, r)

        # Seconda ricerca — fallisce
        dialogo._comandi.cerca_numero.return_value = self._esito_non_trovato()
        DialogoRicercaNumero._on_cerca(dialogo, None)

        self.assertIsNone(dialogo._primo_risultato)
        self.assertFalse(dialogo._risultato_pronto_per_conferma)

    # ------------------------------------------------------------------
    # Test: stato _no_risultati dopo ricerca fallita
    # ------------------------------------------------------------------

    def test_non_trovato_imposta_no_risultati(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_non_trovato()

        DialogoRicercaNumero._on_cerca(dialogo, None)

        self.assertTrue(dialogo._no_risultati)
        self.assertEqual(dialogo._ultimo_numero_cercato, "42")

    def test_invio_su_input_senza_risultati_chiude_con_id_cancel(self) -> None:
        """Se _no_risultati è True e l'input non è cambiato, Enter chiude il dialog."""
        dialogo = self._crea_dialog_stub()
        dialogo._no_risultati = True
        dialogo._ultimo_numero_cercato = "42"
        dialogo.FindFocus.return_value = dialogo._input_ctrl
        evento = MagicMock()
        evento.GetKeyCode.return_value = wx.WXK_RETURN

        DialogoRicercaNumero._on_char_hook(dialogo, evento)

        dialogo.EndModal.assert_called_once_with(wx.ID_CANCEL)

    def test_invio_su_input_numero_cambiato_esegue_ricerca(self) -> None:
        """Se l'utente ha modificato il numero, Enter deve lanciare _on_cerca non chiudere."""
        dialogo = self._crea_dialog_stub()
        dialogo._no_risultati = True
        dialogo._ultimo_numero_cercato = "42"
        dialogo._input_ctrl.GetValue.return_value = "7"  # numero diverso
        dialogo.FindFocus.return_value = dialogo._input_ctrl
        dialogo._comandi.cerca_numero.return_value = self._esito_non_trovato()
        evento = MagicMock()
        evento.GetKeyCode.return_value = wx.WXK_RETURN

        DialogoRicercaNumero._on_char_hook(dialogo, evento)

        dialogo._comandi.cerca_numero.assert_called_once_with(7)
        dialogo.EndModal.assert_not_called()
