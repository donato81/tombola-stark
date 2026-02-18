"""
Modulo: bingo_game.game_controller

Controller di alto livello per la gestione di una partita di tombola/bingo.

Questo modulo si pone sopra al motore di gioco (Tabellone, Cartella,
GiocatoreBase/GiocatoreUmano/GiocatoreAutomatico, Partita) e fornisce
funzioni di comodo per:

- creare una partita standard (tabellone + giocatori + cartelle);
- avviare la partita in modo sicuro, gestendo eventuali eccezioni;
- eseguire un turno di gioco e restituire un dizionario pronto per l'interfaccia;
- ottenere una fotografia sintetica dello stato della partita.

L'obiettivo è separare la logica del "cosa succede" (motore) dalla logica
del "come viene presentato" (interfaccia da terminale, screen reader, ecc.).
"""

from __future__ import annotations
#import dei tipi di dato necessari 
from typing import List, Optional, Dict, Any
#import della libreria random per la generazione di numeri casuali.
import random
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
# Helper interno per logging sicuro
# =========================

# Track se abbiamo già loggato la terminazione per evitare duplicati
_partita_terminata_logged: bool = False

def _log_safe(message: str, level: str = "info", *args) -> None:
    """Scrive nel log senza mai propagare eccezioni al chiamante.

    Args:
        message: Messaggio da registrare.
        level: Livello logging ('info', 'warning', 'debug', 'error').
        *args: Argomenti per il formato stringa del logger.

    Version:
        v0.4.0: Helper interno per logging sicuro nel controller
    """
    try:
        logger = GameLogger.get_instance()
        getattr(logger, level)(message, *args)
    except Exception:  # noqa: BLE001
        pass


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
    # Usa il costruttore di default di Tabellone
    # che inizializza automaticamente i numeri 1-90
    return Tabellone()


def assegna_cartelle_a_giocatore(giocatore: GiocatoreBase, num_cartelle: int) -> None:
    """
    Assegna un certo numero di cartelle a un giocatore.

    Per ciascuna cartella:
    - crea una nuova istanza di Cartella;
    - la aggiunge al giocatore tramite GiocatoreBase.aggiungi_cartella().

    Parametri:
    - giocatore: GiocatoreBase
      Giocatore a cui assegnare le cartelle.
    - num_cartelle: int
      Numero di cartelle da creare e assegnare.
      
    Raises:
    - ControllerCartelleNegativeException: Se num_cartelle è negativo.
    """
    # Verifica di sicurezza: il numero di cartelle non può essere negativo
    if num_cartelle < 0:
        raise ControllerCartelleNegativeException(num_cartelle)

    # Avviamo un ciclo che si ripete tante volte quante sono le cartelle richieste
    for _ in range(num_cartelle):
        
        # 1. Creiamo una nuova cartella
        # Il costruttore di Cartella() si occupa già di generare i 15 numeri casuali
        nuova_cartella = Cartella()

        # 2. Aggiungiamo la cartella appena creata alla lista del giocatore
        # Usiamo il metodo della classe base per garantire la coerenza dei dati
        giocatore.aggiungi_cartella(nuova_cartella)


