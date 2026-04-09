---
type: plan
feature: finestra_principale_menu
agent: Agent-Plan
status: DRAFT
version: v1.1.0
design_ref: docs/2 - projects/DESIGN_finestra_principale_menu.md
date: 2026-04-09
report_ref: docs/4 - reports/REPORT_ANALISI_finestra_principale_menu_2026-04-09.md
---

# PLAN — FinestraPrincipale (Menu Principale) v1.1.0

## 1. Executive Summary

| Campo | Valore |
|---|---|
| Tipo | Feature UI |
| Feature | finestra_principale_menu |
| Priorità | Alta |
| Branch | feat/finestra-principale-menu |
| Versione target | v1.1.0 |
| Status | DRAFT |
| Commit attesi | 4 |
| Design di riferimento | docs/2 - projects/DESIGN_finestra_principale_menu.md |

---

## 2. Problema / Obiettivo

### Problema

L'applicazione Tombola Stark si avvia direttamente su `FinestraConfigurazione`,
saltando qualsiasi punto di ingresso navigazionale. Non esiste una schermata
principale che orienti l'utente né un percorso strutturato di ritorno al menu
dopo la conclusione di una partita.

### Obiettivo misurabile

Al termine dell'implementazione:

- L'avvio di `main.py` mostra `FinestraPrincipale` con 4 pulsanti (Nuova
  partita, Impostazioni, Guida, Esci), focus su "Nuova partita" e
  vocalizzazione NVDA immediata del titolo del frame.
- Premendo "Nuova partita" si apre `FinestraConfigurazione`; al termine della
  configurazione si apre `FinestraGioco`.
- A partita terminata, appare il pulsante "Torna al menu principale" in
  `FinestraGioco`; premendolo si torna a `FinestraPrincipale` senza riavviare
  l'applicazione.
- "Impostazioni" e "Guida" mostrano un messaggio vocale placeholder senza
  aprire dialog.
- "Esci" termina l'applicazione via `wx.GetApp().ExitMainLoop()`.

### Riferimento DESIGN

Documento REVIEWED: `docs/2 - projects/DESIGN_finestra_principale_menu.md`  
Sezioni di riferimento chiave: §2 Obiettivo, §4 Flusso target, §5–6 Componenti,
§7 Gestione MainLoop, §9 Accessibilità NVDA.

---

## 3. File coinvolti

| File | Azione | Note |
|---|---|---|
| `bingo_game/ui/finestra_principale.py` | CREATE | Nuovo modulo: classe `FinestraPrincipale` |
| `main.py` | MODIFY | 2 righe: import + istanziazione |
| `bingo_game/ui/finestra_configurazione.py` | MODIFY | Aggiunta parametro `parent_frame` |
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Aggiunta param + pulsante + handler torna al menu |

---

## 4. Fasi sequenziali

### FASE 1 — Crea `FinestraPrincipale`

**File coinvolti:**

- CREATE: `bingo_game/ui/finestra_principale.py`

**Operazioni:**

1. Creare il file `bingo_game/ui/finestra_principale.py`.
2. Definire la classe `FinestraPrincipale(wx.Frame)` con i seguenti metodi
   (tutti con type hints obbligatori):

   - `__init__(self, renderer: WxRenderer, parent: wx.Window | None = None) -> None`
     - Salva `self._renderer = renderer`
     - Chiama `super().__init__(parent, title="Tombola Stark — Menu principale")`
     - Chiama `self._build_ui()`
     - Chiama `renderer.aggiorna_finestra(self)`
     - Chiama `renderer.mostra_messaggio_sistema("Tombola Stark. Scegli un'opzione.")`
     - Chiama `self.Show()`

   - `_build_ui(self) -> None`
     - Crea un `wx.Panel` come contenitore
     - Crea `wx.BoxSizer(wx.VERTICAL)` come sizer principale
     - Aggiunge nell'ordine: "Nuova partita", "Impostazioni", "Guida", "Esci"
       come `wx.Button` assegnati rispettivamente a:
       `self._btn_nuova_partita`, `self._btn_impostazioni`,
       `self._btn_guida`, `self._btn_esci`
     - Chiama `self._bind_events()`
     - Chiama `self._btn_nuova_partita.SetFocus()` (esplicitamente a fine metodo)

   - `_bind_events(self) -> None`
     - `Bind(wx.EVT_BUTTON, self._on_nuova_partita, self._btn_nuova_partita)`
     - `Bind(wx.EVT_BUTTON, self._on_impostazioni, self._btn_impostazioni)`
     - `Bind(wx.EVT_BUTTON, self._on_guida, self._btn_guida)`
     - `Bind(wx.EVT_BUTTON, self._on_esci, self._btn_esci)`

   - `_on_nuova_partita(self, event: wx.Event) -> None`
     - `from bingo_game.ui.finestra_configurazione import FinestraConfigurazione`
     - `FinestraConfigurazione(renderer=self._renderer, parent_frame=self).Show()`
     - `self.Hide()`

   - `_on_impostazioni(self, event: wx.Event) -> None`
     - `self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")`

   - `_on_guida(self, event: wx.Event) -> None`
     - `self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")`

   - `_on_esci(self, event: wx.Event) -> None`
     - `wx.GetApp().ExitMainLoop()`

