---
type: design
feature: finestra_guida_regole
agent: Agent-Design
status: REVIEWED
version: v0.14.0
date: 2026-04-13
report_ref: docs/4 - reports/REPORT_ANALISI_finestra_guida_regole_2026-04-13.md
---

# DESIGN — Finestra guida regole del gioco

## Metadati

tipo: design
titolo: Finestra guida regole del gioco navigabile a pagine
data_creazione: 2026-04-13
agente: Agent-Design
stato: REVIEWED
versione_target: v0.14.0
report_riferimento: docs/4 - reports/REPORT_ANALISI_finestra_guida_regole_2026-04-13.md

---

## 1. Idea in 3 righe

Introdurre una finestra di guida alle regole del gioco, navigabile a
pagine come un libro, apribile con Ctrl+Shift+H da FinestraGioco e con
Ctrl+G dal menu principale. Il testo dei capitoli risiede in un file
separato it_guida.py seguendo le stesse convenzioni di it.py. La finestra
usa wx.Dialog modale con annuncio NVDA automatico del titolo capitolo a
ogni cambio di pagina tramite spostamento del focus.

---

## 2. Attori e Concetti

- FinestraGioco: intercetta Ctrl+Shift+H in _on_char_hook e apre il dialog.
- FinestraPrincipale: handler _on_guida() attualmente placeholder; va aggiornato
  per aprire il dialog con wx.GetTopLevelParent o self come parent.
- FinestraGuidaRegole: nuovo componente wx.Dialog modale del layer di
  presentazione. Gestisce la navigazione a pagine e l'annuncio NVDA.
- it_guida.py: nuovo file in bingo_game/ui/locales/ con i dizionari
  GUIDA_CAPITOLI e GUIDA_UI. Estensibile aggiungendo voci a GUIDA_CAPITOLI
  senza toccare il codice della finestra.
- GUIDA_CAPITOLI: sequenza ordinata di tuple (titolo, testo_righe). L'ordine
  nella sequenza determina l'ordine delle pagine.
- GUIDA_UI: dizionario con etichette dell'interfaccia (pulsanti, annunci NVDA).
- wx.StaticText titolo: controllo che mostra il titolo del capitolo corrente.
  Riceve il focus al cambio pagina per triggerare l'annuncio NVDA.
- wx.TextCtrl testo: area di lettura del contenuto del capitolo. Multilinea
  read-only. Unico controllo che riceve il focus all'apertura iniziale del dialog.
- PannelloGriglia: destinazione del focus alla chiusura del dialog da FinestraGioco.

---

## 3. Flussi Concettuali

### 3.1 Apertura del dialog da FinestraGioco

```text
Utente preme Ctrl+Shift+H
  -> FinestraGioco._on_char_hook intercetta la combinazione
  -> FinestraGioco crea FinestraGuidaRegole(parent=self)
  -> FinestraGioco invoca ShowModal()
  -> wxWidgets sposta il focus nel dialog
  -> wx.TextCtrl del primo capitolo riceve il focus iniziale
  -> NVDA annuncia il titolo del dialog ("Guida alle regole del gioco")
  -> NVDA legge il TextCtrl in focus (testo del capitolo 1)
```

### 3.2 Apertura del dialog da FinestraPrincipale

```text
Utente attiva pulsante "Guida (Ctrl+G)" oppure preme Ctrl+G
  -> FinestraPrincipale._on_guida() crea FinestraGuidaRegole(parent=self)
  -> ShowModal() apre il dialog modale
  -> focus iniziale sul TextCtrl del capitolo 1
```

### 3.3 Navigazione tra capitoli

```text
Dialog aperto al capitolo N
  -> utente preme Tab fino al pulsante Successivo
  -> utente preme Spazio (o Invio) su Successivo
  -> _vai_pagina_successiva() incrementa _indice_corrente
  -> _aggiorna_visualizzazione() aggiorna StaticText titolo e TextCtrl testo
  -> wx.CallAfter(self._lbl_titolo.SetFocus) sposta il focus al titolo
  -> NVDA legge il titolo del nuovo capitolo (es. "La cartella")
  -> utente preme Tab per tornare al TextCtrl e legge il testo con le frecce
  -> pulsante Precedente viene abilitato; pulsante Successivo disabilitato
     se siamo all'ultima pagina
```

### 3.4 Chiusura e ripristino del focus (da FinestraGioco)

```text
Utente preme Escape oppure attiva Chiudi
  -> EndModal(wx.ID_CANCEL)
  -> FinestraGioco riprende dopo ShowModal()
  -> dlg.Destroy()
  -> FinestraGioco chiama self._pannello_griglia.SetFocus()
  -> il focus torna alla griglia di gioco
```

