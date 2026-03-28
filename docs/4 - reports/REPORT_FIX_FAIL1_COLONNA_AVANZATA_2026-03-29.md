---
type: report
feature: fix_fail1_colonna_avanzata
agent: Agent-Analyze
status: DRAFT
date: 2026-03-29
title: Report analisi FAIL-1 sul test colonna avanzata
---

## Metadati

tipo: report
titolo: Report analisi FAIL-1 sul test colonna avanzata
data_creazione: 2026-03-29
agente: Agent-Analyze
stato: bozza
feature: fix_fail1_colonna_avanzata

## Contenuto

### Trigger

Fallimento del test `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`
in `tests/test_giocatore_umano.py` con `AssertionError: 'vuota' not found in
EsitoAzione(...)`.

### Sommario esecutivo

Il test e' rimasto ancorato a un comportamento vecchio: assume che
`sposta_focus_colonna_sinistra_avanzata()` ritorni una stringa pronta da
analizzare con `assertIn`. La firma reale del metodo ora ritorna un oggetto
`EsitoAzione` con un evento strutturato `EventoNavigazioneColonnaAvanzata`.

Il guasto non e' nel comportamento applicativo, ma nel modo in cui il test
osserva il risultato. Il test deve quindi smettere di cercare testo libero e
controllare i campi strutturati dell'esito e dell'evento.

### Dettaglio osservazioni

#### Bug del test

- Test coinvolto: `tests/test_giocatore_umano.py`, funzione
  `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale`.
- Causa diretta: uso di `assertIn("Colonna 4:", risultato)`,
  `assertIn(str(numero), risultato)`, `assertIn("Segnati:", risultato)` e
  `assertIn("vuota", risultato)` su un oggetto dataclass, non su una stringa.
- Traccia errore osservata: `AssertionError: 'vuota' not found in EsitoAzione(...)`.

#### Firma attuale del metodo

Il metodo `sposta_focus_colonna_sinistra_avanzata()` in
`bingo_game/players/giocatore_umano.py` ritorna `EsitoAzione`.

Nel caso di movimento normale verso sinistra:
- `risultato.ok` e' `True`
- `risultato.errore` e' `None`
- `risultato.evento` e' un `EventoNavigazioneColonnaAvanzata`
- l'evento ha `esito="mostra"`
- il numero colonna esposto all'utente e' 1-based, quindi la colonna interna 4
  diventa `numero_colonna_corrente == 4`

#### Struttura osservabile di EsitoAzione

Campi utili al test:
- `ok`
- `errore`
- `evento`

Regola pratica:
- se `ok=True`, il controllo va fatto dentro `evento`
- se `ok=False`, il controllo va fatto su `errore`

#### Struttura osservabile di EventoNavigazioneColonnaAvanzata

Campi utili al test in questo scenario:
- `esito`
- `numero_colonna_corrente`
- `colonna_semplice`
- `stato_colonna`
- `numeri_segnati_colonna_ordinati`

Nel caso di colonna vuota, il test non deve cercare la parola `vuota` dentro
l'oggetto. Deve invece verificare il dato strutturato che lo rappresenta,
cioe' `colonna_semplice`, dove le celle vuote sono rese con `"-"`.

#### Assertion da correggere

Nel test attuale vanno sostituite queste verifiche testuali:
- `assertIn("Colonna 4:", risultato)`
- ciclo `assertIn(str(numero), risultato)`
- `assertIn("vuota", risultato)`
- `assertIn("Segnati:", risultato)`

Con verifiche strutturate su:
- `risultato.ok`
- tipo di `risultato.evento`
- `risultato.evento.esito`
- `risultato.evento.numero_colonna_corrente`
- `risultato.evento.colonna_semplice`
- `risultato.evento.stato_colonna`
- `risultato.evento.numeri_segnati_colonna_ordinati`

### Raccomandazioni

- Correggere il test senza toccare il metodo applicativo.
- Usare assertion sui campi dell'evento invece che su testo gia' renderizzato.
- Limitare il fix al solo file `tests/test_giocatore_umano.py` nella fase di codifica.

### File analizzati

- `tests/test_giocatore_umano.py`
- `bingo_game/players/giocatore_umano.py`
- `bingo_game/events/eventi.py`
- `bingo_game/events/eventi_output_ui_umani.py`

## Stato Avanzamento

- [x] Bozza completata
- [ ] Revisionato
- [ ] Condiviso
