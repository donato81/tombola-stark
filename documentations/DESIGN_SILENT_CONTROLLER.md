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
                                        ↓ scrive diagnostica in
                                  GameLogger → tombola_stark.log
```

---

## 🎬 Scenari & Flussi

### Scenario 1: Avvio Partita Riuscito

**Punto di partenza**: L'utente ha completato la configurazione (nome, bot, cartelle). La TUI si trova allo Stato E.

**Flusso**:

1. **TUI**: Chiama `crea_partita_standard(nome, bot, cartelle)`
   → **Controller**: Costruisce tabellone, giocatore umano e bot. **Scrive nel log** a livello `DEBUG`: `"[GAME] crea_partita_standard: tabellone creato."`, `"[GAME] crea_partita_standard: giocatore umano creato. nome='...'"`, `"[GAME] crea_partita_standard: N bot creati."`. Ritorna l'oggetto `Partita`.
   → **stdout**: nulla

2. **TUI**: Chiama `avvia_partita_sicura(partita)`
   → **Controller**: Chiama `partita.avvia_partita()`. **Scrive nel log** a livello `INFO`: `"[GAME] Partita avviata — stato: in_corso, giocatori: N."` (questo log già esiste e va mantenuto). Ritorna `True`.
   → **stdout**: nulla

3. **TUI**: Riceve `True`. Legge `MESSAGGI_CONFIGURAZIONE["CONFIG_CONFERMA_AVVIO"]` da `it.py`. Stampa a schermo il testo localizzato.
   → **stdout**: `"Configurazione completata. Avvio partita..."` (solo da TUI)

**Punto di arrivo**: L'utente vede un messaggio di avvio. Il log contiene la diagnostica completa di costruzione. Nessun doppio output.

**Cosa cambia rispetto a oggi**: Spariscono i `print()` del controller come `"✅ Partita avviata con successo!"` e `"Creazione tabellone standard..."`. Il log è più ricco (log DEBUG per ogni sotto-passo di costruzione).

---

### Scenario 2: Avvio Partita Fallito (qualsiasi causa)

**Punto di partenza**: `avvia_partita_sicura` fallisce per qualunque motivo (giocatori insufficienti, partita già avviata, errore generico).

> **Decisione confermata (donato81, 2026-02-20)**: La TUI mostra sempre un unico messaggio generico `CTRL_AVVIO_FALLITO_GENERICO`, indipendentemente dalla causa specifica. La distinzione diagnostica tra le diverse eccezioni esiste **solo nel log** (`WARNING` con tipo eccezione), non nell'interfaccia utente. Questi errori non dovrebbero mai verificarsi in produzione perché la TUI valida i parametri prima di chiamare il controller.

**Flusso**:

1. **TUI**: Chiama `avvia_partita_sicura(partita)`
   → **Controller**: Intercetta l'eccezione (qualunque essa sia). **Scrive nel log** a livello `WARNING` con il tipo specifico per il debug: `"[GAME] Avvio fallito: tipo='PartitaGiocatoriInsufficientiException'"` oppure `"[GAME] Avvio fallito: tipo='PartitaGiaIniziataException'"` ecc. Ritorna sempre e comunque `False`.
   → **stdout**: nulla

2. **TUI**: Riceve `False`. Legge **sempre** `MESSAGGI_CONTROLLER["CTRL_AVVIO_FALLITO_GENERICO"]` da `it.py`. Stampa il messaggio localizzato.
   → **stdout**: `"Impossibile avviare la partita. Riprova o riavvia l'applicazione."` (solo da TUI)

**Punto di arrivo**: L'utente vede un messaggio chiaro. Il log registra la causa tecnica precisa. Il controller non ha mai toccato stdout.

**Cosa cambia**: Spariscono i `print(f"❌ Impossibile avviare: {exc}")`, `print(f"❌ Partita già avviata: {exc}")` e simili. La TUI aggiunge una guardia sul valore di ritorno `False` che oggi non controlla.

---

### Scenario 3: Turno di Gioco Eseguito

**Punto di partenza**: La partita è in corso. La TUI sta per richiedere il prossimo turno.

**Flusso**:

1. **TUI**: Chiama `esegui_turno_sicuro(partita)`
   → **Controller**: Esegue il turno, incrementa `_turno_corrente`. **Scrive nel log** a livello `DEBUG`: `"[GAME] Turno #N — estratto: M, avanzamento: X%."`. Se ci sono premi, scrive a livello `INFO` per ciascun premio (già implementato, va mantenuto). Ritorna il dizionario del turno con `numero_estratto`, `premi_nuovi`, `tombola_rilevata`, ecc.
   → **stdout**: nulla

2. **TUI**: Riceve il dizionario. Lo passa al renderer. Il renderer produce le righe da stampare: annuncio del numero estratto, eventuali premi, eventuale tombola.
   → **stdout**: output controllato esclusivamente dalla TUI tramite renderer

**Punto di arrivo**: L'utente vede il numero estratto e i premi. Il controller non ha scritto nulla su stdout.

**Cosa cambia**: Spariscono i `print(f"✅ Turno #{n}: {numero}")` e `print(f"🎉 {n} nuovi premi!")`.

---

### Scenario 4: Turno Fallito (partita non in corso)

**Punto di partenza**: Per qualche motivo la partita non è nello stato `in_corso` quando viene richiesto un turno.

**Flusso**:

1. **TUI**: Chiama `esegui_turno_sicuro(partita)`
   → **Controller**: Rileva stato non valido prima ancora di tentare il turno. **Scrive nel log** a livello `WARNING`: `"[GAME] esegui_turno_sicuro: stato '...' non in corso, turno saltato."`. Ritorna `None`.
   → **stdout**: nulla

2. **TUI**: Riceve `None`. Legge `MESSAGGI_CONTROLLER["CTRL_TURNO_NON_IN_CORSO"]` da `it.py`. Stampa il messaggio localizzato.
   → **stdout**: messaggio localizzato (solo da TUI)

**Punto di arrivo**: Utente informato. Log diagnostico disponibile per lo sviluppatore. Controller silenzioso.

---

### Scenario 5: Verifica Fine Partita (loop di gioco)

**Punto di partenza**: La TUI è nel loop `while not partita_terminata(partita)`.

**Flusso**:

1. **TUI**: Chiama `partita_terminata(partita)` ad ogni iterazione
   → **Controller**: Ottiene stato dalla `Partita`. **Scrive nel log** a livello `DEBUG` (solo se abilitato): `"[GAME] partita_terminata: stato='in_corso'."` o `"[GAME] partita_terminata: stato='terminata'."`. Ritorna `False` o `True`.
   → **stdout**: nulla

2. Quando ritorna `True`:
   → **Controller**: Scrive nel log a livello `INFO` (solo la prima volta, grazie al flag `_partita_terminata_logged`): `"[GAME] Partita terminata."` (già implementato, va mantenuto).
   → **TUI**: Riceve `True`, esce dal loop, entra nella schermata di fine partita.

**Punto di arrivo**: Loop controllato silenziosamente. Spariscono i `print("🏁 Partita TERMINATA")` e `print("▶️ Partita in corso")` che oggi vengono emessi ad ogni iterazione del loop.

---

### Scenario 6: Edge Case — Parametro non-Partita in `ottieni_stato_sintetico`

**Cosa succede se**: `ottieni_stato_sintetico` viene chiamata con un parametro che non è un oggetto `Partita`.

> **Decisione confermata (donato81, 2026-02-20)**: `ottieni_stato_sintetico` è l'**unica funzione del controller che mantiene il `ValueError`** invece di ritornare `False`/`None`. Motivazione: principio _fail fast_. Questa funzione viene chiamata solo nel riepilogo finale; un parametro errato indica un bug reale nel codice della TUI, non un errore dell'utente. Un crash esplicito aiuta il developer a trovare il problema immediatamente. Il `ValueError` è già documentato nella docstring e nella firma pubblica. La TUI deve catturarlo esplicitamente.

**Sistema dovrebbe**: Lanciare immediatamente `ValueError` con messaggio descrittivo. **Scrivere nel log** a livello `ERROR` (sub-logger `_logger_errors`): `"[ERR] ottieni_stato_sintetico: parametro non è Partita — tipo: '...'."` La TUI cattura il `ValueError` e mostra un messaggio di errore critico.

---

### Scenario 7: Edge Case — Parametro non-Partita in `avvia_partita_sicura` e `esegui_turno_sicuro`

**Cosa succede se**: Le altre funzioni del controller vengono chiamate con un parametro che non è un oggetto `Partita`.

**Sistema dovrebbe**: Rilevare il problema immediatamente. **Scrivere nel log** a livello `ERROR` (sub-logger `_logger_errors`): `"[ERR] avvia_partita_sicura: parametro non è Partita — tipo: '...'."` Ritornare `False` o `None` secondo contratto. Non stampare nulla su stdout. Coerente con il pattern generale del controller (nessuna eccezione propagata, solo valore di ritorno sentinel).

---

## 🔀 Classificazione dei `print()` Esistenti

Questa è la tassonomia completa dei `print()` attualmente presenti nel controller, organizzata per tipo di intervento.

### Gruppo A — Scaffolding di sviluppo (→ `_log_safe` livello `DEBUG`)

Frasi che descrivono passaggi interni della costruzione di una partita. Nessun valore per l'utente finale.

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

Messaggi di gioco rilevanti il cui contenuto è già trasportato dal valore di ritorno della funzione. La TUI riceve il valore e stampa con il renderer.

| `print()` attuale | Chi lo gestisce invece |
|---|---|
| `"✅ Partita avviata con successo!"` | TUI legge `True` da `avvia_partita_sicura` |
| `"✅ Turno #N: M"` | TUI legge `numero_estratto` dal dict del turno |
| `"🎉 N nuovi premi!"` | TUI legge `premi_nuovi` dal dict del turno |
| `"🎉 TOMBOLA RILEVATA nella partita!"` | TUI legge `tombola_rilevata=True` dal dict del turno |
| `"🏁 Partita TERMINATA - esci dal loop"` | TUI riceve `True` da `partita_terminata()` |

### Gruppo C — Errori che la TUI mostra da `it.py` (→ rimossi dal controller + testi in `it.py`)

Messaggi di fallimento che oggi vengono stampati dal controller. La TUI non li vede perché riceve già `False` o `None` — deve essere aggiornata per leggere il messaggio corretto da `it.py`.

> **Decisione confermata (donato81, 2026-02-20)**: tutti i fallimenti di `avvia_partita_sicura` mappano sulla stessa chiave `CTRL_AVVIO_FALLITO_GENERICO`. Distinzione diagnostica solo nel log.

| `print()` attuale | Chiave `MESSAGGI_CONTROLLER` usata dalla TUI |
|---|---|
| `"❌ Impossibile avviare: {exc}"` (giocatori insufficienti) | `CTRL_AVVIO_FALLITO_GENERICO` |
| `"❌ Partita già avviata: {exc}"` | `CTRL_AVVIO_FALLITO_GENERICO` |
| `"❌ Errore partita generico: {exc}"` | `CTRL_AVVIO_FALLITO_GENERICO` |
| `"❌ Impossibile turno: stato '...'"` | `CTRL_TURNO_NON_IN_CORSO` |
| `"🏁 Partita finita - Numeri esauriti: {exc}"` | `CTRL_NUMERI_ESAURITI` |
| `"❌ Turno fallito - Partita non in corso: {exc}"` | `CTRL_TURNO_NON_IN_CORSO` |
| `"❌ Errore partita durante turno: {exc}"` | `CTRL_TURNO_FALLITO_GENERICO` |

### Gruppo D — Avvisi di infrastruttura (→ `_log_safe` livello `WARNING` o `ERROR`)

Comportamenti inattesi dell'infrastruttura o errori di programmazione. Destinati allo sviluppatore, mai all'utente.

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

### Dopo questa modifica (stato target)

```
Chiamata funzione controller
    ↓
