---
type: design
titolo: Annuncio posizione focus dopo il benvenuto NVDA
feature: annuncio_posizione_focus_post_benvenuto_nvda
versione: 0.12.5
data_creazione: 2026-04-14
agent: Agent-Design
status: REVIEWED
---

# DESIGN — Annuncio posizione focus dopo il benvenuto NVDA

## Idea in 3 righe

All'avvio della finestra di gioco il benvenuto deve restare il primo annuncio
udibile, ma non basta piu: subito dopo l'utente deve ricevere anche la posizione
logica iniziale sulla griglia. La soluzione scelta non costruisce una nuova stringa
ad hoc nel benvenuto, ma riusa il canale gia esistente di stato focus tramite
`self._comandi.stato_focus()`, schedulato in un secondo callback differito.

---

## Obiettivo

Far sentire a NVDA due annunci distinti e ordinati all'ingresso in
`FinestraGioco`:

1. prima il messaggio di benvenuto orientativo;
2. poi un secondo annuncio esplicito della posizione iniziale, ad esempio
   "Cartella 1, riga 1, colonna 1".

Il requisito chiave non e solo parlare la posizione, ma farlo senza rompere il
fix gia validato sul benvenuto: l'ordine deve restare stabile, il secondo
annuncio non deve interrompere il primo e la soluzione deve sfruttare il path
event-driven gia presente nel renderer invece di duplicare logica testuale.

---

## Attori e Concetti

| Attore / Concetto | File | Ruolo |
|---|---|---|
| FinestraGioco | bingo_game/ui/finestra_gioco.py | orchestra focus iniziale, benvenuto e secondo annuncio post-benvenuto |
| `_imposta_focus_iniziale()` | bingo_game/ui/finestra_gioco.py | esegue i dispatch iniziali silenziosi e stabilizza il focus reale sulla griglia |
| `_annuncia_benvenuto_iniziale()` | bingo_game/ui/finestra_gioco.py | punto da cui parte il benvenuto e da cui deve essere schedulato l'annuncio della posizione |
| ComandiPartita.stato_focus | bingo_game/comandi_partita.py | comando applicativo gia esistente che restituisce lo stato logico corrente del focus |
| `EventoStatoFocusCorrente` | bingo_game/events/eventi_output_ui_umani.py | evento strutturato con cartella/riga/colonna gia disponibile nel sistema |
| WxRenderer | bingo_game/ui/renderers/renderer_wx.py | gestisce gia l'evento di stato focus e vocalizza la posizione corrente |
| NVDA / sintetizzatore condiviso | runtime Windows/NVDA | vincolo esterno che impone sequenze non sovrapposte e timing prudente |

---

## Flussi Concettuali

### Flusso attuale dopo il fix del benvenuto

```text
FinestraGioco._imposta_focus_iniziale()
  ├─ _avvio_silenzioso = True
  ├─ dispatch focus cartella/riga/colonna (silenziosi)
  ├─ _avvio_silenzioso = False
  ├─ aggiornamenti visivi
  ├─ SetFocus() sulla griglia
  └─ wx.CallLater(350, _annuncia_benvenuto_iniziale)

_annuncia_benvenuto_iniziale()
  └─ renderer.mostra_messaggio_benvenuto(...)
```

Risultato: il benvenuto viene letto correttamente, ma l'utente non riceve un
annuncio esplicito della posizione logica iniziale dopo che il focus e stato
stabilizzato in modo silenzioso.

### Flusso target Phase 2

```text
FinestraGioco._imposta_focus_iniziale()
  ├─ dispatch iniziali silenziosi
  ├─ aggiornamenti visivi
  ├─ SetFocus() sulla griglia
  └─ wx.CallLater(350, _annuncia_benvenuto_iniziale)

_annuncia_benvenuto_iniziale()
  ├─ renderer.mostra_messaggio_benvenuto(...)
  └─ wx.CallLater(<delay_tuned>, _annuncia_posizione_focus_iniziale)

_annuncia_posizione_focus_iniziale()
  └─ self._dispatch(self._comandi.stato_focus())
    └─ renderer.render_esito(...)
      └─ _handle_stato_focus_corrente()
        └─ vocalizza "Cartella X, riga Y, colonna Z"
```

Il secondo annuncio non nasce da una nuova composizione testuale nel metodo di
benvenuto. Nasce dalla stessa pipeline gia usata durante la navigazione reale,
cosi la finestra espone all'utente lo stato iniziale tramite lo stesso contratto
che usera poi per il resto della partita.

### Sequenza uditiva attesa

```text
1. La finestra si apre e stabilizza il focus reale sulla griglia
2. NVDA esaurisce gli annunci nativi immediati di show/focus
3. Parte il benvenuto orientativo
4. Dopo un secondo delay controllato, parte l'annuncio della posizione iniziale
5. L'utente sente due messaggi distinti: orientamento prima, coordinate poi
```

---

## Decisioni Architetturali

### D1 — Il benvenuto resta sempre il primo annuncio applicativo

