"""
Modulo: bingo_game.ui.tui.game_loop

Implementa la macchina a stati del Game Loop interattivo (v0.9.0).

Stati:
    F — ANTE_TURNO:      estrazione numero, aggiornamento display, avanzamento.
    G — ATTESA_COMANDO:  prompt loop; processa p/s/c/v/q/?.
    H — REPORT_FINALE:   riepilogo partita terminata.

Contratti architetturali:
    - Nessun import dal Domain Layer (Partita, GiocatoreUmano, ecc.).
    - Tutta la logica di gioco passa tramite game_controller.
    - Tutto l'output passa tramite _stampa_righe(); zero chiamate print() dirette.
    - Tutte le stringhe utente sono prese da MESSAGGI_OUTPUT_UI_UMANI (chiavi LOOP_*).

Version:
    v0.9.0: Prima implementazione.
"""
from __future__ import annotations

import logging
from typing import Optional

from bingo_game.game_controller import (
    esegui_turno_sicuro,
    ottieni_giocatore_umano,
    ottieni_stato_sintetico,
    partita_terminata,
)
from bingo_game.events.codici_controller import (
    CTRL_TURNO_NON_IN_CORSO,
    CTRL_NUMERI_ESAURITI,
    CTRL_TURNO_FALLITO_GENERICO,
)
from bingo_game.ui.locales.it import (
    MESSAGGI_CONTROLLER,
    MESSAGGI_ERRORI,
    MESSAGGI_OUTPUT_UI_UMANI,
)
from bingo_game.ui.renderers.renderer_terminal import TerminalRenderer

logger = logging.getLogger(__name__)


