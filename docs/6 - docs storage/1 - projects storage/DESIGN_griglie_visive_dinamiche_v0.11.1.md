---
type: design
feature: griglie_visive_dinamiche
agent: Agent-Design
status: REVIEWED
version: v0.11.1
date: 2026-04-11
---

# DESIGN — Collegamento dinamico griglie visive ↔ stato di gioco

## 1. Idea in 3 righe

Aggiungere metodi `aggiorna(...)` a `PannelloTabellone` e `PannelloCartella` in
`finestra_gioco.py` per ridipingere le celle usando i colori di `tema.py` in base
allo stato reale della `Partita`. Collegare il metodo privato `_aggiorna_griglie_visive()`
ai tre momenti chiave del ciclo di turno.

## 2. Attori e Concetti

| Attore / Concetto | Ruolo |
|---|---|
| `PannelloTabellone` | Esistente; si aggiunge dizionario `_celle: dict[int, wx.StaticText]` e metodo `aggiorna(numeri_estratti)` |
| `PannelloCartella` | Esistente; si sostituisce `_PLACEHOLDER` con `_celle: list[list[wx.StaticText]]` e si aggiunge `aggiorna(griglia, numeri_segnati, numeri_estratti)` |
| `FinestraGioco._aggiorna_griglie_visive()` | Nuovo metodo privato; coordina i due pannelli con i dati live |
| `Cartella.get_griglia_semplice()` | API dominio: restituisce `tuple[tuple[int\|str,...],...]` 3×9 — `"-"` per celle vuote |
| `Cartella.numeri_segnati` | Attributo `set[int]` già presente nel dominio |
| `GiocatoreUmano._indice_cartella_focus` | Indice 0-based della cartella in focus; accesso via `getattr` per robustezza |
| `Tabellone.numeri_estratti` | `set[int]` con i numeri già usciti |
| `tema.py` | Unicamente costanti colore; zero modifiche |

## 3. Flussi Concettuali

```
PannelloTabellone._build_ui:
  self._celle: dict[int, wx.StaticText] = {}
  for row in 0..9, col in 0..8:
    numero = col*10 + row + 1
    cell = wx.StaticText(...)
    self._celle[numero] = cell

PannelloTabellone.aggiorna(numeri_estratti):
  for numero, cell in self._celle.items():
    if numero in numeri_estratti:
      cell.SetBackgroundColour(COLORE_CELLA_ESTRATTO)
      cell.SetForegroundColour(COLORE_TESTO_CHIARO)
    else:
      cell.SetBackgroundColour(COLORE_CELLA_VUOTA)
      cell.SetForegroundColour(COLORE_CELLA_TESTO_INATTIVO)
  self.Refresh()

PannelloCartella._build_ui:
  self._celle: list[list[wx.StaticText]] = []
  (NO _PLACEHOLDER, celle inizialmente bianche/vuote)

PannelloCartella.aggiorna(griglia, numeri_segnati, numeri_estratti):
  for row in 0..2:
    for col in 0..8:
      val = griglia[row][col]  # "-" o int
      cell = self._celle[row][col]
      if isinstance(val, str):  # "-" = vuota
        ...COLORE_CELLA_CARTELLA_VUOTA, label=""
      elif val in numeri_segnati:
        ...COLORE_CELLA_SEGNATA, COLORE_TESTO_CHIARO
      elif val in numeri_estratti:
        ...COLORE_CELLA_ESTRATTA_NON_SEGNATA, COLORE_TESTO_SCURO
      else:
        ...COLORE_CELLA_CARTELLA_NUMERO, COLORE_TESTO_SCURO
  self.Refresh()

FinestraGioco._aggiorna_griglie_visive():
  pannello_tabellone.aggiorna(partita.tabellone.numeri_estratti)
  giocatore_umano = next(g for g not automatico, None)
  if giocatore_umano is None or not giocatore_umano.cartelle: return
  indice = getattr(giocatore_umano, '_indice_cartella_focus', None) or 0
  cartella = giocatore_umano.cartelle[indice]
  pannello_cartella.aggiorna(
    griglia=cartella.get_griglia_semplice(),
    numeri_segnati=cartella.numeri_segnati,
    numeri_estratti=partita.tabellone.numeri_estratti,
  )

Punti di chiamata in FinestraGioco:
  1. _on_pulsante_principale → ramo "attesa_estrazione"
     → subito dopo annuncia_numero_estratto(...)
  2. _esegui_verifica_premi
     → subito dopo annuncia_premi_turno(...)
  3. _imposta_focus_iniziale
     → in coda, dopo vai_a_colonna(1)
```

## 4. Decisioni Architetturali

| Decisione | Motivazione |
|---|---|
| `dict[int, wx.StaticText]` per tabellone | Accesso O(1) per numero; più espressivo di un vettore flat |
| `list[list[wx.StaticText]]` per cartella | Matriciale, allineato con il formato 3×9 di `get_griglia_semplice()` |
| `isinstance(val, str)` per cella vuota | `get_griglia_semplice()` restituisce `"-"` (str), non `0`; controllo type-safe |
| `getattr(giocatore_umano, '_indice_cartella_focus', None)` | Attributo privato ma unico punto di verità dell'indice; `getattr` + fallback 0 garantisce robustezza |
| Solo 3 punti di chiamata | Coprono tutti i momenti visibili: estrazione, verifica premi, avvio partita |
| Nessun nuovo file | Tutta la logica già nel modulo di presentazione |

## 5. Rischi e Vincoli

| Rischio | Mitigazione |
|---|---|
| `get_griglia_semplice()` è immutabile (tuple di tuple) | Iterazione in sola lettura; nessun problema |
| `_indice_cartella_focus` None al primo avvio | Fallback a 0: mostra sempre la prima cartella |
| `Refresh()` senza `Freeze()/Thaw()`: possibile flicker su Windows lento | Accettabile per fase 3; ottimizzazione in fasi future |
| Griglia vuota all'avvio (prima di `_imposta_focus_iniziale`) | Chiamata in `_imposta_focus_iniziale` garantisce che la griglia si popoli all'avvio |
