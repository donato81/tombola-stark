📋 TODO – Tasti Rapidi TUI (v0.10.0)
Branch: refactory-mappatura-tasti-game-play
Tipo: FEATURE
Priorità: HIGH
Stato: READY

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

**FASE 1 — Modulo codici tasti**
- [ ] Costanti definite per tutti i 26 tasti (frecce, PagSu/PagGiù, lettere
      A,Z,Q,W,R,C,D,F,G,H,U,I,O,L,E,N,?,S,V,P,X)
- [ ] Coppie byte documentate nei commenti per tasti speciali
- [ ] File salvato in `bingo_game/ui/tui/codici_tasti_tui.py`

**FASE 2 — tui_commander**
- [ ] Funzione `leggi_tasto()` implementata con msvcrt
- [ ] Funzione `comando_da_tasto(tasto)` implementata con mappatura completa
- [ ] Gestione stato Attesa Prompt distinto da Attesa Conferma S/N
- [ ] Prompt numerici usano `input()` standard (non msvcrt)
- [ ] Input non valido ai prompt gestito con messaggio + nuovo prompt
- [ ] Tasto non riconosciuto restituisce messaggio corretto

**FASE 3 — Loop tui_partita**
- [ ] Parser comandi testuali sostituito con chiamate a tui_commander
- [ ] Prompt numerici e conferme S/N gestiti correttamente nel loop
- [ ] Dipendenze da `comandi_partita` rimosse
- [ ] `_stampa()` aggiornata per nuovi messaggi

**FASE 4 — Localizzazione**
- [ ] Stringhe aggiunte per tutti i feedback attesi (Gruppi 1-10 del DESIGN)
- [ ] Messaggio tasto non valido aggiornato ("Premi ? per conoscere il focus")
- [ ] Nessun messaggio hardcoded nel Commander

**FASE 5 — Verifica controller**
- [ ] Verificato che esistano tutti i 27 metodi richiamati dal Commander
- [ ] Nessuna modifica apportata salvo approvazione esplicita
- [ ] Se metodo mancante: sub-task documentato e approvazione ricevuta

**FASE 6 — Test unitari**
- [ ] Test per ogni tasto → comando nel Commander
- [ ] Edge case: tasto senza cartella selezionata
- [ ] Edge case: navigazione oltre il bordo (6 casi)
- [ ] Edge case: prompt con input non valido
- [ ] Edge case: tasto non riconosciuto
- [ ] Test esistenti `test_tui_partita.py` aggiornati e passanti

**FASE 7 — Test di integrazione**
- [ ] Scenario partita completa simulata (selezione cartella → navigazione
      → segnatura → vittoria → uscita)
- [ ] Fixture `mock_partita` creata o riutilizzata
- [ ] Tutti i test integrazione passano

**FASE 8 — Pulizia finale**
- [ ] `comandi_partita.py` rimosso dopo verifica grep dipendenze
- [ ] README.md aggiornato con istruzioni tasti rapidi
- [ ] CHANGELOG.md aggiornato con entry `Unreleased - Added`
- [ ] TODO v0.10.0 aggiornato con checklist completate
- [ ] ARCHITECTURE.md aggiornato con tui_commander e codici_tasti_tui

---

**Presentation / Accessibilità**
- [ ] Ogni tasto produce una riga di testo leggibile da NVDA
- [ ] Nessun carattere speciale o colore ANSI nell'output
- [ ] Ogni messaggio entro 120 caratteri
- [ ] Verificato manualmente con NVDA al termine dell'implementazione

---

✅ Criteri di Completamento

L'implementazione è considerata completa quando:

- [ ] Tutte le checklist sopra sono spuntate
- [ ] Tutti i test unitari e di integrazione passano
- [ ] Copertura ≥ 85% sui moduli coinvolti
- [ ] Nessun comando testuale attivo nel codice
- [ ] Verifica NVDA completata con esito positivo
- [ ] Versione aggiornata a v0.10.0 (MINOR — nuova feature retrocompatibile)

---

📝 Aggiornamenti Obbligatori a Fine Implementazione

- [ ] Aggiornare `README.md` con la sezione tasti rapidi
- [ ] Aggiornare `CHANGELOG.md` con entry dettagliata nella sezione
      `Unreleased - Added`
- [ ] Incrementare versione a v0.10.0 (MINOR — nuova feature retrocompatibile)
- [ ] Commit finale con messaggio convenzionale
- [ ] Push su branch `refactory-mappatura-tasti-game-play`

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

---

**Fine.**

Snello, consultabile in 30 secondi, zero fronzoli.
Il documento lungo resta come fonte di verità tecnica.
Questo è il cruscotto operativo.