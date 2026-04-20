# Report Analisi — Pannello Riepilogo Finale appare grigio a fine partita

**Data:** 2026-04-20  
**Agente:** Agent-Analyze  
**Stato:** COMPLETATA  
**Priorità:** Alta — regressione visiva su funzionalità chiave

---

## 1. Sommario Esecutivo

A fine partita (dopo tombola dichiarata), il pannello di riepilogo
`PannelloRiepilogoFinale` viene popolato correttamente e NVDA legge i dati
attesi. Tuttavia, la finestra visiva appare completamente grigia, priva di
contenuto. La causa principale è una chiamata `Layout()` sul frame radice
(`FinestraGioco`) invece che sul pannello figlio (`self._panel`) che è l'unico
a possedere il sizer. Concorrono tre difetti secondari che amplificano l'effetto.

---

## 2. Flusso di Esecuzione a Fine Partita

```
FinestraGioco._on_verifica()
  → self._renderer.mostra_report_finale(dati_report)           [linea ~1101]
      → WxRenderer.mostra_report_finale()                      [renderer_wx.py:133]
          → self._wx_mostra_report_finale(dati_partita)        [renderer_wx.py:846]
              → self._finestra.mostra_testo(testo)
              → self._finestra.aggiungi_a_log(testo)
              → self._finestra.mostra_riepilogo_finale(dati)   [finestra_gioco.py:1338]
          → self._ao2_vocalizza(testo)   ← NVDA OK
  → self._btn_principale.Disable()
  → self._btn_pausa.Disable()
  → self._btn_torna_menu.Enable() + Show()
  → self.Layout()                        ← no-op (v. Difetto D1)
  → self._btn_torna_menu.SetFocus()      ← ridondante (v. Difetto D4)
```

**Osservazione chiave:** `_ao2_vocalizza()` è chiamato incondizionatamente e
produce il testo corretto → NVDA funziona. Il fallimento è isolato al layer
visivo `_wx_*`.

---

## 3. Analisi Struttura UI in `_build_ui()`

Il sizer principale risiede su `self._panel` (un `wx.Panel` figlio del frame):

```python
self._panel = wx.Panel(self)
panel = self._panel
sizer = wx.BoxSizer(wx.VERTICAL)
# ... add children ...
panel.SetSizer(sizer)    # ← sizer APPARTIENE al panel, NON al frame
```

Il frame `FinestraGioco` non ha nessun sizer direttamente assegnato.

Ordine degli elementi nel sizer del panel:

| # | Widget | proportion | Nascosto in mostra_riepilogo_finale? |
|---|--------|-----------|--------------------------------------|
| 1 | `_header_bar` | 0 | NO — rimane visibile |
| 2 | `_btn_principale` | 0 | NO — solo Disable() |
| 3 | `_btn_pausa` | 0 | NO — solo Disable() |
| 4 | `_btn_torna_menu` | 0 | NO — viene Show()+Enable() |
| 5 | `_pannello_griglia` | 1 | Sì — Hide() |
| 6 | `_pannello_riepilogo` | 1 | Sì → viene poi Show() |
| 7 | `sizer_griglie` | 0 | Parziale (v. sotto) |
| 8 | `_sizer_selezione` | 0 | Parziale (solo btn interni) |
| 9 | `sizer_premi` | 0 | NO — pulsanti Ambo…Tombola visibili |
| 10 | `_lbl_log` | 0 | NO — label "Cronologia annunci" visibile |
| 11 | `_log_ctrl` | 0 | NO — area log visibile e occupante spazio |

Contenuto di `sizer_griglie` (elemento 7):
- `_pannello_tabellone` — Hide() OK
- `_btn_freccia_sx` + `_btn_freccia_dx` — Hide() OK
- `sizer_cartella_con_titolo` — NON rimosso
  - `_lbl_cartella_titolo` (label "Cartella") — **NON nascosto** (bug)
  - `_pannello_cartella` — Hide() OK

---

## 4. Difetti Identificati

### D1 — CRITICO: `self.Layout()` su frame senza sizer (no-op)

**File:** `bingo_game/ui/finestra_gioco.py`  
**Righe:** 1353 (in `mostra_riepilogo_finale`) e ~1106 (in `_on_verifica`)  

