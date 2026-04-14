---
type: todo
titolo: TODO lettura NVDA stato premi
feature: lettura_nvda_stato_premi
versione: 1.2.0
data_creazione: 2026-04-12
agent: Agent-Plan
status: IN_PROGRESS
---

# TODO — Lettura NVDA stato premi v1.2.0

Piano completo: [PLAN_lettura_nvda_stato_premi_v1.2.0.md](../3%20-%20coding%20plans/PLAN_lettura_nvda_stato_premi_v1.2.0.md)

---

## Istruzioni per Agent-Code

Esegui le fasi in ordine sequenziale. Ogni fase è un commit atomico
committabile separatamente. Prima di ogni fase verifica:

1. `python -m py_compile <file modificato>` — zero errori
2. `pytest tests/unit/ -q` — nessuna regressione
3. Aggiorna il checkbox corrispondente dopo il commit.

---

## Checklist fasi implementative

- [ ] Fase 1: Dominio — aggiungere `ultimo_premio_evento: Optional[Dict[str, Any]] = None`
  in `Partita.__init__()` e aggiornarlo in `verifica_premi()` dopo il ciclo
  di assegnazione (`bingo_game/partita.py`)

- [ ] Fase 2: Application — aggiungere `stato_premi() -> str` e
  `dettaglio_premi() -> str` in `ComandiGiocatoreUmano`, con costante
  `_SEQUENZA_PREMI` e gestione dei 3 casi (nessuno/attivo/tutti)
  (`bingo_game/comandi_partita.py`)

- [ ] Fase 3: Eventi — aggiungere 5 codici template in
  `CodiciOutputUiUmani`: `UMANI_STATO_PREMI_SINTETICO`,
  `UMANI_STATO_PREMI_NESSUNO`, `UMANI_STATO_PREMI_TUTTI`,
  `UMANI_DETTAGLIO_PREMI_HEADER`, `UMANI_DETTAGLIO_PREMI_VOCE`
  (`bingo_game/events/codici_output_ui_umani.py`)

- [ ] Fase 4: Renderer — aggiungere `annuncia_stato_premi(testo: str)` e
  `annuncia_dettaglio_premi(testo: str)` in `WxRenderer` come thin
  wrapper su `mostra_messaggio_sistema()`
  (`bingo_game/ui/renderers/renderer_wx.py`)

- [ ] Fase 5: Presentazione — aggiungere handler `Ctrl+G` e `Ctrl+I`
  in `FinestraGioco._on_char_hook()` (intercettazione `EVT_CHAR_HOOK`),
  aggiornare docstring binding in testa al file
  (`bingo_game/ui/finestra_gioco.py`)

- [ ] Fase 6: Test — creare `tests/unit/test_partita_ultimo_premio_evento.py`
  e `tests/unit/test_comandi_stato_premi.py`; eseguire
  `pytest tests/unit/ -q` e verificare tutti verdi

---

## Verifica finale pre-commit

- [ ] `python -m py_compile bingo_game/partita.py`
- [ ] `python -m py_compile bingo_game/comandi_partita.py`
- [ ] `python -m py_compile bingo_game/events/codici_output_ui_umani.py`
- [ ] `python -m py_compile bingo_game/ui/renderers/renderer_wx.py`
- [ ] `python -m py_compile bingo_game/ui/finestra_gioco.py`
- [ ] `pytest tests/unit/ -q` — tutti verdi, nessuna regressione
- [ ] Test NVDA manuale: Ctrl+G e Ctrl+I vocalizzano senza popup
- [ ] `docs/API.md` aggiornato sezione "Categoria C"
- [ ] `CHANGELOG.md` aggiornato con voce `[Unreleased]`
