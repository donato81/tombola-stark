---
tipo: report
titolo: Analisi aggiunta FinestraPrincipale — menu principale app
data: 2026-04-09
agente: Agent-Analyze
stato: definitivo
feature: finestra_principale_menu
---

# Report Analisi — FinestraPrincipale (Menu Principale)

## Sommario esecutivo

L'aggiunta di `FinestraPrincipale` introduce un livello di navigazione intermedio tra il bootstrap dell'applicazione (`main.py`) e la logica di configurazione partita (`FinestraConfigurazione`). L'impatto è circoscritto a tre file produzione: `main.py` (punto di apertura), un nuovo `bingo_game/ui/finestra_principale.py` (da creare) e nessuna modifica strutturale ai layer domain/application. Il renderer (`WxRenderer`) è già progettato per essere rediretto tra finestre via `aggiorna_finestra()`, quindi la transizione è compatibile con il meccanismo esistente senza refactoring del renderer stesso.

Il rischio principale riguarda il flusso di fine partita: attualmente `FinestraGioco` non ha alcun meccanismo per tornare indietro; questo gap deve essere deciso a livello di design prima di implementare.

Un rischio accessibilità minore è il focus iniziale della nuova finestra: le convenzioni NVDA già stabilite nel progetto richiedono che il primo controllo interattivo riceva il focus esplicitamente nell'`__init__`.

---

## Componenti coinvolti

| File | Classe/Simbolo | Ruolo nel task |
|------|---------------|----------------|
| `main.py` | funzione `main()` | Entry point: crea `wx.App`, `Vocalizzatore`, `WxRenderer` e apre la prima finestra. Attualmente apre `FinestraConfigurazione`, dovrà aprire `FinestraPrincipale`. |
| `bingo_game/ui/finestra_principale.py` | `FinestraPrincipale` (nuovo) | Nuovo frame: menu principale con voci Nuova partita, Impostazioni (placeholder), Guida (placeholder), Esci. |
| `bingo_game/ui/finestra_configurazione.py` | `FinestraConfigurazione` | Frame configurazione partita. Già esistente, verrà aperta da `FinestraPrincipale` invece che direttamente da `main.py`. |
| `bingo_game/ui/finestra_gioco.py` | `FinestraGioco` | Frame di gioco. Non viene modificato direttamente, ma il flusso di ritorno a fine partita è un gap aperto che la feature deve considerare. |
| `bingo_game/ui/renderers/renderer_wx.py` | `WxRenderer` | Renderer wxPython condiviso tra tutte le finestre. Cambia frame attivo via `aggiorna_finestra()`. Nessuna modifica necessaria. |
| `bingo_game/ui/renderers/base_renderer.py` | `BaseRenderer`, `StatoConfigurazione` | Contratto astratto del renderer. Non modificato. |
| `my_lib/vocalizzatore.py` | `IVocalizzatore`, `Vocalizzatore` | Backend TTS (AO2). Passato al renderer in `main.py`. Non impattato. |
| `bingo_game/ui/__init__.py` | (vuoto) | Package marker. Non richiede modifiche. |
| `bingo_game/logging/game_logger.py` | `GameLogger` | Inizializzato in `main()` con blocco `finally`. Non impattato dalla feature. |
| `docs/API.md` | — | Documentazione pubblica dei componenti: andrà aggiornata con `FinestraPrincipale`. |
| `docs/ARCHITECTURE.md` | — | Diagramma flusso `main.py → FinestraConfigurazione / FinestraGioco`: andrà esteso. |

---

## Dipendenze

```
main.py
  └─ crea wx.App
  └─ crea Vocalizzatore
  └─ crea WxRenderer (via __new__ bypass, _finestra=None)
  └─ crea FinestraPrincipale(renderer=renderer)
       └─ __init__ chiama renderer.aggiorna_finestra(self)
       └─ on "Nuova partita" → crea FinestraConfigurazione(renderer=renderer)
            └─ __init__ chiama renderer.aggiorna_finestra(self)
            └─ on conferma → crea FinestraGioco(partita, renderer, ...)
                 └─ __init__ chiama renderer.aggiorna_finestra(self)
                 └─ __init__ chiama renderer.imposta_widget_log(self._log_ctrl)

WxRenderer
  └─ _finestra: aggiornato ad ogni transizione finestra
  └─ _vocalizzatore: IVocalizzatore, invariato
  └─ _log_text_ctrl: None fino a FinestraGioco; reset a None se si torna al menu

Vocalizzatore
  └─ passato a WxRenderer alla creazione, mai ricreato

ComandiSistema
  └─ istanziato indipendentemente sia in FinestraConfigurazione che in FinestraGioco
  └─ non condiviso tra finestre

Partita
  └─ creata da ComandiSistema in FinestraConfigurazione._on_conferma()
  └─ passata a FinestraGioco come parametro
```

