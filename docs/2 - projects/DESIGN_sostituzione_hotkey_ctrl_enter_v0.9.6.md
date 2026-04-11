---
type: design
titolo: Sostituzione hotkey Ctrl+P con Ctrl+Enter per passa-turno
feature: sostituzione_hotkey_ctrl_enter
versione: 0.9.6
data_creazione: 2026-04-11
agent: Agent-Design
status: REVIEWED
---

# Design: Sostituzione hotkey Ctrl+P con Ctrl+Enter per passa-turno

## 1. Obiettivo

Sostituire il binding `Ctrl+P` (passa turno) con `Ctrl+Enter` in `FinestraGioco`.
Il cambiamento migliora l'ergonomia durante la partita: `Ctrl+Enter` è eseguibile
con la mano sinistra sul tasto Ctrl e pollice/indice destro su Enter, senza alcuno
spostamento della mano. La funzione di destinazione `_on_pulsante_principale`
resta invariata; cambia solo il trigger tastiera.

## 2. Componenti coinvolti

| File | Metodo | Riga | Ruolo |
|------|--------|------|-------|
| `bingo_game/ui/finestra_gioco.py` | `_on_char_hook` | 300 | Unico punto di binding da modificare |
| `bingo_game/ui/dialogo_ricerca.py` | `_on_char_hook` | — | Intercetta `WXK_RETURN` senza guard ctrl; non modificato (modale) |

### Dettaglio riga 300 — stato attuale

```python
# Ctrl+P — passa turno
if ctrl and key == ord("P"):
    self._on_pulsante_principale(None)
    return
```

### Stato target

```python
# Ctrl+Enter — passa turno
if ctrl and key == wx.WXK_RETURN:
    self._on_pulsante_principale(None)
    return
```

Nessun altro file è coinvolto.

## 3. Soluzione tecnica proposta

### Approccio

Sostituzione chirurgica di una singola condizione booleana in
`FinestraGioco._on_char_hook`. Il pattern `EVT_CHAR_HOOK` è già in uso;
non serve alcun cambio architetturale né nuova registrazione di handler.

### Logica di disambiguazione con `DialogoRicerca`

`DialogoRicerca._on_char_hook` intercetta `WXK_RETURN` (senza guard ctrl)
per confermare la ricerca. Il conflitto non esiste perché il dialog è modale:
quando è aperto, cattura tutti gli eventi tastiera prima che raggiungano
`FinestraGioco`. Quando il dialog è chiuso, solo `FinestraGioco` riceve
l'evento. Il comportamento è corretto e invariato con la modifica proposta.

### Diagramma flusso eventi (testuale)

```
Tasto premuto: Ctrl+Enter
       |
       v
FinestraGioco._on_char_hook attivo?
   |-- NO (DialogoRicerca aperto, modale) --> DialogoRicerca._on_char_hook
   |                                          --> conferma ricerca (WXK_RETURN, no ctrl)
   |-- SI --> ctrl=True AND key==wx.WXK_RETURN?
                |-- SI --> _on_pulsante_principale(None) --> passa turno
                |-- NO --> prosegue catena if
```

## 4. Impatto su test esistenti

Nessun test esistente verifica direttamente il binding `Ctrl+P` in
`_on_char_hook`. I test di `FinestraGioco` e `DialogoRicerca` che esercitano
metodi di dominio (passaggio turno, ricerca numero) non dipendono dal codice
tasto sorgente e rimangono validi senza modifiche.

Se si desidera aggiungere un test di regressione esplicito per il nuovo binding,
il test dovrà simulare un evento `EVT_CHAR_HOOK` con `key=wx.WXK_RETURN` e
`ControlDown()=True` e verificare che `_on_pulsante_principale` venga invocato.
Questa copertura è raccomandata ma non bloccante per la release.

## 5. Compatibilità NVDA

`Ctrl+Enter` non è assegnato a comandi NVDA predefiniti in modalità focus su
applicazioni wxPython. In modalità navigazione NVDA usa `Enter` da solo per
attivare elementi, ma la combinazione `Ctrl+Enter` è libera. Il rischio di
intercettazione da parte dello screen reader è basso.

Comportamenti NVDA invariati:
- Annuncio del risultato di `_on_pulsante_principale` (gestito dall'evento
  di dominio che aggiorna il testo accessibile della finestra)
- Nessuna modifica all'accessibilità del focus, dei label o degli annunci

## 6. Rischi e mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Conflitto con `DialogoRicerca` su `WXK_RETURN` | Bassa | Alto | Comportamento modale già garantisce isolamento degli eventi |
| NVDA intercetta `Ctrl+Enter` | Bassa | Medio | Testare con NVDA in modalità focus su `FinestraGioco` prima del rilascio |
| `Ctrl+P` usato inconsistentemente in altro handler non rilevato | Bassa | Basso | Analisi già condotta: un solo punto di binding `Ctrl+P` nel codebase |
| Regressione su test esistenti | Minima | Basso | Nessun test verifica il codice tasto direttamente |

## 7. File da modificare (checklist)

- [ ] `bingo_game/ui/finestra_gioco.py` — riga 300: sostituire
  `key == ord("P")` con `key == wx.WXK_RETURN`; aggiornare il commento
  da `# Ctrl+P — passa turno` a `# Ctrl+Enter — passa turno`
- [ ] `docs/CHANGELOG.md` — aggiungere voce `Changed` in `[Unreleased]`
- [ ] `docs/API.md` — aggiornare la tabella hotkey se presente
- [ ] *(opzionale)* aggiungere test di regressione per il nuovo binding
