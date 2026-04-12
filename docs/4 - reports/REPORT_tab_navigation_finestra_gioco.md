# Report: Tab navigation non funzionante nella finestra di gioco

- Data analisi: 2026-04-12
- Agente: Agent-Analyze
- File coinvolto: bingo_game/ui/finestra_gioco.py
- Severita: alta (blocca accessibilita tastiera su controlli critici)

---

## Sintomo

Nella finestra di gioco, il tasto Tab non permette di raggiungere:

- Pulsante "Cartella precedente" (freccia sinistra)
- Pulsante "Cartella successiva" (freccia destra)
- Pulsanti selezione diretta cartella (1..N)
- Pulsanti dichiarazione vittoria (Ambo, Terno, Quaterna, Cinquina, Tombola)

Il focus rimane intrappolato nel PannelloGriglia senza possibilita
di spostarsi ai controlli successivi con Tab.

---

## Causa principale: wx.WANTS_CHARS blocca Tab traversal

### Dove

Riga 216 di finestra_gioco.py, nel costruttore di PannelloGriglia:

```python
super().__init__(parent, style=wx.WANTS_CHARS | wx.TAB_TRAVERSAL)
```

### Perche

Il flag `wx.WANTS_CHARS` indica a wxWidgets che il pannello vuole
ricevere TUTTI i tasti, inclusi i tasti di navigazione come Tab.
Questo sovrascrive il comportamento standard di `wx.TAB_TRAVERSAL`.

La documentazione wxWidgets e esplicita:

> If you need to use this style in order to get the arrows or etc.,
> but would still like to have normal keyboard navigation take place,
> you should call Navigate() in response to the tab key being pressed.

### Cosa succede oggi

1. L'utente preme Tab nel PannelloGriglia
2. EVT_CHAR_HOOK su FinestraGioco: Tab non e gestito, chiama event.Skip()
3. EVT_KEY_DOWN su PannelloGriglia: Tab non e gestito esplicitamente,
   cade nel ramo event.Skip() finale (riga circa 328)
4. `WANTS_CHARS` impedisce a wxWidgets di attivare la navigazione
   standard. Il focus resta sul pannello.

### Cosa manca

Nel metodo `PannelloGriglia._on_key_down` non c'e nessun blocco
per `wx.WXK_TAB`. Non c'e nessuna chiamata a `self.Navigate()`
in tutto il file. Grep conferma: zero occorrenze di `Navigate(`
o `WXK_TAB` nell'intero progetto.

---

## Causa secondaria: pulsanti disabilitati all'avvio

Tutti i pulsanti coinvolti sono creati in stato `Disable()`:

- `_btn_freccia_sx.Disable()` (riga ~427)
- `_btn_freccia_dx.Disable()` (riga ~437)
- Pulsanti premi: `btn.Disable()` nel loop (riga ~475)
- Pulsanti selezione cartella: creati solo dinamicamente al primo turno

Un controllo `wx.Button` disabilitato viene saltato dal ciclo Tab.
Questo significa che anche dopo aver risolto la causa principale,
i pulsanti sono raggiungibili solo durante le fasi in cui sono abilitati
(tipicamente fase `attesa_reclami` e quando la partita e attiva).

Questo e il comportamento corretto: i pulsanti devono essere
raggiungibili solo quando sono operativi. Tuttavia questo va
documentato chiaramente per l'utente.

---

## Causa terziaria: ordine Tab dei pulsanti selezione cartella

I pulsanti selezione diretta cartella (1..N) sono creati
dinamicamente dal metodo `_crea_pulsanti_selezione_cartella`
(riga ~1063), solo dopo il primo turno.

Poiche vengono creati dopo tutti gli altri widget, la loro
posizione nel ciclo Tab sara dopo il log_ctrl, non tra le
frecce di navigazione e i pulsanti premi come il layout
visivo suggerisce.

Non c'e nessuna chiamata a `MoveAfterInTabOrder()` per
correggere la sequenza. Questo viola la regola delle
ui.instructions.md:

> Ordine TAB logico: usa MoveAfterInTabOrder() se ordine di
> creazione non corrisponde all'ordine di navigazione atteso

---

## Riepilogo problemi trovati

1. `PannelloGriglia` usa `wx.WANTS_CHARS` senza gestire Tab
   con `Navigate()` — blocca completamente lo scorrimento Tab
2. Nessuna chiamata a `MoveAfterInTabOrder()` per i pulsanti
   selezione cartella creati dinamicamente
3. I pulsanti disabilitati sono correttamente saltati dal Tab,
   ma serve annuncio vocale che informi l'utente sullo stato

---

## Correzione proposta

### Fix 1 — Gestire Tab in PannelloGriglia._on_key_down

Aggiungere prima del ramo event.Skip() finale:

```python
# Tab / Shift+Tab — navigazione tra controlli
if key == wx.WXK_TAB:
    flags = wx.NavigationKeyEvent.IsForward
    if shift:
        flags = wx.NavigationKeyEvent.IsBackward
    self.Navigate(flags)
    return
```

### Fix 2 — Ordine Tab per pulsanti selezione cartella

In `_crea_pulsanti_selezione_cartella`, dopo la creazione
dei pulsanti, aggiungere chiamate `MoveAfterInTabOrder()`
per posizionarli nell'ordine logico:

```python
# Posiziona dopo le frecce di navigazione, prima dei premi
if self._pulsanti_selezione:
    self._pulsanti_selezione[0].MoveAfterInTabOrder(self._btn_freccia_dx)
    for i in range(1, len(self._pulsanti_selezione)):
        self._pulsanti_selezione[i].MoveAfterInTabOrder(
            self._pulsanti_selezione[i - 1]
        )
```

### Fix 3 (opzionale) — Feedback vocale su Tab

Aggiungere un annuncio vocale quando il focus arriva su
pulsanti critici (frecce, selezione, premi) per confermare
all'utente dove si trova nel ciclo Tab.

---

## Ordine Tab atteso dopo le correzioni

1. Pulsante principale (Inizia partita / Passa turno)
2. Pulsante pausa
3. PannelloGriglia (navigazione tastiera cartella)
4. Pulsante freccia sinistra (Cartella precedente)
5. Pulsante freccia destra (Cartella successiva)
6. Pulsanti selezione cartella (1..N) — se creati
7. Pulsanti premi (Ambo, Terno, Quaterna, Cinquina, Tombola)
8. Log annunci

Controlli disabilitati vengono saltati automaticamente.

---

## File da modificare

- bingo_game/ui/finestra_gioco.py (3 interventi)

## Impatto docs

- docs/API.md: nessun impatto (non cambia interfaccia pubblica)
- docs/ARCHITECTURE.md: nessun impatto (non cambia architettura)
- CHANGELOG.md: aggiungere voce Fixed per accessibilita Tab
