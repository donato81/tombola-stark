"""
Modulo: bingo_game.game_controller

Controller di alto livello per la gestione di una partita di tombola/bingo.

Questo modulo si pone sopra al motore di gioco (Tabellone, Cartella,
GiocatoreBase/GiocatoreUmano/GiocatoreAutomatico, Partita) e fornisce
funzioni di comodo per:

- creare una partita standard (tabellone + giocatori + cartelle);
- avviare la partita in modo sicuro, gestendo eventuali eccezioni;
- eseguire un turno di gioco e restituire un dizionario pronto per l'interfaccia;
- ottenere una fotografia sintetica dello stato della partita;
- ottenere il giocatore umano dalla partita (v0.9.0).

L'obiettivo è separare la logica del "cosa succede" (motore) dalla logica
del "come viene presentato" (interfaccia da terminale, screen reader, ecc.).
"""

from __future__ import annotations
#import dei tipi di dato necessari
from typing import List, Optional, Dict, Any
#import della libreria random per la generazione di numeri casuali.
import random
import logging
# Import delle classi di gioco
from bingo_game.tabellone import Tabellone
from bingo_game.cartella import Cartella
from bingo_game.partita import Partita
from bingo_game.players import GiocatoreBase, GiocatoreUmano, GiocatoreAutomatico

# Import delle eccezioni per la gestione "sicura" delle operazioni
from bingo_game.exceptions import (
    #per partita
    PartitaException,
    PartitaGiocatoriInsufficientiException,
    PartitaGiaIniziataException,
    PartitaNonInCorsoException,
    PartitaNumeriEsauritiException,
    #per game_controller
    ControllerNomeGiocatoreException,
    ControllerCartelleNegativeException,
    ControllerBotNegativeException,
    ControllerBotExcessException,
)

# Import sistema di logging centralizzato
from bingo_game.logging import GameLogger


# =========================
# Sub-logger per categoria
# =========================

# Sub-logger per categoria — figli del logger radice tombola_stark
# Nessuna configurazione necessaria: ereditano handler e livello dal padre
_logger_game   = logging.getLogger("tombola_stark.game")
_logger_prizes = logging.getLogger("tombola_stark.prizes")
_logger_system = logging.getLogger("tombola_stark.system")
_logger_errors = logging.getLogger("tombola_stark.errors")

# Stato di sessione — variabili di modulo (reset in crea_partita_standard)
_turno_corrente: int = 0
_premi_totali: int = 0


# =========================
# Helper interno per logging sicuro
# =========================

# Track se abbiamo già loggato la terminazione per evitare duplicati
_partita_terminata_logged: bool = False

def _log_safe(message: str, level: str = "info", *args,
              logger: logging.Logger | None = None) -> None:
    """Scrive nel log senza mai propagare eccezioni al chiamante.

    Args:
        message: Messaggio da registrare.
        level: Livello logging ('info', 'warning', 'debug', 'error').
        *args: Argomenti per il formato stringa del logger.
        logger: Sub-logger specifico. Se None, usa il logger radice.

    Version:
        v0.4.0: Helper interno per logging sicuro nel controller
        v0.5.0: Aggiunto parametro logger per supporto sub-logger
    """
    try:
        target = logger or GameLogger.get_instance()
        getattr(target, level)(message, *args)
    except Exception:  # noqa: BLE001
        pass


def _log_prize_event(evento: dict) -> None:
    """Logga un singolo evento di vincita dalla lista premi_nuovi.

    Args:
        evento: Dizionario con chiavi 'giocatore', 'cartella', 'premio', 'riga'.
                Formato come da API Partita.verifica_premi().

    Version:
        v0.5.0: Prima implementazione
    """
    premio = evento.get("premio", "sconosciuto")
    giocatore = evento.get("giocatore", "?")
    cartella = evento.get("cartella", "?")
    riga = evento.get("riga")

    if premio == "tombola":
        _log_safe(
            "[PRIZE] TOMBOLA! — giocatore='%s', cartella=%s",
            "info", giocatore, cartella, logger=_logger_prizes
        )
    else:
        _log_safe(
            "[PRIZE] %s — giocatore='%s', cartella=%s, riga=%s",
            "info", premio.upper(), giocatore, cartella, riga,
            logger=_logger_prizes
        )


