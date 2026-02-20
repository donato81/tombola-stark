"""Interfaccia utente da terminale per Tombola Stark.

Implementa il flusso completo:
  Fase 1 (Start Menu, stati A→E): configurazione pre-partita accessibile.
  Fase 2 (Game Loop, stati F→H): ciclo di gioco interattivo v0.9.0.

Compatibile con screen reader NVDA/JAWS/Orca.
Pattern di riferimento: bingo_game/ui/locales/it.py

Version: v0.9.0
"""
from __future__ import annotations

import logging

from bingo_game.game_controller import (
    avvia_partita_sicura,
    crea_partita_standard,
    ottieni_stato_sintetico,
)
from bingo_game.ui.locales import MESSAGGI_CONTROLLER
from bingo_game.ui.locales.it import MESSAGGI_CONFIGURAZIONE, MESSAGGI_ERRORI
from bingo_game.events.codici_controller import (
    CTRL_AVVIO_FALLITO_GENERICO,
    CTRL_TURNO_NON_IN_CORSO,
    CTRL_NUMERI_ESAURITI,
    CTRL_TURNO_FALLITO_GENERICO,
)
from bingo_game.ui.renderers.renderer_terminal import TerminalRenderer
from bingo_game.ui.tui.game_loop import GameLoop

logger = logging.getLogger(__name__)

_LUNGHEZZA_MAX_NOME = 15
_BOT_MIN = 1
_BOT_MAX = 7
_CARTELLE_MIN = 1
_CARTELLE_MAX = 6


