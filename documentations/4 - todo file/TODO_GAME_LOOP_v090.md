# 📋 TODO – Game Loop (v0.9.0)

**Branch**: `feat/v0.9.0-game-loop`  
**Tipo**: FEATURE  
**Priorità**: HIGH  
**Stato**: COMPLETATO

---

## 📖 Riferimento Documentazione

Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:

`documentations/3 - planning/PLAN_GAME_LOOP.md`

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase dell'implementazione.  
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici.

---

## 🤖 Workflow Agente

> **L'agente di codifica deve completare tutte le fasi in un unico branch (`feat/v0.9.0-game-loop`) per evitare divergenze, eseguendo commit separati per ogni fase.**

Implementare le modifiche in modo **incrementale** su 5 commit atomici e logici.

**Workflow per ogni fase:**

1. **Leggi questo TODO** → Identifica la prossima fase da implementare
2. **Consulta piano completo** → Rivedi dettagli tecnici, architettura, edge case della fase
3. **Implementa modifiche** → Codifica solo la fase corrente (scope limitato)
4. **Commit atomico** → Messaggio conventional, scope chiaro, riferimento fase
5. **Aggiorna questo TODO** → Spunta checkbox completate per la fase
6. **Acquisisci info sommarie** → Rivedi stato globale prima di proseguire
7. **RIPETI** → Passa alla fase successiva (torna al punto 1)

⚠️ **REGOLE FONDAMENTALI:**

- ✅ **Un commit per fase logica** (no mega-commit con tutto)
- ✅ **Dopo ogni commit**: aggiorna questo TODO spuntando checkbox
- ✅ **Prima di ogni fase**: rileggi sezione pertinente nel piano completo
- ✅ **Approccio sequenziale**: fase → commit → aggiorna TODO → fase successiva
- ✅ **Commit message format**: `type(scope): description [Phase N/5]`
- ✅ **Branch unico**: non creare branch separati per sotto-fasi
- ❌ **NO commit multipli senza aggiornare TODO** (perde tracciabilità)
- ❌ **NO import di classi Domain nella TUI** (viola separazione layer)
- ❌ **NO avanzamento turno su comandi informativi** (`s`, `c`, `v`, `?` non chiamano `esegui_turno_sicuro`)

**Esempio workflow reale:**
```
Fase 1: Infrastruttura (codici_loop.py + it.py)
→ Crea file + Modifica it.py + Commit [Phase 1/5] + Aggiorna TODO ✅

Fase 2: Controller (ottieni_giocatore_umano)
→ Rileggi piano sezione Fase 2
→ Modifica game_controller.py + Commit [Phase 2/5] + Aggiorna TODO ✅

Fase 3: TUI Core (_loop_partita + dispatch comandi)
→ Rileggi piano sezione Fase 3
→ Crea tui_partita.py + Commit [Phase 3/5] + Aggiorna TODO ✅

... e così via per le fasi 4 e 5
```

---

## 🎯 Obiettivo Implementazione

- Introdurre il **Game Loop interattivo** della TUI: la macchina a stati `_loop_partita` che governa ogni turno di gioco.
- Esporre un helper `ottieni_giocatore_umano()` nel controller per mantenere la **separazione dei layer** (TUI non importa Domain).
- Supportare i comandi `p`, `s`, `c`, `v`, `q`, `?` con **azioni informative illimitate** prima dell'avanzamento turno.
- Garantire **flessibilità di marcatura**: l'utente può segnare qualsiasi numero estratto, non solo l'ultimo.
- Produrre output **screen reader-ready** (righe autonome, ≤ 120 caratteri, senza ASCII art).

---

## 📂 File Coinvolti

