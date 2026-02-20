# 🎨 Design Document - Silent Controller

> **FASE: CONCEPT & FLOW DESIGN**  
> Nessuna decisione tecnica qui - solo logica e flussi concettuali  
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-20
- **Stato**: DESIGN FREEZE ✅
- **Versione Target**: v0.8.0
- **Autore**: AI Assistant + donato81

---

## 💡 L'Idea in 3 Righe

Il `game_controller.py` contiene oggi circa 22 chiamate `print()` hardcoded che scrivono direttamente su stdout, bypassando completamente il sistema di localizzazione, il renderer e il sistema di logging già costruiti nelle versioni precedenti. Questi `print()` erano scaffolding di sviluppo — utili durante la costruzione del motore, ma oggi si frappongono tra la TUI e il terminale, rendendo impossibile avere controllo esclusivo dell'output da parte dell'interfaccia. Vogliamo che il controller torni a fare il suo lavoro silenziosamente: orchestrare il dominio, restituire dati strutturati e delegare qualsiasi comunicazione verso l'utente alla TUI.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Controller** (`game_controller.py`): Orchestratore della logica applicativa. Crea partita, avvia gioco, esegue turni, risponde con dati strutturati. **Non deve mai parlare direttamente all'utente.**
- **TUI** (`ui_terminale.py`): Unico attore autorizzato a scrivere su stdout. Riceve i dati strutturati dal controller e decide come presentarli, attingendo ai testi localizzati in `it.py`.
- **Sistema di Logging** (`GameLogger`, sub-logger): Canale silenzioso per messaggi diagnostici destinati allo sviluppatore. Scrive su file, mai su stdout.
- **Dizionario Localizzazione** (`it.py`): Contenitore immutabile di tutti i testi leggibili dall'utente. È il contratto tra dominio e interfaccia.
- **Sviluppatore**: Legge il file di log per diagnosticare problemi. Non legge stdout durante il normale gioco.

### Concetti Chiave

#### Controller Silenzioso
- **Cos'è**: Un controller che non emette nessun output diretto su stdout, in nessuna condizione
- **Stati possibili**: Correttamente silenzioso, Compromesso (contiene `print()`)
- **Proprietà**: Il suo comportamento è verificabile meccanicamente con `grep` o con un test `capsys`

#### Messaggio Diagnostico
- **Cos'è**: Informazione destinata allo sviluppatore, non all'utente finale. Descrive passaggi interni, stati intermedi, anomalie gestite.
- **Destinazione**: Il file di log (`tombola_stark.log`), mai stdout
- **Livelli**: `DEBUG` per passaggi ordinari di costruzione, `WARNING` per comportamenti inattesi, `ERROR` per errori di programmazione gravi

#### Messaggio Utente
- **Cos'è**: Testo che il giocatore deve leggere o sentire (screen reader) per capire cosa sta succedendo
- **Destinazione**: stdout, via TUI via renderer. Mai prodotto direttamente dal controller.
- **Proprietà**: Sempre localizzato in `it.py`, mai hardcoded

#### Contratto di Ritorno del Controller
- **Cos'è**: Il valore restituito da ogni funzione pubblica del controller — `bool`, `dict`, `None` o eccezione — che porta tutta l'informazione necessaria alla TUI per decidere cosa stampare
- **Esempi**: `True` = avvio riuscito; `False` = avvio fallito; `dict` con chiave `tombola_rilevata` = turno completato; `None` = turno fallito; `ValueError` = bug di programmazione (solo `ottieni_stato_sintetico`)

### Relazioni Concettuali

```
Utente
  ↕ input/output
TUI (ui_terminale.py)
  ↓ legge testi da                      ↓ chiama
it.py (MESSAGGI_*)              game_controller.py
  ↑ nuovo: MESSAGGI_CONTROLLER          ↓ ritorna bool / dict / None / ValueError
  ↑ tipizzato con codici_controller.py  ↓ scrive diagnostica in
                                  GameLogger → tombola_stark.log
```

---

## ⚙️ Infrastruttura Interna del Controller (v0.8.0)

Questa sezione documenta la configurazione interna di `game_controller.py` che **non cambia** con questa modifica ma che è essenziale per capire come verranno incanalati i nuovi log sostitutivi dei `print()`.

### Import di Logging

Il controller già importa e inizializza il sistema di logging nella sezione di testa del modulo. Questo pattern **va preservato invariato** durante l'implementazione:

```
# Import sistema di logging centralizzato
from bingo_game.logging import GameLogger
import logging

# Sub-logger per categoria — figli del logger radice tombola_stark
# Ereditano handler e livello dal padre: nessuna configurazione aggiuntiva necessaria
_logger_game   = logging.getLogger("tombola_stark.game")
_logger_prizes = logging.getLogger("tombola_stark.prizes")
_logger_system = logging.getLogger("tombola_stark.system")
_logger_errors = logging.getLogger("tombola_stark.errors")
```

L'helper `_log_safe()` incapsula ogni chiamata ai sub-logger proteggendo il flusso di gioco da eccezioni del sistema di logging:

