"""
ECCEZIONI PERSONALIZZATE PER LA GESTIONE DELLA PARTITA
Modulo: bingo_game.exceptions.partita_exceptions

Questo modulo definisce tutte le eccezioni specifiche che possono essere sollevate
dalla classe Partita durante il ciclo di vita del gioco.

L'uso di eccezioni specifiche permette al livello di controllo (Controller/Interfaccia)
di reagire in modo puntuale agli errori, distinguendo ad esempio tra un problema
di configurazione (roster pieno) e un problema di stato (partita non iniziata),
senza dover analizzare le stringhe dei messaggi di errore.

GERARCHIA DELLE ECCEZIONI
-------------------------
PartitaException (Base)
  ├── PartitaStatoException (Problemi legati allo stato della partita)
  │     ├── PartitaGiaIniziataException
  │     ├── PartitaNonInCorsoException
  │     └── PartitaGiaTerminataException
  │
  ├── PartitaRosterException (Problemi legati ai giocatori)
  │     ├── PartitaRosterPienoException
  │     ├── PartitaGiocatoriInsufficientiException
  │     └── PartitaGiocatoreTypeException
  PartitaGiocatoreGiaPresenteException
  │
  └── PartitaGiocoException (Problemi legati alle meccaniche di gioco)
        └── PartitaNumeriEsauritiException
"""

class PartitaException(Exception):
    """
    Eccezione base per tutti gli errori relativi alla classe Partita.
    Tutte le altre eccezioni di questo modulo ereditano da questa classe.
    """
    pass


# =============================================================================
# SEZIONE 1: ECCEZIONI RELATIVE ALLO STATO DELLA PARTITA
# =============================================================================

class PartitaStatoException(PartitaException):
    """
    Eccezione base per errori dovuti a uno stato della partita non compatibile
    con l'operazione richiesta.
    """
    pass

class PartitaGiaIniziataException(PartitaStatoException):
    """
    Sollevata quando si tenta un'operazione consentita solo PRIMA dell'inizio
    (es. aggiungere giocatori, avviare nuovamente), ma la partita è già in corso o terminata.
    """
    pass

class PartitaNonInCorsoException(PartitaStatoException):
    """
    Sollevata quando si tenta un'operazione di gioco (es. estrarre numero)
    ma la partita non è nello stato 'in_corso' (es. è ancora da iniziare o è finita).
    """
    pass

class PartitaGiaTerminataException(PartitaStatoException):
    """
    Sollevata quando si tenta di terminare una partita che è già nello stato 'terminata'.
    """
    pass


# =============================================================================
# SEZIONE 2: ECCEZIONI RELATIVE ALLA GESTIONE DEI GIOCATORI (ROSTER)
# =============================================================================

class PartitaRosterException(PartitaException):
    """
    Eccezione base per errori relativi alla gestione della lista dei giocatori.
    """
    pass

class PartitaRosterPienoException(PartitaRosterException):
    """
    Sollevata quando si tenta di aggiungere un giocatore ma è stato raggiunto
    il limite massimo (MAX_GIOCATORI).
    """
    pass

class PartitaGiocatoriInsufficientiException(PartitaRosterException):
    """
    Sollevata quando si tenta di avviare la partita ma non è stato raggiunto
    il numero minimo di giocatori richiesto (MIN_GIOCATORI).
    """
    pass

class PartitaGiocatoreTypeException(PartitaRosterException):
    """
    Sollevata quando si tenta di aggiungere alla partita un oggetto che non è
    un'istanza valida di GiocatoreBase o delle sue sottoclassi.
    """
    pass

class PartitaGiocatoreGiaPresenteException(PartitaRosterException):
    """
    Eccezione sollevata quando si tenta di aggiungere un giocatore
    che è già presente nella partita.
    """
    pass


# =============================================================================
# SEZIONE 3: ECCEZIONI RELATIVE ALLE MECCANICHE DI GIOCO
# =============================================================================

class PartitaGiocoException(PartitaException):
    """
    Eccezione base per errori che avvengono durante lo svolgimento del gioco.
    """
    pass

class PartitaNumeriEsauritiException(PartitaGiocoException):
    """
    Sollevata quando si tenta di estrarre un numero ma il tabellone ha esaurito
    tutti i 90 numeri disponibili. Indica una fine naturale della partita per esaurimento.
    """
    pass
