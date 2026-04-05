---
type: plan
feature: hotkey_ctrl_p_ctrl_f_feedback
agent: Agent-Plan
status: DRAFT
version: v0.9.5
design_ref: docs/2 - projects/DESIGN_hotkey_ctrl_p_ctrl_f_feedback.md
date: 2026-04-05
---

# PLAN — Correzione hotkey Ctrl+P e Ctrl+F con feedback accessibile

## Executive Summary

Tipo intervento: fix accessibilità layer Presentation, correzione boundary applicativo e comportamento dialog
Priorità: P1 — feedback da tastiera bloccante per NVDA e JAWS
Branch: fix/hotkey-ctrl-p-ctrl-f-feedback
Versione di riferimento: v0.9.5
Scope: due correzioni distinte e atomiche nella UI wx.
Ctrl+P viene corretto per delegare la dichiarazione di fine turno al boundary
applicativo `ComandiGiocatoreUmano.dichiara_fine_turno()` e per emettere un feedback
immediato e idempotente su `mostra_messaggio_sistema`.
Ctrl+F viene corretto per mantenere `DialogoRicercaNumero` aperto dopo la ricerca,
introducendo un'area di risultato interna stabilee accessibile, con chiusura solo
esplicita da parte dell'utente.
Vincoli: nessuna nuova regola di dominio; i test esistenti non devono rompersi;
nessun cambio alla logica di estrazione o di verifica premi.

## Problema e Obiettivo

### Problema — Ctrl+P in fase attesa_reclami

Il gestore `_on_pulsante_principale` nella fase `attesa_reclami` accede
direttamente all'oggetto `GiocatoreUmano` recuperato da `ComandiSistema`,
chiamando `umano.dichiara_fine_turno()` senza passare dal boundary applicativo
`ComandiGiocatoreUmano`. Conseguenze:
- Accoppiamento presentation-domain che aggira il contratto di ComandiGiocatoreUmano.
- Nessun feedback immediato emesso quando la dichiarazione è registrata.
- Silenzio totale quando il turno era già dichiarato (idempotenza muta).

### Problema — Ctrl+F con chiusura automatica del dialog

`DialogoRicercaNumero._on_cerca` chiama `self.EndModal(wx.ID_OK)` subito dopo
aver invocato `self._renderer.render_esito(esito)`. Conseguenze:
- Il dialog si chiude prima che NVDA/JAWS abbia annunciato l'esito.
- Il focus ritorna alla griglia mentre l'utente non ha ancora letto il risultato.
- L'esito è disponibile solo nel log della finestra madre, invisibile al focus corrente.

### Obiettivo

Garantire che ogni pressione di Ctrl+P e Ctrl+F produca un riscontro percepibile
subito, nel contesto che mantiene il focus, senza che il focus cambi prima che
l'informazione sia stata resa disponibile all'utente.

## File coinvolti

- [bingo_game/comandi_partita.py](../../bingo_game/comandi_partita.py) — MODIFY
  Aggiungere metodo `turno_gia_dichiarato() -> bool` in `ComandiGiocatoreUmano`.
  Il metodo legge `self._giocatore.turno_dichiarato_concluso` in modo None-safe
  (ritorna `False` se nessun giocatore umano è presente).

- [bingo_game/ui/finestra_gioco.py](../../bingo_game/ui/finestra_gioco.py) — MODIFY
  In `_on_pulsante_principale`, branch `attesa_reclami`:
  sostituire l'accesso diretto a `umano` con le chiamate ai metodi
  `self._comandi.turno_gia_dichiarato()` e `self._comandi.dichiara_fine_turno(self._partita)`;
  aggiungere feedback `mostra_messaggio_sistema` per entrambi i casi
  (dichiarazione nuova e dichiarazione già registrata).

- [bingo_game/ui/dialogo_ricerca.py](../../bingo_game/ui/dialogo_ricerca.py) — MODIFY
  Aggiungere widget `self._lbl_risultato: wx.StaticText` nell'area del dialog.
  Rimuovere `self.EndModal(wx.ID_OK)` dalla fine di `_on_cerca`.
  Aggiornare `_lbl_risultato` con il testo dell'esito dopo ogni ricerca.
  Aggiungere un elemento di chiusura esplicita (pulsante "Chiudi" o istruzione Escape).
  Regolare la dimensione del dialog per ospitare l'area risultato.

- [tests/unit/test_umano_dichiara_fine_turno.py](../../tests/unit/test_umano_dichiara_fine_turno.py) — MODIFY
  Aggiungere test su `ComandiGiocatoreUmano.turno_gia_dichiarato()`:
  stato False prima della dichiarazione, True dopo, False con giocatore assente.