```
_log_safe(messaggio, livello, *args, logger=_logger_game)
```

**Regola di routing dei log** — quale sub-logger usare per i nuovi messaggi sostitutivi:

| Tipo di messaggio | Sub-logger | Livello |
|---|---|---|
| Passaggi di costruzione partita (Gruppo A) | `_logger_game` | `DEBUG` |
| Avvio/termine partita, premi, tombola | `_logger_game` / `_logger_prizes` | `INFO` |
| Stato inatteso, comportamento imprevisto gestito | `_logger_system` | `WARNING` |
| Parametro non-Partita, eccezione imprevista | `_logger_errors` | `ERROR` |

### Relazione con `GameLogger`

I sub-logger `tombola_stark.*` sono figli del logger radice `tombola_stark` configurato da `GameLogger.get_instance()`. Non richiedono configurazione propria: ereditano automaticamente l'handler su file e il livello impostato all'avvio. Questa catena è già operativa dalla v0.4.0 e **non deve essere modificata** per questa feature.

---

## 📦 Struttura dei Nuovi File (v0.8.0)

### `bingo_game/events/codici_controller.py` (nuovo)

File di costanti stringa che definisce i codici evento del controller. Segue il pattern già in uso per `Codici_Configurazione`, `Codici_Errori` e `Codici_Eventi`.

**Costanti definite**:

| Costante | Valore stringa | Descrizione |
|---|---|---|
| `CTRL_AVVIO_FALLITO_GENERICO` | `"ctrl.avvio_fallito_generico"` | Qualsiasi fallimento di `avvia_partita_sicura` |
| `CTRL_TURNO_NON_IN_CORSO` | `"ctrl.turno_non_in_corso"` | Turno richiesto con partita non `in_corso` |
| `CTRL_NUMERI_ESAURITI` | `"ctrl.numeri_esauriti"` | `PartitaNumeriEsauritiException` intercettata |
| `CTRL_TURNO_FALLITO_GENERICO` | `"ctrl.turno_fallito_generico"` | Qualsiasi altro fallimento di `esegui_turno_sicuro` |

**Posizione**: `bingo_game/events/codici_controller.py`  
**Dipendenze**: nessuna (file di soli letterali stringa)  
**Chi importa questo file**: `bingo_game/ui/locales/it.py` per annotare `MESSAGGI_CONTROLLER`

### `bingo_game/ui/locales/it.py` (modifica)

Aggiunta del dizionario `MESSAGGI_CONTROLLER` al file di localizzazione esistente.

**Import necessario in cima al file**:

```
from bingo_game.events.codici_controller import (
    CTRL_AVVIO_FALLITO_GENERICO,
    CTRL_TURNO_NON_IN_CORSO,
    CTRL_NUMERI_ESAURITI,
    CTRL_TURNO_FALLITO_GENERICO,
)
```

**Struttura del nuovo dizionario**:

```
MESSAGGI_CONTROLLER: dict[str, str] = {
    CTRL_AVVIO_FALLITO_GENERICO:  "Impossibile avviare la partita. "
                                  "Riprova o riavvia l'applicazione.",
    CTRL_TURNO_NON_IN_CORSO:      "Impossibile eseguire il turno: "
                                  "la partita non è in corso.",
    CTRL_NUMERI_ESAURITI:         "Tutti i 90 numeri sono stati estratti. "
                                  "La partita termina senza vincitore.",
    CTRL_TURNO_FALLITO_GENERICO:  "Errore durante l'esecuzione del turno. "
                                  "La partita potrebbe essere terminata.",
}
```

**Motivazione dell'import**: usare le costanti come chiavi del dizionario — invece di stringhe letterali — garantisce che il refactoring di un codice si propaghi automaticamente sia in `codici_controller.py` che in `it.py`, eliminando il rischio di disallineamento silenzioso tra i due file.

---

## 🎬 Scenari & Flussi

### Scenario 1: Avvio Partita Riuscito

**Punto di partenza**: L'utente ha completato la configurazione (nome, bot, cartelle). La TUI si trova allo Stato E.

**Flusso**:

1. **TUI**: Chiama `crea_partita_standard(nome, bot, cartelle)`
   → **Controller**: Costruisce tabellone, giocatore umano e bot. **Scrive nel log** via `_log_safe(..., logger=_logger_game)` a livello `DEBUG`: `"[GAME] crea_partita_standard: tabellone creato."`, `"[GAME] crea_partita_standard: giocatore umano creato. nome='...'"`, `"[GAME] crea_partita_standard: N bot creati."`. Ritorna l'oggetto `Partita`.
   → **stdout**: nulla

2. **TUI**: Chiama `avvia_partita_sicura(partita)`
   → **Controller**: Chiama `partita.avvia_partita()`. **Scrive nel log** via `_log_safe(..., logger=_logger_game)` a livello `INFO`: `"[GAME] Partita avviata — stato: in_corso, giocatori: N."` (log già esistente, va mantenuto). Ritorna `True`.
   → **stdout**: nulla

