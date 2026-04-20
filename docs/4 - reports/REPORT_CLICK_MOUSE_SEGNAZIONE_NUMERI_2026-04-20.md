# REPORT — Click mouse per segnazione numeri sulla cartella

> **Data analisi**: 20 aprile 2026
> **Versione baseline**: 0.14.0-alpha
> **Autore analisi**: Agent-Analyze (Tombola Stark Framework)
> **Priorita del report**: bugfix UX / accessibilita utenti vedenti

---

## 1. Problema segnalato

Utenti vedenti che non usano screen reader non riescono a segnare i numeri
sulle cartelle possedute cliccando con il mouse. L'unico modo attualmente
funzionante e' la navigazione da tastiera (frecce + Spazio).

---

## 2. Analisi causa radice

### 2.1. Flusso attuale (solo tastiera)

Il percorso funzionante per segnare un numero e':

1. L'utente naviga con le frecce dentro `PannelloGriglia`
2. `PannelloGriglia._on_key_down` intercetta i tasti freccia e li inoltra
   a `ComandiGiocatoreUmano` (metodi `riga_su/giu`, `colonna_sinistra/destra`)
3. Il renderer (`WxRenderer`) aggiorna `self.numero_in_focus` tramite
   `_aggiorna_numero_in_focus_da_riga()` / `_aggiorna_numero_in_focus_da_colonna()`
4. Quando l'utente preme Spazio, `PannelloGriglia._on_key_down` chiama
   `FinestraGioco._ottieni_numero_in_focus()` che legge `renderer.numero_in_focus`
5. Il numero viene passato a `ComandiGiocatoreUmano.segna_numero(numero)`
6. L'esito ritorna come `EsitoAzione` e viene renderizzato dal renderer

### 2.2. Cosa manca per il click mouse

Analizzando i file coinvolti:

- [bingo_game/ui/finestra_gioco.py](../../bingo_game/ui/finestra_gioco.py) - classi `PannelloCartella`, `PannelloGriglia`, `FinestraGioco`
- [bingo_game/ui/renderers/renderer_wx.py](../../bingo_game/ui/renderers/renderer_wx.py) - classe `WxRenderer`
- [bingo_game/comandi_partita.py](../../bingo_game/comandi_partita.py) - classe `ComandiGiocatoreUmano`

**Non esiste nessun binding di evento mouse** in tutto il layer UI.
In particolare:

- `PannelloCartella` (linee 163-245 di finestra_gioco.py): le celle sono
  `wx.StaticText` create nel metodo `_build_ui()`. Nessuno dei 27 widget
  (3 righe x 9 colonne) ha un handler `EVT_LEFT_DOWN`, `EVT_LEFT_UP`
  o `EVT_LEFT_DCLICK`.

- `PannelloCartella` ha lo stile `wx.NO_BORDER` e il flag `wx.TAB_TRAVERSAL`
  rimosso esplicitamente, il che lo rende puramente visivo e non interattivo.

- `PannelloTabellone` (linee 108-160): stessa situazione, puramente visivo,
  nessun handler mouse.

- `FinestraGioco` (linee 590-810): il frame ha `EVT_CHAR_HOOK` e
  `EVT_CLOSE`, ma **nessun binding mouse** sul pannello cartella.

- Il metodo `FinestraGioco._ottieni_numero_in_focus()` (linee 1480-1490)
  dipende esclusivamente da `renderer.numero_in_focus`, che viene aggiornato
  solo durante la navigazione da tastiera tramite handler di eventi
  `EventoNavigazioneRiga` / `EventoNavigazioneColonna`.

### 2.3. Diagramma del gap

```
Click su cella cartella
  -> wx.StaticText riceve l'evento nativo wx
  -> NESSUN handler lo intercetta
  -> L'evento viene ignorato silenziosamente
  -> Il numero non viene segnato
```

---

## 3. Proposta di modifica

### 3.1. Strategia generale

Aggiungere un handler `EVT_LEFT_DOWN` su ciascuna cella `wx.StaticText` di
`PannelloCartella`, che:

1. Determina quale numero corrisponde alla cella cliccata
2. Notifica `FinestraGioco` del click
3. `FinestraGioco` chiama `segna_numero()` con il numero identificato

Questa modifica e' **additiva**: non altera nessun binding tastiera esistente,
nessun flusso di navigazione, nessun handler gia' presente.

### 3.2. Modifiche per file

#### File 1: bingo_game/ui/finestra_gioco.py — classe PannelloCartella

**Cosa cambia**: Aggiungere un attributo `_callback_click` e un handler mouse.

- Nel metodo `__init__`, accettare un parametro opzionale `on_click_numero`
  (callable che riceve un `int`), salvandolo come `self._callback_click`.
- Nel metodo `_build_ui()`, per ogni cella `wx.StaticText` creata, aggiungere
  il binding: `cell.Bind(wx.EVT_LEFT_DOWN, self._on_cella_click)`.
