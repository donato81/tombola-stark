# TODO — Pausa del gioco (v1.2.0)

**Piano di riferimento**: [PLAN_pausa_gioco_v1.2.0.md](../3%20-%20coding%20plans/PLAN_pausa_gioco_v1.2.0.md)
**Design di riferimento**: [DESIGN_pausa_gioco.md](../2%20-%20projects/DESIGN_pausa_gioco.md)
**Versione target**: 1.2.0
**Data creazione**: 2026-04-11

---

## Istruzioni per Agent-Code

- Implementa una fase alla volta nell'ordine indicato.
- Ogni fase e committable separatamente (commit atomico).
- Spunta la fase nel TODO subito dopo il commit.
- Prima di ogni commit esegui la pre-commit checklist indicata nel PLAN.
- Non avanzare alla fase successiva senza aver spuntato e committato la precedente.
- Non modificare il dominio: zero modifiche a partita.py, tabellone.py,
  cartella.py, players/, exceptions/.

---

## Checklist fasi

### Fase 1 — Infrastruttura eventi e locales

- [ ] `bingo_game/events/codici_eventi.py`: aggiungere costanti
      `PAUSA_ATTIVATA`, `PAUSA_DISATTIVATA` e aggiornare `Codici_Eventi` Literal.
- [ ] `bingo_game/ui/locales/it.py`: aggiungere 4 entry testo pausa/ripresa.
- [ ] `bingo_game/ui/renderers/base_renderer.py`: aggiungere metodo astratto
      `annuncia_pausa(self, testo: str) -> None`.
- [ ] `bingo_game/ui/renderers/renderer_wx.py`: implementare
      `annuncia_pausa(self, testo: str) -> None`.
- [ ] Verificare: `python -m py_compile` su tutti i file modificati.
- [ ] Commit atomico: `feat(presentation): aggiungi infrastruttura eventi pausa`

---

### Fase 2 — Attributi e logica pausa in FinestraGioco

- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere `import time` in testa.
- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere 5 attributi pausa nel
      costruttore `__init__`.
- [ ] `bingo_game/ui/finestra_gioco.py`: modificare `_avvia_pausa_turno`
      per salvare `_avvio_pausa_turno_mono = time.monotonic()`.
- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere metodo `_toggle_pausa`.
- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere metodo `_metti_in_pausa`
      con precondizioni e calcolo residuo.
- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere metodo `_riprendi_gioco`
      con annuncio stato completo.
- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere guard `if self._in_pausa: return`
      in `_on_pulsante_principale`.
- [ ] Verificare: `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] Commit atomico: `feat(ui): aggiungi logica pausa e timer residuo FinestraGioco`

---

### Fase 3 — Pulsante "Pausa" e binding Ctrl+P

- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere `_btn_pausa` in `_build_ui`.
- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere handler `_on_pausa`.
- [ ] `bingo_game/ui/finestra_gioco.py`: aggiungere binding `Ctrl+P`
      in `_on_char_hook` (Categoria B, dopo Ctrl+Enter).
- [ ] `bingo_game/ui/finestra_gioco.py`: aggiornare `aggiorna_stato_pulsante`
      per gestire la fase `"in_pausa"` e abilitare/disabilitare `_btn_pausa`.
- [ ] Verificare: `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] Commit atomico: `feat(ui): aggiungi pulsante pausa e hotkey Ctrl+P`

---

### Fase 4 — Test unitari

- [ ] `tests/unit/test_pausa_gioco.py`: creare file con le 3 classi di test
      (TestMettereInPausa, TestRiprendereGioco, TestRendererAnnuncio).
- [ ] Verificare: `pytest tests/unit/test_pausa_gioco.py -v` — tutti passati.
- [ ] Verificare: `pytest -m "not gui" -q` — nessuna regressione.
- [ ] Commit atomico: `test(unit): suite test pausa gioco`

---

## Note operative

- La Fase 1 e indipendente e puo' essere committata per prima anche
  se le altre non sono ancora iniziate.
- Le Fasi 2 e 3 dipendono tra loro nell'ordine indicato.
- La Fase 4 dipende dalle Fasi 2 e 3 (testa il codice prodotto).
- Il pulsante "Pausa" deve essere il secondo elemento nel sizer di
  FinestraGioco (dopo `_btn_principale`, prima del pannello griglia),
  per garantire ordine Tab naturale e coerenza con l'UI esistente.