3. **TUI**: Riceve `True`. Legge `MESSAGGI_CONFIGURAZIONE["CONFIG_CONFERMA_AVVIO"]` da `it.py`. Stampa a schermo il testo localizzato.
   → **stdout**: `"Configurazione completata. Avvio partita..."` (solo da TUI)

**Punto di arrivo**: L'utente vede un messaggio di avvio. Il log contiene la diagnostica completa di costruzione. Nessun doppio output.

**Cosa cambia rispetto a oggi**: Spariscono i `print()` del controller come `"✅ Partita avviata con successo!"` e `"Creazione tabellone standard..."`. Il log è più ricco (log DEBUG per ogni sotto-passo di costruzione).

---

### Scenario 2: Avvio Partita Fallito (qualsiasi causa)

**Punto di partenza**: `avvia_partita_sicura` fallisce per qualunque motivo (giocatori insufficienti, partita già avviata, errore generico).

> **Decisione confermata (donato81, 2026-02-20)**: La TUI mostra sempre un unico messaggio generico `CTRL_AVVIO_FALLITO_GENERICO`, indipendentemente dalla causa specifica. La distinzione diagnostica tra le diverse eccezioni esiste **solo nel log** (`WARNING` con tipo eccezione via `_logger_errors`), non nell'interfaccia utente. Questi errori non dovrebbero mai verificarsi in produzione perché la TUI valida i parametri prima di chiamare il controller.

**Flusso**:

1. **TUI**: Chiama `avvia_partita_sicura(partita)`
   → **Controller**: Intercetta l'eccezione. **Scrive nel log** via `_log_safe(..., logger=_logger_errors)` a livello `WARNING` con il tipo specifico: `"[GAME] Avvio fallito: tipo='PartitaGiocatoriInsufficientiException'"` ecc. Ritorna sempre `False`.
   → **stdout**: nulla

2. **TUI**: Riceve `False`. Legge `MESSAGGI_CONTROLLER[CTRL_AVVIO_FALLITO_GENERICO]` da `it.py`. Stampa il messaggio localizzato.
   → **stdout**: `"Impossibile avviare la partita. Riprova o riavvia l'applicazione."` (solo da TUI)

**Punto di arrivo**: L'utente vede un messaggio chiaro. Il log registra la causa tecnica precisa. Il controller non ha mai toccato stdout.

**Cosa cambia**: Spariscono i `print(f"❌ Impossibile avviare: {exc}")` e simili. La TUI aggiunge una guardia sul `False` che oggi non controlla.

---

### Scenario 3: Turno di Gioco Eseguito

**Punto di partenza**: La partita è in corso. La TUI sta per richiedere il prossimo turno.

**Flusso**:

1. **TUI**: Chiama `esegui_turno_sicuro(partita)`
   → **Controller**: Esegue il turno, incrementa `_turno_corrente`. **Scrive nel log** via `_log_safe(..., logger=_logger_game)` a livello `DEBUG`: `"[GAME] Turno #N — estratto: M, avanzamento: X%."`. Se ci sono premi, scrive a livello `INFO` via `_logger_prizes` per ciascun premio (già implementato, va mantenuto). Ritorna il dizionario del turno.
   → **stdout**: nulla

2. **TUI**: Riceve il dizionario. Lo passa al renderer. Il renderer produce le righe da stampare.
   → **stdout**: output controllato esclusivamente dalla TUI tramite renderer

**Cosa cambia**: Spariscono i `print(f"✅ Turno #{n}: {numero}")` e `print(f"🎉 {n} nuovi premi!")`.

---

### Scenario 4: Turno Fallito (partita non in corso)

**Punto di partenza**: La partita non è nello stato `in_corso` quando viene richiesto un turno.

**Flusso**:

1. **TUI**: Chiama `esegui_turno_sicuro(partita)`
   → **Controller**: Rileva stato non valido. **Scrive nel log** via `_log_safe(..., logger=_logger_game)` a livello `WARNING`: `"[GAME] esegui_turno_sicuro: stato '...' non in corso, turno saltato."`. Ritorna `None`.
   → **stdout**: nulla

2. **TUI**: Riceve `None`. Legge `MESSAGGI_CONTROLLER[CTRL_TURNO_NON_IN_CORSO]` da `it.py`. Stampa il messaggio localizzato.
   → **stdout**: messaggio localizzato (solo da TUI)

---

### Scenario 5: Verifica Fine Partita (loop di gioco)

**Punto di partenza**: La TUI è nel loop `while not partita_terminata(partita)`.

**Flusso**:

1. **TUI**: Chiama `partita_terminata(partita)` ad ogni iterazione
   → **Controller**: Ottiene stato dalla `Partita`. **Scrive nel log** via `_log_safe(..., logger=_logger_game)` a livello `DEBUG`: `"[GAME] partita_terminata: stato='...'"`. Ritorna `False` o `True`.
   → **stdout**: nulla

2. Quando ritorna `True`:
   → **Controller**: Scrive nel log a livello `INFO` (solo la prima volta, grazie al flag `_partita_terminata_logged`): `"Partita terminata."` (già implementato, va mantenuto).
   → **TUI**: Riceve `True`, esce dal loop, entra nella schermata di fine partita.