3. Verificare che non ci siano `print()` nel file.
4. Eseguire `python -m py_compile bingo_game/ui/finestra_principale.py` → deve
   terminare senza errori.

**Commit message:**

```
feat(ui): aggiungi FinestraPrincipale con menu principale
```

---

### FASE 2 — Modifica `main.py`

**File coinvolti:**

- MODIFY: `main.py`

**Operazioni:**

1. Sostituire la riga:
   ```python
   from bingo_game.ui.finestra_configurazione import FinestraConfigurazione
   ```
   con:
   ```python
   from bingo_game.ui.finestra_principale import FinestraPrincipale
   ```

2. Sostituire la riga:
   ```python
   finestra = FinestraConfigurazione(renderer=renderer)
   ```
   con:
   ```python
   finestra = FinestraPrincipale(renderer=renderer)
   ```

3. Il resto di `main.py` (creazione `wx.App`, `Vocalizzatore`, `WxRenderer`
   via `__new__`, `app.MainLoop()`, blocco `GameLogger` nel `finally`) rimane
   invariato.

4. Eseguire `python -m py_compile main.py` → deve terminare senza errori.

**Commit message:**

```
feat(ui): main.py apre FinestraPrincipale come finestra iniziale
```

---

### FASE 3 — Modifica `FinestraConfigurazione`

**File coinvolti:**

- MODIFY: `bingo_game/ui/finestra_configurazione.py`

**Operazioni:**

1. Aggiungere il parametro `parent_frame: wx.Frame | None = None` alla firma
   di `__init__` di `FinestraConfigurazione`.  
   Firma completa aggiornata:
   ```python
   def __init__(
       self,
       renderer: WxRenderer,
       parent: wx.Window | None = None,
       parent_frame: wx.Frame | None = None,
   ) -> None:
   ```

2. Salvare il riferimento all'inizio di `__init__`:
   ```python
   self._parent_frame = parent_frame
   ```

3. In `_on_conferma()`, aggiornare l'istanziazione di `FinestraGioco` per
   passare `finestra_principale=self._parent_frame`:
   ```python
   finestra_gioco = FinestraGioco(
       partita=partita,
       renderer=self._renderer,
       parent=None,
       durata_finestra_ms=durata_finestra_ms,
       durata_pausa_ms=durata_pausa_ms,
       finestra_principale=self._parent_frame,
   )
   ```

4. Verificare che non ci siano `print()` nel file.
5. Eseguire `python -m py_compile bingo_game/ui/finestra_configurazione.py`
   → deve terminare senza errori.

**Commit message:**

```
feat(ui): FinestraConfigurazione accetta parent_frame per ritorno a menu
```

---

### FASE 4 — Modifica `FinestraGioco`

**File coinvolti:**

- MODIFY: `bingo_game/ui/finestra_gioco.py`

**Operazioni:**

1. Aggiungere `from typing import Optional` (se non già presente) e import di
   `wx` (invariato).

2. Aggiungere il parametro `finestra_principale: wx.Frame | None = None` alla
   firma di `__init__` di `FinestraGioco`:
   ```python
   def __init__(
       self,
       partita: Partita,
       renderer: WxRenderer,
       parent: wx.Window | None = None,
       durata_finestra_ms: int = ...,
       durata_pausa_ms: int = ...,
       finestra_principale: wx.Frame | None = None,
   ) -> None:
   ```
   Salvare subito dopo nell'`__init__`:
   ```python
   self._finestra_principale: wx.Frame | None = finestra_principale
   ```

3. In `_build_ui()`, dopo aver aggiunto `self._btn_principale` alla sizer,
   aggiungere:
   ```python
   self._btn_torna_menu = wx.Button(panel, label="Torna al menu principale")
   self._btn_torna_menu.Hide()
   self._btn_torna_menu.Disable()
   sizer.Add(self._btn_torna_menu, 0, wx.ALL | wx.EXPAND, 5)
   self.Bind(wx.EVT_BUTTON, self._on_torna_menu, self._btn_torna_menu)
   ```

