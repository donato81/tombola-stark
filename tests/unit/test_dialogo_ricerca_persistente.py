import unittest
from unittest.mock import MagicMock, patch

try:
    import wx
    from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
    from bingo_game.events.eventi_output_ui_umani import (
        EventoRicercaNumeroInCartelle,
        RisultatoRicercaNumeroInCartella,
    )
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
        dialogo.EndModal = MagicMock()
        dialogo._primo_risultato = None
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

        with patch("wx.CallLater"):
            DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo._lbl_risultato.SetLabel.assert_called_once_with("Numero 42 trovato in una cartella.")

    # ------------------------------------------------------------------
    # Test: EndModal non chiamata direttamente (sostituisce il vecchio test)
    # ------------------------------------------------------------------

    def test_on_cerca_non_chiama_end_modal_se_non_trovato(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_non_trovato()

        DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo.EndModal.assert_not_called()

    def test_on_cerca_non_chiama_end_modal_immediatamente_se_trovato(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato([_crea_risultato()])

        with patch("wx.CallLater") as mock_calllater:
            DialogoRicercaNumero._on_cerca(dialogo, None)

        dialogo.EndModal.assert_not_called()
        mock_calllater.assert_called_once()

    # ------------------------------------------------------------------
    # Test: ritardo dinamico
    # ------------------------------------------------------------------

    def test_ritardo_dinamico_1_risultato(self) -> None:
        dialogo = self._crea_dialog_stub()
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato([_crea_risultato()])

        with patch("wx.CallLater") as mock_calllater:
            DialogoRicercaNumero._on_cerca(dialogo, None)

        ritardo = mock_calllater.call_args[0][0]
        self.assertEqual(ritardo, 400)

    def test_ritardo_dinamico_3_risultati(self) -> None:
        dialogo = self._crea_dialog_stub()
        risultati = [_crea_risultato(0), _crea_risultato(1), _crea_risultato(2)]
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato(risultati)

        with patch("wx.CallLater") as mock_calllater:
            DialogoRicercaNumero._on_cerca(dialogo, None)

        ritardo = mock_calllater.call_args[0][0]
        self.assertEqual(ritardo, 800)

    # ------------------------------------------------------------------
    # Test: attributo _primo_risultato
    # ------------------------------------------------------------------

    def test_primo_risultato_impostato_se_trovato(self) -> None:
        dialogo = self._crea_dialog_stub()
        r = _crea_risultato()
        dialogo._comandi.cerca_numero.return_value = self._esito_trovato([r])

        with patch("wx.CallLater"):
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
