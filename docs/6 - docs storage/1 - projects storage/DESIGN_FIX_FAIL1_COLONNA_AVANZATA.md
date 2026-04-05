---
type: design
feature: fix_fail1_colonna_avanzata
agent: Agent-Design
status: DRAFT
version: v0.9.3
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_FAIL1_COLONNA_AVANZATA_2026-03-29.md
---

## Metadati

tipo: design
titolo: Design correzione FAIL-1 su test colonna avanzata
data_creazione: 2026-03-29
agente: Agent-Design
stato: bozza
feature: fix_fail1_colonna_avanzata
versione_progetto: v0.9.3
report: docs/4 - reports/REPORT_FIX_FAIL1_COLONNA_AVANZATA_2026-03-29.md

## Contenuto

### Obiettivo

Correggere il test `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`
in modo che osservi la struttura reale del valore restituito dal metodo,
senza alterare il comportamento di produzione.

### Contesto

Il metodo `sposta_focus_colonna_sinistra_avanzata()` non produce piu' una
stringa gia' pronta per l'utente. Produce un esito strutturato, pensato per
separare la logica dall'eventuale resa testuale finale. Il test invece legge
ancora il risultato come se fosse testo puro e per questo fallisce anche
quando il comportamento applicativo e' corretto.

### Componenti coinvolti

- `tests/test_giocatore_umano.py` come unico file da modificare nella fase di fix.
- `EsitoAzione` come contenitore del risultato del comando.
- `EventoNavigazioneColonnaAvanzata` come descrizione strutturata del movimento.

### Comportamento attuale vs atteso

Comportamento attuale del test:
- cerca frammenti di testo dentro `risultato`
- interpreta `risultato` come una stringa
- fallisce quando incontra un dataclass strutturato

Comportamento atteso del test:
- verifica `risultato.ok == True`
- verifica che `risultato.evento` sia un `EventoNavigazioneColonnaAvanzata`
- verifica che `risultato.evento.numero_colonna_corrente == 4`
- nel caso colonna vuota, controlla il campo strutturato appropriato
  dell'evento invece di cercare la parola `vuota`

### Schema nuove assertion

Le assertion corrette devono seguire questa logica:
- `risultato.ok == True`
- `risultato.errore is None`
- `isinstance(risultato.evento, EventoNavigazioneColonnaAvanzata)`
- `risultato.evento.esito == "mostra"`
- `risultato.evento.numero_colonna_corrente == 4`
- se la colonna contiene numeri:
  confrontare `risultato.evento.colonna_semplice` e i numeri segnati/visibili
- se la colonna e' vuota:
  verificare che `risultato.evento.colonna_semplice` rappresenti tre celle
  vuote, oppure che `risultato.evento.stato_colonna` confermi zero contenuto
  utile nella colonna, secondo la struttura reale esposta dall'evento

### Decisione architetturale

Il test deve controllare dati strutturati e non testo renderizzato.

Motivazione:
- la stringa finale puo' cambiare senza che il comportamento logico cambi
- il contratto stabile del metodo e' l'oggetto `EsitoAzione`
- l'evento e' il punto corretto in cui osservare il movimento di focus

### Vincoli

- Nessuna modifica fuori da `tests/test_giocatore_umano.py` nella fase di fix.
- Nessun adattamento del metodo produttivo solo per compiacere il test.
- Nessuna regressione su altri test della suite.

### Criteri di accettazione

- Il test `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale` passa.
- La suite completa arriva a 366/366 OK.
- Nessun altro file del progetto viene modificato nella fase implementativa.

### Coding plans correlati

- `docs/3 - coding plans/PLAN_FIX_FAIL1_COLONNA_AVANZATA.md`

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Approvato
- [ ] Archiviato
