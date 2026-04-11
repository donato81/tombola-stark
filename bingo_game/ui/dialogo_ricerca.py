"""
Dialog modale di ricerca numero — wxPython accessibile.

Aperto da FinestraGioco tramite Ctrl+F.
L'utente digita un numero, preme Invio o il tasto Cerca.
L'esito viene mostrato nell'area risultato interna e vocalizzato da NVDA/JAWS.
Il dialog rimane aperto per permettere ricerche successive.
L'utente chiude il dialog tramite il pulsante Chiudi o il tasto Escape.

path: bingo_game/ui/dialogo_ricerca.py
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

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
    - L'esito viene mostrato nell'area risultato interna e vocalizzato da NVDA/JAWS.
    - Il dialog rimane aperto per permettere ricerche successive.
    - L'utente chiude il dialog tramite il pulsante Chiudi o il tasto Escape.
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
            size=(300, 280),
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self._renderer = renderer
        self._comandi = comandi
        self._primo_risultato: Optional[Any] = None
        self._risultato_pronto_per_conferma: bool = False
        self._no_risultati: bool = False
        self._ultimo_numero_cercato: str = ""
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

        self._lbl_risultato = wx.StaticText(panel, label="")
        sizer.Add(self._lbl_risultato, 0, wx.ALL | wx.EXPAND, 10)

        self._btn_vai = wx.Button(panel, label="Vai al risultato")
        self._btn_vai.Disable()
        sizer.Add(self._btn_vai, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self._btn_chiudi = wx.Button(panel, wx.ID_CANCEL, label="Chiudi")
        sizer.Add(self._btn_chiudi, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        panel.SetSizer(sizer)
        panel.Layout()

        # Focus iniziale sull'input
        self._input_ctrl.SetFocus()

    # ------------------------------------------------------------------
    # Binding
    # ------------------------------------------------------------------

    def _bind_events(self) -> None:
        self._btn_cerca.Bind(wx.EVT_BUTTON, self._on_cerca)
        self._btn_vai.Bind(wx.EVT_BUTTON, self._on_vai_al_risultato)
        self._btn_chiudi.Bind(wx.EVT_BUTTON, lambda _: self.EndModal(wx.ID_CANCEL))
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        key = event.GetKeyCode()
        if key == wx.WXK_RETURN:
            focused = self.FindFocus()
            if self._risultato_pronto_per_conferma and focused is self._btn_vai:
                self._on_vai_al_risultato(None)
            elif (
                self._no_risultati
                and focused is self._input_ctrl
                and self._input_ctrl.GetValue().strip() == self._ultimo_numero_cercato
            ):
                self.EndModal(wx.ID_CANCEL)
            else:
                self._on_cerca(None)
        elif key == wx.WXK_ESCAPE:
            self.EndModal(wx.ID_CANCEL)
        else:
            event.Skip()

    # ------------------------------------------------------------------
    # Ricerca
    # ------------------------------------------------------------------

    def _on_cerca(self, event: object) -> None:
        # Reset stato conferma a ogni nuova ricerca
        self._primo_risultato = None
        self._risultato_pronto_per_conferma = False
        self._no_risultati = False
        self._ultimo_numero_cercato = ""
        self._btn_vai.Disable()

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

        testo_risultato = getattr(self._renderer, "_ultimo_annuncio", "")
        if not testo_risultato and esito is not None:
            testo_risultato = str(esito)
        self._lbl_risultato.SetLabel(testo_risultato)

        from bingo_game.events.eventi_output_ui_umani import EventoRicercaNumeroInCartelle
        evento_ricerca = esito.evento if hasattr(esito, "evento") else None
        if isinstance(evento_ricerca, EventoRicercaNumeroInCartelle) and evento_ricerca.esito == "trovato":
            if not evento_ricerca.risultati:
                self._input_ctrl.SetFocus()
                return
            self._primo_risultato = evento_ricerca.risultati[0]
            self._risultato_pronto_per_conferma = True
            self._btn_vai.Enable()
            self._btn_vai.SetFocus()
        else:
            self._ultimo_numero_cercato = testo
            self._no_risultati = True
            self._input_ctrl.SetFocus()

    def _on_vai_al_risultato(self, event: object) -> None:
        self.EndModal(wx.ID_OK)