def crea_giocatore_umano(nome: str, num_cartelle: int = 1, id_giocatore: Optional[int] = None) -> GiocatoreUmano:
    """
    Crea un nuovo giocatore umano, assegnandogli un ID (se disponibile) e le cartelle richieste.

    Questa funzione supporta l'identificazione univoca del giocatore tramite id_giocatore,
    fondamentale per scenari futuri con login o profili multipli.

    Passaggi:
    1. Istanzia GiocatoreUmano passando nome ed eventuale ID;
    2. Delega la creazione delle cartelle alla funzione di supporto.

    Parametri:
    - nome: str
      Nome descrittivo del giocatore (es. "Mario").
      Non deve essere vuoto.
    - num_cartelle: int
      Numero di cartelle da assegnare subito. Default: 1.
    - id_giocatore: Optional[int]
      Identificativo univoco del giocatore (es. da database o sistema di login).
      Se non fornito, il giocatore verrà creato senza ID specifico (o con default di classe).

    Ritorna:
    - GiocatoreUmano: l'istanza del giocatore creata e configurata.

    Raises:
    - ControllerNomeGiocatoreException: Se il nome è vuoto.
    - ControllerCartelleNegativeException: Se num_cartelle è negativo.
    """
    # Verifica di sicurezza: il nome è obbligatorio per l'interfaccia utente
    if not nome or not nome.strip():
        raise ControllerNomeGiocatoreException(nome)

    # 1. Creiamo l'istanza del GiocatoreUmano
    # Passiamo esplicitamente anche l'id_giocatore per garantire tracciabilità futura
    giocatore = GiocatoreUmano(nome=nome, id_giocatore=id_giocatore)

    # 2. Assegniamo le cartelle richieste
    # Usiamo la funzione comune definita in precedenza nel controller
    assegna_cartelle_a_giocatore(giocatore, num_cartelle)

    # 3. Restituiamo l'oggetto completo
    return giocatore


def crea_giocatori_automatici(num_bot: int = 1) -> List[GiocatoreAutomatico]:
    """
    Crea una lista di giocatori automatici (bot) per la partita di tombola.

    Questa funzione garantisce che ci sia sempre almeno 1 bot in partita
    (per raggiungere il minimo di 2 giocatori totali con l'umano).
    Rispetta il limite massimo di 8 giocatori totali (1 umano + 7 bot).

    Per ogni bot creato:
    1. Genera un nome univoco "Bot X" dove X è il numero progressivo;
    2. Assegna un numero casuale di cartelle tra 1 e 6;
    3. Usa la funzione di supporto per creare e assegnare le cartelle.

    Parametri:
    - num_bot: int
      Numero desiderato di bot da creare.
      Default: 1. Se <= 0, crea comunque 1 bot minimo.
      Massimo consentito: 7 (per arrivare a 8 giocatori totali).

    Ritorna:
    - List[GiocatoreAutomatico]: lista dei bot creati e configurati.

    Raises:
    - ControllerBotNegativeException: Se num_bot < 0.
    - ControllerBotExcessException: Se num_bot > 7 (limite partita).
    """
    # 1. VALIDAZIONE INPUT - Controlli di sicurezza sui parametri
    if num_bot < 0:
        raise ControllerBotNegativeException(num_bot)
    
    if num_bot > 7:
        raise ControllerBotExcessException()

    # 2. DETERMINAZIONE NUMERO EFFETTIVO DI BOT
    # Garantiamo sempre almeno 1 bot, indipendentemente dal valore passato
    num_bot_effettivi = max(1, num_bot)

    # 3. INIZIALIZZAZIONE LISTA RISULTATO
    # Lista che conterrà tutti i bot creati e configurati
    lista_bot: List[GiocatoreAutomatico] = []

    # 4. CICLO DI CREAZIONE DEI BOT
    # Per ogni bot richiesto, creiamo l'istanza completa
    for indice in range(num_bot_effettivi):
        
        # 4a. GENERAZIONE NOME UNIVOCO
        # Nome standard "Bot 1", "Bot 2", ecc. per identificare chiaramente i bot
        nome_bot = f"Bot {indice + 1}"

        # 4b. CREAZIONE ISTANZA GIOCATORE AUTOMATICO
        # Istanziamo direttamente la classe specifica per i bot
        bot = GiocatoreAutomatico(nome=nome_bot)

        # 4c. DETERMINAZIONE NUMERO CARTELLE CASUALE
        # Ogni bot riceve un numero casuale di cartelle tra 1 e 6 (regola tombola)
        num_cartelle_bot = random.randint(1, 6)

        # 4d. ASSEGNAZIONE CARTELLE
        # Delega alla funzione comune già implementata nel controller
        # Questo mantiene la logica pulita e riutilizzabile
        assegna_cartelle_a_giocatore(bot, num_cartelle_bot)

        # 4e. AGGIUNTA ALLA LISTA RISULTATO
        lista_bot.append(bot)

    # 5. RITORNO RISULTATO
    # Restituiamo la lista completa dei bot pronti per la partita
    return lista_bot


