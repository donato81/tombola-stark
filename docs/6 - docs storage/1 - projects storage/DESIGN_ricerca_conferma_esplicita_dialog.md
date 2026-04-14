---
type: design
feature: ricerca_conferma_esplicita_dialog
agent: Agent-Design
status: REVIEWED
version: v1.1.1
date: 2026-04-09
report_ref: docs/4 - reports/REPORT_ANALISI_ricerca_nvda_lettura_interrotta_2026-04-09.md
---

# DESIGN — Conferma esplicita dialog ricerca numero (Ctrl+F) v1.1.1

## 1. Idea in 3 righe

Il dialog di ricerca non deve più chiudersi automaticamente dopo un esito positivo.
Dopo la vocalizzazione del risultato, il dialog resta aperto e passa in uno stato di conferma esplicita.
L'utente preme Invio per navigare al primo risultato trovato oppure Escape per uscire senza navigazione.

---

## 2. Obiettivo misurabile

Al termine dell'implementazione:

- Dopo una ricerca con esito `trovato`, NVDA può leggere integralmente il testo del risultato senza che la chiusura del dialog interrompa la speech.
- L'utente può premere `Invio` una seconda volta per chiudere il dialog con `wx.ID_OK` e spostare il focus sul primo risultato trovato.
- L'utente può premere `Escape` in qualsiasi momento per chiudere il dialog con `wx.ID_CANCEL` senza navigazione automatica.
- Dopo una ricerca con esito `non_trovato`, il focus resta sull'input per consentire una nuova ricerca immediata.
- Non deve esistere alcun timer `wx.CallLater` nel flusso di conferma del risultato trovato.

---

## 3. Attori e Concetti

- `DialogoRicercaNumero`
  - Responsabile del flusso modale di ricerca.
  - Introduce uno stato interno di conferma dopo un risultato trovato.
- `FinestraGioco`
  - Continua ad aprire il dialog e a leggere il codice di ritorno di `ShowModal()`.
  - Se il dialog termina con `wx.ID_OK`, naviga al primo risultato salvato nel dialog.
- `EventoRicercaNumeroInCartelle`
  - Resta la fonte dati per distinguere `trovato` e `non_trovato`.
- `RisultatoRicercaNumeroInCartella`
  - Resta il payload per cartella, riga e colonna del primo risultato.
- `WxRenderer`
  - Continua a costruire e vocalizzare il messaggio di ricerca; non richiede modifiche strutturali.
- Utente NVDA
  - Deve avere il controllo esplicito del momento in cui il dialog termina.

---

## 4. Flussi Concettuali

### 4.1 Flusso trovato

1. L'utente apre il dialog con `Ctrl+F`.
2. Inserisce il numero e preme `Invio`.
3. `_on_cerca()` invoca `cerca_numero()` e `render_esito(esito)`.
4. Il renderer vocalizza il testo completo del risultato.
5. Il dialog salva il primo risultato in `_primo_risultato`.
6. Il dialog entra in stato `risultato_confermabile`.
7. Il focus si sposta su un'azione esplicita di conferma, riattivabile con `Invio`.
8. Solo quando l'utente conferma, il dialog chiude con `wx.ID_OK`.
9. `FinestraGioco` naviga a cartella, riga e colonna del primo risultato.

### 4.2 Flusso non trovato

1. L'utente apre il dialog e cerca un numero.
2. Il renderer vocalizza il messaggio di mancato ritrovamento.
3. Il dialog non cambia stato e non prepara alcuna navigazione.
4. Il focus torna all'input per una nuova ricerca.
5. Il dialog resta aperto finché l'utente non riprova o preme `Escape`.

### 4.3 Flusso cancel

1. L'utente apre il dialog.
2. Può premere `Escape` prima o dopo una ricerca.
3. Il dialog chiude con `wx.ID_CANCEL`.
4. `FinestraGioco` ripristina il focus sulla griglia senza navigazione automatica.

---

## 5. Decisioni Architetturali

### Decisione 1 — Rimuovere il timer dal percorso trovato

Si elimina la chiusura automatica basata su `wx.CallLater`.
Motivazione: il timer non è correlato al tempo reale di lettura NVDA e genera interruzioni del parlato al cambio focus.

### Decisione 2 — Introdurre uno stato interno di conferma nel dialog

