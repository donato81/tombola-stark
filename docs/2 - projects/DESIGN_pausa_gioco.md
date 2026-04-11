---
type: design
titolo: Pausa del gioco su richiesta del giocatore umano
feature: pausa_gioco
versione: 1.2.0
data_creazione: 2026-04-11
agent: Agent-Design
status: REVIEWED
---

# Design: Pausa del gioco (v1.2.0)

## 1. Idea in 3 righe

Il giocatore umano puo sospendere la partita in qualsiasi momento
(Ctrl+P o pulsante "Pausa") durante il gioco attivo. Tutti i timer
si congelano; alla ripresa ripartono dal tempo residuo. Il dominio
non viene toccato: la pausa e un comportamento esclusivo del layer
di presentazione.

---

## 2. Attori e Concetti

### Attori

- **Giocatore umano**: unico attore che attiva/disattiva la pausa.
- **FinestraGioco**: gestore della macchina a stati UI e dei timer.
- **WxRenderer**: responsabile dell'annuncio vocale pausa/ripresa.

### Concetti chiave

- **Stato UI "in_pausa"**: nuovo valore di `_fase_turno_ui`.
  Aggiunto alla macchina a stati di FinestraGioco.
- **Fase pre-pausa**: variabile `_fase_pre_pausa` che memorizza
  lo stato da cui si e entrati in pausa.
- **Tempo residuo timer azione**: `_ms_residui_azione` calcolato come
  `_durata_finestra_corrente_ms - _ms_trascorsi_azione`.
- **Tempo residuo timer pausa turno**: calcolato tramite timestamp
  di avvio esposto da `_avvio_pausa_turno_ms` e `time.monotonic()`.
- **Guard pausa**: controllo `_in_pausa` inserito nei callback
  di progressione automatica (bot, tick timer).

### Vincolo: pausa attiva solo durante partita attiva

La pausa e disponibile solo quando almeno un numero e stato estratto
(`tabellone.get_conteggio_estratti() > 0`) e la partita non e terminata.
Prima del primo turno il tasto Ctrl+P e ignorato e il pulsante e disabilitato.

---

## 3. Flussi Concettuali

### 3.1 Attivazione pausa

```
Utente: Ctrl+P  (o clic su btn_pausa)
   |
   v
_toggle_pausa():
   _in_pausa == False?  SI
   |
   v
_metti_in_pausa():
   1. Controlla precondizioni (partita attiva, turno avviato)
   2. Memorizza _fase_pre_pausa = _fase_turno_ui
   3. Calcola e salva tempo residuo timer azione / timer pausa turno
   4. Chiama _ferma_tutti_i_timer()
   5. Imposta _in_pausa = True
   6. Imposta _fase_turno_ui = "in_pausa"
   7. Disabilita btn_principale e btn_pausa_aggiorna_etichetta
   8. renderer.annuncia_pausa("Gioco in pausa.")
```

### 3.2 Ripresa gioco

```
Utente: Ctrl+P  (o clic su btn_pausa)
   |
   v
_toggle_pausa():
   _in_pausa == True?  SI
   |
   v
_riprendi_gioco():
   1. Imposta _in_pausa = False
   2. Ripristina _fase_turno_ui = _fase_pre_pausa
   3. Aggiorna il pulsante principale
   4. Riavvia timer dal tempo residuo:
      - fase "attesa_reclami" e _ms_residui_azione > 0:
          _avvia_timer_azione(_ms_residui_azione)
      - fase "pausa_turno" e _ms_residui_pausa > 0:
          _avvia_pausa_turno(_ms_residui_pausa)
   5. renderer.annuncia_pausa(testo_stato_completo)
      Testo: "Gioco ripreso. Fase: <desc>. Tempo rimanente: <N> secondi."
```

### 3.3 Guard protezione progressione automatica

```
_on_pulsante_principale():
   if _in_pausa: return   <-- blocca click durante pausa

_on_tick_azione():
   gia' protetto: _fase_turno_ui != "attesa_reclami" blocca il tick
   (perche _fase_turno_ui = "in_pausa" durante la pausa)

_on_tick_pausa():
   timer e stato al momento della pausa; il timer sara' gia' fermato
   da _ferma_tutti_i_timer(); il guard e comunque aggiunto per robustezza

_dichiara_fine_bot():
   if _fase_turno_ui != "attesa_reclami": return
   (gia' presente; nessun bot puo dichiarare durante la pausa)
```

---

## 4. Decisioni Architetturali