---

## 4. Decisioni Architetturali

### D1 — Testi in it_guida.py separato da it.py

I testi dei capitoli sono contenuto narrativo, non messaggi di sistema.
Residono in un file dedicato it_guida.py con le stesse convenzioni
del file it.py esistente (MappingProxyType, chiavi maiuscole, import da
__future__). La separazione garantisce che it.py resti coeso con i
messaggi di sistema e che it_guida.py possa crescere liberamente.

### D2 — GUIDA_CAPITOLI come sequenza di tuple (titolo, righe)

La struttura (titolo, tuple_di_righe) rende ogni capitolo atomico e
autodescrittivo. L'aggiunta di un nuovo capitolo richiede solo l'inserimento
di una nuova tupla nella sequenza, senza modificare il codice della finestra.
La finestra calcola len(GUIDA_CAPITOLI) per il totale pagine e accede
all'indice corrente direttamente.

### D3 — Annuncio NVDA al cambio pagina tramite spostamento focus

Si usa wx.CallAfter(self._lbl_titolo.SetFocus) dopo aggiornamento dei
controlli. Questo forza NVDA a leggere il nuovo titolo del capitolo senza
richiedere AccessibleDescription o hook custom. E la tecnica gia collaudata
in altri componenti del progetto ed e NVDA-safe.

### D4 — Tasto Ctrl+Shift+H in FinestraGioco, Ctrl+G in FinestraPrincipale

Ctrl+G e gia riservato dalla FinestraGioco per "stato premi sintetico".
Ctrl+Shift+H e completamente libero in tutti i contesti e mantiene Ctrl+H
dedicato alla finestra tasti rapidi. La coesistenza di due hotkey diverse
(una per contesto) riflette il fatto che i due frame sono separati e non
attivi contemporaneamente.

### D5 — Dialog modale, non frame separato

Il dialog modale sospende gli input della finestra chiamante durante la
consultazione. Questo e coerente con il pattern gia in uso per
FinestraAiutoTastiRapidi e DialogoRicercaNumero.

### D6 — Focus iniziale sul TextCtrl, non sul titolo

All'apertura il focus va sul TextCtrl del testo del capitolo perche
NVDA annuncia comunque il titolo del dialog prima di leggere il controllo
in focus. Se il focus fosse sul titolo, NVDA leggerebbe il titolo due
volte (una come titolo dialog, una come controllo in focus). Il TextCtrl
permette all'utente di iniziare subito a leggere il contenuto.

### D7 — Zero dipendenze da dominio e renderer

Il dialog e puramente informativo. Non richiede istanze di Partita,
ComandiGiocatoreUmano, WxRenderer o eventi di dominio. Dipende solo
da wx e da it_guida.py.

---

## 5. Contratto della classe FinestraGuidaRegole

### 5.1 Costruttore

```
FinestraGuidaRegole(parent: wx.Window) -> None
```

- parent: il frame chiamante (FinestraGioco o FinestraPrincipale).
  Usato da wxWidgets per la gerarchia modale e il posizionamento.
- Chiama super().__init__ con title=GUIDA_UI["TITOLO_FINESTRA"]
  e style=wx.DEFAULT_DIALOG_STYLE.
- Imposta self._indice_corrente = 0.
- Chiama _build_ui() poi _aggiorna_visualizzazione().
- Centra il dialog con self.Centre().

### 5.2 Attributi privati

- _indice_corrente: int — indice 0-based del capitolo visibile.
- _lbl_titolo: wx.StaticText — titolo del capitolo corrente.
- _testo: wx.TextCtrl — contenuto del capitolo corrente.
- _btn_precedente: wx.Button — disabilitato sulla prima pagina.
- _btn_successivo: wx.Button — disabilitato sull'ultima pagina.
- _btn_chiudi: wx.Button — sempre abilitato.
- _lbl_pagina: wx.StaticText — indicatore "Pagina N di M".

### 5.3 Metodi privati principali

```
_build_ui() -> None
```
Costruisce tutti i controlli wx, assembla il layout con BoxSizer,
chiama SetSizerAndFit. Bind EVT_BUTTON per i tre pulsanti. Bind EVT_SHOW.

```
_aggiorna_visualizzazione() -> None
```
Legge GUIDA_CAPITOLI[_indice_corrente]. Aggiorna _lbl_titolo, _testo,
_lbl_pagina. Abilita/disabilita _btn_precedente e _btn_successivo secondo
i limiti. Non sposta il focus (questo e responsabilita del chiamante tramite
wx.CallAfter).