| File | Azione | Fase |
|------|--------|------|
| `bingo_game/events/codici_loop.py` | CREATE | 1 |
| `bingo_game/ui/locales/it.py` | MODIFY — aggiungere 13 chiavi `LOOP_*` | 1 |
| `bingo_game/game_controller.py` | MODIFY — aggiungere `ottieni_giocatore_umano()` | 2 |
| `bingo_game/ui/tui/tui_partita.py` | CREATE | 3 |
| `bingo_game/ui/renderers/renderer_terminal.py` | MODIFY (se necessario) | 4 |
| `tests/unit/test_codici_loop.py` | CREATE | 1 |
| `tests/unit/test_game_controller_loop.py` | CREATE | 2 |
| `tests/unit/test_tui_partita.py` | CREATE | 3 |
| `tests/unit/test_renderer_report_finale.py` | CREATE | 4 |
| `tests/flow/test_flusso_game_loop.py` | CREATE | 5 |
| `docs/API.md` | UPDATE | 5 |
| `docs/ARCHITECTURE.md` | UPDATE | 5 |
| `docs/README.md` | UPDATE | 5 |
| `docs/CHANGELOG.md` | UPDATE | 5 |

---

## 🛠 Checklist Implementazione

---

### 🟡 FASE 1 — Infrastruttura: `codici_loop.py` + `it.py`

> Commit: `feat(infra): add codici_loop.py and LOOP_* keys in it.py [Phase 1/5]`

**Creazione `bingo_game/events/codici_loop.py`**
- [x] Creare il file `bingo_game/events/codici_loop.py`
- [x] Aggiungere costante `LOOP_TURNO_AVANZATO`
- [x] Aggiungere costante `LOOP_NUMERO_ESTRATTO`
- [x] Aggiungere costante `LOOP_SEGNAZIONE_OK`
- [x] Aggiungere costante `LOOP_REPORT_FINALE`
- [x] Aggiungere costante `LOOP_QUIT_CONFERMATO`
- [x] Aggiungere costante `LOOP_QUIT_ANNULLATO`
- [x] Aggiungere costante `LOOP_HELP`
- [x] Aggiungere costante `LOOP_FOCUS_AUTO`
- [x] Verificare che tutte le costanti siano stringhe non vuote e non duplicate

**Aggiornamento `bingo_game/ui/locales/it.py`**
- [x] Aggiungere chiave `LOOP_NUMERO_ESTRATTO` con placeholder `{numero}`
- [x] Aggiungere chiave `LOOP_PROMPT_COMANDO` (testo prompt interattivo)
- [x] Aggiungere chiave `LOOP_HELP_COMANDI` (tupla multi-riga con tutti i comandi)
- [x] Aggiungere chiave `LOOP_HELP_FOCUS` con placeholder `{numero_cartella}`
- [x] Aggiungere chiave `LOOP_QUIT_CONFERMA`
- [x] Aggiungere chiave `LOOP_QUIT_ANNULLATO`
- [x] Aggiungere chiave `LOOP_REPORT_FINALE_INTESTAZIONE`
- [x] Aggiungere chiave `LOOP_REPORT_FINALE_TURNI` con placeholder `{turni}`
- [x] Aggiungere chiave `LOOP_REPORT_FINALE_ESTRATTI` con placeholder `{estratti}`
- [x] Aggiungere chiave `LOOP_REPORT_FINALE_VINCITORE` con placeholder `{nome}`
- [x] Aggiungere chiave `LOOP_REPORT_FINALE_NESSUN_VINCITORE`
- [x] Aggiungere chiave `LOOP_REPORT_FINALE_PREMI` con placeholder `{premi}`
- [x] Aggiungere chiave `LOOP_COMANDO_NON_RICONOSCIUTO`
- [x] Verificare che nessuna chiave esistente in `it.py` sia stata rimossa o modificata

**Testing Fase 1**
- [x] Creare `tests/unit/test_codici_loop.py`
- [x] Test: tutte le costanti `codici_loop` sono stringhe non vuote
- [x] Test: nessuna costante duplicata tra quelle di `codici_loop`
- [x] Test: tutte le 13 chiavi `LOOP_*` presenti in `MESSAGGI_OUTPUT_UI_UMANI`
- [x] Test: template con placeholder sono formattabili senza eccezioni
- [x] Test: import di `codici_loop` non produce side effect
- [x] Eseguire `python -m pytest tests/unit/test_codici_loop.py -v` → tutti PASSED