def crea_partita_standard(
    nome_giocatore_umano: str = "Giocatore 1",
    num_cartelle_umano: int = 1,
    num_bot: int = 1
) -> Partita:
    """
    Crea una partita di tombola standard completamente configurata e pronta per essere avviata.

    Questa funzione orchestra tutte le componenti necessarie per una partita completa:
    1. Crea un tabellone standard (numeri 1-90);
    2. Crea il giocatore umano con nome e cartelle specificate;
    3. Crea i bot automatici (minimo 1, massimo 7) con cartelle casuali;
    4. Inizializza l'oggetto Partita con tabellone e tutti i giocatori.

    Garantisce sempre almeno 2 giocatori totali (1 umano + 1 bot minimo).

    Parametri:
    - nome_giocatore_umano: str
      Nome del giocatore umano principale (es. "Mario"). Default: "Giocatore 1".
    - num_cartelle_umano: int
      Numero di cartelle da assegnare al giocatore umano. Default: 1.
    - num_bot: int
      Numero di bot automatici da includere (1-7). Default: 1.
      Se <= 0, crea comunque 1 bot minimo.

    Ritorna:
    - Partita: istanza completamente configurata nello stato "non_iniziata".

    Raises:
    - ControllerNomeGiocatoreException: Se nome_giocatore_umano è vuoto.
    - ControllerCartelleNegativeException: Se num_cartelle_umano < 0.
    - ControllerBotNegativeException: Se num_bot < 0.
    - ControllerBotExcessException: Se num_bot > 7.
    """
    global _partita_terminata_logged
    
    # Reset flag terminazione per nuova partita
    _partita_terminata_logged = False
    
    # 1. VALIDAZIONE PARAMETRI DI INPUT
    # Controlli di sicurezza per garantire coerenza della partita
    if not nome_giocatore_umano or not nome_giocatore_umano.strip():
        raise ControllerNomeGiocatoreException(nome_giocatore_umano)
    
    if num_cartelle_umano < 0:
        raise ControllerCartelleNegativeException(num_cartelle_umano)
    
    if num_bot < 0:
        raise ControllerBotNegativeException(num_bot)
    if num_bot > 7:
        raise ControllerBotExcessException()

    # 2. CREAZIONE COMPONENTI PRINCIPALI
    
    # 2a. TABELLONE STANDARD
    # Crea il tabellone con numeri 1-90 usando la funzione dedicata del controller
    print("Creazione tabellone standard...")
    tabellone = crea_tabellone_standard()

    # 2b. GIOCATORE UMANO
    # Crea il giocatore umano principale con nome e cartelle specificate
    print(f"Creazione giocatore umano '{nome_giocatore_umano}' con {num_cartelle_umano} cartella/e...")
    giocatore_umano = crea_giocatore_umano(
        nome=nome_giocatore_umano,
        num_cartelle=num_cartelle_umano
    )

    # 2c. GIOCATORI AUTOMATICI (BOT)
    # Calcola numero effettivo di bot (garantisce almeno 1)
    num_bot_effettivi = max(1, num_bot)
    print(f"Creazione {num_bot_effettivi} bot automatici...")
    lista_bot = crea_giocatori_automatici(num_bot_effettivi)

    # 3. COMPOSIZIONE LISTA GIOCATORI TOTALI
    # Unisce umano + tutti i bot in un'unica lista per la partita
    tutti_i_giocatori = [giocatore_umano] + lista_bot
    print(f"Partita composta da {len(tutti_i_giocatori)} giocatori totali")

    # 4. CREAZIONE E CONFIGURAZIONE PARTITA
    # Istanzia la Partita passando tabellone e lista completa dei giocatori
    print("Inizializzazione oggetto Partita...")
    partita = Partita(tabellone, tutti_i_giocatori)

    # 5. VERIFICA FINALE CONFIGURAZIONE
    # Controllo di sicurezza: verifica che la partita sia correttamente inizializzata
    if not hasattr(partita, 'tabellone') or partita.tabellone is None:
        raise RuntimeError("Errore critico: tabellone non inizializzato nella partita")
    if len(partita.get_giocatori()) != len(tutti_i_giocatori):
        raise RuntimeError("Errore critico: giocatori non inizializzati nella partita")

    print("✅ Partita standard creata con successo!")
    
    # Log creazione partita riuscita
    _log_safe(
        "Partita creata: giocatore='%s', cartelle_umano=%d, bot=%d, tot_giocatori=%d",
        "info", nome_giocatore_umano, num_cartelle_umano, num_bot_effettivi,
        len(tutti_i_giocatori)
    )
    
    # 6. RITORNO PARTITA PRONTA
    return partita