```
_vai_pagina_precedente(event: wx.CommandEvent) -> None
```
Se _indice_corrente > 0: decrementa, chiama _aggiorna_visualizzazione(),
poi wx.CallAfter(self._lbl_titolo.SetFocus).

```
_vai_pagina_successiva(event: wx.CommandEvent) -> None
```
Se _indice_corrente < len(GUIDA_CAPITOLI) - 1: incrementa, chiama
_aggiorna_visualizzazione(), poi wx.CallAfter(self._lbl_titolo.SetFocus).

```
_on_chiudi(event: wx.CommandEvent) -> None
```
Chiama self.EndModal(wx.ID_CANCEL).

```
_on_show(event: wx.ShowEvent) -> None
```
Se event.IsShown(): self._testo.SetFocus(). Chiama event.Skip().

---

## 6. Layout dei controlli wx

### 6.1 Struttura visiva (dall'alto al basso)

```
+--------------------------------------------------+
|  Guida alle regole del gioco              [X]   |  <- titolo finestra wx
+--------------------------------------------------+
|  [wxStaticText: titolo capitolo corrente]        |  <- _lbl_titolo
|                                                  |
|  [wxTextCtrl read-only: testo capitolo]          |  <- _testo
|  (altezza fissa 300px, larghezza 520px)          |
|                                                  |
+--------------------------------------------------+
|  [Precedente]  Pagina 1 di 5  [Successivo]      |  <- riga navigazione
|               [Chiudi]                           |  <- riga chiusura
+--------------------------------------------------+
```

### 6.2 Sizer annidati

```
BoxSizer(VERTICAL) (sizer principale)
  +-- _lbl_titolo         flag: ALL | EXPAND  border: 10
  +-- _testo              flag: ALL | EXPAND  proporzione: 1
  +-- BoxSizer(HORIZONTAL) (sizer navigazione)
  |     +-- _btn_precedente   flag: ALL  border: 5
  |     +-- _lbl_pagina       flag: ALL | ALIGN_CENTER_VERTICAL  border: 5
  |     +-- _btn_successivo   flag: ALL  border: 5
  +-- StdDialogButtonSizer
        +-- _btn_chiudi        AddButton + Realize
```

### 6.3 Ordine di navigazione con Tab (ciclo completo)

