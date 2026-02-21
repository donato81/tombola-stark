"""
Modulo: bingo_game.ui.tui.tui_partita

TUI Game Loop interattivo a funzioni — v0.9.0.

Implementa la macchina a stati `_loop_partita` che governa ogni turno di gioco.
Comandi supportati: p (prosegui), s <N> (segna), c (cartella), v (tabellone),
q (esci con conferma), ? (aiuto).

Vincoli architetturali:
- Nessun import di classi Domain (GiocatoreUmano, Partita, Tabellone, Cartella).
- Accesso al dominio esclusivamente tramite bingo_game.game_controller.
- Solo il comando `p` chiama esegui_turno_sicuro: i comandi informativi non avanzano il turno.
- Il comando `q` richiede sempre conferma esplicita e logga WARNING.
- Ogni riga di output è autonoma e ≤ 120 caratteri (screen reader compatibility).

Version:
    v0.9.0: Prima implementazione.
"""
from __future__ import annotations

import logging
from typing import List

from bingo_game.game_controller import (
    esegui_turno_sicuro,
    ottieni_giocatore_umano,
    ottieni_stato_sintetico,
    partita_terminata,
)
from bingo_game.ui.locales.it import MESSAGGI_ERRORI, MESSAGGI_OUTPUT_UI_UMANI
from bingo_game.ui.renderers.renderer_terminal import TerminalRenderer

_logger_tui = logging.getLogger("tombola_stark.tui")
_renderer = TerminalRenderer()


# ---------------------------------------------------------------------------
# Entry point pubblico
# ---------------------------------------------------------------------------

def _loop_partita(partita) -> None:
    """Macchina a stati principale del Game Loop interattivo.

    Gestisce ogni turno di gioco: accetta comandi dall'utente, dispatcha alle
    funzioni delegate, avanza il turno solo su comando `p`.

    Al termine (tombola, numeri esauriti, quit confermato) emette il report finale.

    Args:
        partita: Istanza Partita già avviata (stato 'in_corso').

    Note:
        Non importa classi Domain. Tutto l'accesso al dominio passa tramite
        game_controller.

    Version:
        v0.9.0: Prima implementazione.
    """
    turno: int = 0

    # Focus auto su prima cartella (indice 0 → numero_cartella=1 in 1-based)
    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is not None:
        giocatore.imposta_focus_cartella(1)
        _logger_tui.debug("[LOOP] Focus impostato su cartella 1.")

    while not partita_terminata(partita):
        _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_PROMPT_COMANDO"][0])
        raw = input("> ").strip()

        if not raw:
            continue

        parti = raw.split(maxsplit=1)
        cmd = parti[0].lower()
        args = parti[1] if len(parti) > 1 else ""

        if cmd == "p":
            risultato = esegui_turno_sicuro(partita)
            if risultato is None:
                _logger_tui.warning("[LOOP] esegui_turno_sicuro ha ritornato None.")
                break
            turno += 1
            numero = risultato.get("numero_estratto")
            if numero is not None:
                _stampa(
                    MESSAGGI_OUTPUT_UI_UMANI["LOOP_NUMERO_ESTRATTO"][0].format(
                        numero=numero
                    )
                )
            if risultato.get("tombola_rilevata") or risultato.get("partita_terminata"):
                break

        elif cmd == "s":
            for riga in _gestisci_segna(partita, args):
                _stampa(riga)

        elif cmd == "c":
            for riga in _gestisci_riepilogo_cartella(partita):
                _stampa(riga)

        elif cmd == "v":
            for riga in _gestisci_riepilogo_tabellone(partita):
                _stampa(riga)

        elif cmd == "q":
            if _gestisci_quit(partita, turno):
                break

        elif cmd == "?":
            for riga in _gestisci_help(partita):
                _stampa(riga)

        else:
            _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_COMANDO_NON_RICONOSCIUTO"][0])

    _emetti_report_finale(partita)


# ---------------------------------------------------------------------------
# Comandi
# ---------------------------------------------------------------------------

