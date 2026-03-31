"""
Finestra di gioco principale — wxPython accessibile.

Ospita:
- PannelloGriglia: pannello focalizzabile con binding Categoria A.
- Pulsante principale a due stati (Inizia partita / Passa turno).
- Area log annunci consultabile (Ctrl+E).
- Binding Categoria B e C via EVT_CHAR_HOOK sulla finestra.

Binding tastiera applicati (da report analisi):
  Categoria A — EVT_KEY_DOWN sul pannello griglia:
    Frecce su/giu          -> riga semplice
    Frecce sx/dx           -> colonna sinistra/destra semplice
        1..9                   -> vai a colonna diretta
    Spazio                 -> segna numero
        R                      -> riepilogo cartella corrente
    V                      -> visualizza semplice
    Shift+V                -> visualizza avanzata
    Shift+Ctrl+V           -> visualizza tutte avanzata
    S                      -> stato focus
    F1..F5                 -> dichiara vittoria (ambo/terno/quaterna/cinquina/tombola)
    F6                     -> ripeti ultimo annuncio
    Escape                 -> esci dalla griglia (focus a pulsante)

  Categoria B — EVT_CHAR_HOOK sul frame (Skip=False per bloccare propagazione):
    Ctrl+P                 -> passa turno
    Ctrl+F                 -> apre dialog ricerca numero
    Ctrl+1..6              -> salta a cartella N
        Alt+1..3               -> salta a riga N

  Categoria C — EVT_CHAR_HOOK (da verificare empiricamente su NVDA):
    Ctrl+T                 -> ultimo numero estratto
    Ctrl+L                 -> lista numeri estratti
    Ctrl+U                 -> ultimi 5 estratti
    Ctrl+R                 -> riepilogo tabellone
    Ctrl+E                 -> consulta log annunci

path: bingo_game/ui/finestra_gioco.py
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import wx

from bingo_game.comandi_partita import ComandiSistema, ComandiGiocatoreUmano
from bingo_game.partita import Partita

if TYPE_CHECKING:
    from bingo_game.ui.renderers.renderer_wx import WxRenderer

_ui_logger = logging.getLogger("ui")

_TIPI_VITTORIA = ["ambo", "terno", "quaterna", "cinquina", "tombola"]


class PannelloGriglia(wx.Panel):
    """
    Pannello focalizzabile che funge da centro della navigazione tastiera.

    Cattura i tasti Categoria A (navigazione, segnazione, vittorie).
    Il focus entra automaticamente all'apertura della finestra.
    Escape sposta il focus al pulsante principale.
    """

    def __init__(self, parent: wx.Window, finestra: "FinestraGioco") -> None:
        super().__init__(parent, style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL)
        self._finestra = finestra
        # Etichetta accessibile per screen reader
        self.SetName("Griglia cartella")
        self._build_ui()
        self._bind_keys()

    def _build_ui(self) -> None:
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._etichetta = wx.StaticText(
            self,
            label="Pannello griglia. Usa i tasti freccia per navigare.",
        )
        sizer.Add(self._etichetta, 1, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

    def mostra_testo(self, testo: str) -> None:
        """Aggiorna l'etichetta di stato visibile nel pannello griglia."""
        self._etichetta.SetLabel(testo[:500])

    def _bind_keys(self) -> None:
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

    def _on_key_down(self, event: wx.KeyEvent) -> None:
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        shift = event.ShiftDown()
        alt = event.AltDown()
        fg = self._finestra

        # Escape — esci dalla griglia
        if key == wx.WXK_ESCAPE:
            fg._btn_principale.SetFocus()
            return

        # Frecce su/giu
        if key == wx.WXK_UP:
            if shift:
                event.Skip()
                return
            fg._dispatch(fg._comandi.riga_su())
            return

        if key == wx.WXK_DOWN:
            if shift:
                event.Skip()
                return
            fg._dispatch(fg._comandi.riga_giu())
            return

        # Frecce sinistra/destra
        if key == wx.WXK_LEFT:
            if shift:
                event.Skip()
                return
            fg._dispatch(fg._comandi.colonna_sinistra())
            return

        if key == wx.WXK_RIGHT:
            if shift:
                event.Skip()
                return
            fg._dispatch(fg._comandi.colonna_destra())
            return

        # Tasti 1..9 — vai a colonna diretta
        if ord("1") <= key <= ord("9") and not ctrl and not shift and not alt:
            numero_colonna = key - ord("0")
            fg._dispatch(fg._comandi.vai_a_colonna(numero_colonna))
            return

        # Spazio — segna numero
        if key == wx.WXK_SPACE:
            numero_corrente = fg._ottieni_numero_in_focus()
            if numero_corrente is not None:
                fg._dispatch(fg._comandi.segna_numero(numero_corrente))
            return

        # V / Shift+V / Shift+Ctrl+V — visualizzazione
        if key == ord("V"):
            if shift and ctrl:
                fg._dispatch(fg._comandi.visualizza_tutte_avanzate())
            elif shift:
                fg._dispatch(fg._comandi.visualizza_avanzata())
            else:
                fg._dispatch(fg._comandi.visualizza_semplice())
            return

        # S — stato focus
        if key == ord("S") and not ctrl and not shift:
            fg._dispatch(fg._comandi.stato_focus())
            return

        # R — riepilogo rapido cartella corrente
        if key == ord("R") and not ctrl and not shift and not alt:
            fg._dispatch(fg._comandi.riepilogo_cartella_corrente())
            return

        # F1..F5 — dichiara vittoria
        if wx.WXK_F1 <= key <= wx.WXK_F5 and not ctrl and not shift:
            indice = key - wx.WXK_F1  # 0..4
            tipo = _TIPI_VITTORIA[indice]
            fg._dispatch(fg._comandi.annuncia_vittoria(tipo, fg._turno_corrente))
            return

        # F6 — ripeti ultimo annuncio
        if key == wx.WXK_F6 and not ctrl and not shift:
            fg._finestra._renderer.ripeti_ultimo_annuncio()
            return

        event.Skip()


