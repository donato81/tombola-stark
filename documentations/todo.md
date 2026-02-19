# 📋 TODO – Bot Attivo: GiocatoreAutomatico dichiara i premi (v0.6.0)

Branch: `feature/bot-attivo`
Tipo: `FEATURE`
Priorità: `HIGH`
Stato: `READY`

---

## 📖 Riferimento Documentazione

Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:

| Documento | Scopo |
|---|---|
| `documentations/PLAN_BOT_ATTIVO.md` | **Piano completo** — architettura, algoritmi, edge case, ordine di implementazione |
| `documentations/API.md` | Contratti API pubblici di tutte le classi coinvolte |
| `documentations/ARCHITECTURE.md` | Regole di dipendenza, flusso del turno, pattern architetturali |

Questo file TODO è solo un sommario operativo da consultare e aggiornare durante ogni fase.
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici.

---

## 🤖 Istruzioni per Copilot Agent

Implementare le modifiche in modo **incrementale** su più commit atomici e logici.

**Workflow per ogni fase:**

1. **Leggi questo TODO** → Identifica la prossima fase da implementare
2. **Consulta `PLAN_BOT_ATTIVO.md`** → Rivedi algoritmo, edge case e vincoli della fase
3. **Implementa modifiche** → Codifica solo la fase corrente (scope limitato)
4. **Commit atomico** → Messaggio conventional, scope chiaro, riferimento fase
5. **Aggiorna questo TODO** → Spunta le checkbox completate per la fase
6. **Acquisisci stato sommario** → Rivedi stato globale prima di proseguire
7. **RIPETI** → Passa alla fase successiva (torna al punto 1)

⚠️ **REGOLE FONDAMENTALI:**

- ✅ **Un commit per fase logica** (no mega-commit con tutto)
- ✅ **Dopo ogni commit**: aggiorna questo TODO spuntando le checkbox
- ✅ **Prima di ogni fase**: rileggi la sezione pertinente in `PLAN_BOT_ATTIVO.md`
- ✅ **Approccio sequenziale**: fase → commit → aggiorna TODO → fase successiva
- ✅ **Commit message format**: `type(scope): description [Phase N/7]`
- ❌ **NO commit multipli senza aggiornare TODO** (perde tracciabilità)
- ❌ **NO implementazione completa in un colpo** (viola incrementalità)
- ❌ **NO logica di gioco nel Controller** (viola ARCHITECTURE.md)
- ❌ **NO import di librerie UI/TTS nel Dominio** (viola ARCHITECTURE.md)

**Esempio workflow reale:**
```
Fase 1: GiocatoreBase.is_automatico()
→ Implementa + Commit `feat(players): add is_automatico() [Phase 1/7]` + Aggiorna TODO ✅

Fase 2: GiocatoreAutomatico._valuta_potenziale_reclamo()
→ Rileggi PLAN_BOT_ATTIVO.md sezione FASE 1 Task 1.1
→ Implementa + Commit `feat(players): add _valuta_potenziale_reclamo() [Phase 2/7]` + Aggiorna TODO ✅

... e così via fino alla Fase 7
```

---

## 🎯 Obiettivo Implementazione

- Estendere `GiocatoreAutomatico` affinché valuti autonomamente, dopo ogni estrazione,
  se ha conseguito un premio e lo dichiari tramite un `ReclamoVittoria`.
- Integrare la fase di reclamo bot nel ciclo `Partita.esegui_turno()`,
  mantenendo `verifica_premi()` come unico arbitro dei premi reali.
- Esporre gli esiti dei reclami bot nel dizionario risultato del turno (nuova chiave
  backward-compatible `reclami_bot`) e loggarli nel controller.
- **Zero breaking change** su API esistente e architettura a livelli.

---

## 📂 File Coinvolti

- `bingo_game/players/giocatore_base.py` → **MODIFY** (aggiunta `is_automatico()`)
- `bingo_game/players/giocatore_automatico.py` → **MODIFY** (override `is_automatico()` + `_valuta_potenziale_reclamo()`)
- `bingo_game/partita.py` → **MODIFY** (estensione `esegui_turno()`)
- `bingo_game/game_controller.py` → **MODIFY** (logging `reclami_bot` in `esegui_turno_sicuro()`)
- `tests/unit/test_giocatore_automatico_bot_attivo.py` → **CREATE**
- `tests/integration/test_partita_bot_attivo.py` → **CREATE**
- `documentations/API.md` → **UPDATE**
- `documentations/ARCHITECTURE.md` → **UPDATE**
- `README.md` → **UPDATE**

---

## 🛠 Checklist Implementazione

### Fase 1 — Preparazione base (GiocatoreBase + GiocatoreAutomatico)