**Problema:**  
`FinestraGioco.mostra_riepilogo_finale()` e il blocco chiamante in
`_on_verifica()` chiamano entrambi `self.Layout()` sul frame.

In wxPython, `wx.Window.Layout()` esegue `GetSizer()->SetDimension(...)` solo
se la finestra ha un sizer ad essa assegnato. `FinestraGioco` non ha un sizer
proprio: il sizer è assegnato a `self._panel`. Di conseguenza `self.Layout()`
è un no-op: il panel non ricalcola le posizioni e dimensioni dei suoi figli
dopo le chiamate a `Hide()` e `Show()`.

`PannelloRiepilogoFinale` viene mostrato (`Show()`) ma conserva la posizione e
dimensione precedenti (potenzialmente zero, perché era nascosto fin dall'inizio
durante il primo layout).

**Fix atteso:**  
Sostituire `self.Layout()` con `self._panel.Layout()` in entrambi i punti.

---

### D2 — ALTO: Numerosi elementi UI non nascosti nel riepilogo finale

**File:** `bingo_game/ui/finestra_gioco.py`  
**Metodo:** `mostra_riepilogo_finale()` linea 1338  

**Problema:**  
I seguenti widget rimangono visibili dopo la transizione alla schermata di
riepilogo, occupando spazio nel sizer e riducendo (o azzerando) lo spazio
disponibile per `_pannello_riepilogo`:

- `_header_bar` (header informativo turno/numero)
- `_btn_principale` (disabilitato ma visibile, occupa altezza fissa)
- `_btn_pausa` (disabilitato ma visibile)
- `_lbl_cartella_titolo` (label statica "Cartella" dentro `sizer_griglie`)
- tutti i pulsanti in `_btn_premi` (Ambo, Terno, Quaterna, Cinquina, Tombola)
- `_lbl_log` (label "Cronologia annunci")
- `_log_ctrl` (TextCtrl read-only con altezza fissa 120px)

Dato che `_pannello_riepilogo` ha `proportion=1` al pari di `_pannello_griglia`,
occuperebbe comunque metà dello spazio "stretch" disponibile — ma con tutti gli
elementi fissi sopra ancora presenti, lo spazio stretch è quasi zero e il pannello
si riduce a una striscia sottile o invisibile.

**Fix atteso:**  
Aggiungere `Hide()` espliciti per tutti gli elementi sopra elencati in
`mostra_riepilogo_finale()`.

---

### D3 — MEDIO: Mancanza di `Refresh()` dopo il ricalcolo layout

**File:** `bingo_game/ui/finestra_gioco.py`  
**Metodo:** `mostra_riepilogo_finale()` linea 1338  

**Problema:**  
Dopo `Layout()`, wxPython su Windows non garantisce sempre il ridisegno
automatico delle aree precedentemente occupate da widget nascosti. Senza
un`Refresh()` esplicito, le aree vacate restano grigie a livello GDI.

**Fix atteso:**  
Aggiungere `self._panel.Refresh()` dopo `self._panel.Layout()`.

---

### D4 — BASSO: Doppio `SetFocus` ridondante su `_btn_torna_menu`

**File:** `bingo_game/ui/finestra_gioco.py`  
**Righe:** ~1356 (in `mostra_riepilogo_finale`) e ~1107 (in `_on_verifica`)  

**Problema:**  
`mostra_riepilogo_finale` pianifica `wx.CallAfter(self._btn_torna_menu.SetFocus)`.
Il codice chiamante chiama poi `self._btn_torna_menu.SetFocus()` in modo
sincrono, prima che `CallAfter` venga processato. Il risultato è un doppio
tentativo di focus: il primo sincrono (su un bottone appena abilitato ma
potenzialmente non ancora visibilizzato completamente), il secondo asincrono
(superfluo).

**Fix atteso:**  
Rimuovere uno dei due `SetFocus`. Il `wx.CallAfter` in `mostra_riepilogo_finale`
è preferibile perché garantisce che tutti i cambiamenti visivi siano stati
processati prima di spostare il focus.

---

## 5. Percorso della Chiamata (stack logico)

