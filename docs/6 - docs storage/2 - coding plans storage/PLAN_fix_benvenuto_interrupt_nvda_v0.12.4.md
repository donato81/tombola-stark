---
type: plan
titolo: Fix definitivo benvenuto NVDA con focus stabilizzato e annuncio differito
feature: fix_benvenuto_interrupt_nvda
versione: 0.12.4
data_creazione: 2026-04-14
agent: Agent-Plan
status: READY
design_ref: docs/2 - projects/DESIGN_fix_benvenuto_interrupt_nvda.md
report_ref: docs/4 - reports/REPORT_ANALISI_fix_definitivo_benvenuto_nvda_2026-04-14.md
---

# PLAN — Fix definitivo benvenuto NVDA v0.12.4

## Executive Summary

- Tipo: fix accessibilita NVDA — terzo tentativo, root cause verificato
- Priorita: critica (blocker accessibilita)
- Branch suggerito: `feature/fix-benvenuto-callafter-v0.12.4`
- Versione target: v0.12.4
- Design di riferimento: [DESIGN_fix_benvenuto_interrupt_nvda.md](../2%20-%20projects/DESIGN_fix_benvenuto_interrupt_nvda.md) — REVIEWED
- Report analisi: [REPORT_ANALISI_fix_definitivo_benvenuto_nvda_2026-04-14.md](../4%20-%20reports/REPORT_ANALISI_fix_definitivo_benvenuto_nvda_2026-04-14.md)
- Piano precedente (deprecato): [PLAN_fix_benvenuto_interrupt_nvda_v0.12.3.md](PLAN_fix_benvenuto_interrupt_nvda_v0.12.3.md)

---

## Problema e Obiettivo

Il PLAN v0.12.3 ha introdotto `mostra_messaggio_benvenuto` con `interrompi=True`
ma non ha risolto il root cause reale: il `SetFocus()` sulla griglia avveniva
**dopo** la vocalizzazione, generando un evento nativo NVDA `gainFocus` che
sovrascriveva il parlato AO2 sul sintetizzatore condiviso.

Root cause definitivo (verificato nel report 2026-04-14):
- `_annuncia_benvenuto_iniziale` viene chiamato mentre il focus non e ancora stabile
- NVDA riceve l'annuncio nativo di focus immediatamente dopo l'inizio del benvenuto
- l'ultimo evento sul sintetizzatore condiviso vince: il gainFocus tronca il benvenuto

Fix definitivo (dalle decisioni architetturali D1-D4 del DESIGN REVIEWED):
1. `_pannello_griglia.SetFocus()` viene eseguito **prima** dell'emissione del benvenuto
2. Il benvenuto viene emesso con `wx.CallLater(350, self._annuncia_benvenuto_iniziale)`
3. Il metodo `_annuncia_benvenuto_iniziale` usa `interrupt=True` (gia presente dopo v0.12.3)
4. Nessuna modifica a dominio o backend TTS

---

## File coinvolti

| File | Operazione | Motivo |
|---|---|---|
| `bingo_game/ui/finestra_gioco.py` | MODIFY | refactor `_imposta_focus_iniziale`: SetFocus prima, poi CallLater(350) per il benvenuto |
| `tests/ui/test_finestra_gioco.py` | MODIFY | aggiornare test: verificare ordine SetFocus/CallLater + mock CallLater |

---

## Fasi sequenziali

### Fase 1 — Refactor `_imposta_focus_iniziale` in FinestraGioco

**File**: `bingo_game/ui/finestra_gioco.py`

**Obiettivo**: separare la stabilizzazione del focus dall'emissione del benvenuto.

**Operazioni**:

1. Individuare il metodo `_imposta_focus_iniziale`.

2. Rimuovere qualsiasi chiamata diretta a `renderer.mostra_messaggio_benvenuto`
   o a `_annuncia_benvenuto_iniziale` dalla sequenza sincona del metodo.

3. Spostare `_pannello_griglia.SetFocus()` come ultima istruzione sincrona
   del metodo, subito prima del CallLater.

4. Aggiungere come ultima riga del metodo:
   ```python
   wx.CallLater(350, self._annuncia_benvenuto_iniziale)
   ```