### 4.1 Pausa solo nel layer UI — zero modifiche al dominio

La pausa non e una regola di business della tombola.
`Partita.stato_partita` continua ad avere solo i valori
`non_iniziata`, `in_corso`, `terminata`. Nessun metodo del dominio
viene modificato.

**Motivazione**: rispetta la Clean Architecture. Il dominio e la
source of truth per le regole di gioco, non per la UX.

### 4.2 Timer azione: residuo tramite ms_trascorsi (gia' disponibile)

Il timer azione usa un tick da 500 ms e mantiene `_ms_trascorsi_azione`
aggiornato. Il residuo e calcolato come:
```python
_ms_residui_azione = max(
    0, _durata_finestra_corrente_ms - _ms_trascorsi_azione
)
```
Nessun import di `time` necessario per questo timer.

### 4.3 Timer pausa turno: residuo tramite timestamp monotonic

Il timer pausa turno e un ONE_SHOT senza tick ricorrente.
Per calcolare il residuo si aggiunge l'attributo
`_avvio_pausa_turno_mono: float = 0.0` (valore di `time.monotonic()`
al momento dell'avvio) e si calcola:
```python
import time
elapsed = (time.monotonic() - _avvio_pausa_turno_mono) * 1000
_ms_residui_pausa = max(0, durata_ms - int(elapsed))
```

`_avvio_pausa_turno_mono` viene impostato all'inizio di
`_avvia_pausa_turno()`.

### 4.4 Pulsante "Pausa" posizionato nel panel, dopo il principale

Il pulsante Pausa e posizionato subito dopo `_btn_principale`
nel sizer verticale. E visibile e raggiungibile via Tab ma
disabilitato fino al primo turno avviato. Il testo cambia in:
- "Metti in pausa" (partita attiva)
- "Riprendi" (in pausa)

### 4.5 Annuncio vocale di ripresa: testo completo di stato

Alla ripresa il renderer vocalizza un messaggio che include:
- lo stato della fase pre-pausa (in italiano leggibile)
- il tempo rimanente in secondi (se un timer era attivo)

Mappatura fasi -> descrizione leggibile:
- `"attesa_estrazione"` -> "Attesa nuova estrazione"
- `"attesa_reclami"` -> "Finestra reclami aperta"
- `"pausa_turno"` -> "Pausa breve tra turni"

### 4.6 Hotkey Ctrl+P — intercettazione a livello frame

Ctrl+P e intercettato in `_on_char_hook` (EVT_CHAR_HOOK) come
Categoria B. Nessun conflitto con binding esistenti:
`Ctrl+P` era il binding per "passa turno" nelle versioni precedenti
ma e gia' stato sostituito con `Ctrl+Enter` in v0.9.6.
Ctrl+P e quindi completamente libero a partire da v0.9.6.

---

## 5. Rischi e Vincoli

### R1 — Bot schedulati con CallLater durante la pausa (BASSO)

I bot sono schedulati con `wx.CallLater`. Se la pausa avviene
dopo la schedulazione, il callback del bot arriva durante la pausa.
**Mitigazione**: il guard `if self._fase_turno_ui != "attesa_reclami": return`
in `_dichiara_fine_bot` e gia' presente e sufficiente. Il bot non
provoca progressione durante la pausa.

### R2 — Residuo timer pausa turno < 0 (BASSO)

Se il giocatore mette in pausa e riprende molto velocemente, il
residuo potrebbe essere quasi uguale alla durata originale, mai negativo
(grazie al `max(0, ...)`). Non ci sono rischi di comportamento anomalo.

### R3 — Pausa durante la fase "attesa_estrazione" senza timer (BASSO)

Se l'utente preme Ctrl+P in fase "attesa_estrazione" (nessun timer attivo),
`_ms_residui_azione` e `_ms_residui_pausa` restano 0. Alla ripresa
non viene riavviato nessun timer: il gioco attende semplicemente il
prossimo Ctrl+Enter. Comportamento corretto.

### R4 — Conflitto NVDA con Ctrl+P (DA VERIFICARE)

Ctrl+P non ha binding NVDA predefiniti noti, ma va verificato
empiricamente nell'ambiente reale. Se necessario, il fallback e F7.

### R5 — Accessibilita pulsante Pausa

Il pulsante deve avere un nome accessibile (`SetName` o `SetLabel`)
coerente con il suo stato corrente per essere correttamente
annunciato da NVDA quando riceve il focus via Tab.
