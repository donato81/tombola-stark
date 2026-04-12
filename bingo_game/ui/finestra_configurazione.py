"""
Finestra di configurazione partita — wxPython accessibile.

Raccoglie nome giocatore, numero bot e numero cartelle.
Delega la creazione e l'avvio della partita a ComandiSistema.
Non introduce logica di dominio: è un puro bordo di presentazione.

path: bingo_game/ui/finestra_configurazione.py
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import wx

from bingo_game.ui.tema import (
    COLORE_ACCENT_BLU,
    COLORE_BTN_INIZIA,
    COLORE_CONFIGURAZIONE_BG,
    COLORE_TESTO_CHIARO,
    COLORE_TESTO_ERRORE,
    COLORE_TESTO_LABEL,
    DIMENSIONE_FINESTRA_CONFIGURAZIONE,
    FONT_BTN_PT,
    FONT_LABEL_PT,
)
from bingo_game.comandi_partita import ComandiSistema

if TYPE_CHECKING:
    from bingo_game.ui.renderers.renderer_wx import WxRenderer

_ui_logger = logging.getLogger("ui")


class FinestraConfigurazione(wx.Frame):
    """
    Frame di configurazione partita.

    Controlli minimi: nome giocatore, numero bot (1-7), cartelle per giocatore (1-6).
    Il focus iniziale è posizionato sul primo campo utile (nome).
    La conferma delega a ComandiSistema e apre FinestraGioco in caso di successo.
    """

    def __init__(
        self,
        renderer: "WxRenderer",
        parent: Optional[wx.Window] = None,
        parent_frame: Optional[wx.Frame] = None,
    ) -> None:
        super().__init__(
            parent,
            title="Tombola Stark — Configurazione partita",
            size=DIMENSIONE_FINESTRA_CONFIGURAZIONE,
            style=wx.DEFAULT_FRAME_STYLE,
        )
        self._renderer = renderer
        self._parent_frame = parent_frame
        self._comandi_sistema = ComandiSistema()
        self._build_ui()
        self._bind_events()
        self.Centre()
        # Aggiorna il renderer sul frame corrente
        self._renderer.aggiorna_finestra(self)

    # ------------------------------------------------------------------
    # Costruzione UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(COLORE_CONFIGURAZIONE_BG))
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Titolo visivo
        lbl_titolo = wx.StaticText(panel, label="Configurazione partita")
        lbl_titolo.SetFont(
            wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        lbl_titolo.SetForegroundColour(wx.Colour(COLORE_ACCENT_BLU))
        sizer.Add(lbl_titolo, 0, wx.TOP | wx.ALIGN_CENTER_HORIZONTAL, 15)

        # Nome giocatore
        lbl_nome = wx.StaticText(panel, label="Nome giocatore:")
        lbl_nome.SetFont(
            wx.Font(FONT_LABEL_PT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        )
        lbl_nome.SetForegroundColour(wx.Colour(COLORE_TESTO_LABEL))
        sizer.Add(lbl_nome, 0, wx.LEFT | wx.TOP, 10)
        self._nome_ctrl = wx.TextCtrl(panel, value="Giocatore")
        sizer.Add(self._nome_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Numero bot
        lbl_bot = wx.StaticText(panel, label="Numero bot avversari (1-7):")
        lbl_bot.SetFont(
            wx.Font(FONT_LABEL_PT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        )
        lbl_bot.SetForegroundColour(wx.Colour(COLORE_TESTO_LABEL))
        sizer.Add(lbl_bot, 0, wx.LEFT | wx.TOP, 10)
        self._bot_ctrl = wx.Choice(panel, choices=["1", "2", "3", "4", "5", "6", "7"])
        self._bot_ctrl.SetSelection(0)
        sizer.Add(self._bot_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Numero cartelle
        lbl_cartelle = wx.StaticText(panel, label="Cartelle per giocatore (1-6):")
        lbl_cartelle.SetFont(
            wx.Font(FONT_LABEL_PT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        )
        lbl_cartelle.SetForegroundColour(wx.Colour(COLORE_TESTO_LABEL))
        sizer.Add(lbl_cartelle, 0, wx.LEFT | wx.TOP, 10)
        self._cartelle_ctrl = wx.Choice(panel, choices=["1", "2", "3", "4", "5", "6"])
        self._cartelle_ctrl.SetSelection(0)
        sizer.Add(self._cartelle_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Durata finestra d'azione (V2)
        lbl_fa = wx.StaticText(panel, label="Durata finestra d'azione in secondi (5-300):")
        lbl_fa.SetFont(
            wx.Font(FONT_LABEL_PT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        )
        lbl_fa.SetForegroundColour(wx.Colour(COLORE_TESTO_LABEL))
        sizer.Add(lbl_fa, 0, wx.LEFT | wx.TOP, 10)
        self._finestra_azione_ctrl = wx.SpinCtrl(panel, value="60", min=5, max=300)
        sizer.Add(self._finestra_azione_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Durata pausa tra turni (V2)
        lbl_p = wx.StaticText(panel, label="Durata pausa tra turni in secondi (1-30):")
        lbl_p.SetFont(
            wx.Font(FONT_LABEL_PT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        )
        lbl_p.SetForegroundColour(wx.Colour(COLORE_TESTO_LABEL))
        sizer.Add(lbl_p, 0, wx.LEFT | wx.TOP, 10)
        self._pausa_turni_ctrl = wx.SpinCtrl(panel, value="5", min=1, max=30)
        sizer.Add(self._pausa_turni_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Pulsante conferma
        self._btn_conferma = wx.Button(panel, label="Avvia partita")
        self._btn_conferma.SetBackgroundColour(wx.Colour(COLORE_BTN_INIZIA))
        self._btn_conferma.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._btn_conferma.SetFont(
            wx.Font(FONT_BTN_PT, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        self._btn_conferma.SetMinSize((200, 44))
        sizer.Add(self._btn_conferma, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        # Riga messaggi errori
        self._msg_ctrl = wx.StaticText(panel, label="")
        self._msg_ctrl.SetFont(
            wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        )
        self._msg_ctrl.SetForegroundColour(wx.Colour(COLORE_TESTO_ERRORE))
        sizer.Add(self._msg_ctrl, 0, wx.LEFT | wx.BOTTOM, 10)

        panel.SetSizer(sizer)
        panel.Layout()

        # Focus iniziale sul primo campo utile
        self._nome_ctrl.SetFocus()

    # ------------------------------------------------------------------
    # Binding eventi
    # ------------------------------------------------------------------

    def _bind_events(self) -> None:
        self._btn_conferma.Bind(wx.EVT_BUTTON, self._on_conferma)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        if event.GetKeyCode() == wx.WXK_RETURN:
            self._on_conferma(None)
        else:
            event.Skip()

    # ------------------------------------------------------------------
    # Azione conferma
    # ------------------------------------------------------------------

    def _on_conferma(self, event: Optional[wx.CommandEvent]) -> None:
        nome = self._nome_ctrl.GetValue().strip()
        if not nome:
            self._mostra_errore("Inserisci un nome per il giocatore.")
            self._nome_ctrl.SetFocus()
            return

        num_bot = int(self._bot_ctrl.GetString(self._bot_ctrl.GetSelection()))
        num_cartelle = int(self._cartelle_ctrl.GetString(self._cartelle_ctrl.GetSelection()))

        _ui_logger.debug(
            "Configurazione: nome=%s bot=%d cartelle=%d",
            nome, num_bot, num_cartelle,
        )

        partita = self._comandi_sistema.crea_nuova_partita(
            nome_umano=nome,
            num_cartelle_umano=num_cartelle,
            num_bot=num_bot,
        )
        if partita is None:
            self._mostra_errore(
                "Impossibile creare la partita. Verifica i parametri e riprova."
            )
            return

        successo = self._comandi_sistema.avvia_partita(partita)
        if not successo:
            self._mostra_errore("Impossibile avviare la partita.")
            return

        durata_finestra_ms = self._finestra_azione_ctrl.GetValue() * 1000
        durata_pausa_ms = self._pausa_turni_ctrl.GetValue() * 1000

        _ui_logger.debug(
            "Configurazione V2: durata_finestra=%dms durata_pausa=%dms",
            durata_finestra_ms, durata_pausa_ms,
        )

        # Apri finestra di gioco e nascondi questa
        from bingo_game.ui.finestra_gioco import FinestraGioco

        finestra_gioco = FinestraGioco(
            partita=partita,
            renderer=self._renderer,
            parent=None,
            durata_finestra_ms=durata_finestra_ms,
            durata_pausa_ms=durata_pausa_ms,
            finestra_principale=self._parent_frame,
        )
        finestra_gioco.Show()
        self.Hide()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def mostra_testo(self, testo: str) -> None:
        """Interfaccia per il renderer: aggiorna il campo messaggi."""
        self._msg_ctrl.SetLabel(testo[:200])

    def _mostra_errore(self, testo: str) -> None:
        self._msg_ctrl.SetLabel(testo)
        self._renderer.mostra_messaggio_sistema(testo)
