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
            size=(500, 430),
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
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Nome giocatore
        sizer.Add(wx.StaticText(panel, label="Nome giocatore:"), 0, wx.LEFT | wx.TOP, 10)
        self._nome_ctrl = wx.TextCtrl(panel, value="Giocatore")
        sizer.Add(self._nome_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Numero bot
        sizer.Add(wx.StaticText(panel, label="Numero bot avversari (1-7):"), 0, wx.LEFT | wx.TOP, 10)
        self._bot_ctrl = wx.SpinCtrl(panel, value="1", min=1, max=7)
        sizer.Add(self._bot_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Numero cartelle
        sizer.Add(wx.StaticText(panel, label="Cartelle per giocatore (1-6):"), 0, wx.LEFT | wx.TOP, 10)
        self._cartelle_ctrl = wx.SpinCtrl(panel, value="1", min=1, max=6)
        sizer.Add(self._cartelle_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Durata finestra d'azione (V2)
        sizer.Add(
            wx.StaticText(panel, label="Durata finestra d'azione in secondi (5-300):"),
            0, wx.LEFT | wx.TOP, 10,
        )
        self._finestra_azione_ctrl = wx.SpinCtrl(panel, value="60", min=5, max=300)
        sizer.Add(self._finestra_azione_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Durata pausa tra turni (V2)
        sizer.Add(
            wx.StaticText(panel, label="Durata pausa tra turni in secondi (1-30):"),
            0, wx.LEFT | wx.TOP, 10,
        )
        self._pausa_turni_ctrl = wx.SpinCtrl(panel, value="5", min=1, max=30)
        sizer.Add(self._pausa_turni_ctrl, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Pulsante conferma
        self._btn_conferma = wx.Button(panel, label="Avvia partita")
        sizer.Add(self._btn_conferma, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        # Riga messaggi errori
        self._msg_ctrl = wx.StaticText(panel, label="")
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

        num_bot = self._bot_ctrl.GetValue()
        num_cartelle = self._cartelle_ctrl.GetValue()

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
