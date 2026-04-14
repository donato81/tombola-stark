---
type: design
feature: pulsanti_interattivi
agent: Agent-Design
status: REVIEWED
version: v0.12.0
date: 2026-04-12
---

# DESIGN — Pulsanti interattivi FinestraGioco v0.12.0

## Stato

`REVIEWED` — Approvato per pianificazione.

---

## Scope

Aggiungere tre gruppi di pulsanti cliccabili a `FinestraGioco`
(`bingo_game/ui/finestra_gioco.py`) per consentire l'interazione
via mouse equivalente ai tasti già esistenti.
Nessuna modifica a logica di gioco, eventi, renderer vocale o binding tastiera.

---

## Contesto architetturale

| Elemento | Ruolo |
|----------|-------|
| `FinestraGioco` | Frame principale — coordina il gioco |
| `self._comandi` | `ComandiGiocatoreUmano` — source of commands |
| `self._dispatch(esito)` | Invia un esito al renderer |
| `self._fase_turno_ui` | Fase corrente: `attesa_estrazione`, `attesa_reclami`, `pausa_turno`, `in_pausa` |
| `self._turno_corrente` | Numero turno corrente |
| `self._partita.premi_tipo_chiusi` | Set tipi premio definitivamente assegnati |
| `aggiorna_stato_pulsante()` | Punto canonico di abilitazione/disabilitazione pulsanti |
| `_build_ui()` | Costruisce il layout iniziale |
| `sizer_griglie` | BoxSizer orizzontale con tabellone + cartella |

---

## Gruppo 1 — Frecce navigazione cartella

### Descrizione

Due pulsanti `◀` e `▶` ai lati del `PannelloCartella`.

### Layout

```
sizer_griglie (HORIZONTAL):
  [pannello_tabellone]
  [btn_freccia_sx ◀]  [pannello_cartella]  [btn_freccia_dx ▶]
```

### Comportamento

| Evento | Azione |
|--------|--------|
| Click `◀` | `self._dispatch(self._comandi.cartella_precedente())` |
| Click `▶` | `self._dispatch(self._comandi.cartella_successiva())` |

### Abilitazione

- Abilitate quando `get_conteggio_estratti() > 0` e partita non terminata e
  fase non in `("in_pausa", "pausa_turno")`.
- Disabilitate in tutti gli altri stati.

### Accessibilità

- `btn.SetName("Cartella precedente")` / `btn.SetName("Cartella successiva")`
- No `TAB_TRAVERSAL` aggiuntivo — entrano nel normale ciclo Tab.

### Stile

- Background: `COLORE_ACCENT_BLU` (`#1565C0`)
- Foreground: `COLORE_TESTO_CHIARO`
- Dimensione: `DIMENSIONE_BTN_FRECCIA` (`(40, 40)`) — costante già in `tema.py`

---

## Gruppo 2 — Selezione diretta cartella (pulsanti 1…N)

### Descrizione

Riga orizzontale di pulsanti numerati (1…N) per saltare direttamente a una
cartella. Creati dinamicamente al primo avvio della partita (quando le
cartelle esistono).

### Layout

```
sizer (VERTICAL):
  sizer_griglie
  sizer_selezione (HORIZONTAL) ← nuova riga
  sizer_premi
  log
```

### Creazione dinamica

Metodo `_crea_pulsanti_selezione_cartella()`:
1. Legge `self._partita.giocatori` per trovare il primo non-automatico.
2. Crea da 1 a 6 `wx.Button` con label `"1"`, `"2"`, … `"N"`.
3. Collega ogni pulsante a `_on_seleziona_cartella(n, event)`.
4. Imposta `SetName(f"Cartella {n}")`.
5. Aggiunge a `self._sizer_selezione`, relayouta il pannello.

Chiamata da `_on_pulsante_principale()` alla condizione:
- `fase == "attesa_estrazione"` E `get_conteggio_estratti() == 0`
- (= prima che venga eseguito il primo turno)

### Evidenziazione cartella corrente

- Metodo privato `_aggiorna_evidenziazione_selezione(numero_cartella)`:
  colora pulsante attivo con `COLORE_ACCENT_BLU`/`COLORE_TESTO_CHIARO`;
  gli altri con `COLORE_BTN_NEUTRO`/`COLORE_TESTO_SCURO`.
- Metodo pubblico `aggiorna_selezione_cartella(numero)` (duck typing per il renderer).
- Chiamata dal renderer in `_handle_focus_cartella_impostato` tramite:
  ```python
  if hasattr(self._finestra, "aggiorna_selezione_cartella"):
      self._finestra.aggiorna_selezione_cartella(evento.numero_cartella)
  ```

