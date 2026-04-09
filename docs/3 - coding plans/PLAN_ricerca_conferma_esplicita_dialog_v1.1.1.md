---
type: plan
feature: ricerca_conferma_esplicita_dialog
agent: Agent-Plan
status: DRAFT
version: v1.1.1
design_ref: docs/2 - projects/DESIGN_ricerca_conferma_esplicita_dialog.md
date: 2026-04-09
report_ref: docs/4 - reports/REPORT_ANALISI_ricerca_nvda_lettura_interrotta_2026-04-09.md
---

# PLAN — Conferma esplicita dialog ricerca numero (Ctrl+F) v1.1.1

## 1. Executive Summary

- Tipo: fix UX e accessibilità NVDA
- Feature: ricerca_conferma_esplicita_dialog
- Priorità: alta
- Versione target: v1.1.1
- Stato: DRAFT
- Design di riferimento: docs/2 - projects/DESIGN_ricerca_conferma_esplicita_dialog.md
- Obiettivo: separare la lettura del risultato dalla navigazione al primo match

---

## 2. Problema e Obiettivo

### Problema

L'auto-chiusura del dialog di ricerca interrompe la lettura NVDA perché la chiusura modale provoca un cambio focus e attiva subito nuove vocalizzazioni di navigazione.

### Obiettivo

Introdurre un flusso a due step:

1. ricerca e ascolto del risultato
2. conferma esplicita dell'utente per navigare al primo risultato

Risultati attesi:

- nessun `wx.CallLater` usato per chiudere il dialog dopo un esito trovato
- il dialog chiude con `wx.ID_OK` solo su azione esplicita dell'utente
- il dialog chiude con `wx.ID_CANCEL` su `Escape` o pulsante chiudi
- i test coprono il nuovo stato di conferma e il reset dei risultati

---

## 3. File coinvolti

- MODIFY `bingo_game/ui/dialogo_ricerca.py`
  - aggiunta dello stato di conferma
  - nuova azione esplicita `Vai al risultato`
  - gestione focus e shortcut coerenti con NVDA
- MODIFY `bingo_game/ui/finestra_gioco.py`
  - conferma della lettura del return code del dialog
  - navigazione al primo risultato solo su `wx.ID_OK`
  - nessuna navigazione su `wx.ID_CANCEL`
- MODIFY `tests/unit/test_dialogo_ricerca_persistente.py`
  - sostituzione dei test basati sul timer
  - nuovi test per stato di conferma e pulsante di navigazione

Nessun file da creare o eliminare nel codice applicativo.
Nessuna modifica a domain, eventi o renderer.

---

## 4. Fasi sequenziali

### FASE 1 — Rifattorizzare `DialogoRicercaNumero`

Obiettivo: trasformare il dialog da flusso a timer a flusso a conferma esplicita.

Passi:

1. Rimuovere ogni uso di `wx.CallLater` nel percorso `trovato`.
2. Aggiungere stato esplicito di conferma:
   - `_primo_risultato`
   - `_risultato_pronto_per_conferma`
3. Aggiungere un controllo esplicito `Vai al risultato`, inizialmente disabilitato.
4. Dopo una ricerca con esito `trovato`:
   - salvare il primo risultato
   - abilitare il controllo di conferma
   - spostare il focus sul controllo di conferma
5. Dopo una ricerca con esito `non_trovato`:
   - resettare `_primo_risultato`
   - disabilitare il controllo di conferma
   - riportare il focus all'input
6. Gestire `Invio` in modo coerente con il focus attuale:
   - su input o pulsante cerca: esegue la ricerca
   - su pulsante `Vai al risultato`: chiude con `wx.ID_OK`

Commit proposto:
`fix(ui): dialogo ricerca richiede conferma esplicita prima della navigazione`

### FASE 2 — Verificare e rifinire `FinestraGioco`

Obiettivo: assicurare che il frame consumi il risultato del dialog senza effetti collaterali.

Passi:

1. Verificare che `_apri_ricerca_numero()` legga `_primo_risultato` solo se `rc == wx.ID_OK`.
2. Confermare che il ramo `wx.ID_CANCEL` ripristini il focus sulla griglia senza navigazione.
3. Se necessario, aggiungere logica difensiva per evitare uso di risultati nulli o stantii.
4. Lasciare invariata la responsabilità del metodo `_naviga_a_risultato_ricerca()`.

Commit proposto:
`fix(ui): finestra gioco naviga solo dopo conferma esplicita del dialog ricerca`

### FASE 3 — Aggiornare i test unitari

Obiettivo: sostituire la suite basata sul timer con test orientati allo stato del dialog.

Passi:

1. Rimuovere o riscrivere i test che verificano `wx.CallLater`.
2. Aggiungere test per i seguenti scenari:
   - esito trovato abilita il controllo `Vai al risultato`
   - esito trovato imposta `_primo_risultato`
   - esito non trovato resetta `_primo_risultato`
   - esito non trovato lascia il dialog aperto
   - pressione del controllo `Vai al risultato` chiama `EndModal(wx.ID_OK)`
   - pressione `Escape` chiude con `wx.ID_CANCEL`
   - un nuovo tentativo fallito dopo un successo precedente non riusa il risultato vecchio
3. Eseguire test mirati del file.

Commit proposto:
`test(ui): aggiorna i test del dialogo ricerca per il flusso a conferma esplicita`

---

## 5. Test Plan

### Unit

- `tests/unit/test_dialogo_ricerca_persistente.py`
- eventuali test mirati su `FinestraGioco` se esistono fixture già disponibili

### Integration/manuale

Scenario 1:

1. aprire la ricerca con `Ctrl+F`
2. cercare un numero trovato
3. ascoltare il messaggio completo di NVDA
4. verificare che il dialog resti aperto
5. premere `Invio` su `Vai al risultato`
6. verificare la navigazione alla prima occorrenza

Scenario 2:

1. cercare un numero non trovato
2. verificare che il dialog resti aperto
3. verificare che il focus torni all'input
4. verificare che `Vai al risultato` sia disabilitato

Scenario 3:

1. ottenere un risultato trovato
2. senza confermare, premere `Escape`
3. verificare ritorno alla griglia senza navigazione

---

## 6. Dipendenze

- `EventoRicercaNumeroInCartelle` deve continuare a esporre `esito` e `risultati`.
- `RisultatoRicercaNumeroInCartella` deve continuare a fornire `numero_cartella`, `indice_riga`, `indice_colonna`.
- `FinestraGioco` gia' supporta la navigazione al primo risultato; la fase 2 e' soprattutto di conferma e pulizia del flusso.

---

## 7. Rischi

- Ambiguità di `Invio` se il focus non viene spostato chiaramente dopo la ricerca.
- Stato stantio del pulsante di conferma dopo ricerche consecutive.
- Regressione del comportamento `Escape` se la nuova logica intercetta male `EVT_CHAR_HOOK`.

Mitigazioni:

- focus esplicito sul controllo di conferma dopo un esito trovato
- reset completo dello stato a ogni nuova ricerca
- test separati per `Invio`, `Escape`, trovato e non trovato

---

## 8. Criteri di completamento

- `DialogoRicercaNumero` non usa più timer per auto-chiudersi dopo un risultato trovato.
- L'utente deve poter ascoltare il risultato e solo dopo confermare la navigazione.
- Il comportamento `Cancel` resta invariato e sicuro.
- I test mirati della ricerca passano.
- La verifica manuale con NVDA conferma che il parlato non viene interrotto dalla chiusura automatica.
