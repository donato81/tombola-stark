# 📋 TODO – Game Loop (v0.9.0)

**Branch**: `feat/v0.9.0-game-loop`  
**Tipo**: FEATURE  
**Priorità**: HIGH  
**Stato**: READY

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
- [ ] Creare il file `bingo_game/events/codici_loop.py`
- [ ] Aggiungere costante `LOOP_TURNO_AVANZATO`
- [ ] Aggiungere costante `LOOP_NUMERO_ESTRATTO`
- [ ] Aggiungere costante `LOOP_SEGNAZIONE_OK`
- [ ] Aggiungere costante `LOOP_REPORT_FINALE`
- [ ] Aggiungere costante `LOOP_QUIT_CONFERMATO`
- [ ] Aggiungere costante `LOOP_QUIT_ANNULLATO`
- [ ] Aggiungere costante `LOOP_HELP`
- [ ] Aggiungere costante `LOOP_FOCUS_AUTO`
- [ ] Verificare che tutte le costanti siano stringhe non vuote e non duplicate

**Aggiornamento `bingo_game/ui/locales/it.py`**
- [ ] Aggiungere chiave `LOOP_NUMERO_ESTRATTO` con placeholder `{numero}`
- [ ] Aggiungere chiave `LOOP_PROMPT_COMANDO` (testo prompt interattivo)
- [ ] Aggiungere chiave `LOOP_HELP_COMANDI` (tupla multi-riga con tutti i comandi)
- [ ] Aggiungere chiave `LOOP_HELP_FOCUS` con placeholder `{numero_cartella}`
- [ ] Aggiungere chiave `LOOP_QUIT_CONFERMA`
- [ ] Aggiungere chiave `LOOP_QUIT_ANNULLATO`
- [ ] Aggiungere chiave `LOOP_REPORT_FINALE_INTESTAZIONE`
- [ ] Aggiungere chiave `LOOP_REPORT_FINALE_TURNI` con placeholder `{turni}`
- [ ] Aggiungere chiave `LOOP_REPORT_FINALE_ESTRATTI` con placeholder `{estratti}`
- [ ] Aggiungere chiave `LOOP_REPORT_FINALE_VINCITORE` con placeholder `{nome}`
- [ ] Aggiungere chiave `LOOP_REPORT_FINALE_NESSUN_VINCITORE`
- [ ] Aggiungere chiave `LOOP_REPORT_FINALE_PREMI` con placeholder `{premi}`
- [ ] Aggiungere chiave `LOOP_COMANDO_NON_RICONOSCIUTO`
- [ ] Verificare che nessuna chiave esistente in `it.py` sia stata rimossa o modificata

**Testing Fase 1**
- [ ] Creare `tests/unit/test_codici_loop.py`
- [ ] Test: tutte le costanti `codici_loop` sono stringhe non vuote
- [ ] Test: nessuna costante duplicata tra quelle di `codici_loop`
- [ ] Test: tutte le 13 chiavi `LOOP_*` presenti in `MESSAGGI_OUTPUT_UI_UMANI`
- [ ] Test: template con placeholder sono formattabili senza eccezioni
- [ ] Test: import di `codici_loop` non produce side effect
- [ ] Eseguire `python -m pytest tests/unit/test_codici_loop.py -v` → tutti PASSED

**Commit Fase 1** *(dopo aver spuntato tutto)*
- [ ] `git add bingo_game/events/codici_loop.py bingo_game/ui/locales/it.py tests/unit/test_codici_loop.py`
- [ ] `git commit -m "feat(infra): add codici_loop.py and LOOP_* keys in it.py [Phase 1/5]"`
- [ ] Aggiornare questo TODO: spuntare tutti i task Fase 1

---

### 🟡 FASE 2 — Controller: `ottieni_giocatore_umano()`

> Commit: `feat(controller): add ottieni_giocatore_umano() helper for TUI isolation [Phase 2/5]`

**Modifica `bingo_game/game_controller.py`**
- [ ] Aggiungere la funzione `ottieni_giocatore_umano(partita)` dopo `partita_terminata()`
- [ ] Funzione ritorna il primo `GiocatoreUmano` trovato tramite `partita.get_giocatori()`
- [ ] Funzione ritorna `None` se nessun `GiocatoreUmano` è presente
- [ ] Funzione solleva `ValueError` se `partita` non è un'istanza di `Partita`
- [ ] Log `DEBUG` quando il giocatore umano viene trovato (`_log_safe` + `_logger_game`)
- [ ] Log `WARNING` quando nessun giocatore umano è trovato (`_log_safe` + `_logger_game`)
- [ ] Docstring completa: Args, Returns, Raises, Version (`v0.9.0`)
- [ ] Nessuna funzione esistente in `game_controller.py` modificata

