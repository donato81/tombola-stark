---
type: plan
titolo: Fix lettura benvenuto NVDA via interrupt — secondo tentativo
feature: fix_benvenuto_interrupt_nvda
versione: 0.12.3
data_creazione: 2026-04-14
agent: Agent-Plan
status: READY
design_ref: docs/2 - projects/DESIGN_fix_benvenuto_interrupt_nvda.md
report_ref: docs/4 - reports/REPORT_ANALISI_benvenuto_ancora_muto_2026-04-14.md
---

# PLAN — Fix lettura benvenuto NVDA via interrupt v0.12.3

## Executive Summary

- Tipo: fix accessibilita NVDA — secondo tentativo dopo G2
- Priorita: alta
- Branch suggerito: feature/fix-benvenuto-interrupt-nvda-v0.12.3
- Versione target: v0.12.3
- Design di riferimento: [DESIGN_fix_benvenuto_interrupt_nvda.md](../2%20-%20projects/DESIGN_fix_benvenuto_interrupt_nvda.md) — DRAFT
- Report tecnico: [REPORT_ANALISI_benvenuto_ancora_muto_2026-04-14.md](../4%20-%20reports/REPORT_ANALISI_benvenuto_ancora_muto_2026-04-14.md)

---

## Problema e Obiettivo

Le fix precedenti (G2, v0.12.2) hanno introdotto correttamente il flag
`_avvio_silenzioso` e rimosso il CallAfter annidato, ma NON hanno applicato
`interrompi=True` al momento di emettere il messaggio di benvenuto.
Il benvenuto si accoda agli annunci NVDA nativi di Show/SetFocus e non viene
mai raggiunto dall'utente.

Obiettivo: applicare interrupt=True sul benvenuto e spostare SetFocus per
ridurre il rumore NVDA pre-benvenuto, in modo che NVDA legga immediatamente
il messaggio orientativo all'ingresso nella finestra di gioco.

---

## File coinvolti

| File | Operazione | Motivo |
|---|---|---|
| bingo_game/ui/renderers/renderer_wx.py | MODIFY | nuovo metodo mostra_messaggio_benvenuto con interrompi=True |
| bingo_game/ui/finestra_gioco.py | MODIFY | rimuovi SetFocus dal costruttore; aggiorna _imposta_focus_iniziale |
| tests/ui/test_finestra_gioco.py | MODIFY | aggiorna test per nuova sequenza di chiamate |

---

## Fasi sequenziali

### Fase 1 — Aggiungere mostra_messaggio_benvenuto al renderer

**File**: `bingo_game/ui/renderers/renderer_wx.py`

**Posizione**: subito dopo il metodo `mostra_messaggio_sistema` (riga ~173).

**Operazioni**:

1. Aggiungere il metodo:

```python
def mostra_messaggio_benvenuto(self, testo: str) -> None:
    """Vocalizza un messaggio di ingresso finestra con interruzione della coda NVDA.

    Usare esclusivamente per messaggi orientativi all'ingresso in una nuova finestra,
    dove e necessario interrompere qualsiasi annuncio precedente in coda.
    NON usare per messaggi normali di gioco.
    """
    self._wx_aggiorna_output(testo)
    self._ultimo_annuncio = testo
    self._vocalizzatore.vocalizza_testo(testo, interrompi=True)
```

**Commit atomico**: `feat(renderer): aggiunge mostra_messaggio_benvenuto con interrupt`

---

### Fase 2 — Aggiornare FinestraGioco: SetFocus e benvenuto

**File**: `bingo_game/ui/finestra_gioco.py`

**Operazioni**:

1. Nel costruttore di `FinestraGioco.__init__`, rimuovere la riga:
   ```python
   self._pannello_griglia.SetFocus()
   ```
   (riga ~636, prima di `wx.CallAfter(self._imposta_focus_iniziale)`)

2. In `_imposta_focus_iniziale`, dopo `_aggiorna_titolo_cartella()`,
   modificare la chiamata da:
   ```python
   self._renderer.mostra_messaggio_sistema(
       "Sei nella finestra di gioco. ..."
   )
   ```
   a:
   ```python
   self._renderer.mostra_messaggio_benvenuto(
       "Sei nella finestra di gioco. "
       "Premi Inizia partita o Ctrl+Invio per estrarre il primo numero. "
       "Premi Ctrl+H per la guida ai tasti rapidi."
   )
   self._pannello_griglia.SetFocus()
   ```

Il SetFocus viene spostato come ultima istruzione dopo il benvenuto,
in modo che NVDA riceva il focus sulla griglia solo quando la coda e libera.

**Commit atomico**: `fix(ui): applica interrupt benvenuto e sposta SetFocus in FinestraGioco`

---

### Fase 3 — Aggiornare i test

**File**: `tests/ui/test_finestra_gioco.py`

**Operazioni**:

1. Verificare che il test esistente sull'annuncio iniziale rifletta la
   nuova sequenza: `mostra_messaggio_benvenuto` al posto di `mostra_messaggio_sistema`.

2. Aggiungere o aggiornare un test che verifichi che:
   - `mostra_messaggio_benvenuto` viene chiamato una volta sola a fine
     `_imposta_focus_iniziale`
   - `mostra_messaggio_sistema` NON viene chiamato durante `_imposta_focus_iniziale`
   - `SetFocus` viene chiamato dopo `mostra_messaggio_benvenuto`
     (verificabile tramite mock e ordine delle chiamate)

3. Verificare che nessun test esistente rompa a causa dello spostamento di SetFocus.

**Commit atomico**: `test(ui): aggiorna test benvenuto per interrupt e nuovo ordine SetFocus`

---

## Test Plan

### Automatici

```bash
python -m py_compile bingo_game/ui/renderers/renderer_wx.py
python -m py_compile bingo_game/ui/finestra_gioco.py
python -m py_compile tests/ui/test_finestra_gioco.py
python -m unittest tests/ui/test_finestra_gioco -v
```

### Manuali (con NVDA attivo)

1. Aprire la configurazione partita e avviare il gioco.
2. Verificare che NVDA legga immediatamente:
   "Sei nella finestra di gioco. Premi Inizia partita o Ctrl+Invio..."
3. Verificare che NON vengano letti prima annunci di navigazione
   (cartella, riga, colonna) ne il titolo finestra come messaggio separato.
4. Verificare che Escape, frecce e Ctrl+H funzionino correttamente
   dopo l'ingresso nella finestra.

---

## Rischi

- SetFocus spostato non deve alterare il comportamento del ciclo Tab.
- mostra_messaggio_benvenuto non deve essere riutilizzato fuori dal contesto
  di ingresso finestra.
- I test di sequenza su finestra_gioco sono parzialmente dipendenti da wx:
  usare mock granulare sul renderer per isolare le verifiche.

---

## Criteri di completamento

- [ ] WxRenderer ha il metodo mostra_messaggio_benvenuto con interrompi=True
- [ ] FinestraGioco non chiama SetFocus nel costruttore
- [ ] _imposta_focus_iniziale chiama mostra_messaggio_benvenuto poi SetFocus
- [ ] I test automatici passano senza regressioni
- [ ] Verifica manuale NVDA superata