def _log_game_summary(partita: Partita) -> None:
    """Logga il riepilogo finale della partita al termine.

    Scrive un blocco INFO con le statistiche essenziali:
    turni giocati, numeri estratti, premi assegnati, vincitore (se tombola).

    Args:
        partita: L'istanza Partita terminata da cui leggere lo stato finale.

    Version:
        v0.5.0: Prima implementazione
    """
    try:
        stato = ottieni_stato_sintetico(partita)
        giocatori = stato.get("giocatori", [])
        vincitore = next(
            (g["nome"] for g in giocatori if g.get("ha_tombola")), None
        )

        _log_safe(
            "[GAME] === RIEPILOGO PARTITA ===",
            "info", logger=_logger_game
        )
        _log_safe(
            "[GAME] Turni giocati: %d | Numeri estratti: %d/90",
            "info", _turno_corrente, len(stato.get("numeri_estratti", [])),
            logger=_logger_game
        )
        _log_safe(
            "[PRIZE] Riepilogo premi: %d premi totali assegnati",
            "info", _premi_totali, logger=_logger_prizes
        )
        if vincitore:
            _log_safe(
                "[PRIZE] Vincitore TOMBOLA: '%s'",
                "info", vincitore, logger=_logger_prizes
            )
        else:
            _log_safe(
                "[GAME] Partita senza vincitore (numeri esauriti)",
                "info", logger=_logger_game
            )
    except Exception:
        pass  # Il riepilogo non deve mai interrompere la chiusura


# =========================
# Sezione 1: Creazione oggetti
# =========================

def crea_tabellone_standard() -> Tabellone:
    """
    Crea e ritorna un'istanza standard di Tabellone.

    Per la tombola italiana classica:
    - numeri da 1 a 90
    - tabellone inizialmente pieno (nessun numero estratto)

    Ritorna:
    - Tabellone: tabellone pronto all'uso per una partita standard.
    """
    return Tabellone()


def assegna_cartelle_a_giocatore(giocatore: GiocatoreBase, num_cartelle: int) -> None:
    """
    Assegna un certo numero di cartelle a un giocatore.

    Per ciascuna cartella:
    - crea una nuova istanza di Cartella;
    - la aggiunge al giocatore tramite GiocatoreBase.aggiungi_cartella().

    Parametri:
    - giocatore: GiocatoreBase
    - num_cartelle: int

    Raises:
    - ControllerCartelleNegativeException: Se num_cartelle è negativo.
    """
    if num_cartelle < 0:
        raise ControllerCartelleNegativeException(num_cartelle)

    for _ in range(num_cartelle):
        nuova_cartella = Cartella()
        giocatore.aggiungi_cartella(nuova_cartella)


def crea_giocatore_umano(nome: str, num_cartelle: int = 1, id_giocatore: Optional[int] = None) -> GiocatoreUmano:
    """
    Crea un nuovo giocatore umano, assegnandogli un ID (se disponibile) e le cartelle richieste.

    Raises:
    - ControllerNomeGiocatoreException: Se il nome è vuoto.
    - ControllerCartelleNegativeException: Se num_cartelle è negativo.
    """
    if not nome or not nome.strip():
        raise ControllerNomeGiocatoreException(nome)

    giocatore = GiocatoreUmano(nome=nome, id_giocatore=id_giocatore)
    assegna_cartelle_a_giocatore(giocatore, num_cartelle)
    return giocatore


def crea_giocatori_automatici(num_bot: int = 1) -> List[GiocatoreAutomatico]:
    """
    Crea una lista di giocatori automatici (bot) per la partita di tombola.

    Raises:
    - ControllerBotNegativeException: Se num_bot < 0.
    - ControllerBotExcessException: Se num_bot > 7 (limite partita).
    """
    if num_bot < 0:
        raise ControllerBotNegativeException(num_bot)

    if num_bot > 7:
        raise ControllerBotExcessException()

    num_bot_effettivi = max(1, num_bot)
    lista_bot: List[GiocatoreAutomatico] = []

    for indice in range(num_bot_effettivi):
        nome_bot = f"Bot {indice + 1}"
        bot = GiocatoreAutomatico(nome=nome_bot)
        num_cartelle_bot = random.randint(1, 6)
        assegna_cartelle_a_giocatore(bot, num_cartelle_bot)
        lista_bot.append(bot)

    return lista_bot