**Commit Fase 1** *(dopo aver spuntato tutto)*
- [x] `git add bingo_game/events/codici_loop.py bingo_game/ui/locales/it.py tests/unit/test_codici_loop.py`
- [x] `git commit -m "feat(infra): add codici_loop.py and LOOP_* keys in it.py [Phase 1/5]"`
- [x] Aggiornare questo TODO: spuntare tutti i task Fase 1

---

### 🟡 FASE 2 — Controller: `ottieni_giocatore_umano()`

> Commit: `feat(controller): add ottieni_giocatore_umano() helper for TUI isolation [Phase 2/5]`

**Modifica `bingo_game/game_controller.py`**
- [x] Aggiungere la funzione `ottieni_giocatore_umano(partita)` dopo `partita_terminata()`
- [x] Funzione ritorna il primo `GiocatoreUmano` trovato tramite `partita.get_giocatori()`
- [x] Funzione ritorna `None` se nessun `GiocatoreUmano` è presente
- [x] Funzione solleva `ValueError` se `partita` non è un'istanza di `Partita`
- [x] Log `DEBUG` quando il giocatore umano viene trovato (`_log_safe` + `_logger_game`)
- [x] Log `WARNING` quando nessun giocatore umano è trovato (`_log_safe` + `_logger_game`)
- [x] Docstring completa: Args, Returns, Raises, Version (`v0.9.0`)
- [x] Nessuna funzione esistente in `game_controller.py` modificata

**Testing Fase 2**
- [x] Creare `tests/unit/test_game_controller_loop.py`
- [x] Test: `ottieni_giocatore_umano` ritorna il primo giocatore umano
- [x] Test: ritorna `None` se la partita ha solo bot
- [x] Test: solleva `ValueError` se il parametro non è `Partita`
- [x] Test: il log WARNING viene emesso quando nessun umano è trovato
- [x] Test: la funzione non modifica lo stato della partita (nessun side effect)
- [x] Test: `crea_partita_standard` non è regredita (smoke test)
- [x] Test: `esegui_turno_sicuro` non è regredita (smoke test)
- [x] Test: `ottieni_stato_sintetico` non è regredita (smoke test)
- [x] Test: `avvia_partita_sicura` non è regredita (smoke test)
- [x] Eseguire `python -m pytest tests/unit/test_game_controller_loop.py -v` → tutti PASSED

**Commit Fase 2** *(dopo aver spuntato tutto)*
- [x] `git add bingo_game/game_controller.py tests/unit/test_game_controller_loop.py`
- [x] `git commit -m "feat(controller): add ottieni_giocatore_umano() helper for TUI isolation [Phase 2/5]"`
- [x] Aggiornare questo TODO: spuntare tutti i task Fase 2

---

### 🟡 FASE 3 — TUI Core: `_loop_partita` e Dispatch Comandi

> Commit: `feat(tui): implement _loop_partita state machine and command dispatch [Phase 3/5]`

**Creazione `bingo_game/ui/tui/tui_partita.py`**
- [x] Creare il file `bingo_game/ui/tui/tui_partita.py`
- [x] Verificare che **nessun import** di classi Domain sia presente (`GiocatoreUmano`, `Partita`, `Tabellone`, `Cartella` — nessuno di questi)
- [x] Importare solo da `bingo_game.game_controller` e `bingo_game.ui.*`
- [x] Definire `_logger_tui = logging.getLogger("tombola_stark.tui")`
- [x] Definire `_renderer = TerminalRenderer()` a livello di modulo

**Implementazione `_loop_partita(partita)`**
- [x] Focus automatico sulla prima cartella (`indice=0`) all’avvio del loop
- [x] Stampa il prompt comandi iniziale (`LOOP_PROMPT_COMANDO`) prima di entrare nel while
- [x] Ciclo `while not partita_terminata(partita)` come condizione principale
- [x] Lettura input utente via `input("> ").strip()`
- [x] Split input in `cmd` (lowercase) e `args` (resto della stringa)
- [x] Gestione input vuoto: `continue` senza stampe
- [x] Chiamata a `_emetti_report_finale(partita)` dopo l’uscita dal loop