class FinestraGioco(wx.Frame):
    """
    Frame principale del gioco.

    Contiene pannello griglia, pulsante principale a due stati e log annunci.
    Coordina il ciclo di gioco tramite ComandiSistema e ComandiGiocatoreUmano.
    """

    def __init__(
        self,
        partita: Partita,
        renderer: "WxRenderer",
        parent: Optional[wx.Window] = None,
    ) -> None:
        super().__init__(
            parent,
            title="Tombola Stark — In gioco",
            size=(700, 500),
            style=wx.DEFAULT_FRAME_STYLE,
        )
        self._partita = partita
        self._renderer = renderer
        self._comandi_sistema = ComandiSistema()
        self._comandi = ComandiGiocatoreUmano(partita)
        self._turno_corrente: int = 0

        self._build_ui()
        self._bind_finestra()
        self.Centre()

        # Aggiorna il renderer sul frame corrente e sul widget log
        self._renderer.aggiorna_finestra(self)
        self._renderer.imposta_widget_log(self._log_ctrl)

        # Focus iniziale sulla griglia
        self._pannello_griglia.SetFocus()

    # ------------------------------------------------------------------
    # Costruzione UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Pulsante principale a due stati
        self._btn_principale = wx.Button(panel, label="Inizia partita")
        sizer.Add(self._btn_principale, 0, wx.ALL | wx.EXPAND, 5)

        # Pannello griglia
        self._pannello_griglia = PannelloGriglia(panel, self)
        sizer.Add(self._pannello_griglia, 1, wx.ALL | wx.EXPAND, 5)

        # Area log annunci (read-only)
        sizer.Add(wx.StaticText(panel, label="Log annunci (Ctrl+E per consultare):"), 0, wx.LEFT | wx.TOP, 5)
        self._log_ctrl = wx.TextCtrl(
            panel,
                style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(-1, 120),
        )
        sizer.Add(self._log_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)
        panel.Layout()

        self._btn_principale.Bind(wx.EVT_BUTTON, self._on_pulsante_principale)

    # ------------------------------------------------------------------
    # Binding finestra (Categoria B e C)
    # ------------------------------------------------------------------

    def _bind_finestra(self) -> None:
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        alt = event.AltDown()
        shift = event.ShiftDown()

        # Categoria B — blocca propagazione

        # Shift+Frecce: intercettate a livello frame per evitare che
        # Windows/NVDA consumino il gesto prima del pannello griglia.
        if shift and not ctrl and not alt:
            if key == wx.WXK_UP:
                self._dispatch(self._comandi.riga_su_avanzata())
                return
            if key == wx.WXK_DOWN:
                self._dispatch(self._comandi.riga_giu_avanzata())
                return
            if key == wx.WXK_LEFT:
                self._dispatch(self._comandi.colonna_sinistra_avanzata())
                return
            if key == wx.WXK_RIGHT:
                self._dispatch(self._comandi.colonna_destra_avanzata())
                return

        # Ctrl+P — passa turno
        if ctrl and key == ord("P"):
            self._on_pulsante_principale(None)
            return

        # Ctrl+F — ricerca numero
        if ctrl and key == ord("F"):
            self._apri_ricerca_numero()
            return

        # Ctrl+1..6 — salta a cartella N
        if ctrl and not shift and ord("1") <= key <= ord("6"):
            numero = key - ord("0")
            self._dispatch(self._comandi.imposta_focus_cartella(numero))
            return

        # Alt+1..3 — salta a riga N
        if alt and not ctrl and not shift and ord("1") <= key <= ord("3"):
            numero = key - ord("0")
            self._dispatch(self._comandi.vai_a_riga(numero))
            return

        # Categoria C — da verificare empiricamente su NVDA

        # Ctrl+T — ultimo numero estratto  [NVDA-VERIFY: potenziale conflitto]
        if ctrl and key == ord("T"):
            self._dispatch(self._comandi.ultimo_numero_estratto())
            return

        # Ctrl+L — lista numeri estratti  [NVDA-VERIFY: potenziale conflitto]
        if ctrl and key == ord("L"):
            self._dispatch(self._comandi.lista_numeri_estratti())
            return

        # Ctrl+U — ultimi 5 estratti  [NVDA-VERIFY: potenziale conflitto]
        if ctrl and key == ord("U"):
            self._dispatch(self._comandi.ultimi_numeri_estratti())
            return

        # Ctrl+R — riepilogo tabellone  [NVDA-VERIFY: potenziale conflitto]
        if ctrl and key == ord("R"):
            self._dispatch(self._comandi.riepilogo_tabellone())
            return

        # Ctrl+E — consulta log annunci
        if ctrl and key == ord("E"):
            self._consulta_log()
            return

        event.Skip()

    # ------------------------------------------------------------------
    # Azione pulsante principale
    # ------------------------------------------------------------------

    def _on_pulsante_principale(self, event: object) -> None:
        if self._comandi_sistema.is_terminata(self._partita):
            self._renderer.mostra_messaggio_sistema("La partita è terminata.")
            return

        risultato = self._comandi_sistema.esegui_turno(self._partita)
        if risultato is None:
            self._renderer.mostra_messaggio_sistema(
                "Impossibile eseguire il turno. La partita potrebbe essere terminata."
            )
            return

        self._turno_corrente += 1
        self._annuncia_risultato_turno(risultato)
        self._aggiorna_stato_pulsante()

        if risultato.get("partita_terminata") or risultato.get("tombola_rilevata"):
            self._renderer.mostra_messaggio_sistema("La partita è terminata.")
            self._btn_principale.Disable()

    # ------------------------------------------------------------------
    # Consultazione log  
    # ------------------------------------------------------------------

    def _consulta_log(self) -> None:
        """Porta il focus all'area log annunci e la vocalizza."""
        self._log_ctrl.SetFocus()
        contenuto = self._log_ctrl.GetValue()
        if contenuto.strip():
            self._renderer.mostra_messaggio_sistema("Consultazione log annunci.")
        else:
            self._renderer.mostra_messaggio_sistema("Log annunci vuoto.")

    # ------------------------------------------------------------------
    # Interfaccia per il renderer (duck typing)
    # ------------------------------------------------------------------

    def mostra_testo(self, testo: str) -> None:
        """Interfaccia per il renderer: aggiorna il pannello griglia."""
        self._pannello_griglia.mostra_testo(testo)

    def aggiungi_a_log(self, testo: str) -> None:
        """Interfaccia per il renderer: aggiunge riga al log annunci."""
        if self._log_ctrl:
            self._log_ctrl.AppendText(testo + "\n")

    def aggiorna_stato_pulsante(self, primo_turno_eseguito: bool) -> None:
        """Interfaccia per il renderer: aggiorna etichetta pulsante."""
        if primo_turno_eseguito:
            self._btn_principale.SetLabel("Passa turno")
        else:
            self._btn_principale.SetLabel("Inizia partita")

    # ------------------------------------------------------------------
    # Helper interni
    # ------------------------------------------------------------------

    def _dispatch(self, esito: object) -> None:
        """Delega l'esito al renderer per visualizzazione e vocalizzazione."""
        # EsitoAzione è importato lazy per evitare import circolari
        from bingo_game.events.eventi import EsitoAzione
        if isinstance(esito, EsitoAzione):
            self._renderer.render_esito(esito)

    def _aggiorna_stato_pulsante(self) -> None:
        primo_turno_eseguito = (
            self._partita.tabellone.get_conteggio_estratti() > 0
        )
        self.aggiorna_stato_pulsante(primo_turno_eseguito)

    def _annuncia_risultato_turno(self, risultato: dict) -> None:
        """Costruisce e vocalizza il messaggio riassuntivo del turno."""
        numero = risultato.get("numero_estratto", "?")
        premi_nuovi = risultato.get("premi_nuovi", [])

        testo = f"Turno {self._turno_corrente}. Numero estratto: {numero}."
        if premi_nuovi:
            testo += f" Premi: {', '.join(str(p) for p in premi_nuovi)}."
        self._renderer.mostra_messaggio_sistema(testo)

    def _apri_ricerca_numero(self) -> None:
        """Apre il dialog modale di ricerca numero."""
        from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
        dlg = DialogoRicercaNumero(
            parent=self,
            renderer=self._renderer,
            comandi=self._comandi,
        )
        dlg.ShowModal()
        dlg.Destroy()
        # Ripristina focus sulla griglia
        self._pannello_griglia.SetFocus()

    def _ottieni_numero_in_focus(self) -> Optional[int]:
        """
        Restituisce il numero correntemente in focus per la segnazione.

        Il renderer mantiene _numero_in_focus aggiornato durante la navigazione.
        Se non disponibile vocalizza un messaggio di diagnostica.
        """
        numero = getattr(self._renderer, "numero_in_focus", None)
        if numero is not None:
            return numero
        self._renderer.mostra_messaggio_sistema(
            "Nessun numero in focus. Naviga su una cella prima di segnare."
        )
        return None