- [tests/unit/test_finestra_gioco_shortcuts.py](../../tests/unit/test_finestra_gioco_shortcuts.py) — MODIFY
  Aggiungere test su `_on_pulsante_principale` in fase `attesa_reclami`:
  verifica che il messaggio di conferma sia emesso alla prima dichiarazione;
  verifica che il messaggio idempotente sia emesso se il turno era già dichiarato.

- [tests/unit/test_dialogo_ricerca_persistente.py](../../tests/unit/test_dialogo_ricerca_persistente.py) — CREATE
  Verificare, tramite mock di `EndModal`, che `_on_cerca` non chiuda il dialog
  dopo la ricerca. Verificare che `_lbl_risultato` venga aggiornato con il testo
  dell'esito restituito dal renderer.

## Fasi sequenziali

### Fase 1 — Aggiungere `turno_gia_dichiarato` nel boundary applicativo

File: `bingo_game/comandi_partita.py`

Aggiungere in `ComandiGiocatoreUmano` il metodo:

```python
def turno_gia_dichiarato(self) -> bool:
    """Ritorna True se il giocatore umano ha già dichiarato fine turno."""
    if self._giocatore is None:
        return False
    return self._giocatore.turno_dichiarato_concluso
```

Il metodo è puramente read-only sul dominio. Non modifica stato.
Questa fase è atomica e committable da sola, permettendo alla Fase 2
di usare il nuovo helper senza accoppiamento diretto al dominio.

Criteri di completamento:
- Il metodo è presente in `ComandiGiocatoreUmano`.
- `py_compile` su `comandi_partita.py` non produce errori.

### Fase 2 — Correggere `_on_pulsante_principale` per Ctrl+P

File: `bingo_game/ui/finestra_gioco.py`

Nel branch `attesa_reclami` di `_on_pulsante_principale`, sostituire:

```python
# Codice attuale — accesso diretto al dominio
umano = self._comandi_sistema.ottieni_giocatore_umano(self._partita)
if umano is not None and not umano.turno_dichiarato_concluso:
    umano.dichiara_fine_turno()
self._controlla_tutti_pronti()
```

con:

```python
# Codice nuovo — boundary corretto con feedback immediato
if self._comandi.turno_gia_dichiarato():
    self._renderer.mostra_messaggio_sistema(
        "Hai già dichiarato la fine del tuo turno. Attendo gli altri giocatori."
    )
else:
    self._comandi.dichiara_fine_turno(self._partita)
    self._renderer.mostra_messaggio_sistema(
        "Turno dichiarato concluso. Attendo gli altri giocatori."
    )
self._controlla_tutti_pronti()
```

Regole:
- `_controlla_tutti_pronti()` è chiamato in entrambi i casi per permettere
  l'avanzamento se tutti i giocatori sono pronti.
- I testi dei messaggi devono essere brevi, lineari e terminare senza punteggiatura
  eccedente per facilitare la lettura NVDA.
- Il recupero diretto di `umano` tramite `ottieni_giocatore_umano` in questo
  contesto è rimosso: la verifica sullo stato dichiarazione passa solo dal boundary.

Criteri di completamento:
- Nessun accesso diretto a `umano.turno_dichiarato_concluso` in questo branch.
- `_on_pulsante_principale` usa solo `self._comandi` e `self._renderer`.
- `py_compile` su `finestra_gioco.py` non produce errori.

### Fase 3 — Correggere `DialogoRicercaNumero` per Ctrl+F

File: `bingo_game/ui/dialogo_ricerca.py`

Step 3a — Aggiungere l'area risultato interna in `_build_ui`:
- Aggiungere `wx.StaticText` con `label=""` etichettato "Risultato ricerca:"
  o simile, posizionato sotto il pulsante Cerca.
- Salvare il riferimento come `self._lbl_risultato`.
- Aggiungere un pulsante "Chiudi" che chiama `self.EndModal(wx.ID_CANCEL)`.
- Aumentare l'altezza del dialog da 160 a ~230 per ospitare i nuovi widget.

Step 3b — Aggiornare `_on_cerca` per non chiudere il dialog:
- Rimuovere la riga `self.EndModal(wx.ID_OK)` dalla fine di `_on_cerca`.
- Dopo `self._renderer.render_esito(esito)`, determinare il testo da mostrare
  (`trovato` / `non trovato` / messaggio di errore) e chiamare
  `self._lbl_risultato.SetLabel(testo_esito)`.
- Il focus dopo la ricerca rimane nell'input del dialog
  (opzione preferita per permettere ricerche successive senza azioni extra).

