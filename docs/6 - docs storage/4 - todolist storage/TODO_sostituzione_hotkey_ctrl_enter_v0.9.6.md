---
type: todo
feature: sostituzione_hotkey_ctrl_enter
status: DONE
---

# TODO: Sostituzione hotkey Ctrl+P → Ctrl+Enter (v0.9.6)

Piano completo: [PLAN_sostituzione_hotkey_ctrl_enter_v0.9.6.md](../3%20-%20coding%20plans/PLAN_sostituzione_hotkey_ctrl_enter_v0.9.6.md)

---

## Checklist

- [x] **Fase 1** — Modifica binding attivo in `bingo_game/ui/finestra_gioco.py` (riga 300)
  - `if ctrl and key == ord("P"):` → `if ctrl and key == wx.WXK_RETURN:`

- [x] **Fase 2** — Aggiorna commenti/docstring in `bingo_game/ui/finestra_gioco.py`
  - riga 28: `Ctrl+P -> passa turno` → `Ctrl+Enter -> passa turno`
  - riga 299: `# Ctrl+P — passa turno` → `# Ctrl+Enter — passa turno`

- [x] **Fase 3** — Aggiorna docstring in `bingo_game/partita.py` (riga 814)
  - `"Ho finito"/Ctrl+P` → `"Ho finito"/Ctrl+Enter`

- [x] **Fase 4** — Rename simboli test + aggiungi test binding `_on_char_hook`
  - Rename classe: `TestFinestraGiocoCtrlPAttesaReclami` → `TestFinestraGiocoCtrlEnterAttesaReclami`
  - Rename metodo: `test_ctrl_p_attesa_reclami_emette_conferma_prima_dichiarazione` → `test_ctrl_enter_...`
  - Rename metodo: `test_ctrl_p_attesa_reclami_emette_messaggio_idempotente` → `test_ctrl_enter_...`
  - Aggiungi `test_char_hook_ctrl_enter_invoca_pulsante_principale` in `TestFinestraGiocoShortcuts`

- [x] **Fase 5** — Pre-commit check
  - `python -m py_compile bingo_game/ui/finestra_gioco.py` → exit 0
  - `python -m py_compile bingo_game/partita.py` → exit 0
  - `python -m py_compile tests/unit/test_finestra_gioco_shortcuts.py` → exit 0
  - `pytest tests/unit/test_finestra_gioco_shortcuts.py -v` → tutti verdi

---

## Istruzioni per Agent-Code

Esegui le fasi in ordine sequenziale. Ogni fase è atomica e committable
separatamente. Prima di iniziare, esegui:

```bash
grep -r "CtrlP\|ctrl_p" tests/
```

per escludere riferimenti incrociati al simbolo rinominato.

Dopo ogni fase verifica la compilazione sintattica del file modificato.
Alla Fase 5 esegui la suite completa prima di proporre il commit.