def crea_partita_standard(
    nome_giocatore_umano: str = "Giocatore 1",
    num_cartelle_umano: int = 1,
    num_bot: int = 1
) -> Partita:
    """
    Crea una partita di tombola standard completamente configurata e pronta per essere avviata.

    Raises:
    - ControllerNomeGiocatoreException: Se nome_giocatore_umano è vuoto.
    - ControllerCartelleNegativeException: Se num_cartelle_umano < 0.
    - ControllerBotNegativeException: Se num_bot < 0.
    - ControllerBotExcessException: Se num_bot > 7.
    """
    global _partita_terminata_logged, _turno_corrente, _premi_totali

    # Reset flag terminazione e contatori per nuova partita
    _partita_terminata_logged = False
    _turno_corrente = 0
    _premi_totali = 0

    if not nome_giocatore_umano or not nome_giocatore_umano.strip():
        raise ControllerNomeGiocatoreException(nome_giocatore_umano)

    if num_cartelle_umano < 0:
        raise ControllerCartelleNegativeException(num_cartelle_umano)

    if num_bot < 0:
        raise ControllerBotNegativeException(num_bot)
    if num_bot > 7:
        raise ControllerBotExcessException()

    _log_safe("[GAME] crea_partita_standard: tabellone creato.", "debug", logger=_logger_game)
    tabellone = crea_tabellone_standard()

    _log_safe("[GAME] crea_partita_standard: giocatore umano '%s' creato, cartelle=%d.", "debug", nome_giocatore_umano, num_cartelle_umano, logger=_logger_game)
    giocatore_umano = crea_giocatore_umano(
        nome=nome_giocatore_umano,
        num_cartelle=num_cartelle_umano
    )

    num_bot_effettivi = max(1, num_bot)
    _log_safe("[GAME] crea_partita_standard: %d bot automatici creati.", "debug", num_bot_effettivi, logger=_logger_game)
    lista_bot = crea_giocatori_automatici(num_bot_effettivi)

    tutti_i_giocatori = [giocatore_umano] + lista_bot
    _log_safe("[GAME] crea_partita_standard: %d giocatori totali.", "debug", len(tutti_i_giocatori), logger=_logger_game)

    _log_safe("[GAME] crea_partita_standard: inizializzazione Partita.", "debug", logger=_logger_game)
    partita = Partita(tabellone, tutti_i_giocatori)

    if not hasattr(partita, 'tabellone') or partita.tabellone is None:
        raise RuntimeError("Errore critico: tabellone non inizializzato nella partita")
    if len(partita.get_giocatori()) != len(tutti_i_giocatori):
        raise RuntimeError("Errore critico: giocatori non inizializzati nella partita")

    _log_safe("[GAME] crea_partita_standard: partita creata con successo.", "debug", logger=_logger_game)
    _log_safe(
        "[GAME] Partita creata — giocatore='%s', cartelle=%d, bot=%d, tot_giocatori=%d",
        "info", nome_giocatore_umano, num_cartelle_umano, num_bot_effettivi,
        len(tutti_i_giocatori),
        logger=_logger_game
    )

    return partita


# =========================
# Sezione 2: Operazioni di alto livello sulla partita
# =========================