class TerminalUI:
    """Interfaccia utente da terminale per la configurazione e il gioco.

    Implementa il flusso completo:
    - Start Menu (stati A→E): raccolta configurazione e avvio partita.
    - Game Loop (stati F→H): delegato a GameLoop per il ciclo di gioco.

    Attributes:
        _renderer: Istanza di TerminalRenderer (condivisa col GameLoop).

    Note:
        Consuma esclusivamente il Controller (Application Layer).
        Nessun import diretto dal Domain Layer.

    Version: v0.9.0
    """

    def __init__(self) -> None:
        """Inizializza TerminalUI con il renderer terminale."""
        self._renderer = TerminalRenderer()
        logger.debug("[TUI] TerminalUI inizializzata.")

    # ------------------------------------------------------------------
    # Entry point pubblico
    # ------------------------------------------------------------------

    def avvia(self) -> None:
        """Avvia il flusso completo: configurazione + game loop.

        Esegue gli stati A→E (start menu), poi delega il game loop
        a GameLoop.avvia() se la partita viene avviata correttamente.
        """
        logger.info("[TUI] Avvio configurazione partita.")
        self._mostra_benvenuto()
        nome = self._chiedi_nome()
        numero_bot = self._chiedi_bot()
        numero_cartelle = self._chiedi_cartelle()
        partita = self._avvia_partita(nome, numero_bot, numero_cartelle)
        if partita is not None:
            logger.info("[TUI] Avvio game loop.")
            game_loop = GameLoop(partita, self._renderer)
            game_loop.avvia()

    # ------------------------------------------------------------------
    # Stati della macchina a stati (Start Menu A→E)
    # ------------------------------------------------------------------

    def _mostra_benvenuto(self) -> None:
        """Stato A: BENVENUTO — mostra il messaggio di apertura."""
        logger.debug("[TUI] Stato A: BENVENUTO")
        self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_BENVENUTO"])

    def _chiedi_nome(self) -> str:
        """Stato B: ATTESA_NOME — raccoglie e valida il nome del giocatore.

        Returns:
            str: Nome valido dopo strip, non vuoto e di lunghezza <= 15.
        """
        logger.debug("[TUI] Stato B: ATTESA_NOME")
        while True:
            input_raw = self._chiedi_input("CONFIG_RICHIESTA_NOME")
            nome = input_raw.strip()
            logger.debug("[TUI] Nome dopo strip: '%s' (len=%d)", nome, len(nome))
            if len(nome) == 0:
                logger.warning("[TUI] Validazione nome: vuoto dopo strip.")
                self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_NOME_VUOTO"])
                continue
            if len(nome) > _LUNGHEZZA_MAX_NOME:
                logger.warning(
                    "[TUI] Validazione nome: troppo lungo (%d > %d).",
                    len(nome),
                    _LUNGHEZZA_MAX_NOME,
                )
                self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_NOME_TROPPO_LUNGO"])
                continue
            logger.debug("[TUI] Nome valido acquisito: '%s'", nome)
            return nome

    def _chiedi_bot(self) -> int:
        """Stato C: ATTESA_BOT — raccoglie e valida il numero di bot.

        Returns:
            int: Numero di bot valido compreso tra 1 e 7.
        """
        logger.debug("[TUI] Stato C: ATTESA_BOT")
        while True:
            input_raw = self._chiedi_input("CONFIG_RICHIESTA_BOT")
            try:
                valore = int(input_raw)
            except ValueError:
                logger.warning("[TUI] Validazione bot: tipo non valido (input='%s').", input_raw)
                self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])
                continue
            if not (_BOT_MIN <= valore <= _BOT_MAX):
                logger.warning(
                    "[TUI] Validazione bot: fuori range (%d non in [%d, %d]).",
                    valore, _BOT_MIN, _BOT_MAX,
                )
                self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_BOT_RANGE"])
                continue
            logger.debug("[TUI] Numero bot valido: %d", valore)
            return valore

    def _chiedi_cartelle(self) -> int:
        """Stato D: ATTESA_CARTELLE — raccoglie e valida il numero di cartelle.

        Returns:
            int: Numero di cartelle valido compreso tra 1 e 6.
        """
        logger.debug("[TUI] Stato D: ATTESA_CARTELLE")
        while True:
            input_raw = self._chiedi_input("CONFIG_RICHIESTA_CARTELLE")
            try:
                valore = int(input_raw)
            except ValueError:
                logger.warning(
                    "[TUI] Validazione cartelle: tipo non valido (input='%s').", input_raw
                )
                self._stampa_righe(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])
                continue
            if not (_CARTELLE_MIN <= valore <= _CARTELLE_MAX):
                logger.warning(
                    "[TUI] Validazione cartelle: fuori range (%d non in [%d, %d]).",
                    valore, _CARTELLE_MIN, _CARTELLE_MAX,
                )
                self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_ERRORE_CARTELLE_RANGE"])
                continue
            logger.debug("[TUI] Numero cartelle valido: %d", valore)
            return valore

    def _avvia_partita(self, nome: str, numero_bot: int, numero_cartelle: int):
        """Stato E: AVVIO_PARTITA — crea e avvia la partita.

        Args:
            nome: Nome del giocatore umano (già validato).
            numero_bot: Numero di bot (già validato, 1–7).
            numero_cartelle: Numero di cartelle del giocatore (già validato, 1–6).

        Returns:
            Partita | None: la partita avviata, oppure None se l'avvio fallisce.
        """
        logger.debug("[TUI] Stato E: AVVIO_PARTITA")
        self._stampa_righe(MESSAGGI_CONFIGURAZIONE["CONFIG_CONFERMA_AVVIO"])
        partita = crea_partita_standard(
            nome_giocatore_umano=nome,
            num_cartelle_umano=numero_cartelle,
            num_bot=numero_bot,
        )
        esito = avvia_partita_sicura(partita)
        if not esito:
            self._stampa_righe((MESSAGGI_CONTROLLER[CTRL_AVVIO_FALLITO_GENERICO],))
            logger.error("[TUI] Avvio partita fallito — esito=False da avvia_partita_sicura.")
            return None
        logger.info(
            "[TUI] Configurazione completata. nome='%s', bot=%d, cartelle=%d.",
            nome, numero_bot, numero_cartelle,
        )
        return partita

    # ------------------------------------------------------------------
    # Helper privati
    # ------------------------------------------------------------------

    def _stampa_righe(self, righe: tuple[str, ...]) -> None:
        """Stampa su stdout ogni riga della tupla ricevuta.

        Args:
            righe: Tupla di stringhe da stampare, una per riga.
        """
        for riga in righe:
            print(riga)

    def _ottieni_stato_sicuro(self, partita) -> dict | None:
        """Helper sicuro per ottieni_stato_sintetico."""
        try:
            return ottieni_stato_sintetico(partita)
        except ValueError as e:
            logger.error("[TUI] Errore critico ottieni_stato_sintetico: %s", e)
            self._stampa_righe((MESSAGGI_CONTROLLER[CTRL_TURNO_FALLITO_GENERICO],))
            return None

    def _chiedi_input(self, chiave_prompt: str) -> str:
        """Mostra il prompt associato alla chiave e acquisisce l'input dell'utente.

        Args:
            chiave_prompt: Chiave in MESSAGGI_CONFIGURAZIONE il cui primo elemento è
                           il testo del prompt da mostrare all'utente.

        Returns:
            str: Stringa grezza letta da stdin (senza strip).
        """
        return input(MESSAGGI_CONFIGURAZIONE[chiave_prompt][0])
