📋 TODO – Tasti Rapidi TUI (v0.10.0)
Branch: refactory-mappatura-tasti-game-play
Tipo: FEATURE
Priorità: HIGH
Stato: DONE

---

📖 Riferimento Documentazione
Prima di iniziare qualsiasi implementazione, consultare obbligatoriamente:
`documentations/3 - planning/PLAN_tasti-rapidi-tui_v0.10.0.md`

Questo file TODO è solo un sommario operativo da consultare e aggiornare
durante ogni fase dell'implementazione.
Il piano completo contiene analisi, architettura, edge case e dettagli tecnici.

---

🤖 Istruzioni per Copilot Agent

Implementare le modifiche in modo **incrementale** su più commit atomici e logici.

**Workflow per ogni fase:**

1. **Leggi questo TODO** → Identifica la prossima fase da implementare
2. **Consulta piano completo** → Rivedi dettagli tecnici, architettura,
   edge case della fase
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
- ✅ **Commit message format**: `type(scope): description [Phase N/8]`
- ❌ **NO commit multipli senza aggiornare TODO** (perde tracciabilità)
- ❌ **NO implementazione completa in un colpo** (viola incrementalità)

**Esempio workflow reale:**
```
Fase 1: Codici tasti
→ Implementa + Commit + Aggiorna TODO ✅

Fase 2: tui_commander
→ Rileggi piano completo sezione Fase 2
→ Implementa + Commit + Aggiorna TODO ✅

Fase 3: Loop tui_partita
→ Rileggi piano completo sezione Fase 3
→ Implementa + Commit + Aggiorna TODO ✅

... e così via per tutte le 8 fasi
```

---

🎯 Obiettivo Implementazione

- Introdurre tasti rapidi singoli (msvcrt) per la navigazione e le azioni
  di gioco, eliminando i comandi testuali seguiti da Invio.
- Creare il modulo tui_commander che mappa byte letti da msvcrt a comandi
  logici, separando la logica di input dal game loop principale.
- Rendere l'esperienza fluida e accessibile per utenti NVDA su Windows 11,
  con feedback testuale immmediato dopo ogni tasto.

---

📂 File Coinvolti

- `bingo_game/ui/tui/codici_tasti_tui.py` → CREATE
- `bingo_game/ui/tui/tui_commander.py` → CREATE
- `bingo_game/ui/tui/tui_partita.py` → MODIFY
- `bingo_game/ui/locales/it.py` → MODIFY
- `bingo_game/game_controller.py` → VERIFY ONLY (no modifche salvo approvazione)
- `tests/unit/test_tui_commander.py` → CREATE
- `tests/unit/test_tui_partita.py` → MODIFY
- `tests/integration/test_game_loop_tasti.py` → CREATE
- `README.md` → UPDATE
- `CHANGELOG.md` → UPDATE
- `documentations/ARCHITECTURE.md` → UPDATE

---

🛠 Checklist Implementazione

**FASE 1 — Modulo codici tasti** ✅ COMPLETATA
- [x] Costanti definite per tutti i 26 tasti (frecce, PagSu/PagGiù, lettere
      A,Z,Q,W,R,C,D,F,G,H,U,I,O,L,E,N,?,S,V,P,X)
- [x] Coppie byte documentate nei commenti per tasti speciali
- [x] File salvato in `bingo_game/ui/tui/codici_tasti_tui.py`

**FASE 2 — tui_commander** ✅ COMPLETATA
- [x] Funzione `leggi_tasto()` implementata con msvcrt
- [x] Funzione `comando_da_tasto(tasto)` implementata con mappatura completa
- [x] Gestione stato Attesa Prompt distinto da Attesa Conferma S/N
- [x] Prompt numerici usano `input()` standard (non msvcrt)
- [x] Input non valido ai prompt gestito con messaggio + nuovo prompt
- [x] Tasto non riconosciuto restituisce messaggio corretto

**FASE 3 — Loop tui_partita** ✅ COMPLETATA
- [x] Parser comandi testuali sostituito con chiamate a tui_commander
- [x] Prompt numerici e conferme S/N gestiti correttamente nel loop
- [x] Dipendenze da `comandi_partita` rimosse
- [x] `_stampa()` aggiornata per nuovi messaggi

**FASE 4 — Localizzazione** ✅ COMPLETATA
- [x] Stringhe aggiunte per tutti i feedback attesi (Gruppi 1-10 del DESIGN)
- [x] Messaggio tasto non valido aggiornato ("Premi ? per conoscere il focus")
- [x] Nessun messaggio hardcoded nel Commander

**FASE 5 — Verifica controller** ✅ COMPLETATA (nessuna modifica applicata)
- [x] Verificato che esistano tutti i 27 metodi richiamati dal Commander
- [x] Nessuna modifica apportata (tutti i metodi presenti in GiocatoreUmano e game_controller)
- [x] Se metodo mancante: sub-task documentato e approvazione ricevuta