def avvia_partita_sicura(partita: Partita) -> bool:
    """
    Avvia la partita in modo sicuro, intercettando eccezioni comuni.

    Ritorna:
    - True: avvio riuscito, partita ora in stato "in_corso"
    - False: avvio fallito
    """
    if not isinstance(partita, Partita):
        _log_safe(f"[ERR] avvia_partita_sicura: parametro non e' Partita. tipo='{type(partita).__name__}'.", "error", logger=_logger_errors)
        return False

    try:
        partita.avvia_partita()

        if partita.get_stato_partita() == "in_corso":
            _log_safe(
                "[GAME] Partita avviata — stato: %s, giocatori: %d",
                "info", partita.get_stato_partita(), partita.get_numero_giocatori(),
                logger=_logger_game
            )
            return True
        else:
            _log_safe(f"[SYS] avvia_partita_sicura: stato post-avvio inatteso='{partita.get_stato_partita()}'.", "warning", logger=_logger_system)
            return False

    except PartitaGiocatoriInsufficientiException as exc:
        _log_safe("[GAME] Avvio fallito: %s", "warning", str(exc), logger=_logger_game)
        _log_safe("[ERR] Eccezione avvio partita: %s — tipo: %s", "warning", str(exc), type(exc).__name__, logger=_logger_errors)
        return False

    except PartitaGiaIniziataException as exc:
        _log_safe("[GAME] Avvio fallito: %s", "warning", str(exc), logger=_logger_game)
        _log_safe("[ERR] Eccezione avvio partita: %s — tipo: %s", "warning", str(exc), type(exc).__name__, logger=_logger_errors)
        return False

    except PartitaException as exc:
        _log_safe("[GAME] Avvio fallito: %s", "warning", str(exc), logger=_logger_game)
        _log_safe("[ERR] Eccezione avvio partita: %s — tipo: %s", "warning", str(exc), type(exc).__name__, logger=_logger_errors)
        return False

    except Exception as exc:
        _log_safe(f"[ERR] avvia_partita_sicura: eccezione imprevista. tipo='{type(exc).__name__}'.", "error", logger=_logger_errors)
        _log_safe("[GAME] Avvio fallito (errore imprevisto): %s", "warning", str(exc), logger=_logger_game)
        raise


def esegui_turno_sicuro(partita: Partita) -> Optional[Dict[str, Any]]:
    """
    Esegue un turno di gioco in modo completamente sicuro.

    Ritorna:
    - Dict[str, Any]: dizionario completo del turno se successo.
    - None: se ERRORE.
    """
    if not isinstance(partita, Partita):
        _log_safe(f"[ERR] esegui_turno_sicuro: parametro non e' Partita. tipo='{type(partita).__name__}'.", "error", logger=_logger_errors)
        return None

    stato_attuale = partita.get_stato_partita()
    if stato_attuale != "in_corso":
        _log_safe(f"[GAME] esegui_turno_sicuro: stato '{stato_attuale}' non in corso.", "warning", logger=_logger_game)
        return None

    global _turno_corrente, _premi_totali
    try:
        risultato_turno = partita.esegui_turno()
        _turno_corrente += 1

        if not isinstance(risultato_turno, dict):
            _log_safe("[SYS] esegui_turno_sicuro: risultato turno non valido (non dict).", "warning", logger=_logger_system)
            return None

        chiavi_essenziali = {
            "numero_estratto", "stato_partita_prima", "stato_partita_dopo",
            "tombola_rilevata", "partita_terminata", "premi_nuovi"
        }
        if not chiavi_essenziali.issubset(risultato_turno.keys()):
            _log_safe("[SYS] esegui_turno_sicuro: dizionario turno incompleto.", "warning", logger=_logger_system)
            return None

        _log_safe(
            "[GAME] Turno #%d — estratto: %d, avanzamento: %.1f%%",
            "debug", _turno_corrente,
            risultato_turno["numero_estratto"],
            ((_turno_corrente / 90) * 100),
            logger=_logger_game
        )
        _log_safe(
            "[GAME] Stato: estratti=%d/90, premi_sessione=%d",
            "debug", partita.tabellone.get_conteggio_estratti(), _premi_totali,
            logger=_logger_game
        )

        for evento in risultato_turno.get("premi_nuovi", []):
            _premi_totali += 1
            _log_prize_event(evento)

        reclami_bot = risultato_turno.get("reclami_bot", [])
        for reclamo_esito in reclami_bot:
            try:
                nome_bot = reclamo_esito.get("nome_giocatore", "?")
                id_bot = reclamo_esito.get("id_giocatore", "?")
                reclamo = reclamo_esito.get("reclamo")
                successo = reclamo_esito.get("successo", False)

                if reclamo is not None:
                    tipo_premio = reclamo.tipo
                    cartella = reclamo.indice_cartella
                    riga = reclamo.indice_riga

                    if successo:
                        _log_safe(
                            "[PRIZE] Bot '%s' (id=%s) dichiara %s — cartella=%s, riga=%s → ACCETTATO",
                            "info", nome_bot, id_bot, tipo_premio.upper(), cartella, riga,
                            logger=_logger_prizes
                        )
                    else:
                        _log_safe(
                            "[GAME]  Bot '%s' (id=%s) dichiara %s — cartella=%s, riga=%s → RIGETTATO",
                            "info", nome_bot, id_bot, tipo_premio.upper(), cartella, riga,
                            logger=_logger_game
                        )
            except Exception:
                pass

        if risultato_turno.get("tombola_rilevata"):
            _log_safe(
                "[GAME] Partita terminata per TOMBOLA al turno #%d",
                "info", _turno_corrente, logger=_logger_game
            )
            _log_game_summary(partita)

        elif risultato_turno.get("partita_terminata"):
            _log_safe(
                "[GAME] Partita terminata per NUMERI ESAURITI al turno #%d",
                "info", _turno_corrente, logger=_logger_game
            )
            _log_safe(
                "[ERR] Numeri esauriti al turno #%d",
                "warning", _turno_corrente, logger=_logger_errors
            )
            _log_game_summary(partita)

        return risultato_turno

    except PartitaNonInCorsoException as exc:
        _log_safe(f"[GAME] esegui_turno_sicuro: turno fallito, partita non in corso. tipo='{type(exc).__name__}'.", "warning", logger=_logger_game)
        _log_safe("[ERR] Eccezione turno #%d: %s — tipo: %s", "warning", _turno_corrente, str(exc), type(exc).__name__, logger=_logger_errors)
        return None

    except PartitaNumeriEsauritiException as exc:
        _log_safe(f"[GAME] esegui_turno_sicuro: numeri esauriti. tipo='{type(exc).__name__}'.", "warning", logger=_logger_game)
        _log_safe("[ERR] Numeri esauriti al turno #%d — %s", "warning", _turno_corrente, str(exc), logger=_logger_errors)
        return None

    except PartitaException as exc:
        _log_safe(f"[GAME] esegui_turno_sicuro: errore partita durante turno. tipo='{type(exc).__name__}'.", "warning", logger=_logger_game)
        _log_safe("[ERR] Eccezione turno #%d: %s — tipo: %s", "warning", _turno_corrente, str(exc), type(exc).__name__, logger=_logger_errors)
        return None

    except Exception as exc:
        _log_safe(f"[ERR] esegui_turno_sicuro: eccezione imprevista. tipo='{type(exc).__name__}'.", "error", logger=_logger_errors)
        _log_safe("[ERR] Eccezione imprevista turno #%d: %s — tipo: %s", "warning", _turno_corrente, str(exc), type(exc).__name__, logger=_logger_errors)
        raise


