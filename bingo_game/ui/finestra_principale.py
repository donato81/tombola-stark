"""
Finestra principale — menu di avvio wxPython accessibile.

Punto di ingresso navigazionale dell'applicazione Tombola Stark.
Espone quattro voci: Nuova partita, Impostazioni (placeholder),
Guida (placeholder), Esci.
Nessuna logica di dominio: puro bordo di presentazione.

path: bingo_game/ui/finestra_principale.py
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import wx

if TYPE_CHECKING:
    from bingo_game.ui.renderers.renderer_wx import WxRenderer

_ui_logger = logging.getLogger("ui")


class FinestraPrincipale(wx.Frame):
    """
    Frame menu principale dell'applicazione.

    Apre FinestraConfigurazione su "Nuova partita".
    Mostra messaggi placeholder per "Impostazioni" e "Guida".
    Termina il processo su "Esci" via ExitMainLoop.
    """

    def __init__(
        self,
        renderer: "WxRenderer",
        parent: Optional[wx.Window] = None,
    ) -> None:
        super().__init__(
            parent,
            title="Tombola Stark — Menu principale",
            size=(400, 300),
            style=wx.DEFAULT_FRAME_STYLE,
        )
        self._renderer = renderer
        self._build_ui()
        self.Centre()
        renderer.aggiorna_finestra(self)
        renderer.mostra_messaggio_sistema("Tombola Stark. Scegli un'opzione.")

    # ------------------------------------------------------------------
    # Costruzione UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self._btn_nuova_partita = wx.Button(panel, label="Nuova partita")
        sizer.Add(self._btn_nuova_partita, 0, wx.ALL | wx.EXPAND, 10)

        self._btn_impostazioni = wx.Button(panel, label="Impostazioni")
        sizer.Add(self._btn_impostazioni, 0, wx.ALL | wx.EXPAND, 10)

        self._btn_guida = wx.Button(panel, label="Guida")
        sizer.Add(self._btn_guida, 0, wx.ALL | wx.EXPAND, 10)

        self._btn_esci = wx.Button(panel, label="Esci")
        sizer.Add(self._btn_esci, 0, wx.ALL | wx.EXPAND, 10)

        panel.SetSizer(sizer)
        panel.Layout()

        self._bind_events()
        self._btn_nuova_partita.SetFocus()

    # ------------------------------------------------------------------
    # Binding eventi
    # ------------------------------------------------------------------

    def _bind_events(self) -> None:
        self.Bind(wx.EVT_BUTTON, self._on_nuova_partita, self._btn_nuova_partita)
        self.Bind(wx.EVT_BUTTON, self._on_impostazioni, self._btn_impostazioni)
        self.Bind(wx.EVT_BUTTON, self._on_guida, self._btn_guida)
        self.Bind(wx.EVT_BUTTON, self._on_esci, self._btn_esci)

    # ------------------------------------------------------------------
    # Handler voci menu
    # ------------------------------------------------------------------

    def _on_nuova_partita(self, event: wx.Event) -> None:
        _ui_logger.debug("Menu: Nuova partita selezionata.")
        from bingo_game.ui.finestra_configurazione import FinestraConfigurazione
        finestra_conf = FinestraConfigurazione(
            renderer=self._renderer,
            parent_frame=self,
        )
        finestra_conf.Show()
        self.Hide()

    def _on_impostazioni(self, event: wx.Event) -> None:
        _ui_logger.debug("Menu: Impostazioni selezionate (placeholder).")
        self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")

    def _on_guida(self, event: wx.Event) -> None:
        _ui_logger.debug("Menu: Guida selezionata (placeholder).")
        self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")

    def _on_esci(self, event: wx.Event) -> None:
        _ui_logger.debug("Menu: Esci selezionato.")
        wx.GetApp().ExitMainLoop()
