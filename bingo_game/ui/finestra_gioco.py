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
    Alt+Frecce             -> navigazione avanzata riga/colonna
        1..9                   -> vai a colonna diretta
    Spazio                 -> segna numero
        R                      -> riepilogo cartella corrente
    A                      -> lettura avanzata posizione corrente (riga o colonna)
    V                      -> visualizza semplice
    Shift+V                -> visualizza avanzata
    Shift+Ctrl+V           -> visualizza tutte avanzata
    S                      -> stato focus
    F1..F5                 -> dichiara vittoria (ambo/terno/quaterna/cinquina/tombola)
    F6                     -> ripeti ultimo annuncio
    Escape                 -> esci dalla griglia (focus a pulsante)

  Categoria B — EVT_CHAR_HOOK sul frame (Skip=False per bloccare propagazione):
    Ctrl+Enter             -> passa turno
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

import functools
import logging
import random
import time
from typing import TYPE_CHECKING, Any, Optional

import wx

from bingo_game.ui.tema import (
    COLORE_CELLA_VUOTA, COLORE_CELLA_TESTO_INATTIVO,
    COLORE_CELLA_ESTRATTO, COLORE_TESTO_CHIARO,
    COLORE_CELLA_CARTELLA_VUOTA, COLORE_CELLA_CARTELLA_NUMERO,
    COLORE_CELLA_SEGNATA, COLORE_CELLA_ESTRATTA_NON_SEGNATA,
    COLORE_TESTO_SCURO,
    COLORE_ACCENT_BLU, COLORE_ACCENT_ROSSO,
    COLORE_BTN_TOMBOLA, COLORE_BTN_TOMBOLA_TESTO, COLORE_BTN_NEUTRO,
    FONT_CARTELLA_NUMERO_PT,
    DIMENSIONE_FINESTRA_GIOCO,
    DIMENSIONE_CELLA_TABELLONE, DIMENSIONE_CELLA_CARTELLA,
    DIMENSIONE_BTN_FRECCIA, DIMENSIONE_BTN_SELEZIONE_CARTELLA,
)

from bingo_game.comandi_partita import ComandiSistema, ComandiGiocatoreUmano
from bingo_game.partita import Partita

if TYPE_CHECKING:
    from bingo_game.ui.renderers.renderer_wx import WxRenderer

_ui_logger = logging.getLogger("ui")

_TIPI_VITTORIA = ["ambo", "terno", "quaterna", "cinquina", "tombola"]
# WXK_RETURN = 13 in tutte le versioni wx; getattr per robustezza in ambienti stub
_KEY_RETURN: int = getattr(wx, "WXK_RETURN", 13)
# Tasti funzione — getattr per robustezza in ambienti di test con stub wx parziale
_KEY_F1: int = getattr(wx, "WXK_F1", 340)
_KEY_F5: int = getattr(wx, "WXK_F5", 344)
_KEY_F6: int = getattr(wx, "WXK_F6", 345)


class PannelloTabellone(wx.Panel):
    """
    Griglia visiva 9 colonne × 10 righe del tabellone (numeri 1-90).

    Puramente visiva e non focalizzabile. Ogni colonna raggruppa una decina.
    Dati statici placeholder: aggiornamento dinamico in fase successiva.
    """

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, style=wx.NO_BORDER)
        # Rimuove TAB_TRAVERSAL: il pannello non partecipa al ciclo focus
        self.SetWindowStyleFlag(self.GetWindowStyleFlag() & ~wx.TAB_TRAVERSAL)
        self._build_ui()

    def _build_ui(self) -> None:
        font = wx.Font(
            FONT_CARTELLA_NUMERO_PT,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        self._celle: dict[int, wx.StaticText] = {}
        sizer = wx.GridSizer(rows=10, cols=9, vgap=1, hgap=1)
        for row in range(10):
            for col in range(9):
                numero = col * 10 + row + 1  # 1..90; ogni colonna raggruppa una decina
                cell = wx.StaticText(
                    self, label=str(numero), style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
                )
                cell.SetMinSize(wx.Size(*DIMENSIONE_CELLA_TABELLONE))
                cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_VUOTA))
                cell.SetForegroundColour(wx.Colour(COLORE_CELLA_TESTO_INATTIVO))
                cell.SetFont(font)
                sizer.Add(cell, 1, wx.EXPAND)
                self._celle[numero] = cell
        self.SetSizer(sizer)

    def aggiorna(self, numeri_estratti: set) -> None:
        """Ridipinge le celle secondo i numeri già estratti."""
        for numero, cell in self._celle.items():
            if numero in numeri_estratti:
                cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_ESTRATTO))
                cell.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
            else:
                cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_VUOTA))
                cell.SetForegroundColour(wx.Colour(COLORE_CELLA_TESTO_INATTIVO))
        self.Refresh()