# =========================
# Sezione 2: Operazioni di alto livello sulla partita
# =========================

def avvia_partita_sicura(partita: Partita) -> bool:
    """
    Avvia la partita in modo sicuro, intercettando eccezioni comuni.

    Questa funzione chiama Partita.avvia_partita() e gestisce automaticamente
    le eccezioni più frequenti, permettendo all'interfaccia di continuare
    senza crash.

    Eccezioni intercettate:
    - PartitaGiocatoriInsufficientiException: meno di 2 giocatori
    - PartitaGiaIniziataException: partita già avviata/terminata
    - Altre PartitaException*: qualsiasi altro errore di Partita

    Parametri:
    - partita: Partita
      Istanza della partita da avviare (deve essere nello stato "non_iniziata").

    Ritorna:
    - bool:
      - True: avvio riuscito, partita ora in stato "in_corso"
      - False: avvio fallito per uno dei motivi sopra (interfaccia mostra messaggio)
    """
    # 1. Verifica preliminare: partita esiste ed è valida
    if not isinstance(partita, Partita):
        print("❌ ERRORE: Oggetto non è una Partita valida")
        return False
    
    # 2. Tentativo di avvio con gestione eccezioni sicure
    try:
        # Chiamata diretta al metodo della Partita
        partita.avvia_partita()
        
        # 3. Verifica POST-avvio: stato effettivamente cambiato
        if partita.get_stato_partita() == "in_corso":
            print("✅ Partita avviata con successo!")
            _log_safe("Partita avviata con successo.", "info")
            return True
        else:
            print("⚠️  Avvio completato ma stato inatteso:", partita.get_stato_partita())
            return False
            
    # 4. Eccezioni SPECIFICHE intercettate e gestite
    except PartitaGiocatoriInsufficientiException as exc:
        print(f"❌ Impossibile avviare: {exc}")
        print(f"   Serve almeno {Partita.MIN_GIOCATORI} giocatori, presenti: {partita.get_numero_giocatori()}")
        _log_safe("Avvio partita fallito: %s", "warning", str(exc))
        return False
        
    except PartitaGiaIniziataException as exc:
        print(f"❌ Partita già avviata: {exc}")
        print(f"   Stato attuale: '{partita.get_stato_partita()}'")
        _log_safe("Avvio partita fallito: %s", "warning", str(exc))
        return False
        
    # 5. QUALSIASI altra eccezione di Partita
    except PartitaException as exc:
        print(f"❌ Errore partita generico: {exc}")
        _log_safe("Avvio partita fallito: %s", "warning", str(exc))
        return False
        
    # 6. Eccezioni IMATTESA (propagate per debug)
    except Exception as exc:
        print(f"💥 Errore critico imprevisto: {exc}")
        _log_safe("Avvio partita fallito (errore imprevisto): %s", "warning", str(exc))
        raise  # Ri-lancia per debug completo