**Nota dipendenza critica**: `WxRenderer.__init__` richiede `finestra_principale: wx.Frame` come parametro obbligatorio, ma in `main.py` il renderer è costruito via `WxRenderer.__new__(WxRenderer)` con attributi impostati manualmente, per spezzare la dipendenza circolare. Questo pattern dovrà essere replicato identicamente per `FinestraPrincipale`.

---

## Flusso attuale vs flusso target

### Flusso attuale

```
python main.py
  → main():
      wx.App()
      Vocalizzatore()
      WxRenderer.__new__() + attributi manuali
      FinestraConfigurazione(renderer=renderer)
        → aggiorna_finestra(FinestraConfigurazione)
        → [utente clicca "Avvia partita"]
        → FinestraGioco(partita, renderer)
            → aggiorna_finestra(FinestraGioco) + imposta_widget_log(log_ctrl)
            → FinestraConfigurazione.Hide()
            → [gioco fino a tombola]
            → partita_terminata → btn.Disable()
            → [nessun ritorno automatico]
      app.MainLoop()
  → GameLogger.shutdown()
```

### Flusso target

```
python main.py
  → main():
      wx.App()
      Vocalizzatore()
      WxRenderer.__new__() + attributi manuali
      FinestraPrincipale(renderer=renderer)
        → aggiorna_finestra(FinestraPrincipale)
        → Mostra menu: Nuova partita | Impostazioni | Guida | Esci
        → [utente: "Nuova partita"]
        → FinestraConfigurazione(renderer=renderer)
            → aggiorna_finestra(FinestraConfigurazione)
            → FinestraPrincipale.Hide()
            → [utente configura e avvia]
            → FinestraGioco(partita, renderer)
                → aggiorna_finestra(FinestraGioco) + imposta_widget_log(log_ctrl)
                → FinestraConfigurazione.Hide()
                → [gioco fino a tombola]
                → partita_terminata
                → [DECISIONE APERTA: ritorno a FinestraPrincipale?]
        → [utente: "Esci"]
        → app termina
      app.MainLoop()
  → GameLogger.shutdown()
```

---

## Analisi dettagliata per domanda

### 1. Come viene passato WxRenderer da main.py a FinestraConfigurazione e poi a FinestraGioco?

Il renderer è creato una volta sola in `main()` tramite bypass di `__init__`:

```python
renderer: WxRenderer = WxRenderer.__new__(WxRenderer)
renderer._finestra = None
renderer._vocalizzatore = vocalizzatore
renderer._ultimo_annuncio = ""
renderer._log_text_ctrl = None
renderer.numero_in_focus = None
```

Il campo `_finestra` viene aggiornato ad ogni transizione:

- `FinestraConfigurazione.__init__`: `self._renderer.aggiorna_finestra(self)` → renderer punta a FinestraConfigurazione.
- `FinestraGioco.__init__`: `self._renderer.aggiorna_finestra(self)` → renderer punta a FinestraGioco. Aggiunge `self._renderer.imposta_widget_log(self._log_ctrl)`.

Per `FinestraPrincipale` il pattern sarà identico: riceve `renderer` in `__init__`, chiama `aggiorna_finestra(self)`, salva il riferimento e lo passa a `FinestraConfigurazione` quando l'utente seleziona "Nuova partita".

### 2. Ritorno da FinestraGioco a fine partita?

**No. Non esiste alcun meccanismo di ritorno.** In `_esegui_verifica_premi()`:

```python
if risultato_ver.get("partita_terminata") or risultato_ver.get("tombola_rilevata"):
    self._renderer.mostra_messaggio_sistema("La partita è terminata.")
    self._btn_principale.Disable()
    return
```

La finestra rimane aperta e bloccata. Questo è un **gap da colmare** con la nuova feature.

### 3. Ciclo vita wx.App e app.MainLoop()?

`app.MainLoop()` esce automaticamente quando viene distrutto l'ultimo top-level frame non nascosto. Se l'utente clicca "Esci" su `FinestraPrincipale` mentre `FinestraConfigurazione` è nascosta (non distrutta), il MainLoop non uscirà. La strategia sicura: nel handler "Esci" chiamare `wx.GetApp().ExitMainLoop()` o distruggere tutte le finestre nascoste prima di chiudere se stessa.