**Cosa cambia**: Spariscono i `print("🏁 Partita TERMINATA")` e `print("▶️ Partita in corso")` emessi ad ogni iterazione.

---

### Scenario 6: Edge Case — Parametro non-Partita in `ottieni_stato_sintetico`

**Cosa succede se**: `ottieni_stato_sintetico` viene chiamata con un parametro che non è un oggetto `Partita`.

> **Decisione confermata (donato81, 2026-02-20)**: `ottieni_stato_sintetico` è l'**unica funzione del controller che mantiene il `ValueError`** invece di ritornare `False`/`None`. Motivazione: principio _fail fast_. Questa funzione viene chiamata solo nel riepilogo finale; un parametro errato indica un bug reale nel codice della TUI, non un errore dell'utente. Un crash esplicito aiuta il developer a trovare il problema immediatamente. La TUI deve catturarlo esplicitamente.

**Sistema dovrebbe**: Lanciare immediatamente `ValueError` con messaggio descrittivo. **Scrivere nel log** via `_log_safe(..., logger=_logger_errors)` a livello `ERROR`: `"[ERR] ottieni_stato_sintetico: parametro non è Partita — tipo: '...'."`

---

### Scenario 7: Edge Case — Parametro non-Partita in `avvia_partita_sicura` e `esegui_turno_sicuro`

**Cosa succede se**: Le altre funzioni del controller vengono chiamate con un parametro che non è un oggetto `Partita`.

**Sistema dovrebbe**: Rilevare il problema immediatamente. **Scrivere nel log** via `_log_safe(..., logger=_logger_errors)` a livello `ERROR`: `"[ERR] avvia_partita_sicura: parametro non è Partita — tipo: '...'"`. Ritornare `False` o `None` secondo contratto. Non stampare nulla su stdout.

---

## 🔀 Classificazione dei `print()` Esistenti

### Gruppo A — Scaffolding di sviluppo (→ `_log_safe` livello `DEBUG`, `logger=_logger_game`)

| `print()` attuale | Log sostitutivo |
|---|---|
| `"Creazione tabellone standard..."` | `[GAME] crea_partita_standard: tabellone creato.` — DEBUG |
| `"Creazione giocatore umano '...' con N cartelle..."` | `[GAME] crea_partita_standard: giocatore umano creato. nome='...', cartelle=N.` — DEBUG |
| `"Creazione N bot automatici..."` | `[GAME] crea_partita_standard: N bot automatici richiesti.` — DEBUG |
| `"Partita composta da N giocatori totali"` | `[GAME] crea_partita_standard: lista giocatori composta. tot=N.` — DEBUG |
| `"Inizializzazione oggetto Partita..."` | `[GAME] crea_partita_standard: oggetto Partita inizializzato.` — DEBUG |
| `"✅ Partita standard creata con successo!"` | `[GAME] crea_partita_standard: completato con successo.` — DEBUG |
| `"📸 Stato partita '...' — N estratti, N giocatori"` | `[GAME] ottieni_stato_sintetico: stato='...', estratti=N, giocatori=N.` — DEBUG |
| `"🔍 Controllo tombola: N giocatori, stato '...'"` | `[GAME] ha_partita_tombola: verifica su N giocatori, stato='...'.` — DEBUG |
| `"⏳ Nessuna tombola, gioco continua..."` | `[GAME] ha_partita_tombola: esito=False.` — DEBUG |
| `"🔍 Controllo fine partita: stato '...'"` | `[GAME] partita_terminata: stato='...'.` — DEBUG |
| `"▶️ Partita in corso - continua il loop"` | `[GAME] partita_terminata: esito=False.` — DEBUG |

### Gruppo B — Output di stato che la TUI gestisce (→ rimossi dal controller)

| `print()` attuale | Chi lo gestisce invece |
|---|---|
| `"✅ Partita avviata con successo!"` | TUI legge `True` da `avvia_partita_sicura` |
| `"✅ Turno #N: M"` | TUI legge `numero_estratto` dal dict del turno |
| `"🎉 N nuovi premi!"` | TUI legge `premi_nuovi` dal dict del turno |
| `"🎉 TOMBOLA RILEVATA nella partita!"` | TUI legge `tombola_rilevata=True` dal dict del turno |
| `"🏁 Partita TERMINATA - esci dal loop"` | TUI riceve `True` da `partita_terminata()` |

### Gruppo C — Errori che la TUI mostra da `it.py` (→ rimossi dal controller + testi in `it.py`)

> **Decisione confermata (donato81, 2026-02-20)**: tutti i fallimenti di `avvia_partita_sicura` mappano su `CTRL_AVVIO_FALLITO_GENERICO`. Distinzione diagnostica solo nel log.