**Implementazione comando `p` — Prosegui turno**
- [x] Chiamare `esegui_turno_sicuro(partita)` e gestire `None` come errore
- [x] Vocalizzare il numero estratto con `LOOP_NUMERO_ESTRATTO`
- [x] Ristampare il prompt comandi dopo ogni estrazione
- [x] Il comando `p` è **l’unico** che chiama `esegui_turno_sicuro`

**Implementazione comando `s` — Segna numero**
- [x] Implementare `_gestisci_segna(partita, args) -> list[str]`
- [x] Parsing `args` come intero; gestire `ValueError` con feedback "Numero non valido"
- [x] Ottenere il giocatore via `ottieni_giocatore_umano(partita)`
- [x] Chiamare `giocatore.segna_numero(numero)` e passare l’esito al renderer
- [x] **Flessibilità marcatura**: qualsiasi numero estratto è segnabile (non solo l’ultimo)
- [x] Gestire il caso `giocatore is None` con messaggio di errore
- [x] Il comando `s` **NON** avanza il turno (nessun side effect su game state)

**Implementazione comando `c` — Riepilogo cartella**
- [x] Implementare `_gestisci_riepilogo_cartella(partita) -> list[str]`
- [x] Chiamare `giocatore.riepilogo_cartella_corrente()` e passare l’esito al renderer
- [x] Gestire eccezioni con log WARNING e messaggio di fallback
- [x] Il comando `c` **NON** avanza il turno

**Implementazione comando `v` — Riepilogo tabellone**
- [x] Implementare `_gestisci_riepilogo_tabellone(partita) -> list[str]`
- [x] Chiamare `ottieni_stato_sintetico(partita)` per ottenere i dati
- [x] Ritornare almeno 2 righe: estratti totali + ultimo numero
- [x] Gestire il caso "nessun numero estratto"
- [x] Il comando `v` **NON** avanza il turno

**Implementazione comando `q` — Quit con conferma**
- [x] Implementare `_gestisci_quit(partita) -> bool`
- [x] Stampare `LOOP_QUIT_CONFERMA` e leggere la risposta dell’utente
- [x] Accettare solo `"s"` come conferma esplicita (case-insensitive)
- [x] Se confermato: loggare **WARNING** su `tombola_stark.tui` con il numero di turno corrente
  - Formato log: `"[ALERT] Partita interrotta dall'utente al turno #N."`
- [x] Se confermato: ritornare `True` (il loop principale esegue `break`)
- [x] Se annullato: stampare `LOOP_QUIT_ANNULLATO` e ritornare `False`
- [x] Il log di allerta deve essere emesso **sempre** quando l’utente conferma il quit

**Implementazione comando `?` — Help**
- [x] Implementare `_gestisci_help(partita) -> list[str]`
- [x] Ritornare tutte le righe di `LOOP_HELP_COMANDI` (tupla multi-riga)
- [x] Aggiungere la cartella attualmente in focus come ultima riga (`LOOP_HELP_FOCUS`)
- [x] Ottenere il focus via `ottieni_giocatore_umano(partita).get_focus_cartella()`
- [x] Convertire l’indice 0-based in numero umano 1-based
- [x] Gestire `None` focus senza crash (focus non ancora impostato)
- [x] Il comando `?` **NON** avanza il turno

**Implementazione comando non riconosciuto**
- [x] Stampare `LOOP_COMANDO_NON_RICONOSCIUTO` per qualsiasi input non mappato
- [x] Nessun crash, nessun side effect

**Implementazione `_emetti_report_finale` e `_costruisci_report_finale`**
- [x] Implementare `_costruisci_report_finale(stato: dict) -> list[str]`
- [x] Riga 1: intestazione (`LOOP_REPORT_FINALE_INTESTAZIONE`)
- [x] Riga 2: turni giocati (`LOOP_REPORT_FINALE_TURNI`)
- [x] Riga 3: numeri estratti su 90 (`LOOP_REPORT_FINALE_ESTRATTI`)
- [x] Riga 4+: vincitore/i per tombola (`LOOP_REPORT_FINALE_VINCITORE`) o "nessun vincitore"
- [x] Ultima riga: premi totali assegnati (`LOOP_REPORT_FINALE_PREMI`)
- [x] Implementare `_emetti_report_finale(partita)` che chiama `ottieni_stato_sintetico` e stampa il report
- [x] Gestire eccezioni con log WARNING (il report non deve mai crashare il programma)

