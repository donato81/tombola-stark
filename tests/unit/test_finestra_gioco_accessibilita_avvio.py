import unittest
from unittest.mock import Mock, call

try:
    import wx
    from bingo_game.ui.finestra_gioco import FinestraGioco
except Exception:  # pragma: no cover - ambiente senza wx
    wx = None
    FinestraGioco = None


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestFinestraGiocoFocusIniziale(unittest.TestCase):
    def _crea_stub(self) -> "FinestraGioco":
        finestra = FinestraGioco.__new__(FinestraGioco)  # type: ignore[misc]
        finestra._avvio_silenzioso = False
        finestra._dispatch = Mock()
        finestra._renderer = Mock()
        finestra._comandi = Mock()
        finestra._aggiorna_griglie_visive = Mock()
        finestra._aggiorna_titolo_cartella = Mock()
        return finestra

    def test_imposta_focus_iniziale_dispatcha_cartella_1(self) -> None:
        finestra = self._crea_stub()
        risultato_cartella = "focus-cartella-1"
        finestra._comandi.imposta_focus_cartella.return_value = risultato_cartella
        finestra._comandi.vai_a_riga.return_value = "vai-riga-1"
        finestra._comandi.vai_a_colonna.return_value = "vai-colonna-1"

        finestra._imposta_focus_iniziale()

        finestra._dispatch.assert_any_call(risultato_cartella)
        finestra._comandi.imposta_focus_cartella.assert_called_once_with(1)

    def test_imposta_focus_iniziale_dispatcha_riga_1(self) -> None:
        finestra = self._crea_stub()
        risultato_riga = "vai-riga-1"
        finestra._comandi.imposta_focus_cartella.return_value = "focus-cartella-1"
        finestra._comandi.vai_a_riga.return_value = risultato_riga
        finestra._comandi.vai_a_colonna.return_value = "vai-colonna-1"

        finestra._imposta_focus_iniziale()

        finestra._dispatch.assert_any_call(risultato_riga)
        finestra._comandi.vai_a_riga.assert_called_once_with(1)

    def test_imposta_focus_iniziale_dispatcha_colonna_1(self) -> None:
        finestra = self._crea_stub()
        risultato_colonna = "vai-colonna-1"
        finestra._comandi.imposta_focus_cartella.return_value = "focus-cartella-1"
        finestra._comandi.vai_a_riga.return_value = "vai-riga-1"
        finestra._comandi.vai_a_colonna.return_value = risultato_colonna

        finestra._imposta_focus_iniziale()

        finestra._dispatch.assert_any_call(risultato_colonna)
        finestra._comandi.vai_a_colonna.assert_called_once_with(1)


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestOnTickAzionePostDichiarazione(unittest.TestCase):
    def _crea_stub(self) -> "FinestraGioco":
        finestra = FinestraGioco.__new__(FinestraGioco)  # type: ignore[misc]
        finestra._fase_turno_ui = "attesa_reclami"
        finestra._tick_ms = 1
        finestra._ms_trascorsi_azione = 64
        finestra._durata_finestra_corrente_ms = 100
        finestra._avvisi_emessi: set = set()
        finestra._comandi = Mock()
        finestra._renderer = Mock()
        finestra._on_timeout_azione = Mock()
        return finestra

    def test_nessun_avviso_se_umano_ha_dichiarato(self) -> None:
        finestra = self._crea_stub()
        finestra._comandi.turno_gia_dichiarato.return_value = True

        finestra._on_tick_azione(Mock())

        finestra._renderer.annuncia_avviso_timeout.assert_not_called()
        finestra._on_timeout_azione.assert_not_called()

    def test_avviso_emesso_se_umano_non_ha_dichiarato(self) -> None:
        finestra = self._crea_stub()
        finestra._comandi.turno_gia_dichiarato.return_value = False

        finestra._on_tick_azione(Mock())

        finestra._renderer.annuncia_avviso_timeout.assert_called_once()
        args, kwargs = finestra._renderer.annuncia_avviso_timeout.call_args
        self.assertEqual(kwargs.get("livello", args[1] if len(args) > 1 else None), 60)


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestDichiaraFineBotAnnuncio(unittest.TestCase):
    def _crea_stub(self) -> "FinestraGioco":
        finestra = FinestraGioco.__new__(FinestraGioco)  # type: ignore[misc]
        finestra._fase_turno_ui = "attesa_reclami"
        finestra._renderer = Mock()
        finestra._controlla_tutti_pronti = Mock()
        return finestra

    def test_annuncio_passaggio_turno_bot(self) -> None:
        finestra = self._crea_stub()
        bot = Mock()
        bot.nome = "BotTest"

        finestra._dichiara_fine_bot(bot, set(), set())

        finestra._renderer.mostra_messaggio_sistema.assert_called_once()
        testo: str = finestra._renderer.mostra_messaggio_sistema.call_args.args[0]
        self.assertIn("BotTest", testo)
        self.assertIn("passato il turno", testo)


if __name__ == "__main__":
    unittest.main()
