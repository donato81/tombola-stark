---
type: plan
titolo: Annuncio posizione focus dopo il benvenuto NVDA
feature: annuncio_posizione_focus_post_benvenuto_nvda
versione: 0.12.5
data_creazione: 2026-04-14
agent: Agent-Plan
status: READY
design_ref: docs/2 - projects/DESIGN_annuncio_posizione_focus_post_benvenuto_nvda.md
---

# PLAN — Annuncio posizione focus dopo il benvenuto NVDA v0.12.5

## Executive Summary

- Tipo: estensione accessibilita NVDA — completamento orientamento spaziale iniziale
- Priorita: alta (accessibilita — orientamento cartella/riga/colonna all'ingresso)
- Branch suggerito: `feature/annuncio-posizione-focus-nvda-v0.12.5`
- Versione target: v0.12.5
- Design di riferimento: [DESIGN_annuncio_posizione_focus_post_benvenuto_nvda.md](../2%20-%20projects/DESIGN_annuncio_posizione_focus_post_benvenuto_nvda.md) — REVIEWED
- Piano precedente correlato: [PLAN_fix_benvenuto_interrupt_nvda_v0.12.4.md](PLAN_fix_benvenuto_interrupt_nvda_v0.12.4.md)

---

## Problema e Obiettivo

Dopo il fix del benvenuto NVDA (v0.12.4), la finestra di gioco annuncia
correttamente il messaggio orientativo iniziale, ma l'utente non riceve un
annuncio esplicito della posizione logica iniziale sulla griglia
(cartella, riga, colonna).

Root cause: il boot silenziosa di `_imposta_focus_iniziale` stabilizza il focus
senza emettere la posizione corrente, e il benvenuto da solo non descrive dove
il cursore si trova sulla griglia.

Obiettivo: schedulare un secondo callback differito dopo `mostra_messaggio_benvenuto`
che invochi `self._comandi.stato_focus()` e inoltri l'evento risultante al renderer
esistente. Il renderer gestisce gia `EventoStatoFocusCorrente` e vocalizza
cartella/riga/colonna tramite il path event-driven standard.

Sequenza uditiva attesa al termine:

```
1. La finestra si apre; focus stabilizzato sulla griglia in modo silenzioso
2. NVDA esaurisce gli annunci nativi di show/focus
3. Benvenuto orientativo (primo annuncio applicativo)
4. Dopo delay controllato: "Cartella X, riga Y, colonna Z" (secondo annuncio)
```

---

## File coinvolti

| File | Operazione | Motivo |
|---|---|---|
| `bingo_game/ui/finestra_gioco.py` | MODIFY | aggiungere `_annuncia_posizione_focus_iniziale` e secondo `wx.CallLater` in `_annuncia_benvenuto_iniziale` |
| `tests/ui/test_finestra_gioco.py` | LIKELY MODIFY | verificare schedulazione secondo callback, dispatch `stato_focus()`, assenza duplicazione testuale |
| `CHANGELOG.md` | MODIFY | voce `[Unreleased]` in fase docs sync |
| `bingo_game/ui/renderers/renderer_wx.py` | NO CHANGE atteso | supporto `EventoStatoFocusCorrente` gia presente; modifiche solo se i test evidenziano necessita tecnica specifica |

---

## Fasi sequenziali

### Fase 1 — Secondo callback differito in `_annuncia_benvenuto_iniziale`

**File**: `bingo_game/ui/finestra_gioco.py`

**Obiettivo**: estendere `_annuncia_benvenuto_iniziale` per schedulare l'annuncio
della posizione focus senza alterare l'ordine del benvenuto.

**Operazioni**:

1. Aprire `bingo_game/ui/finestra_gioco.py` e individuare il metodo
   `_annuncia_benvenuto_iniziale`.

2. Verificare che il metodo non contenga gia una schedulazione per la posizione
   focus (check precauzionale per evitare duplicazione).

3. Aggiungere al fondo del metodo, dopo la chiamata a `mostra_messaggio_benvenuto`:
   ```python
   wx.CallLater(<delay_tuned>, self._annuncia_posizione_focus_iniziale)
   ```
   Valore di partenza consigliato per `<delay_tuned>`: 200 ms.
   Questo valore e empirico (vedi N1 — Note e Rischi): va validato con NVDA
   reale e regolato per evitare overlap con il parlato del benvenuto.

4. Creare il nuovo metodo helper dedicato:
   ```python
   def _annuncia_posizione_focus_iniziale(self) -> None:
      self._dispatch(self._comandi.stato_focus())
   ```
   Il metodo non costruisce stringhe testuali: delega interamente al path
   event-driven esistente per `EventoStatoFocusCorrente`.

5. Compilazione sintattica di verifica:
   ```
   python -m py_compile bingo_game/ui/finestra_gioco.py
   ```

**Struttura target post-modifica di `_annuncia_benvenuto_iniziale`**:

```
mostra_messaggio_benvenuto(self._testo_benvenuto)     <- benvenuto invariato
wx.CallLater(<delay_tuned>, _annuncia_posizione_focus_iniziale)  <- NUOVO
```

**Commit atomico**: `feat(ui): aggiungi annuncio posizione focus dopo benvenuto NVDA`

---

### Fase 2 — Aggiornare / aggiungere test UI per il secondo callback

**File**: `tests/ui/test_finestra_gioco.py`

**Obiettivo**: verificare automaticamente che il secondo callback sia presente,
che deleghi a `stato_focus()` e che non duplichi stringhe testuali nel benvenuto.

**Operazioni**:

1. Individuare i test esistenti che coprono `_annuncia_benvenuto_iniziale`
   (es. `test_annuncia_benvenuto_chiama_renderer`, test su `wx.CallLater`).

2. Aggiungere `test_annuncia_benvenuto_schedula_secondo_callafter`:
   - patcha `wx.CallLater`
   - chiama direttamente `_annuncia_benvenuto_iniziale()` sull'istanza mocked
   - verifica che `wx.CallLater` sia stato chiamato con
     callable=`self.finestra._annuncia_posizione_focus_iniziale` (o nome equivalente)

3. Aggiungere `test_annuncia_posizione_usa_stato_focus`:
   - mocka `self._comandi.stato_focus` per restituire un evento fittizio
   - chiama direttamente `_annuncia_posizione_focus_iniziale()`
   - verifica che `stato_focus()` sia stato chiamato esattamente una volta
   - verifica che `self._dispatch` sia stato chiamato con l'esito restituito

4. Aggiungere `test_nessun_testo_posizione_in_benvenuto`:
   - verifica che il testo del benvenuto (`_testo_benvenuto` o argomento di
     `mostra_messaggio_benvenuto`) non contenga le parole "riga", "colonna"
     costruite localmente nel metodo di benvenuto
   - questo garantisce l'assenza di duplicazione rispetto al path `stato_focus`

5. Usare `unittest.mock.patch('wx.CallLater')` per intercettare la schedulazione
   senza attendere ms reali nel contesto headless.

6. Eseguire la suite:
   ```
   pytest tests/ui/ -v
   ```

**Commit atomico**: `test(ui): aggiungi test secondo callafter e dispatch stato_focus`

---

### Fase 3 — Validazione sintattica, test suite e check manuale NVDA

**Obiettivo**: zero regressioni prima del commit finale; validazione accessibilita
percettiva obbligatoria su NVDA reale.

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

5. CHECK MANUALE NVDA — OBBLIGATORIO (non sostituibile da test automatici):
   - Avviare l'applicazione con NVDA attivo su Windows
   - Confermare una partita dalla finestra di configurazione
   - Verificare che il benvenuto sia il primo annuncio applicativo percepito
   - Verificare che dopo una pausa distinta venga letto l'annuncio della posizione
     (es. "Cartella 1, riga 1, colonna 1") come secondo messaggio separato
   - Verificare assenza di overlap percepibili o troncamenti del benvenuto
   - Se il delay produce overlap o pausa eccessiva, regolare `<delay_tuned>` e ripetere

**Commit atomico**: non necessario (validazione pre-commit, nessun file modificato)

---

### Fase 4 — Sync documentazione e changelog

**File**: `CHANGELOG.md`, `docs/ARCHITECTURE.md` (solo se il bootstrap flow e documentato)

**Operazioni**:

1. Aggiungere voce `[Unreleased]` in `CHANGELOG.md`:
   ```
   ### Added
   - Annuncio posizione focus iniziale dopo il benvenuto NVDA: secondo callback
     differito che richiama stato_focus() via pipeline event-driven esistente (v0.12.5)
   ```

2. Verificare se `_annuncia_posizione_focus_iniziale` e un metodo privato
   (prefisso `_`): se si, non aggiornare `docs/API.md`.

3. Aggiornare `docs/ARCHITECTURE.md` se il bootstrap flow della finestra di gioco
   e descritto in un diagramma o in una sezione dedicata con la sequenza CallLater.

**Commit atomico**: `docs: sync changelog dopo annuncio posizione focus v0.12.5`

---

## Test Plan

### Unit test (headless, senza display)

| Test | File | Verifica |
|---|---|---|
| `test_annuncia_benvenuto_schedula_secondo_callafter` | `tests/ui/test_finestra_gioco.py` | `wx.CallLater` chiamato con callable=`_annuncia_posizione_focus_iniziale` dopo il benvenuto |
| `test_annuncia_posizione_usa_stato_focus` | `tests/ui/test_finestra_gioco.py` | `stato_focus()` chiamato esattamente una volta e relativo esito passato a `self._dispatch(...)` |
| `test_nessun_testo_posizione_in_benvenuto` | `tests/ui/test_finestra_gioco.py` | testo benvenuto non contiene stringa posizione duplicata localmente |

### Integration check manuale con NVDA attivo — OBBLIGATORIO

I test automatici verificano il contratto applicativo (ordine di chiamata,
schedulazione, riuso di `stato_focus()`), ma non possono garantire la resa
audio percepita su NVDA reale. Il check manuale e obbligatorio prima del merge.

1. Avviare l'applicazione con NVDA attivo su Windows.
2. Confermare una partita dalla finestra di configurazione.
3. Verificare che NVDA legga il benvenuto orientativo come primo annuncio
   applicativo completo, senza troncamenti.
4. Verificare che dopo una pausa distinta venga letta la posizione iniziale
   (es. "Cartella 1, riga 1, colonna 1") come secondo annuncio separato.
5. Verificare assenza di sovrapposizioni o troncamenti percepibili tra i due messaggi.
6. Se necessario, regolare il valore di `<delay_tuned>` e ripetere la validazione.

---

## Note e Rischi

### N1 — Delay empirico non contrattuale

Il valore `<delay_tuned>` del secondo `wx.CallLater` va tarato su Windows con
NVDA attivo. Il valore di partenza proposto (200 ms) e una stima; potrebbe essere
necessario aumentarlo se il sintetizzatore fatica a completare il benvenuto prima
del secondo annuncio (R2 DESIGN), o ridurlo se la pausa percepita risulta eccessiva
(R3 DESIGN).

### N2 — Disponibilita di `stato_focus()` all'esecuzione del callback

Il callback `_annuncia_posizione_focus_iniziale` invoca `self._comandi.stato_focus()`.
Il PLAN v0.12.4 garantisce che i dispatch silenziosi iniziali precedano il benvenuto,
quindi lo stato focus e gia stabile al momento del secondo callback.
Verificare comunque che `ComandiPartita` sia completamente inizializzato nell'istante
in cui il callback viene eseguito (350 + delay_tuned ms dopo l'avvio sincrono).

### N3 — renderer_wx.py non dovrebbe essere modificato

Il renderer non richiede modifiche strutturali perche il supporto a
`EventoStatoFocusCorrente` e gia presente (D4 del DESIGN).
Se i test evidenziano la necessita di un adattamento tecnico minimo, il perimetro
va dichiarato esplicitamente prima del commit e documentato con motivazione tecnica.

### N4 — Copertura test parziale per design

I test automatici verificano: schedulazione, riuso di `stato_focus()`, assenza di
duplicazione testuale nel benvenuto. Non verificano la resa audio effettiva su NVDA.
La validazione manuale (Fase 3) non e opzionale.
