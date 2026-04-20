---
type: design
titolo: Click mouse per segnazione numeri sulla cartella
data_creazione: 2026-04-20
agent: Agent-Design
status: REVIEWED
feature: click_mouse_segnazione
---

## Obiettivo

Abilitare la segnazione dei numeri sulla cartella tramite click sinistro del mouse, senza alterare la navigazione da tastiera o l'accessibilità NVDA. La modifica è additiva: nessun comportamento esistente viene rimosso o alterato.

## Contesto

Fix post-alpha segnalata da utenti vedenti che non usano screen reader. Versione baseline: 0.14.0-alpha.

Attualmente l'unico metodo per segnare un numero è la navigazione da tastiera (frecce + Spazio tramite `PannelloGriglia`). Il click sinistro del mouse su una cella della cartella viene ignorato silenziosamente: nessun binding mouse è presente in tutto il layer UI.

```
Click su cella cartella
  -> wx.StaticText riceve l'evento nativo wx
  -> NESSUN handler lo intercetta
  -> L'evento viene ignorato silenziosamente
  -> Il numero non viene segnato
```

## Componenti coinvolti

- `bingo_game/ui/finestra_gioco.py`
  - Classe `PannelloCartella`: aggiunta binding `EVT_LEFT_DOWN` sulle celle e handler `_on_cella_click`
  - Classe `FinestraGioco`: aggiunta callback `_on_click_numero_cartella` e passaggio del callback al `PannelloCartella` in `_build_ui()`

## Dipendenze

- `ComandiGiocatoreUmano.segna_numero(numero: int)` è già il punto di ingresso corretto per la segnazione; non richiede modifiche.
- `WxRenderer._handle_segnazione_numero` gestisce già l'esito `EventoSegnazioneNumero` in modo generico, indipendente dall'origine (tastiera o mouse).
- `_mappa_celle_numero` (dizionario `wx.StaticText → int`) già presente in `PannelloCartella`, usato per la ricerca inversa durante il click.

Nessuna modifica al dominio o all'infrastruttura. File non modificati: `comandi_partita.py`, `renderer_wx.py`, `cartella.py`, `giocatore_umano.py`.

## Rischi

Nessun rischio rilevante. La modifica è interamente additiva:

- Nessuna modifica al dominio.
- Nessuna modifica al controller.
- Nessun binding esistente viene rimosso o sovrascritto.
- Stima: 1 file modificato, 2 classi coinvolte, 2 nuovi metodi, circa 30-40 righe aggiunte e 3-5 righe modificate.

## Vincoli accessibilità NVDA

Nessun impatto sull'accessibilità:

- `PannelloCartella` rimane non-focalizzabile e non partecipa al ciclo `TAB_TRAVERSAL`.
- I binding `EVT_LEFT_DOWN` sulle celle `wx.StaticText` non interferiscono con `EVT_KEY_DOWN` su `PannelloGriglia`.
- `_on_cella_click` chiama `event.Skip()`, garantendo che nessun altro handler venga bloccato e che eventuali animazioni (lampeggio celle) non vengano interrotte.
- NVDA continua a navigare e annunciare gli elementi esattamente come prima.

## Approccio tecnico

### Modifica 1 — `PannelloCartella` (finestra_gioco.py, righe ~163-200 e nuovi metodi dopo ~300)

- `__init__`: accettare parametro opzionale `on_click_numero: Callable[[int], None] | None = None`, salvato come `self._callback_click`.
- `_build_ui()`: per ogni cella `wx.StaticText`, aggiungere il binding `cell.Bind(wx.EVT_LEFT_DOWN, self._on_cella_click)`.
- Nuovo metodo `_on_cella_click(self, event: wx.MouseEvent) -> None`:

```python
def _on_cella_click(self, event: wx.MouseEvent) -> None:
    """Handler click sinistro su una cella della cartella."""
    cella = event.GetEventObject()
    for numero, widget in self._mappa_celle_numero.items():
        if widget is cella:
            if self._callback_click is not None:
                self._callback_click(numero)
            break
    event.Skip()
```

### Modifica 2 — `FinestraGioco` (finestra_gioco.py, riga ~700 e nuovo metodo dopo ~1610)

- `_build_ui()`: passare il callback alla creazione di `self._pannello_cartella`:
  `on_click_numero=self._on_click_numero_cartella`.
- Nuovo metodo `_on_click_numero_cartella(self, numero: int) -> None`:

```python
def _on_click_numero_cartella(self, numero: int) -> None:
    """Handler per click mouse su un numero della cartella visiva."""
    if self._comandi_sistema.is_terminata(self._partita):
        return
    if self._in_pausa:
        return
    if self._fase_turno_ui != "attesa_reclami":
        self._renderer.mostra_messaggio_sistema(
            "Puoi segnare i numeri solo dopo l'estrazione."
        )
        return
    self._dispatch(self._comandi.segna_numero(numero))
    self._aggiorna_griglie_visive()
```

Il guard sulla fase `"attesa_reclami"` garantisce coerenza con il comportamento attuale del tasto Spazio: la segnazione è consentita solo quando un numero è stato estratto e la finestra d'azione è aperta.

## Coding plans correlati

- `PLAN_click_mouse_segnazione_v0.14.1.md` — da creare in `docs/3 - coding plans/`