**Testing Fase 2**
- [ ] Creare `tests/unit/test_game_controller_loop.py`
- [ ] Test: `ottieni_giocatore_umano` ritorna il primo giocatore umano
- [ ] Test: ritorna `None` se la partita ha solo bot
- [ ] Test: solleva `ValueError` se il parametro non è `Partita`
- [ ] Test: il log WARNING viene emesso quando nessun umano è trovato
- [ ] Test: la funzione non modifica lo stato della partita (nessun side effect)
- [ ] Test: `crea_partita_standard` non è regredita (smoke test)
- [ ] Test: `esegui_turno_sicuro` non è regredita (smoke test)
- [ ] Test: `ottieni_stato_sintetico` non è regredita (smoke test)
- [ ] Test: `avvia_partita_sicura` non è regredita (smoke test)
- [ ] Eseguire `python -m pytest tests/unit/test_game_controller_loop.py -v` → tutti PASSED

**Commit Fase 2** *(dopo aver spuntato tutto)*
- [ ] `git add bingo_game/game_controller.py tests/unit/test_game_controller_loop.py`
- [ ] `git commit -m "feat(controller): add ottieni_giocatore_umano() helper for TUI isolation [Phase 2/5]"`
- [ ] Aggiornare questo TODO: spuntare tutti i task Fase 2

---

### 🟡 FASE 3 — TUI Core: `_loop_partita` e Dispatch Comandi

> Commit: `feat(tui): implement _loop_partita state machine and command dispatch [Phase 3/5]`

**Creazione `bingo_game/ui/tui/tui_partita.py`**
- [ ] Creare il file `bingo_game/ui/tui/tui_partita.py`
- [ ] Verificare che **nessun import** di classi Domain sia presente (`GiocatoreUmano`, `Partita`, `Tabellone`, `Cartella` — nessuno di questi)
- [ ] Importare solo da `bingo_game.game_controller` e `bingo_game.ui.*`
- [ ] Definire `_logger_tui = logging.getLogger("tombola_stark.tui")`
- [ ] Definire `_renderer = TerminalRenderer()` a livello di modulo

**Implementazione `_loop_partita(partita)`**
- [ ] Focus automatico sulla prima cartella (`indice=0`) all’avvio del loop
- [ ] Stampa il prompt comandi iniziale (`LOOP_PROMPT_COMANDO`) prima di entrare nel while
- [ ] Ciclo `while not partita_terminata(partita)` come condizione principale
- [ ] Lettura input utente via `input("> ").strip()`
- [ ] Split input in `cmd` (lowercase) e `args` (resto della stringa)
- [ ] Gestione input vuoto: `continue` senza stampe
- [ ] Chiamata a `_emetti_report_finale(partita)` dopo l’uscita dal loop

**Implementazione comando `p` — Prosegui turno**
- [ ] Chiamare `esegui_turno_sicuro(partita)` e gestire `None` come errore
- [ ] Vocalizzare il numero estratto con `LOOP_NUMERO_ESTRATTO`
- [ ] Ristampare il prompt comandi dopo ogni estrazione
- [ ] Il comando `p` è **l’unico** che chiama `esegui_turno_sicuro`

**Implementazione comando `s` — Segna numero**
- [ ] Implementare `_gestisci_segna(partita, args) -> list[str]`
- [ ] Parsing `args` come intero; gestire `ValueError` con feedback "Numero non valido"
- [ ] Ottenere il giocatore via `ottieni_giocatore_umano(partita)`
- [ ] Chiamare `giocatore.segna_numero(numero)` e passare l’esito al renderer
- [ ] **Flessibilità marcatura**: qualsiasi numero estratto è segnabile (non solo l’ultimo)
- [ ] Gestire il caso `giocatore is None` con messaggio di errore
- [ ] Il comando `s` **NON** avanza il turno (nessun side effect su game state)

**Implementazione comando `c` — Riepilogo cartella**
- [ ] Implementare `_gestisci_riepilogo_cartella(partita) -> list[str]`
- [ ] Chiamare `giocatore.riepilogo_cartella_corrente()` e passare l’esito al renderer
- [ ] Gestire eccezioni con log WARNING e messaggio di fallback
- [ ] Il comando `c` **NON** avanza il turno

