import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

try:
    import wx
    from bingo_game.ui import finestra_gioco as finestra_gioco_module
    from bingo_game.ui.finestra_gioco import FinestraGioco
except Exception:  # pragma: no cover - ambiente senza wx
    wx = None
    FinestraGioco = None
    finestra_gioco_module = None


class _FakeButton:
    def __init__(self, parent: object, label: str, size: object | None = None) -> None:
        self.parent = parent
        self.label = label
        self.size = size
        self._name = ""
        self._tooltip = ""

    def SetName(self, name: str) -> None:
        self._name = name

    def GetName(self) -> str:
        return self._name

    def SetToolTip(self, tooltip: str) -> None:
        self._tooltip = tooltip

    def GetToolTip(self) -> str:
        return self._tooltip

    def SetBackgroundColour(self, colour: object) -> None:
        return None

    def SetForegroundColour(self, colour: object) -> None:
        return None

    def Disable(self) -> None:
        return None

    def Hide(self) -> None:
        return None

    def Bind(self, event: object, handler: object) -> None:
        return None


class _FakeTextCtrl:
    def __init__(self, parent: object, style: int, size: object | None = None) -> None:
        self.parent = parent
        self.style = style
        self.size = size
        self._name = ""

    def SetName(self, name: str) -> None:
        self._name = name

    def GetName(self) -> str:
        return self._name


class _FakePanel:
    def __init__(self, parent: object) -> None:
        self.parent = parent

    def SetSizer(self, sizer: object) -> None:
        self.sizer = sizer

    def Layout(self) -> None:
        return None


class _FakeStaticText:
    def __init__(self, parent: object, label: str) -> None:
        self.parent = parent
        self.label = label