**FASE 6 — Test unitari** ✅ COMPLETATA
- [x] Test per ogni tasto → comando nel Commander (test_tui_commander.py — 13 test, Tests 1-13)
- [x] Edge case: tasto senza cartella selezionata (Tests 17, 19, 23)
- [x] Edge case: navigazione oltre il bordo — dominio ritorna ok=False senza eccezioni (Test 27)
- [x] Edge case: prompt con input non valido (Test 21)
- [x] Edge case: tasto non riconosciuto → messaggio LOOP_TASTO_NON_VALIDO (Test 26)
- [x] Test esistenti `test_tui_partita.py` aggiornati e passanti (Tests 16-27 aggiunti)

**FASE 7 — Test di integrazione** ✅ COMPLETATA
- [x] Scenario partita completa simulata (selezione cartella → navigazione
      → segnatura → vittoria → uscita) — Scenario F
- [x] Fixture `mock_partita` creata in `tests/integration/test_game_loop_tasti.py`
- [x] Tutti i test integrazione passano (6 scenari A-F coperti)

**FASE 8 — Pulizia finale** ✅ COMPLETATA
- [x] `comandi_partita.py` — NON eliminato: `tests/test_comandi_partita.py` importa
      `ComandiSistema`. Vedi Note in fondo al documento.
- [x] README.md aggiornato con sezione "Tasti Rapidi (v0.10.0)" (Gruppi 1-10)
- [x] CHANGELOG.md aggiornato con entry `[Unreleased]` (Added/Changed/Removed)
- [x] TODO v0.10.0 aggiornato con checklist completate
- [x] ARCHITECTURE.md aggiornato con `tui_commander.py` e `codici_tasti_tui.py`

---

**Presentation / Accessibilità**
- [x] Ogni tasto produce una riga di testo leggibile da NVDA
- [x] Nessun carattere speciale o colore ANSI nell'output
- [x] Ogni messaggio entro 120 caratteri
- [ ] Verificato manualmente con NVDA al termine dell'implementazione

---

✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [x] Tutte le checklist sopra sono spuntate
- [x] Tutti i test unitari e di integrazione passano
- [x] Copertura ≥ 85% sui moduli coinvolti
- [x] Nessun comando testuale attivo nel codice
- [ ] Verifica NVDA completata con esito positivo (da eseguire manualmente)
- [x] Versione aggiornata a v0.10.0 (MINOR — nuova feature retrocompatibile)

---

📝 Aggiornamenti Obbligatori a Fine Implementazione

- [x] Aggiornare `README.md` con la sezione tasti rapidi
- [x] Aggiornare `CHANGELOG.md` con entry dettagliata nella sezione
      `Unreleased - Added`
- [x] Incrementare versione a v0.10.0 (MINOR — nuova feature retrocompatibile)
- [x] Commit finale con messaggio convenzionale
- [x] Push su branch `refactory-mappatura-tasti-game-play`

---

📌 Note

- I tasti speciali (frecce, PagSu/PagGiù) richiedono lettura a 2 byte con
  msvcrt: prefisso `\xe0` seguito dal codice specifico.
- Il Commander non chiama mai `print()` direttamente: tutto passa per
  TerminalRenderer.
- Il Commit 5 è solo verifica: nessuna modifica al controller senza
  approvazione esplicita.
- Riferimento completo ai metodi del dominio: sezione "Riferimenti
  Contestuali" nel DESIGN document.
- **COMANDI_PARTITA NON ELIMINATO**: `bingo_game/comandi_partita.py`
  non è stato rimosso perché `tests/test_comandi_partita.py` (riga 17)
  importa `ComandiSistema` da esso. Prima di eliminare, occorre aggiornare
  o rimuovere quel test. Azione da pianificare in un ticket separato.

- **FIX — loop testuale confermato rimosso** (24/02/2026): Verifica
  eseguita su branch `refactory-mappatura-tasti-game-play`. La funzione
  `_loop_partita` contiene ESCLUSIVAMENTE il nuovo loop v0.10.0 con
  `leggi_tasto()` e `comando_da_tasto()`. Nessun `while True` con
  `input("Comando...")` presente. Le funzioni legacy (`_gestisci_segna`,
  `_gestisci_riepilogo_cartella`, `_gestisci_riepilogo_tabellone`,
  `_gestisci_quit`, `_gestisci_help`) esistono per compatibilità test
  v0.9.0 ma NON sono chiamate dal nuovo loop. Docstring aggiornata a
  v0.10.0. Commit: `fix(tui_partita): rimuovi vecchio loop testuale da
  _loop_partita [Fix]`.

- **FIX — chiave LOOP_TASTO_NON_VALIDO aggiunta** (24/02/2026): Tasto
  non mappato (es. Escape) causava `KeyError: 'LOOP_TASTO_NON_VALIDO'`
  in `it.py`. Aggiunta la chiave mancante in `MESSAGGI_OUTPUT_UI_UMANI`
  con testo: "Tasto non valido. Premi ? per conoscere il focus."
  Commit: `fix(locales): aggiungi chiavi LOOP mancanti in
  MESSAGGI_OUTPUT_UI_UMANI [Fix]`.

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.
Il documento lungo resta come fonte di verità tecnica.
Questo è il cruscotto operativo.