- Aggiungere il metodo `_on_cella_click(self, event: wx.MouseEvent)`:
  - Identifica la cella sorgente con `event.GetEventObject()`
  - Cerca il numero nella `_mappa_celle_numero` (dizionario inverso)
  - Se trovato e `_callback_click` e' definito, lo invoca con il numero
  - Chiama `event.Skip()` per non bloccare altri handler

**Righe interessate**: circa 163-200 (`__init__`, `_build_ui`), nuovi metodi dopo linea 300.

Esempio di implementazione handler:

```python
def _on_cella_click(self, event: wx.MouseEvent) -> None:
    """Handler click sinistro su una cella della cartella."""
    cella = event.GetEventObject()
    # Ricerca inversa: trova il numero associato alla cella cliccata
    for numero, widget in self._mappa_celle_numero.items():
        if widget is cella:
            if self._callback_click is not None:
                self._callback_click(numero)
            break
    event.Skip()
```

#### File 2: bingo_game/ui/finestra_gioco.py — classe FinestraGioco

**Cosa cambia**: Passare il callback al PannelloCartella e gestire il click.

- Nella creazione di `self._pannello_cartella` in `_build_ui()` (circa linea 700),
  passare un callback: `on_click_numero=self._on_click_numero_cartella`.
- Aggiungere il metodo `_on_click_numero_cartella(self, numero: int)`:
  - Verifica che la partita sia in fase `attesa_reclami` (segnazione consentita
    solo quando c'e' un numero estratto e la finestra d'azione e' aperta)
  - Chiama `self._dispatch(self._comandi.segna_numero(numero))`
  - Aggiorna le griglie visive dopo la segnazione

**Righe interessate**: circa 700 (creazione pannello), nuovo metodo dopo linea 1610.

Esempio di implementazione:

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

#### File 3: nessuna modifica necessaria

I file seguenti **non richiedono modifiche**:

- `comandi_partita.py`: il metodo `segna_numero(numero)` accetta gia' un `int`
  direttamente, non dipende dal tipo di input (tastiera o mouse).
- `renderer_wx.py`: `_handle_segnazione_numero` e' gia' generico, renderizza
  l'evento `EventoSegnazioneNumero` indipendentemente dall'origine.
- `cartella.py`: la logica di dominio e' gia' completa.
- `giocatore_umano.py`: `segna_numero_manuale` e' gia' il punto di ingresso
  corretto per la segnazione.

### 3.3. Vincoli di compatibilita

- **Accessibilita NVDA**: nessun impatto. I binding mouse non interferiscono
  con `EVT_KEY_DOWN` su `PannelloGriglia`. Lo screen reader continua a
  funzionare esattamente come prima perche' il `PannelloCartella` rimane
  non-focalizzabile e non partecipa al ciclo TAB_TRAVERSAL.

- **Navigazione tastiera**: invariata. Il `PannelloGriglia` mantiene tutti
  i binding Categoria A. `numero_in_focus` continua a funzionare per Spazio.

- **Timer e fasi turno**: il guard `fase_turno_ui != "attesa_reclami"` nel
  nuovo handler garantisce che il click funzioni solo durante la finestra
  d'azione, coerente col funzionamento attuale del tasto Spazio.

- **Lampeggio celle**: `_on_cella_click` chiama `event.Skip()` quindi non
  interferisce con eventuali animazioni in corso.

---

## 4. Stima impatto

- File modificati: 1 (finestra_gioco.py)
- Classi modificate: 2 (PannelloCartella, FinestraGioco)
- Metodi nuovi: 2 (`_on_cella_click`, `_on_click_numero_cartella`)
- Metodi modificati: 2 (`PannelloCartella.__init__`, `FinestraGioco._build_ui`)
- Righe aggiunte stimate: circa 30-40
- Righe modificate stimate: circa 3-5

---

## 5. Test consigliati

- Test manuale: click sinistro su un numero presente in cartella durante
  fase "attesa_reclami" → il numero deve risultare segnato.
- Test manuale: click su cella vuota ("-") → nessuna azione.
- Test manuale: click durante fase "attesa_estrazione" → messaggio informativo.
- Test manuale: click durante pausa → nessuna azione.
- Test regressione tastiera: verificare che Spazio continui a funzionare
  identicamente dopo la modifica.
- Test regressione NVDA: verificare che la navigazione vocale non sia alterata.

---

## 6. Documentazione da aggiornare

- `docs/API.md`: aggiungere documentazione per i nuovi metodi pubblici
  se esposti nell'interfaccia.
- `CHANGELOG.md`: voce sotto [Unreleased] → Added: "Segnazione numeri
  cartella con click del mouse".

---

## 7. Prossimo passo consigliato

Delegare l'implementazione ad **Agent-Code** con riferimento a questo report.
La modifica e' contenuta e non richiede ne' design architetturale ne' piano
multi-commit.
