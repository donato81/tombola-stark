"""
Dialog modale di ricerca numero — wxPython accessibile.

Aperto da FinestraGioco tramite Ctrl+F.
L'utente digita un numero, preme Invio o il tasto Cerca.
AO2 vocalizza l'esito nel dialog prima della chiusura automatica.
Il focus torna alla posizione precedente nella finestra chiamante.

path: bingo_game/ui/dialogo_ricerca.py
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import wx

if TYPE_CHECKING:
    from bingo_game.ui.renderers.renderer_wx import WxRenderer
    from bingo_game.comandi_partita import ComandiGiocatoreUmano

_ui_logger = logging.getLogger("ui")


class DialogoRicercaNumero(wx.Dialog):
    """
    Dialog modale per la ricerca di un numero nelle cartelle.

    Flusso:
    - Si apre con il focus sul campo di input.
    - L'utente digita un numero e preme Invio o il pulsante Cerca.
    - AO2 vocalizza l'esito (trovato/non trovato/errore).
    - Il dialog si chiude automaticamente dopo l'esito.
    - Il focus torna al pannello griglia della finestra chiamante.
    """

    def __init__(
        self,
        parent: wx.Window,
        renderer: "WxRenderer",
        comandi: "ComandiGiocatoreUmano",
    ) -> None:
        super().__init__(
            parent,
            title="Cerca numero",
            size=(300, 160),
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self._renderer = renderer
        self._comandi = comandi
        self._build_ui()
        self._bind_events()
        self.Centre()

    # ------------------------------------------------------------------
    # Costruzione UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(
            wx.StaticText(panel, label="Numero da cercare (1-90):"),
            0, wx.ALL, 10,
        )
        self._input_ctrl = wx.TextCtrl(panel)
        sizer.Add(self._input_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        self._btn_cerca = wx.Button(panel, label="Cerca")
        sizer.Add(self._btn_cerca, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        panel.SetSizer(sizer)
        panel.Layout()

        # Focus iniziale sull'input
        self._input_ctrl.SetFocus()

    # ------------------------------------------------------------------
    # Binding
    # ------------------------------------------------------------------

    def _bind_events(self) -> None:
        self._btn_cerca.Bind(wx.EVT_BUTTON, self._on_cerca)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        if event.GetKeyCode() == wx.WXK_RETURN:
            self._on_cerca(None)
        elif event.GetKeyCode() == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    # ------------------------------------------------------------------
    # Ricerca
    # ------------------------------------------------------------------

    def _on_cerca(self, event: object) -> None:
        testo = self._input_ctrl.GetValue().strip()
        try:
            numero = int(testo)
        except ValueError:
            self._renderer.mostra_messaggio_sistema(
                "Inserisci un numero intero tra 1 e 90."
            )
            self._input_ctrl.SelectAll()
            self._input_ctrl.SetFocus()
            return

        esito = self._comandi.cerca_numero(numero)
        self._renderer.render_esito(esito)

        # Chiusura automatica dopo l'esito
        self.EndModal(wx.ID_OK)
