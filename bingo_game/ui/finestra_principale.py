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

from bingo_game.ui.tema import (
    COLORE_ACCENT_ROSSO,
    COLORE_BTN_GRIGIO,
    COLORE_BTN_INIZIA,
    COLORE_MENU_BG,
    COLORE_TESTO_CHIARO,
    COLORE_TESTO_MUTED,
    COLORE_TITOLO_MENU,
    DIMENSIONE_FINESTRA_PRINCIPALE,
    FONT_BTN_PT,
    FONT_TITOLO_MENU_PT,
)

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
            size=DIMENSIONE_FINESTRA_PRINCIPALE,
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
        panel.SetBackgroundColour(wx.Colour(COLORE_MENU_BG))
        sizer = wx.BoxSizer(wx.VERTICAL)

        titolo_font = wx.Font(
            FONT_TITOLO_MENU_PT,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
        )
        sottotitolo_font = wx.Font(
            9,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        pulsante_font = wx.Font(
            FONT_BTN_PT,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
        )

        titolo = wx.StaticText(panel, label="TOMBOLA STARK")
        titolo.SetFont(titolo_font)
        titolo.SetForegroundColour(wx.Colour(COLORE_TITOLO_MENU))
        sizer.Add(titolo, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 20)

        sottotitolo = wx.StaticText(panel, label="Accessibile con NVDA")
        sottotitolo.SetFont(sottotitolo_font)
        sottotitolo.SetForegroundColour(wx.Colour(COLORE_TESTO_MUTED))
        sizer.Add(
            sottotitolo,
            0,
            wx.TOP | wx.BOTTOM | wx.ALIGN_CENTER_HORIZONTAL,
            10,
        )

        sizer.AddSpacer(10)

        self._btn_nuova_partita = wx.Button(
            panel,
            label="Nuova partita  (Ctrl+N)",
        )
        self._btn_nuova_partita.SetMinSize((200, 44))
        self._btn_nuova_partita.SetBackgroundColour(wx.Colour(COLORE_BTN_INIZIA))
        self._btn_nuova_partita.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._btn_nuova_partita.SetFont(pulsante_font)
        sizer.Add(
            self._btn_nuova_partita,
            0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL,
            10,
        )

        self._btn_impostazioni = wx.Button(
            panel,
            label="Impostazioni  (Ctrl+I)",
        )
        self._btn_impostazioni.SetMinSize((200, 44))
        self._btn_impostazioni.SetBackgroundColour(wx.Colour(COLORE_BTN_GRIGIO))
        self._btn_impostazioni.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._btn_impostazioni.SetFont(pulsante_font)
        sizer.Add(
            self._btn_impostazioni,
            0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL,
            10,
        )

        self._btn_guida = wx.Button(panel, label="Guida  (Ctrl+G)")
        self._btn_guida.SetMinSize((200, 44))
        self._btn_guida.SetBackgroundColour(wx.Colour(COLORE_BTN_GRIGIO))
        self._btn_guida.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._btn_guida.SetFont(pulsante_font)
        sizer.Add(
            self._btn_guida,
            0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL,
            10,
        )

        self._btn_esci = wx.Button(panel, label="Esci  (Ctrl+Q)")
        self._btn_esci.SetMinSize((200, 44))
        self._btn_esci.SetBackgroundColour(wx.Colour(COLORE_ACCENT_ROSSO))
        self._btn_esci.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._btn_esci.SetFont(pulsante_font)
        sizer.Add(
            self._btn_esci,
            0,
            wx.ALL | wx.ALIGN_CENTER_HORIZONTAL,
            10,
        )

        panel.SetSizer(sizer)
        panel.Layout()

        self._bind_events()
        self._configure_accelerators()
        self._btn_nuova_partita.SetFocus()

    # ------------------------------------------------------------------
    # Binding eventi
    # ------------------------------------------------------------------

    def _bind_events(self) -> None:
        self.Bind(wx.EVT_BUTTON, self._on_nuova_partita, self._btn_nuova_partita)
        self.Bind(wx.EVT_BUTTON, self._on_impostazioni, self._btn_impostazioni)
        self.Bind(wx.EVT_BUTTON, self._on_guida, self._btn_guida)
        self.Bind(wx.EVT_BUTTON, self._on_esci, self._btn_esci)

    def _configure_accelerators(self) -> None:
        nuova_partita_id = wx.NewIdRef()
        impostazioni_id = wx.NewIdRef()
        guida_id = wx.NewIdRef()
        esci_id = wx.NewIdRef()

        entries = [
            (wx.ACCEL_CTRL, ord("N"), nuova_partita_id),
            (wx.ACCEL_CTRL, ord("I"), impostazioni_id),
            (wx.ACCEL_CTRL, ord("G"), guida_id),
            (wx.ACCEL_CTRL, ord("Q"), esci_id),
        ]
        self.SetAcceleratorTable(wx.AcceleratorTable(entries))

        self.Bind(wx.EVT_MENU, self._on_nuova_partita, id=nuova_partita_id)
        self.Bind(wx.EVT_MENU, self._on_impostazioni, id=impostazioni_id)
        self.Bind(wx.EVT_MENU, self._on_guida, id=guida_id)
        self.Bind(wx.EVT_MENU, self._on_esci, id=esci_id)

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
        _ui_logger.debug("Menu: Guida alle regole aperta.")
        from bingo_game.ui.finestra_guida_regole import FinestraGuidaRegole  # noqa: PLC0415
        dlg = FinestraGuidaRegole(self)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_esci(self, event: wx.Event) -> None:
        _ui_logger.debug("Menu: Esci selezionato.")
        wx.GetApp().ExitMainLoop()
