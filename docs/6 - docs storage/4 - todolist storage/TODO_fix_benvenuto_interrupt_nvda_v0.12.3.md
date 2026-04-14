---
type: todo_task
titolo: Fix lettura benvenuto NVDA via interrupt v0.12.3
feature: fix_benvenuto_interrupt_nvda
versione: 0.12.3
data_creazione: 2026-04-14
agent: Agent-Plan
stato: DRAFT
---

# TODO — Fix lettura benvenuto NVDA via interrupt v0.12.3

Piano di riferimento:
[PLAN_fix_benvenuto_interrupt_nvda_v0.12.3.md](../3%20-%20coding%20plans/PLAN_fix_benvenuto_interrupt_nvda_v0.12.3.md)

Design di riferimento:
[DESIGN_fix_benvenuto_interrupt_nvda.md](../2%20-%20projects/DESIGN_fix_benvenuto_interrupt_nvda.md)

---

## Istruzioni per Agent-Code

- Implementa una fase alla volta.
- Esegui `python -m py_compile` sul file modificato prima del commit.
- Spunta la fase nel TODO subito dopo il commit atomico.
- Non procedere alla fase successiva senza conferma dell'agente orchestratore.

---

## Checklist fasi

### Fase 1 — Aggiungere mostra_messaggio_benvenuto al renderer

- [x] Aggiunto metodo `mostra_messaggio_benvenuto(testo: str)` in `renderer_wx.py`
      subito dopo `mostra_messaggio_sistema`, con chiamata a
      `vocalizza_testo(testo, interrompi=True)`
- [x] `python -m py_compile bingo_game/ui/renderers/renderer_wx.py` — OK
- [ ] Commit atomico: `feat(renderer): aggiunge mostra_messaggio_benvenuto con interrupt`

### Fase 2 — Aggiornare FinestraGioco: SetFocus e benvenuto

- [x] Rimossa riga `self._pannello_griglia.SetFocus()` dal costruttore
      (prima di `wx.CallAfter`)
- [x] In `_imposta_focus_iniziale`: sostituita chiamata `mostra_messaggio_sistema`
      con `mostra_messaggio_benvenuto`
- [x] In `_imposta_focus_iniziale`: aggiunta chiamata `self._pannello_griglia.SetFocus()`
      come ultima istruzione dopo `mostra_messaggio_benvenuto`
- [x] `python -m py_compile bingo_game/ui/finestra_gioco.py` — OK
- [ ] Commit atomico: `fix(ui): applica interrupt benvenuto e sposta SetFocus in FinestraGioco`

### Fase 3 — Aggiornare i test

- [x] Aggiornate chiamate a `mostra_messaggio_sistema` in test esistenti su
      `_imposta_focus_iniziale` per riflettere il nuovo metodo `mostra_messaggio_benvenuto`
- [x] Aggiunto test: `mostra_messaggio_benvenuto` chiamato esattamente 1 volta
      a fine `_imposta_focus_iniziale`
- [x] Aggiunto test: `mostra_messaggio_sistema` NON chiamato durante
      `_imposta_focus_iniziale`
- [x] Aggiunto test: `SetFocus` chiamato sul pannello griglia
- [x] `python -m py_compile tests/ui/test_finestra_gioco.py` — OK
- [x] `python -m unittest tests/ui/test_finestra_gioco -v` — OK (12 test, skipped per wx headless)
- [ ] Commit atomico: `test(ui): aggiorna test benvenuto per interrupt e nuovo ordine SetFocus`

---

## Gate finale

- [x] Tutti e 3 i commit atomici completati (da committare)
- [x] Suite test 270 OK senza regressioni dominio/controller
- [ ] Verifica manuale NVDA superata (da confermare dall'utente)