> 📖 Consulta: `PLAN_BOT_ATTIVO.md` → sezione "Decisione aperta" + "FASE 1"

- [x] Aggiungere `is_automatico() -> bool` in `GiocatoreBase` (default: `return False`)
- [x] Override `is_automatico()` in `GiocatoreAutomatico` (return `True`)
- [x] Commit: `feat(players): add is_automatico() helper [Phase 1/7]`
- [x] Aggiornare questo TODO (spuntare le righe qui sopra)

### Fase 2 — Logica di reclamo del Bot

> 📖 Consulta: `PLAN_BOT_ATTIVO.md` → sezione "FASE 1 — Task 1.1"

- [x] Aggiungere import di `ReclamoVittoria` in `giocatore_automatico.py`
- [x] Implementare `_valuta_potenziale_reclamo(premi_gia_assegnati: set[str]) -> Optional[ReclamoVittoria]`
  - [x] Gerarchia premi decrescente: `tombola > cinquina > quaterna > terno > ambo`
  - [x] Logica tombola: controlla `verifica_cartella_completa()` + chiave `"cartella_{idx}_tombola"`
  - [x] Logica riga: controlla `verifica_<tipo>_riga(riga)` + chiave `"cartella_{idx}_riga_{r}_{tipo}"`
  - [x] Scelta del `best_claim` per rango più alto tra tutte le cartelle
  - [x] Usa costruttore diretto `ReclamoVittoria()` (factory methods non disponibili per bug esistente)
  - [x] Ritorna `None` se nessun premio reclamabile
- [x] Commit: `feat(players): add _valuta_potenziale_reclamo() to GiocatoreAutomatico [Phase 2/7]`
- [x] Aggiornare questo TODO

### Fase 3 — Test unitari GiocatoreAutomatico

> 📖 Consulta: `PLAN_BOT_ATTIVO.md` → sezione "Test da implementare — Test unitari"

- [x] Creare `tests/unit/test_giocatore_automatico_bot_attivo.py`
- [x] `test_bot_reclama_ambo_disponibile`
- [x] `test_bot_non_reclama_premio_gia_assegnato`
- [x] `test_bot_sceglie_premio_piu_alto`
- [x] `test_bot_reclama_tombola`
- [x] `test_bot_nessun_premio_disponibile`
- [x] `test_bot_sceglie_tra_piu_cartelle`
- [x] Tutti i test passano ✅
- [x] Commit: `test(players): add unit tests for bot _valuta_potenziale_reclamo [Phase 3/7]`
- [x] Aggiornare questo TODO

### Fase 4 — Estensione Partita.esegui_turno()

> 📖 Consulta: `PLAN_BOT_ATTIVO.md` → sezione "FASE 2 — Task 2.1, 2.2, 2.3"

- [x] Inserire ciclo reclami bot **dopo** `estrai_prossimo_numero()` e **prima** di `verifica_premi()`
  - [x] Iterare su `self.giocatori` filtrando con `giocatore.is_automatico()`
  - [x] Chiamare `bot._valuta_potenziale_reclamo(self.premi_gia_assegnati)` (passare snapshot pre-turno)
  - [x] Se reclamo presente: `bot.reclamo_turno = reclamo`