5. Creare (o verificare l'esistenza di) il metodo helper dedicato:
   ```python
   def _annuncia_benvenuto_iniziale(self) -> None:
       self._renderer.mostra_messaggio_benvenuto(self._testo_benvenuto)
   ```
   dove `_testo_benvenuto` e la stringa orientativa gia costruita.

**Sequenza target di `_imposta_focus_iniziale`**:
```
_avvio_silenzioso = True
_dispatch x3 (silenziosi)
_avvio_silenzioso = False
_aggiorna_griglie_visive()
_aggiorna_titolo_cartella()
_pannello_griglia.SetFocus()          <- focus reale, ultimo atto sincrono
wx.CallLater(350, _annuncia_benvenuto_iniziale)
```

**Commit atomico**: `fix(ui): stabilizza focus prima del benvenuto NVDA`

---

### Fase 2 — Aggiornare i test UI per il nuovo ordine SetFocus/CallLater

**File**: `tests/ui/test_finestra_gioco.py`

**Obiettivo**: verificare che la nuova sequenza sia rispettata e che il benvenuto
non venga piu chiamato direttamente in `_imposta_focus_iniziale`.

**Operazioni**:

1. Individuare i test esistenti che verificano il flusso di avvio
   (es. `test_imposta_focus_iniziale`, test che verificano `SetFocus`,
   test che verificano `mostra_messaggio_benvenuto`).

2. Aggiornare o aggiungere un test che verifica:
   - `_pannello_griglia.SetFocus()` viene chiamato prima di `wx.CallLater`
   - `wx.CallLater` viene chiamato con delay=350 e callable=`_annuncia_benvenuto_iniziale`
   - `mostra_messaggio_benvenuto` NON viene chiamato durante il corpo sincrono
     di `_imposta_focus_iniziale` (niente chiamate dirette)

3. Aggiungere un test che verifica che `_annuncia_benvenuto_iniziale` chiami
   `renderer.mostra_messaggio_benvenuto` con il testo orientativo atteso.

4. Usare `unittest.mock.patch('wx.CallLater')` per intercettare la schedulazione
   senza attendere i 350 ms nel test headless.

**Commit atomico**: `test(ui): aggiorna test FinestraGioco per CallLater e ordine focus`

---

### Fase 3 — Validazione sintattica e test suite

**Obiettivo**: zero regressioni prima del commit finale.

**Operazioni**:

1. Compilazione sintattica:
   ```
   python -m py_compile bingo_game/ui/finestra_gioco.py
   ```

2. Esecuzione test UI headless:
   ```
   pytest tests/ui/ -v
   ```

3. Verifica nessun `print()` introdotto:
   ```
   grep -r "print(" bingo_game/ui/finestra_gioco.py
   ```

4. Verifica type hints (se mypy e configurato):
   ```
   mypy bingo_game/ui/finestra_gioco.py --strict
   ```

**Commit atomico**: non necessario (validazione pre-commit, nessun file modificato)

---

### Fase 4 — Sync documentazione e changelog

**File**: `CHANGELOG.md`, `docs/API.md` (solo se cambiano signature pubbliche)

**Operazioni**:

1. Aggiungere voce `[Unreleased]` in `CHANGELOG.md`:
   ```
   ### Fixed
   - Fix definitivo benvenuto NVDA: SetFocus prima del parlato,
     annuncio differito con wx.CallLater(350) e interrupt=True (v0.12.4)
   ```

2. Verificare se `_annuncia_benvenuto_iniziale` e un metodo pubblico o privato.
   Se privato (prefisso `_`), non aggiornare `docs/API.md`.

3. Aggiornare `docs/ARCHITECTURE.md` se il bootstrap flow della finestra
   di gioco e descritto in un diagramma o in una sezione dedicata.

**Commit atomico**: `docs: sync changelog e architettura dopo fix benvenuto v0.12.4`

---

## Test Plan

### Unit test (headless, senza display)

| Test | File | Verifica |
|---|---|---|
| `test_imposta_focus_iniziale_ordine` | `tests/ui/test_finestra_gioco.py` | SetFocus prima di CallLater |
| `test_callafter_delay_350` | `tests/ui/test_finestra_gioco.py` | delay=350, callable=`_annuncia_benvenuto_iniziale` |
| `test_annuncia_benvenuto_chiama_renderer` | `tests/ui/test_finestra_gioco.py` | `mostra_messaggio_benvenuto` chiamato con testo corretto |
| `test_nessun_benvenuto_sincrono` | `tests/ui/test_finestra_gioco.py` | benvenuto non emesso nel corpo sincrono |

### Integration check (manuale con NVDA attivo)

1. Avviare l'applicazione con NVDA attivo
2. Confermare una partita dalla finestra di configurazione
3. Verificare che NVDA legga il messaggio orientativo completo senza troncamenti
4. Verificare che il focus sia gia sulla griglia quando il benvenuto inizia
5. Verificare che nessun annuncio successivo interrompa la lettura

---

## Note tecniche

- `mostra_messaggio_benvenuto` rimane in `renderer_wx.py` (introdotto in v0.12.3).
  Nessuna modifica necessaria al renderer se gia presente e usa `interrompi=True`.
- Se il metodo non esiste ancora nel renderer, la Fase 1 deve includerlo
  (ma il PLAN v0.12.3 lo aveva introdotto: verificare prima di duplicare).
- Il valore 350 ms e fisso per questa release. Futuri aggiustamenti potranno
  renderlo configurabile, ma non rientrano nel perimetro di v0.12.4.
