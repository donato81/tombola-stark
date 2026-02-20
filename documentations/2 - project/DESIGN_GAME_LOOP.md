# 🎨 Design Document - Game Loop

> **FASE: CONCEPT & FLOW DESIGN**
> Nessuna decisione tecnica qui - solo logica e flussi concettuali
> Equivalente a "diagrammi di flusso sulla lavagna"

---

## 📌 Metadata

- **Data Inizio**: 2026-02-20
- **Stato**: DRAFT
- **Versione Target**: v0.9.0
- **Autore**: AI Assistant + donato81

---

## 💡 L'Idea in 3 Righe

Le versioni precedenti hanno costruito tutti i componenti del gioco separatamente: la configurazione pre-partita (v0.7.0), il controller silenzioso (v0.8.0), il renderer e il sistema di eventi. La v0.9.0 li collega per la prima volta in un gioco completo e giocabile end-to-end. Vogliamo che il giocatore — dopo aver configurato nome, bot e cartelle — possa giocare una partita intera: segnare numeri, consultare le sue cartelle, annunciare vittorie e vedere i risultati fino alla schermata finale, il tutto tramite input testuale sequenziale accessibile a screen reader.

---

## 🎭 Attori e Concetti

### Attori (Chi/Cosa Interagisce)

- **Giocatore Umano**: Interagisce con il gioco tramite tastiera. Risponde ai menu, segna numeri, consulta cartelle, annuncia vittorie o passa il turno.
- **TUI** (`ui_terminale.py`): Unico attore autorizzato a scrivere su stdout. Gestisce il loop di gioco, mostra menu, legge input e presenta output del renderer. Riceve dati strutturati esclusivamente dal Controller.
- **Controller** (`game_controller.py`): Silenzioso per contratto (v0.8.0). Esegue turni, fornisce lo stato della partita, restituisce dati strutturati. Non scrive mai su stdout.
- **Renderer** (`renderer_terminal.py`): Trasforma eventi e dizionari di stato in righe testuali pronte per stdout e screen reader. Non decide cosa mostrare: traduce solo quello che la TUI gli passa.
- **Bot** (`GiocatoreAutomatico`): Gioca automaticamente durante ogni turno. I suoi reclami e premi vengono vocalizzati dalla TUI tramite il renderer alla fine di ogni turno.
- **Sistema di Logging**: Canale silenzioso per diagnostica sviluppatore. Scrive su file, mai su stdout.
- **Dizionario Localizzazione** (`it.py`): Unica sorgente di tutti i testi leggibili dall'utente. Nessuna stringa hardcoded nella TUI o nel renderer.

### Concetti Chiave

#### Loop di Partita
- **Cos'è**: Il ciclo principale del gioco che si ripete per ogni turno fino alla fine della partita
- **Stati possibili**: In attesa di azione pre-turno, In esecuzione turno, In vocalizzazione risultati, In verifica terminazione, Terminato
- **Proprietà**: Gestisce l'interazione tra il giocatore umano e il motore di gioco per tutti i 90 numeri estraibili

#### Turno di Gioco
- **Cos'è**: Un'unità atomica di gioco composta da una fase di azione pre-estrazione e una fase di estrazione del numero
- **Stati possibili**: Attesa azione, Esecuzione estrazione, Presentazione risultati
- **Proprietà**: Ogni turno estrae esattamente un numero. Prima dell'estrazione il giocatore può agire zero o più volte (solo azioni informative)

#### Azione Pre-Turno
- **Cos'è**: Qualsiasi azione che il giocatore esegue prima di richiedere l'estrazione del numero
- **Tipi**: Informativa (non avanza il turno), Di avanzamento (avanza al turno successivo o alla verifica), Di uscita (interrompe la partita)
- **Proprietà**: Le azioni informative possono ripetersi senza limiti nello stesso turno; le azioni di avanzamento terminano la fase pre-turno

#### Azione Informativa
- **Cos'è**: Un'azione che il giocatore esegue per consultare o modificare lo stato delle sue cartelle, senza richiedere l'estrazione del numero
- **Esempi**: segnare un numero già estratto, consultare una cartella, chiedere lo stato del focus, mostrare l'help
- **Proprietà**: Dopo l'esecuzione, il sistema torna in attesa della prossima azione pre-turno (rimane in Fase F)

#### Azione di Avanzamento
- **Cos'è**: Un'azione che porta il gioco alla fase di estrazione del numero (Fase G)
- **Esempi**: passare direttamente all'estrazione, annunciare una vittoria pre-turno
- **Proprietà**: Ce n'è sempre esattamente una per turno; dopo di essa non è più possibile tornare alla fase pre-turno

#### Schermata di Fine Partita
- **Cos'è**: La presentazione finale del riepilogo della partita dopo che la condizione di terminazione è stata rilevata
- **Stati possibili**: Terminata per tombola, Terminata per numeri esauriti
- **Proprietà**: Non prevede input interattivi; mostra il riepilogo completo e termina il programma

### Relazioni Concettuali

```
Giocatore Umano
  ↕ input/output da tastiera
TUI (ui_terminale.py)  ←── unico gestore stdout
  ↓ chiama per ogni turno              ↓ legge testi da
Controller (game_controller.py)     it.py (MESSAGGI_LOOP_*)
  ↓ ritorna dict/bool/None/ValueError
  ↓ scrive diagnostica in
GameLogger → tombola_stark.log
  ↓ eventi strutturati arrivano a
Renderer (renderer_terminal.py)
  ↓ produce righe pronte
TUI → stampa su stdout
```

---

## ⚙️ Infrastruttura Esistente Riutilizzata (v0.9.0)

Questa sezione documenta i componenti già disponibili che v0.9.0 **usa senza modificare**.

### Funzioni del Controller già pronte

| Funzione | Contratto di ritorno | Uso nel loop |
|---|---|---|
| `crea_partita_standard(...)` | `Partita` | Già chiamata in `_avvia_partita` (Stato E) |
| `avvia_partita_sicura(partita)` | `True` / `False` | Già chiamata in `_avvia_partita` (Stato E) |
| `esegui_turno_sicuro(partita)` | `dict` / `None` | Chiamata in Fase G per ogni estrazione |
| `partita_terminata(partita)` | `bool` | Chiamata in Fase I dopo ogni turno |
| `ottieni_stato_sintetico(partita)` | `dict` / `ValueError` | Chiamata in Fase J per il riepilogo finale |

