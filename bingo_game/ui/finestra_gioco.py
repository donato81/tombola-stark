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
import random
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
        durata_finestra_ms: int = 60000,
        durata_pausa_ms: int = 5000,
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

        self._build_ui()
        self._bind_finestra()
        self.Centre()

        # Aggiorna il renderer sul frame corrente e sul widget log
        self._renderer.aggiorna_finestra(self)
        self._renderer.imposta_widget_log(self._log_ctrl)

        # Focus iniziale sulla griglia
        self._pannello_griglia.SetFocus()
        wx.CallAfter(self._imposta_focus_iniziale)

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

        if self._fase_turno_ui == "attesa_estrazione":
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

        if risultato_ver.get("partita_terminata") or risultato_ver.get("tombola_rilevata"):
            self._renderer.mostra_messaggio_sistema("La partita è terminata.")
            self._btn_principale.Disable()
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

    # ------------------------------------------------------------------
    # Pausa tra turni (D-7)
    # ------------------------------------------------------------------

    def _avvia_pausa_turno(self, durata_ms: int) -> None:
        """Avvia la pausa tra turni con annuncio vocale iniziale."""
        self._ferma_tutti_i_timer()  # Protezione mutua esclusione
        secondi = durata_ms // 1000
        self._renderer.annuncia_avvio_pausa_turno(secondi)
        self._timer_pausa = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_tick_pausa, self._timer_pausa)
        self._timer_pausa.Start(durata_ms, wx.TIMER_ONE_SHOT)

    def _on_tick_pausa(self, event: wx.TimerEvent) -> None:
        """Fine della pausa: avvia automaticamente un nuovo turno."""
        self._timer_pausa = None
        self._fase_turno_ui = "attesa_estrazione"
        self._aggiorna_stato_pulsante()
        # Azione 2: simula click automatico sul pulsante per avviare il turno successivo.
        self._on_pulsante_principale(None)


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
        # Re-announce esplicito per NVDA (l'etichetta potrebbe non essere riletta automaticamente).
        self._renderer.annuncia_fase_turno(label)

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

    def _imposta_focus_iniziale(self) -> None:
        """Imposta il focus di gioco su cartella 1, riga 1, colonna 1 all'avvio."""
        self._dispatch(self._comandi.imposta_focus_cartella(1))
        self._dispatch(self._comandi.vai_a_riga(1))
        self._dispatch(self._comandi.vai_a_colonna(1))
