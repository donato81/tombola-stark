---
type: todo
feature: report_finale_storico_premi_nvda
agent: Agent-Plan
status: DRAFT
version: v0.15.0
plan_ref: docs/3 - coding plans/PLAN_report_finale_storico_premi_nvda_v0.15.0.md
date: 2026-04-13
---

# TODO — Report finale esaustivo e storico premi NVDA v0.15.0

**Piano di riferimento**: [PLAN_report_finale_storico_premi_nvda_v0.15.0.md](../3%20-%20coding%20plans/PLAN_report_finale_storico_premi_nvda_v0.15.0.md)

---

## Istruzioni per Agent-Code

Esegui le fasi nell'ordine indicato. Ogni fase deve restare atomica e
committabile separatamente. Prima di marcare una fase come completata:

1. verifica che le fasi precedenti siano `[x]`
2. esegui `python -m py_compile` sui file toccati
3. esegui i test mirati sui moduli interessati
4. aggiorna questo file dopo il commit della fase

---

## Checklist fasi implementative

- [ ] Fase A — Dominio: aggiungere `storico_premi` a `Partita` e valorizzarlo
      durante l'assegnazione premi, mantenendo coerenti `premi_gia_assegnati`,
      `premi_tipo_chiusi` e `ultimo_premio_evento`
      (`bingo_game/partita.py`)

- [ ] Fase B — Application: aggiornare `ComandiGiocatoreUmano.dettaglio_premi()`
      per leggere lo storico reale dei premi e restituire premio, vincitore e
      cartella in testo leggibile da NVDA (`bingo_game/comandi_partita.py`)

- [ ] Fase C — Presentazione: arricchire `dati_report` in `FinestraGioco`
      con `storico_premi`, `numeri_estratti` e `riepilogo_umano`
      (`bingo_game/ui/finestra_gioco.py`)

- [ ] Fase D — Renderer/UI finale: aggiornare `mostra_report_finale()` e il
      pannello riepilogo finale per mostrare premi leggibili e statistiche
      sintetiche del giocatore umano (`bingo_game/ui/renderers/renderer_wx.py`)

- [ ] Fase E — Test e documentazione: aggiornare test mirati,
      `CHANGELOG.md` e `docs/API.md`

---

## Gate di verifica finale

- [ ] `python -m py_compile bingo_game/partita.py`
- [ ] `python -m py_compile bingo_game/comandi_partita.py`
- [ ] `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] `python -m py_compile bingo_game/ui/renderers/renderer_wx.py`
- [ ] test mirati `partita` verdi
- [ ] test mirati `comandi_partita` verdi
- [ ] verifica manuale NVDA: `Ctrl+I` legge vincitori reali
- [ ] verifica manuale fine partita: nessun output `? per ?`

---

## Note operative

- G1 e G2 risultano gia chiusi nel codice corrente; questo TODO copre solo i
  gap residui G3, G4, G5 e G6 del report di diagnosi alfa.
- Non introdurre popup o finestre aggiuntive al termine della partita.
- Evitare di derivare i vincitori da stringhe tecniche nel renderer.