### Handler del Renderer già pronti

Il `TerminalRenderer` già gestisce (via `render_esito()`) tutti gli eventi prodotti dai metodi del `GiocatoreUmano`. Non occorre aggiungere handler per le azioni informative del giocatore: il renderer sa già vocalizzare `EventoSegnazioneNumero`, `EventoVisualizzaCartellaAvanzata`, `EventoStatoFocusCorrente`, `EventoReclamoVittoria`, `EventoEsitoReclamoVittoria`, `EventoFineTurno` e tutti gli altri eventi del catalogo esistente.

### Sub-logger del Controller già configurati

Il pattern di logging del controller è già operativo e va esteso alla TUI per il loop:

```
_logger_game   → tombola_stark.game    (eventi di turno, transizioni stato)
_logger_prizes → tombola_stark.prizes  (premi umano e bot)
_logger_system → tombola_stark.system  (stati inattesi, menu invalidi)
_logger_errors → tombola_stark.errors  (input invalidi, abbandono partita)
```

---

## 📦 Struttura dei Nuovi Componenti (v0.9.0)

### `game_controller.py` (modifica — aggiunta di una sola funzione)

#### `ottieni_giocatore_umano(partita)`

Nuova funzione pubblica che restituisce il primo `GiocatoreUmano` dalla lista giocatori della partita. La TUI ne ha bisogno per chiamare i metodi interattivi del giocatore umano (`segna_numero`, `annuncia_vittoria`, `passa_turno_con_reclamo`, ecc.) senza mai importare direttamente dal Domain Layer.

- **Contratto di ritorno**: `GiocatoreUmano` se trovato
- **Eccezione**: `ValueError` se la partita non contiene giocatori umani (bug di programmazione)
- **Logging**: `DEBUG` via `_logger_game`
- **Motivazione**: Rispetta la regola architetturale che la TUI consuma **solo** il Controller

### `bingo_game/events/codici_loop.py` (nuovo)

File di costanti stringa per i codici evento del loop di gioco, seguendo il pattern già in uso per `codici_controller.py` e `Codici_Errori`.

**Costanti definite**:

| Costante | Valore stringa | Descrizione |
|---|---|---|
| `LOOP_MENU_PRINCIPALE` | `"loop.menu_principale"` | Testo del menu azioni pre-turno |
| `LOOP_INPUT_NON_VALIDO` | `"loop.input_non_valido"` | Input non riconosciuto dal menu |
| `LOOP_RICHIESTA_NUMERO_SEGNA` | `"loop.richiesta_numero_segna"` | Prompt per il numero da segnare |
| `LOOP_RICHIESTA_TIPO_VITTORIA` | `"loop.richiesta_tipo_vittoria"` | Prompt per il tipo di vittoria |
| `LOOP_NUMERO_ESTRATTO` | `"loop.numero_estratto"` | Testo "Estratto: N" |
| `LOOP_PREMIO_UMANO` | `"loop.premio_umano"` | Premio conquistato dall'umano |
| `LOOP_RECLAMO_BOT_ACCETTATO` | `"loop.reclamo_bot_accettato"` | Premio conquistato da un bot |
| `LOOP_RECLAMO_BOT_RIFIUTATO` | `"loop.reclamo_bot_rifiutato"` | Reclamo bot non valido |
| `LOOP_TOMBOLA_RILEVATA` | `"loop.tombola_rilevata"` | Annuncio di tombola |
| `LOOP_NUMERI_ESAURITI` | `"loop.numeri_esauriti"` | Tutti i 90 numeri estratti |
| `LOOP_FINE_PARTITA_INTESTAZIONE` | `"loop.fine_partita_intestazione"` | Apertura schermata finale |
| `LOOP_FINE_PARTITA_TURNI` | `"loop.fine_partita_turni"` | "Turni giocati: N" |
| `LOOP_FINE_PARTITA_ESTRATTI` | `"loop.fine_partita_estratti"` | "N numeri estratti su 90" |
| `LOOP_FINE_PARTITA_PREMI` | `"loop.fine_partita_premi"` | Riepilogo premi assegnati |
| `LOOP_FINE_PARTITA_VINCITORE` | `"loop.fine_partita_vincitore"` | Nome vincitore tombola |
| `LOOP_FINE_PARTITA_NESSUNA_TOMBOLA` | `"loop.fine_partita_nessuna_tombola"` | Partita senza tombola |
| `LOOP_ABBANDONO_PARTITA` | `"loop.abbandono_partita"` | Conferma abbandono con `q` |
| `LOOP_CONFERMA_ABBANDONO` | `"loop.conferma_abbandono"` | Prompt conferma `q` |

### `bingo_game/ui/locales/it.py` (modifica)

Aggiunta del dizionario `MESSAGGI_LOOP` al file di localizzazione esistente, con import delle costanti da `codici_loop.py`. Il pattern è identico a quello già in uso per `MESSAGGI_CONTROLLER`.

**Struttura concettuale del dizionario**:

```
MESSAGGI_LOOP: dict[str, tuple[str, ...]] = {
    LOOP_MENU_PRINCIPALE:         ("--- Azioni disponibili ---",
                                   "P - Passa: estrai il prossimo numero",
                                   "S - Segna: segna un numero sulla tua cartella",
                                   "C - Consulta: visualizza la cartella corrente",
                                   "V - Vittoria: annuncia una vittoria",
                                   "? - Aiuto: mostra stato focus corrente",
                                   "Q - Abbandona: esci dalla partita"),
    LOOP_INPUT_NON_VALIDO:        ("Comando non riconosciuto. Riprova.",),
    LOOP_RICHIESTA_NUMERO_SEGNA:  ("Inserisci il numero da segnare: ",),
    LOOP_RICHIESTA_TIPO_VITTORIA: ("Tipo di vittoria (ambo/terno/quaterna/cinquina/tombola): ",),
    LOOP_NUMERO_ESTRATTO:         ("Numero estratto: {numero}",),
    LOOP_PREMIO_UMANO:            ("Hai vinto: {premio} sulla cartella {cartella}",),
    LOOP_RECLAMO_BOT_ACCETTATO:   ("{nome_bot} ha vinto: {premio}",),
    LOOP_RECLAMO_BOT_RIFIUTATO:   ("{nome_bot} ha annunciato {premio} ma non e' valido",),
    LOOP_TOMBOLA_RILEVATA:        ("TOMBOLA! {nome} ha vinto la partita!",),
    LOOP_NUMERI_ESAURITI:         ("Tutti i 90 numeri sono stati estratti. Fine partita.",),
    LOOP_FINE_PARTITA_INTESTAZIONE: ("--- Fine Partita ---",),
    LOOP_FINE_PARTITA_TURNI:      ("Turni giocati: {turni}",),
    LOOP_FINE_PARTITA_ESTRATTI:   ("{estratti} numeri estratti su 90",),
    LOOP_FINE_PARTITA_PREMI:      ("Premi assegnati: {premi}",),
    LOOP_FINE_PARTITA_VINCITORE:  ("{nome} ha vinto con la tombola al turno {turno}",),
    LOOP_FINE_PARTITA_NESSUNA_TOMBOLA: ("Nessuna tombola. Partita terminata per numeri esauriti.",),
    LOOP_ABBANDONO_PARTITA:       ("Partita abbandonata.",),
    LOOP_CONFERMA_ABBANDONO:      ("Confermi abbandono? (s/n): ",),
}
```