### 4. Convenzioni accessibilità NVDA consolidate nel codebase

- **Titolo frame semantico**: pattern `"Tombola Stark — <fase>"`
- **Focus iniziale esplicito**: `self._<ctrl>.SetFocus()` a fine `_build_ui()`, eventualmente + `wx.CallAfter`
- **Label prima dei controlli**: ogni `wx.TextCtrl/SpinCtrl` precede un `wx.StaticText` nella sizer
- **Pulsanti con label esplicite**: "Avvia partita", non "OK" o abbreviazioni
- **Nessun simbolo non testuale** nei label
- **Enter come alternativa al click**: `EVT_CHAR_HOOK` intercetta `WXK_RETURN`
- **Messaggi errore via label statica + vocalizzazione renderer**: `SetLabel()` + `renderer.mostra_messaggio_sistema()`

### 5. Dove deve stare il nuovo file?

`bingo_game/ui/finestra_principale.py` — coerente con `finestra_configurazione.py` e `finestra_gioco.py` nella stessa cartella.

### 6. Modifiche minime necessarie in main.py

Due righe:

```python
# PRIMA
from bingo_game.ui.finestra_configurazione import FinestraConfigurazione
finestra = FinestraConfigurazione(renderer=renderer)

# DOPO
from bingo_game.ui.finestra_principale import FinestraPrincipale
finestra = FinestraPrincipale(renderer=renderer)
```

Il resto di `main.py` rimane invariato.

### 7. FinestraPrincipale ha bisogno del renderer e del vocalizzatore?

**Renderer**: sì, deve riceverlo come parametro per (1) agganciarlo con `aggiorna_finestra(self)` e (2) passarlo a `FinestraConfigurazione`. Non lo usa per events di gioco.

**Vocalizzatore**: no, non direttamente. Il vocalizzatore è incapsulato nel renderer. Per vocalizzare testi, si usa `renderer.mostra_messaggio_sistema(...)`.

### 8. FinestraConfigurazione deve essere figlia di FinestraPrincipale o indipendente?

