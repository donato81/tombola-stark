"""bingo_game/ui/finestra_guida_regole.py

Dialog modale con la guida alle regole del gioco (FinestraGuidaRegole).
Cinque capitoli navigabili con pulsanti Precedente e Successivo.

Apertura:  Ctrl+Shift+H da FinestraGioco; Ctrl+G da FinestraPrincipale (menu Guida).
Chiusura:  pulsante Chiudi o tasto Escape.
Focus:     all'apertura va su _testo (primo capitolo);
           al cambio pagina va su _lbl_titolo (NVDA legge il nuovo titolo).
"""
from __future__ import annotations

import logging

import wx

from bingo_game.ui.locales.it_guida import GUIDA_CAPITOLI, GUIDA_UI

_ui_logger = logging.getLogger(__name__)


class FinestraGuidaRegole(wx.Dialog):
    """Dialog modale read-only con cinque capitoli di regole navigabili."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(
            parent,
            title=GUIDA_UI["TITOLO_FINESTRA"],
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self._indice_corrente: int = 0
        self._build_ui()
        self._aggiorna_visualizzazione()
        self.Centre()
        self.Bind(wx.EVT_SHOW, self._on_show)

    def _build_ui(self) -> None:
        sizer_principale = wx.BoxSizer(wx.VERTICAL)

        self._lbl_titolo = wx.StaticText(self, label="")
        sizer_principale.Add(self._lbl_titolo, 0, wx.ALL | wx.EXPAND, 8)

        self._testo = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
            size=wx.Size(520, 300),
        )
        sizer_principale.Add(self._testo, 1, wx.ALL | wx.EXPAND, 8)

        sizer_nav = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_precedente = wx.Button(self, label=GUIDA_UI["BTN_PRECEDENTE"])
        self._lbl_pagina = wx.StaticText(self, label="")
        self._btn_successivo = wx.Button(self, label=GUIDA_UI["BTN_SUCCESSIVO"])
        sizer_nav.Add(self._btn_precedente, 0, wx.RIGHT, 8)
        sizer_nav.Add(self._lbl_pagina, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer_nav.Add(self._btn_successivo, 0, wx.LEFT, 8)
        sizer_principale.Add(sizer_nav, 0, wx.ALL | wx.EXPAND, 8)

        btn_sizer = wx.StdDialogButtonSizer()
        self._btn_chiudi = wx.Button(self, id=wx.ID_CANCEL, label=GUIDA_UI["BTN_CHIUDI"])
        btn_sizer.AddButton(self._btn_chiudi)
        btn_sizer.Realize()
        sizer_principale.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 6)

        self.SetSizerAndFit(sizer_principale)

        self.Bind(wx.EVT_BUTTON, self._vai_pagina_precedente, self._btn_precedente)
        self.Bind(wx.EVT_BUTTON, self._vai_pagina_successiva, self._btn_successivo)
        self.Bind(wx.EVT_BUTTON, self._on_chiudi, self._btn_chiudi)

    def _aggiorna_visualizzazione(self) -> None:
        titolo, righe = GUIDA_CAPITOLI[self._indice_corrente]
        self._lbl_titolo.SetLabel(titolo)
        self._testo.SetValue("\n".join(righe))
        totale = len(GUIDA_CAPITOLI)
        self._lbl_pagina.SetLabel(
            GUIDA_UI["ANNUNCIO_PAGINA"].format(
                corrente=self._indice_corrente + 1,
                totale=totale,
            )
        )
        self._btn_precedente.Enable(self._indice_corrente > 0)
        self._btn_successivo.Enable(self._indice_corrente < totale - 1)

    def _vai_pagina_precedente(self, event: wx.CommandEvent) -> None:  # noqa: ARG002
        self._indice_corrente -= 1
        self._aggiorna_visualizzazione()
        wx.CallAfter(self._lbl_titolo.SetFocus)

    def _vai_pagina_successiva(self, event: wx.CommandEvent) -> None:  # noqa: ARG002
        self._indice_corrente += 1
        self._aggiorna_visualizzazione()
        wx.CallAfter(self._lbl_titolo.SetFocus)

    def _on_chiudi(self, event: wx.CommandEvent) -> None:  # noqa: ARG002
        self.EndModal(wx.ID_CANCEL)

    def _on_show(self, event: wx.ShowEvent) -> None:
        if event.IsShown():
            self._testo.SetFocus()
        event.Skip()
