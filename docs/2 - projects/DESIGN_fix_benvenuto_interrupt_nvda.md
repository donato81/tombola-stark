---
type: design
titolo: Fix lettura benvenuto NVDA via interrupt — secondo tentativo
feature: fix_benvenuto_interrupt_nvda
versione: 0.12.3
data_creazione: 2026-04-14
agent: Agent-Design
status: DRAFT
---

# DESIGN — Fix lettura benvenuto NVDA via interrupt

## Idea in 3 righe

I fix precedenti (G2) hanno introdotto il flag `_avvio_silenzioso` e rimosso
il CallAfter annidato, ma non hanno applicato `interrompi=True` sulla
vocalizzazione del benvenuto. Il messaggio si accoda dopo gli annunci NVDA
nativi di Show/SetFocus e non viene raggiunto. Questa fix aggiunge l'interruzione
esplicita della coda e riposiziona SetFocus per ridurre il rumore pre-benvenuto.

---

## Obiettivo

Garantire che all'ingresso nella finestra di gioco NVDA legga immediatamente
e senza ostacoli il messaggio orientativo:

"Sei nella finestra di gioco. Premi Inizia partita o Ctrl+Invio per estrarre
il primo numero. Premi Ctrl+H per la guida ai tasti rapidi."

Il testo deve essere il PRIMO messaggio udibile, non l'ultimo di una coda.

---

## Attori e Concetti

| Attore / Concetto | File | Ruolo |
|---|---|---|
| FinestraGioco | bingo_game/ui/finestra_gioco.py | schedula e emette il benvenuto |
| WxRenderer | bingo_game/ui/renderers/renderer_wx.py | vocalizza tramite AO2 |
| Vocalizzatore | my_lib/vocalizzatore.py | backend TTS con parametro interrompi |
| NVDA focus events | runtime UI | generati da Show(), SetFocus(), Hide() |
| Report analisi | docs/4 - reports/REPORT_ANALISI_benvenuto_ancora_muto_2026-04-14.md | evidenza tecnica del problema residuo |

---

## Flussi Concettuali

### Flusso attuale (post-G2, ancora difettoso)

```
FinestraConfigurazione._on_conferma()
  ├─ FinestraGioco.__init__()
  │    ├─ _build_ui()
  │    ├─ _bind_finestra()
  │    ├─ renderer.aggiorna_finestra(self)
  │    ├─ _pannello_griglia.SetFocus()        ← SetFocus PRIMA di Show
  │    └─ wx.CallAfter(_imposta_focus_iniziale)
  ├─ finestra_gioco.Show()
  │    └─ NVDA: "Tombola Stark — In gioco" + "Griglia cartella"
  └─ self.Hide()

[idle loop]
  └─ _imposta_focus_iniziale()
       ├─ _avvio_silenzioso = True
       ├─ _dispatch x3  (silenziosi — ok)
       ├─ _avvio_silenzioso = False
       ├─ _aggiorna_griglie_visive()
       ├─ _aggiorna_titolo_cartella()
       └─ renderer.mostra_messaggio_sistema(benvenuto)
            └─ _ao2_vocalizza(testo)
                 └─ vocalizza_testo(testo)      ← interrupt=False → ACCODA
```

Il benvenuto arriva in coda DOPO gli annunci NVDA nativi. Se l'utente preme
un tasto o sposta il focus, la coda viene azzerata e il benvenuto non viene
mai letto.

### Flusso target

```
FinestraConfigurazione._on_conferma()
  ├─ FinestraGioco.__init__()
  │    ├─ _build_ui()
  │    ├─ _bind_finestra()
  │    ├─ renderer.aggiorna_finestra(self)
  │    └─ wx.CallAfter(_imposta_focus_iniziale)  ← NO SetFocus nel costruttore
  ├─ finestra_gioco.Show()
  │    └─ NVDA: (titolo finestra, senza focus extra)
  └─ self.Hide()

[idle loop]
  └─ _imposta_focus_iniziale()
       ├─ _avvio_silenzioso = True
       ├─ _dispatch x3  (silenziosi)
       ├─ _avvio_silenzioso = False
       ├─ _aggiorna_griglie_visive()
       ├─ _aggiorna_titolo_cartella()
       ├─ renderer.mostra_messaggio_benvenuto(benvenuto)
       │    └─ vocalizza_testo(testo, interrompi=True)  ← INTERROMPE coda
       └─ _pannello_griglia.SetFocus()               ← SetFocus DOPO il benvenuto
```

