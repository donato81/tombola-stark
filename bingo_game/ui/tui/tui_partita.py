"""
Modulo: bingo_game.ui.tui.tui_partita

TUI Game Loop interattivo a funzioni — v0.10.0.

Implementa la macchina a stati `_loop_partita` che governa ogni turno di gioco.
Input: tasto singolo via msvcrt (Windows), gestito da tui_commander.
Ogni tasto è mappato a un ComandoTasto che descrive il comportamento atteso.

Vincoli architetturali:
- Nessun import di classi Domain (GiocatoreUmano, Partita, Tabellone, Cartella).
- Accesso al dominio esclusivamente tramite bingo_game.game_controller e i metodi
  del giocatore umano recuperato tramite ottieni_giocatore_umano().
- Solo il tasto P chiama esegui_turno_sicuro: i comandi informativi non avanzano il turno.
- Il tasto X richiede sempre conferma esplicita e logga WARNING.
- Ogni riga di output è autonoma e <= 120 caratteri (screen reader compatibility).

Routing delle azioni:
    AZIONE_DIRETTA      — chiamata al metodo GiocatoreUmano (o esegui_turno_sicuro per P).
    RICHIEDE_PROMPT_NUM — prompt input() -> intero -> metodo con argomento.
    RICHIEDE_CONFERMA   — prompt S/N -> esci se confermato (tasto X).
    SELEZIONA_CARTELLA  — imposta_focus_cartella(valore) direttamente (tasti 1-6).
    TASTO_NON_VALIDO    — mostra messaggio errore.

Version:
    v0.9.0: Prima implementazione (comandi testuali).
    v0.10.0: Tasti rapidi via msvcrt (tui_commander).
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
from bingo_game.ui.tui.tui_commander import (
    ComandoTasto,
    TipoComando,
    comando_da_tasto,
    leggi_tasto,
)

_logger_tui = logging.getLogger("tombola_stark.tui")
_renderer = TerminalRenderer()

# ---------------------------------------------------------------------------
# Routing: insiemi di nomi-metodo che richiedono argomenti speciali
# ---------------------------------------------------------------------------

# Metodi AZIONE_DIRETTA su GiocatoreUmano che richiedono (tabellone) come unico arg.
_METODI_DIRETTI_CON_TABELLONE: frozenset = frozenset({
    "comunica_ultimo_numero_estratto",
    "visualizza_ultimi_numeri_estratti",
    "riepilogo_tabellone",
    "lista_numeri_estratti",
})

# Metodi RICHIEDE_PROMPT_NUM su GiocatoreUmano che richiedono (numero, tabellone).
_METODI_PROMPT_CON_TABELLONE: frozenset = frozenset({
    "segna_numero_manuale",
    "verifica_numero_estratto",
})


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
        try:
            giocatore.imposta_focus_cartella(1)
            _logger_tui.debug("[LOOP] Focus impostato su cartella 1.")
        except Exception as exc:
            _logger_tui.warning("[LOOP] Impossibile impostare focus auto: %s", exc)
            if len(giocatore.cartelle) == 1:
                giocatore._indice_cartella_focus = 0
                _logger_tui.debug("[LOOP] Focus fallback impostato su cartella 1 (cartella singola).")

    while not partita_terminata(partita):
        tasto = leggi_tasto()
        _logger_tui.debug("[LOOP] tasto letto: %r", tasto)
        cmd = comando_da_tasto(tasto)

        if cmd.tipo == TipoComando.TASTO_NON_VALIDO:
            _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_TASTO_NON_VALIDO"][0])

        elif cmd.tipo == TipoComando.SELEZIONA_CARTELLA:
            _esegui_seleziona_cartella(giocatore, cmd.valore)

        elif cmd.tipo == TipoComando.RICHIEDE_CONFERMA:
            # Solo TASTO_X (esci): conferma S/N prima di uscire.
            if _esegui_conferma_esci(partita, turno):
                break

        elif cmd.tipo == TipoComando.AZIONE_DIRETTA:
            if cmd.nome == "passa_turno":
                # Tasto P: avanza il turno estraendo il prossimo numero.
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
            else:
                # Tutti gli altri tasti AZIONE_DIRETTA: delega al giocatore.
                _esegui_azione_giocatore(cmd.nome, partita, giocatore)

        elif cmd.tipo == TipoComando.RICHIEDE_PROMPT_NUM:
            _esegui_con_prompt_numero(cmd, partita, giocatore)

    _emetti_report_finale(partita)


# ---------------------------------------------------------------------------
# Dispatch comandi tasti rapidi (v0.10.0)
# ---------------------------------------------------------------------------

def _esegui_seleziona_cartella(giocatore, numero_cartella: int) -> None:
    """Seleziona la cartella numero_cartella (1-based) come focus (tasti 1-6).

    Args:
        giocatore: Istanza GiocatoreUmano corrente (può essere None).
        numero_cartella: Numero cartella 1-based (da ComandoTasto.valore).

    Version:
        v0.10.0: Introdotto con i tasti rapidi.
    """
    if giocatore is None:
        _stampa(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"][0])
        return
    try:
        esito = giocatore.imposta_focus_cartella(numero_cartella)
        for riga in _renderer.render_esito(esito):
            _stampa(riga)
    except Exception as exc:
        _logger_tui.warning("[LOOP] _esegui_seleziona_cartella: %s", exc)
        _stampa(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"][0])


def _esegui_azione_giocatore(nome: str, partita, giocatore) -> None:
    """Esegue un'AZIONE_DIRETTA sul giocatore umano recuperando il metodo per nome.

    I metodi in _METODI_DIRETTI_CON_TABELLONE vengono chiamati con
    (partita.tabellone) come argomento. Tutti gli altri vengono chiamati
    senza argomenti.

    Args:
        nome: Nome del metodo GiocatoreUmano da invocare.
        partita: Istanza Partita corrente (per accedere a partita.tabellone).
        giocatore: Istanza GiocatoreUmano corrente (può essere None).

    Version:
        v0.10.0: Introdotto con i tasti rapidi.
    """
    if giocatore is None:
        _stampa(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"][0])
        return
    try:
        metodo = getattr(giocatore, nome, None)
        if metodo is None:
            _logger_tui.warning("[LOOP] Metodo non trovato su giocatore: %s", nome)
            return
        if nome in _METODI_DIRETTI_CON_TABELLONE:
            esito = metodo(partita.tabellone)
        else:
            esito = metodo()
        for riga in _renderer.render_esito(esito):
            _stampa(riga)
    except Exception as exc:
        _logger_tui.warning("[LOOP] _esegui_azione_giocatore '%s': %s", nome, exc)
        _stampa(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"][0])


def _esegui_con_prompt_numero(cmd: ComandoTasto, partita, giocatore) -> None:
    """Gestisce un tasto che richiede un prompt numerico prima dell'azione.

    Flusso:
        1. Mostra prompt testuale (generico; Phase 4 aggiunge chiavi specifiche).
        2. Legge input tramite input() standard (non msvcrt).
        3. Valida che sia un intero (se non lo è, mostra errore e ritorna).
        4. Chiama il metodo corrispondente su giocatore.
        5. Stampa il risultato tramite renderer.

    La validazione del range (es. 1-3 per riga, 1-9 per colonna) è delegata
    al dominio: GiocatoreUmano ritorna EsitoAzione(ok=False) con codice errore.

    Caso speciale: "annuncia_vittoria" mostra un placeholder finché il controller
    wrapper non sarà disponibile (TODO Fase 5).

    Args:
        cmd: ComandoTasto con tipo RICHIEDE_PROMPT_NUM.
        partita: Istanza Partita corrente.
        giocatore: Istanza GiocatoreUmano corrente.

    Version:
        v0.10.0: Introdotto con i tasti rapidi.
    """
    if giocatore is None:
        _stampa(MESSAGGI_ERRORI["CARTELLE_NESSUNA_ASSEGNATA"][0])
        return

    # Caso speciale: annuncia_vittoria richiede Tipo_Vittoria (enum dominio).
    # TODO (Fase 5): aggiungere wrapper in game_controller e rimuovere placeholder.
    if cmd.nome == "annuncia_vittoria":
        _logger_tui.debug("[LOOP] annuncia_vittoria: placeholder attivo (Fase 5 pendente).")
        _stampa("Comando V (annuncia vittoria): non disponibile in questa versione. Premi ? per lo stato focus.")
        return

    # Prompt generico (Phase 4 aggiunge chiavi specifiche per ogni tasto).
    _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_SEGNA_CHIEDI_NUMERO"][0])
    raw_val = input("> ").strip()

    try:
        numero = int(raw_val)
    except ValueError:
        for riga in MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]:
            _stampa(riga)
        return

    try:
        metodo = getattr(giocatore, cmd.nome)
        if cmd.nome in _METODI_PROMPT_CON_TABELLONE:
            esito = metodo(numero, partita.tabellone)
        else:
            esito = metodo(numero)
        for riga in _renderer.render_esito(esito):
            _stampa(riga)
    except Exception as exc:
        _logger_tui.warning("[LOOP] _esegui_con_prompt_numero '%s': %s", cmd.nome, exc)
        _stampa(MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"][0])


def _esegui_conferma_esci(partita, turno: int) -> bool:
    """Richiede conferma S/N e gestisce l'uscita dalla partita (tasto X).

    Usa input() standard per permettere editing della risposta.
    Se confermato logga un WARNING con il numero di turno corrente.

    Args:
        partita: Istanza Partita corrente (contesto per il log).
        turno: Numero di turno corrente, per il messaggio di allerta nel log.

    Returns:
        True se l'utente conferma l'uscita ('s'), False altrimenti.

    Version:
        v0.10.0: Introduce il tasto X al posto del comando testuale q.
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


# ---------------------------------------------------------------------------
# Comandi legacy (v0.9.0 — mantenuti per compatibilità test)
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
        _stampa(MESSAGGI_OUTPUT_UI_UMANI["LOOP_SEGNA_CHIEDI_NUMERO"][0])
        args = input("> ").strip()

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

    numero_cartella: object = "nessuna"
    giocatore = ottieni_giocatore_umano(partita)
    if giocatore is not None:
        try:
            esito_focus = giocatore.stato_focus_corrente()
            if esito_focus.ok and esito_focus.evento is not None:
                nc = getattr(esito_focus.evento, "numero_cartella", None)
                numero_cartella = nc if nc is not None else "nessuna"
        except Exception:
            pass

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