Elaborazione interna
    ↓ (risultato)
Log su file (DEBUG/INFO/WARNING/ERROR per sviluppatore)
    +
Ritorno valore (bool/dict/None) ←── unica comunicazione verso TUI
    ↓
TUI interpreta il valore
    ↓
TUI legge testo da it.py (MESSAGGI_CONTROLLER o altri)
    ↓
TUI stampa su stdout via renderer

Eccezione: ottieni_stato_sintetico (parametro non-Partita)
    ↓
Lancia ValueError — fail fast
    ↓
TUI cattura e mostra errore critico
```

### Diagramma stati del controller

```
[Controller chiamato]
        ↓
[Elaborazione interna]
        ↓ (sempre)
[Scrive in log — mai su stdout]
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

> Nota: `avvia_partita_sicura` ritorna sempre `False` per qualsiasi fallimento. La TUI mostra sempre `CTRL_AVVIO_FALLITO_GENERICO`. La distinzione diagnostica è esclusivamente nel log per il developer.

| Funzione controller | Valore ritornato | Azione TUI |
|---|---|---|
| `crea_partita_standard(...)` | Oggetto `Partita` | Continua al passo successivo |
| `crea_partita_standard(...)` | Eccezione (propagata) | Mostra errore critico, esci |
| `avvia_partita_sicura(partita)` | `True` | Mostra `CONFIG_CONFERMA_AVVIO` (già in `it.py`) |
| `avvia_partita_sicura(partita)` | `False` (qualsiasi causa) | Mostra `CTRL_AVVIO_FALLITO_GENERICO` |
| `esegui_turno_sicuro(partita)` | `dict` | Renderer elabora il dict e stampa |
| `esegui_turno_sicuro(partita)` | `None` (non in corso) | Mostra `CTRL_TURNO_NON_IN_CORSO` |
| `esegui_turno_sicuro(partita)` | `None` (numeri esauriti) | Mostra `CTRL_NUMERI_ESAURITI` |
| `esegui_turno_sicuro(partita)` | `None` (generico) | Mostra `CTRL_TURNO_FALLITO_GENERICO` |
| `partita_terminata(partita)` | `True` | TUI esce dal loop, entra in schermata fine |
| `partita_terminata(partita)` | `False` | TUI prosegue il loop |
| `ottieni_stato_sintetico(partita)` | `dict` | TUI elabora il riepilogo finale |
| `ottieni_stato_sintetico(partita)` | `ValueError` (bug) | TUI cattura, mostra errore critico |

