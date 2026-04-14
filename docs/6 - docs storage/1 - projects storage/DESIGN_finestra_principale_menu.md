---
type: design
feature: finestra_principale_menu
agent: Agent-Design
status: REVIEWED
version: v1.1.0
date: 2026-04-09
report_ref: docs/4 - reports/REPORT_ANALISI_finestra_principale_menu_2026-04-09.md
---

# DESIGN — FinestraPrincipale (Menu Principale)

## 1. Idea in 3 righe

Introduce `FinestraPrincipale`, un frame wxPython che funge da punto di ingresso
navigazionale dell'applicazione Tombola Stark. Sostituisce l'apertura diretta
di `FinestraConfigurazione` da `main.py`, aggiungendo voci menu (Nuova partita,
Impostazioni, Guida, Esci) e un pulsante "Torna al menu principale" in
`FinestraGioco` attivabile solo a partita terminata.

---

## 2. Obiettivo

Questa feature introduce i seguenti comportamenti:

- L'utente vede un menu principale all'avvio dell'applicazione, prima di
  accedere alla configurazione.
- Da lì può avviare una nuova partita, esplorare voci placeholder (Impostazioni,
  Guida) o uscire dall'applicazione.
- Al termine di una partita, può tornare al menu principale premendo un pulsante
  dedicato, senza dover riavviare il programma.
- Il ciclo di vita dell'applicazione (`wx.App.MainLoop`) è gestito correttamente
  anche in presenza di finestre nascoste.

---

## 3. Attori e Concetti

| Attore / Concetto | Ruolo |
|---|---|
| `FinestraPrincipale` | Nuovo frame menu principale. Primo frame aperto da `main.py`. |
| `FinestraConfigurazione` | Frame esistente configurazione. Aperto da `FinestraPrincipale` su "Nuova partita". |
| `FinestraGioco` | Frame esistente di gioco. Modificato: aggiunge pulsante "Torna al menu principale". |
| `WxRenderer` | Renderer wxPython condiviso. Aggiorna `_finestra` ad ogni transizione. Non modificato strutturalmente. |
| `Vocalizzatore` | Backend TTS. Invariato. |
| `main.py` | Entry point. Modifica minima: apre `FinestraPrincipale` invece di `FinestraConfigurazione`. |

---

## 4. Flusso target completo

```
python main.py
  ↓
main():
  wx.App()
  Vocalizzatore()
  WxRenderer (via __new__ bypass)
  FinestraPrincipale(renderer=renderer)
    ↓ renderer.aggiorna_finestra(FinestraPrincipale)
    ↓ FinestraPrincipale.Show()
    │
    ├─ [utente: "Nuova partita"]
    │     FinestraConfigurazione(renderer=renderer, parent_frame=self)
    │       ↓ renderer.aggiorna_finestra(FinestraConfigurazione)
    │       ↓ FinestraPrincipale.Hide()
    │       ↓ [utente configura e avvia]
    │       FinestraGioco(partita, renderer, finestra_principale=FinestraPrincipale)
    │         ↓ renderer.aggiorna_finestra(FinestraGioco)
    │         ↓ renderer.imposta_widget_log(log_ctrl)
    │         ↓ FinestraConfigurazione.Hide()
    │         ↓ [gioco fino a tombola]
    │         ↓ partita_terminata = True
    │         ↓ btn_principale.Disable()
    │         ↓ btn_torna_menu.Enable() + btn_torna_menu.Show()
    │         │
    │         └─ [utente: "Torna al menu principale"]
    │               renderer.imposta_widget_log(None)
    │               FinestraGioco.Hide()
    │               FinestraPrincipale.Show()
    │               renderer.aggiorna_finestra(FinestraPrincipale)
    │
    ├─ [utente: "Impostazioni"]
    │     renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")
    │
    ├─ [utente: "Guida"]
    │     renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")
    │
    └─ [utente: "Esci"]
          wx.GetApp().ExitMainLoop()

app.MainLoop() ← blocca qui finché ExitMainLoop() non viene chiamato
  ↓
GameLogger.shutdown()
```

---

## 5. Componenti da creare

### `bingo_game/ui/finestra_principale.py`

Classe: `FinestraPrincipale(wx.Frame)`

Parametri `__init__`:

```
__init__(
    self,
    renderer: WxRenderer,
    parent: wx.Window | None = None
) -> None
```

Metodi principali attesi:

| Metodo | Responsabilità |
|---|---|
| `__init__` | Salva `renderer`, chiama `super().__init__()` con titolo `"Tombola Stark — Menu principale"`, chiama `_build_ui()`, chiama `renderer.aggiorna_finestra(self)`. |
| `_build_ui(self) -> None` | Costruisce la sizer verticale con i quattro pulsanti nell'ordine: Nuova partita, Impostazioni, Guida, Esci. Chiama `SetFocus()` sul primo pulsante a fine metodo. |
| `_on_nuova_partita(self, event: wx.Event) -> None` | Crea `FinestraConfigurazione(renderer=self._renderer, parent_frame=self)`, nasconde se stessa. |
| `_on_impostazioni(self, event: wx.Event) -> None` | Chiama `self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")`. |
| `_on_guida(self, event: wx.Event) -> None` | Chiama `self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")`. |
| `_on_esci(self, event: wx.Event) -> None` | Chiama `wx.GetApp().ExitMainLoop()`. |