**Implementazione comando `v` — Riepilogo tabellone**
- [ ] Implementare `_gestisci_riepilogo_tabellone(partita) -> list[str]`
- [ ] Chiamare `ottieni_stato_sintetico(partita)` per ottenere i dati
- [ ] Ritornare almeno 2 righe: estratti totali + ultimo numero
- [ ] Gestire il caso "nessun numero estratto"
- [ ] Il comando `v` **NON** avanza il turno

**Implementazione comando `q` — Quit con conferma**
- [ ] Implementare `_gestisci_quit(partita) -> bool`
- [ ] Stampare `LOOP_QUIT_CONFERMA` e leggere la risposta dell’utente
- [ ] Accettare solo `"s"` come conferma esplicita (case-insensitive)
- [ ] Se confermato: loggare **WARNING** su `tombola_stark.tui` con il numero di turno corrente
  - Formato log: `"[ALERT] Partita interrotta dall'utente al turno #N."`
- [ ] Se confermato: ritornare `True` (il loop principale esegue `break`)
- [ ] Se annullato: stampare `LOOP_QUIT_ANNULLATO` e ritornare `False`
- [ ] Il log di allerta deve essere emesso **sempre** quando l’utente conferma il quit

**Implementazione comando `?` — Help**
- [ ] Implementare `_gestisci_help(partita) -> list[str]`
- [ ] Ritornare tutte le righe di `LOOP_HELP_COMANDI` (tupla multi-riga)
- [ ] Aggiungere la cartella attualmente in focus come ultima riga (`LOOP_HELP_FOCUS`)
- [ ] Ottenere il focus via `ottieni_giocatore_umano(partita).get_focus_cartella()`
- [ ] Convertire l’indice 0-based in numero umano 1-based
- [ ] Gestire `None` focus senza crash (focus non ancora impostato)
- [ ] Il comando `?` **NON** avanza il turno

**Implementazione comando non riconosciuto**
- [ ] Stampare `LOOP_COMANDO_NON_RICONOSCIUTO` per qualsiasi input non mappato
- [ ] Nessun crash, nessun side effect

**Implementazione `_emetti_report_finale` e `_costruisci_report_finale`**
- [ ] Implementare `_costruisci_report_finale(stato: dict) -> list[str]`
- [ ] Riga 1: intestazione (`LOOP_REPORT_FINALE_INTESTAZIONE`)
- [ ] Riga 2: turni giocati (`LOOP_REPORT_FINALE_TURNI`)
- [ ] Riga 3: numeri estratti su 90 (`LOOP_REPORT_FINALE_ESTRATTI`)
- [ ] Riga 4+: vincitore/i per tombola (`LOOP_REPORT_FINALE_VINCITORE`) o "nessun vincitore"
- [ ] Ultima riga: premi totali assegnati (`LOOP_REPORT_FINALE_PREMI`)
- [ ] Implementare `_emetti_report_finale(partita)` che chiama `ottieni_stato_sintetico` e stampa il report
- [ ] Gestire eccezioni con log WARNING (il report non deve mai crashare il programma)

**Implementazione `_stampa(riga)`**
- [ ] Implementare `_stampa(riga: str) -> None` come wrapper su `print`
- [ ] Il wrapper facilita il mock nei test (nessuna stampa diretta nel codice)

**Testing Fase 3**
- [ ] Creare `tests/unit/test_tui_partita.py`
- [ ] Test: `_gestisci_quit` ritorna `True` quando l’utente digita `"s"` (monkeypatch `input`)
- [ ] Test: `_gestisci_quit` ritorna `False` quando l’utente digita `"n"` (monkeypatch `input`)
- [ ] Test: `_gestisci_quit` ritorna `False` quando l’utente digita stringa vuota
- [ ] Test: `_gestisci_quit` emette log WARNING se confermato
- [ ] Test: `_gestisci_segna` ritorna messaggio errore su input non numerico (`"xyz"`)
- [ ] Test: `_gestisci_segna` ritorna messaggio errore su input vuoto
- [ ] Test: `_gestisci_help` contiene tutte le righe di `LOOP_HELP_COMANDI`
- [ ] Test: `_gestisci_help` include la cartella in focus
- [ ] Test: `_costruisci_report_finale` include il nome del vincitore se presente
- [ ] Test: `_costruisci_report_finale` include "nessun vincitore" se assente
- [ ] Test: `_costruisci_report_finale` include sempre intestazione, turni, estratti, premi
- [ ] Test: `_gestisci_riepilogo_tabellone` ritorna almeno 2 righe
- [ ] Test: comando non riconosciuto non genera eccezioni
- [ ] Test: focus auto viene impostato su cartella 0 all’avvio del loop
- [ ] Eseguire `python -m pytest tests/unit/test_tui_partita.py -v` → tutti PASSED
- [ ] Eseguire `python -m py_compile bingo_game/ui/tui/tui_partita.py` → nessun errore di sintassi
- [ ] Verificare manualmente che `tui_partita.py` non contenga import di classi Domain