La sequenza validata in v0.12.4 non va invertita. L'annuncio della posizione non
puo anticipare il benvenuto ne fondersi con esso nello stesso payload vocale.

Motivo: il benvenuto ha valore orientativo globale, mentre la posizione e un
dettaglio locale di navigazione. Invertire l'ordine peggiorerebbe il contesto
iniziale percepito dall'utente e rischierebbe di riaprire il problema di overlap
tra focus e parlato gia corretto.

### D2 — Riutilizzare il path esistente `stato_focus()`

La posizione iniziale deve essere annunciata richiamando il comando gia esistente
`self._comandi.stato_focus()` tramite il percorso gia usato dalla finestra,
cioe `self._dispatch(...)`.

Motivo: il sistema possiede gia un evento dedicato, un renderer che lo interpreta
e una semantica vocale coerente per cartella/riga/colonna. Duplicare la stringa
nel metodo di benvenuto introdurrebbe una seconda fonte di verita e aumenterebbe
il rischio di divergenza tra annuncio iniziale e annunci successivi di navigazione.

### D3 — Secondo callback differito e non interrupting

Dopo `mostra_messaggio_benvenuto(...)` va schedulato un secondo `wx.CallLater`
dedicato all'annuncio della posizione. Questo secondo annuncio deve essere non
interrompente rispetto al benvenuto e il suo delay va tarato empiricamente per
evitare sovrapposizioni in NVDA.

Motivo: lo scopo non e prevaricare il benvenuto ma concatenare due messaggi.
Serve quindi una separazione temporale esplicita tra i due eventi applicativi,
con tuning sufficiente a lasciare al sintetizzatore il tempo di completare o
quasi completare il primo parlato prima dell'avvio del secondo.

### D4 — Il renderer puo restare invariato

`renderer_wx.py` non richiede verosimilmente modifiche strutturali per questa
feature, perche il supporto a `EventoStatoFocusCorrente` e gia presente.

Motivo: la nuova feature estende l'orchestrazione della finestra, non il contratto
di rendering. Eventuali modifiche al renderer sarebbero giustificate solo se i
test evidenziassero la necessita di un helper tecnico minimo, non per la logica
funzionale principale.

### D5 — La fix resta confinata al layer presentation

La responsabilita del nuovo comportamento appartiene alla sequenza di bootstrap
UI della finestra di gioco e ai suoi test di integrazione UI.

Motivo: non cambia alcuna regola di dominio. Il layer application fornisce gia il
comando necessario e il renderer presentation sa gia come esporre l'evento.

---

## Rischi e Vincoli

### R1 — Timing empirico su NVDA reale

Il ritardo tra benvenuto e annuncio posizione non deriva da un contratto forte di
wxPython o NVDA. Va quindi considerato un parametro empirico da validare su
Windows con screen reader reale.

### R2 — Sovrapposizione se il delay e troppo corto

Se il secondo callback parte troppo presto, la posizione puo sovrapporsi al
benvenuto o troncarne la percezione. Questo vanificherebbe il requisito primario
di lasciare il benvenuto come primo messaggio compiuto.

### R3 — Ridondanza se il delay e troppo lungo

Se il secondo callback e eccessivamente ritardato, l'utente percepisce una pausa
artificiale e la posizione perde il valore di continuita immediata rispetto al
benvenuto iniziale.

### R4 — Nessuna duplicazione testuale fuori dal path ufficiale

Qualsiasi scorciatoia che costruisce manualmente la frase in `_annuncia_benvenuto_iniziale()`
crea accoppiamento inutile e rende piu fragile la manutenzione dei testi vocali.

### R5 — Copertura automatica solo parziale

I test possono verificare ordine delle chiamate, schedulazione e riuso del comando
`stato_focus()`, ma non garantiscono da soli la resa audio finale di NVDA. Resta
necessaria validazione manuale accessibile.

---

## File coinvolti

| File | Operazione | Motivo |
|---|---|---|
| bingo_game/ui/finestra_gioco.py | MODIFY | aggiungere la seconda schedulazione post-benvenuto e riusare `self._comandi.stato_focus()` |
| tests/ui/test_finestra_gioco.py | LIKELY MODIFY | verificare ordine: benvenuto prima, annuncio posizione dopo, senza duplicare stringhe locali |
| bingo_game/ui/renderers/renderer_wx.py | NO CHANGE atteso | il path `EventoStatoFocusCorrente` esiste gia e dovrebbe restare invariato |

---

## Criteri di accettazione

- All'apertura di `FinestraGioco` il benvenuto resta il primo annuncio applicativo percepito.
- Dopo il benvenuto viene emesso un secondo annuncio distinto con cartella, riga e colonna iniziali.
- L'annuncio della posizione usa il path `self._comandi.stato_focus()` + renderer esistente, senza nuova stringa duplicata nel benvenuto.
- Il secondo annuncio e schedulato con delay dedicato e non interrompe il benvenuto.
- `renderer_wx.py` puo restare invariato salvo minimi adattamenti tecnici non funzionali.
- La validazione manuale con NVDA conferma assenza di overlap percepibile tra i due messaggi.