def _gestisci_segna(partita, args: str) -> List[str]:
    """Comando `s <N>`: segna il numero N sulla cartella in focus.

    Qualsiasi numero estratto è segnabile (flessibilità marcatura v0.9.0).

    Args:
        partita: Istanza Partita corrente.
        args: Stringa argomento del comando (es. "42").

    Returns:
        Lista di righe di feedback da stampare.

    Version:
        v0.9.0: Prima implementazione.
    """
    if not args:
        return list(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])

    try:
        numero = int(args)
    except ValueError:
        return list(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"])

    if not (1 <= numero <= 90):
        return list(MESSAGGI_ERRORI["NUMERO_NON_VALIDO"])

    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is None:
        return list(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"])

    try:
        esito = giocatore.segna_numero_manuale(numero, partita.tabellone)
        return list(_renderer.render_esito(esito))
    except Exception as exc:
        _logger_tui.warning("[LOOP] _gestisci_segna: errore — %s", exc)
        return list(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"])


def _gestisci_riepilogo_cartella(partita) -> List[str]:
    """Comando `c`: mostra il riepilogo della cartella in focus.

    Comando informativo — non avanza il turno.

    Args:
        partita: Istanza Partita corrente.

    Returns:
        Lista di righe del riepilogo da stampare.

    Version:
        v0.9.0: Prima implementazione.
    """
    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is None:
        return list(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"])

    try:
        esito = giocatore.riepilogo_cartella_corrente()
        return list(_renderer.render_esito(esito))
    except Exception as exc:
        _logger_tui.warning("[LOOP] _gestisci_riepilogo_cartella: errore — %s", exc)
        return list(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"])


def _gestisci_riepilogo_tabellone(partita) -> List[str]:
    """Comando `v`: mostra il riepilogo del tabellone.

    Comando informativo — non avanza il turno.

    Args:
        partita: Istanza Partita corrente.

    Returns:
        Lista di righe del riepilogo da stampare (almeno 2).

    Version:
        v0.9.0: Prima implementazione.
    """
    try:
        stato = ottieni_stato_sintetico(partita)
    except Exception as exc:
        _logger_tui.warning("[LOOP] _gestisci_riepilogo_tabellone: errore — %s", exc)
        return list(MESSAGGI_ERRORI["TABELLONE_NON_DISPONIBILE"])

    numeri_estratti = stato.get("numeri_estratti", [])
    estratti = len(numeri_estratti)
    totale = 90
    mancanti = totale - estratti
    percentuale = round((estratti / totale) * 100, 1) if totale else 0.0

    tpl = MESSAGGI_OUTPUT_UI_UMANI["UMANI_RIEPILOGO_TABELLONE_RIGA_1"]
    riga_1 = tpl[0].format(
        totale_estratti=estratti,
        totale_numeri=totale,
        totale_mancanti=mancanti,
        percentuale_estrazione=percentuale,
    )

    righe: List[str] = [riga_1]

    ultimo = stato.get("ultimo_numero_estratto")
    if ultimo is not None:
        righe.append(f"Ultimo estratto: {ultimo}.")
    else:
        righe.append("Nessun numero ancora estratto.")

    return righe


def _gestisci_quit(partita, turno: int = 0) -> bool:
    """Comando `q`: chiede conferma prima di uscire dalla partita.

    Se confermato logga un WARNING con il numero di turno corrente.

    Args:
        partita: Istanza Partita corrente (usato per il log di contesto).
        turno: Numero di turno corrente, per il messaggio di allerta nel log.

    Returns:
        True se l'utente conferma l'uscita, False altrimenti.

    Version:
        v0.9.0: Prima implementazione.
    """
    _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_QUIT_CONFERMA"][0])
    risposta = input("> ").strip().lower()

    if risposta == "s":
        _logger_tui.warning(
            "[ALERT] Partita interrotta dall'utente al turno #%s.", turno
        )
        return True

    _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_QUIT_ANNULLATO"][0])
    return False


def _gestisci_help(partita) -> List[str]:
    """Comando `?`: mostra l'aiuto sui comandi e la cartella in focus.

    Comando informativo — non avanza il turno.

    Args:
        partita: Istanza Partita corrente.

    Returns:
        Lista di righe: comandi disponibili + cartella in focus.

    Version:
        v0.9.0: Prima implementazione.
    """
    righe: List[str] = list(MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_COMANDI"])

    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is not None:
        indice = giocatore._indice_cartella_focus
        numero_cartella = (indice + 1) if indice is not None else "nessuna"
    else:
        numero_cartella = "nessuna"

    riga_focus = MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_FOCUS"][0].format(
        numero_cartella=numero_cartella
    )
    righe.append(riga_focus)
    return righe


# ---------------------------------------------------------------------------
# Report finale
# ---------------------------------------------------------------------------

def _costruisci_report_finale(stato: dict) -> List[str]:
    """Costruisce le righe del report finale a partire dallo stato della partita.

    Args:
        stato: Dizionario stato restituito da ottieni_stato_sintetico().

    Returns:
        Lista di righe del report (intestazione, turni, estratti, vincitore, premi).

    Version:
        v0.9.0: Prima implementazione.
    """
    righe: List[str] = []

    righe.append(MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_INTESTAZIONE"][0])

    estratti = len(stato.get("numeri_estratti", []))
    righe.append(
        MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_TURNI"][0].format(turni=estratti)
    )
    righe.append(
        MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_ESTRATTI"][0].format(
            estratti=estratti
        )
    )

    giocatori = stato.get("giocatori", [])
    vincitore = next(
        (g.get("nome") for g in giocatori if g.get("ha_tombola")), None
    )
    if vincitore:
        righe.append(
            MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_VINCITORE"][0].format(
                nome=vincitore
            )
        )
    else:
        righe.append(MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_NESSUN_VINCITORE"][0])

    premi = len(stato.get("premi_gia_assegnati", []))
    righe.append(
        MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_PREMI"][0].format(premi=premi)
    )

    return righe


def _emetti_report_finale(partita) -> None:
    """Emette su stdout il report finale di partita.

    Recupera lo stato tramite ottieni_stato_sintetico() e stampa ogni riga
    del report. In caso di errore logga un WARNING e non solleva eccezioni.

    Args:
        partita: Istanza Partita (qualsiasi stato al termine del loop).

    Version:
        v0.9.0: Prima implementazione.
    """
    try:
        stato = ottieni_stato_sintetico(partita)
    except Exception as exc:
        _logger_tui.warning("[LOOP] _emetti_report_finale: errore stato — %s", exc)
        return

    for riga in _costruisci_report_finale(stato):
        _stampa(riga)


# ---------------------------------------------------------------------------
# Helper output
# ---------------------------------------------------------------------------

def _stampa(riga: str) -> None:
    """Wrapper su print per facilitare il mock nei test.

    Args:
        riga: Stringa da stampare su stdout.

    Version:
        v0.9.0: Prima implementazione.
    """
    print(riga)
