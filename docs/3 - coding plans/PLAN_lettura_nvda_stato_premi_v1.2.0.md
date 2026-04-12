---
type: plan
titolo: Piano implementazione lettura NVDA stato premi
feature: lettura_nvda_stato_premi
versione: 1.2.0
data_creazione: 2026-04-12
agent: Agent-Plan
status: READY
---

# PLAN — Lettura NVDA stato premi v1.2.0

## Executive summary

- Tipo: nuova feature accessibilità (Categoria C, keyboard-only)
- Priorità: alta — critica per utente non vedente
- Branch: `feature/lettura-nvda-stato-premi-v1.2.0`
- Versione target: v1.2.0
- Design di riferimento: [DESIGN_lettura_nvda_stato_premi_v1.2.0.md](../2%20-%20projects/DESIGN_lettura_nvda_stato_premi_v1.2.0.md) — REVIEWED

---

## Obiettivo

Aggiungere due tasti rapidi Categoria C (`Ctrl+G` e `Ctrl+I`) che
permettono al giocatore non vedente di rileggere con NVDA l'ultima
vittoria assegnata (tipo + nome vincitore) e il prossimo premio nella
sequenza della tombola, senza interrompere il flusso di gioco.

Il dato "vincitore dell'ultimo premio" transita in `verifica_premi()`
ma viene perso dopo ogni turno: la feature richiede di memorizzarlo
in un attributo `ultimo_premio_evento` su `Partita` (dominio).

---

## Fasi

### Fase 1 — Dominio: aggiunta attributo `ultimo_premio_evento`

**File coinvolti**: `bingo_game/partita.py` (MODIFY)

Operazioni:

1. In `Partita.__init__()`: aggiungere
   `self.ultimo_premio_evento: Optional[Dict[str, Any]] = None`
   dopo gli attributi `premi_gia_assegnati` e `premi_tipo_chiusi`
   (righe 203-204).
2. In `Partita.verifica_premi()`: dopo il ciclo di assegnazione
   candidati, se `nuovi_eventi` non è vuoto, aggiungere
   `self.ultimo_premio_evento = nuovi_eventi[-1]`
   (inserimento dopo riga 652, dentro il blocco `if nuovi_eventi:`).
3. Aggiungere `from typing import Optional, Dict, Any` se non già
   importato (verificare import esistenti).

Commit atomico: `feat(domain): aggiunge attributo ultimo_premio_evento a Partita`

---

### Fase 2 — Application: metodi `stato_premi()` e `dettaglio_premi()`

**File coinvolti**: `bingo_game/comandi_partita.py` (MODIFY)

Operazioni:

1. Aggiungere costante di classe a `ComandiGiocatoreUmano`:
   `_SEQUENZA_PREMI: list[str] = ["ambo", "terno", "quaterna", "cinquina", "tombola"]`
2. Aggiungere metodo `stato_premi(self) -> str`:
   - legge `self._partita.ultimo_premio_evento`
   - se `None`: usa template `UMANI_STATO_PREMI_NESSUNO`
   - altrimenti: usa template `UMANI_STATO_PREMI_SINTETICO`
   - calcola `prossimo_premio` iterando `_SEQUENZA_PREMI` vs
     `self._partita.premi_tipo_chiusi`; se tutti chiusi usa
     `UMANI_STATO_PREMI_TUTTI`
3. Aggiungere metodo `dettaglio_premi(self) -> str`:
   - se `premi_gia_assegnati` vuoto: restituisce
     "Nessun premio ancora assegnato."
   - altrimenti: costruisce elenco con `UMANI_DETTAGLIO_PREMI_HEADER`
     + righe `UMANI_DETTAGLIO_PREMI_VOCE` per ogni premio assegnato
   - iterazione in ordine `_SEQUENZA_PREMI` per output coerente

Commit atomico: `feat(application): aggiunge stato_premi e dettaglio_premi a ComandiGiocatoreUmano`

---

### Fase 3 — Eventi: nuovi codici template in `codici_output_ui_umani.py`

**File coinvolti**: `bingo_game/events/codici_output_ui_umani.py` (MODIFY)

Operazioni:

Aggiungere in coda alla sezione costanti esistente:

```python
UMANI_STATO_PREMI_SINTETICO = (
    "Ultimo premio: {ultimo_premio} vinto da {vincitore}. "
    "Prossimo: {prossimo_premio}."
)
UMANI_STATO_PREMI_NESSUNO = "Nessun premio ancora assegnato. Prossimo: {prossimo_premio}."
UMANI_STATO_PREMI_TUTTI = "Tutti i premi sono stati assegnati."
UMANI_DETTAGLIO_PREMI_HEADER = "Premi assegnati in questa partita:"
UMANI_DETTAGLIO_PREMI_VOCE = "{premio} - vinto da {vincitore} (cartella {cartella})"
```

Commit atomico: `feat(events): aggiunge codici template stato premi a CodiciOutputUiUmani`

---

### Fase 4 — Renderer: metodi `annuncia_stato_premi()` e `annuncia_dettaglio_premi()`