class PannelloCartella(wx.Panel):
    """
    Griglia visiva 9 colonne × 3 righe per una cartella (15 numeri).

    Puramente visiva e non focalizzabile. Celle vuote e celle con numero
    usano colori distinti da tema.py. Dati statici placeholder.
    """

    def __init__(self, parent: wx.Window) -> None:
        super().__init__(parent, style=wx.NO_BORDER)
        # Rimuove TAB_TRAVERSAL: il pannello non partecipa al ciclo focus
        self.SetWindowStyleFlag(self.GetWindowStyleFlag() & ~wx.TAB_TRAVERSAL)
        self._build_ui()

    def _build_ui(self) -> None:
        font = wx.Font(
            FONT_CARTELLA_NUMERO_PT,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
        )
        self._celle: list[list[wx.StaticText]] = []
        sizer = wx.GridSizer(rows=3, cols=9, vgap=2, hgap=2)
        for row in range(3):
            riga: list[wx.StaticText] = []
            for col in range(9):
                cell = wx.StaticText(
                    self, label="", style=wx.ALIGN_CENTER | wx.ST_NO_AUTORESIZE
                )
                cell.SetMinSize(wx.Size(*DIMENSIONE_CELLA_CARTELLA))
                cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_CARTELLA_VUOTA))
                cell.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
                cell.SetFont(font)
                sizer.Add(cell, 1, wx.EXPAND)
                riga.append(cell)
            self._celle.append(riga)
        self.SetSizer(sizer)

    def aggiorna(
        self,
        griglia: tuple,
        numeri_segnati: set,
        numeri_estratti: set,
    ) -> None:
        """Ridipinge la cartella con i colori semantici correnti.

        griglia: restituita da Cartella.get_griglia_semplice() —
                 "-" per cella vuota, int per numero.
        numeri_segnati: set dei numeri già segnati sul questa cartella.
        numeri_estratti: set dei numeri già usciti dal tabellone.
        """
        for row in range(3):
            for col in range(9):
                val = griglia[row][col]
                cell = self._celle[row][col]
                if isinstance(val, str):            # cella vuota ("-")
                    cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_CARTELLA_VUOTA))
                    cell.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
                    cell.SetLabel("")
                elif val in numeri_segnati:          # numero segnato
                    cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_SEGNATA))
                    cell.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
                    cell.SetLabel(str(val))
                elif val in numeri_estratti:         # estratto non segnato
                    cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_ESTRATTA_NON_SEGNATA))
                    cell.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
                    cell.SetLabel(str(val))
                else:                               # numero non ancora estratto
                    cell.SetBackgroundColour(wx.Colour(COLORE_CELLA_CARTELLA_NUMERO))
                    cell.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
                    cell.SetLabel(str(val))
        self.Refresh()


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
            fg._dispatch(fg._comandi.riga_su())
            return

        if key == wx.WXK_DOWN:
            fg._dispatch(fg._comandi.riga_giu())
            return

        # Frecce sinistra/destra
        if key == wx.WXK_LEFT:
            fg._dispatch(fg._comandi.colonna_sinistra())
            return

        if key == wx.WXK_RIGHT:
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

        # A — lettura avanzata della riga o colonna corrente senza spostarsi
        if key == ord("A") and not ctrl and not shift and not alt:
            fg._dispatch(fg._comandi.leggi_posizione_avanzata())
            return

        # F1..F5 — dichiara vittoria
        if _KEY_F1 <= key <= _KEY_F5 and not ctrl and not shift:
            indice = key - _KEY_F1  # 0..4
            tipo = _TIPI_VITTORIA[indice]
            fg._dispatch(fg._comandi.annuncia_vittoria(tipo, fg._turno_corrente))
            return

        # F6 — ripeti ultimo annuncio
        if key == _KEY_F6 and not ctrl and not shift:
            fg._renderer.ripeti_ultimo_annuncio()
            return

        # Tab / Shift+Tab — naviga tra controlli della finestra
        # Necessario perche wx.WANTS_CHARS intercetta Tab senza delegarlo
        # al ciclo TAB_TRAVERSAL del framework. Navigate() lo cede correttamente.
        if key == wx.WXK_TAB:
            flags = wx.NavigationKeyEvent.IsForward
            if shift:
                flags = wx.NavigationKeyEvent.IsBackward
            self.Navigate(flags)
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
        durata_finestra_ms: int = 60000,
        durata_pausa_ms: int = 5000,
        finestra_principale: Optional[wx.Frame] = None,
    ) -> None:
        super().__init__(
            parent,
            title="Tombola Stark — In gioco",
            size=DIMENSIONE_FINESTRA_GIOCO,
            style=wx.DEFAULT_FRAME_STYLE,
        )
        self._partita = partita
        self._renderer = renderer
        self._finestra_principale: Optional[wx.Frame] = finestra_principale
        self._comandi_sistema = ComandiSistema()
        self._comandi = ComandiGiocatoreUmano(partita)
        self._turno_corrente: int = 0
        # Stato trifasico UI V2: "attesa_estrazione" -> "attesa_reclami" -> "pausa_turno"
        self._fase_turno_ui: str = "attesa_estrazione"

        # --- Timer e scheduling V2 ---
        self._durata_finestra_ms: int = durata_finestra_ms
        self._durata_pausa_ms: int = durata_pausa_ms
        self._timer_azione: Optional[wx.Timer] = None
        self._timer_pausa: Optional[wx.Timer] = None
        self._tick_ms: int = 500
        self._ms_trascorsi_azione: int = 0
        self._durata_finestra_corrente_ms: int = 0
        self._avvisi_emessi: set[int] = set()

        # --- Stato pausa ---
        self._in_pausa: bool = False
        self._fase_pre_pausa: str = ""
        self._ms_residui_azione: int = 0
        self._ms_residui_pausa: int = 0
        self._avvio_pausa_turno_mono: float = 0.0

        self._build_ui()
        self._bind_finestra()
        self.Centre()

        # Aggiorna il renderer sul frame corrente e sul widget log
        self._renderer.aggiorna_finestra(self)
        self._renderer.imposta_widget_log(self._log_ctrl)

        # Connessione opzionale allo stato partita per aggiornamenti live delle griglie
        if hasattr(self._partita, "subscribe"):
            try:
                self._partita.subscribe(self._on_partita_change)
            except Exception as e:
                _ui_logger.debug("Partita.subscribe non disponibile: %s", e)

        # Focus iniziale sulla griglia
        self._pannello_griglia.SetFocus()
        wx.CallAfter(self._imposta_focus_iniziale)

    # ------------------------------------------------------------------
    # Costruzione UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self._panel = wx.Panel(self)
        panel = self._panel
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Pulsante principale a due stati
        self._btn_principale = wx.Button(panel, label="Inizia partita")
        self._btn_principale.SetName("Pulsante principale partita")
        sizer.Add(self._btn_principale, 0, wx.ALL | wx.EXPAND, 5)

        # Pulsante pausa (disabilitato fino al primo turno)
        self._btn_pausa = wx.Button(panel, label="Metti in pausa")
        self._btn_pausa.SetName("Metti in pausa")
        self._btn_pausa.Disable()
        sizer.Add(self._btn_pausa, 0, wx.ALL | wx.EXPAND, 5)
        self.Bind(wx.EVT_BUTTON, self._on_pausa, self._btn_pausa)

        # Pulsante ritorno al menu (nascosto fino a fine partita)
        self._btn_torna_menu = wx.Button(panel, label="Torna al menu principale")
        self._btn_torna_menu.SetName("Torna al menu principale")
        self._btn_torna_menu.Hide()
        self._btn_torna_menu.Disable()
        sizer.Add(self._btn_torna_menu, 0, wx.ALL | wx.EXPAND, 5)
        self.Bind(wx.EVT_BUTTON, self._on_torna_menu, self._btn_torna_menu)

        # Pannello griglia
        self._pannello_griglia = PannelloGriglia(panel, self)
        sizer.Add(self._pannello_griglia, 1, wx.ALL | wx.EXPAND, 5)

        # Pannelli visivi affiancati: tabellone (sinistra) e cartella con frecce (destra)
        sizer_griglie = wx.BoxSizer(wx.HORIZONTAL)
        self._pannello_tabellone = PannelloTabellone(panel)
        sizer_griglie.Add(self._pannello_tabellone, 0, wx.ALL, 5)

        # Gruppo 1 — freccia sinistra [◀]
        self._btn_freccia_sx = wx.Button(
            panel, label="◀", size=wx.Size(*DIMENSIONE_BTN_FRECCIA)
        )
        self._btn_freccia_sx.SetName("Cartella precedente")
        self._btn_freccia_sx.SetBackgroundColour(wx.Colour(COLORE_ACCENT_BLU))
        self._btn_freccia_sx.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._btn_freccia_sx.Disable()
        sizer_griglie.Add(self._btn_freccia_sx, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 2)

        self._pannello_cartella = PannelloCartella(panel)
        sizer_griglie.Add(self._pannello_cartella, 1, wx.ALL | wx.EXPAND, 5)

        # Gruppo 1 — freccia destra [▶]
        self._btn_freccia_dx = wx.Button(
            panel, label="▶", size=wx.Size(*DIMENSIONE_BTN_FRECCIA)
        )
        self._btn_freccia_dx.SetName("Cartella successiva")
        self._btn_freccia_dx.SetBackgroundColour(wx.Colour(COLORE_ACCENT_BLU))
        self._btn_freccia_dx.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
        self._btn_freccia_dx.Disable()
        sizer_griglie.Add(self._btn_freccia_dx, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)

        sizer.Add(sizer_griglie, 0, wx.ALL | wx.EXPAND, 0)

        # Bind frecce navigazione
        self.Bind(wx.EVT_BUTTON, self._on_cartella_precedente, self._btn_freccia_sx)
        self.Bind(wx.EVT_BUTTON, self._on_cartella_successiva, self._btn_freccia_dx)

        # Gruppo 2 — riga selezione diretta cartella (pulsanti 1…N, creati dinamicamente)
        self._sizer_selezione = wx.BoxSizer(wx.HORIZONTAL)
        self._pulsanti_selezione: list[wx.Button] = []
        sizer.Add(self._sizer_selezione, 0, wx.ALL | wx.EXPAND, 5)

        # Gruppo 3 — riga pulsanti premi (Ambo…Tombola)
        sizer_premi = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_premi: dict[str, wx.Button] = {}
        for tipo in _TIPI_VITTORIA:
            if tipo == "tombola":
                bg = COLORE_BTN_TOMBOLA
                fg = COLORE_BTN_TOMBOLA_TESTO
            else:
                bg = COLORE_ACCENT_ROSSO
                fg = "#FFFFFF"
            btn = wx.Button(panel, label=tipo.capitalize())
            btn.SetName(f"Dichiara {tipo}")
            btn.SetBackgroundColour(wx.Colour(bg))
            btn.SetForegroundColour(wx.Colour(fg))
            btn.Disable()
            self.Bind(wx.EVT_BUTTON, functools.partial(self._on_premio, tipo), btn)
            sizer_premi.Add(btn, 1, wx.ALL, 3)
            self._btn_premi[tipo] = btn
        sizer.Add(sizer_premi, 0, wx.ALL | wx.EXPAND, 5)

        # Area log annunci (read-only)
        sizer.Add(wx.StaticText(panel, label="Log annunci (Ctrl+E per consultare):"), 0, wx.LEFT | wx.TOP, 5)
        self._log_ctrl = wx.TextCtrl(
            panel,
                style=wx.TE_MULTILINE | wx.TE_READONLY,
            size=(-1, 120),
        )
        self._log_ctrl.SetName("Log annunci. Usa Ctrl+E per consultare.")
        sizer.Add(self._log_ctrl, 0, wx.ALL | wx.EXPAND, 5)

        panel.SetSizer(sizer)
        panel.Layout()

        self._btn_principale.Bind(wx.EVT_BUTTON, self._on_pulsante_principale)

    # ------------------------------------------------------------------
    # Binding finestra (Categoria B e C)
    # ------------------------------------------------------------------

    def _bind_finestra(self) -> None:
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_pausa(self, event: object) -> None:
        """Handler del pulsante pausa: delega a _toggle_pausa."""
        self._toggle_pausa()

    def _on_char_hook(self, event: wx.KeyEvent) -> None:
        key = event.GetKeyCode()
        ctrl = event.ControlDown()
        alt = event.AltDown()
        shift = event.ShiftDown()

        # Categoria B — blocca propagazione

        # Alt+Frecce: intercettate a livello frame per evitare che
        # Windows/NVDA consumino il gesto prima del pannello griglia.
        if not ctrl and (alt or shift):
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

        # Ctrl+Enter — passa turno
        if ctrl and key == _KEY_RETURN:
            self._on_pulsante_principale(None)
            return

        # Ctrl+P — pausa/ripresa
        if ctrl and key == ord("P"):
            self._toggle_pausa()
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
        if self._in_pausa:
            return

        if self._fase_turno_ui == "attesa_estrazione":
            # Al primo turno, crea i pulsanti di selezione diretta cartella
            if self._partita.tabellone.get_conteggio_estratti() == 0:
                self._crea_pulsanti_selezione_cartella()
            # Fase 1: estrae il numero + avvia finestra d'azione V2.
            risultato_est = self._comandi_sistema.esegui_fase_estrazione(self._partita)
            if risultato_est is None:
                self._renderer.mostra_messaggio_sistema(
                    "Impossibile estrarre il numero. La partita potrebbe essere terminata."
                )
                return
            self._turno_corrente += 1
            numero = risultato_est.get("numero_estratto", "?")
            self._renderer.annuncia_numero_estratto(numero, self._turno_corrente)
            self._aggiorna_griglie_visive()
            self._fase_turno_ui = "attesa_reclami"
            self._aggiorna_stato_pulsante()
            # Avvia il timer della finestra d'azione e pianifica le risposte dei bot.
            self._avvia_timer_azione(self._durata_finestra_ms)
            self._pianifica_risposta_bot()

        elif self._fase_turno_ui == "attesa_reclami":
            # Fase 2: l'umano dichiara fine manualmente (prima del timeout).
            if self._comandi.turno_gia_dichiarato():
                self._renderer.mostra_messaggio_sistema(
                    "Hai già dichiarato la fine del tuo turno. Attendo gli altri giocatori."
                )
            else:
                self._comandi.dichiara_fine_turno(self._partita)
                self._renderer.mostra_messaggio_sistema(
                    "Turno dichiarato concluso. Attendo gli altri giocatori."
                )
            self._controlla_tutti_pronti()

        # Stato "pausa_turno": il pulsante è disabilitato o ignorato durante la pausa.

    # ------------------------------------------------------------------
    # Timer finestra d'azione (D-2)
    # ------------------------------------------------------------------

    def _ferma_tutti_i_timer(self) -> None:
        """Ferma entrambi i timer garantendo mutua esclusione."""
        if self._timer_azione is not None:
            self._timer_azione.Stop()
            self._timer_azione = None
        if self._timer_pausa is not None:
            self._timer_pausa.Stop()
            self._timer_pausa = None

    def _avvia_timer_azione(self, durata_ms: int) -> None:
        """Avvia il timer tick della finestra d'azione."""
        self._ferma_tutti_i_timer()  # Protezione mutua esclusione
        self._durata_finestra_corrente_ms = durata_ms
        self._ms_trascorsi_azione = 0
        self._avvisi_emessi = set()
        self._timer_azione = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_tick_azione, self._timer_azione)
        self._timer_azione.Start(self._tick_ms)

    def _on_tick_azione(self, event: wx.TimerEvent) -> None:
        """Tick del timer d'azione: calcola percentuale e lancia avvisi vocali."""
        if self._fase_turno_ui != "attesa_reclami":
            return
        self._ms_trascorsi_azione += self._tick_ms
        if self._comandi.turno_gia_dichiarato():
            if self._ms_trascorsi_azione >= self._durata_finestra_corrente_ms:
                self._on_timeout_azione()
            return
        if self._durata_finestra_corrente_ms <= 0:
            return
        pct = self._ms_trascorsi_azione / self._durata_finestra_corrente_ms * 100
        secondi_rim = max(0, (self._durata_finestra_corrente_ms - self._ms_trascorsi_azione) // 1000)

        if pct >= 95 and 95 not in self._avvisi_emessi:
            self._avvisi_emessi.add(95)
            self._renderer.annuncia_avviso_timeout(secondi_rim, livello=95)
        elif pct >= 80 and 80 not in self._avvisi_emessi:
            self._avvisi_emessi.add(80)
            self._renderer.annuncia_avviso_timeout(secondi_rim, livello=80)
        elif pct >= 60 and 60 not in self._avvisi_emessi:
            self._avvisi_emessi.add(60)
            self._renderer.annuncia_avviso_timeout(secondi_rim, livello=60)

        if self._ms_trascorsi_azione >= self._durata_finestra_corrente_ms:
            self._on_timeout_azione()

    # ------------------------------------------------------------------
    # Timeout finestra (D-3) e terminazione anticipata (D-4)
    # ------------------------------------------------------------------

    def _on_timeout_azione(self) -> None:
        """Scaduto il timer: salta il reclamo umano e avanza alla verifica."""
        self._ferma_tutti_i_timer()  # Protezione mutua esclusione
        if self._fase_turno_ui != "attesa_reclami":
            return
        self._esegui_verifica_premi()

    def _controlla_tutti_pronti(self) -> None:
        """Verifica se tutti i giocatori hanno dichiarato fine; avanza se sì."""
        if self._partita.tutti_hanno_dichiarato_fine():
            self._on_all_ready()

    def _on_all_ready(self) -> None:
        """Tutti pronti: ferma il timer e avanza a verifica in anticipo."""
        self._ferma_tutti_i_timer()  # Protezione mutua esclusione
        if self._fase_turno_ui != "attesa_reclami":
            return
        self._renderer.annuncia_tutti_pronti()
        self._esegui_verifica_premi()

    def _esegui_verifica_premi(self) -> None:
        """Esegue la fase di verifica premi e avvia la pausa tra turni."""
        self._fase_turno_ui = "pausa_turno"
        self._aggiorna_stato_pulsante()
        risultato_ver = self._comandi_sistema.esegui_fase_verifica(self._partita)
        if risultato_ver is None:
            self._renderer.mostra_messaggio_sistema("Impossibile verificare i premi.")
            self._fase_turno_ui = "attesa_estrazione"
            self._aggiorna_stato_pulsante()
            return
        premi_nuovi = risultato_ver.get("premi_nuovi", [])
        self._renderer.annuncia_premi_turno(premi_nuovi)
        self._aggiorna_griglie_visive()

        if risultato_ver.get("partita_terminata") or risultato_ver.get("tombola_rilevata"):
            self._renderer.mostra_messaggio_sistema("La partita è terminata.")
            self._btn_principale.Disable()
            if self._finestra_principale is not None:
                self._btn_torna_menu.Enable()
                self._btn_torna_menu.Show()
                self.Layout()
                self._btn_torna_menu.SetFocus()
            return

        self._avvia_pausa_turno(self._durata_pausa_ms)

    # ------------------------------------------------------------------
    # Pianificazione risposte bot (D-5)
    # ------------------------------------------------------------------

    def _pianifica_risposta_bot(self) -> None:
        """Schedula con wx.CallLater le dichiarazioni dei bot con ritardi distribuiti."""
        bots = [g for g in self._partita.giocatori if g.is_automatico()]
        if not bots:
            return
        premi_gia_assegnati: set = self._partita.premi_gia_assegnati
        premi_tipo_chiusi: set = self._partita.premi_tipo_chiusi
        delay_max = max(500, int(self._durata_finestra_corrente_ms * 0.70))
        for bot in bots:
            delay = random.randint(500, delay_max)
            wx.CallLater(delay, self._dichiara_fine_bot, bot, premi_gia_assegnati, premi_tipo_chiusi)

    def _dichiara_fine_bot(self, bot: object, premi_gia_assegnati: set, premi_tipo_chiusi: set) -> None:
        """Handler chiamato dal CallLater dopo il ritardo di risposta del bot."""
        if self._fase_turno_ui != "attesa_reclami":
            return
        bot.dichiara_fine_fase_azione(premi_gia_assegnati, premi_tipo_chiusi)  # type: ignore[union-attr]
        nome_bot: str = getattr(bot, "nome", "Bot")
        self._renderer.mostra_messaggio_sistema(f"{nome_bot} ha passato il turno.")
        self._controlla_tutti_pronti()

    def _on_torna_menu(self, event: wx.Event) -> None:
        """Torna alla finestra principale nascondendo questa finestra di gioco."""
        self._renderer.imposta_widget_log(None)
        self.Hide()
        if self._finestra_principale is not None:
            self._finestra_principale.Show()
            self._renderer.aggiorna_finestra(self._finestra_principale)

    # ------------------------------------------------------------------
    # Pausa tra turni (D-7)
    # ------------------------------------------------------------------

    def _avvia_pausa_turno(self, durata_ms: int) -> None:
        """Avvia la pausa tra turni con annuncio vocale iniziale."""
        self._ferma_tutti_i_timer()  # Protezione mutua esclusione
        self._avvio_pausa_turno_mono = time.monotonic()
        secondi = durata_ms // 1000
        self._renderer.annuncia_avvio_pausa_turno(secondi)
        self._timer_pausa = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_tick_pausa, self._timer_pausa)
        self._timer_pausa.Start(durata_ms, wx.TIMER_ONE_SHOT)

    def _on_tick_pausa(self, event: wx.TimerEvent) -> None:
        """Fine della pausa: avvia automaticamente un nuovo turno."""
        # Guard difensiva: ignora callback tardivi se la partita è in pausa utente
        # o se la fase non è più "pausa_turno" (es. riprendi anticipato).
        if self._in_pausa or self._fase_turno_ui != "pausa_turno":
            return
        self._timer_pausa = None
        self._fase_turno_ui = "attesa_estrazione"
        self._aggiorna_stato_pulsante()
        # Azione 2: simula click automatico sul pulsante per avviare il turno successivo.
        self._on_pulsante_principale(None)

    # ------------------------------------------------------------------
    # Pausa gioco su richiesta del giocatore (Ctrl+P)
    # ------------------------------------------------------------------

    def _toggle_pausa(self) -> None:
        """Alterna tra pausa e ripresa del gioco."""
        if self._in_pausa:
            self._riprendi_gioco()
        else:
            self._metti_in_pausa()

    def _metti_in_pausa(self) -> None:
        """Mette in pausa la partita attiva, congela timer e aggiorna UI."""
        if self._comandi_sistema.is_terminata(self._partita):
            return
        if self._partita.tabellone.get_conteggio_estratti() == 0:
            return  # Pausa disponibile solo durante partita attiva
        self._fase_pre_pausa = self._fase_turno_ui
        # Calcola residuo timer azione (se attivo)
        self._ms_residui_azione = max(
            0, self._durata_finestra_corrente_ms - self._ms_trascorsi_azione
        )
        # Calcola residuo timer pausa turno (se attivo)
        if self._timer_pausa is not None and self._avvio_pausa_turno_mono > 0:
            elapsed = int((time.monotonic() - self._avvio_pausa_turno_mono) * 1000)
            self._ms_residui_pausa = max(0, self._durata_pausa_ms - elapsed)
        else:
            self._ms_residui_pausa = 0
        self._ferma_tutti_i_timer()
        self._in_pausa = True
        self._fase_turno_ui = "in_pausa"
        self._aggiorna_stato_pulsante()
        self._renderer.annuncia_pausa("Gioco in pausa.")

    def _riprendi_gioco(self) -> None:
        """Riprende il gioco dalla pausa, ripristinando timer e fase precedente."""
        self._in_pausa = False
        self._fase_turno_ui = self._fase_pre_pausa
        self._aggiorna_stato_pulsante()
        # Costruisce testo di ripresa con stato completo
        _mappa_fase = {
            "attesa_estrazione": "Attesa nuova estrazione",
            "attesa_reclami": "Finestra reclami aperta",
            "pausa_turno": "Pausa breve tra turni",
        }
        desc_fase = _mappa_fase.get(self._fase_pre_pausa, self._fase_pre_pausa)
        if self._fase_pre_pausa == "attesa_reclami" and self._ms_residui_azione > 0:
            secondi = max(1, self._ms_residui_azione // 1000)
            testo = f"Gioco ripreso. Fase: {desc_fase}. Tempo rimanente: {secondi} secondi."
            self._avvia_timer_azione(self._ms_residui_azione)
        elif self._fase_pre_pausa == "pausa_turno" and self._ms_residui_pausa > 0:
            secondi = max(1, self._ms_residui_pausa // 1000)
            testo = f"Gioco ripreso. Fase: {desc_fase}. Tempo rimanente: {secondi} secondi."
            self._avvia_pausa_turno(self._ms_residui_pausa)
        else:
            testo = f"Gioco ripreso. Fase: {desc_fase}."
        self._renderer.annuncia_pausa(testo)


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

    def aggiorna_stato_pulsante(self, primo_turno_eseguito: bool, fase: Optional[str] = None) -> None:
        """Interfaccia per il renderer: aggiorna etichetta pulsante in base alla fase."""
        if fase == "in_pausa":
            label = "Gioco in pausa"
            self._btn_principale.SetLabel(label)
            self._btn_principale.Disable()
            if hasattr(self, "_btn_pausa"):
                self._btn_pausa.SetLabel("Riprendi")
                self._btn_pausa.Enable()
            # Frecce e premi disabilitati durante pausa
            if hasattr(self, "_btn_freccia_sx"):
                self._btn_freccia_sx.Disable()
                self._btn_freccia_dx.Disable()
            if hasattr(self, "_btn_premi"):
                for btn in self._btn_premi.values():
                    btn.Disable()
            self._renderer.annuncia_fase_turno(label)
            return
        if fase == "attesa_reclami":
            label = "Ho finito — avvia verifica"
        elif fase == "pausa_turno":
            label = "Pausa in corso…"
        elif primo_turno_eseguito:
            label = "Passa turno"
        else:
            label = "Inizia partita"
        self._btn_principale.SetLabel(label)
        self._btn_principale.Enable(fase != "pausa_turno")
        # Abilita btn_pausa solo se la partita è attiva
        if hasattr(self, "_btn_pausa"):
            partita_attiva = (
                self._partita.tabellone.get_conteggio_estratti() > 0
                and not self._comandi_sistema.is_terminata(self._partita)
                and fase != "pausa_turno"
            )
            self._btn_pausa.SetLabel("Metti in pausa")
            if partita_attiva:
                self._btn_pausa.Enable()
            else:
                self._btn_pausa.Disable()
        # Frecce navigazione cartella
        if hasattr(self, "_btn_freccia_sx"):
            nav_attiva = (
                self._partita.tabellone.get_conteggio_estratti() > 0
                and not self._comandi_sistema.is_terminata(self._partita)
                and fase not in ("pausa_turno",)
            )
            self._btn_freccia_sx.Enable(nav_attiva)
            self._btn_freccia_dx.Enable(nav_attiva)
        # Pulsanti premi
        if hasattr(self, "_btn_premi") and self._btn_premi:
            premi_chiusi: set = getattr(self._partita, "premi_tipo_chiusi", set())
            for tipo, btn in self._btn_premi.items():
                if tipo in premi_chiusi:
                    btn.Disable()
                    etichetta = tipo.capitalize()
                    if not btn.GetLabel().endswith(" ✓"):
                        btn.SetLabel(f"{etichetta} ✓")
                elif fase == "attesa_reclami":
                    btn.Enable()
                    btn.SendSizeEvent()
                else:
                    btn.Disable()
        # Re-announce esplicito per NVDA (l'etichetta potrebbe non essere riletta automaticamente).
        self._renderer.annuncia_fase_turno(label)

    # ------------------------------------------------------------------
    # Helper interni
    # ------------------------------------------------------------------

    def _aggiorna_griglie_visive(self) -> None:
        """Sincronizza le griglie visive con lo stato corrente della partita."""
        if not hasattr(self, "_pannello_tabellone") or not hasattr(self, "_pannello_cartella"):
            return
        self._pannello_tabellone.aggiorna(self._partita.tabellone.numeri_estratti)
        giocatore_umano = next(
            (g for g in self._partita.giocatori if not g.is_automatico()), None
        )
        if giocatore_umano is None or not giocatore_umano.cartelle:
            return
        indice = getattr(giocatore_umano, "_indice_cartella_focus", None)
        if indice is None:
            indice = 0
        indice = max(0, min(indice, len(giocatore_umano.cartelle) - 1))
        cartella = giocatore_umano.cartelle[indice]
        self._pannello_cartella.aggiorna(
            griglia=cartella.get_griglia_semplice(),
            numeri_segnati=cartella.numeri_segnati,
            numeri_estratti=self._partita.tabellone.numeri_estratti,
        )

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
        self.aggiorna_stato_pulsante(primo_turno_eseguito, fase=self._fase_turno_ui)

    def _annuncia_risultato_turno(self, risultato: dict) -> None:
        """Costruisce e vocalizza il messaggio riassuntivo del turno (percorso monolitico)."""
        numero = risultato.get("numero_estratto", "?")
        premi_nuovi = risultato.get("premi_nuovi", [])
        self._renderer.annuncia_numero_estratto(numero, self._turno_corrente)
        self._renderer.annuncia_premi_turno(premi_nuovi)

    def _apri_ricerca_numero(self) -> None:
        """Apre il dialog modale di ricerca numero."""
        from bingo_game.ui.dialogo_ricerca import DialogoRicercaNumero
        dlg = DialogoRicercaNumero(
            parent=self,
            renderer=self._renderer,
            comandi=self._comandi,
        )
        rc = dlg.ShowModal()
        primo_risultato = getattr(dlg, "_primo_risultato", None) if rc == wx.ID_OK else None
        dlg.Destroy()
        if primo_risultato is not None:
            self._naviga_a_risultato_ricerca(primo_risultato)
        else:
            self._pannello_griglia.SetFocus()

    def _naviga_a_risultato_ricerca(self, risultato: Any) -> None:
        """Naviga alla posizione del primo risultato della ricerca."""
        self._dispatch(self._comandi.imposta_focus_cartella(risultato.numero_cartella))
        self._dispatch(self._comandi.vai_a_riga(risultato.indice_riga + 1))
        self._dispatch(self._comandi.vai_a_colonna(risultato.indice_colonna + 1))

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

    def _imposta_focus_iniziale(self) -> None:
        """Imposta il focus di gioco su cartella 1, riga 1, colonna 1 all'avvio."""
        self._dispatch(self._comandi.imposta_focus_cartella(1))
        self._dispatch(self._comandi.vai_a_riga(1))
        self._dispatch(self._comandi.vai_a_colonna(1))
        self._aggiorna_griglie_visive()

    def _on_partita_change(self, *args, **kwargs) -> None:
        """Handler duck-typed per ricevere eventi di stato partita (se supportato).

        Usa wx.CallAfter per aggiornare le griglie in modo thread-safe dal dominio.
        """
        try:
            wx.CallAfter(self._aggiorna_griglie_visive)
        except Exception:
            # Non fatale: il subscribe è opzionale e l'aggiornamento è best-effort
            pass

    # ------------------------------------------------------------------
    # Gruppo 1 — Handler frecce navigazione cartella
    # ------------------------------------------------------------------

    def _on_cartella_precedente(self, event: object) -> None:
        """Handler del pulsante ◀: naviga alla cartella precedente."""
        self._dispatch(self._comandi.cartella_precedente())
        return

    def _on_cartella_successiva(self, event: object) -> None:
        """Handler del pulsante ▶: naviga alla cartella successiva."""
        self._dispatch(self._comandi.cartella_successiva())
        return

    # ------------------------------------------------------------------
    # Gruppo 2 — Selezione diretta cartella
    # ------------------------------------------------------------------

    def _crea_pulsanti_selezione_cartella(self) -> None:
        """Crea dinamicamente i pulsanti di selezione diretta cartella (1…N)."""
        if self._pulsanti_selezione:
            return
        giocatore_umano = next(
            (g for g in self._partita.giocatori if not g.is_automatico()), None
        )
        if giocatore_umano is None:
            return
        n_cartelle = len(giocatore_umano.cartelle)
        for i in range(1, n_cartelle + 1):
            btn = wx.Button(
                self._panel, label=str(i), size=wx.Size(*DIMENSIONE_BTN_SELEZIONE_CARTELLA)
            )
            btn.SetName(f"Vai a cartella {i}")
            btn.SetToolTip(f"Salta direttamente alla cartella {i}")
            btn.SetBackgroundColour(wx.Colour(COLORE_BTN_NEUTRO))
            btn.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
            self.Bind(
                wx.EVT_BUTTON,
                functools.partial(self._on_selezione_cartella_btn, i),
                btn,
            )
            self._sizer_selezione.Add(btn, 0, wx.ALL, 3)
            self._pulsanti_selezione.append(btn)
        # Corregge ordine Tab: i pulsanti creati tardivamente andrebbero in fondo
        # al ciclo focus; MoveAfterInTabOrder li posiziona dopo la freccia destra.
        if self._pulsanti_selezione:
            self._pulsanti_selezione[0].MoveAfterInTabOrder(self._btn_freccia_dx)
            for i in range(1, len(self._pulsanti_selezione)):
                self._pulsanti_selezione[i].MoveAfterInTabOrder(
                    self._pulsanti_selezione[i - 1]
                )
        self._panel.Layout()
        self.Layout()

    def _on_selezione_cartella_btn(self, numero: int, event: object) -> None:
        """Handler dei pulsanti selezione diretta cartella."""
        self._dispatch(self._comandi.imposta_focus_cartella(numero))
        self._pannello_griglia.SetFocus()
        return

    def _aggiorna_evidenziazione_selezione(self, numero_cartella: int) -> None:
        """Colora il pulsante attivo con blu e gli altri con grigio neutro."""
        for i, btn in enumerate(self._pulsanti_selezione, start=1):
            if i == numero_cartella:
                btn.SetBackgroundColour(wx.Colour(COLORE_ACCENT_BLU))
                btn.SetForegroundColour(wx.Colour(COLORE_TESTO_CHIARO))
            else:
                btn.SetBackgroundColour(wx.Colour(COLORE_BTN_NEUTRO))
                btn.SetForegroundColour(wx.Colour(COLORE_TESTO_SCURO))
            btn.Refresh()

    def aggiorna_selezione_cartella(self, numero: int) -> None:
        """Aggiorna l'evidenziazione del pulsante selezione cartella (duck typing per renderer)."""
        self._aggiorna_evidenziazione_selezione(numero)

    # ------------------------------------------------------------------
    # Gruppo 3 — Handler pulsanti premi
    # ------------------------------------------------------------------

    def _on_premio(self, tipo: str, event: object) -> None:
        """Handler dei pulsanti premi: annuncia vittoria del tipo indicato."""
        self._dispatch(self._comandi.annuncia_vittoria(tipo, self._turno_corrente))
        return

