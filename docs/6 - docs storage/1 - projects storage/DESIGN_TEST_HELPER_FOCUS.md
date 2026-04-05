---
type: design
feature: test_helper_focus
agent: Agent-Design
status: COMPLETED
version: v1.0
date: 2026-03-30
report_ref: docs/4 - reports/report_verifica_lavori_test_helper_focus.md
---

## Metadati

tipo: design
titolo: Design test diretti per GestioneFocusMixin
data_creazione: 2026-03-30
agente: Agent-Design
stato: completato
feature: test_helper_focus
versione_progetto: v1.0
report: docs/4 - reports/report_verifica_lavori_test_helper_focus.md

## Contenuto

### Obiettivo

Portare a copertura diretta e isolata i metodi di `GestioneFocusMixin`
attualmente scoperti o solo parzialmente coperti, usando esclusivamente
`unittest` e uno stub minimale. Il file di test dovra' verificare i casi
di errore, i casi validi e il reset completo dei focus, senza dipendere da
`GiocatoreUmano`.

### Architettura dello stub

`GestioneFocusMixin` non e' istanziabile direttamente: presuppone che la
classe concreta esponga `cartelle`, `_indice_cartella_focus`,
`_indice_riga_focus` e `_indice_colonna_focus`.

Per isolare il mixin dal resto del giocatore verra' usato questo stub,
vincolante per tutta l'implementazione:

```python
class StubFocus(GestioneFocusMixin):
    def __init__(self):
        self.cartelle = []
        self._indice_cartella_focus = None
        self._indice_riga_focus = None
        self._indice_colonna_focus = None
```

Questo stub e' necessario per testare il comportamento puro del mixin,
evitando dipendenze non necessarie verso `GiocatoreUmano`.

### Struttura del file di test

Il file da creare sara': `tests/unit/test_helper_focus.py`.

Struttura prevista:

- una sola classe `TestGestioneFocusMixin(unittest.TestCase)`
- un metodo `setUp` che istanzia `StubFocus`
- nel `setUp`, creazione di una `Cartella` di test riutilizzabile

### Gruppi di test e ordine di scrittura

#### Gruppo 1 — Cartella (metodi 2 e 3)

Casi mancanti rispetto alla copertura indiretta esistente.

#### Gruppo 2 — Riga (metodi 5, 6, 7)

Copertura diretta completa, da usare come modello interno per i test colonna.

#### Gruppo 3 — Colonna (metodi 8, 9, 10)

Copertura diretta completa, speculare al gruppo riga.

#### Gruppo 4 — Reset (metodo 15)

Test del reset completo di tutti e tre i focus.

### Lista completa dei test da implementare

#### Gruppo 1 — Cartella

- `test_esito_focus_cartella_impostato_rigoroso_senza_focus`
  Input: cartella presente, focus None, `auto_imposta=False`
  Output atteso: `ok=False`, `errore="FOCUS_CARTELLA_NON_IMPOSTATO"`

- `test_esito_focus_cartella_in_range_fuori_range_superiore`
  Input: focus impostato su indice inesistente, ad esempio 5 con 1 cartella
  Output atteso: `ok=False`, `errore="FOCUS_CARTELLA_FUORI_RANGE"`

- `test_esito_focus_cartella_in_range_indice_negativo`
  Input: focus impostato su indice negativo
  Output atteso: `ok=False`, `errore="FOCUS_CARTELLA_FUORI_RANGE"`

#### Gruppo 2 — Riga

- `test_esito_focus_riga_impostata_cartella_assente`
  Input: nessuna cartella
  Output atteso: `ok=False`, errore propagato da cartella

- `test_esito_focus_riga_impostata_riga_assente`
  Input: cartella valida in focus, riga None
  Output atteso: `ok=False`, `errore="FOCUS_RIGA_NON_IMPOSTATA"`

- `test_esito_focus_riga_impostata_ok`
  Input: cartella valida, riga impostata
  Output atteso: `ok=True`

- `test_esito_focus_riga_in_range_fuori_range_superiore`
  Input: riga impostata su indice inesistente, ad esempio 5
  Output atteso: `ok=False`, `errore="FOCUS_RIGA_FUORI_RANGE"`

- `test_esito_focus_riga_in_range_indice_negativo`
  Input: riga impostata su indice negativo
  Output atteso: `ok=False`, `errore="FOCUS_RIGA_FUORI_RANGE"`

- `test_esito_focus_riga_in_range_ok`
  Input: cartella valida, riga in range
  Output atteso: `ok=True`

- `test_esito_focus_riga_valido_riga_fuori_range`
  Input: cartella valida, riga fuori range
  Output atteso: `ok=False`, `errore="FOCUS_RIGA_FUORI_RANGE"`

#### Gruppo 3 — Colonna

- `test_esito_focus_colonna_impostata_cartella_assente`
  Input: nessuna cartella
  Output atteso: `ok=False`, errore propagato da cartella

- `test_esito_focus_colonna_impostata_colonna_assente`
  Input: cartella valida in focus, colonna None
  Output atteso: `ok=False`, `errore="FOCUS_COLONNA_NON_IMPOSTATA"`

- `test_esito_focus_colonna_impostata_ok`
  Input: cartella valida, colonna impostata
  Output atteso: `ok=True`

- `test_esito_focus_colonna_in_range_fuori_range_superiore`
  Input: colonna impostata su indice inesistente, ad esempio 10
  Output atteso: `ok=False`, `errore="FOCUS_COLONNA_FUORI_RANGE"`

- `test_esito_focus_colonna_in_range_indice_negativo`
  Input: colonna impostata su indice negativo
  Output atteso: `ok=False`, `errore="FOCUS_COLONNA_FUORI_RANGE"`

- `test_esito_focus_colonna_in_range_ok`
  Input: cartella valida, colonna in range
  Output atteso: `ok=True`

- `test_esito_focus_colonna_valido_colonna_assente`
  Input: cartella valida, colonna None
  Output atteso: `ok=False`

- `test_esito_focus_colonna_valido_colonna_fuori_range`
  Input: cartella valida, colonna fuori range
  Output atteso: `ok=False`, `errore="FOCUS_COLONNA_FUORI_RANGE"`

- `test_esito_focus_colonna_valido_ok`
  Input: cartella valida, colonna in range
  Output atteso: `ok=True`

#### Gruppo 4 — Reset

- `test_reset_focus_cartella_riga_e_colonna_azzera_tutto`
  Input: tutti i focus gia' a None
  Output atteso: tutti i focus restano None dopo il reset

- `test_reset_focus_cartella_riga_e_colonna_da_stato_impostato`
  Input: tutti e tre i focus impostati su valori validi
  Output atteso: tutti i focus tornano None dopo il reset

### Cosa NON fare

- Non scrivere test per i metodi 1, 4, 11, 12, 13, 14.
- Non correggere i docstring dei metodi 11 e 13.
- Non usare `pytest`.
- Non toccare file `.py` in questa fase.

## Stato Avanzamento

- [x] Design creato
- [x] Validato
- [x] Passato a implementazione