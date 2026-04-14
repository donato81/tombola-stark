---
type: todo
feature: finestra_principale_menu
agent: Agent-Plan
status: COMPLETED
version: v1.1.0
plan_ref: docs/3 - coding plans/PLAN_finestra_principale_menu_v1.1.0.md
design_ref: docs/2 - projects/DESIGN_finestra_principale_menu.md
date: 2026-04-09
---

# TODO — FinestraPrincipale (Menu Principale) v1.1.0

Piano di riferimento (fonte di verità):
[PLAN_finestra_principale_menu_v1.1.0.md](../3%20-%20coding%20plans/PLAN_finestra_principale_menu_v1.1.0.md)

---

## Istruzioni per Agent-Code

Esegui le fasi nell'ordine indicato. Ogni fase corrisponde a un commit atomico.
Prima di ogni commit esegui `python -m py_compile` sul file modificato.
Non procedere alla fase successiva se il compile fallisce.
Riferiti al PLAN per le specifiche tecniche dettagliate di ogni operazione.

---

## Checklist operativa

- [ ] **FASE 1**: Crea `bingo_game/ui/finestra_principale.py`
  - [ ] Classe `FinestraPrincipale(wx.Frame)` creata
  - [ ] `__init__` con parametri `renderer: WxRenderer`, `parent: wx.Window | None = None`
  - [ ] `_build_ui()` con 4 pulsanti nell'ordine: Nuova partita, Impostazioni, Guida, Esci
  - [ ] `_bind_events()` con binding `wx.EVT_BUTTON` per ciascun pulsante
  - [ ] `_on_nuova_partita()` apre `FinestraConfigurazione(renderer, parent_frame=self)` e chiama `self.Hide()`
  - [ ] `_on_impostazioni()` chiama `renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")`
  - [ ] `_on_guida()` chiama `renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")`
  - [ ] `_on_esci()` chiama `wx.GetApp().ExitMainLoop()`
  - [ ] Focus iniziale: `self._btn_nuova_partita.SetFocus()` esplicito a fine `_build_ui()`
  - [ ] Vocalizzazione apertura: `renderer.mostra_messaggio_sistema("Tombola Stark. Scegli un'opzione.")`
  - [ ] Titolo frame: `"Tombola Stark — Menu principale"`
  - [ ] Type hints presenti su tutti i metodi pubblici
  - [ ] Nessun `print()` nel file
  - [ ] `python -m py_compile bingo_game/ui/finestra_principale.py` → OK
  - [ ] Commit: `feat(ui): aggiungi FinestraPrincipale con menu principale`

- [ ] **FASE 2**: Modifica `main.py`
  - [ ] Import aggiornato: `from bingo_game.ui.finestra_principale import FinestraPrincipale`
  - [ ] Istanziazione aggiornata: `finestra = FinestraPrincipale(renderer=renderer)`
  - [ ] Il resto di `main.py` invariato
  - [ ] Nessun `print()` aggiunto
  - [ ] `python -m py_compile main.py` → OK
  - [ ] Commit: `feat(ui): main.py apre FinestraPrincipale come finestra iniziale`

- [ ] **FASE 3**: Modifica `bingo_game/ui/finestra_configurazione.py`
  - [ ] Parametro `parent_frame: wx.Frame | None = None` aggiunto a `__init__`
  - [ ] `self._parent_frame = parent_frame` salvato in `__init__`
  - [ ] In `_on_conferma()`: `FinestraGioco` riceve `finestra_principale=self._parent_frame`
  - [ ] Type hints aggiornati sulla firma di `__init__`
  - [ ] Nessun `print()` nel file
  - [ ] `python -m py_compile bingo_game/ui/finestra_configurazione.py` → OK
  - [ ] Commit: `feat(ui): FinestraConfigurazione accetta parent_frame per ritorno a menu`

- [ ] **FASE 4**: Modifica `bingo_game/ui/finestra_gioco.py`
  - [ ] Parametro `finestra_principale: wx.Frame | None = None` aggiunto a `__init__`
  - [ ] `self._finestra_principale = finestra_principale` salvato in `__init__`
  - [ ] `self._btn_torna_menu = wx.Button(panel, label="Torna al menu principale")` aggiunto in `_build_ui()`
  - [ ] `self._btn_torna_menu.Hide()` e `.Disable()` chiamati a fine creazione pulsante
  - [ ] Pulsante aggiunto alla sizer dopo `_btn_principale`
  - [ ] Binding `wx.EVT_BUTTON` → `_on_torna_menu` in `_build_ui()`
  - [ ] In `_esegui_verifica_premi()`: `self._btn_torna_menu.Enable()`, `.Show()`, `self.Layout()`, `.SetFocus()` condizionati a `self._finestra_principale is not None`
  - [ ] Metodo `_on_torna_menu(self, event: wx.Event) -> None` implementato con `imposta_widget_log(None)`, `Hide()`, `Show()`, `aggiorna_finestra()`
  - [ ] Type hints presenti
  - [ ] Nessun `print()` nel file
  - [ ] `python -m py_compile bingo_game/ui/finestra_gioco.py` → OK
  - [ ] Commit: `feat(ui): FinestraGioco aggiunge pulsante Torna al menu principale`

---

## Verifica manuale finale (post FASE 4)

- [ ] `python main.py` → appare `FinestraPrincipale`, NVDA annuncia il titolo
- [ ] Tab order: Nuova partita → Impostazioni → Guida → Esci
- [ ] "Impostazioni" → messaggio vocale placeholder, nessun dialog
- [ ] "Guida" → messaggio vocale placeholder, nessun dialog
- [ ] "Nuova partita" → si apre `FinestraConfigurazione`, menu sparisce
- [ ] Configurazione + avvio partita → si apre `FinestraGioco`
- [ ] Tombola raggiunta → appare "Torna al menu principale" con focus automatico
- [ ] "Torna al menu principale" → si ritorna al menu, NVDA annuncia la finestra
- [ ] "Esci" → applicazione termina correttamente, nessun errore nel log
