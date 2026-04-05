---
type: plan
feature: fix_fail1_colonna_avanzata
agent: Agent-Plan
status: DRAFT
version: v0.9.3
design_ref: docs/2 - projects/DESIGN_FIX_FAIL1_COLONNA_AVANZATA.md
date: 2026-03-29
report_ref: docs/4 - reports/REPORT_FIX_FAIL1_COLONNA_AVANZATA_2026-03-29.md
---

## Metadati

tipo: coding_plan
titolo: Piano correzione FAIL-1 su test colonna avanzata
data_creazione: 2026-03-29
agente: Agent-Plan
stato: bozza
feature: fix_fail1_colonna_avanzata
versione_progetto: v0.9.3
design: docs/2 - projects/DESIGN_FIX_FAIL1_COLONNA_AVANZATA.md
report: docs/4 - reports/REPORT_FIX_FAIL1_COLONNA_AVANZATA_2026-03-29.md

## Contenuto

### Executive Summary

Tipo intervento: fix di test
Priorita': alta
Branch: main
Target: un solo test fallito, nessuna modifica al codice applicativo
Versione di riferimento: v0.9.3

### Problema da risolvere

Il test `test_sposta_focus_colonna_sinistra_avanzata_movimento_normale` in
`tests/test_giocatore_umano.py` usa assertion basate su sottostringhe, ma il
metodo testato restituisce ormai un oggetto `EsitoAzione` con evento
strutturato. Questo genera un falso fallimento anche se il movimento del focus
funziona correttamente.

### Approccio tecnico

Intervenire solo nel blocco assertion del test, sostituendo i controlli su testo
con controlli su struttura. Il piano non prevede nessuna modifica al metodo
`sposta_focus_colonna_sinistra_avanzata()` e a nessun'altra parte del progetto.

### File da modificare

- `tests/test_giocatore_umano.py` — MODIFY
  - area da aggiornare: blocco del test dichiarato a partire da riga 1153
  - assertion obsolete rilevate attorno alle righe 1172, 1180 e 1184

### Fase unica di intervento

#### Fase A — Correzione del solo test fallito

Sostituire nel test:
- `assertIn("Colonna 4:", risultato)`
- ciclo `assertIn(str(numero), risultato)`
- `assertIn("vuota", risultato)`
- `assertIn("Segnati:", risultato)`

Con nuove assertion orientate all'oggetto:

```python
self.assertTrue(risultato.ok)
self.assertIsNone(risultato.errore)
self.assertIsInstance(risultato.evento, EventoNavigazioneColonnaAvanzata)
self.assertEqual(risultato.evento.esito, "mostra")
self.assertEqual(risultato.evento.numero_colonna_corrente, 4)

numeri_colonna4 = self.cartella1.get_numeri_colonna(4)
if numeri_colonna4:
    for numero in numeri_colonna4:
        self.assertIn(numero, risultato.evento.colonna_semplice)
    self.assertIsNotNone(risultato.evento.stato_colonna)
else:
    self.assertEqual(risultato.evento.colonna_semplice, ("-", "-", "-"))
```

Nota: prima del fix va verificato se la rappresentazione reale della colonna
vuota e' esattamente `("-", "-", "-")` oppure una variante equivalente.
Il test dovra' aderire ai dati reali esposti dall'evento.

### Dipendenze

- `docs/4 - reports/REPORT_FIX_FAIL1_COLONNA_AVANZATA_2026-03-29.md`
- `docs/2 - projects/DESIGN_FIX_FAIL1_COLONNA_AVANZATA.md`

### Rischi

- Correggere solo la prima assertion e lasciare il test ancora legato al testo.
- Assumere una forma della colonna vuota senza verificarla sui dati reali.
- Introdurre import aggiuntivi nel test senza necessità.

### Criterio di verifica

`py -3.10 -m unittest discover -s tests -q` deve terminare con `0 failures`.

### Project padre

- `docs/2 - projects/DESIGN_FIX_FAIL1_COLONNA_AVANZATA.md`

## Stato Avanzamento

- [x] Definito
- [ ] In implementazione
- [ ] Test superati
- [ ] Chiuso