**Implementazione `_stampa(riga)`**
- [x] Implementare `_stampa(riga: str) -> None` come wrapper su `print`
- [x] Il wrapper facilita il mock nei test (nessuna stampa diretta nel codice)

**Testing Fase 3**
- [x] Creare `tests/unit/test_tui_partita.py`
- [x] Test: `_gestisci_quit` ritorna `True` quando l’utente digita `"s"` (monkeypatch `input`)
- [x] Test: `_gestisci_quit` ritorna `False` quando l’utente digita `"n"` (monkeypatch `input`)
- [x] Test: `_gestisci_quit` ritorna `False` quando l’utente digita stringa vuota
- [x] Test: `_gestisci_quit` emette log WARNING se confermato
- [x] Test: `_gestisci_segna` ritorna messaggio errore su input non numerico (`"xyz"`)
- [x] Test: `_gestisci_segna` ritorna messaggio errore su input vuoto
- [x] Test: `_gestisci_help` contiene tutte le righe di `LOOP_HELP_COMANDI`
- [x] Test: `_gestisci_help` include la cartella in focus
- [x] Test: `_costruisci_report_finale` include il nome del vincitore se presente
- [x] Test: `_costruisci_report_finale` include "nessun vincitore" se assente
- [x] Test: `_costruisci_report_finale` include sempre intestazione, turni, estratti, premi
- [x] Test: `_gestisci_riepilogo_tabellone` ritorna almeno 2 righe
- [x] Test: comando non riconosciuto non genera eccezioni
- [x] Test: focus auto viene impostato su cartella 0 all’avvio del loop
- [x] Eseguire `python -m pytest tests/unit/test_tui_partita.py -v` → tutti PASSED
- [x] Eseguire `python -m py_compile bingo_game/ui/tui/tui_partita.py` → nessun errore di sintassi
- [x] Verificare manualmente che `tui_partita.py` non contenga import di classi Domain

**Commit Fase 3** *(dopo aver spuntato tutto)*
- [x] `git add bingo_game/ui/tui/tui_partita.py tests/unit/test_tui_partita.py`
- [x] `git commit -m "feat(tui): implement _loop_partita state machine and command dispatch [Phase 3/5]"`
- [x] Aggiornare questo TODO: spuntare tutti i task Fase 3

---

### 🟡 FASE 4 — Renderer: Vocalizzazione Gerarchica e Report Finale

> Commit: `feat(renderer): verify hierarchical vocalization for game loop events [Phase 4/5]`

**Verifica Gerarchia di Vocalizzazione**
- [x] Verificare che `_render_evento_riepilogo_tabellone` ritorni esattamente **3 righe**
- [x] Verificare che `_render_evento_segnazione_numero` ritorni **1 riga** per ciascuno dei 4 esiti (`segnato`, `gia_segnato`, `non_presente`, `non_estratto`)
- [x] Verificare che `_render_evento_fine_turno` ritorni **1 riga**
- [x] Verificare che `_render_evento_riepilogo_cartella_corrente` ritorni **2 righe**
- [x] Verificare che nessuna riga di output superi **120 caratteri**
- [x] Verificare che ogni riga sia **autonoma e autoesplicativa** (leggibile senza contesto precedente)
- [x] Verificare che nessun metodo del renderer usi ASCII art o box-drawing characters nei messaggi utente

**Estensione Renderer (solo se necessario)**
- [x] Se un test di Fase 4 fallisce, aggiungere il minimo necessario al renderer
- [x] Qualsiasi aggiunta deve rispettare il pattern esistente: fallback robusto, nessuna eccezione verso l’esterno, tuple immutabili
- [x] Nessuna modifica alle firme dei metodi esistenti

