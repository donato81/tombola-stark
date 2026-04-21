"""
Overlay visivo del numero estratto per la finestra di gioco.

Mostra il numero estratto in formato grande per pochi secondi senza
interferire con il focus tastiera o con i flussi NVDA gia' esistenti.

path: bingo_game/ui/overlay_numero.py
"""
from __future__ import annotations

from typing import Optional

import wx

from bingo_game.ui.tema import (
    COLORE_HEADER_ACCENT,
    COLORE_HEADER_BG,
    COLORE_TESTO_MUTED,
    DIMENSIONE_OVERLAY,
    FONT_OVERLAY_LABEL_PT,
    FONT_OVERLAY_PT,
)

_DURATA_OVERLAY_MS: int = 10_000
_MARGINE_OVERLAY_PX: int = 16


class OverlayNumeroEstratto(wx.Frame):
    """Finestra overlay non modale che mostra temporaneamente il numero estratto."""

    def __init__(self, parent: wx.Frame, durata_ms: int = _DURATA_OVERLAY_MS) -> None:
        style = (
            wx.STAY_ON_TOP
            | wx.FRAME_NO_TASKBAR
            | wx.FRAME_TOOL_WINDOW
            | wx.BORDER_NONE
        )
        super().__init__(parent, title="Overlay numero estratto", style=style)
        self._parent: wx.Frame = parent
        self._durata_ms: int = durata_ms
        self._timer = wx.Timer(self)
        self._lbl_numero: Optional[wx.StaticText] = None
        self._build_ui()
        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)
        self.Hide()

    def _build_ui(self) -> None:
        self.SetSize(wx.Size(*DIMENSIONE_OVERLAY))
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(COLORE_HEADER_BG))

        sizer = wx.BoxSizer(wx.VERTICAL)

        lbl_titolo = wx.StaticText(panel, label="Numero estratto")
        lbl_titolo.SetForegroundColour(wx.Colour(COLORE_TESTO_MUTED))
        lbl_titolo.SetFont(
            wx.Font(
                FONT_OVERLAY_LABEL_PT,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
            )
        )
        sizer.Add(lbl_titolo, 0, wx.ALIGN_CENTER | wx.TOP, 12)

        self._lbl_numero = wx.StaticText(panel, label="", style=wx.ALIGN_CENTER_HORIZONTAL)
        self._lbl_numero.SetForegroundColour(wx.Colour(COLORE_HEADER_ACCENT))
        self._lbl_numero.SetFont(
            wx.Font(
                FONT_OVERLAY_PT,
                wx.FONTFAMILY_DEFAULT,
                wx.FONTSTYLE_NORMAL,
                wx.FONTWEIGHT_BOLD,
            )
        )
        sizer.Add(self._lbl_numero, 1, wx.ALIGN_CENTER | wx.ALL, 8)

        panel.SetSizer(sizer)
        panel.Layout()
        self.SetBackgroundColour(wx.Colour(COLORE_HEADER_BG))

    def mostra_numero(self, numero: int) -> None:
        """Aggiorna il numero visualizzato e mostra l'overlay con timeout automatico."""
        if self._lbl_numero is None:
            return
        self._lbl_numero.SetLabel(str(numero))
        self._posiziona_overlay()
        if self._timer.IsRunning():
            self._timer.Stop()
        self.ShowWithoutActivating()
        self._timer.Start(self._durata_ms, wx.TIMER_ONE_SHOT)

    def _posiziona_overlay(self) -> None:
        """Posiziona l'overlay nell'angolo in basso a destra della finestra parent."""
        px, py = self._parent.GetScreenPosition()
        pw, ph = self._parent.GetSize()
        ow, oh = DIMENSIONE_OVERLAY
        self.SetPosition(
            wx.Point(
                px + pw - ow - _MARGINE_OVERLAY_PX,
                py + ph - oh - _MARGINE_OVERLAY_PX,
            )
        )

    def _on_timer(self, event: wx.TimerEvent) -> None:
        """Nasconde l'overlay allo scadere del timer."""
        self.Hide()