### Nuovo dizionario `MESSAGGI_CONTROLLER` in `it.py`

Questi testi vengono letti **esclusivamente dalla TUI**, mai dal controller. Il controller non conosce e non importa `it.py`.

> Le chiavi sono **4** (non 6): `CTRL_AVVIO_FALLITO_GIOCATORI` e `CTRL_AVVIO_GIA_AVVIATA` non vengono create — tutti i fallimenti di avvio usano `CTRL_AVVIO_FALLITO_GENERICO`.

| Chiave costante | Testo (Italian) | Quando |
|---|---|---|
| `CTRL_AVVIO_FALLITO_GENERICO` | `"Impossibile avviare la partita."` + `"Riprova o riavvia l'applicazione."` | `avvia_partita_sicura` → `False` per qualsiasi causa |
| `CTRL_TURNO_NON_IN_CORSO` | `"Impossibile eseguire il turno: la partita non è in corso."` | `esegui_turno_sicuro` → `None` per stato non `in_corso` |
| `CTRL_NUMERI_ESAURITI` | `"Tutti i 90 numeri sono stati estratti."` + `"La partita termina senza vincitore."` | `esegui_turno_sicuro` → `None` per `PartitaNumeriEsauritiException` |
| `CTRL_TURNO_FALLITO_GENERICO` | `"Errore durante l'esecuzione del turno."` + `"La partita potrebbe essere terminata."` | `esegui_turno_sicuro` → `None` per altri errori |