| `print()` attuale | Chiave `MESSAGGI_CONTROLLER` usata dalla TUI |
|---|---|
| `"❌ Impossibile avviare: {exc}"` (giocatori insufficienti) | `CTRL_AVVIO_FALLITO_GENERICO` |
| `"❌ Partita già avviata: {exc}"` | `CTRL_AVVIO_FALLITO_GENERICO` |
| `"❌ Errore partita generico: {exc}"` | `CTRL_AVVIO_FALLITO_GENERICO` |
| `"❌ Impossibile turno: stato '...'"` | `CTRL_TURNO_NON_IN_CORSO` |
| `"🏁 Partita finita - Numeri esauriti: {exc}"` | `CTRL_NUMERI_ESAURITI` |
| `"❌ Turno fallito - Partita non in corso: {exc}"` | `CTRL_TURNO_NON_IN_CORSO` |
| `"❌ Errore partita durante turno: {exc}"` | `CTRL_TURNO_FALLITO_GENERICO` |

### Gruppo D — Avvisi di infrastruttura (→ `_log_safe` livello `WARNING`/`ERROR`, `logger=_logger_errors`)

| `print()` attuale | Log sostitutivo |
|---|---|
| `"⚠️ Avvio completato ma stato inatteso: ..."` | `[SYS] avvia_partita_sicura: stato post-avvio inatteso='...'.` — WARNING |
| `"❌ ERRORE: Oggetto non è una Partita valida"` (in avvia) | `[ERR] avvia_partita_sicura: parametro non è Partita.` — ERROR |
| `"❌ ERRORE: Parametro non è una Partita valida"` (in turno) | `[ERR] esegui_turno_sicuro: parametro non è Partita.` — ERROR |
| `"💥 Errore critico imprevisto: {exc}"` (avvia) | `[ERR] avvia_partita_sicura: eccezione imprevista. tipo='...'.` — ERROR |
| `"💥 Errore critico imprevisto nel turno: {exc}"` | `[ERR] esegui_turno_sicuro: eccezione imprevista. tipo='...'.` — ERROR |

---

## 🔀 Stati e Transizioni del Controller

### Prima di questa modifica (stato attuale)

```
Chiamata funzione controller
    ↓
Elaborazione interna
    ↓ (risultato)
print() su stdout  ←── scrive direttamente
    +
Ritorno valore (bool/dict/None)
    +
Log su file
```

### Dopo questa modifica (stato target v0.8.0)

```
Chiamata funzione controller
    ↓
Elaborazione interna
    ↓ (risultato)
_log_safe(…, logger=_logger_*) → tombola_stark.log
    +
Ritorno valore (bool/dict/None) ←── unica comunicazione verso TUI
    ↓
TUI interpreta il valore
    ↓
TUI legge testo da it.py tramite MESSAGGI_CONTROLLER[CTRL_*]
    ↓
TUI stampa su stdout via renderer

Eccezione: ottieni_stato_sintetico (parametro non-Partita)
    ↓
_log_safe(ERROR, logger=_logger_errors) + ValueError
    ↓
TUI cattura ValueError e mostra errore critico
```

### Diagramma stati del controller

```
[Controller chiamato]
        ↓
[Elaborazione interna]
        ↓ (sempre)
[_log_safe — mai su stdout]
        ↓ (biforcazione esito)
   ┌────┴────┐
[Successo]  [Errore]
   ↓            ↓
[Ritorna    [Ritorna False
bool True    o None +
o dict]      log WARNING/ERROR]
   └────┬────┘
        ↓
[TUI riceve il valore]
        ↓
[TUI decide cosa stampare]
```

---

## 🎮 Interazione Utente — Nuovo Flusso di Messaggi

### Mappa completa: Ritorno Controller → Azione TUI

> Nota: `avvia_partita_sicura` ritorna sempre `False` per qualsiasi fallimento. La TUI mostra sempre `CTRL_AVVIO_FALLITO_GENERICO`. La distinzione diagnostica è esclusivamente nel log.

| Funzione controller | Valore ritornato | Azione TUI |
|---|---|---|
| `crea_partita_standard(...)` | Oggetto `Partita` | Continua al passo successivo |
| `crea_partita_standard(...)` | Eccezione (propagata) | Mostra errore critico, esci |
| `avvia_partita_sicura(partita)` | `True` | Mostra `CONFIG_CONFERMA_AVVIO` (già in `it.py`) |
| `avvia_partita_sicura(partita)` | `False` (qualsiasi causa) | Mostra `MESSAGGI_CONTROLLER[CTRL_AVVIO_FALLITO_GENERICO]` |
| `esegui_turno_sicuro(partita)` | `dict` | Renderer elabora il dict e stampa |
| `esegui_turno_sicuro(partita)` | `None` (non in corso) | Mostra `MESSAGGI_CONTROLLER[CTRL_TURNO_NON_IN_CORSO]` |
| `esegui_turno_sicuro(partita)` | `None` (numeri esauriti) | Mostra `MESSAGGI_CONTROLLER[CTRL_NUMERI_ESAURITI]` |
| `esegui_turno_sicuro(partita)` | `None` (generico) | Mostra `MESSAGGI_CONTROLLER[CTRL_TURNO_FALLITO_GENERICO]` |
| `partita_terminata(partita)` | `True` | TUI esce dal loop, entra in schermata fine |
| `partita_terminata(partita)` | `False` | TUI prosegue il loop |
| `ottieni_stato_sintetico(partita)` | `dict` | TUI elabora il riepilogo finale |
| `ottieni_stato_sintetico(partita)` | `ValueError` (bug) | TUI cattura, mostra errore critico |

