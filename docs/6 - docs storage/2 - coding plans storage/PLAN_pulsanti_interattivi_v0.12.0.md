---
type: plan
feature: pulsanti_interattivi
agent: Agent-Plan
status: READY
version: v0.12.0
design_ref: docs/2 - projects/DESIGN_pulsanti_interattivi_v0.12.0.md
date: 2026-04-12
---

# PLAN — Pulsanti interattivi FinestraGioco v0.12.0

## 1. Executive Summary

- **Tipo**: Feature UI (presentazione) — interazione mouse
- **Priorità**: Media — equivalente tasti già esistenti, zero regressioni NVDA
- **Branch**: main
- **Versione target**: v0.12.0
- **Commit attesi**: 2 (finestra_gioco + renderer, poi CHANGELOG)

## 2. Problema e Obiettivo

`FinestraGioco` ha binding tastiera completi (Categorie A, B, C) ma nessun
pulsante cliccabile per la navigazione cartelle, la selezione diretta cartella
e la dichiarazione premi. Gli utenti vedenti che usano il mouse non possono
eseguire queste azioni.

Obiettivo: aggiungere tre gruppi di pulsanti che chiamano gli stessi comandi
già collegati ai tasti, senza toccare il sistema vocale, i timer o i binding.

## 3. File coinvolti

| File | Operazione | Note |
|------|-----------|------|
| `bingo_game/ui/finestra_gioco.py` | Modifica — layout + pulsanti + handler | Principal target |
| `bingo_game/ui/renderers/renderer_wx.py` | Modifica — aggiunta chiamata duck typing | 1 riga in 1 handler |
| `CHANGELOG.md` | Modifica — entry `[Unreleased]` | Fase 2 pulsanti |

`bingo_game/ui/tema.py` — nessuna modifica (tutte le costanti già presenti).

## 4. Fasi implementative

### Fase A — Import e struttura base `finestra_gioco.py`

**File**: `bingo_game/ui/finestra_gioco.py`

1. Aggiungere `import functools` agli import standard.
2. Aggiungere ai import da `tema.py`:
   - `COLORE_ACCENT_BLU`, `COLORE_ACCENT_ROSSO`
   - `COLORE_BTN_TOMBOLA`, `COLORE_BTN_TOMBOLA_TESTO`, `COLORE_BTN_NEUTRO`
   - `DIMENSIONE_BTN_FRECCIA`, `DIMENSIONE_BTN_SELEZIONE_CARTELLA`
3. Salvare `self._panel = wx.Panel(self)` in `_build_ui()` per accesso
   dinamico da `_crea_pulsanti_selezione_cartella()`.

### Fase B — Gruppo 1: frecce navigazione cartella

**File**: `bingo_game/ui/finestra_gioco.py`

In `_build_ui()`, modificare la costruzione di `sizer_griglie`:
- Creare `self._btn_freccia_sx` (label `"◀"`, size `DIMENSIONE_BTN_FRECCIA`,
  name `"Cartella precedente"`, colori `COLORE_ACCENT_BLU`/`COLORE_TESTO_CHIARO`).
- Creare `self._btn_freccia_dx` (label `"▶"`, analoghi).
- Aggiungere al sizer: `[tabellone]  [◀]  [cartella]  [▶]`.
- Entrambi disabilitati all'avvio.
- Bind: `self._on_cartella_precedente`, `self._on_cartella_successiva`.

Aggiungere i metodi:
- `_on_cartella_precedente(self, event)`: dispatcha `cartella_precedente()`.
- `_on_cartella_successiva(self, event)`: dispatcha `cartella_successiva()`.

In `aggiorna_stato_pulsante()`:
- Abilitare frecce quando `conteggio > 0 AND not terminata AND fase not in ("in_pausa", "pausa_turno")`.
- Gestire anche il ramo `in_pausa` (early return) con disabilitazione esplicita.

### Fase C — Gruppo 2: selezione diretta cartella

**File**: `bingo_game/ui/finestra_gioco.py`

In `_build_ui()`:
- Aggiungere `self._sizer_selezione = wx.BoxSizer(wx.HORIZONTAL)`.
- Inizializzare `self._pulsanti_selezione: list[wx.Button] = []`.
- Aggiungere `self._sizer_selezione` al sizer principale sotto `sizer_griglie`.