Binding eventi: `wx.EVT_BUTTON` per ciascun pulsante. Nessun `wx.EVT_CLOSE`
aggiuntivo: la chiusura della finestra tramite Alt+F4 è gestita implicitamente
da `ExitMainLoop` nell'handler "Esci"; la X della finestra può essere bloccata
con `style=wx.DEFAULT_FRAME_STYLE & ~wx.CLOSE_BOX` se si vuole forzare il
percorso "Esci" esplicito (decisione implementativa rimandata ad Agent-Code).

---

## 6. Componenti da modificare

### `main.py` — 2 righe

```python
# PRIMA
from bingo_game.ui.finestra_configurazione import FinestraConfigurazione
finestra = FinestraConfigurazione(renderer=renderer)

# DOPO
from bingo_game.ui.finestra_principale import FinestraPrincipale
finestra = FinestraPrincipale(renderer=renderer)
```

Il resto di `main.py` (creazione `wx.App`, `Vocalizzatore`, `WxRenderer` via
`__new__`, `app.MainLoop()`, blocco `GameLogger` nel `finally`) rimane
invariato.

### `bingo_game/ui/finestra_gioco.py` — 3 modifiche

**Modifica 1 — Parametro aggiuntivo in `__init__`:**

```python
# PRIMA
def __init__(
    self,
    partita: Partita,
    renderer: WxRenderer,
    parent: wx.Window | None = None,
    durata_finestra_ms: int = ...,
    durata_pausa_ms: int = ...
) -> None:

# DOPO
def __init__(
    self,
    partita: Partita,
    renderer: WxRenderer,
    finestra_principale: wx.Frame,
    parent: wx.Window | None = None,
    durata_finestra_ms: int = ...,
    durata_pausa_ms: int = ...
) -> None:
    self._finestra_principale = finestra_principale
```

**Modifica 2 — Aggiunta pulsante in `_build_ui()`:**

Alla fine della sizer principale, aggiungere un `wx.Button` con label
`"Torna al menu principale"`, inizialmente nascosto (`Hide()`) e disabilitato
(`Disable()`). Assegnato a `self._btn_torna_menu`.

**Modifica 3 — Abilitazione pulsante in `_esegui_verifica_premi()`:**

```python
# PRIMA (fine partita)
self._btn_principale.Disable()
return

# DOPO (fine partita)
self._btn_principale.Disable()
self._btn_torna_menu.Enable()
self._btn_torna_menu.Show()
self.Layout()
self._btn_torna_menu.SetFocus()
return
```

Aggiungere il metodo handler `_on_torna_menu`:

```python
def _on_torna_menu(self, event: wx.Event) -> None:
    self._renderer.imposta_widget_log(None)
    self.Hide()
    self._finestra_principale.Show()
    self._renderer.aggiorna_finestra(self._finestra_principale)
```

Binding: `self.Bind(wx.EVT_BUTTON, self._on_torna_menu, self._btn_torna_menu)`.

### `bingo_game/ui/finestra_configurazione.py` — 1 modifica

`_on_conferma()` deve passare `finestra_principale` a `FinestraGioco`. Richiede
che `FinestraConfigurazione` riceva e conservi un riferimento a
`FinestraPrincipale` (via parametro `parent_frame` nel suo `__init__`,
assegnato a `self._finestra_principale`).

```python
# In _on_conferma():
finestra_gioco = FinestraGioco(
    partita=partita,
    renderer=self._renderer,
    finestra_principale=self._finestra_principale,
    ...
)
```

---

## 7. Gestione ciclo vita MainLoop

`wx.App.MainLoop()` termina automaticamente quando viene distrutto l'ultimo
frame top-level non nascosto. Poiché `FinestraPrincipale`, `FinestraConfigurazione`
e `FinestraGioco` sono create come top-level frame (parent=None) e la
navigazione avviene tramite `Hide()`/`Show()` (non `Destroy()`), possono esistere
più frame nascosti quando l'utente preme "Esci".

Strategia adottata: **`wx.GetApp().ExitMainLoop()`** nell'handler `_on_esci`.

Questa chiamata segnala al loop principale di terminare al prossimo ciclo di
eventi, indipendentemente dal numero di frame aperti o nascosti. Non richiede
la distruzione esplicita delle finestre nascoste prima dell'uscita: wxPython
gestisce la pulizia in `wx.App.__del__`. Il blocco `finally` in `main.py`
(contenente `GameLogger.shutdown()`) viene eseguito correttamente dopo che
`app.MainLoop()` ritorna.

---

