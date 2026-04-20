---
type: todo
feature: lampeggio_btn_pronto
status: COMPLETED
---

# TODO — Lampeggio pulsante "Sono pronto / Ho finito" (v0.15.0)

Piano di riferimento: [PLAN_lampeggio_btn_pronto_v0.15.0.md](../3%20-%20coding%20plans/PLAN_lampeggio_btn_pronto_v0.15.0.md)

## Istruzioni per Agent-Code

- Implementa ogni fase come modifica atomica
- Ogni fase va verificata con `py -m py_compile bingo_game/ui/finestra_gioco.py`
- NON modificare nulla fuori dal perimetro PLAN

## Checklist fasi

- [x] Fase 1 — Costante colore in tema.py + import
- [x] Fase 2 — Attributi di stato in FinestraGioco.__init__
- [x] Fase 3 — Tre nuovi metodi privati (_avvia, _ferma, _on_tick_lampeggio_btn)
- [x] Fase 4 — Agganci in aggiorna_stato_pulsante e _on_close

## Stato: COMPLETATO
