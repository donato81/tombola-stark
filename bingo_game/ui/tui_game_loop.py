"""TUI Game Loop per Tombola Stark — v0.9.0.

Implementa il ciclo interattivo di partita accessibile da terminale.
Compatibile con screen reader (NVDA / JAWS / Orca).

Architettura a layer rispettata:
- Import esclusivi dal Controller (bingo_game.game_controller)
- Import esclusivi dalla TUI/Locale layer (bingo_game.ui.*)
- NESSUN import diretto dal Domain Layer (bingo_game.partita, .players, ecc.)

Version: v0.9.0
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
from bingo_game.partita import Partita  # usato SOLO per type hint, non per logica Domain
from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI
from bingo_game.ui.renderers.renderer_terminal import TerminalRenderer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Costanti di configurazione
# ---------------------------------------------------------------------------
_COMANDI_VALIDI = frozenset({"p", "s", "c", "v", "q", "?"})
_RISPOSTA_CONFERMA_SI = frozenset({"s", "si", "sì"})


class TuiGameLoop:
    """Ciclo interattivo di gioco per Tombola Stark.

    Riceve la Partita già avviata da TerminalUI e gestisce il loop
    fino a fine partita o quit esplicito del giocatore umano.

    Attributes:
        _partita: Riferimento alla Partita in corso (già in stato 'in_corso').
        _renderer: TerminalRenderer per la vocalizzazione degli eventi.
        _quit_richiesto: flag interno per l'uscita confermata.

    Note:
        Nessuna importazione diretta dal Domain Layer.
        I comandi informativi (c, v, ?) NON avanzano il turno.
        Il comando q richiede sempre conferma esplicita.

    Version: v0.9.0
    """

    def __init__(self, partita: Partita) -> None:
        """Inizializza il TUI Game Loop.

        Args:
            partita: Istanza Partita già avviata (stato 'in_corso').
        """
        self._partita = partita
        self._renderer = TerminalRenderer()
        self._quit_richiesto: bool = False
        logger.debug("[TUI-LOOP] TuiGameLoop inizializzato.")

    # ------------------------------------------------------------------
    # Entry point pubblico
    # ------------------------------------------------------------------

    def avvia(self) -> None:
        """Avvia il loop interattivo di partita.

        Esegue un turno automatico, mostra il numero estratto, poi entra
        nel sotto-loop dei comandi utente fino a che:
        - il giocatore preme 'p' per proseguire al turno successivo,
        - il giocatore preme 'q' e conferma l'uscita,
        - la partita termina (tombola o numeri esauriti).
        """
        logger.info("[TUI-LOOP] Avvio loop di partita.")

        while not partita_terminata(self._partita) and not self._quit_richiesto:
            risultato = esegui_turno_sicuro(self._partita)

            if risultato is None:
                # Partita probabilmente terminata o errore
                break

            self._stampa_numero_estratto(risultato["numero_estratto"])

            # Check tombola / fine partita
            if risultato.get("tombola_rilevata") or risultato.get("partita_terminata"):
                self._mostra_report_finale()
                break

            # Sotto-loop comandi: rimane qui finché l'utente non preme 'p' o 'q'
            self._loop_comandi()

        logger.info("[TUI-LOOP] Loop di partita terminato.")

    # ------------------------------------------------------------------
    # Loop comandi
    # ------------------------------------------------------------------

    def _loop_comandi(self) -> None:
        """Sotto-loop: raccoglie e dispatcha i comandi fino a 'p' o quit."""
        while not self._quit_richiesto:
            self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_PROMPT_COMANDO"])
            raw = input("").strip().lower()

            # Parsing: separa comando da argomento opzionale
            parti = raw.split(maxsplit=1)
            comando = parti[0] if parti else ""
            argomento = parti[1] if len(parti) > 1 else None

            if comando == "p":
                logger.debug("[TUI-LOOP] Comando 'p': prosegui.")
                break  # Esce dal sotto-loop → turno successivo

            elif comando == "s":
                self._cmd_segna(argomento)

            elif comando == "c":
                self._cmd_cartella()

            elif comando == "v":
                self._cmd_tabellone()

            elif comando == "q":
                self._cmd_quit()
                if self._quit_richiesto:
                    break  # Uscita confermata: interrompe il sotto-loop

            elif comando == "?":
                self._cmd_help()

            else:
                # Comando sconosciuto o input vuoto
                self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_COMANDO_NON_RICONOSCIUTO"])
                logger.debug("[TUI-LOOP] Comando non riconosciuto: '%s'.", raw)

    # ------------------------------------------------------------------
    # Comandi
    # ------------------------------------------------------------------

    def _cmd_segna(self, argomento: Optional[str]) -> None:
        """Comando 's <N>': segna il numero N sulla cartella in focus del giocatore umano.

        Il numero viene passato al renderer che invoca il metodo appropriato
        sul GiocatoreUmano tramite il Controller.

        Args:
            argomento: Stringa con il numero da segnare, oppure None se mancante.
        """
        logger.debug("[TUI-LOOP] Comando 's': argomento='%s'.", argomento)

        # Validazione: argomento mancante
        if argomento is None:
            from bingo_game.ui.locales.it import MESSAGGI_ERRORI
            self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])
            return

        # Validazione: argomento non intero
        try:
            numero = int(argomento)
        except ValueError:
            from bingo_game.ui.locales.it import MESSAGGI_ERRORI
            self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])
            logger.debug("[TUI-LOOP] Comando 's': argomento non intero '%s'.", argomento)
            return

        # Ottieni il giocatore umano tramite Controller
        giocatore = ottieni_giocatore_umano(self._partita)
        if giocatore is None:
            from bingo_game.ui.locales.it import MESSAGGI_ERRORI
            self._stampa_righe(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"])
            return

        # Delega la segnazione al renderer (che usa il GiocatoreUmano)
        self._renderer.stampa_segnazione_numero(giocatore, numero)

    def _cmd_cartella(self) -> None:
        """Comando 'c': mostra il riepilogo della cartella in focus."""
        logger.debug("[TUI-LOOP] Comando 'c': riepilogo cartella.")
        giocatore = ottieni_giocatore_umano(self._partita)
        if giocatore is None:
            from bingo_game.ui.locales.it import MESSAGGI_ERRORI
            self._stampa_righe(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"])
            return
        self._renderer.stampa_riepilogo_cartella_corrente(giocatore)

    def _cmd_tabellone(self) -> None:
        """Comando 'v': mostra il riepilogo del tabellone."""
        logger.debug("[TUI-LOOP] Comando 'v': riepilogo tabellone.")
        try:
            stato = ottieni_stato_sintetico(self._partita)
        except ValueError as exc:
            logger.error("[TUI-LOOP] Errore ottieni_stato_sintetico: %s", exc)
            return
        self._renderer.stampa_riepilogo_tabellone(stato)

    def _cmd_quit(self) -> None:
        """Comando 'q': richiede conferma prima di uscire.

        Imposta self._quit_richiesto = True SOLO se l'utente conferma con 's'.
        Con 'n' o input non valido, l'uscita viene annullata.
        """
        logger.debug("[TUI-LOOP] Comando 'q': richiesta conferma.")
        self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_QUIT_CONFERMA"])
        risposta = input("").strip().lower()

        if risposta in _RISPOSTA_CONFERMA_SI:
            self._quit_richiesto = True
            logger.info("[TUI-LOOP] Quit confermato dall'utente.")
        else:
            self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_QUIT_ANNULLATO"])
            logger.debug("[TUI-LOOP] Quit annullato (risposta='%s').", risposta)

    def _cmd_help(self) -> None:
        """Comando '?': mostra l'aiuto sui comandi disponibili."""
        logger.debug("[TUI-LOOP] Comando '?': aiuto.")
        self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_COMANDI"])

        # Mostra la cartella in focus attuale (se presente)
        giocatore = ottieni_giocatore_umano(self._partita)
        if giocatore is not None and giocatore.focus_cartella is not None:
            numero_cartella = giocatore.focus_cartella + 1  # 1-based
            riga_focus = MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_FOCUS"][0].format(
                numero_cartella=numero_cartella
            )
            print(riga_focus)

    # ------------------------------------------------------------------
    # Stampa helper
    # ------------------------------------------------------------------

    def _stampa_numero_estratto(self, numero: int) -> None:
        """Stampa il numero appena estratto in questo turno.

        Args:
            numero: Numero estratto (1..90).
        """
        riga = MESSAGGI_OUTPUT_UI_UMANI["LOOP_NUMERO_ESTRATTO"][0].format(numero=numero)
        print(riga)

    def _mostra_report_finale(self) -> None:
        """Stampa il report di fine partita (intestazione + statistiche)."""
        logger.info("[TUI-LOOP] Mostra report finale.")
        try:
            stato = ottieni_stato_sintetico(self._partita)
        except ValueError:
            return

        # Intestazione
        self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_INTESTAZIONE"])

        # Turni giocati
        turni = len(stato.get("numeri_estratti", []))
        riga_turni = MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_TURNI"][0].format(turni=turni)
        print(riga_turni)

        # Numeri estratti
        estratti = len(stato.get("numeri_estratti", []))
        riga_estratti = MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_ESTRATTI"][0].format(
            estratti=estratti
        )
        print(riga_estratti)

        # Premi assegnati
        premi = len(stato.get("premi_gia_assegnati", []))
        riga_premi = MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_PREMI"][0].format(premi=premi)
        print(riga_premi)

        # Vincitore tombola o nessun vincitore
        giocatori = stato.get("giocatori", [])
        vincitore = next((g["nome"] for g in giocatori if g.get("ha_tombola")), None)
        if vincitore:
            riga_v = MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_VINCITORE"][0].format(
                nome=vincitore
            )
            print(riga_v)
        else:
            self._stampa_righe(MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_NESSUN_VINCITORE"])

    def _stampa_righe(self, righe: tuple) -> None:
        """Stampa ogni riga della tupla su stdout (una riga per elemento).

        Args:
            righe: Tupla di stringhe da stampare.
        """
        for riga in righe:
            print(riga)