## 8. Lista completa voci menu

| Voce | Tipo widget | Comportamento |
|---|---|---|
| Nuova partita | `wx.Button` | Crea `FinestraConfigurazione(renderer, parent_frame=self)`, chiama `self.Hide()`. |
| Impostazioni | `wx.Button` | Chiama `renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")`. Nessun dialog. |
| Guida | `wx.Button` | Chiama `renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")`. Nessun dialog. |
| Esci | `wx.Button` | Chiama `wx.GetApp().ExitMainLoop()`. Nessun dialog di conferma. |

Ordine nella sizer: Nuova partita → Impostazioni → Guida → Esci.
Tab order = ordine nella sizer (comportamento wxPython di default).
Focus iniziale: pulsante "Nuova partita" (`SetFocus()` esplicito a fine `_build_ui()`).

---

## 9. Accessibilità NVDA

Checklist specifica per `FinestraPrincipale`:

- Titolo frame: `"Tombola Stark — Menu principale"` (pattern consolidato nel progetto).
- Focus iniziale esplicito: `self._btn_nuova_partita.SetFocus()` a fine `_build_ui()`.
  Usare `wx.CallAfter` se il focus non viene annunciato correttamente al primo Show.
- Pulsanti con label verbosa: "Nuova partita", "Impostazioni", "Guida", "Esci"
  (nessuna abbreviazione, nessun simbolo non testuale).
- Tab order: Nuova partita→Impostazioni→Guida→Esci (ordine naturale nella sizer).
- Placeholder non aprono dialog vuoti: usano `renderer.mostra_messaggio_sistema(...)`.
  Il messaggio viene vocalizzato via AO2 senza che l'utente perda il focus.
- Pulsante "Torna al menu principale" in `FinestraGioco`: diventa visibile e
  riceve il focus automaticamente (`SetFocus()`) nel momento in cui viene
  abilitato, così NVDA annuncia la disponibilità della nuova azione.
- Nessun dialog di conferma per "Esci": l'azione è immediatamente reversibile
  solo riavviando il programma, ma un dialog sarebbe rumore inutile per utenti
  NVDA in un contesto single-user locale.
- `wx.Button` verticali (no `wx.MenuBar`): la barra menu nativa wx non è
  comoda con NVDA in modalità focus; i pulsanti sono più prevedibili.

---

## 10. Vincoli

Cosa questa feature NON deve fare:

- Non usare `wx.MenuBar` o `wx.Menu`: meno accessibile di `wx.Button` su NVDA.
- Non contenere logica di dominio (no istanziazione `Partita`, no `ComandiSistema`)
  in `FinestraPrincipale`. Solo presentazione e navigazione.
- Non aprire dialog vuoti per le voci placeholder: il feedback si limita a
  `renderer.mostra_messaggio_sistema(...)`.
- Non modificare `WxRenderer.__init__` o la firma pubblica del renderer:
  il pattern `__new__` di `main.py` rimane invariato.
- Non usare `Destroy()` per nascondere finestre durante il flusso normale:
  usare esclusivamente `Hide()`/`Show()`.
- Non aggiungere una voce "Torna al menu principale" come opzione di navigazione
  sempre visibile durante la partita: deve essere invisibile finché la partita
  non è terminata.

---

## 11. Scope esplicito fuori perimetro

Le seguenti funzionalità sono escluse da questa feature:

- Implementazione reale delle Impostazioni (profili, volumi, velocità TTS, ecc.).
- Implementazione reale della Guida (testo, screen reader mode, help contestuale).
- Finestre modali o dialog per la navigazione.
- Refactoring del pattern `WxRenderer.__new__` in `main.py`.
- Modifica del sistema di logging (`GameLogger`) o del `Vocalizzatore`.
- Persistenza dello stato tra sessioni (es. ultima partita, preferenze).
- Multi-lingua o localizzazione delle etichette.

---

## 12. Impatto su documentazione

Post-implementazione, i seguenti file devono essere aggiornati:

| File | Aggiornamento richiesto |
|---|---|
| `docs/API.md` | Aggiungere voce `FinestraPrincipale`: parametri `__init__`, metodi pubblici, pattern navigazione. Aggiornare la voce `FinestraGioco` con il nuovo parametro `finestra_principale` e il metodo `_on_torna_menu`. Aggiornare `FinestraConfigurazione` con il parametro `parent_frame`. |
| `docs/ARCHITECTURE.md` | Estendere il diagramma flusso `main.py → FinestraConfigurazione → FinestraGioco` inserendo `FinestraPrincipale` come entry point e il ciclo di ritorno post-partita. |
| `CHANGELOG.md` | Aggiungere voce `[Unreleased]` con sezione `Added`: "FinestraPrincipale: menu principale con navigazione accessibile NVDA". Sezione `Changed`: "main.py apre FinestraPrincipale invece di FinestraConfigurazione"; "FinestraGioco: aggiunto pulsante Torna al menu principale abilitato a partita terminata". |