**File coinvolti**: `bingo_game/ui/renderers/renderer_wx.py` (MODIFY)

Operazioni:

1. Aggiungere `annuncia_stato_premi(self, testo: str) -> None`:
   - delega a `self.mostra_messaggio_sistema(testo)`
2. Aggiungere `annuncia_dettaglio_premi(self, testo: str) -> None`:
   - delega a `self.mostra_messaggio_sistema(testo)`

Nota: i metodi sono thin wrapper che incapsulano la semantica dell'azione
per mantenere la separation of concerns tra presentazione e vocalizzazione.

Commit atomico: `feat(presentation): aggiunge annuncia_stato_premi e annuncia_dettaglio_premi a WxRenderer`

---

### Fase 5 — Presentazione: handler `Ctrl+G` e `Ctrl+I` in `finestra_gioco.py`

**File coinvolti**: `bingo_game/ui/finestra_gioco.py` (MODIFY)

Operazioni:

1. In `_on_char_hook()`: aggiungere blocco per `Ctrl+G`:
   ```python
   if key == ord("G") and evt.ControlDown():
       if self._partita_in_corso:
           testo = self._comandi.stato_premi()
           self._renderer.annuncia_stato_premi(testo)
       return
   ```
2. In `_on_char_hook()`: aggiungere blocco per `Ctrl+I`:
   ```python
   if key == ord("I") and evt.ControlDown():
       if self._partita_in_corso:
           testo = self._comandi.dettaglio_premi()
           self._renderer.annuncia_dettaglio_premi(testo)
       return
   ```
3. Aggiornare la docstring/tabella binding in testa al file (riga ~33-38)
   aggiungendo le due voci Categoria C:
   - `Ctrl+G` — Rileggi ultima vittoria assegnata (sintetico)
   - `Ctrl+I` — Rileggi dettaglio premi assegnati (completo)

Commit atomico: `feat(presentation): aggiunge handler Ctrl+G e Ctrl+I per lettura NVDA stato premi`

---

### Fase 6 — Test plan

**File coinvolti**: `tests/unit/` (CREATE — nuovi file test)

Test unitari da creare:

- `tests/unit/test_partita_ultimo_premio_evento.py`
  - verifica che `ultimo_premio_evento` sia `None` all'avvio
  - verifica che venga aggiornato dopo `verifica_premi()` con almeno un vincitore
  - verifica che rimanga l'ultimo evento dopo più assegnazioni nello stesso turno

- `tests/unit/test_comandi_stato_premi.py`
  - `stato_premi()` con `ultimo_premio_evento = None` → testo "Nessun premio..."
  - `stato_premi()` con evento → testo formattato correttamente
  - `stato_premi()` con tutti i premi chiusi → testo "Tutti i premi..."
  - `dettaglio_premi()` con `premi_gia_assegnati` vuoto → fallback
  - `dettaglio_premi()` con premi → elenco multi-riga corretto

Test di integrazione (verifica manuale NVDA):
- Ctrl+G durante partita con nessun premio → voce corretta
- Ctrl+G durante partita con ambo assegnato → voce corretta
- Ctrl+I durante partita → elenco vocalizzato senza popup

Commit atomico: `test(unit): aggiunge test per ultimo_premio_evento e stato/dettaglio premi`

---

## File coinvolti

| Layer | File | Operazione |
|---|---|---|
| Domain | `bingo_game/partita.py` | MODIFY — attributo + aggiornamento in verifica_premi() |
| Application | `bingo_game/comandi_partita.py` | MODIFY — metodi stato_premi() e dettaglio_premi() |
| Events | `bingo_game/events/codici_output_ui_umani.py` | MODIFY — 5 nuovi codici template |
| Presentation | `bingo_game/ui/renderers/renderer_wx.py` | MODIFY — 2 thin wrapper |
| Presentation | `bingo_game/ui/finestra_gioco.py` | MODIFY — handler Ctrl+G, Ctrl+I, docstring |
| Tests | `tests/unit/test_partita_ultimo_premio_evento.py` | CREATE |
| Tests | `tests/unit/test_comandi_stato_premi.py` | CREATE |

---

## Criteri di completamento

- [ ] `Partita.ultimo_premio_evento` aggiornato correttamente dopo ogni `verifica_premi()`
- [ ] `ComandiGiocatoreUmano.stato_premi()` restituisce testo corretto nei 3 casi (nessuno, attivo, tutti)
- [ ] `ComandiGiocatoreUmano.dettaglio_premi()` restituisce elenco corretto (vuoto e con premi)
- [ ] I 5 codici template aggiunti a `codici_output_ui_umani.py`
- [ ] `Ctrl+G` e `Ctrl+I` intercettati in `EVT_CHAR_HOOK` senza side effect sul gioco
- [ ] NVDA vocalizza il testo senza aprire popup o finestre modali
- [ ] Tutti i test unitari passano (`pytest tests/unit/`)
- [ ] `python -m py_compile` su tutti i file modificati: zero errori
- [ ] `docs/API.md` aggiornato nella sezione "Categoria C" con le due nuove voci
