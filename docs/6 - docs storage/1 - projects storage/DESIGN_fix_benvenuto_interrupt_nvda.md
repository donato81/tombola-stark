---
type: design
titolo: Fix definitivo benvenuto NVDA con focus stabilizzato e annuncio differito
feature: fix_benvenuto_interrupt_nvda
versione: 0.12.4
data_creazione: 2026-04-14
agent: Agent-Design
status: REVIEWED
---

# DESIGN — Fix definitivo benvenuto NVDA con focus stabilizzato e annuncio differito

## Idea in 3 righe

Il fix v0.12.3 non ha risolto il problema perche il benvenuto AO2 continua a
competere con un evento nativo NVDA di gainFocus generato subito dopo la
vocalizzazione. Il focus sulla griglia va quindi stabilizzato per primo e il
benvenuto va emesso solo dopo una breve attesa controllata con `wx.CallLater(350, ...)`.
Il messaggio deve usare `interrupt=True` quando il focus e gia fermo, cosi
l'ultimo evento sul sintetizzatore condiviso e il benvenuto stesso.

---

## Obiettivo

Garantire che all'ingresso nella finestra di gioco NVDA legga in modo affidabile
e completo il messaggio orientativo:

"Sei nella finestra di gioco. Premi Inizia partita o Ctrl+Invio per estrarre
il primo numero. Premi Ctrl+H per la guida ai tasti rapidi."

Il criterio non e piu "parlare prima del focus", ma "parlare quando il focus e
gia stabile", evitando che un evento gainFocus successivo interrompa o sovrascriva
il parlato AO2 sul sintetizzatore condiviso.

---

## Attori e Concetti

| Attore / Concetto | File | Ruolo |
|---|---|---|
| FinestraGioco | bingo_game/ui/finestra_gioco.py | orchestra focus iniziale e schedulazione del benvenuto |
| Pannello griglia | bingo_game/ui/finestra_gioco.py | controllo che deve ricevere il focus reale di avvio |
| WxRenderer | bingo_game/ui/renderers/renderer_wx.py | punto di emissione del messaggio tramite AO2 |
| Vocalizzatore | my_lib/vocalizzatore.py | backend TTS con supporto a `interrompi=True` |
| NVDA gainFocus nativo | runtime Windows/NVDA | annuncio nativo generato dal cambio focus sulla griglia |
| Sintetizzatore condiviso | runtime audio | canale finale dove confluiscono parlato AO2 e annunci NVDA |
| Report analisi precedente | docs/4 - reports/REPORT_ANALISI_benvenuto_ancora_muto_2026-04-14.md | evidenza del fallimento v0.12.3 |

---

## Flussi Concettuali

### Flusso osservato dopo v0.12.3 (ancora difettoso)

```
FinestraGioco._imposta_focus_iniziale()
  ├─ dispatch iniziali silenziosi
  ├─ aggiornamenti visivi/titolo
  ├─ renderer.mostra_messaggio_benvenuto(..., interrupt=True?)
  └─ _pannello_griglia.SetFocus()
       └─ NVDA gainFocus nativo sulla griglia

[sintetizzatore condiviso]
  1. AO2 inizia il benvenuto
  2. NVDA riceve gainFocus subito dopo
  3. l'ultimo evento vince
  4. il benvenuto viene troncato o sostituito
```

Anche con `interrupt=True`, il problema resta se il focus viene cambiato dopo
la vocalizzazione: AO2 e NVDA confluiscono sullo stesso sintetizzatore e il
gainFocus successivo prevale.

### Flusso target definitivo

```
FinestraConfigurazione._on_conferma()
  ├─ FinestraGioco.__init__()
  │    ├─ _build_ui()
  │    ├─ _bind_finestra()
  │    ├─ renderer.aggiorna_finestra(self)
  │    └─ wx.CallAfter(_imposta_focus_iniziale)
  ├─ finestra_gioco.Show()
  └─ self.Hide()

[idle loop]
  └─ _imposta_focus_iniziale()
       ├─ _avvio_silenzioso = True
       ├─ _dispatch x3 (silenziosi)
       ├─ _avvio_silenzioso = False
       ├─ _aggiorna_griglie_visive()
       ├─ _aggiorna_titolo_cartella()
       ├─ _pannello_griglia.SetFocus()          ← focus reale prima del parlato
       └─ wx.CallLater(350, _annuncia_benvenuto_iniziale)

[350 ms dopo, focus stabile]
  └─ _annuncia_benvenuto_iniziale()
       └─ renderer.mostra_messaggio_benvenuto(benvenuto)
            └─ vocalizza_testo(testo, interrompi=True)
```