**Testing Fase 4**
- [x] Creare `tests/unit/test_renderer_report_finale.py`
- [x] Test: `_render_evento_riepilogo_tabellone` → esattamente 3 righe
- [x] Test: tutte le righe di `_render_evento_riepilogo_tabellone` sono ≤ 120 caratteri
- [x] Test: `_render_evento_segnazione_numero` esito `"segnato"` → 1 riga contenente il numero
- [x] Test: `_render_evento_segnazione_numero` esito `"gia_segnato"` → 1 riga
- [x] Test: `_render_evento_segnazione_numero` esito `"non_presente"` → 1 riga
- [x] Test: `_render_evento_segnazione_numero` esito `"non_estratto"` → 1 riga
- [x] Test: `_render_evento_fine_turno` senza reclamo → 1 riga
- [x] Test: `_render_evento_riepilogo_cartella_corrente` → 2 righe
- [x] Eseguire `python -m pytest tests/unit/test_renderer_report_finale.py -v` → tutti PASSED

**Commit Fase 4** *(dopo aver spuntato tutto)*
- [x] `git add bingo_game/ui/renderers/renderer_terminal.py tests/unit/test_renderer_report_finale.py`
- [x] `git commit -m "feat(renderer): verify hierarchical vocalization for game loop events [Phase 4/5]"`
- [x] Aggiornare questo TODO: spuntare tutti i task Fase 4

---

### 🟡 FASE 5 — Chiusura: Test di Regressione, Flusso e Docs

> Commit: `docs(v0.9.0): test suite, flow tests, update API.md, ARCHITECTURE.md, README.md, CHANGELOG.md [Phase 5/5]`

**Test di Regressione (272+ test esistenti)**
- [x] Eseguire `python -m pytest tests/ -v --tb=short`
- [x] Verificare **272+ test PASSED**
- [x] Verificare **0 FAILED**
- [x] Verificare **0 ERROR**
- [x] Se ci sono fallimenti: correggere prima di procedere ai test di flusso

**Test di Validazione Input Critici**
- [x] Creare `tests/flow/test_flusso_game_loop.py`
- [x] Test flusso `q` + conferma `"s"` → log WARNING emesso con numero di turno
- [x] Test flusso `q` + annulla `"n"` → loop continua, nessun WARNING
- [x] Test flusso `q` + input non valido (es. `"x"`) → trattato come annullato
- [x] Test: comando `"zzz"` non riconosciuto → messaggio errore, nessun crash
- [x] Test: comando `"s"` senza argomento → messaggio errore "Numero non valido"
- [x] Test: comando `"s abc"` con argomento non numerico → messaggio errore

**Test di Flusso End-to-End**
- [x] Test flusso `p` avanza turno → numero estratto vocalizzato
- [x] Test flusso `s <N>` su numero estratto → segnazione confermata
- [x] Test flusso `s <N>` su numero **non** estratto → errore `non_estratto`
- [x] Test flusso `s <N>` su numero estratto **non ultimo** → segnazione confermata (flessibilità marcatura)
- [x] Test flusso partita completa → report finale con vincitore (se tombola)
- [x] Test flusso partita completa → report finale senza vincitore (numeri esauriti)

**Aggiornamento Documentazione** *(task obbligatorio)*
- [x] Aggiornare `docs/API.md`:
  - Aggiungere sezione `ottieni_giocatore_umano(partita)` con firma, Args, Returns, Raises
  - Aggiungere sezione `_loop_partita(partita)` con descrizione e comandi disponibili
- [x] Aggiornare `docs/ARCHITECTURE.md`:
  - Aggiornare Layer Diagram con `tui_partita.py` nel Presentation Layer
  - Aggiungere `codici_loop.py` nell’infrastruttura eventi
  - Documentare il vincolo: la TUI non importa classi Domain
- [x] Aggiornare `docs/README.md`:
  - Aggiungere sezione "Come si gioca" con lista comandi v0.9.0 (`p/s/c/v/q/?`)
  - Documentare la flessibilità di marcatura
- [x] Aggiornare `docs/CHANGELOG.md`:
  - Aggiungere entry `[0.9.0] - Game Loop` con data 2026-02-21
  - Elencare: Added (nuovi file), Modified (file aggiornati), Notes (decisioni di design)