class _FakeSizer:
    def __init__(self) -> None:
        self.children: list[object] = []

    def Add(self, child: object, proportion: int, flags: int, border: int) -> None:
        self.children.append(child)


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestFinestraGiocoAccessibilitaBuildUi(unittest.TestCase):
    def _crea_finestra_stub(self) -> FinestraGioco:
        finestra = FinestraGioco.__new__(FinestraGioco)
        finestra.Bind = Mock()
        finestra.Layout = Mock()
        finestra._on_pausa = Mock()
        finestra._on_torna_menu = Mock()
        finestra._on_cartella_precedente = Mock()
        finestra._on_cartella_successiva = Mock()
        finestra._on_premio = Mock()
        finestra._on_pulsante_principale = Mock()
        return finestra

    def test_build_ui_imposta_nomi_accessibili_principali_e_log(self) -> None:
        finestra = self._crea_finestra_stub()

        with patch.object(finestra_gioco_module.wx, "Panel", _FakePanel), \
             patch.object(finestra_gioco_module.wx, "Button", _FakeButton), \
             patch.object(finestra_gioco_module.wx, "TextCtrl", _FakeTextCtrl), \
             patch.object(finestra_gioco_module.wx, "StaticText", _FakeStaticText), \
             patch.object(finestra_gioco_module.wx, "BoxSizer", lambda orient: _FakeSizer()), \
             patch.object(finestra_gioco_module, "PannelloGriglia", lambda parent, frame: object()), \
             patch.object(finestra_gioco_module, "PannelloTabellone", lambda parent: object()), \
             patch.object(finestra_gioco_module, "PannelloCartella", lambda parent: object()):
            FinestraGioco._build_ui(finestra)

        self.assertEqual("Pulsante principale partita", finestra._btn_principale.GetName())
        self.assertEqual("Metti in pausa", finestra._btn_pausa.GetName())
        self.assertEqual("Torna al menu principale", finestra._btn_torna_menu.GetName())
        self.assertEqual("Log annunci. Usa Ctrl+E per consultare.", finestra._log_ctrl.GetName())


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestFinestraGiocoSelezioneCartella(unittest.TestCase):
    def _crea_finestra_stub(self, cartelle: int = 3) -> FinestraGioco:
        finestra = FinestraGioco.__new__(FinestraGioco)
        giocatore_umano = SimpleNamespace(
            cartelle=[object() for _ in range(cartelle)],
            is_automatico=lambda: False,
        )
        finestra._partita = SimpleNamespace(giocatori=[giocatore_umano])
        finestra._panel = Mock()
        finestra._panel.Layout = Mock()
        finestra._sizer_selezione = _FakeSizer()
        finestra._pulsanti_selezione = []
        finestra.Bind = Mock()
        finestra.Layout = Mock()
        finestra._dispatch = Mock()
        finestra._comandi = Mock()
        finestra._pannello_griglia = Mock()
        return finestra

    def test_crea_pulsanti_selezione_cartella_crea_numero_corretto(self) -> None:
        finestra = self._crea_finestra_stub(cartelle=4)

        with patch.object(finestra_gioco_module.wx, "Button", _FakeButton):
            FinestraGioco._crea_pulsanti_selezione_cartella(finestra)

        self.assertEqual(len(finestra._pulsanti_selezione), 4)
        self.assertEqual(len(finestra._sizer_selezione.children), 4)

    def test_crea_pulsanti_selezione_cartella_imposta_nomi_accessibili(self) -> None:
        finestra = self._crea_finestra_stub(cartelle=2)

        with patch.object(finestra_gioco_module.wx, "Button", _FakeButton):
            FinestraGioco._crea_pulsanti_selezione_cartella(finestra)

        nomi = [btn.GetName().lower() for btn in finestra._pulsanti_selezione]
        self.assertEqual(2, len(nomi))
        self.assertTrue(all("cartella" in nome for nome in nomi))

    def test_on_selezione_cartella_btn_dispatcha_comando_corretto(self) -> None:
        finestra = self._crea_finestra_stub(cartelle=1)
        esito = object()
        finestra._comandi.imposta_focus_cartella.return_value = esito

        FinestraGioco._on_selezione_cartella_btn(finestra, 3, Mock())

        finestra._comandi.imposta_focus_cartella.assert_called_once_with(3)
        finestra._dispatch.assert_called_once_with(esito)
        finestra._pannello_griglia.SetFocus.assert_called_once_with()


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestFinestraGiocoAvvioSilenzioso(unittest.TestCase):
    """Verifica che _imposta_focus_iniziale non vocalizza i dispatch iniziali
    e che il messaggio di benvenuto venga emesso una sola volta al termine."""

    def _crea_finestra_stub(self) -> FinestraGioco:
        finestra = FinestraGioco.__new__(FinestraGioco)
        finestra._avvio_silenzioso = False
        finestra._renderer = Mock()
        finestra._comandi = Mock()
        finestra._comandi.imposta_focus_cartella.return_value = object()
        finestra._comandi.vai_a_riga.return_value = object()
        finestra._comandi.vai_a_colonna.return_value = object()
        finestra._aggiorna_griglie_visive = Mock()
        finestra._aggiorna_titolo_cartella = Mock()
        return finestra

    def test_dispatch_silenziato_durante_avvio(self) -> None:
        """_dispatch non deve delegare al renderer mentre _avvio_silenzioso e True."""
        finestra = FinestraGioco.__new__(FinestraGioco)
        finestra._avvio_silenzioso = True
        finestra._renderer = Mock()

        from bingo_game.events.eventi import EsitoAzione
        esito = EsitoAzione(ok=True, evento=None)
        FinestraGioco._dispatch(finestra, esito)

        finestra._renderer.render_esito.assert_not_called()

    def test_dispatch_attivo_quando_non_in_avvio(self) -> None:
        """_dispatch deve delegare al renderer quando _avvio_silenzioso e False."""
        finestra = FinestraGioco.__new__(FinestraGioco)
        finestra._avvio_silenzioso = False
        finestra._renderer = Mock()

        from bingo_game.events.eventi import EsitoAzione
        esito = EsitoAzione(ok=True, evento=None)
        FinestraGioco._dispatch(finestra, esito)

        finestra._renderer.render_esito.assert_called_once_with(esito)

    def test_imposta_focus_iniziale_emette_benvenuto(self) -> None:
        """_imposta_focus_iniziale deve chiamare mostra_messaggio_sistema una sola volta."""
        finestra = self._crea_finestra_stub()

        FinestraGioco._imposta_focus_iniziale(finestra)

        finestra._renderer.mostra_messaggio_sistema.assert_called_once()
        testo_chiamato = finestra._renderer.mostra_messaggio_sistema.call_args[0][0]
        assert "finestra di gioco" in testo_chiamato.lower()

    def test_imposta_focus_iniziale_ripristina_flag(self) -> None:
        """Al termine di _imposta_focus_iniziale il flag _avvio_silenzioso deve essere False."""
        finestra = self._crea_finestra_stub()

        FinestraGioco._imposta_focus_iniziale(finestra)

        assert finestra._avvio_silenzioso is False

    def test_imposta_focus_iniziale_non_usa_callafter(self) -> None:
        """_imposta_focus_iniziale non deve usare wx.CallAfter per il benvenuto."""
        finestra = self._crea_finestra_stub()

        with patch.object(finestra_gioco_module.wx, "CallAfter") as mock_call_after:
            FinestraGioco._imposta_focus_iniziale(finestra)

        mock_call_after.assert_not_called()


@unittest.skipIf(wx is None or FinestraGioco is None, "wxPython non disponibile nel test environment")
class TestFinestraGiocoMostraRiepilogoFinale(unittest.TestCase):
    def _crea_finestra_stub(self) -> FinestraGioco:
        finestra = FinestraGioco.__new__(FinestraGioco)
        finestra._pannello_griglia = Mock()
        finestra._pannello_tabellone = Mock()
        finestra._pannello_cartella = Mock()
        finestra._pannello_riepilogo = Mock()
        finestra._btn_torna_menu = Mock()
        finestra.Layout = Mock()
        finestra.SetTitle = Mock()
        return finestra

    def test_mostra_riepilogo_finale_mostra_pannello(self) -> None:
        """mostra_riepilogo_finale deve rendere visibile PannelloRiepilogoFinale."""
        finestra = self._crea_finestra_stub()
        dati_campione: dict = {
            "vincitore_tombola": "Alice",
            "turni_giocati": 42,
            "conteggio_estratti": 42,
            "storico_premi": [],
        }

        with patch.object(finestra_gioco_module.wx, "CallAfter") as mock_call_after:
            FinestraGioco.mostra_riepilogo_finale(finestra, dati_campione)

        finestra._pannello_riepilogo.mostra.assert_called_once_with(dati_campione)
        finestra._pannello_riepilogo.Show.assert_called_once()
        finestra._pannello_griglia.Hide.assert_called_once()
        finestra.SetTitle.assert_called_once_with("Tombola Stark — Partita terminata")
        mock_call_after.assert_called_once_with(finestra._btn_torna_menu.SetFocus)


if __name__ == "__main__":
    unittest.main()