Il dialog mantiene due stati logici:

- stato `ricerca`: input attivo, ricerca eseguibile
- stato `conferma`: esito trovato già annunciato, azione successiva esplicita dell'utente

Motivazione: separare la fase di ascolto della risposta dalla fase di navigazione.

### Decisione 3 — Usare `wx.ID_OK` solo per conferma intenzionale dell'utente

Il dialog non deve più chiamare `EndModal(wx.ID_OK)` in autonomia.
`wx.ID_OK` viene emesso soltanto dopo conferma esplicita.
Motivazione: il codice di ritorno del dialog resta semanticamente affidabile.

### Decisione 4 — Conservare la responsabilità di navigazione in `FinestraGioco`

La navigazione al risultato resta fuori dal dialog.
Motivazione: il dialog produce un'intenzione e un payload; il frame applica il focus di gioco.

### Decisione 5 — Minima superficie di modifica

La soluzione tocca solo presentation layer e test UI:

- `bingo_game/ui/dialogo_ricerca.py`
- `bingo_game/ui/finestra_gioco.py`
- `tests/unit/test_dialogo_ricerca_persistente.py`

Motivazione: nessun cambiamento a domain, application event model o vocalizzatore.

---

## 6. Soluzione UI proposta

La soluzione preferita è aggiungere un controllo esplicito per la conferma del risultato trovato.
Le due varianti accettabili sono:

- Variante A: riuso del pulsante `Cerca`, che dopo un esito trovato cambia etichetta in `Vai al risultato`
- Variante B: aggiunta di un nuovo pulsante `Vai al risultato`, inizialmente disabilitato

Per minimizzare il rischio implementativo si preferisce la Variante B:

- `Cerca` mantiene un solo significato operativo
- `Vai al risultato` rappresenta chiaramente l'azione successiva
- il focus può essere spostato sul nuovo pulsante dopo la vocalizzazione del risultato trovato
- `Escape` mantiene sempre il significato di annullamento

Il dialog dovrà quindi gestire almeno i seguenti attributi:

- `_primo_risultato: Optional[Any]`
- `_risultato_pronto_per_conferma: bool`
- `_btn_vai_risultato` oppure equivalente controllo esplicito

---

## 7. Rischi e Vincoli

### Vincoli accessibilità NVDA

- Nessun cambio di focus automatico deve avvenire immediatamente dopo la vocalizzazione del risultato trovato.
- Il controllo che riceve focus dopo un esito trovato deve avere un nome chiaro e stabile, ad esempio `Vai al risultato`.
- `Invio` deve essere coerente con il controllo focalizzato; evitare doppi significati opachi nello stesso istante.
- `Escape` deve restare disponibile come uscita rapida e prevedibile.

### Rischi tecnici

- Se il dialog riusa `Invio` senza uno stato esplicito, si rischia una seconda ricerca invece della conferma.
- Se il nuovo pulsante non viene abilitato/disabilitato correttamente, l'utente potrebbe confermare senza un risultato valido.
- Se `_primo_risultato` non viene resettato dopo un nuovo tentativo fallito, si rischia una navigazione stantia.

### Mitigazioni

- Stato booleano esplicito per distinguere ricerca e conferma.
- Reset di `_primo_risultato` e dello stato di conferma a ogni nuova ricerca.
- Test dedicati per i percorsi `trovato`, `non_trovato`, conferma con `Invio`, annullamento con `Escape`.

---

## 8. Componenti coinvolti

- MODIFY `bingo_game/ui/dialogo_ricerca.py`
- MODIFY `bingo_game/ui/finestra_gioco.py`
- MODIFY `tests/unit/test_dialogo_ricerca_persistente.py`
- READ ONLY `docs/4 - reports/REPORT_ANALISI_ricerca_nvda_lettura_interrotta_2026-04-09.md`

---

## 9. Dipendenze

- Dipendenza dal comportamento attuale di `FinestraGioco._apri_ricerca_numero()` che gia' distingue `wx.ID_OK` e `wx.ID_CANCEL`.
- Dipendenza dal contratto esistente di `EventoRicercaNumeroInCartelle` e `RisultatoRicercaNumeroInCartella`.
- Nessuna dipendenza da hook NVDA o callback di fine lettura del sintetizzatore.