- [x] Eseguire `verifica_premi()` invariato (rimane l'unico arbitro)
- [x] Inserire ciclo confronto reclami vs `premi_nuovi` **dopo** `verifica_premi()`
  - [x] Matching per `(cartella, tipo, riga)`
  - [x] Costruire lista `reclami_bot` con struttura `{nome, id, reclamo, successo}`
- [x] Inserire reset `bot.reset_reclamo_turno()` per tutti i bot
- [x] Aggiungere chiave `"reclami_bot"` al dizionario `risultato_turno`
- [x] Commit: `feat(partita): integrate bot reclamo phase in esegui_turno [Phase 4/7]`
- [x] Aggiornare questo TODO

### Fase 5 — Test di integrazione Partita

> 📖 Consulta: `PLAN_BOT_ATTIVO.md` → sezione "Test da implementare — Test di integrazione"

- [x] Creare `tests/integration/test_partita_bot_attivo.py`
- [x] `test_partita_reclami_bot_nel_risultato`
- [x] `test_reclamo_bot_rigettato_premio_gia_preso`
- [x] `test_bot_tombola_termina_partita`
- [x] `test_reclami_bot_vuoto_se_nessun_premio`
- [x] `test_reset_reclamo_dopo_turno`
- [x] Tutti i test esistenti ancora passano (no regressioni) ✅
- [x] Commit: `test(partita): add integration tests for bot attivo [Phase 5/7]`
- [x] Aggiornare questo TODO

### Fase 6 — Logging nel Controller

> 📖 Consulta: `PLAN_BOT_ATTIVO.md` → sezione "FASE 3 — Task 3.1"

- [x] In `game_controller.py`, in `esegui_turno_sicuro()`, leggere `risultato.get("reclami_bot", [])`
- [x] Per reclamo con `successo=True`: log su `tombola_stark.prizes` con `_log_safe()`
- [x] Per reclamo con `successo=False`: log su `tombola_stark.game` con `_log_safe()`
- [x] Verificare che il logging non interrompa mai il flusso (wrap in `try/except Exception: pass`)
- [x] Commit: `feat(controller): log bot reclami in esegui_turno_sicuro [Phase 6/7]`
- [x] Aggiornare questo TODO

### Fase 7 — Documentazione e aggiornamenti finali

> 📖 Consulta: `PLAN_BOT_ATTIVO.md` → sezione "Aggiornamenti documentazione"

- [x] `API.md`: aggiungere sezione `GiocatoreAutomatico` con nuova logica Bot Attivo
- [x] `API.md`: aggiornare contratto `Partita.esegui_turno()` con chiave `reclami_bot`
- [x] `ARCHITECTURE.md`: aggiornare diagramma "Flusso Tipico: Esecuzione di un Turno"
- [x] `ARCHITECTURE.md`: incrementare versione documento a `v0.6.0`
- [x] `README.md`: aggiornare descrizione funzionale (bot reclamano premi automaticamente)
- [x] Commit: `docs: update API.md, ARCHITECTURE.md, README.md for bot attivo [Phase 7/7]`
- [x] Aggiornare questo TODO

---

## ✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [x] Tutte le checklist sopra sono spuntate
- [x] Tutti i test passano (unit + integration)
- [x] Nessuna regressione funzionale sui test esistenti
- [x] Nessuna violazione delle regole architetturali (ARCHITECTURE.md)
- [x] Versione incrementata a `v0.6.0` (MINOR: nuova feature retrocompatibile)

---

## 📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] Aggiornare `README.md` con la nuova funzionalità Bot Attivo
- [ ] Aggiornare `CHANGELOG.md` con entry `v0.6.0`
- [ ] Incrementare versione a `v0.6.0` (MINOR — nuova feature retrocompatibile, zero breaking change)
- [ ] Commit finale con messaggio convenzionale
- [ ] Push su branch `feature/bot-attivo`

---

## 🔧 Correzioni Post-Review PR#4 (Issue #5)

Branch: `copilot/fix-giocatorebase-attributes`
Riferimento: Issue donato81/tombola-stark#5

### Fix 1 — CRITICO: metodi GiocatoreBase
- [x] Verificato `self.reclamo_turno = None` nel `__init__` (già presente)
- [x] Verificato metodo `is_automatico()` (già presente)
- [x] Verificato metodo `reset_reclamo_turno()` (già presente)
- [x] Aggiunti test unitari per i metodi sopra
- [x] Commit: `fix(giocatore_base): add tests for is_automatico(), reset_reclamo_turno(), reclamo_turno init [Fix 1/3]`

### Fix 2 — Bug latente: matching per ID
- [x] Aggiunto `"id_giocatore"` agli eventi premio in `verifica_premi()` (tombola + righe)
- [x] Sostituito matching per nome con matching robusto (ID + fallback nome) in `esegui_turno()`
- [x] Test esistenti ancora passano (no regressioni)
- [x] Commit: `fix(partita): add id_giocatore to prize events, robust bot claim matching [Fix 2/3]`

### Fix 3 — Ottimizzazione loop
- [x] Aggiunto `break` dopo il primo tipo trovato per riga in `_valuta_potenziale_reclamo()`
- [x] Test manuali confermano che l'ottimizzazione funziona correttamente
- [x] Commit: `perf(giocatore_automatico): add break in _valuta_potenziale_reclamo loop [Fix 3/3]`

### Status
✅ **Tutte e 3 le correzioni completate e testate**

---

## 📌 Note

- **Decisione aperta risolta**: si usa `is_automatico()` in `GiocatoreBase` (Opzione B del piano).
  Nessun `isinstance` diretto su sottoclassi in `partita.py`.
- **Backward-compatible**: la chiave `reclami_bot` è sempre presente nel dict di `esegui_turno()`
  (lista vuota se nessun bot ha reclamato). Nessun consumer esistente si rompe.
- **Il bot non è infallibile**: il reclamo può essere rigettato (es. due bot in gara sullo stesso
  ambo). `verifica_premi()` rimane l'unico arbitro. I reclami sono solo un segnale UX/log.
- **Logging silenzioso**: tutto il logging usa `_log_safe()`. Non può mai interrompere il gioco.

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.
`PLAN_BOT_ATTIVO.md` è la fonte di verità tecnica. Questo è il cruscotto operativo.