### Dizionario `MESSAGGI_CONTROLLER` in `it.py`

Questi testi vengono letti **esclusivamente dalla TUI**, mai dal controller. Il controller non conosce e non importa `it.py`. Le chiavi sono le costanti importate da `codici_controller.py`.

| Chiave costante | Testo (Italian) | Quando |
|---|---|---|
| `CTRL_AVVIO_FALLITO_GENERICO` | `"Impossibile avviare la partita. Riprova o riavvia l'applicazione."` | `avvia_partita_sicura` → `False` per qualsiasi causa |
| `CTRL_TURNO_NON_IN_CORSO` | `"Impossibile eseguire il turno: la partita non è in corso."` | `esegui_turno_sicuro` → `None` per stato non `in_corso` |
| `CTRL_NUMERI_ESAURITI` | `"Tutti i 90 numeri sono stati estratti. La partita termina senza vincitore."` | `esegui_turno_sicuro` → `None` per `PartitaNumeriEsauritiException` |
| `CTRL_TURNO_FALLITO_GENERICO` | `"Errore durante l'esecuzione del turno. La partita potrebbe essere terminata."` | `esegui_turno_sicuro` → `None` per altri errori |

---

## 📄 Side Effects Documentali (v0.8.0)

Questa feature richiede l'aggiornamento di tre file di documentazione **oltre al codice**. Questi aggiornamenti sono obbligatori e fanno parte della Definition of Done della PR v0.8.0.

### `API.md` — Rimozione riferimenti a stdout

**File**: `documentations/API.md`

**Cosa cambia**: Le firme delle funzioni pubbliche del controller oggi riportano nei commenti/note eventuali riferimenti a output su stdout (es. "stampa messaggio di avvio", "scrive su terminale"). Tutti questi riferimenti vanno rimossi o sostituiti con la descrizione corretta del contratto di ritorno.

**Aggiornamenti richiesti per funzione**:

| Funzione | Rimozione | Sostituzione |
|---|---|---|
| `crea_partita_standard` | Qualsiasi nota su `print()` di costruzione | "Scrive log DEBUG per ogni sotto-passo" |
| `avvia_partita_sicura` | Note su messaggi di avvio/errore stampati | "Ritorna `True`/`False`. Fallimenti loggati a WARNING." |
| `esegui_turno_sicuro` | Note su stampa turno/premi | "Ritorna `dict` o `None`. Premi loggati a INFO." |
| `ottieni_stato_sintetico` | Note su stampa stato | "Ritorna `dict`. Lancia `ValueError` su parametro non valido." |
| `partita_terminata` | Note su stampa stato loop | "Ritorna `bool`. Stato loggato a DEBUG." |
| `ha_partita_tombola` | Note su stampa tombola | "Ritorna `bool`. Verifica loggata a DEBUG." |

**Criterio di done**: Nessuna funzione del controller in `API.md` deve menzionare stdout o `print()` come effetto collaterale.

---

### `ARCHITECTURE.md` — Aggiornamento diagramma flussi

**File**: `documentations/ARCHITECTURE.md`

**Cosa cambia**: Il diagramma architetturale deve riflettere il pattern "Silent Controller". La freccia di comunicazione tra Controller e UI era bidirezionale di fatto (Controller scriveva su stdout). Diventa **strettamente unidirezionale**.

**Aggiornamenti richiesti**:

1. **Diagramma layer**: Aggiornare il diagramma dei layer per mostrare che `game_controller.py` non ha più dipendenza verso stdout. La freccia `Controller → stdout` deve essere rimossa.

2. **Diagramma flusso dati**: Aggiornare per mostrare il nuovo flusso:
   ```
   game_controller.py → (bool/dict/None) → ui_terminale.py → stdout
   game_controller.py → (log) → tombola_stark.log
   ```
   Al posto di:
   ```
   game_controller.py → stdout  [DA RIMUOVERE]
   game_controller.py → (bool/dict/None) → ui_terminale.py → stdout
   ```

