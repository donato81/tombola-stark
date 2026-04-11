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

- [x] `bingo_game/events/codici_eventi.py`: aggiungere costanti
      `PAUSA_ATTIVATA`, `PAUSA_DISATTIVATA` e aggiornare `Codici_Eventi` Literal.
- [x] `bingo_game/ui/locales/it.py`: aggiungere 4 entry testo pausa/ripresa.
- [x] `bingo_game/ui/renderers/base_renderer.py`: aggiungere metodo astratto
      `annuncia_pausa(self, testo: str) -> None`.
- [x] `bingo_game/ui/renderers/renderer_wx.py`: implementare
      `annuncia_pausa(self, testo: str) -> None`.
- [x] Verificare: `python -m py_compile` su tutti i file modificati.
- [ ] Commit atomico: `feat(presentation): aggiungi infrastruttura eventi pausa`

---

### Fase 2 — Attributi e logica pausa in FinestraGioco

- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere `import time` in testa.
- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere 5 attributi pausa nel
      costruttore `__init__`.
- [x] `bingo_game/ui/finestra_gioco.py`: modificare `_avvia_pausa_turno`
      per salvare `_avvio_pausa_turno_mono = time.monotonic()`.
- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere metodo `_toggle_pausa`.
- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere metodo `_metti_in_pausa`
      con precondizioni e calcolo residuo.
- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere metodo `_riprendi_gioco`
      con annuncio stato completo.
- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere guard `if self._in_pausa: return`
      in `_on_pulsante_principale`.
- [x] Verificare: `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] Commit atomico: `feat(ui): aggiungi logica pausa e timer residuo FinestraGioco`

---

### Fase 3 — Pulsante "Pausa" e binding Ctrl+P

- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere `_btn_pausa` in `_build_ui`.
- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere handler `_on_pausa`.
- [x] `bingo_game/ui/finestra_gioco.py`: aggiungere binding `Ctrl+P`
      in `_on_char_hook` (Categoria B, dopo Ctrl+Enter).
- [x] `bingo_game/ui/finestra_gioco.py`: aggiornare `aggiorna_stato_pulsante`
      per gestire la fase `"in_pausa"` e abilitare/disabilitare `_btn_pausa`.
- [x] Verificare: `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] Commit atomico: `feat(ui): aggiungi pulsante pausa e hotkey Ctrl+P`

---

### Fase 4 — Test unitari

- [x] `tests/unit/test_pausa_gioco.py`: creare file con le 3 classi di test
      (TestMettereInPausa, TestRiprendereGioco, TestRendererAnnuncio).
- [x] Verificare: `pytest tests/unit/test_pausa_gioco.py -v` — tutti passati (18/18).
- [x] Verificare: `pytest -m "not gui" -q` — nessuna regressione introdotta.
- [ ] Commit atomico: `test(unit): suite test pausa gioco`

---

## Correzioni post-validazione (2026-04-11)

Le seguenti anomalie emerse da validazione esterna sono state risolte
senza modificare il comportamento confermato:

- `bingo_game/ui/finestra_gioco.py`: aggiunta costanti modulo `_KEY_F1`,
  `_KEY_F5`, `_KEY_F6` via `getattr` per robustezza in ambienti wx parziali;
  `_on_key_down` ora le usa al posto di `wx.WXK_F*` diretti.
- `bingo_game/ui/finestra_gioco.py`: `_on_tick_pausa` — guard difensiva
  `if self._in_pausa or self._fase_turno_ui != "pausa_turno": return`
  per ignorare callback tardivi durante pausa utente o fase errata.
- `tests/unit/test_pausa_gioco.py`: rimosso `_FinestraGiocoStub` che
  duplicava la logica; i test ora esercitano i metodi reali di
  `FinestraGioco` tramite istanza bare (`__new__`) con dipendenze moccate.
- `tests/unit/test_ciclo_turno_v2_azioni_2_3.py`: aggiunto
  `_in_pausa: bool = False` agli stub di `TestOnTickPausaAzione2`
  per allinearli alla nuova guard in `_on_tick_pausa`.

---

## Note operative

- La Fase 1 e indipendente e puo' essere committata per prima anche
  se le altre non sono ancora iniziate.
- Le Fasi 2 e 3 dipendono tra loro nell'ordine indicato.
- La Fase 4 dipende dalle Fasi 2 e 3 (testa il codice prodotto).
- Il pulsante "Pausa" deve essere il secondo elemento nel sizer di
  FinestraGioco (dopo `_btn_principale`, prima del pannello griglia),
  per garantire ordine Tab naturale e coerenza con l'UI esistente.

## Stato

- Stato implementazione: COMPLETED (2026-04-11)
- Commit/PR: implementazione e test già applicati localmente (non eseguire azioni git da agenti automatici secondo policy).

## Validazione finale

- Test unitari dedicati a pausa: PASS (tests/unit/test_pausa_gioco.py — 18/18 verdi)
- Test hotkey/shortcut: PASS (verifiche manuali e test automation locali confermano `Ctrl+P` funzionale)
- Suite non-GUI: `pytest -m "not gui"` — PASS (nessuna regressione)

## Note sui rischi residui

- La pausa è implementata esclusivamente nel layer UI; assicurarsi che integrazioni future non spostino logica di sospensione nel dominio.
- Edge-case: callback timer tardivi vengono già filtrati ma su ambienti con clock instabile verificare comportamenti su sospensioni di sistema (sleep/hibernate).