def ottieni_stato_sintetico(partita: Partita) -> Dict[str, Any]:
    """
    Ritorna una fotografia completa e validata dello stato della partita.

    Raises:
    - ValueError: parametro non-Partita o stato incompleto/incoerente
    """
    if not isinstance(partita, Partita):
        raise ValueError("ottieni_stato_sintetico: parametro deve essere Partita, ricevuto: " + str(type(partita)))

    try:
        stato_completo = partita.get_stato_completo()
    except Exception as exc:
        raise ValueError(f"Errore interno Partita.get_stato_completo(): {exc}") from exc

    if not isinstance(stato_completo, dict):
        raise ValueError("Partita.get_stato_completo() non ha ritornato un dizionario valido")

    chiavi_obbligatorie = {
        "stato_partita", "ultimo_numero_estratto", "numeri_estratti",
        "giocatori", "premi_gia_assegnati"
    }
    chiavi_mancanti = chiavi_obbligatorie - set(stato_completo.keys())
    if chiavi_mancanti:
        raise ValueError(f"Stato incompleto, mancano chiavi: {chiavi_mancanti}")

    numeri_estratti = stato_completo["numeri_estratti"]
    if not isinstance(numeri_estratti, list):
        raise ValueError("numeri_estratti non è lista")

    giocatori = stato_completo["giocatori"]
    if not isinstance(giocatori, list):
        raise ValueError("giocatori non è lista")

    stato_partita = stato_completo["stato_partita"]
    stati_validi = {"non_iniziata", "in_corso", "terminata"}
    if stato_partita not in stati_validi:
        raise ValueError(f"stato_partita invalido: '{stato_partita}', deve essere: {stati_validi}")

    premi_ordinati = sorted(stato_completo["premi_gia_assegnati"])
    stato_completo["premi_gia_assegnati"] = premi_ordinati

    _log_safe("[GAME] ottieni_stato_sintetico: stato='%s', estratti=%d, giocatori=%d.", "debug", stato_partita, len(numeri_estratti), len(giocatori), logger=_logger_game)

    return stato_completo