**Raccomandata: indipendente (parent=None), con FinestraPrincipale nascosta.** Motivazioni:
- `FinestraConfigurazione.__init__` già accetta `parent=None` — nessuna modifica.
- Le finestre indipendenti sono più semplici per NVDA (ognuna ha il proprio titolo nell'albero).
- Il pattern `.Hide()` / aggiorna renderer / apri nuova finestra è già consolidato nel codebase.

### 9. Ritorno da FinestraGioco: dove va l'utente?

Attualmente da nessuna parte (gap — vedi Gap 1). Le opzioni per il Design:
- **Opzione A** (consigliata): pulsante "Torna al menu" che appare solo a `partita_terminata=True`
- **Opzione B**: handler `EVT_CLOSE` su `FinestraGioco` che mostra `FinestraPrincipale`
- **Opzione C**: tornare a `FinestraConfigurazione` per una nuova partita immediata

L'Opzione A è la più NVDA-friendly (tasto dedicato senza richiedere chiusura manuale).

### 10. Altri entry point che aprono FinestraConfigurazione?

- `main.py`: unico entry point produzione impattato.
- Test (`tests/unit/`, `tests/integration/`): nessuno importa né istanzia `FinestraConfigurazione` direttamente.
- Scripts (`scripts/`): nessuno apre finestre UI.
- `docs/API.md` e `docs/ARCHITECTURE.md`: solo riferimenti documentali, richiederanno aggiornamento post-implementazione.

---

## Rischi

### R1 — Ciclo vita MainLoop con finestre nascoste (gravità: media)

Se l'utente preme "Esci" dal menu mentre `FinestraConfigurazione` è nascosta, il MainLoop potrebbe non terminare automaticamente.

**Mitigazione**: nel handler "Esci", distruggere esplicitamente le finestre nascoste oppure chiamare `wx.GetApp().ExitMainLoop()`.

### R2 — Renderer _log_text_ctrl puntante a widget distrutto (gravità: bassa)

Se si torna da `FinestraGioco` a `FinestraPrincipale`, il renderer ha ancora `_log_text_ctrl` impostato sul widget distrutto.

**Mitigazione**: prima di distruggere `FinestraGioco`, chiamare `renderer.imposta_widget_log(None)`.

### R3 — Focus NVDA non annunciato senza SetFocus esplicito (gravità: media)

Senza `SetFocus()` esplicito, NVDA potrebbe non annunciare nulla all'apertura del menu principale, rendendo la finestra disorientante.

**Mitigazione**: SetFocus esplicito sul primo pulsante a fine `_build_ui()`, seguendo il pattern di `FinestraConfigurazione`.

### R4 — Pattern `WxRenderer.__new__` fragile (gravità: bassa, preesistente)

Il bypass di `__init__` in `main.py` è accoppiato agli attributi interni di `WxRenderer`. Non è introdotto da questa feature.

**Mitigazione**: out of scope. Considerare in un ciclo successivo rendere `Optional[wx.Frame]` il parametro di `__init__`.

### R5 — Copertura test assente per la nuova finestra (gravità: bassa)

Non esistono test UI automatizzati per le finestre wxPython nel progetto.

**Mitigazione**: aggiungere almeno un test di istanziazione con renderer mock nel piano di implementazione.

---

## Vincoli accessibilità NVDA

1. **Titolo frame semantico**: `"Tombola Stark — Menu principale"` o equivalente, senza abbreviazioni.
2. **Focus iniziale esplicito**: `SetFocus()` sul primo pulsante (Nuova partita) a fine `_build_ui()`.
3. **Keyboard-first**: ogni voce raggiungibile via Tab, attivabile con Invio o Spazio.
4. **Ordine Tab coerente**: disposizione sizer = ordine logico navigazione: Nuova partita → Impostazioni → Guida → Esci.
5. **Label espliciti**: "Nuova partita" non "Play". "Esci" non "X".
6. **Placeholder non aprono dialog vuoti**: "Impostazioni" e "Guida" devono rispondere con `renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")` senza aprire dialog.
7. **Nessun dialog di conferma per "Esci"**: chiusura diretta senza messagebox intermedia.
8. **Vocalizzazione all'apertura**: dopo `aggiorna_finestra(self)`, chiamare `renderer.mostra_messaggio_sistema("Tombola Stark. Scegli un'opzione.")`.

---

## Gap e decisioni aperte

### Gap 1 — Meccanismo di ritorno da FinestraGioco [RISOLTO — 2026-04-09]

**Decisione utente: Opzione A.**
Aggiungere un pulsante "Torna al menu principale" a `FinestraGioco` che diventa visibile (o abilitato) solo quando `partita_terminata = True`. Alla pressione: il pulsante chiama `renderer.imposta_widget_log(None)`, distrugge o nasconde `FinestraGioco`, mostra `FinestraPrincipale` (precedentemente nascosta). Questa è la soluzione più NVDA-friendly perché offre un controllo dedicato e annunciabile senza richiedere all'utente di chiudere manualmente la finestra.

### Gap 2 — Gestione finestre nascoste a "Esci" [CRITICO per stabilità]

Se l'utente preme "Esci" con `FinestraConfigurazione` nascosta, il MainLoop deve terminare correttamente. La strategia esatta va specificata nel design.

### Gap 3 — Notifica placeholder Impostazioni e Guida [MINORE]

Definire se le voci mostrano messaggio vocale, dialog "In costruzione", o controllo disabilitato. L'approccio consigliato è messaggio vocale via renderer (più accessibile).

### Gap 4 — Refactoring WxRenderer.__new__ bypass [BASSO, futura feature]

Non bloccante per questa implementazione.

### Gap 5 — Aggiornamento docs API.md e ARCHITECTURE.md [CERTO, post-implementazione]

Richiesto dopo l'implementazione da Agent-Docs.

---

## Raccomandazioni

1. **Creare `bingo_game/ui/finestra_principale.py`** con `FinestraPrincipale(wx.Frame)`, stesse convenzioni strutturali di `finestra_configurazione.py`.

2. **Usare `wx.Button` verticali in sizer invece di `wx.MenuBar`**: i pulsanti sono più accessibili su NVDA rispetto al menu bar nativo di wxPython, non richiedono comportamenti speciali dei tasti e sono coerenti con il resto della UI.

3. **Modifiche minime a `main.py`**: solo 2 righe (import e istanziazione). Nessuna altra modifica.

4. **Non modificare `FinestraConfigurazione`**: continua a funzionare con `parent=None`. `FinestraPrincipale` la nasconde se stessa all'apertura.

5. **Risolvere il Gap 1 in Design**: almeno un handler `on_fine_partita` su `FinestraGioco` (o pulsante "Torna al menu") è il minimo per un flusso completo.

6. **Test manuale del ciclo vita MainLoop**: la sequenza "avvia → nuova partita → gioca → esci" deve essere verificata empiricamente su Windows con NVDA attivo prima del commit.

7. **Delegare a Agent-Design** la specifica del layout visivo, la gestione dei gap e la sequenza commit per Agent-Plan.