4. In `_esegui_verifica_premi()`, subito dopo `self._btn_principale.Disable()`,
   aggiungere:
   ```python
   if self._finestra_principale is not None:
       self._btn_torna_menu.Enable()
       self._btn_torna_menu.Show()
       self.Layout()
       self._btn_torna_menu.SetFocus()
   ```

5. Aggiungere il metodo handler:
   ```python
   def _on_torna_menu(self, event: wx.Event) -> None:
       self._renderer.imposta_widget_log(None)
       self.Hide()
       self._finestra_principale.Show()
       self._renderer.aggiorna_finestra(self._finestra_principale)
   ```

6. Verificare che non ci siano `print()` nel file.
7. Eseguire `python -m py_compile bingo_game/ui/finestra_gioco.py`
   → deve terminare senza errori.

**Commit message:**

```
feat(ui): FinestraGioco aggiunge pulsante Torna al menu principale
```

---

## 5. Test Plan

### Verifica manuale (tutte le fasi)

Al completamento di tutte e 4 le fasi:

1. Avviare `python main.py` — verificare che appaia la finestra menu con
   NVDA che annuncia "Tombola Stark — Menu principale".
2. Premere Tab — verificare il tab order: Nuova partita → Impostazioni → Guida → Esci.
3. Premere "Impostazioni" — verificare il messaggio vocale placeholder.
4. Premere "Guida" — verificare il messaggio vocale placeholder.
5. Premere "Nuova partita" — verificare che si apra `FinestraConfigurazione`
   e che `FinestraPrincipale` scompaia.
6. Configurare e avviare una partita — verificare che si apra `FinestraGioco`.
7. Completare la partita fino alla tombola — verificare che appaia e riceva
   focus il pulsante "Torna al menu principale".
8. Premere "Torna al menu principale" — verificare che si ritorni al menu
   con NVDA che lo annuncia correttamente.
9. Premere "Esci" — verificare che l'applicazione termini senza residui nel
   log degli errori.

### Unit test da aggiungere (opzionale, bassa priorità)

- `tests/unit/test_finestra_principale.py`:
  - Test che `FinestraPrincipale.__init__` invochi `renderer.aggiorna_finestra`.
  - Test che `_on_nuova_partita` chiami `Hide()` sulla finestra.
  - Test che `_on_esci` invochi `wx.GetApp().ExitMainLoop()`.

Nota: I test UI wxPython richiedono `wx.App()` attivo. Utilizzare mock o
`MockRenderer` già presenti nel progetto per isolare le dipendenze.

---

## 6. Dipendenze tra fasi

```
FASE 1 (crea FinestraPrincipale)
  └─ FASE 2 richiede FASE 1 completata (main.py importa FinestraPrincipale)
  └─ FASE 3 è indipendente da FASE 2 ma deve precedere FASE 4
  └─ FASE 4 richiede FASE 3 completata (usa finestra_principale da FinestraConfigurazione)

Ordine obbligatorio: FASE 1 → FASE 2 → FASE 3 → FASE 4
```

| Fase | Dipende da |
|---|---|
| FASE 1 | Nessuna |
| FASE 2 | FASE 1 |
| FASE 3 | FASE 1 (indirettamente: `FinestraGioco` riceve `finestra_principale`) |
| FASE 4 | FASE 3 |

---

## 7. Rischi

| Rischio | Probabilità | Impatto | Mitigazione |
|---|---|---|---|
| `SetFocus()` non annunciato da NVDA al primo `Show()` | Media | Alto | Usare `wx.CallAfter(self._btn_nuova_partita.SetFocus)` se necessario |
| `ExitMainLoop()` non termina il processo con frame nascosti | Bassa | Alto | Già verificato nel DESIGN §7: `ExitMainLoop()` è il pattern corretto con `Hide()`/`Show()` |
| Firma `__init__` di `FinestraGioco` rompe test esistenti | Media | Medio | Parametro aggiunto con default `None`; nessun test esistente passa valori posizionali su `finestra_principale` |
| `Layout()` non ridisegna la sizer con `_btn_torna_menu` visibile | Bassa | Medio | Usare `panel.Layout()` invece di `self.Layout()` se necessario |

---

## 8. Criteri di completamento

- `bingo_game/ui/finestra_principale.py` creato, compilabile, senza `print()`.
- `main.py` aggiornato: istanzia `FinestraPrincipale` come prima finestra.
- `FinestraConfigurazione.__init__` accetta `parent_frame`, lo passa a `FinestraGioco`.
- `FinestraGioco.__init__` accetta `finestra_principale`, mostra il pulsante
  "Torna al menu principale" solo a partita terminata.
- Tutti i pre-commit check superati su tutti e 4 i file modificati.
- Verifica manuale NVDA completata (punti 1–9 del Test Plan §5).
- Status PLAN aggiornato a `READY` dopo review utente.