Step 3c — Aggiornare il docstring del dialog:
- Rimuovere il riferimento alla "chiusura automatica" dal docstring della classe.
- Descrivere la nuova funzionalità: dialog persistente, area risultato,
  chiusura esplicita tramite Escape o pulsante Chiudi.

Criteri di completamento:
- `_on_cerca` non chiama `EndModal` direttamente.
- Il dialog rimane aperto dopo la ricerca.
- `_lbl_risultato` contiene il testo aggiornato dell'esito.
- `py_compile` su `dialogo_ricerca.py` non produce errori.

### Fase 4 — Test unitari sui comportamenti accessibili

File:
- `tests/unit/test_umano_dichiara_fine_turno.py` (MODIFY)
- `tests/unit/test_finestra_gioco_shortcuts.py` (MODIFY)
- `tests/unit/test_dialogo_ricerca_persistente.py` (CREATE)

Step 4a — `test_umano_dichiara_fine_turno.py`:
Aggiungere classe `TestComandiGiocatoreUmanoDichiarazioneTurno` con:
- `test_turno_gia_dichiarato_false_prima_di_dichiarare`: verifica False iniziale.
- `test_turno_gia_dichiarato_true_dopo_dichiarare`: verifica True dopo dichiarazione.
- `test_turno_gia_dichiarato_senza_giocatore_ritorna_false`: verifica None-safe.

Step 4b — `test_finestra_gioco_shortcuts.py`:
Aggiungere (nella classe esistente o in classe separata) test su
`_on_pulsante_principale` con `_fase_turno_ui = "attesa_reclami"`:
- `test_ctrl_p_attesa_reclami_emette_conferma_prima_dichiarazione`: verifica che
  `mostra_messaggio_sistema` sia chiamato con testo contenente "concluso".
- `test_ctrl_p_attesa_reclami_emette_messaggio_idempotente`: imposta
  `turno_gia_dichiarato` → True, verifica che `mostra_messaggio_sistema`
  sia chiamato con testo contenente "già dichiarato".
- In entrambi i casi verificare che `_controlla_tutti_pronti` sia chiamato.

Step 4c — `test_dialogo_ricerca_persistente.py`:
Creare la suite con il pattern `__new__` già usato in altri test wx:
- `test_on_cerca_non_chiama_end_modal`: mock di `EndModal`; verifica che
  dopo `_on_cerca` `EndModal` non sia stato chiamato.
- `test_on_cerca_aggiorna_lbl_risultato`: verifica che `_lbl_risultato.SetLabel`
  sia chiamato con il testo dell'esito dopo la ricerca.

Criteri di completamento:
- Tutti e tre i file passano `python -m unittest` senza errori.
- Nessun test esistente regredisce.

## Test Plan

### Scope della copertura

| Comportamento | File di test | Tipo |
|---|---|---|
| `turno_gia_dichiarato()` False/True/None-safe | test_umano_dichiara_fine_turno | unit boundary |
| Ctrl+P prima dichiarazione, messaggio "concluso" | test_finestra_gioco_shortcuts | unit UI mock |
| Ctrl+P idempotente, messaggio "già dichiarato" | test_finestra_gioco_shortcuts | unit UI mock |
| `_controlla_tutti_pronti` chiamato in entrambi i percorsi | test_finestra_gioco_shortcuts | unit UI mock |
| `_on_cerca` non chiude il dialog | test_dialogo_ricerca_persistente | unit UI mock |
| `_lbl_risultato` aggiornato dopo ricerca | test_dialogo_ricerca_persistente | unit UI mock |

### Strategia di isolamento

Tutti i test wx usano il pattern `__new__` + mock degli attributi di istanza
già consolidato in `test_finestra_gioco_shortcuts.py`.
`wx` viene importato con `try/except`; l'intera suite è decorata
`@unittest.skipIf(wx is None, "wxPython non disponibile")`.

### Pre-commit validation attesa

```
python -m py_compile bingo_game/comandi_partita.py
python -m py_compile bingo_game/ui/finestra_gioco.py
python -m py_compile bingo_game/ui/dialogo_ricerca.py
python -m unittest tests/unit/test_umano_dichiara_fine_turno -v
python -m unittest tests/unit/test_finestra_gioco_shortcuts -v
python -m unittest tests/unit/test_dialogo_ricerca_persistente -v
```

### Test di regressione attesi stabili

```
python -m unittest tests/unit/test_ciclo_turno_v2_bot_declaration -v
python -m unittest tests/unit/test_ciclo_turno_v2_tutti_pronti -v
python -m unittest tests/unit/test_ciclo_turno_v2_timeout_umano -v
```