### Stile iniziale

- Background: `COLORE_BTN_NEUTRO` (`#E0E0E0`)
- Foreground: `COLORE_TESTO_SCURO`
- Dimensione: `DIMENSIONE_BTN_SELEZIONE_CARTELLA` (`(36, 36)`) — costante già in `tema.py`

---

## Gruppo 3 — Pulsanti premi (Ambo … Tombola)

### Descrizione

Riga fissa di 5 pulsanti per dichiarare i premi.

### Layout

```
sizer (VERTICAL):
  sizer_griglie
  sizer_selezione
  sizer_premi (HORIZONTAL) ← nuova riga   [Ambo][Terno][Quaterna][Cinquina][Tombola]
  log
```

### Comportamento

| Pulsante | Azione |
|----------|--------|
| Ambo | `_dispatch(_comandi.annuncia_vittoria("ambo", _turno_corrente))` |
| Terno | `_dispatch(_comandi.annuncia_vittoria("terno", _turno_corrente))` |
| Quaterna | `_dispatch(_comandi.annuncia_vittoria("quaterna", _turno_corrente))` |
| Cinquina | `_dispatch(_comandi.annuncia_vittoria("cinquina", _turno_corrente))` |
| Tombola | `_dispatch(_comandi.annuncia_vittoria("tombola", _turno_corrente))` |

Collegate tramite `functools.partial` per chiusura corretta del valore `tipo`.

### Abilitazione per fase

| Fase | Stato |
|------|-------|
| `attesa_estrazione` | Disabilitati |
| `attesa_reclami` | Abilitati (salvo premio già chiuso) |
| `pausa_turno` | Disabilitati |
| `in_pausa` | Disabilitati |

Aggiornamento in `aggiorna_stato_pulsante()`.

### Disabilitazione permanente per premio già assegnato

Se `tipo in self._partita.premi_tipo_chiusi`:
- Disabilitato permanentemente (anche in `attesa_reclami`).
- Label modificata: `"Ambo ✓"`, `"Terno ✓"`, etc.

### Stile

| Pulsante | Background | Foreground |
|----------|-----------|-----------|
| Ambo–Cinquina | `COLORE_ACCENT_ROSSO` (`#E53935`) | `#FFFFFF` |
| Tombola | `COLORE_BTN_TOMBOLA` (`#FFB300`) | `COLORE_BTN_TOMBOLA_TESTO` (`#212121`) |

Pulsanti disabilitati: stile nativo wx (non sovrascrivere).

### Accessibilità

- `btn.SetName(f"Dichiara {tipo}")` su ogni pulsante.
- I tasti F1–F5 non vengono toccati.

---

## Dimensione finestra

`DIMENSIONE_FINESTRA_GIOCO` in `tema.py` è già a `(1000, 700)`. Nessuna modifica
necessaria.

---

## File da modificare

| File | Modifiche |
|------|-----------|
| `bingo_game/ui/finestra_gioco.py` | Layout, pulsanti, handler, nuovi metodi |
| `bingo_game/ui/renderers/renderer_wx.py` | `aggiorna_selezione_cartella` in `_handle_focus_cartella_impostato` |
| `CHANGELOG.md` | Entry `### Fase 2 — Pulsanti interattivi` in `[Unreleased]` |

`bingo_game/ui/tema.py` — nessuna modifica (costanti già presenti).

## File da NON toccare

Tutto il resto incluso: binding tastiera, renderer vocale, `partita.py`,
`comandi_partita.py`, `bingo_game/events/`, `bingo_game/players/`.

---

## Regole invarianti

1. Nessun binding tastiera modificato (Categorie A, B, C).
2. Nessun metodo renderer che produce testo o voce modificato.
3. Ogni handler click termina con `return` senza `event.Skip()`.
4. Ordine nel sizer: tabellone+cartella → frecce → selezione diretta → premi → log.
5. Docstring brevi su ogni nuovo metodo privato.

---

## Rischi e vincoli

| Rischio | Mitigazione |
|---------|-------------|
| `_pulsanti_selezione` creati più volte | Guard `if self._pulsanti_selezione: return` |
| `_on_premio` chiude valore sbagliato in loop | `functools.partial(self._on_premio, tipo)` |
| Freeze wx su relayout dinamico | `self.Layout()` dopo aggiunta a sizer |
| `premi_tipo_chiusi` non presente su Partita stub | `getattr(self._partita, "premi_tipo_chiusi", set())` |
| `cartella_precedente`/`successiva` non nei mock | Test esistenti non devono essere modificati come logica |