def esegui_turno_sicuro(partita: Partita) -> Optional[Dict[str, Any]]:
    """
    Esegue un turno di gioco in modo completamente sicuro.

    Questa funzione è il "pilota automatico" del ciclo di gioco:
    1. Verifica preliminare: partita valida e in stato "in_corso"
    2. Esegue Partita.esegui_turno() (estrazione + aggiornamento + premi)
    3. Ritorna dizionario completo se tutto OK
    4. Intercetta QUALSIASI errore → None (interfaccia mostra messaggio)

    Eccezioni intercettate:
    - PartitaNonInCorsoException: partita non avviata/terminata
    - PartitaNumeriEsauritiException: tabellone finito (90 estrazioni)
    - PartitaException: qualsiasi errore della Partita
    - Parametro non-Partita: validazione input

    Parametri:
    - partita: Partita
      La partita su cui eseguire il turno (DEVE essere "in_corso").

    Ritorna:
    - Dict[str, Any]: dizionario completo del turno se successo:
        - numero_estratto, stato_partita_prima/dopo, tombola_rilevata
        - premi_nuovi (lista eventi vincita)
    - None: se ERRORE (interfaccia deve mostrare messaggio appropriato)
    """
    # 1. VALIDAZIONE PRELIMINARE PARAMETRO
    if not isinstance(partita, Partita):
        print("❌ ERRORE: Parametro non è una Partita valida")
        return None
    
    # Verifica stato partita PRIMA del turno
    stato_attuale = partita.get_stato_partita()
    if stato_attuale != "in_corso":
        print(f"❌ Impossibile turno: stato '{stato_attuale}' (serve 'in_corso')")
        return None
    
    # 2. ESECUZIONE TURNO CON GESTIONE ECCEZIONI COMPLETE
    try:
        # Chiamata centrale: esegue TUTTO il ciclo del turno
        risultato_turno = partita.esegui_turno()
        
        # 3. VERIFICA RISULTATO VALIDO
        if not isinstance(risultato_turno, dict):
            print("⚠️  Turno completato ma risultato invalido (non dict)")
            return None
        
        # Verifica chiavi essenziali presenti
        chiavi_essenziali = {
            "numero_estratto", "stato_partita_prima", "stato_partita_dopo",
            "tombola_rilevata", "partita_terminata", "premi_nuovi"
        }
        if not chiavi_essenziali.issubset(risultato_turno.keys()):
            print("⚠️  Turno completato ma dizionario incompleto")
            return None
        
        # ✅ TURNO COMPLETATO PERFETTAMENTE
        print(f"✅ Turno #{partita.tabellone.get_conteggio_estratti()}: {risultato_turno['numero_estratto']}")
        if risultato_turno["premi_nuovi"]:
            print(f"   🎉 {len(risultato_turno['premi_nuovi'])} nuovi premi!")
        
        # Log turno (solo DEBUG)
        _log_safe(
            "Turno eseguito: numero=%s, premi=%d",
            "debug",
            risultato_turno.get("numero_estratto"),
            len(risultato_turno.get("premi_nuovi", []))
        )
        
        return risultato_turno
        
    # 4. ECCEZIONI SPECIFICHE DEL CICLO DI GIOCO
    except PartitaNonInCorsoException as exc:
        print(f"❌ Turno fallito - Partita non in corso: {exc}")
        _log_safe("Anomalia nel turno intercettata: %s", "warning", str(exc))
        return None
        
    except PartitaNumeriEsauritiException as exc:
        print(f"🏁 Partita finita - Numeri esauriti: {exc}")
        _log_safe("Anomalia nel turno intercettata: %s", "warning", str(exc))
        return None
        
    # 5. QUALSIASI ALTRA ECCEZIONE PARTITA
    except PartitaException as exc:
        print(f"❌ Errore partita durante turno: {exc}")
        _log_safe("Anomalia nel turno intercettata: %s", "warning", str(exc))
        return None
        
    # 6. ECCEZIONI CRITICHE (propagate per debug)
    except Exception as exc:
        print(f"💥 Errore critico imprevisto nel turno: {exc}")
        _log_safe("Anomalia nel turno intercettata (errore imprevisto): %s", "warning", str(exc))
        raise  # Rilancia per analisi completa