### `renderer_terminal.py` (modifica — aggiunta di due metodi)

#### `render_risultato_turno(risultato: dict) -> Sequence[str]`

Metodo che trasforma il dizionario restituito da `esegui_turno_sicuro()` in righe pronte per stdout. Rispetta la gerarchia di vocalizzazione ottimizzata per screen reader (vedi Sezione "Accessibilità — Gerarchia di Vocalizzazione").

#### `render_riepilogo_fine_partita(stato: dict) -> Sequence[str]`

Metodo che trasforma il dizionario di `ottieni_stato_sintetico()` in righe pronte per la schermata finale. Nessuna stringa hardcoded: usa esclusivamente `MESSAGGI_LOOP`.

### `ui_terminale.py` (modifica — completamento e aggiunta metodi)

#### `_avvia_partita` (completamento)

Rimozione del `TODO C7-D` e aggiunta della chiamata a `_loop_partita(partita)` dopo il controllo di `esito`.

#### `_loop_partita(partita)` (nuovo)

Metodo principale del loop. Implementa la macchina a stati F→J (vedi sezione "Stati e Transizioni").

#### `_chiedi_azione_turno()` (nuovo)

Helper per la Fase F. Mostra il menu, legge l'input, classifica l'azione e ritorna il codice azione.

#### `_esegui_azione_informativa(codice, giocatore, partita)` (nuovo)

Helper per le azioni di tipo informativo in Fase F. Esegue l'azione, passa l'esito al renderer, stampa le righe.

#### `_schermata_fine_partita(partita)` (nuovo)

Metodo per la Fase J. Chiama `ottieni_stato_sintetico`, passa il risultato al renderer e stampa le righe del riepilogo finale.

---

## 🎬 Scenari & Flussi

### Scenario 1: Turno Standard — Giocatore Passa Direttamente

**Punto di partenza**: Partita in corso. Il giocatore ha appena finito di leggere il risultato del turno precedente e non vuole eseguire azioni pre-turno.

**Flusso**:

1. **TUI**: Mostra il menu azioni pre-turno tramite `MESSAGGI_LOOP[LOOP_MENU_PRINCIPALE]`
   → **Giocatore**: Digita `p` e preme Invio

2. **TUI** (Fase G): Chiama `esegui_turno_sicuro(partita)`
   → **Controller**: Estrae il numero, esegue i reclami bot, verifica premi. Ritorna il dizionario del turno.

3. **TUI** (Fase H): Passa il dizionario a `renderer.render_risultato_turno(risultato)`
   → **Renderer**: Produce le righe nella gerarchia: numero estratto → eventuali premi umano → eventuali reclami bot → eventuale tombola
   → **stdout**: Una riga per informazione, lineare per screen reader

4. **TUI** (Fase I): Chiama `partita_terminata(partita)` → `False`
   → **TUI**: Torna a Fase F (prossimo turno)

**Punto di arrivo**: Il turno è completato, il giocatore è informato del numero estratto e degli esiti dei bot.

**Cosa cambia rispetto alla v0.8.0**: Il TODO C7-D viene completato. La partita è finalmente giocabile.

---

### Scenario 2: Turno con Azioni Informative Multiple

**Punto di partenza**: Il numero 45 è stato estratto nel turno precedente. Il giocatore sa di averlo sulla cartella ma non l'ha ancora segnato.

**Flusso**:

1. **TUI** (Fase F): Mostra menu pre-turno
   → **Giocatore**: Digita `s` per segnare

2. **TUI**: Mostra prompt `LOOP_RICHIESTA_NUMERO_SEGNA`
   → **Giocatore**: Digita `45`

3. **TUI**: Chiama `giocatore_umano.segna_numero(45)` (via Controller)
   → **Renderer**: Vocalizza `EventoSegnazioneNumero` → `"Numero 45 segnato sulla cartella 1, riga 2"`

4. **TUI** (Fase F): Torna al menu pre-turno — **non avanza il turno**
   → **Giocatore**: Digita `c` per consultare la cartella

5. **TUI**: Chiama `giocatore_umano.visualizza_cartella_corrente_avanzata()` (via Controller)
   → **Renderer**: Vocalizza `EventoVisualizzaCartellaAvanzata` con i numeri segnati

6. **TUI** (Fase F): Torna al menu pre-turno
   → **Giocatore**: Digita `p` per passare

7. **TUI** (Fase G → H → I): Estrae numero, vocalizza, verifica terminazione → torna a Fase F

**Punto di arrivo**: Il giocatore ha segnato il numero, consultato la cartella e poi estratto il prossimo numero. Tutto in un unico turno.

**Cosa cambia**: La Fase F è un ciclo indipendente che termina solo con `p`, `v` (avanzamento) o `q` (uscita).

---

### Scenario 3: Annuncio Vittoria Pre-Turno

**Punto di partenza**: Il giocatore ritiene di aver completato un ambo sulla sua cartella e vuole annunciarlo prima dell'estrazione successiva.

**Flusso**:

1. **TUI** (Fase F): Mostra menu pre-turno
   → **Giocatore**: Digita `v` per vittoria

2. **TUI**: Mostra prompt `LOOP_RICHIESTA_TIPO_VITTORIA`
   → **Giocatore**: Digita `ambo`

3. **TUI**: Chiama il metodo di annuncio vittoria del giocatore umano (via Controller)
   → **Renderer**: Vocalizza `EventoReclamoVittoria` → conferma registrazione reclamo