### Nuovo file `codici_controller.py`

Per rispettare il pattern del progetto (`Codici_Configurazione`, `Codici_Errori`, `Codici_Eventi`), le 4 chiavi sopra vengono definite come costanti stringa in `bingo_game/events/codici_controller.py`.

---

## 🤔 Domande & Decisioni

### Domande Aperte

*(Nessuna — tutte le domande sono state risolte il 2026-02-20)*

### Decisioni Prese

- ✅ **Controller non importa mai `it.py`**: La dipendenza `Controller → UI` è vietata dall'architettura. Le costanti `codici_controller.py` vivono in `bingo_game/events/` (layer dominio/infrastruttura), non in `bingo_game/ui/`.
- ✅ **Log DEBUG per i passaggi di costruzione**: I dettagli della costruzione (tabellone, giocatori, bot) vanno a livello `DEBUG` — visibili solo con `--debug`, in linea con il principio del `DESIGN_LOGGING_SYSTEM.md` di non appesantire il log ordinario.
- ✅ **Log INFO mantenuti per eventi di gioco**: I log `INFO` già esistenti in `esegui_turno_sicuro` per premi e tombola vengono preservati — rispettano il contratto del `DESIGN_LOGGING_SYSTEM.md`.
- ✅ **Il sub-logger `_logger_errors` riceve i casi gravi**: Errori di parametro non-Partita e eccezioni impreviste vanno a `_logger_errors` con livello `ERROR`, coerentemente con la convenzione `[ERR]` già in uso.
- ✅ **Nessuna nuova eccezione introdotta nelle funzioni sicure**: Il controller continua a ritornare `False`/`None` per i casi di errore gestiti. Il comportamento pubblico non cambia.
- ✅ **Tutti i fallimenti di `avvia_partita_sicura` → `False` + `CTRL_AVVIO_FALLITO_GENERICO` in TUI** *(donato81, 2026-02-20)*: La TUI mostra sempre il messaggio generico. La distinzione tra `PartitaGiocatoriInsufficientiException`, `PartitaGiaIniziataException` e altri errori esiste solo nel log per il developer. Motivazione: questi errori non devono verificarsi in produzione (la TUI valida prima); il dettaglio fine non aggiunge valore per l'utente. Le chiavi `CTRL_AVVIO_FALLITO_GIOCATORI` e `CTRL_AVVIO_GIA_AVVIATA` **non vengono create**.
- ✅ **`ottieni_stato_sintetico` mantiene il `ValueError`** *(donato81, 2026-02-20)*: È l'unica funzione del controller che non segue il pattern `False`/`None`. Motivazione: viene chiamata solo nel riepilogo finale; un parametro errato indica un bug reale nel codice della TUI — il principio _fail fast_ prevale sulla coerenza formale. La TUI deve catturare il `ValueError` esplicitamente.