Il benvenuto viene pronunciato con interruzione esplicita prima di qualsiasi
annuncio di focus, poi SetFocus posiziona l'utente sulla griglia senza disturbare
la coda appena svuotata.

---

## Decisioni Architetturali

### D1 — Nuovo metodo renderer: mostra_messaggio_benvenuto

Introdurre in WxRenderer un metodo `mostra_messaggio_benvenuto(testo: str)`
che chiama `_vocalizzatore.vocalizza_testo(testo, interrompi=True)`.

Motivo: non modificare `mostra_messaggio_sistema` (usato in tutto il ciclo di
gioco senza interruzione), ma aggiungere un metodo specializzato solo per i
messaggi di ingresso/orientamento che richiedono priorita assoluta sulla coda.

### D2 — Spostare SetFocus alla fine di _imposta_focus_iniziale

Rimuovere `self._pannello_griglia.SetFocus()` dal costruttore di FinestraGioco
(riga 636) e inserirlo come ultima istruzione di `_imposta_focus_iniziale`,
dopo `mostra_messaggio_benvenuto`.

Motivo: SetFocus prima di Show genera eventi NVDA non necessari che saturano
la coda. Eseguito dopo il benvenuto, il focus event di NVDA arriva quando la
coda e libera e il benvenuto e stato gia pronunciato con interrupt=True.

### D3 — Nessuna modifica al Vocalizzatore

Il parametro `interrompi` e gia supportato da `Vocalizzatore.vocalizza_testo`.
Basta passarlo correttamente.

### D4 — Nessuna modifica alla logica di dominio o al costruttore di WxRenderer

La fix e confinata a FinestraGioco (costruttore e _imposta_focus_iniziale)
e a WxRenderer (nuovo metodo). Nessun file di dominio, application o infrastruttura
viene toccato.

---

## Rischi e Vincoli

### R1 — SetFocus spostato puo alterare il comportamento Tab al primo accesso

Verificare che dopo lo spostamento di SetFocus il ciclo Tab dalla griglia
ai pulsanti funzioni identicamente a prima.

### R2 — interrupt=True puo troncare annunci legittimi se usato fuori dal benvenuto

Il metodo `mostra_messaggio_benvenuto` NON deve essere usato per messaggi
normali: e dedicato esclusivamente ai messaggi di ingresso finestra.
L'agente Code deve evitare di riutilizzarlo per altri output.

### R3 — NVDA potrebbe comunque leggere il titolo finestra sopra al benvenuto

La lettura del titolo finestra da parte di NVDA avviene in risposta all'evento
WM_SETFOCUS/Show, ed e gestita da NVDA in modo autonomo, fuori dalla coda AO2.
Il benvenuto con interrupt=True svuota la coda AO2 ma non puo sopprimere annunci
NVDA indipendenti. In pratica, NVDA legge il titolo finestra brevissimamente
(una parola o meno) e poi AO2 con interrupt=True prende il controllo.
Il risultato netto e accettabile.

### R4 — Accessibilita NVDA: nessuna regressione sui binding tastiera

I binding Categoria A (frecce, spazio, R, A, V, F1-F5, F6, Escape) devono
continuare a funzionare identicamente dopo lo spostamento di SetFocus.
Il pannello griglia riceve focus nell'ultimo passo di _imposta_focus_iniziale,
come avveniva in precedenza; il cambiamento e solo la sequenza temporale.

---

## File coinvolti

| File | Operazione | Motivo |
|---|---|---|
| bingo_game/ui/finestra_gioco.py | MODIFY | rimuovi SetFocus dal costruttore; sposta SetFocus a fine _imposta_focus_iniziale; cambia chiamata a mostra_messaggio_benvenuto |
| bingo_game/ui/renderers/renderer_wx.py | MODIFY | nuovo metodo mostra_messaggio_benvenuto con interrompi=True |
| tests/ui/test_finestra_gioco.py | MODIFY | aggiorna test per nuovo ordine chiamate |

---

## Criteri di accettazione

- NVDA legge il benvenuto come primo messaggio udibile all'ingresso in FinestraGioco
- Nessun annuncio "Cartella 1 selezionata", "Riga 1" o "Colonna 1" prima del benvenuto
- Il focus sulla griglia e attivo dopo il benvenuto
- I binding tastiera Categoria A non regrediscono
- I test automatici su test_finestra_gioco.py passano