3. **Sezione dipendenze**: Aggiungere alla lista delle regole architetturali invarianti: *"Il Controller non scrive mai su stdout (verificabile con `grep -n "print(" game_controller.py` → zero risultati)"*.

4. **Sezione nuovi componenti v0.8.0**: Aggiungere `bingo_game/events/codici_controller.py` alla mappa dei moduli con la sua descrizione (costanti codici evento controller).

**Criterio di done**: Il diagramma in `ARCHITECTURE.md` deve riflettere il flusso dati corretto dopo la v0.8.0: Controller → valori di ritorno → TUI → stdout, mai Controller → stdout diretto.

---

### `CHANGELOG.md` — Voce v0.8.0

**File**: `documentations/CHANGELOG.md`

**Cosa aggiungere** nella sezione `v0.8.0`:

```
### Changed
- game_controller.py: rimossi tutti i print() (~22 chiamate).
  I passaggi di costruzione vanno ora a log DEBUG.
  Gli output di stato sono trasportati dai valori di ritorno.
  I messaggi di errore sono gestiti dalla TUI via MESSAGGI_CONTROLLER.

### Added
- bingo_game/events/codici_controller.py: nuove costanti stringa
  CTRL_AVVIO_FALLITO_GENERICO, CTRL_TURNO_NON_IN_CORSO,
  CTRL_NUMERI_ESAURITI, CTRL_TURNO_FALLITO_GENERICO.
- bingo_game/ui/locales/it.py: nuovo dizionario MESSAGGI_CONTROLLER
  (4 voci) tipizzato con le costanti di codici_controller.py.
```

---

## 🤔 Domande & Decisioni

### Domande Aperte

*(Nessuna — tutte le domande sono state risolte il 2026-02-20)*

### Decisioni Prese

- ✅ **Controller non importa mai `it.py`**: La dipendenza `Controller → UI` è vietata dall'architettura. Le costanti `codici_controller.py` vivono in `bingo_game/events/` (layer dominio/infrastruttura), non in `bingo_game/ui/`.
- ✅ **`it.py` importa le costanti da `codici_controller.py`**: Il dizionario `MESSAGGI_CONTROLLER` usa le costanti come chiavi tipizzate. Questo garantisce coerenza e refactoring sicuro tra i due file.
- ✅ **Log DEBUG per i passaggi di costruzione**: I dettagli della costruzione vanno a livello `DEBUG` via `_logger_game` — visibili solo con `--debug`, in linea con `DESIGN_LOGGING_SYSTEM.md`.
- ✅ **Log INFO mantenuti per eventi di gioco**: I log `INFO` già esistenti in `esegui_turno_sicuro` per premi e tombola vengono preservati.
- ✅ **Il sub-logger `_logger_errors` riceve i casi gravi**: Errori di parametro non-Partita e eccezioni impreviste vanno a `_logger_errors` con livello `ERROR`.
- ✅ **Nessuna nuova eccezione introdotta nelle funzioni sicure**: Il controller continua a ritornare `False`/`None` per i casi di errore gestiti. Comportamento pubblico invariato.
- ✅ **Tutti i fallimenti di `avvia_partita_sicura` → `False` + `CTRL_AVVIO_FALLITO_GENERICO`** *(donato81, 2026-02-20)*: Distinzione diagnostica solo nel log. Le chiavi `CTRL_AVVIO_FALLITO_GIOCATORI` e `CTRL_AVVIO_GIA_AVVIATA` non vengono create.
- ✅ **`ottieni_stato_sintetico` mantiene il `ValueError`** *(donato81, 2026-02-20)*: Principio _fail fast_. La TUI deve catturarlo esplicitamente.
- ✅ **Aggiornamento obbligatorio di `API.md` e `ARCHITECTURE.md`** nella stessa PR v0.8.0: La coerenza documentale è parte della Definition of Done.

### Assunzioni

- Il controller viene sempre chiamato dalla TUI e mai direttamente da altri moduli
- I test esistenti non fanno `capsys.readouterr()` sul controller (da verificare prima dell'implementazione)
- La modifica non richiede cambiamenti al dominio (`partita.py`, `cartella.py`, `tabellone.py`, `players/`)

---

## 🎯 Opzioni Considerate

### Opzione A: Rimpiazzare i `print()` con messaggi in `it.py` e stampare dal controller stesso

**Pro**: messaggi localizzati, nessun cambiamento alla TUI.  
**Contro**: viola la freccia di dipendenza `Controller → UI`; il controller continua a scrivere su stdout; il renderer non può processare i messaggi.

### Opzione B: Silenzio totale — controller ritorna dati, TUI parla *(Scelta)*

**Pro**: rispetta la dipendenza unidirezionale; TUI ha controllo esclusivo su stdout; messaggi passano per il renderer; log più ricco; zero modifiche all'API pubblica.  
**Contro**: la TUI deve aggiungere guardie sul `False` di `avvia_partita_sicura` (piccolo lavoro extra ma necessario).

**Scelta finale**: **Opzione B**. È l'unica coerente con l'architettura e sblocca il loop di gioco v0.8.0 senza compromessi.

---

## ✅ Design Freeze Checklist

- [x] Tutti gli scenari principali mappati (Scenario 1–7)
- [x] Tassonomia completa dei `print()` con destino di ciascuno (Gruppi A–D)
- [x] Mappa ritorno controller → azione TUI completa e aggiornata
- [x] Contenuto di `MESSAGGI_CONTROLLER` definito (**4 chiavi** con testi)
- [x] Nuovo file `codici_controller.py` progettato con costanti tipizzate
- [x] Import di `codici_controller.py` in `it.py` specificato
- [x] Infrastruttura di logging interna documentata (sub-logger, routing, `_log_safe`)
- [x] Side effects documentali: `API.md`, `ARCHITECTURE.md`, `CHANGELOG.md` — criteri di done esplicitati
- [x] Opzioni valutate e scelta motivata
- [x] **Domanda 1 risolta** — `False` di `avvia_partita_sicura` → `CTRL_AVVIO_FALLITO_GENERICO` *(donato81, 2026-02-20)*
- [x] **Domanda 2 risolta** — `ottieni_stato_sintetico` mantiene `ValueError`, fail fast *(donato81, 2026-02-20)*
- [x] Tutti i riferimenti puntano a v0.8.0
- [x] Verifica nessun `capsys` esistente sul controller (da eseguire a inizio implementazione)

**Stato**: ~~DRAFT~~ → **DESIGN FREEZE** ✅  
**Data Freeze**: 2026-02-20

**Next Step**: Creare `PLAN_SILENT_CONTROLLER.md` con:
- File structure e responsabilità precise
- Strategia di testing dettagliata (capsys, mock, regression)
- Sequenza di commit consigliata
- Aggiornamenti `API.md`, `ARCHITECTURE.md`, `CHANGELOG.md`

---

## 🧪 Protocollo di Verifica (Preview per il PLAN)

### Test di Non-Regressione stdout

```
DATO  una partita creata con parametri validi
QUANDO chiamo [funzione controller]
ALLORA capsys.readouterr().out == ""
```

Funzioni da coprire:
1. `crea_tabellone_standard`
2. `crea_partita_standard`
3. `avvia_partita_sicura` — percorso `True` e percorso `False` generico
4. `esegui_turno_sicuro`
5. `partita_terminata`
6. `ottieni_stato_sintetico` — percorso `dict` (il `ValueError` non riguarda stdout)

### Criterio di Done Meccanico

```bash
grep -n "print(" bingo_game/game_controller.py
```

Deve restituire **zero risultati**.

---

## 📝 Note di Brainstorming

- La modifica è completamente backward-compatible: l'API pubblica non cambia in nessuna firma.
- Il log in modalità `--debug` diventa molto più ricco: ogni sotto-passo di costruzione partita oggi invisibile sarà tracciabile.
- Prerequisito architetturale per il loop di gioco v0.8.0: senza controller silenzioso il loop produrrebbe output disordinato.
- I `print()` con emoji (✅, ❌, 🎉, 🏁) sono problematici per gli screen reader: la rimozione ha beneficio diretto sull'accessibilità.
- La riduzione da 6 a 4 chiavi `MESSAGGI_CONTROLLER` semplifica la TUI: un solo ramo condizionale per il fallimento dell'avvio.
- Valutare check `print(` in pre-commit hook o regola `ruff` custom in versione futura.

---

## 📚 Riferimenti Contestuali

### Feature Correlate
- **Sistema di Logging v0.4.0–v0.5.0**: Sub-logger e `_log_safe()` già esistenti sono gli strumenti per sostituire i `print()` di Gruppo A e D.
- **TUI Start Menu v0.7.0** (`ui_terminale.py`): Pattern testi-da-`it.py` già in uso negli stati A–D è il modello da replicare per la gestione dei ritorni del controller.
- **Loop di Gioco v0.8.0** (da implementare): Questa modifica è il prerequisito diretto.
- **TerminalRenderer** (`renderer_terminal.py`): Già implementato. I messaggi `MESSAGGI_CONTROLLER` arriveranno al renderer tramite TUI.

### Vincoli da Rispettare
- **`TerminalUI` usa solo il Controller** — vietato importare da `partita.py`, `giocatore_base.py`, ecc.
- **Zero stringhe hardcoded in `ui_terminale.py`** — tutti i nuovi testi vanno in `it.py`
- **Logger centralizzato** — pattern `_log_safe()` obbligatorio per tutti i nuovi log, mai `print()` per debug
- **Log DEBUG non appesantiscono il log normale** — tutti i nuovi log di costruzione a livello `DEBUG`
- **`API.md` e `ARCHITECTURE.md` aggiornati nella stessa PR** — la coerenza documentale è parte della Definition of Done v0.8.0

---

## 🎯 Risultato Finale Atteso

✅ `grep -n "print(" bingo_game/game_controller.py` → zero risultati  
✅ Ogni funzione pubblica supera `capsys.readouterr().out == ""`  
✅ Log `tombola_stark.log` in `--debug` mostra tutti i sotto-passi di costruzione  
✅ Log in modalità normale mostra solo eventi INFO rilevanti  
✅ `it.py` importa le costanti da `codici_controller.py` e le usa come chiavi di `MESSAGGI_CONTROLLER`  
✅ TUI riceve `False` da `avvia_partita_sicura` e mostra `CTRL_AVVIO_FALLITO_GENERICO`  
✅ TUI cattura `ValueError` di `ottieni_stato_sintetico` e mostra errore critico  
✅ `API.md` aggiornato: nessun riferimento a stdout nelle firme del controller  
✅ `ARCHITECTURE.md` aggiornato: diagramma riflette il Silent Controller v0.8.0  
✅ `CHANGELOG.md` aggiornato: voce v0.8.0 con Changed e Added  
✅ Messaggi senza emoji problematiche per screen reader  
✅ Loop di gioco v0.8.0 collegabile al renderer senza rischio di output duplicato  

---

**Fine Design Document**