4. **TUI** (Fase G): L'annuncio vittoria è un'azione di avanzamento — procede all'estrazione
   → **Controller**: Esegue turno. La Partita valida il reclamo a fine turno.

5. **TUI** (Fase H): Vocalizza il risultato del turno incluso l'esito del reclamo
   → **Renderer**: Se reclamo accettato → `EventoEsitoReclamoVittoria` con successo; se rigettato → evento con motivazione

**Punto di arrivo**: Il giocatore ha annunciato la vittoria e riceve immediatamente l'esito dopo l'estrazione.

---

### Scenario 4: Fine Partita per Tombola

**Punto di partenza**: Al termine del turno, `esegui_turno_sicuro` restituisce `tombola_rilevata: True`.

**Flusso**:

1. **TUI** (Fase H): `render_risultato_turno` include la riga tombola come ultima informazione
   → **stdout**: `"TOMBOLA! Mario ha vinto la partita!"`

2. **TUI** (Fase I): `partita_terminata(partita)` → `True`
   → **TUI**: Esce dal loop, entra in Fase J

3. **TUI** (Fase J): `_schermata_fine_partita(partita)` chiama `ottieni_stato_sintetico`
   → **Renderer**: Produce le righe del riepilogo — intestazione, turni, estratti, premi, vincitore

4. **TUI**: Stampa tutte le righe del riepilogo finale e termina il metodo

**Punto di arrivo**: Il giocatore ha sentito l'annuncio tombola, poi il riepilogo completo della partita. Il programma termina.

---

### Scenario 5: Fine Partita per Numeri Esauriti

**Punto di partenza**: Il novantesimo numero è stato estratto. `esegui_turno_sicuro` restituisce `partita_terminata: True` ma `tombola_rilevata: False`.

**Flusso**:

1. **TUI** (Fase H): `render_risultato_turno` include la riga numeri esauriti
   → **stdout**: `"Tutti i 90 numeri sono stati estratti. Fine partita."`

2. **TUI** (Fase I): `partita_terminata(partita)` → `True` → entra in Fase J

3. **TUI** (Fase J): Riepilogo finale con `LOOP_FINE_PARTITA_NESSUNA_TOMBOLA`
   → **stdout**: `"Nessuna tombola. Partita terminata per numeri esauriti."`

**Punto di arrivo**: Riepilogo chiaro, senza vincitore. Il programma termina.

---

### Scenario 6: Abbandono Partita

**Punto di partenza**: Il giocatore in Fase F digita `q`.

**Flusso**:

1. **TUI** (Fase F): Riconosce `q` come azione di uscita
   → **TUI**: Mostra prompt di conferma `LOOP_CONFERMA_ABBANDONO`

2. **Giocatore**: Digita `s` per confermare
   → **TUI**: Stampa `MESSAGGI_LOOP[LOOP_ABBANDONO_PARTITA]`
   → **Logging**: `_logger_errors` a livello `WARNING` — `"[LOOP] Partita abbandonata dal giocatore al turno N"`
   → **TUI**: Esce dal loop senza passare per Fase J (nessun riepilogo)

3. **Giocatore**: Digita `n` per annullare
   → **TUI**: Torna al menu pre-turno (rimane in Fase F)

**Punto di arrivo**: Se confermato, la partita termina immediatamente senza riepilogo. L'evento è loggato per diagnostica.

---

### Scenario 7: Input Invalido nel Menu

**Punto di partenza**: In Fase F, il giocatore digita un carattere non riconosciuto (es. `x`, `3`, stringa vuota).

**Sistema dovrebbe**:
- Stampare `MESSAGGI_LOOP[LOOP_INPUT_NON_VALIDO]`
- Logare a livello `WARNING` su `_logger_system` — `"[LOOP] Input non valido in menu: '{input}' al turno N"`
- Tornare al menu pre-turno senza modificare lo stato del gioco

---

### Scenario 8: Errore Critico — `ottieni_stato_sintetico` Lancia `ValueError`

**Cosa succede se**: In Fase J, il metodo del controller lancia `ValueError` (indica un bug nella TUI).

**Sistema dovrebbe**:
- Catturare il `ValueError` tramite `_ottieni_stato_sicuro` (già implementato)
- Logare a livello `ERROR` su `_logger_errors`
- Stampare `MESSAGGI_CONTROLLER[CTRL_TURNO_FALLITO_GENERICO]` come fallback
- Terminare il metodo senza crash del programma

---

### Scenario 9: `esegui_turno_sicuro` Restituisce `None`

**Cosa succede se**: Il controller non riesce a eseguire il turno e restituisce `None`.

**Sistema dovrebbe**:
- Determinare il tipo di fallimento: stato non in corso → `CTRL_TURNO_NON_IN_CORSO`; numeri esauriti → `CTRL_NUMERI_ESAURITI`; generico → `CTRL_TURNO_FALLITO_GENERICO`

> **Nota di design**: La TUI in v0.9.0 non ha un meccanismo nativo per distinguere il tipo di `None`. Il controller gestisce già `partita_terminata` separatamente; se `esegui_turno_sicuro` ritorna `None`, la TUI verifica subito `partita_terminata(partita)` per scegliere il messaggio corretto. Se la partita è terminata → `CTRL_NUMERI_ESAURITI`; altrimenti → `CTRL_TURNO_FALLITO_GENERICO`.

---

## 🔀 Stati e Transizioni

### Diagramma Completo della Macchina a Stati (v0.7.0 → v0.9.0)

```
[Stato A: BENVENUTO]
      ↓ (automatico)
[Stato B: ATTESA_NOME]
      ↓ (nome valido)
[Stato C: ATTESA_BOT]
      ↓ (numero bot valido)
[Stato D: ATTESA_CARTELLE]
      ↓ (numero cartelle valido)
[Stato E: AVVIO_PARTITA]
      ↓ (avvio riuscito → True)
      ↓ ←──────────────────────────────────────────┐
[Stato F: ATTESA_AZIONE_PRE_TURNO]                 │
      ↓ azione informativa (s,c,?)                 │
[Fase F — esegue azione, vocalizza, torna a F]     │
      ↓ azione avanzamento (p,v)                   │
[Stato G: ESECUZIONE_TURNO]                        │
      ↓ (dict del turno)                           │
[Stato H: VOCALIZZAZIONE_RISULTATI]                │
      ↓ (righe stampate)                           │
[Stato I: VERIFICA_TERMINAZIONE]                   │
      ↓ False (partita in corso)  ─────────────────┘
      ↓ True (partita terminata)
[Stato J: FINE_PARTITA]
      ↓
[Programma termina]

--- Percorsi alternativi ---
Stato F → q (abbandono confermato) → [Programma termina senza Stato J]
Stato E → avvio fallito (False)    → [TUI mostra errore, termina]
```

