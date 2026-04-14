---
feature: fix_tab_navigation_finestra_gioco
agent: Agent-Design
status: REVIEWED
version: v0.12.1
date: 2026-04-12
---

## Metadati

tipo: design
titolo: Fix navigazione Tab nella finestra di gioco
data_creazione: 2026-04-12
agente: Agent-Design
stato: REVIEWED

---

## 1. Idea in 3 righe

Il tasto Tab non raggiungo i pulsanti Cartella precedente, Cartella successiva,
selezione diretta e dichiarazione vittorie nella finestra di gioco.
La causa e il flag wx.WANTS_CHARS su PannelloGriglia che intercetta Tab
senza delegare la navigazione al ciclo focus di wxWidgets.

---

## 2. Attori e Concetti

- PannelloGriglia: pannello con wx.WANTS_CHARS + wx.TAB_TRAVERSAL. Intercetta
  tutti i tasti incluso Tab; deve chiamare Navigate() per cedere il focus.
- FinestraGioco._build_ui: crea i widget nell'ordine btn_principale, btn_pausa,
  pannello_griglia, frecce, pannello_cartella, pulsanti_selezione, btn_premi, log_ctrl.
- _crea_pulsanti_selezione_cartella: crea dinamicamente i pulsanti 1..N solo
  al primo turno; la creazione tardiva li posiziona in fondo al ciclo Tab.
- MoveAfterInTabOrder: metodo wxWidget per correggere l'ordine Tab senza
  dipendere dall'ordine di creazione dei widget.
- Navigate(flags): metodo wxWidget per delegare esplicitamente la navigazione
  Tab a partire da un widget con WANTS_CHARS.

---

## 3. Flussi Concettuali

### Flusso attuale (rotto)

1. Utente preme Tab all'interno di PannelloGriglia
2. EVT_KEY_DOWN in PannelloGriglia._on_key_down riceve il tasto
3. Nessun handler per WXK_TAB; si arriva al ramo finale event.Skip()
4. wx.WANTS_CHARS impedisce al framework di attivare TAB_TRAVERSAL
5. Il focus non si sposta — rimane bloccato sul pannello

### Flusso atteso dopo la fix

1. Utente preme Tab all'interno di PannelloGriglia
2. EVT_KEY_DOWN in PannelloGriglia._on_key_down riceve il tasto
3. Handler WXK_TAB chiama self.Navigate(wx.NavigationKeyEvent.IsForward)
   oppure IsBackward per Shift+Tab
4. wxWidgets sposta il focus sul prossimo controllo abilitato nel ciclo Tab
5. I pulsanti freccia, selezione e premi ricevono il focus quando abilitati

### Ordine Tab atteso (dopo fix)

1. _btn_principale
2. _btn_pausa
3. PannelloGriglia
4. _btn_freccia_sx
5. _btn_freccia_dx
6. _pulsanti_selezione[0..N] (ordine corretto via MoveAfterInTabOrder)
7. _btn_premi[ambo..tombola]
8. _log_ctrl

I widget disabilitati vengono automaticamente saltati da wxWidgets.

---

## 4. Decisioni Architetturali

### D1 — Navigate() invece di wx.PostEvent

Navigate() e l'API ufficiale wxWidgets per cedere il focus da un pannello
con WANTS_CHARS. E piu robusta di PostEvent con NavigationKeyEvent perche
usa il meccanismo interno del framework, funziona con NVDA, ed e la soluzione
documentata nella wxWidgets FAQ.

### D2 — MoveAfterInTabOrder per pulsanti dinamici

I pulsanti selezione cartella vengono creati dopo tutti gli altri widget, quindi
wxWidgets li inserisce alla fine del ciclo Tab (dopo log_ctrl).
MoveAfterInTabOrder permette di inserirli nella posizione logica corretta
(dopo _btn_freccia_dx) senza dover ricreare o riordinare i widget.
E la tecnica raccomandata da ui.instructions.md.

### D3 — Nessun feedback vocale aggiuntivo (Fix 3 scartato)

Il focus su wx.Button in wxPython + NVDA viene gia annunciato automaticamente
dal name del widget (SetName). Aggiungere annunci vocali espliciti duplicherebbe
la lettura. Il Fix 3 opzionale e scartato.

---

## 5. Rischi e Vincoli

- Navigate() con WANTS_CHARS: testato su wxPython Phoenix su Windows 11.
  Su piattaforme non-Windows il comportamento potrebbe differire, ma il
  progetto e Windows-only per vincolo di accessibilita NVDA.
- Pulsanti disabilitati: il Tab li salta automaticamente. L'utente deve
  essere a conoscenza che i pulsanti sono raggiungibili solo durante
  la partita attiva e in fase attesa_reclami.
- Ordine Tab dei pulsanti premi: sono creati in _build_ui con ordine fisso
  ambo..tombola; nessuna correzione MoveAfterInTabOrder necessaria per loro.

---

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [ ] Approvato
- [ ] Archiviato