```
_on_verifica()                          [finestra_gioco.py ~1085]
  └─ renderer.mostra_report_finale()   [renderer_wx.py:133]
        └─ _wx_mostra_report_finale()  [renderer_wx.py:846]
              ├─ mostra_testo()        [OK — aggiorna _pannello_griglia]
              ├─ aggiungi_a_log()      [OK — aggiunge al log]
              └─ mostra_riepilogo_finale()  [finestra_gioco.py:1338]
                    ├─ _pannello_griglia.Hide()      [OK]
                    ├─ _pannello_tabellone.Hide()    [OK]
                    ├─ _pannello_cartella.Hide()     [OK]
                    ├─ _btn_freccia_sx/dx.Hide()     [OK]
                    ├─ _pulsanti_selezione Hide()    [OK]
                    ├─ _pannello_riepilogo.mostra()  [OK — dati popolati]
                    ├─ _pannello_riepilogo.Show()    [OK]
                    ├─ self.Layout()    ← D1: no-op (nessun sizer sul frame)
                    └─ CallAfter(SetFocus)           ← D4: poi duplicato
```

---

## 6. Perché NVDA Funziona ma il Visivo No

`WxRenderer.mostra_report_finale()` esegue in sequenza:

1. `self._wx_mostra_report_finale(dati_partita)` — layer visivo (rotto)
2. `self._ao2_vocalizza(testo)` — layer voce (funzionante)

Il layer voce costruisce il testo `parti = [...]` in modo completamente
indipendente dall'esito del layer visivo e lo passa al `Vocalizzatore`.
NVDA riceve il testo corretto indipendentemente dal fatto che il pannello
sia visivamente corretto o no.

---

## 7. Valutazione Fattibilità Fix

| Difetto | Complessità fix | Rischio regressione | Stimato |
|---------|----------------|--------------------|---------| 
| D1 `self._panel.Layout()` | Bassa — 2 sostituzioni | Molto basso | < 15 min |
| D2 Hide elementi mancanti | Bassa — 7 chiamate `.Hide()` | Basso | < 20 min |
| D3 `Refresh()` aggiuntivo | Minima — 1 riga | Nessuno | < 5 min |
| D4 Rimozione SetFocus dup | Minima — 1 riga | Nessuno | < 5 min |

**Fattibilità complessiva:** Alta.  
Nessun refactor architetturale richiesto. I quattro fix sono modifiche
chirurgiche a un singolo metodo e al suo chiamante. Il test manuale
(avviare una partita con un bot e aspettare la tombola automatica) è
sufficiente per verificare il risultato.

**Test di regressione suggeriti:**
- `tests/test_game_controller.py` – invariante: nessuna modifica alla logica di gioco
- Lancio manuale applicazione: avviare partita, attendere tombola automatica, verificare
  che si apra il pannello riepilogo con titolo, vincitore, turni, estratti e lista premi

---

## 8. File Coinvolti

| File | Righe da modificare | Tipo modifica |
|------|-------------------|---------------|
| [bingo_game/ui/finestra_gioco.py](../../bingo_game/ui/finestra_gioco.py#L1338) | 1338-1356 (`mostra_riepilogo_finale`) | D1, D2, D3, D4 |
| [bingo_game/ui/finestra_gioco.py](../../bingo_game/ui/finestra_gioco.py#L1101) | ~1101-1110 (blocco post-verifica in `_on_verifica`) | D1, D4 |

Nessuna modifica necessaria a: `renderer_wx.py`, `PannelloRiepilogoFinale`, `base_renderer.py`.

---

## 9. Conclusioni

Il report visivo di fine partita è stato implementato correttamente a livello
di struttura dati, vocalizzazione e pannello `PannelloRiepilogoFinale`.
Il collegamento visivo è stato interrotto da un errore nella gestione del
layout wxPython (D1) e da un'implementazione incompleta della transizione
tra schermate (D2). I quattro difetti sono tutti isolati in `finestra_gioco.py`
e richiedono modifiche minime. Il fix è consigliato come alta priorità
perché la finestra grigia è l'unica interfaccia visiva a fine partita e
rappresenta una regressione percettibile per gli utenti vedenti.
