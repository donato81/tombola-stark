---
type: todo
feature: ricerca_conferma_esplicita_dialog
agent: Agent-Plan
status: DRAFT
version: v1.1.1
plan_ref: docs/3 - coding plans/PLAN_ricerca_conferma_esplicita_dialog_v1.1.1.md
design_ref: docs/2 - projects/DESIGN_ricerca_conferma_esplicita_dialog.md
date: 2026-04-09
---

# TODO — Conferma esplicita dialog ricerca numero (Ctrl+F) v1.1.1

Piano di riferimento:
[PLAN_ricerca_conferma_esplicita_dialog_v1.1.1.md](../3%20-%20coding%20plans/PLAN_ricerca_conferma_esplicita_dialog_v1.1.1.md)

---

## Istruzioni per Agent-Code

- Eseguire le fasi nell'ordine indicato.
- Ogni fase deve restare atomica e committabile separatamente.
- Prima di ogni commit eseguire il compile del file Python toccato.
- Nessun `print()` nei file di produzione.
- Dopo ogni fase aggiornare questo TODO marcando solo i punti effettivamente completati.

---

## Checklist operativa

- [ ] FASE 1 — Rifattorizzare `bingo_game/ui/dialogo_ricerca.py`
- [ ] Rimuovere la chiusura automatica con timer dal ramo `trovato`
- [ ] Introdurre `_risultato_pronto_per_conferma`
- [ ] Garantire reset di `_primo_risultato` a ogni nuova ricerca
- [ ] Aggiungere il controllo `Vai al risultato` inizialmente disabilitato
- [ ] Abilitare e focalizzare `Vai al risultato` dopo un esito `trovato`
- [ ] Lasciare input focalizzato dopo un esito `non_trovato`
- [ ] Verificare che `Escape` continui a chiudere con `wx.ID_CANCEL`
- [ ] `python -m py_compile bingo_game/ui/dialogo_ricerca.py`
- [ ] Commit fase 1

- [ ] FASE 2 — Rifinire `bingo_game/ui/finestra_gioco.py`
- [ ] Confermare lettura di `_primo_risultato` solo con `rc == wx.ID_OK`
- [ ] Confermare assenza di navigazione sul ramo cancel
- [ ] Aggiungere eventuali guard difensivi se necessari
- [ ] `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] Commit fase 2

- [ ] FASE 3 — Aggiornare `tests/unit/test_dialogo_ricerca_persistente.py`
- [ ] Rimuovere i test dipendenti da `wx.CallLater`
- [ ] Aggiungere test per esito trovato con conferma esplicita
- [ ] Aggiungere test per esito non trovato con reset stato
- [ ] Aggiungere test per `Escape` e `wx.ID_CANCEL`
- [ ] Aggiungere test contro riuso di risultato stantio
- [ ] `python -m py_compile tests/unit/test_dialogo_ricerca_persistente.py`
- [ ] Eseguire i test mirati del file
- [ ] Commit fase 3

---

## Verifica manuale finale

- [ ] Scenario trovato: NVDA legge tutto il risultato senza chiusura automatica del dialog
- [ ] Scenario trovato: `Invio` su `Vai al risultato` chiude il dialog e naviga al primo match
- [ ] Scenario non trovato: il dialog resta aperto e il focus torna all'input
- [ ] Scenario cancel: `Escape` chiude il dialog senza navigazione automatica

---

## Stato Avanzamento

- [x] Pianificato
- [ ] In corso
- [ ] Completato
- [ ] Verificato