class GameLoop:
    """Macchina a stati del ciclo di gioco interattivo per terminale.

    Gestisce le fasi F (ANTE_TURNO), G (ATTESA_COMANDO) e H (REPORT_FINALE)
    del flusso v0.9.0.  Riceve la partita già avviata dall'esterno (TerminalUI)
    e ne guida il ciclo fino alla terminazione.

    Attributes:
        _renderer: Istanza di TerminalRenderer per delega output ricco.
        _partita:  Oggetto Partita passato dal controller.
        _quit_richiesto: Flag che segnala l'uscita anticipata da parte dell'utente.

    Note:
        Non importa oggetti del Domain Layer.  Accede allo stato del giocatore
        umano tramite ottieni_giocatore_umano() del controller.

    Version:
        v0.9.0: Prima implementazione.
    """

    def __init__(self, partita, renderer: Optional[TerminalRenderer] = None) -> None:
        """Inizializza il GameLoop.

        Args:
            partita: L'istanza Partita già avviata (stato 'in_corso').
            renderer: Istanza TerminalRenderer. Se None ne viene creata una nuova.
        """
        self._partita = partita
        self._renderer = renderer if renderer is not None else TerminalRenderer()
        self._quit_richiesto: bool = False
        logger.debug("[LOOP] GameLoop inizializzato.")

    # ------------------------------------------------------------------
    # Entry point pubblico
    # ------------------------------------------------------------------

    def avvia(self) -> None:
        """Avvia il ciclo di gioco completo (Stato F → G → H).

        Esegue il loop principale fino a terminazione della partita o
        uscita volontaria dell'utente (comando q confermato).
        """
        logger.info("[LOOP] Inizio ciclo di gioco.")
        while not self._is_fine_partita():
            self._stato_f_ante_turno()
            if self._quit_richiesto:
                break
            if self._is_fine_partita():
                break
        self._stato_h_report_finale()
        logger.info("[LOOP] Fine ciclo di gioco.")

    # ------------------------------------------------------------------
    # Stato F: ANTE_TURNO
    # ------------------------------------------------------------------

    def _stato_f_ante_turno(self) -> None:
        """Stato F: esegui il turno ed annuncia il numero estratto.

        Delega l'esecuzione del turno a esegui_turno_sicuro(), poi
        annuncia il numero e passa allo stato G (ATTESA_COMANDO).
        """
        logger.debug("[LOOP] Stato F: ANTE_TURNO")
        risultato = esegui_turno_sicuro(self._partita)

        if risultato is None:
            logger.warning("[LOOP] Turno fallito: esegui_turno_sicuro ha ritornato None.")
            self._stampa_righe((MESSAGGI_CONTROLLER[CTRL_TURNO_FALLITO_GENERICO],))
            return

        numero = risultato.get("numero_estratto")
        if numero is not None:
            tpl = MESSAGGI_OUTPUT_UI_UMANI["LOOP_NUMERO_ESTRATTO"]
            self._stampa_righe(tuple(r.format(numero=numero) for r in tpl))

        # Passa subito allo stato G per attendere il comando dell'utente
        if not self._is_fine_partita() and not self._quit_richiesto:
            self._stato_g_attesa_comando()

    # ------------------------------------------------------------------
    # Stato G: ATTESA_COMANDO
    # ------------------------------------------------------------------

    def _stato_g_attesa_comando(self) -> None:
        """Stato G: loop interattivo dei comandi.

        Mostra il prompt e processa ogni comando finché l'utente non
        digita 'p' (prosegui), 'q' confermato, o la partita termina.
        """
        logger.debug("[LOOP] Stato G: ATTESA_COMANDO")
        while not self._is_fine_partita() and not self._quit_richiesto:
            self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_PROMPT_COMANDO"])
            raw = input("").strip().lower()
            logger.debug("[LOOP] Comando ricevuto: %r", raw)

            if raw == "p":
                self._cmd_prosegui()
                return  # torna al ciclo principale
            elif raw.startswith("s"):
                self._cmd_segna(raw)
            elif raw == "c":
                self._cmd_cartella()
            elif raw == "v":
                self._cmd_tabellone()
            elif raw == "q":
                self._cmd_quit()
            elif raw == "?":
                self._cmd_help()
            else:
                self._cmd_sconosciuto(raw)

    # ------------------------------------------------------------------
    # Comandi
    # ------------------------------------------------------------------

    def _cmd_prosegui(self) -> None:
        """Comando p: prosegui al prossimo turno (uscita dal loop G)."""
        logger.debug("[LOOP] Cmd p: prosegui.")
        # Nessun output: il numero del turno successivo è già annunciato in F.

    def _cmd_segna(self, raw: str) -> None:
        """Comando s <N>: segna il numero N sulla cartella in focus.

        Args:
            raw: Stringa grezza del comando (es. 's 42' o 's42').
        """
        logger.debug("[LOOP] Cmd s: raw=%r", raw)
        parti = raw.split()
        if len(parti) < 2:
            self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])
            return

        try:
            numero = int(parti[1])
        except ValueError:
            logger.debug("[LOOP] Cmd s: argomento non intero '%s'.", parti[1])
            self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])
            return

        if not (1 <= numero <= 90):
            self._stampa_righe(MESSAGGI_ERRORI["NUMERO_NON_VALIDO"])
            return

        umano = ottieni_giocatore_umano(self._partita)
        if umano is None:
            logger.warning("[LOOP] Cmd s: giocatore umano non trovato.")
            self._stampa_righe(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"])
            return

        try:
            risultati = umano.segna_numero_su_tutte(numero)
            # Delega il rendering degli esiti al TerminalRenderer
            for evento in risultati:
                self._renderer.render(evento)
        except Exception as exc:
            logger.error("[LOOP] Cmd s: errore segna_numero_su_tutte — %s", exc)
            self._stampa_righe(MESSAGGI_ERRORI["CARTELLA_STATO_INCOERENTE"])

    def _cmd_cartella(self) -> None:
        """Comando c: riepilogo cartella in focus tramite il renderer."""
        logger.debug("[LOOP] Cmd c: cartella in focus.")
        umano = ottieni_giocatore_umano(self._partita)
        if umano is None:
            self._stampa_righe(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"])
            return
        try:
            evento = umano.riepilogo_cartella_corrente()
            self._renderer.render(evento)
        except Exception as exc:
            logger.error("[LOOP] Cmd c: errore riepilogo_cartella_corrente — %s", exc)
            self._stampa_righe(MESSAGGI_ERRORI["CARTELLA_STATO_INCOERENTE"])

    def _cmd_tabellone(self) -> None:
        """Comando v: riepilogo tabellone tramite il renderer."""
        logger.debug("[LOOP] Cmd v: riepilogo tabellone.")
        try:
            stato = ottieni_stato_sintetico(self._partita)
        except ValueError as exc:
            logger.error("[LOOP] Cmd v: errore ottieni_stato_sintetico — %s", exc)
            self._stampa_righe((MESSAGGI_CONTROLLER[CTRL_TURNO_FALLITO_GENERICO],))
            return

        numeri_estratti: list[int] = stato.get("numeri_estratti", [])
        totale = 90
        estratti = len(numeri_estratti)
        mancanti = totale - estratti
        percentuale = round((estratti / totale) * 100, 1) if totale else 0.0

        tpl = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RIEPILOGO_TABELLONE_RIGA_1"]
        self._stampa_righe(tuple(
            r.format(
                totale_estratti=estratti,
                totale_numeri=totale,
                totale_mancanti=mancanti,
                percentuale_estrazione=percentuale,
            )
            for r in tpl
        ))

    def _cmd_quit(self) -> None:
        """Comando q: chiede conferma prima di uscire dalla partita."""
        logger.debug("[LOOP] Cmd q: richiesta uscita.")
        self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_QUIT_CONFERMA"])
        risposta = input("").strip().lower()
        logger.debug("[LOOP] Conferma quit: %r", risposta)
        if risposta == "s":
            self._quit_richiesto = True
            logger.info("[LOOP] Uscita confermata dall'utente.")
        else:
            self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_QUIT_ANNULLATO"])

    def _cmd_help(self) -> None:
        """Comando ?: mostra la lista comandi e il focus cartella attuale."""
        logger.debug("[LOOP] Cmd ?: help.")
        self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_COMANDI"])

        umano = ottieni_giocatore_umano(self._partita)
        if umano is not None:
            try:
                focus = umano.get_focus_cartella()
                numero_cartella = (focus + 1) if focus is not None else "nessuna"
            except Exception:
                numero_cartella = "nessuna"
        else:
            numero_cartella = "nessuna"

        tpl = MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_FOCUS"]
        self._stampa_righe(tuple(
            r.format(numero_cartella=numero_cartella) for r in tpl
        ))

    def _cmd_sconosciuto(self, raw: str) -> None:
        """Gestisce un comando non riconosciuto con feedback accessibile.

        Args:
            raw: La stringa del comando non riconosciuto.
        """
        logger.debug("[LOOP] Comando sconosciuto: %r", raw)
        self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_COMANDO_NON_RICONOSCIUTO"])

    # ------------------------------------------------------------------
    # Stato H: REPORT_FINALE
    # ------------------------------------------------------------------

    def _stato_h_report_finale(self) -> None:
        """Stato H: stampa il riepilogo finale della partita.

        Mostra: intestazione, turni giocati, numeri estratti,
        vincitore (o nessun vincitore), premi assegnati.
        """
        logger.debug("[LOOP] Stato H: REPORT_FINALE")
        self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_INTESTAZIONE"])

        try:
            stato = ottieni_stato_sintetico(self._partita)
        except ValueError as exc:
            logger.error("[LOOP] Stato H: errore ottieni_stato_sintetico — %s", exc)
            return

        numeri_estratti: list[int] = stato.get("numeri_estratti", [])
        estratti = len(numeri_estratti)

        # Turni giocati (usiamo il conteggio estratti come proxy affidabile)
        tpl_turni = MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_TURNI"]
        self._stampa_righe(tuple(r.format(turni=estratti) for r in tpl_turni))

        # Numeri estratti
        tpl_estratti = MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_ESTRATTI"]
        self._stampa_righe(tuple(r.format(estratti=estratti) for r in tpl_estratti))

        # Vincitore (primo giocatore con ha_tombola)
        giocatori = stato.get("giocatori", [])
        vincitore = next(
            (g.get("nome") for g in giocatori if g.get("ha_tombola")),
            None,
        )
        if vincitore:
            tpl_v = MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_VINCITORE"]
            self._stampa_righe(tuple(r.format(nome=vincitore) for r in tpl_v))
        else:
            self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_NESSUN_VINCITORE"])

        # Premi assegnati
        premi = stato.get("premi_gia_assegnati", [])
        tpl_premi = MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_PREMI"]
        self._stampa_righe(tuple(r.format(premi=len(premi)) for r in tpl_premi))

    # ------------------------------------------------------------------
    # Helper privati
    # ------------------------------------------------------------------

    def _is_fine_partita(self) -> bool:
        """Controlla se la partita è terminata tramite il controller.

        Returns:
            True se la partita è in stato 'terminata', False altrimenti.
        """
        try:
            return partita_terminata(self._partita)
        except ValueError as exc:
            logger.error("[LOOP] _is_fine_partita: errore — %s", exc)
            return True  # per sicurezza, esci dal loop

    def _stampa_righe(self, righe: tuple[str, ...]) -> None:
        """Stampa su stdout ogni riga della tupla ricevuta.

        Args:
            righe: Tupla di stringhe da stampare, una per riga.
        """
        for riga in righe:
            print(riga)