### Dettaglio degli Stati

#### Stato F: ATTESA_AZIONE_PRE_TURNO
- **Descrizione**: La TUI mostra il menu e aspetta un comando dell'utente
- **Può passare a**: F (azione informativa), G (azione di avanzamento), uscita (abbandono confermato)
- **Trigger**: Input dell'utente

#### Stato G: ESECUZIONE_TURNO
- **Descrizione**: La TUI chiama `esegui_turno_sicuro(partita)` e riceve il risultato
- **Può passare a**: H (risultato ricevuto), gestione errore (None ricevuto)
- **Trigger**: Chiamata al Controller automatica (nessun input utente)

#### Stato H: VOCALIZZAZIONE_RISULTATI
- **Descrizione**: La TUI passa il risultato al renderer e stampa le righe
- **Può passare a**: I (stampa completata)
- **Trigger**: Completamento stampa (nessun input utente)

#### Stato I: VERIFICA_TERMINAZIONE
- **Descrizione**: La TUI chiama `partita_terminata(partita)` per decidere se continuare o terminare
- **Può passare a**: F (partita ancora in corso), J (partita terminata)
- **Trigger**: Chiamata al Controller automatica (nessun input utente)

#### Stato J: FINE_PARTITA
- **Descrizione**: La TUI chiama `ottieni_stato_sintetico` e stampa il riepilogo finale
- **Può passare a**: [Termina] (nessun ritorno al loop)
- **Trigger**: Completamento stampa del riepilogo (nessun input utente)

---

## 🎮 Interazione Utente — UX Concettuale

### Comandi Disponibili in Fase F

- **`p` — Passa** (azione di avanzamento):
  - Fa cosa? Richiede l'estrazione del prossimo numero senza azioni aggiuntive
  - Quando disponibile? Sempre in Fase F
  - Feedback atteso: Nessuno prima dell'estrazione; poi output Fase H

- **`s` — Segna** (azione informativa):
  - Fa cosa? Chiede un numero e lo segna sulla cartella attiva (se estratto e non già segnato)
  - Quando disponibile? Sempre in Fase F
  - Feedback atteso: Risposta del renderer sull'esito della segnazione (successo / già segnato / non presente / non estratto)

- **`c` — Consulta** (azione informativa):
  - Fa cosa? Visualizza la cartella corrente in modalità avanzata (con numeri segnati evidenziati)
  - Quando disponibile? Sempre in Fase F
  - Feedback atteso: Output completo della cartella con indicatori di segnatura

- **`v` — Vittoria** (azione di avanzamento):
  - Fa cosa? Permette di annunciare un tipo di vittoria (ambo/terno/quaterna/cinquina/tombola) prima dell'estrazione
  - Quando disponibile? Sempre in Fase F
  - Feedback atteso: Conferma registrazione reclamo, poi al turno successivo l'esito della validazione

- **`?` — Aiuto** (azione informativa):
  - Fa cosa? Mostra lo stato del focus corrente (cartella, riga, colonna attive)
  - Quando disponibile? Sempre in Fase F
  - Feedback atteso: Report fisso su 3 righe (cartella N, riga N, colonna N)

- **`q` — Abbandona** (azione di uscita):
  - Fa cosa? Avvia la procedura di abbandono con richiesta di conferma
  - Quando disponibile? Sempre in Fase F
  - Feedback atteso: Prompt di conferma; se confermato → partita abbandonata; se annullato → torna al menu

### Feedback di Sistema in Fase H

La Fase H produce output sempre nella stessa gerarchia per garantire la leggibilità agli screen reader:

1. **Numero estratto** — sempre presente, prima informazione: `"Numero estratto: 42"`
2. **Premi umano** — se presenti, subito dopo il numero: `"Hai vinto: ambo sulla cartella 2"` (zero o più righe)
3. **Reclami e premi bot** — dopo i premi umano: `"Bot 1 ha vinto: ambo"` o `"Bot 2 ha annunciato tombola ma non e' valido"` (zero o più righe)
4. **Tombola rilevata** — se presente, ultima informazione: `"TOMBOLA! Mario ha vinto la partita!"`
5. **Numeri esauriti** — alternativo alla tombola, ultima informazione: `"Tutti i 90 numeri sono stati estratti. Fine partita."`

**Principio di linearità**: ogni informazione occupa una sola riga. Nessun box ASCII, nessuna decorazione estetica. Il pattern è già consolidato nel renderer esistente.

### Navigazione Concettuale Completa

1. Utente apre il programma → Stato A (benvenuto)
2. Inserisce nome, bot, cartelle → Stati B, C, D
3. Partita configurata e avviata → Stato E
4. Vede il menu pre-turno → Stato F
5. Esegue zero o più azioni informative → Rimane in Stato F
6. Passa (`p`) o annuncia vittoria (`v`) → Stato G
7. Sente numero estratto e risultati → Stato H
8. Se partita continua → torna a Stato F
9. Se partita terminata → Stato J (riepilogo)
10. Programma termina

---

## ♿ Accessibilità — Gerarchia di Vocalizzazione

Questa sezione definisce i principi che guidano `render_risultato_turno` per garantire un output ottimale con screen reader NVDA/JAWS/Orca.

### Principi Fondamentali

- **Un'informazione per riga**: ogni riga è una unità semantica autonoma. Lo screen reader la legge senza ambiguità.
- **Informazione più importante prima**: il numero estratto è sempre la prima riga, perché è l'evento principale del turno.
- **Ordine di interesse decrescente**: umano prima, poi bot; vittoria propria prima di vittoria altrui.
- **Nessuna riga decorativa**: vietate righe come `"---"`, `"==="`, `"*** *** ***"`. Non aggiungono informazione e vengono lette dallo screen reader.
- **Messaggi auto-contenuti**: ogni riga deve essere comprensibile da sola, senza contesto delle righe precedenti.

### Gerarchia Fissa di `render_risultato_turno`

