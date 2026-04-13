"""
Dialog modale con elenco statico dei tasti rapidi della partita.

Apertura: Ctrl+H da FinestraGioco.
Chiusura: Escape oppure pulsante Chiudi (entrambi chiamano EndModal).
Focus iniziale: wx.TextCtrl multilinea read-only (navigabile con frecce da NVDA).
Focus alla chiusura: ripristinato su PannelloGriglia da FinestraGioco.

path: bingo_game/ui/finestra_aiuto_tasti_rapidi.py
"""
from __future__ import annotations

import wx

_CONTENUTO_TASTI_RAPIDI = """\
TASTI RAPIDI — TOMBOLA STARK
=============================

Premere Tab per passare al pulsante Chiudi.
Premere Escape per chiudere questa finestra.

------------------------------
CATEGORIA A — navigazione nella cartella
(richiedono il focus sulla griglia di gioco)
------------------------------

Freccia su             — riga precedente
Freccia giu            — riga successiva
Freccia sinistra       — colonna a sinistra
Freccia destra         — colonna a destra
Alt+Freccia su         — navigazione avanzata riga precedente
Alt+Freccia giu        — navigazione avanzata riga successiva
Alt+Freccia sinistra   — navigazione avanzata colonna a sinistra
Alt+Freccia destra     — navigazione avanzata colonna a destra
1..9                   — vai direttamente alla colonna indicata
Alt+1..3               — vai direttamente alla riga indicata
Ctrl+1..6              — salta alla cartella indicata
Tab                    — passa al controllo successivo della finestra
Shift+Tab              — passa al controllo precedente della finestra
Escape                 — esci dalla griglia, focus al pulsante principale
Spazio                 — segna il numero attualmente in focus
F1                     — dichiara ambo
F2                     — dichiara terno
F3                     — dichiara quaterna
F4                     — dichiara cinquina
F5                     — dichiara tombola
F6                     — ripeti ultimo annuncio vocale
R                      — riepilogo rapido cartella corrente
A                      — lettura avanzata posizione corrente
S                      — stato focus corrente
V                      — visualizzazione semplice della cartella
Shift+V                — visualizzazione avanzata della cartella
Shift+Ctrl+V           — visualizzazione avanzata di tutte le cartelle

------------------------------
CATEGORIA B — azioni globali
------------------------------

Ctrl+Enter             — passa turno (equivale al pulsante principale)
Ctrl+F                 — apri ricerca numero nelle cartelle
Ctrl+P                 — metti in pausa oppure riprendi il gioco

------------------------------
CATEGORIA C — informazioni e consultazione
------------------------------

Ctrl+T                 — ultimo numero estratto
Ctrl+L                 — lista completa numeri estratti
Ctrl+U                 — ultimi 5 numeri estratti
Ctrl+R                 — riepilogo tabellone
Ctrl+E                 — consulta cronologia annunci
Ctrl+G                 — stato premi sintetico (ultima vittoria e prossimo)
Ctrl+I                 — dettaglio premi completo (lista vincitori)
Ctrl+H                 — apri questa guida ai tasti rapidi
Ctrl+Shift+H           — apri la guida alle regole del gioco

------------------------------
NOTA: i tasti Categoria A sono attivi solo quando il focus e sulla griglia.
I tasti Categoria B e C sono attivi da qualsiasi punto della finestra di gioco.
"""


class FinestraAiutoTastiRapidi(wx.Dialog):
    """Dialog modale read-only con elenco dei tasti rapidi di gioco."""

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(
            parent,
            title="Tasti rapidi",
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self._build_ui()
        self.Bind(wx.EVT_SHOW, self._on_show)

    def _build_ui(self) -> None:
        sizer = wx.BoxSizer(wx.VERTICAL)

        self._testo = wx.TextCtrl(
            self,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
            size=wx.Size(560, 400),
        )
        self._testo.SetValue(_CONTENUTO_TASTI_RAPIDI)
        sizer.Add(self._testo, 1, wx.ALL | wx.EXPAND, 10)

        btn_sizer = wx.StdDialogButtonSizer()
        self._btn_chiudi = wx.Button(self, id=wx.ID_CANCEL, label="Chiudi")
        btn_sizer.AddButton(self._btn_chiudi)
        btn_sizer.Realize()
        sizer.Add(btn_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 6)

        self.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_BUTTON, self._on_chiudi, self._btn_chiudi)

    def _on_show(self, event: wx.ShowEvent) -> None:
        if event.IsShown():
            self._testo.SetFocus()
        event.Skip()

    def _on_chiudi(self, event: wx.CommandEvent) -> None:  # noqa: ARG002
        self.EndModal(wx.ID_CANCEL)
