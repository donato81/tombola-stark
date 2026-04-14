---
type: todo
titolo: TODO benvenuto avvio partita NVDA
feature: benvenuto_avvio_partita_nvda
versione: 0.12.2
data_creazione: 2026-04-14
agent: Agent-Plan
status: COMPLETED
---

# TODO — Benvenuto avvio partita NVDA v0.12.2

Piano completo: [PLAN_benvenuto_avvio_partita_nvda_v0.12.2.md](../3%20-%20coding%20plans/PLAN_benvenuto_avvio_partita_nvda_v0.12.2.md)

---

## Istruzioni per Agent-Code

Eseguire le fasi in ordine. Non iniziare l'implementazione finche DESIGN e PLAN
non sono stati validati. Dopo ogni fase aggiornare questo file e rieseguire i
controlli minimi richiesti dal workflow.

---

## Checklist fasi implementative

- [x] Fase 1: introdurre in FinestraGioco uno stato locale per distinguere l'avvio iniziale dai dispatch normali.
- [x] Fase 2: rendere silenziosi i tre dispatch di `_imposta_focus_iniziale()` senza perdere gli aggiornamenti di stato interni.
- [x] Fase 3: rimuovere il `CallAfter` annidato e vocalizzare il messaggio di benvenuto una sola volta con priorita corretta.
- [x] Fase 4: aggiungere o aggiornare test UI mirati in `tests/ui/test_finestra_gioco.py`.
- [ ] Fase 5: verificare manualmente con NVDA l'ingresso in partita dopo la configurazione.

---

## Verifiche minime

- [x] `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [x] `python -m py_compile tests/ui/test_finestra_gioco.py`
- [x] Esecuzione mirata di `tests/ui/test_finestra_gioco.py`
- [ ] Test manuale NVDA: il benvenuto viene letto subito e senza annunci tecnici preliminari