**Commit Fase 5** *(dopo aver spuntato tutto)*
- [x] `git add tests/flow/test_flusso_game_loop.py docs/API.md docs/ARCHITECTURE.md docs/README.md docs/CHANGELOG.md`
- [x] `git commit -m "docs(v0.9.0): test suite, flow tests, update API.md, ARCHITECTURE.md, README.md, CHANGELOG.md [Phase 5/5]"`
- [x] Aggiornare questo TODO: spuntare tutti i task Fase 5

---

## ✅ Criteri di Completamento

L’implementazione è considerata completa quando:

- [x] Tutte le 5 fasi sono completate e spuntate
- [x] **272+ test** di regressione: tutti PASSED
- [x] **31+ nuovi unit test**: tutti PASSED
- [x] **6 test di flusso**: tutti PASSED (inclusi validazione input e quit)
- [x] Nessun import di classi Domain in `tui_partita.py`
- [x] Comandi `p/s/c/v/q/?` tutti funzionanti e testati
- [x] Output screen reader-ready (righe autonome, ≤ 120 caratteri)
- [x] Quit logga WARNING con numero turno
- [x] Documentazione (`API.md`, `ARCHITECTURE.md`, `README.md`, `CHANGELOG.md`) aggiornata
- [x] Branch `feat/v0.9.0-game-loop` pronto per review

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

- [x] Aggiornare `docs/README.md` con sezione comandi v0.9.0
- [x] Aggiornare `docs/CHANGELOG.md` con entry `[0.9.0] - Game Loop`
- [x] Aggiornare `docs/API.md` con `ottieni_giocatore_umano()` e `_loop_partita()`
- [x] Aggiornare `docs/ARCHITECTURE.md` con layer diagram aggiornato
- [x] Versione target: `v0.9.0` — incremento **MINOR** (nuova feature retrocompatibile)
- [x] Commit finale con messaggio convenzionale `[Phase 5/5]`
- [x] Push su `feat/v0.9.0-game-loop`
- [x] Aprire Pull Request verso `main` con descrizione delle 5 fasi

---

## 📌 Note Operative

> Snello, consultabile in 30 secondi, zero fronzoli. Il piano completo in `PLAN_GAME_LOOP.md` resta la fonte di verità tecnica. Questo è il cruscotto operativo.

- **Separazione layer**: la TUI accede al dominio **esclusivamente** tramite `game_controller`. Qualsiasi tentativo di importare `GiocatoreUmano`, `Partita`, `Tabellone` in `tui_partita.py` è un bug architetturale.
- **Azioni informative**: `s`, `c`, `v`, `?` non avanzano mai il turno. Solo `p` chiama `esegui_turno_sicuro`.
- **Flessibilità marcatura**: l’utente può segnare qualsiasi numero estratto, non solo l’ultimo. È una decisione di design v0.9.0, non un bug.
- **Navigazione cartelle**: rinviata a v0.10.0. Il focus è sempre sulla prima cartella (indice 0).
- **Quit sempre con conferma**: non esiste un quit immediato. Il WARNING nel log è obbligatorio.
- **Vocalizzazione gerarchica**: ogni riga output deve essere autonoma. Non usare abbreviazioni o simboli non parlabili.

---

## 📊 Progress Tracking

| Fase | Status | Commit SHA | Data |
|------|--------|------------|------|
| Fase 1 — Infrastruttura | ✅ COMPLETATO | 0394594 | 2026-02-21 |
| Fase 2 — Controller | ✅ COMPLETATO | 24c1e81 | 2026-02-21 |
| Fase 3 — TUI Core | ✅ COMPLETATO | 24c1e81 | 2026-02-21 |
| Fase 4 — Renderer | ✅ COMPLETATO | aef1d89 | 2026-02-21 |
| Fase 5 — Chiusura | ✅ COMPLETATO | aef1d89 | 2026-02-21 |

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.  
Il documento lungo resta come fonte di verità tecnica. Questo è il cruscotto operativo.

---

**TODO Version**: v1.0  
**Data Creazione**: 2026-02-21  
**Autore**: AI Assistant + Nemex81  
**Piano di riferimento**: `documentations/3 - planning/PLAN_GAME_LOOP.md`
