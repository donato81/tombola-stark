---
type: plan
titolo: Piano implementazione annuncio di benvenuto NVDA all'avvio partita
feature: benvenuto_avvio_partita_nvda
versione: 0.12.2
data_creazione: 2026-04-14
agent: Agent-Plan
status: DONE
---

# PLAN — Benvenuto avvio partita NVDA v0.12.2

## Executive summary

- Tipo: fix accessibilita NVDA su avvio partita
- Priorita: alta
- Branch suggerito: feature/benvenuto-avvio-partita-nvda-v0.12.2
- Versione target: v0.12.2
- Design di riferimento: [DESIGN_benvenuto_avvio_partita_nvda.md](../2%20-%20projects/DESIGN_benvenuto_avvio_partita_nvda.md) — DRAFT
- Report tecnico di partenza: [REPORT_ANALISI_benvenuto_non_letto_avvio_partita_2026-04-14.md](../4%20-%20reports/REPORT_ANALISI_benvenuto_non_letto_avvio_partita_2026-04-14.md)

---

## Problema e Obiettivo

Il messaggio di benvenuto della finestra di gioco non arriva all'utente
perche viene accodato dopo tre vocalizzazioni tecniche di navigazione e
dopo un `CallAfter` annidato. L'obiettivo e far sentire un solo annuncio
chiaro e immediato all'ingresso nella partita, senza alterare il corretto
allineamento del focus logico iniziale.

---

## File coinvolti

| File | Operazione | Motivo |
|---|---|---|
| bingo_game/ui/finestra_gioco.py | MODIFY | gestisce ordine focus, dispatch iniziale e messaggio di benvenuto |
| tests/ui/test_finestra_gioco.py | MODIFY | verifica flusso di chiamata, silenziamento iniziale e annuncio finale |
| docs/2 - projects/DESIGN_benvenuto_avvio_partita_nvda.md | CREATE | design della fix |
| docs/3 - coding plans/PLAN_benvenuto_avvio_partita_nvda_v0.12.2.md | CREATE | piano implementativo |
| docs/5 - todolist/TODO_benvenuto_avvio_partita_nvda_v0.12.2.md | CREATE | checklist operativa |

Nessun file in .github e nessun componente dominio/application vengono toccati.

---

## Fasi sequenziali

### Fase 1 — Rendere silenziosa l'inizializzazione del focus

**File**: bingo_game/ui/finestra_gioco.py

Operazioni:

1. Introdurre uno stato locale tipo `_avvio_iniziale_in_corso: bool` nel costruttore.
2. Usare questo flag per evitare che i tre dispatch di `_imposta_focus_iniziale()`
   inviino eventi vocali al renderer durante il primo posizionamento logico.
3. Mantenere invariati gli aggiornamenti visivi e lo stato interno del focus.

Commit atomico suggerito: `fix(ui): silenzia dispatch iniziali all'avvio partita`

### Fase 2 — Emettere il benvenuto con priorita corretta

**File**: bingo_game/ui/finestra_gioco.py

Operazioni:

1. Rimuovere il `wx.CallAfter` annidato che rinvia il messaggio di benvenuto.
2. Emettere il messaggio al termine di `_imposta_focus_iniziale()`.
3. Usare una chiamata che vocalizzi con `interrompi=True` oppure un helper locale
   equivalente, senza alterare il contratto standard del renderer per gli altri flussi.

Commit atomico suggerito: `fix(ui): ripristina annuncio iniziale NVDA in FinestraGioco`

### Fase 3 — Copertura test UI mirata

**File**: tests/ui/test_finestra_gioco.py

Operazioni:

1. Aggiungere un test che verifichi che `_imposta_focus_iniziale()` non chiami il renderer
   tramite `_dispatch` in modalita vocale standard durante l'avvio iniziale.
2. Aggiungere un test che verifichi l'emissione del solo messaggio di benvenuto finale.
3. Verificare che il testo resti coerente con le istruzioni utente esistenti.

Commit atomico suggerito: `test(ui): copre annuncio iniziale NVDA in finestra gioco`

---

## Test Plan

### Automatici

- `python -m py_compile bingo_game/ui/finestra_gioco.py`
- `python -m py_compile tests/ui/test_finestra_gioco.py`
- esecuzione mirata della suite `tests/ui/test_finestra_gioco.py`

### Manuali

1. Aprire configurazione partita e avviare il gioco con NVDA attivo.
2. Verificare che all'ingresso venga letto subito il messaggio orientativo.
3. Verificare che non vengano letti prima "Cartella 1 selezionata", riga e colonna.
4. Verificare che Ctrl+H resti coerente con il testo annunciato.

---

## Rischi

- La soppressione dei dispatch iniziali potrebbe nascondere anche side effect utili se applicata in modo troppo ampio.
- Un uso improprio di `interrompi=True` potrebbe troncare annunci legittimi se riutilizzato fuori dall'avvio iniziale.
- I test automatici non possono certificare l'audio reale di NVDA, solo la sequenza di chiamate.

---

## Criteri di completamento

- [ ] L'ingresso in FinestraGioco produce un solo annuncio orientativo udibile.
- [ ] I tre dispatch iniziali non generano voce durante l'avvio.
- [ ] Nessuna regressione sul focus logico iniziale di cartella, riga e colonna.
- [ ] I test mirati di finestra_gioco coprono la nuova sequenza.
- [ ] I controlli `py_compile` sui file modificati sono verdi.