def ottieni_stato_sintetico(partita: Partita) -> Dict[str, Any]:
    """
    Ritorna una fotografia completa e validata dello stato della partita.

    Questa funzione è il "fotografo ufficiale" della partita: chiama
    Partita.get_stato_completo() e valida che il risultato sia perfetto
    prima di passarlo all'interfaccia (terminale, screen reader, GUI).

    VALIDAZIONI EFFETTUATE:
    1. Parametro è Partita valida
    2. Risultato è dict con TUTTE le chiavi essenziali
    3. Dati coerenti (es. len(numeri_estratti) == conteggio)

    Parametri:
    - partita: Partita
      Istanza valida della partita (qualsiasi stato).

    Ritorna:
    - Dict[str, Any]: stato completo garantito con chiavi:
        - stato_partita, ultimo_numero_estratto, numeri_estratti
        - giocatori (lista dict con nome/id/cartelle/tombola)
        - premi_gia_assegnati (lista ordinata)

    Raises:
    - ValueError: parametro non-Partita o stato incompleto/incoerente
    """
    # 1. VALIDAZIONE PARAMETRO INPUT
    if not isinstance(partita, Partita):
        raise ValueError("ottieni_stato_sintetico: parametro deve essere Partita, ricevuto: " + str(type(partita)))
    
    # 2. OTTENIMENTO STATO COMPLETO DALLA PARTITA
    try:
        stato_completo = partita.get_stato_completo()
    except Exception as exc:
        raise ValueError(f"Errore interno Partita.get_stato_completo(): {exc}") from exc
    
    # 3. VALIDAZIONE TIPO E STRUTTURA BASE
    if not isinstance(stato_completo, dict):
        raise ValueError("Partita.get_stato_completo() non ha ritornato un dizionario valido")
    
    # 4. VERIFICA CHIAVI ESSENZIALI OBBLIGATORIE
    chiavi_obbligatorie = {
        "stato_partita", "ultimo_numero_estratto", "numeri_estratti",
        "giocatori", "premi_gia_assegnati"
    }
    chiavi_mancanti = chiavi_obbligatorie - set(stato_completo.keys())
    if chiavi_mancanti:
        raise ValueError(f"Stato incompleto, mancano chiavi: {chiavi_mancanti}")
    
    # 5. VALIDAZIONE DATI COERENTI
    # Verifica coerenza numeri estratti
    numeri_estratti = stato_completo["numeri_estratti"]
    if not isinstance(numeri_estratti, list):
        raise ValueError("numeri_estratti non è lista")
    
    # Verifica giocatori
    giocatori = stato_completo["giocatori"]
    if not isinstance(giocatori, list):
        raise ValueError("giocatori non è lista")
    
    # Verifica stato partita valido
    stato_partita = stato_completo["stato_partita"]
    stati_validi = {"non_iniziata", "in_corso", "terminata"}
    if stato_partita not in stati_validi:
        raise ValueError(f"stato_partita invalido: '{stato_partita}', deve essere: {stati_validi}")
    
    # 6. OTTIMIZZAZIONI PER INTERFACCIA
    # Ordina premi per leggibilità
    premi_ordinati = sorted(stato_completo["premi_gia_assegnati"])
    stato_completo["premi_gia_assegnati"] = premi_ordinati
    
    # 7. LOG DI DEBUG (rimuovibile in produzione)
    print(f"📸 Stato partita '{stato_partita}' - {len(numeri_estratti)} estratti, {len(giocatori)} giocatori")
    
    # 8. RITORNO STATO VALIDATO E PRONTO PER INTERFACCIA
    return stato_completo