1. _testo (wx.TextCtrl) — focus iniziale all'apertura
2. _btn_precedente (disabled su pagina 1, saltato da Tab se disabilitato)
3. _btn_successivo (disabled sull'ultima pagina)
4. _btn_chiudi
5. torna a _testo

Nota: wx.TAB_TRAVERSAL e il comportamento predefinito nei Dialog.
I pulsanti disabilitati vengono saltati automaticamente da Tab.

### 6.4 Controllo che riceve il focus all'apertura

_testo (wx.TextCtrl) — impostato in _on_show tramite self._testo.SetFocus().
Questo permette a NVDA di iniziare subito la lettura del testo del capitolo
dopo l'annuncio del titolo del dialog.

---

## 7. Struttura di it_guida.py

### 7.1 GUIDA_CAPITOLI

Tipo: Sequence[tuple[str, tuple[str, ...]]]
Immutabile: tupla di tuple (non wrappata in MappingProxyType, gia immutabile).
Ogni elemento: (titolo_capitolo: str, righe_testo: tuple[str, ...])

Il renderer unisce le righe con "\n".join(righe) per popolare il TextCtrl.

### 7.2 GUIDA_UI

Tipo: MappingProxyType[str, str]
Chiavi:
- "TITOLO_FINESTRA" — titolo del wx.Dialog
- "BTN_PRECEDENTE" — label del pulsante Precedente
- "BTN_SUCCESSIVO" — label del pulsante Successivo
- "BTN_CHIUDI" — label del pulsante Chiudi
- "ANNUNCIO_PAGINA" — template per _lbl_pagina con placeholder {corrente} e {totale}

### 7.3 Contenuto completo dei cinque capitoli

I testi seguenti sono definitivi e devono essere usati esattamente come
indicato nella sezione "Testi dei capitoli" della richiesta.

**Capitolo 1 — Introduzione alla Tombola**

Titolo: "Introduzione alla Tombola"

Testo (righe):
- "La Tombola è un classico gioco di società italiano. L'obiettivo è"
- "segnare i numeri estratti sulla propria cartella e dichiarare i premi"
- "nel giusto ordine, prima degli avversari."
- ""
- "In Tombola Stark giochi contro uno o più bot controllati dal computer."
- "Il gioco estrae un numero alla volta dal tabellone, che contiene tutti"
- "i numeri da 1 a 90. Ogni numero può essere estratto una sola volta"
- "per partita."
- ""
- "Vince chi dichiara la Tombola per primo, cioè chi completa tutte e"
- "tre le righe della propria cartella."

**Capitolo 2 — La cartella**

Titolo: "La cartella"

Testo (righe):
- "La cartella è la tua scheda di gioco. È composta da tre righe e nove"
- "colonne, per un totale di ventisette caselle. Di queste, solo quindici"
- "contengono numeri: le altre dodici sono vuote."
- ""
- "I numeri sono distribuiti per decine: la prima colonna contiene numeri"
- "tra 1 e 9, la seconda tra 10 e 19, e così via fino alla nona colonna"
- "che contiene numeri tra 80 e 90."
- ""
- "Puoi giocare con una sola cartella o con più cartelle, fino a un"
- "massimo di sei. Puoi scegliere il numero di cartelle nella schermata"
- "di configurazione prima di iniziare la partita. Il gioco ti mostra"
- "una cartella alla volta: puoi passare da una all'altra con i tasti"
- "Ctrl+1, Ctrl+2 fino a Ctrl+6."

**Capitolo 3 — I premi in ordine**

Titolo: "I premi in ordine"

Testo (righe):
- "I premi della Tombola si dichiarano in ordine crescente. Non puoi"
- "saltare un premio: devi vincere l'ambo prima di poter dichiarare"
- "il terno, e così via."
- ""
- "L'ordine dei premi è il seguente:"
- ""
- "Ambo: due numeri segnati sulla stessa riga."
- "Terno: tre numeri segnati sulla stessa riga."
- "Quaterna: quattro numeri segnati sulla stessa riga."
- "Cinquina: cinque numeri segnati sulla stessa riga, cioè una riga completa."
- "Tombola: tutti e quindici i numeri segnati, cioè tutte e tre le righe complete."
- ""
- "Ogni premio può essere vinto una sola volta per partita. Se un bot"
- "dichiara un premio prima di te, quel premio è perso: non puoi più"
- "dichiararlo. La partita termina quando qualcuno dichiara la Tombola."

**Capitolo 4 — Come si svolge un turno**

Titolo: "Come si svolge un turno"

Testo (righe):
- "All'inizio di ogni turno, il gioco estrae automaticamente un numero"
- "dal tabellone e lo annuncia ad alta voce. Se quel numero è presente"
- "su una delle tue cartelle, puoi segnarlo."
- ""
- "Hai 60 secondi per trovare il numero sulla tua cartella e segnarlo"
- "con il tasto Spazio. Se non fai nulla entro i 60 secondi, il turno"
- "passa automaticamente al successivo. Puoi anche decidere di passare"
- "subito il turno con Ctrl+Invio, senza aspettare."
- ""
- "Se dopo aver segnato un numero hai raggiunto una combinazione"
- "vincente, puoi dichiarare il premio con i tasti F1 (ambo), F2"
- "(terno), F3 (quaterna), F4 (cinquina) o F5 (tombola). Ricorda:"
- "i premi vanno dichiarati in ordine. Il gioco segnala automaticamente"
- "se la dichiarazione non è corretta."

**Capitolo 5 — I bot avversari**

Titolo: "I bot avversari"

Testo (righe):
- "I bot sono giocatori automatici controllati dal computer. Per"
- "impostazione predefinita c'è un solo bot, chiamato Bot 1. Puoi"
- "scegliere di aggiungerne altri nella schermata di configurazione"
- "prima di iniziare."
- ""
- "I bot giocano in modo autonomo: segnano i numeri estratti sulle"
- "loro cartelle e dichiarano i premi quando ne hanno diritto. Non"
- "devi fare nulla per farli giocare."
- ""
- "I bot possono vincere i premi prima di te. Se Bot 1 dichiara"
- "l'ambo prima che tu lo faccia, l'ambo è assegnato a lui e tu non"
- "puoi più dichiararlo. Tieni d'occhio i messaggi vocali: il gioco"
- "annuncia ogni vittoria dei bot non appena avviene."

### 7.4 Come aggiungere un capitolo in futuro

Per aggiungere un capitolo: aggiungere una nuova tupla (titolo, righe)
in GUIDA_CAPITOLI nella posizione desiderata. Il codice della finestra
legge len(GUIDA_CAPITOLI) e itera sull'indice. Nessuna modifica al codice
UI e necessaria.

---

## 8. Specifiche accessibilita NVDA

### 8.1 Sequenza annunci all'apertura

1. NVDA annuncia il titolo del dialog: "Guida alle regole del gioco, dialogo"
2. NVDA legge il controllo in focus: il TextCtrl del capitolo 1
3. NVDA legge da dove si trova il cursore (inizio del testo, prima riga)
4. L'utente usa frecce su/giu per leggere riga per riga il testo

### 8.2 Comportamento al cambio pagina

Quando il pulsante Successivo (o Precedente) viene attivato:
1. _aggiorna_visualizzazione() aggiorna _lbl_titolo, _testo, _lbl_pagina
2. wx.CallAfter(self._lbl_titolo.SetFocus) viene chiamato
3. Al prossimo ciclo eventi, _lbl_titolo riceve il focus
4. NVDA legge il nuovo titolo del capitolo (es. "La cartella")
5. L'utente preme Tab per spostarsi al TextCtrl e leggere il testo

Nota: wx.StaticText e focalizzabile via SetFocus() anche se normalmente
non e in ordine Tab. Questo e il meccanismo di annuncio NVDA piu affidabile
senza ricorrere a AccessibleDescription o ARIA equivalenti wxPython.

### 8.3 Comportamento alla chiusura

- Escape o pulsante Chiudi: EndModal(wx.ID_CANCEL)
- FinestraGioco: dlg.Destroy() poi self._pannello_griglia.SetFocus()
- NVDA annuncia il ritorno al contesto di gioco ("Griglia cartella")
- FinestraPrincipale: alla chiusura del dialog il focus torna al
  pulsante Guida del menu principale (comportamento nativo wx.Dialog)

---

## 9. Punti di integrazione

### 9.1 Modifica a _on_char_hook in finestra_gioco.py

Punto di inserimento: nel blocco EVT_CHAR_HOOK di FinestraGioco, dopo
il ramo Ctrl+I e prima di event.Skip(), aggiungere:

```
se ctrl e shift e key == ord("H"):
    dlg = FinestraGuidaRegole(self)
    dlg.ShowModal()
    dlg.Destroy()
    self._pannello_griglia.SetFocus()
    return
```

Import da aggiungere in testa al file:

```
from bingo_game.ui.finestra_guida_regole import FinestraGuidaRegole
```

### 9.2 Modifica a _on_guida() in finestra_principale.py

Sostituire il corpo corrente:

```
# PRIMA (placeholder):
self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")

# DOPO:
dlg = FinestraGuidaRegole(self)
dlg.ShowModal()
dlg.Destroy()
```

Import da aggiungere in testa al file (o nel corpo del metodo per lazy import):

```
from bingo_game.ui.finestra_guida_regole import FinestraGuidaRegole
```

---

## 10. Criteri di accettazione

I seguenti criteri devono essere verificati prima di considerare
l'implementazione completata:

CA1: Il dialog si apre con Ctrl+Shift+H durante una partita in corso
     senza eccezioni e senza interrompere il timer di gioco.

CA2: Il dialog si apre con Ctrl+G dal menu principale.

CA3: All'apertura NVDA annuncia il titolo del dialog e poi il testo
     del primo capitolo.

CA4: Il titolo del capitolo corrente e visibile come StaticText
     nella parte superiore del dialog.

CA5: Il TextCtrl mostra il testo del capitolo 1 all'apertura.

CA6: Il pulsante Precedente e disabilitato sulla prima pagina;
     il pulsante Successivo e disabilitato sull'ultima pagina.

CA7: Al cambio di pagina NVDA legge il titolo del nuovo capitolo
     (annuncio tramite spostamento focus su _lbl_titolo).

CA8: L'indicatore "Pagina N di M" si aggiorna correttamente
     a ogni cambio di pagina.

CA9: Escape chiude il dialog in qualsiasi stato (qualsiasi pagina,
     qualsiasi controllo in focus).

CA10: Alla chiusura da FinestraGioco il focus torna deterministicamente
      su PannelloGriglia.

CA11: Il file it_guida.py contiene esattamente 5 capitoli con i testi
      definitivi validator dal developer.

CA12: Aggiungere un sesto capitolo in it_guida.py (solo dizionario)
      fa apparire automaticamente la nuova pagina nel dialog senza
      modificare il codice di FinestraGuidaRegole.

CA13: La suite test UI per FinestraGuidaRegole e verde in CI
      (wx.App(False), no display reale).

---

## Stato Avanzamento

- [x] Bozza completata
- [x] Revisionato
- [ ] Approvato
- [ ] Archiviato