Aggiungere i metodi:
- `_crea_pulsanti_selezione_cartella()`: crea da 1 a 6 pulsanti nella riga
  `sizer_selezione`. Guard: `if self._pulsanti_selezione: return`.
- `_on_seleziona_cartella(n, event)`: dispatcha `imposta_focus_cartella(n)`.
- `_aggiorna_evidenziazione_selezione(numero_cartella)`: colora pulsante attivo
  con `COLORE_ACCENT_BLU`/`COLORE_TESTO_CHIARO`, gli altri con `COLORE_BTN_NEUTRO`/`COLORE_TESTO_SCURO`.
- `aggiorna_selezione_cartella(numero)` (pubblico): chiama `_aggiorna_evidenziazione_selezione`.

In `_on_pulsante_principale()`:
- Prima del blocco `attesa_estrazione`, inserire guard:
  `if get_conteggio_estratti() == 0: self._crea_pulsanti_selezione_cartella()`.

### Fase D — Gruppo 3: pulsanti premi

**File**: `bingo_game/ui/finestra_gioco.py`

In `_build_ui()`:
- Creare `sizer_premi = wx.BoxSizer(wx.HORIZONTAL)`.
- Creare 5 pulsanti con label `Ambo`, `Terno`, `Quaterna`, `Cinquina`, `Tombola`.
- Stile: Ambo–Cinquina → `COLORE_ACCENT_ROSSO`/`"#FFFFFF"`;
  Tombola → `COLORE_BTN_TOMBOLA`/`COLORE_BTN_TOMBOLA_TESTO`.
- `SetName(f"Dichiara {tipo}")` su ciascuno.
- Tutti disabilitati all'avvio.
- Bind con `functools.partial(self._on_premio, tipo)`.
- Salvare in `self._btn_premi: dict[str, wx.Button] = {}`.

Aggiungere il metodo:
- `_on_premio(tipo, event)`: dispatcha `annuncia_vittoria(tipo, self._turno_corrente)`.

In `aggiorna_stato_pulsante()`:
- Leggere `premi_chiusi = getattr(self._partita, "premi_tipo_chiusi", set())`.
- Per fase `attesa_reclami`: abilitare tutti tranne quelli in `premi_chiusi`.
- Per tutte le altre fasi: disabilitare tutti.
- Se `tipo in premi_chiusi`: disabilitare permanentemente e aggiungere ` ✓` alla label.

### Fase E — Renderer: evidenziazione selezione cartella

**File**: `bingo_game/ui/renderers/renderer_wx.py`

In `_handle_focus_cartella_impostato()`, subito prima di `self._ao2_vocalizza(testo)`:
```python
if hasattr(self._finestra, "aggiorna_selezione_cartella"):
    self._finestra.aggiorna_selezione_cartella(evento.numero_cartella)
```

### Fase F — CHANGELOG

**File**: `CHANGELOG.md`

Aggiungere sotto `## [Unreleased]`:
```markdown
### Fase 2 — Pulsanti interattivi

- `bingo_game/ui/finestra_gioco.py`: aggiunto Gruppo 1 (frecce ◀▶ navigazione cartella),
  Gruppo 2 (pulsanti 1…N selezione diretta, creati dinamicamente all'avvio),
  Gruppo 3 (pulsanti Ambo/Terno/Quaterna/Cinquina/Tombola con abilitazione per fase).
- `bingo_game/ui/renderers/renderer_wx.py`: in `_handle_focus_cartella_impostato`
  aggiunta chiamata duck typing `aggiorna_selezione_cartella` per evidenziare il
  pulsante della cartella corrente.
```

## 5. Pre-commit checklist

Prima di ogni commit eseguire:
```
python -m py_compile bingo_game/ui/finestra_gioco.py
python -m py_compile bingo_game/ui/renderers/renderer_wx.py
python -m unittest tests/test_game_controller.py -q
python -m unittest tests/test_partita.py -q
```

## 6. Criteri di completamento

- [ ] Frecce ◀▶ visibili nel layout, abilitate durante partita attiva.
- [ ] Pulsanti 1…N compaiono dopo il primo click "Inizia partita".
- [ ] Pulsante della cartella corrente evidenziato in blu.
- [ ] Pulsanti premi abilitati solo in fase `attesa_reclami`.
- [ ] Pulsanti premi già assegnati mostrano ` ✓` e sono disabilitati.
- [ ] Test esistenti passano senza regressioni.
- [ ] CHANGELOG aggiornato.