**Commit Fase 3** *(dopo aver spuntato tutto)*
- [ ] `git add bingo_game/ui/tui/tui_partita.py tests/unit/test_tui_partita.py`
- [ ] `git commit -m "feat(tui): implement _loop_partita state machine and command dispatch [Phase 3/5]"`
- [ ] Aggiornare questo TODO: spuntare tutti i task Fase 3

---

### 🟡 FASE 4 — Renderer: Vocalizzazione Gerarchica e Report Finale

> Commit: `feat(renderer): verify hierarchical vocalization for game loop events [Phase 4/5]`

**Verifica Gerarchia di Vocalizzazione**
- [ ] Verificare che `_render_evento_riepilogo_tabellone` ritorni esattamente **3 righe**
- [ ] Verificare che `_render_evento_segnazione_numero` ritorni **1 riga** per ciascuno dei 4 esiti (`segnato`, `gia_segnato`, `non_presente`, `non_estratto`)
- [ ] Verificare che `_render_evento_fine_turno` ritorni **1 riga**
- [ ] Verificare che `_render_evento_riepilogo_cartella_corrente` ritorni **2 righe**
- [ ] Verificare che nessuna riga di output superi **120 caratteri**
- [ ] Verificare che ogni riga sia **autonoma e autoesplicativa** (leggibile senza contesto precedente)
- [ ] Verificare che nessun metodo del renderer usi ASCII art o box-drawing characters nei messaggi utente

**Estensione Renderer (solo se necessario)**
- [ ] Se un test di Fase 4 fallisce, aggiungere il minimo necessario al renderer
- [ ] Qualsiasi aggiunta deve rispettare il pattern esistente: fallback robusto, nessuna eccezione verso l’esterno, tuple immutabili
- [ ] Nessuna modifica alle firme dei metodi esistenti

**Testing Fase 4**
- [ ] Creare `tests/unit/test_renderer_report_finale.py`
- [ ] Test: `_render_evento_riepilogo_tabellone` → esattamente 3 righe
- [ ] Test: tutte le righe di `_render_evento_riepilogo_tabellone` sono ≤ 120 caratteri
- [ ] Test: `_render_evento_segnazione_numero` esito `"segnato"` → 1 riga contenente il numero
- [ ] Test: `_render_evento_segnazione_numero` esito `"gia_segnato"` → 1 riga
- [ ] Test: `_render_evento_segnazione_numero` esito `"non_presente"` → 1 riga
- [ ] Test: `_render_evento_segnazione_numero` esito `"non_estratto"` → 1 riga
- [ ] Test: `_render_evento_fine_turno` senza reclamo → 1 riga
- [ ] Test: `_render_evento_riepilogo_cartella_corrente` → 2 righe
- [ ] Eseguire `python -m pytest tests/unit/test_renderer_report_finale.py -v` → tutti PASSED

**Commit Fase 4** *(dopo aver spuntato tutto)*
- [ ] `git add bingo_game/ui/renderers/renderer_terminal.py tests/unit/test_renderer_report_finale.py`
- [ ] `git commit -m "feat(renderer): verify hierarchical vocalization for game loop events [Phase 4/5]"`
- [ ] Aggiornare questo TODO: spuntare tutti i task Fase 4

---

### 🟡 FASE 5 — Chiusura: Test di Regressione, Flusso e Docs

> Commit: `docs(v0.9.0): test suite, flow tests, update API.md, ARCHITECTURE.md, README.md, CHANGELOG.md [Phase 5/5]`

**Test di Regressione (272+ test esistenti)**
- [ ] Eseguire `python -m pytest tests/ -v --tb=short`
- [ ] Verificare **272+ test PASSED**
- [ ] Verificare **0 FAILED**
- [ ] Verificare **0 ERROR**
- [ ] Se ci sono fallimenti: correggere prima di procedere ai test di flusso

**Test di Validazione Input Critici**
- [ ] Creare `tests/flow/test_flusso_game_loop.py`
- [ ] Test flusso `q` + conferma `"s"` → log WARNING emesso con numero di turno
- [ ] Test flusso `q` + annulla `"n"` → loop continua, nessun WARNING
- [ ] Test flusso `q` + input non valido (es. `"x"`) → trattato come annullato
- [ ] Test: comando `"zzz"` non riconosciuto → messaggio errore, nessun crash
- [ ] Test: comando `"s"` senza argomento → messaggio errore "Numero non valido"
- [ ] Test: comando `"s abc"` con argomento non numerico → messaggio errore