```
Riga 1:  [OBBLIGATORIA] Numero estratto
          "Numero estratto: {numero}"

Righe 2..N: [CONDIZIONALI] Premi del giocatore umano (zero o più)
          "Hai vinto: {premio} sulla cartella {numero_cartella}"
          Una riga per ogni premio. Nell'ordine in cui la Partita li restituisce.

Righe N+1..M: [CONDIZIONALI] Reclami dei bot — accettati prima, rifiutati dopo
          "{nome_bot} ha vinto: {premio}"                    ← accettati
          "{nome_bot} ha annunciato {premio} ma non valido"  ← rifiutati

Riga finale: [CONDIZIONALE — esclusiva] Tombola OPPURE Numeri Esauriti
          "TOMBOLA! {nome} ha vinto la partita!"
          — oppure —
          "Tutti i 90 numeri sono stati estratti. Fine partita."
```

---

## 🧪 Protocollo di Test

### Categoria 1: Test di Validazione Input

**Test 1.1 — Input valido nel menu**

```
DATO  la TUI è in Fase F
QUANDO l'utente digita "p" (o "P" maiuscolo)
ALLORA la TUI avanza a Fase G senza errori
```

**Test 1.2 — Input non valido nel menu**

```
DATO  la TUI è in Fase F
QUANDO l'utente digita "x" o "3" o stringa vuota
ALLORA la TUI stampa LOOP_INPUT_NON_VALIDO
E      rimane in Fase F (non avanza il turno)
E      logga WARNING su _logger_system
```

**Test 1.3 — Numero da segnare non intero**

```
DATO  il giocatore ha scelto "s" per segnare
QUANDO digita "abc" come numero
ALLORA la TUI gestisce il ValueError di int()
E      mostra MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"]
E      torna al prompt di inserimento numero
```

**Test 1.4 — Tipo vittoria non valido**

```
DATO  il giocatore ha scelto "v" per vittoria
QUANDO digita "sestina" come tipo vittoria (non esiste)
ALLORA la TUI mostra un messaggio di errore e ripete il prompt
```

### Categoria 2: Test di Simulazione Partita Completa (Mocking)

**Test 2.1 — Partita termina in tombola**

```
DATO  una partita mockata con esegui_turno_sicuro che ritorna
      tombola_rilevata=True all'N-esimo turno
QUANDO si esegue _loop_partita con input automatici "p" per ogni turno
ALLORA il loop termina dopo l'N-esimo turno
E      viene chiamata _schermata_fine_partita
E      l'output include LOOP_TOMBOLA_RILEVATA e LOOP_FINE_PARTITA_VINCITORE
```

**Test 2.2 — Partita termina per numeri esauriti**

```
DATO  una partita mockata con partita_terminata che ritorna True
      dopo 90 turni e tombola_rilevata=False
QUANDO si esegue _loop_partita
ALLORA l'output include LOOP_NUMERI_ESAURITI e LOOP_FINE_PARTITA_NESSUNA_TOMBOLA
```

**Test 2.3 — Abbandono confermato**

```
DATO  la TUI è in Fase F
QUANDO l'utente digita "q" poi "s" (conferma)
ALLORA il loop termina senza chiamare _schermata_fine_partita
E      il log contiene WARNING su _logger_errors
```

**Test 2.4 — Abbandono annullato**

```
DATO  la TUI è in Fase F
QUANDO l'utente digita "q" poi "n" (annulla)
ALLORA il loop NON termina e torna a Fase F
```

**Test 2.5 — `esegui_turno_sicuro` restituisce None**

```
DATO  una partita mockata con esegui_turno_sicuro che ritorna None
QUANDO si esegue _loop_partita
ALLORA la TUI mostra CTRL_TURNO_FALLITO_GENERICO (o CTRL_NUMERI_ESAURITI se partita terminata)
E      non crasha
```

### Categoria 3: Test sul Renderer

**Test 3.1 — Gerarchia di vocalizzazione**

```
DATO  un dizionario di turno con numero_estratto=42,
      premi_nuovi=[{premio: "ambo", ...}],
      reclami_bot=[{successo: True, premio: "terno", ...}]
QUANDO si chiama render_risultato_turno(risultato)
ALLORA la prima riga contiene "42"
E      la seconda riga contiene "ambo"
E      la terza riga contiene il nome del bot e "terno"
```

**Test 3.2 — Turno senza premi né reclami**

```
DATO  un dizionario con solo numero_estratto=7,
      premi_nuovi=[], reclami_bot=[]
QUANDO si chiama render_risultato_turno(risultato)
ALLORA l'output è esattamente una riga con "7"
```

**Test 3.3 — Nessuna stringa hardcoded**

```
ALLORA render_risultato_turno e render_riepilogo_fine_partita
       non contengono nessuna stringa letterale
       (verificabile con ispezione del codice)
```

### Categoria 4: Test di Non-Regressione

**Test 4.1 — Controller silenzioso nel loop**

```
DATO  un loop completo di 5 turni mockati
QUANDO si esegue _loop_partita
ALLORA capsys.readouterr().out del controller è "" per ogni turno
```

**Test 4.2 — Suite esistente invariata**

```
ALLORA i 272+ test esistenti passano senza modifiche
       (nessuna regressione sui layer Domain e Application)
```

---

## 🤔 Domande & Decisioni

### Domande Aperte

- [ ] Il comando `s` (segna) in Fase F deve permettere di segnare numeri **di turni precedenti** non ancora segnati, oppure solo numeri già estratti prima di questo turno? Il renderer già gestisce entrambi i casi (EventoSegnazioneNumero ha esito `non_estratto`), ma il design UX potrebbe differire.
- [ ] Deve esserci un limite al numero di azioni informative eseguibili in un singolo turno pre-estrazione, oppure il giocatore può consultare le cartelle senza limite?
- [ ] L'azione `?` (stato focus) deve mostrare anche il riepilogo degli ultimi numeri estratti, oppure solo il focus cartella/riga/colonna? Il renderer ha già `EventoStatoFocusCorrente` (3 righe) e `EventoRiepilogoTabellone` (3 righe) separati.
- [ ] Serve un comando per **navigare** tra cartelle (cambiare focus cartella) già in v0.9.0, oppure questa funzionalità è riservata alla v0.10.0 (navigazione interattiva con frecce)?

### Decisioni Prese