### Assunzioni

- Il controller viene sempre chiamato dalla TUI e mai direttamente da altri moduli
- I test esistenti non fanno `capsys.readouterr()` per catturare i `print()` del controller (da verificare all'inizio dell'implementazione — se esistessero tali test andrebbero aggiornati)
- La modifica non richiede cambiamenti al dominio (`partita.py`, `cartella.py`, `tabellone.py`, `players/`)

---

## 🎯 Opzioni Considerate

### Opzione A: Rimpiazzare i `print()` con messaggi in `it.py` e stampare dal controller stesso

**Descrizione**: Il controller importa `MESSAGGI_CONTROLLER` da `it.py` e stampa direttamente i testi localizzati.

**Pro**:
- ✅ I messaggi sono localizzati
- ✅ Nessun cambiamento alla TUI

**Contro**:
- ❌ Viola la freccia di dipendenza: `Controller → UI` è architetturalmente vietato
- ❌ Il controller continua a scrivere su stdout — il problema del controllo esclusivo dell'output non è risolto
- ❌ Il renderer non può processare questi messaggi (niente TTS, niente accessibilità strutturata)

---

### Opzione B: Silenzio totale — controller ritorna dati, TUI parla (Scelta)

**Descrizione**: Il controller non scrive mai su stdout. Ogni `print()` viene o rimosso (se il valore di ritorno già trasporta l'informazione) o convertito in `_log_safe` (se è diagnostica per lo sviluppatore). I messaggi per l'utente vengono aggiunti in `it.py` e stampati dalla TUI sulla base del valore di ritorno del controller.

**Pro**:
- ✅ Rispetta rigorosamente la freccia di dipendenza unidirezionale
- ✅ La TUI ha controllo esclusivo su stdout — prerequisito per v0.8.0 loop di gioco
- ✅ I messaggi passano per il renderer — screen reader e TTS possono consumarli
- ✅ Il log diventa più ricco con log DEBUG verbosi per ogni sotto-passo
- ✅ Zero modifiche all'API pubblica del controller

**Contro**:
- ❌ La TUI deve aggiungere guardie sul valore di ritorno di `avvia_partita_sicura` (oggi non controllato) — piccolo lavoro extra ma necessario

---

### Scelta Finale

**Opzione B: Silenzio totale**. L'Opzione A è una soluzione di comodo che rimanda il problema: il controller continuerebbe a violare il layer di presentazione. L'Opzione B è l'unica coerente con l'architettura del progetto e sblocca il loop di gioco v0.8.0 senza compromessi.

---

## ✅ Design Freeze Checklist

Questo design è pronto per la fase PLAN:

- [x] Tutti gli scenari principali mappati (Scenario 1–7)
- [x] Tassonomia completa dei `print()` con destino di ciascuno (Gruppi A–D)
- [x] Mappa ritorno controller → azione TUI completa e aggiornata
- [x] Contenuto di `MESSAGGI_CONTROLLER` definito (**4 chiavi** con testi)
- [x] Nuovo file `codici_controller.py` progettato
- [x] Opzioni valutate e scelta motivata
- [x] **Domanda 1 risolta** — tutti i `False` di `avvia_partita_sicura` → `CTRL_AVVIO_FALLITO_GENERICO` *(donato81, 2026-02-20)*
- [x] **Domanda 2 risolta** — `ottieni_stato_sintetico` mantiene `ValueError`, fail fast *(donato81, 2026-02-20)*
- [x] Verifica nessun `capsys` esistente sul controller (da eseguire all'inizio dell'implementazione)

**Stato**: ~~DRAFT~~ → **DESIGN FREEZE** ✅  
**Data Freeze**: 2026-02-20

**Next Step**: Creare `PLAN_SILENT_CONTROLLER.md` con:
- File structure e responsabilità precise
- Strategia di testing dettagliata (capsys, mock, regression)
- Sequenza di commit consigliata
- Aggiornamenti `API.md`, `ARCHITECTURE.md`, `CHANGELOG.md`

---

## 🧪 Protocollo di Verifica (Preview per il PLAN)

### Test di Non-Regressione stdout (da formalizzare in PLAN)

Il criterio di done oggettivo è: ogni funzione pubblica del controller, chiamata in qualsiasi condizione, non deve emettere nulla su stdout. Il test pattern è:

```
DATO  una partita creata con parametri validi
QUANDO chiamo [funzione controller]
ALLORA capsys.readouterr().out == ""
```

Questo va applicato a tutte e 6 le funzioni pubbliche:
1. `crea_tabellone_standard`
2. `crea_partita_standard`
3. `avvia_partita_sicura` — percorso `True` e percorso `False` generico
4. `esegui_turno_sicuro`
5. `partita_terminata`
6. `ottieni_stato_sintetico` — percorso `dict` (il `ValueError` non riguarda stdout)

Devono essere coperti sia i percorsi felici sia i percorsi di errore. Per `avvia_partita_sicura` il test `capsys` verifica il singolo percorso `False` — non servono test separati per tipo di eccezione lato TUI.

### Criterio di Done Meccanico

```bash
grep -n "print(" bingo_game/game_controller.py
```

Deve restituire **zero risultati**. Questo comando può essere aggiunto come check nel processo di revisione della PR.

---

## 📝 Note di Brainstorming

- La modifica è completamente backward-compatible: l'API pubblica del controller non cambia in nessuna firma.
- Il log diventa notevolmente più ricco: i passaggi di costruzione in `crea_partita_standard` oggi sono invisibili al log — dopo, con `--debug`, lo sviluppatore vedrà ogni sotto-passo.
- Questa modifica è il prerequisito architetturale per il loop di gioco v0.8.0: senza di essa, il loop produrrebbe output disordinato con frasi del controller mischiate all'output del renderer.
- I `print()` con emoji (✅, ❌, 🎉, 🏁) sono particolarmente problematici per l'accessibilità: uno screen reader li legge letteralmente come "segno di spunta verde", "X rossa", ecc. La rimozione ha un beneficio diretto per l'accessibilità.
- La riduzione delle chiavi `MESSAGGI_CONTROLLER` da 6 a 4 semplifica il lavoro sulla TUI: un solo ramo condizionale per il fallimento dell'avvio invece di tre.
- Valutare se aggiungere un check `print(` in pre-commit hook o regola `ruff` custom in una versione futura.

---

## 📚 Riferimenti Contestuali

### Feature Correlate
- **Sistema di Logging v0.4.0–v0.5.0**: I sub-logger `_logger_game`, `_logger_prizes`, `_logger_system`, `_logger_errors` e il pattern `_log_safe()` già esistenti sono gli strumenti con cui sostituire i `print()` di Gruppo A e D.
- **TUI Start Menu v0.7.0** (`ui_terminale.py`): Il pattern di stampa già in uso negli stati A–D (testi da `it.py`, nessun `print()` hardcoded) è il modello da replicare per la gestione dei ritorni del controller nello Stato E.
- **Loop di Gioco v0.8.0** (da implementare): Questa modifica è il suo prerequisito diretto. Senza controller silenzioso, il loop produrrebbe output non controllato.
- **TerminalRenderer** (`renderer_terminal.py`): Già implementato e pronto. I messaggi di `MESSAGGI_CONTROLLER` arriveranno al renderer tramite la TUI, non direttamente dal controller.

### Vincoli da Rispettare
- **`TerminalUI` usa solo il Controller** — vietato importare da `partita.py`, `giocatore_base.py`, ecc. (invariante architetturale già stabilito)
- **Zero stringhe hardcoded in `ui_terminale.py`** — tutti i nuovi testi di errore controller vanno in `it.py` (invariante già stabilito)
- **Logger centralizzato** — `logging.getLogger(__name__)`, prefisso categoria `[GAME]`/`[SYS]`/`[ERR]`, nessun `print()` per debug (invariante già stabilito da `DESIGN_LOGGING_SYSTEM.md`)
- **Il sistema di logging non propaga mai eccezioni al gioco** — il pattern `_log_safe()` deve essere usato per tutti i nuovi log aggiunti
- **I log DEBUG non devono appesantire il log normale** — i nuovi log di costruzione vanno tutti a livello `DEBUG`, visibili solo con `--debug`

---

## 🎯 Risultato Finale Atteso

Una volta implementato, il controller garantirà:

✅ `grep -n "print(" bingo_game/game_controller.py` → zero risultati  
✅ Ogni funzione pubblica del controller supera il test `capsys.readouterr().out == ""`  
✅ Il log `tombola_stark.log` in modalità `--debug` mostra tutti i sotto-passi di costruzione partita  
✅ Il log `tombola_stark.log` in modalità normale mostra solo eventi INFO rilevanti (avvio, premi, tombola, errori)  
✅ La TUI riceve `False` da `avvia_partita_sicura` e mostra sempre `CTRL_AVVIO_FALLITO_GENERICO`  
✅ La TUI cattura il `ValueError` di `ottieni_stato_sintetico` e mostra un messaggio di errore critico  
✅ I messaggi di errore controller non contengono emoji che interferiscono con lo screen reader  
✅ Il loop di gioco v0.8.0 può collegare il renderer senza rischio di output duplicato o interlacciato  

---

**Fine Design Document**