La finestra entra in uno stato stabile prima della vocalizzazione. Il delay di
350 ms assorbe gli annunci nativi immediati di focus e consente al benvenuto di
diventare l'evento finale e prioritario sul sintetizzatore.

### Sequenza eventi NVDA/AO2 attesa

```
1. Show() della finestra
2. SetFocus() sulla griglia
3. NVDA genera i propri annunci nativi di finestra/focus
4. attesa controllata di 350 ms
5. AO2 emette il benvenuto con interrupt=True
6. nessun ulteriore cambio focus immediato dopo il benvenuto
7. il benvenuto resta udibile fino a completamento
```

---

## Decisioni Architetturali

### D1 — Prima stabilizzare il focus, poi parlare

`_pannello_griglia.SetFocus()` deve avvenire prima dell'annuncio di benvenuto,
non dopo. Il focus iniziale diventa parte della preparazione dello stato UI,
non una conseguenza del parlato.

Motivo: il root cause verificato non e una semplice coda da interrompere, ma la
collisione temporale tra il parlato AO2 e il gainFocus NVDA successivo.

### D2 — Annuncio differito con `wx.CallLater(350, ...)`

Il benvenuto va emesso in un callback separato, schedulato con `wx.CallLater`
di 350 ms dopo il focus iniziale.

Motivo: la finestra ha bisogno di una finestra temporale breve ma esplicita per
lasciare esaurire gli annunci nativi generati da Show/SetFocus/Hide. Il valore
350 ms e la soglia empirica richiesta dal task per trattare il focus come
stabilizzato prima dell'annuncio.

### D3 — `interrupt=True` resta necessario, ma non e sufficiente da solo

Il messaggio di benvenuto deve usare `interrupt=True` nel punto finale di
vocalizzazione oppure tramite un metodo renderer dedicato al benvenuto.

Motivo: quando il callback differito parte, il benvenuto deve ancora avere
priorita massima sulla coda AO2 residua. La differenza rispetto a v0.12.3 e che
ora l'interrupt viene usato dopo la stabilizzazione del focus, non in competizione
con un nuovo evento di focus immediatamente successivo.

### D4 — Nessuna modifica a dominio o backend TTS

La fix resta confinata al layer presentation e alla sequenza UI di bootstrap.
`Vocalizzatore` gia supporta il parametro necessario e non richiede cambiamenti.

---

## Rischi e Vincoli

### R1 — Il valore di 350 ms e empirico

Il delay non e derivato da un contratto wx/NVDA ma da osservazione runtime.
Deve quindi essere trattato come tuning esplicito da verificare manualmente con
NVDA reale su Windows.

### R2 — Ritardo percepibile all'ingresso finestra

L'utente sentira il benvenuto dopo un piccolo intervallo. Il compromesso e
accettato per privilegiare affidabilita e completezza del messaggio rispetto
alla sola immediatezza teorica.

### R3 — Nessun nuovo cambio focus deve seguire il benvenuto

Qualsiasi `SetFocus()`, `Raise()` o navigazione automatica successiva al callback
puo reintrodurre lo stesso problema. La sequenza deve restare monotona: focus,
stabilizzazione, benvenuto, quiete.

### R4 — Accessibilita tastiera invariata

Il focus finale deve restare sulla griglia dopo il completamento del delay e del
messaggio. Va verificato che il ciclo Tab e i binding iniziali rimangano identici
alla UX attuale, senza regressioni all'avvio partita.

---

## File coinvolti

| File | Operazione | Motivo |
|---|---|---|
| bingo_game/ui/finestra_gioco.py | MODIFY | spostare la responsabilita sul focus iniziale stabile e schedulare il benvenuto differito |
| bingo_game/ui/renderers/renderer_wx.py | MODIFY | garantire un percorso di emissione del benvenuto con `interrupt=True` |
| tests/ui/test_finestra_gioco.py | MODIFY | aggiornare i test sull'ordine eventi: focus prima, annuncio dopo delay |

---

## Criteri di accettazione

- NVDA legge il messaggio di benvenuto in modo completo all'avvio di FinestraGioco
- Il focus sulla griglia e gia stabilizzato prima dell'annuncio differito
- Nessun gainFocus immediatamente successivo tronca il benvenuto
- Il delay di 350 ms non rompe tab order e binding tastiera iniziali
- La validazione manuale con NVDA conferma il flusso: focus stabile, poi benvenuto