- ✅ **Loop testuale sequenziale (non interattivo)**: v0.9.0 usa esclusivamente `input()` con invio. La navigazione con frecce e i tasti rapidi sono riservati alla v0.10.0. Motivazione: minimizzare la complessità e consegnare un gioco giocabile prima di aggiungere l'input avanzato.
- ✅ **Azioni di avanzamento terminano la Fase F**: `p` e `v` portano immediatamente a Fase G. Non è possibile tornare a Fase F dopo aver digitato `p` nello stesso turno. Motivazione: coerenza con il ciclo naturale del gioco (un'estrazione per turno).
- ✅ **Abbandono richiede conferma**: Il comando `q` non termina immediatamente. Richiede `s` per confermare. Motivazione: prevenire abbandoni accidentali durante la partita.
- ✅ **Fase J non viene raggiunta in caso di abbandono**: Il riepilogo finale è riservato alle partite terminate normalmente (tombola o numeri esauriti). L'abbandono esce direttamente. Motivazione: coerenza semantica — il riepilogo ha senso solo a partita completata.
- ✅ **`ottieni_giocatore_umano` nel controller**: La TUI non importa mai direttamente `GiocatoreUmano`. Motivazione: rispetto assoluto della regola architetturale che vieta import dal Domain Layer nella TUI (invariante dal v0.7.0).
- ✅ **Gerarchia fissa in `render_risultato_turno`**: L'ordine numero → premi umano → bot → tombola è sempre lo stesso, indipendentemente dal contenuto del dizionario. Motivazione: accessibilità screen reader — l'utente impara dove aspettarsi ogni tipo di informazione.
- ✅ **`codici_loop.py` separato da `codici_controller.py`**: Le costanti del loop vivono nel loro file dedicato. Motivazione: coerenza con il pattern già stabilito; separation of concerns tra codici di controller e codici di UI loop.

### Assunzioni

- Il metodo `GiocatoreUmano.segna_numero()` accetta un intero e ritorna un `EsitoAzione` con `EventoSegnazioneNumero` (già implementato)
- Il metodo `GiocatoreUmano.annuncia_vittoria()` accetta un tipo stringa e ritorna un `EsitoAzione` con `EventoReclamoVittoria` (già implementato)
- Il metodo `GiocatoreUmano.passa_turno_con_reclamo()` esiste nel domain layer e produce `EventoFineTurno` nel dizionario del turno
- Il dizionario di `esegui_turno_sicuro` contiene già le chiavi `premi_nuovi`, `reclami_bot`, `tombola_rilevata`, `partita_terminata` (verificato nel codice del controller)
- La chiave `reclami_bot` nel dizionario del turno è una lista di dict con almeno le chiavi `nome_giocatore`, `successo`, `reclamo` (con attributi `tipo`, `indice_cartella`, `indice_riga`)

---

## 🎯 Opzioni Considerate

### Opzione A: Input a Riga Singola con Comando + Parametro

**Descrizione**: Il giocatore digita il comando e il parametro sulla stessa riga separati da spazio (es. `s 42`, `v ambo`). Il sistema analizza la riga e dispatcha l'azione.

**Pro**:
- ✅ Meno pressioni di Invio (esperienza più fluida per utenti avanzati)
- ✅ Parsing più compatto nel codice

**Contro**:
- ❌ Complessità di parsing (split, gestione errori su parametro mancante)
- ❌ Meno accessibile per utenti screen reader che beneficiano di prompt separati
- ❌ Difficile da estendere (es. parametri con spazi)

---

### Opzione B: Input Sequenziale (Comando prima, Parametro dopo) *(Scelta)*

**Descrizione**: Prima si digita il comando (`s`), il sistema chiede il parametro con un prompt dedicato, poi si digita il parametro.

**Pro**:
- ✅ Massima accessibilità screen reader: ogni prompt è autonomo e chiaramente contestualizzato
- ✅ Validazione separata per comando e parametro (messaggi di errore precisi)
- ✅ Coerente con il pattern già usato negli stati B, C, D di configurazione
- ✅ Nessuna complessità di parsing multi-token

**Contro**:
- ❌ Richiede più pressioni di Invio per azioni con parametri
- ❌ Leggermente più verboso per utenti esperti

**Scelta finale**: **Opzione B**. La priorità di accessibilità screen reader è il vincolo architetturale principale del progetto. L'input sequenziale è già il pattern consolidato della TUI.

---

### Opzione C: Stato di Abbandono Senza Conferma

**Descrizione**: `q` termina immediatamente la partita senza chiedere conferma.

**Pro**:
- ✅ Più veloce per utenti che sanno cosa stanno facendo

**Contro**:
- ❌ Abbandoni accidentali durante la partita (pressione accidentale di `q`)
- ❌ Irrecuperabile: la partita non è salvabile

**Scelta finale**: Scartata. La conferma è obbligatoria per tutelare l'esperienza utente.

---

## ✅ Design Freeze Checklist

- [x] Tutti gli scenari principali mappati (Scenario 1–9)
- [x] Macchina a stati completa (F→J) con transizioni esplicite
- [x] Classificazione azioni: informative vs avanzamento vs uscita
- [x] Gerarchia di vocalizzazione screen reader definita e motivata
- [x] Protocollo di test per input sporco, simulazione completa e regressione
- [x] Nuova funzione `ottieni_giocatore_umano` progettata nel controller
- [x] Nuovi file `codici_loop.py` e `MESSAGGI_LOOP` in `it.py` progettati
- [x] Logging su tutti e 4 i sub-logger mappato agli eventi del loop
- [x] Domande aperte documentate (4 da risolvere prima del PLAN)
- [x] Decisioni chiave prese e motivate (8 decisioni)
- [x] Opzioni valutate e scelta motivata (Opzioni A, B, C)
- [x] Side effects documentali identificati (API.md, ARCHITECTURE.md, README.md, CHANGELOG.md)
- [ ] Domande aperte risolte (4 ancora aperte — richiede decisione donato81)

**Stato**: DRAFT  
**Data**: 2026-02-20

**Next Step**: Risolvere le 4 domande aperte, poi creare `PLAN_GAME_LOOP.md` con:
- File structure e responsabilità precise per ogni metodo
- Strategia di testing dettagliata (fixtures, mocking, sequenza test)
- Sequenza di commit consigliata (atomica per stato della macchina a stati)
- Aggiornamenti `API.md`, `ARCHITECTURE.md`, `README.md`, `CHANGELOG.md`

---

## 📄 Side Effects Documentali (v0.9.0)

Questi aggiornamenti sono obbligatori e fanno parte della Definition of Done della PR v0.9.0.

### `API.md`

Aggiungere la firma e il contratto di `ottieni_giocatore_umano(partita)`. Documentare i due nuovi metodi del renderer (`render_risultato_turno`, `render_riepilogo_fine_partita`). Documentare i nuovi metodi privati della TUI (`_loop_partita`, `_chiedi_azione_turno`, `_schermata_fine_partita`).

### `ARCHITECTURE.md`

Aggiornare il diagramma dei layer per mostrare il loop F→J. Aggiungere `bingo_game/events/codici_loop.py` alla mappa dei moduli. Aggiornare la descrizione della `TerminalUI` da "gestisce stati A→E" a "gestisce stati A→J".

### `README.md`

Aggiornare la sezione "Come si gioca" per descrivere i comandi del loop (`p`, `s`, `c`, `v`, `?`, `q`). Aggiornare la versione da v0.8.0 a v0.9.0.

### `CHANGELOG.md`

```
## [v0.9.0] - 2026-02-20

### Added
- ui_terminale.py: metodi _loop_partita, _chiedi_azione_turno,
  _esegui_azione_informativa, _schermata_fine_partita.
  Loop di gioco completo F→J con macchina a stati.
- game_controller.py: nuova funzione ottieni_giocatore_umano(partita).
- renderer_terminal.py: nuovi metodi render_risultato_turno(risultato)
  e render_riepilogo_fine_partita(stato).
- bingo_game/events/codici_loop.py: costanti stringa per il loop di gioco
  (18 costanti LOOP_*).
- bingo_game/ui/locales/it.py: dizionario MESSAGGI_LOOP con 18 voci.

### Changed
- ui_terminale.py: _avvia_partita completato (rimosso TODO C7-D).
  Ora chiama _loop_partita(partita) dopo avvio riuscito.

### Fixed
- Il gioco è ora giocabile end-to-end dalla configurazione alla fine partita.
```

---

## 📝 Note di Brainstorming

- La v0.9.0 è il "momento della verità" del progetto: per la prima volta tutto il sistema lavora insieme. I bug di integrazione emergeranno qui.
- Il comando `?` (stato focus) potrebbe essere espanso in v0.10.0 per diventare un menu di navigazione completo con frecce.
- In v0.9.0 il giocatore non può navigare tra cartelle diverse dal menu pre-turno. Se il giocatore ha 3 cartelle, può consultare solo la cartella che ha il focus. La navigazione multi-cartella è v0.10.0.
- Il riepilogo finale in Fase J potrebbe in futuro includere statistiche avanzate (percentuale numeri segnati, turni medi per premio, ecc.). Per ora solo i dati disponibili in `ottieni_stato_sintetico`.
- L'abbandono (`q`) non salva la partita. Il salvataggio è fuori scope per tutta la serie 0.x.
- Screen reader test: eseguire la partita completa con NVDA e verificare che nessuna riga di Fase H venga "inglobata" con la riga precedente per via di output troppo rapidi. Potrebbe servire un delay minimo (fuori scope per v0.9.0).
- Attenzione: `input()` in Python blocca il thread. Per v0.9.0 è accettabile (single thread), ma future versioni con timer o musica di sottofondo richiederebbero un input asincrono.

---

## 📚 Riferimenti Contestuali

### Feature Correlate

- **Configurazione Pre-Partita v0.7.0** (`ui_terminale.py`, stati A→E): Il loop F→J è la continuazione diretta dello stato E. Il pattern di validazione input (`while True` + messaggi di errore da catalogo) è riusato invariato in Fase F.
- **Silent Controller v0.8.0** (`game_controller.py`): Il controller è già completamente silenzioso. Tutte le funzioni del loop (`esegui_turno_sicuro`, `partita_terminata`, `ottieni_stato_sintetico`) sono già pronte e testate.
- **TerminalRenderer** (`renderer_terminal.py`): Gli handler per tutti gli eventi del `GiocatoreUmano` sono già implementati (27 handler in `render_esito()`). Il renderer è pronto per essere usato nel loop senza modifiche agli handler esistenti.
- **Sistema di Logging** (`GameLogger`, sub-logger): Il pattern `_log_safe()` con routing su 4 sub-logger è già operativo. Il loop deve seguire le stesse regole di routing definite in `DESIGN_SILENT_CONTROLLER.md`.
- **Navigazione Interattiva v0.10.0** (futura): La v0.9.0 è il prerequisito diretto. Il loop testuale diventerà il loop interattivo quando verrà integrata la libreria di input asincrono.

### Vincoli da Rispettare (Invarianti Architetturali)

- **`TerminalUI` consuma solo il Controller** — vietato importare `GiocatoreUmano`, `Partita`, `Cartella` o qualsiasi altro oggetto del Domain Layer nella TUI
- **Zero stringhe hardcoded nella TUI e nel renderer** — tutti i testi vanno in `it.py` via costanti `codici_loop.py`
- **Pattern `_log_safe()` obbligatorio** — mai `print()` per debug nella TUI o nel controller
- **`EsitoAzione` come contratto di comunicazione** — ogni risposta del `GiocatoreUmano` passa per `renderer.render_esito()` prima di essere stampata
- **Linearità dell'output** — nessuna riga decorativa, ogni riga = un'informazione atomica per screen reader
- **`API.md`, `ARCHITECTURE.md`, `README.md`, `CHANGELOG.md` aggiornati nella stessa PR** — la coerenza documentale è parte della Definition of Done v0.9.0

---

## 🎯 Risultato Finale Atteso

Una volta implementata la v0.9.0, il giocatore potrà:

✅ Avviare una partita di tombola completa dopo la configurazione (stati A→E già funzionanti)
✅ Segnare numeri sulle proprie cartelle prima di ogni estrazione
✅ Consultare la cartella corrente in qualsiasi momento durante il turno pre-estrazione
✅ Annunciare vittorie (ambo, terno, quaterna, cinquina, tombola) e ricevere l'esito
✅ Sentire ogni numero estratto vocalizzato linearmente, ottimizzato per screen reader
✅ Conoscere i premi vinti da sé e dagli avversari bot dopo ogni estrazione
✅ Ricevere il riepilogo completo della partita alla fine (vincitore o numeri esauriti)
✅ Abbandonare la partita in sicurezza con richiesta di conferma

---

**Fine Design Document**