def ha_partita_tombola(partita: Partita) -> bool:
    """
    Verifica se almeno un giocatore della partita ha completato una tombola.

    Questa funzione è il "sensore di vittoria finale": interroga la Partita
    per sapere se QUALSIASI giocatore (umano o bot) ha almeno una cartella
    completamente segnata (tombola).

    LOGICA INTERNA:
    1. Validazione: partita deve essere Partita valida
    2. Delega: partita.has_tombola() → scansiona TUTTI i giocatori
    3. Risultato: True = "TOMBOLA!", False = "Continua a giocare"

    Utilizzo ideale nell'interfaccia:
    - Dopo ogni turno: if ha_partita_tombola(): annuncia_vittoria()
    - Per screen reader: "C'è tombola? Sì/No"

    Parametri:
    - partita: Partita
      Istanza valida della partita (qualsiasi stato).

    Ritorna:
    - bool:
      - True: almeno 1 giocatore ha tombola → partita finita!
      - False: nessuna tombola → continua il gioco

    Raises:
    - ValueError: parametro non-Partita
    """
    # 1. VALIDAZIONE PARAMETRO INPUT
    if not isinstance(partita, Partita):
        raise ValueError(
            f"ha_partita_tombola: parametro deve essere Partita, "
            f"ricevuto: {type(partita).__name__}"
        )
    
    # 2. VERIFICA PRELIMINARE STATO PARTITA
    stato_partita = partita.get_stato_partita()
    if stato_partita not in {"non_iniziata", "in_corso", "terminata"}:
        raise ValueError(f"Stato partita invalido: '{stato_partita}'")
    
    # 3. LOG DI DEBUG (utile per sviluppo)
    print(f"🔍 Controllo tombola: {partita.get_numero_giocatori()} giocatori, stato '{stato_partita}'")
    
    # 4. DELEGA ALLA PARTITA - METODO CORE
    # partita.has_tombola() scansiona TUTTI i giocatori e le LORO cartelle
    ha_tombola = partita.has_tombola()
    
    # 5. LOG RISULTATO (rimuovibile in produzione)
    if ha_tombola:
        print("🎉 TOMBOLA RILEVATA nella partita!")
    else:
        print("⏳ Nessuna tombola, gioco continua...")
    
    # 6. RITORNO RISULTATO BOOLEANO PURO
    return ha_tombola


def partita_terminata(partita: Partita) -> bool:
    """
    Verifica se la partita è nello stato 'terminata' (condizione di uscita).

    Questa funzione è il "sensore di fine loop": ritorna True SOLO quando
    la partita deve fermarsi (stato == "terminata"). Usata nell'interfaccia
    per controllare la condizione di uscita dal ciclo principale di gioco:

    ```
    while not partita_terminata(partita):
        turno = esegui_turno_sicuro(partita)
        if turno and turno["tombola_rilevata"]:
            annuncia_tombola()
    ```

    LOGICA SEMPLICE:
    1. Validazione: partita valida
    2. Verifica stato: partita.is_terminata()
    3. Risultato: True = "FERMA LOOP", False = "Continua"

    Parametri:
    - partita: Partita
      Istanza valida della partita (qualsiasi stato).

    Ritorna:
    - bool:
      - True: stato == "terminata" → esci dal loop di gioco
      - False: altri stati → continua il gioco

    Raises:
    - ValueError: parametro non-Partita o stato invalido
    """
    global _partita_terminata_logged
    
    # 1. VALIDAZIONE PARAMETRO INPUT
    if not isinstance(partita, Partita):
        raise ValueError(
            f"partita_terminata: parametro deve essere Partita, "
            f"ricevuto: {type(partita).__name__}"
        )
    
    # 2. OTTENIMENTO E VALIDAZIONE STATO PARTITA
    try:
        stato_partita = partita.get_stato_partita()
    except Exception as exc:
        raise ValueError(f"Errore lettura stato partita: {exc}") from exc
    
    # 3. VERIFICA STATO VALIDO
    stati_validi = {"non_iniziata", "in_corso", "terminata"}
    if stato_partita not in stati_validi:
        raise ValueError(
            f"Stato partita invalido '{stato_partita}', "
            f"valori ammessi: {stati_validi}"
        )
    
    # 4. LOG DI DEBUG (sviluppo)
    print(f"🔍 Controllo fine partita: stato '{stato_partita}'")
    
    # 5. DELEGA CORE - VERIFICA TERMINATA
    # partita.is_terminata() è il metodo ufficiale che controlla stato == "terminata"
    is_terminata = partita.is_terminata()
    
    # 6. LOG RISULTATO
    if is_terminata:
        print("🏁 Partita TERMINATA - esci dal loop")
        # Log solo la prima volta che rileva la terminazione
        if not _partita_terminata_logged:
            _log_safe("Partita terminata.", "info")
            _partita_terminata_logged = True
    else:
        print("▶️  Partita in corso - continua il loop")
    
    # 7. RITORNO BOOLEANO PURO
    return is_terminata
