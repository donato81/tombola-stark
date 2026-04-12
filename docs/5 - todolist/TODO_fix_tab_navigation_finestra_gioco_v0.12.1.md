## Metadati

tipo: todo_task
titolo: Fix Tab Navigation finestra di gioco — v0.12.1
data_creazione: 2026-04-12
agente: Agent-Code
stato: in corso

Piano di riferimento: [PLAN_fix_tab_navigation_finestra_gioco_v0.12.1.md](../3%20-%20coding%20plans/PLAN_fix_tab_navigation_finestra_gioco_v0.12.1.md)

---

## Checklist fasi

- [x] Fase 1 — Fix Navigate() in PannelloGriglia._on_key_down
- [x] Fase 2 — Fix MoveAfterInTabOrder in _crea_pulsanti_selezione_cartella
- [x] Fase 3 — Verifica test non-GUI (pytest -m "not gui")
- [x] Fase 4 — Aggiornamento CHANGELOG.md sezione [Unreleased]
- [x] Fase 5 — Release v0.12.1 e aggiornamento project-profile.md

---

## Istruzioni per Agent-Code

- Implementare una fase per volta
- Dopo ogni fase: py_compile + mypy (se disponibile) + pytest -m "not gui"
- Spuntare la fase nel TODO dopo ogni commit atomico
- Non procedere alla fase successiva senza gate verde

## Stato Avanzamento

- [ ] Pianificato
- [x] In corso
- [ ] Completato
- [ ] Verificato
