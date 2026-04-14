---
type: design
feature: finestra_aiuto_tasti_rapidi
agent: Agent-Design
status: REVIEWED
version: v0.13.0
date: 2026-04-13
report_ref: docs/4 - reports/REPORT_ANALISI_finestra_aiuto_tasti_rapidi_2026-04-12.md
---

# DESIGN — Finestra aiuto tasti rapidi

## Metadati

tipo: design
titolo: Finestra aiuto tasti rapidi della FinestraGioco
data_creazione: 2026-04-13
agente: Agent-Design
stato: REVIEWED
versione_target: v0.13.0
report_riferimento: docs/4 - reports/REPORT_ANALISI_finestra_aiuto_tasti_rapidi_2026-04-12.md

---

## 1. Idea in 3 righe

Introdurre una finestra di aiuto dedicata ai tasti rapidi della partita,
apribile con Ctrl+H da FinestraGioco come wx.Dialog modale e con contenuto
statico in sola lettura. Il focus iniziale deve cadere sul contenuto del dialog,
Escape deve chiuderlo in modo prevedibile, e alla chiusura il focus deve tornare
alla griglia di gioco senza modificare dominio o renderer.

---

## 2. Attori e Concetti

- FinestraGioco: frame chiamante che intercetta Ctrl+H a livello finestra e
  apre il dialog senza alterare il flusso della partita.
- FinestraAiutoTastiRapidi: nuovo componente wx.Dialog modale del layer di
  presentazione, isolato e con responsabilita esclusiva di esporre l'elenco
  delle scorciatoie.
- Contenuto statico read-only: testo multi-sezione gia derivabile dal report
  di analisi del 2026-04-12; non dipende dallo stato corrente della partita.
- wx.TextCtrl multilinea read-only: controllo principale del dialog, scelto
  come area di lettura iniziale per NVDA e per una navigazione lineare con le
  frecce.
- Pulsante Chiudi: controllo secondario del dialog, utile per il ciclo Tab e
  come affordance esplicita, ma non indispensabile per la chiusura grazie a
  Escape.
- PannelloGriglia: destinazione del focus al termine del dialog; mantiene il
  proprio ruolo di punto di rientro nel gameplay e nelle hotkey di Categoria A.

---

## 3. Flussi Concettuali

### 3.1 Apertura del dialog da FinestraGioco

```text
Utente preme Ctrl+H
  -> FinestraGioco._on_char_hook intercetta la combinazione
  -> FinestraGioco crea FinestraAiutoTastiRapidi(parent=self)
  -> FinestraGioco invoca ShowModal()
  -> wxWidgets sposta il focus nel dialog
  -> il controllo contenuto read-only riceve il focus iniziale
```

### 3.2 Consultazione del contenuto

```text
Dialog aperto
  -> NVDA annuncia il titolo del dialog
  -> NVDA legge il controllo contenuto in focus
  -> l'utente usa frecce su/giu, PagSu/PagGiu o Tab
  -> il dialog cattura gli input e il frame sottostante resta inattivo
  -> nessun tasto di gioco viene elaborato mentre il dialog e modale
```

### 3.3 Chiusura e ripristino del focus

```text
Utente preme Escape oppure attiva Chiudi
  -> il dialog termina con EndModal(wx.ID_CANCEL o wx.ID_OK)
  -> FinestraGioco riprende dopo ShowModal()
  -> il dialog viene distrutto
  -> FinestraGioco richiama _pannello_griglia.SetFocus()
  -> il focus torna alla griglia, pronta per la normale navigazione tastiera
```

---

## 4. Decisioni Architetturali

### D1 — wx.Dialog modale invece di frame o pannello integrato

La guida viene progettata come wx.Dialog modale per sospendere in modo netto
le interazioni con la partita mentre l'utente consulta le scorciatoie.
Questa scelta evita conflitti con i binding gia presenti in FinestraGioco,
mantiene prevedibile il comportamento di Escape e non richiede stati aggiuntivi
nel dominio o nel controller.

### D2 — Contenuto statico in wx.TextCtrl multilinea read-only

Il contenuto resta statico e read-only, senza dipendere dal numero di turno,
dalla cartella corrente o dai premi aperti. Un wx.TextCtrl multilinea in sola
lettura e la soluzione piu semplice e robusta per NVDA: supporta lettura riga
per riga, selezione opzionale e focus iniziale immediato sul testo.

### D3 — Apertura da Ctrl+H in FinestraGioco, non nella griglia

La scorciatoia va intercettata in FinestraGioco a livello frame tramite il
percorso gia usato per le altre hotkey globali, cosi resta disponibile anche
quando il focus non e sul PannelloGriglia. Questo evita di introdurre logica
duplicata nel renderer, nella griglia o in altri componenti di presentazione.

### D4 — Chiusura con Escape e pulsante Chiudi esplicito

Escape resta il percorso di uscita rapido e coerente con gli altri dialog del
progetto. Un pulsante Chiudi rimane comunque utile per il ciclo Tab e per gli
utenti che preferiscono una affordance esplicita. I due percorsi devono avere
lo stesso esito: chiusura del dialog e ritorno del focus alla griglia.

### D5 — Ripristino focus sempre su PannelloGriglia

Alla chiusura il focus non torna genericamente alla finestra, ma in modo
deterministico alla griglia. Questo conserva continuita cognitiva: l'utente
consulta l'aiuto e riprende esattamente dal contesto di gioco principale,
senza dover ritrovare manualmente il punto di rientro tramite Tab.

### D6 — Zero modifiche a dominio e renderer

La feature e puramente di presentazione. Nessun nuovo evento di dominio,
nessun cambiamento alle entity o ai servizi applicativi, nessun adattamento
al renderer esistente. Il renderer non viene toccato perche il dialog puo
essere costruito e gestito direttamente da wxPython senza nuovi contratti.

---

## 5. Rischi e Vincoli

- Vincolo di layer: la soluzione deve rimanere confinata al layer UI.
  Le modifiche previste sono un nuovo dialog wx e un piccolo hook in
  FinestraGioco; dominio e renderer restano invariati.
- Vincolo di accessibilita: il contenuto deve essere lineare, con sezioni
  testuali stabili e leggibili da NVDA senza markup complesso, tabelle o
  widget custom.
- Vincolo di focus: il controllo contenuto deve ricevere il focus iniziale e
  la chiusura deve sempre ripristinare il focus su PannelloGriglia, anche se
  il dialog viene chiuso con Escape.
- Rischio di drift documentale: l'elenco dei tasti rapidi e statico; se in
  futuro cambiano i binding in FinestraGioco, il testo del dialog puo andare
  fuori sincrono. La mitigazione e trattare il contenuto come snapshot esplicito
  del censimento gia approvato nel report di analisi.
- Rischio di conflitto shortcut: Ctrl+H risulta libero nel report corrente,
  ma ogni nuova hotkey globale dovra continuare a verificarne la disponibilita
  per evitare regressioni future.
- Vincolo piattaforma: il comportamento e progettato per wxPython su Windows
  con NVDA; non si fanno assunzioni di parita perfetta su altre piattaforme.

---

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [ ] Approvato
- [ ] Archiviato