def ha_partita_tombola(partita: Partita) -> bool:
    """
    Verifica se almeno un giocatore della partita ha completato una tombola.

    Raises:
    - ValueError: parametro non-Partita
    """
    if not isinstance(partita, Partita):
        raise ValueError(
            f"ha_partita_tombola: parametro deve essere Partita, "
            f"ricevuto: {type(partita).__name__}"
        )

    stato_partita = partita.get_stato_partita()
    if stato_partita not in {"non_iniziata", "in_corso", "terminata"}:
        raise ValueError(f"Stato partita invalido: '{stato_partita}'")

    _log_safe("[GAME] ha_partita_tombola: %d giocatori, stato='%s'.", "debug", partita.get_numero_giocatori(), stato_partita, logger=_logger_game)

    ha_tombola = partita.has_tombola()

    if ha_tombola:
        _log_safe("[GAME] ha_partita_tombola: esito=True.", "debug", logger=_logger_game)
    else:
        _log_safe("[GAME] ha_partita_tombola: nessuna tombola, gioco continua.", "debug", logger=_logger_game)

    return ha_tombola


def partita_terminata(partita: Partita) -> bool:
    """
    Verifica se la partita è nello stato 'terminata' (condizione di uscita).

    Raises:
    - ValueError: parametro non-Partita o stato invalido
    """
    global _partita_terminata_logged

    if not isinstance(partita, Partita):
        raise ValueError(
            f"partita_terminata: parametro deve essere Partita, "
            f"ricevuto: {type(partita).__name__}"
        )

    try:
        stato_partita = partita.get_stato_partita()
    except Exception as exc:
        raise ValueError(f"Errore lettura stato partita: {exc}") from exc

    stati_validi = {"non_iniziata", "in_corso", "terminata"}
    if stato_partita not in stati_validi:
        raise ValueError(
            f"Stato partita invalido '{stato_partita}', "
            f"valori ammessi: {stati_validi}"
        )

    _log_safe("[GAME] partita_terminata: stato='%s'.", "debug", stato_partita, logger=_logger_game)

    is_terminata = partita.is_terminata()

    if is_terminata:
        if not _partita_terminata_logged:
            _log_safe("Partita terminata.", "info")
            _partita_terminata_logged = True
    else:
        _log_safe("[GAME] partita_terminata: partita in corso, continua il loop.", "debug", logger=_logger_game)

    return is_terminata


# =========================
# Sezione 3: Helper per la TUI — v0.9.0
# =========================

def ottieni_giocatore_umano(partita: Partita) -> Optional[GiocatoreUmano]:
    """Ritorna il primo GiocatoreUmano trovato nella partita, oppure None.

    Questa funzione è l'interfaccia ufficiale per la TUI Game Loop: permette
    alla TUI di ottenere un riferimento al giocatore umano senza importare
    direttamente dal Domain Layer (GiocatoreUmano è usato solo nel Controller).

    Args:
        partita: Istanza Partita valida (qualsiasi stato).

    Returns:
        GiocatoreUmano: primo giocatore umano trovato in partita.get_giocatori().
        None: se nessun GiocatoreUmano è presente o partita non è valida.

    Note:
        Nessun side effect. Nessuna eccezione propagata all'esterno.
        Compatibile con partita non ancora avviata (stato 'non_iniziata').

    Version:
        v0.9.0: Prima implementazione.
    """
    if not isinstance(partita, Partita):
        _log_safe(
            "[ERR] ottieni_giocatore_umano: parametro non e' Partita. tipo='%s'.",
            "warning", type(partita).__name__, logger=_logger_errors
        )
        return None

    try:
        for giocatore in partita.get_giocatori():
            if isinstance(giocatore, GiocatoreUmano):
                _log_safe(
                    "[GAME] ottieni_giocatore_umano: trovato '%s'.",
                    "debug", giocatore.nome, logger=_logger_game
                )
                return giocatore
    except Exception as exc:
        _log_safe(
            "[ERR] ottieni_giocatore_umano: eccezione durante get_giocatori(). %s",
            "error", str(exc), logger=_logger_errors
        )
        return None

    _log_safe(
        "[GAME] ottieni_giocatore_umano: nessun GiocatoreUmano trovato.",
        "warning", logger=_logger_game
    )
    return None