**Test di Flusso End-to-End**
- [ ] Test flusso `p` avanza turno → numero estratto vocalizzato
- [ ] Test flusso `s <N>` su numero estratto → segnazione confermata
- [ ] Test flusso `s <N>` su numero **non** estratto → errore `non_estratto`
- [ ] Test flusso `s <N>` su numero estratto **non ultimo** → segnazione confermata (flessibilità marcatura)
- [ ] Test flusso partita completa → report finale con vincitore (se tombola)
- [ ] Test flusso partita completa → report finale senza vincitore (numeri esauriti)

**Aggiornamento Documentazione** *(task obbligatorio)*
- [ ] Aggiornare `docs/API.md`:
  - Aggiungere sezione `ottieni_giocatore_umano(partita)` con firma, Args, Returns, Raises
  - Aggiungere sezione `_loop_partita(partita)` con descrizione e comandi disponibili
- [ ] Aggiornare `docs/ARCHITECTURE.md`:
  - Aggiornare Layer Diagram con `tui_partita.py` nel Presentation Layer
  - Aggiungere `codici_loop.py` nell’infrastruttura eventi
  - Documentare il vincolo: la TUI non importa classi Domain
- [ ] Aggiornare `docs/README.md`:
  - Aggiungere sezione "Come si gioca" con lista comandi v0.9.0 (`p/s/c/v/q/?`)
  - Documentare la flessibilità di marcatura
- [ ] Aggiornare `docs/CHANGELOG.md`:
  - Aggiungere entry `[0.9.0] - Game Loop` con data 2026-02-21
  - Elencare: Added (nuovi file), Modified (file aggiornati), Notes (decisioni di design)

**Commit Fase 5** *(dopo aver spuntato tutto)*
- [ ] `git add tests/flow/test_flusso_game_loop.py docs/API.md docs/ARCHITECTURE.md docs/README.md docs/CHANGELOG.md`
- [ ] `git commit -m "docs(v0.9.0): test suite, flow tests, update API.md, ARCHITECTURE.md, README.md, CHANGELOG.md [Phase 5/5]"`
- [ ] Aggiornare questo TODO: spuntare tutti i task Fase 5

---

## ✅ Criteri di Completamento

L’implementazione è considerata completa quando:

- [ ] Tutte le 5 fasi sono completate e spuntate
- [ ] **272+ test** di regressione: tutti PASSED
- [ ] **31+ nuovi unit test**: tutti PASSED
- [ ] **6 test di flusso**: tutti PASSED (inclusi validazione input e quit)
- [ ] Nessun import di classi Domain in `tui_partita.py`
- [ ] Comandi `p/s/c/v/q/?` tutti funzionanti e testati
- [ ] Output screen reader-ready (righe autonome, ≤ 120 caratteri)
- [ ] Quit logga WARNING con numero turno
- [ ] Documentazione (`API.md`, `ARCHITECTURE.md`, `README.md`, `CHANGELOG.md`) aggiornata
- [ ] Branch `feat/v0.9.0-game-loop` pronto per review

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] Aggiornare `docs/README.md` con sezione comandi v0.9.0
- [ ] Aggiornare `docs/CHANGELOG.md` con entry `[0.9.0] - Game Loop`
- [ ] Aggiornare `docs/API.md` con `ottieni_giocatore_umano()` e `_loop_partita()`
- [ ] Aggiornare `docs/ARCHITECTURE.md` con layer diagram aggiornato
- [ ] Versione target: `v0.9.0` — incremento **MINOR** (nuova feature retrocompatibile)
- [ ] Commit finale con messaggio convenzionale `[Phase 5/5]`
- [ ] Push su `feat/v0.9.0-game-loop`
- [ ] Aprire Pull Request verso `main` con descrizione delle 5 fasi

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
| Fase 1 — Infrastruttura | ⏳ PENDING | — | — |
| Fase 2 — Controller | ⏳ PENDING | — | — |
| Fase 3 — TUI Core | ⏳ PENDING | — | — |
| Fase 4 — Renderer | ⏳ PENDING | — | — |
| Fase 5 — Chiusura | ⏳ PENDING | — | — |

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.  
Il documento lungo resta come fonte di verità tecnica. Questo è il cruscotto operativo.

---

**TODO Version**: v1.0  
**Data Creazione**: 2026-02-21  
**Autore**: AI Assistant + Nemex81  
**Piano di riferimento**: `documentations/3 - planning/PLAN_GAME_LOOP.md`
