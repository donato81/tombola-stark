---
type: plan
feature: report_finale_storico_premi_nvda
agent: Agent-Plan
status: DRAFT
version: v0.15.0
design_ref: docs/2 - projects/DESIGN_report_finale_storico_premi_nvda.md
date: 2026-04-13
---

# PLAN — Report finale esaustivo e storico premi NVDA v0.15.0

## 1. Executive Summary

- **Tipo**: enhancement cross-layer su dominio, application e presentation
- **Priorita**: alta — gap residuo per la chiusura della versione alfa
- **Branch**: main
- **Versione target**: v0.15.0
- **Commit attesi**: 4
- **Design di riferimento**: [DESIGN_report_finale_storico_premi_nvda.md](../2%20-%20projects/DESIGN_report_finale_storico_premi_nvda.md) — DRAFT
- **Report di partenza**: [REPORT_DIAGNOSI_ALFA_2026-04-13.md](../4%20-%20reports/REPORT_DIAGNOSI_ALFA_2026-04-13.md)

---

## 2. Problema e Obiettivo

Il codice corrente ha gia chiuso i gap di naming NVDA dei pannelli e il
messaggio di orientamento iniziale, ma lascia aperti i problemi piu strutturali
del post-partita e della lettura dei premi:

- il report finale usa `premi_gia_assegnati`, che contiene chiavi tecniche
  e non eventi leggibili dall'utente
- `Ctrl+I` non puo leggere i vincitori dei premi gia assegnati
- il pannello finale non espone uno storico chiaro della partita

**Obiettivo**: introdurre `storico_premi` in `Partita`, riusarlo per
`Ctrl+I` e per il report finale, e arricchire il payload di fine partita con
dati sufficienti per un riepilogo accessibile e informativo.

---

## 3. File coinvolti

| File | Operazione | Note |
|---|---|---|
| `bingo_game/partita.py` | MODIFY | Nuovo attributo `storico_premi`, aggiornamento in assegnazione premi |
| `bingo_game/comandi_partita.py` | MODIFY | `dettaglio_premi()` deve usare `storico_premi` |
| `bingo_game/ui/finestra_gioco.py` | MODIFY | Costruzione payload report finale arricchito |
| `bingo_game/ui/renderers/renderer_wx.py` | MODIFY | Vocalizzazione report finale coerente col nuovo payload |
| `tests/test_partita.py` | MODIFY | Test su storico premi e persistenza ordine eventi |
| `tests/test_comandi_partita.py` | MODIFY | Test su `dettaglio_premi()` con vincitori reali |
| `CHANGELOG.md` | MODIFY | Entry [Unreleased] |
| `docs/API.md` | MODIFY | Contratto report finale e nuovi dati esposti |

File deliberatamente esclusi:

- `bingo_game/ui/locales/it.py` — non necessario salvo rifiniture testuali
- `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` — nessun nuovo binding
- `bingo_game/events/*` — i dati richiesti possono essere espressi senza nuovi eventi

---

## 4. Fasi implementative

### Fase A — Dominio: introdurre `storico_premi`

**File**: `bingo_game/partita.py`

Operazioni:

1. Aggiungere in `__init__` l'attributo `self.storico_premi: list[dict[str, Any]] = []`.
2. Nel blocco di assegnazione premi, per ogni nuovo premio validato:
   - continuare a popolare `premi_gia_assegnati`
   - continuare a chiudere `premi_tipo_chiusi`
   - aggiungere un record esplicito a `storico_premi` con almeno:
     `giocatore`, `id_giocatore`, `cartella`, `premio`, `riga`, `turno`
3. Mantenere `ultimo_premio_evento` sincronizzato con l'ultimo record.

Criteri di uscita:

- `storico_premi` vuoto a inizio partita
- un record per ogni assegnazione valida
- ordine stabile e coerente con la validazione del dominio

Commit previsto:
`feat(domain): aggiunge storico_premi a Partita`

---

### Fase B — Application: aggiornare `dettaglio_premi()`

**File**: `bingo_game/comandi_partita.py`

Operazioni:

1. Lasciare invariato `stato_premi()` salvo eventuali allineamenti minori.
2. Riscrivere `dettaglio_premi()` per leggere `self._partita.storico_premi`.
3. Ordinare l'output seguendo `_SEQUENZA_PREMI` e, a parita di premio,
   l'ordine temporale dello storico.
4. Produrre una frase leggibile da NVDA del tipo:
   `Ambo vinto da Bot 1, cartella 2.`

Criteri di uscita:

- nessun uso di `premi_tipo_chiusi` come unica fonte del dettaglio
- output con vincitore reale in tutti i casi non vuoti
- fallback corretto se nessun premio e stato assegnato

Commit previsto:
`feat(application): aggiorna dettaglio_premi con vincitori reali`

---

### Fase C — Presentazione: payload report finale arricchito

**File**: `bingo_game/ui/finestra_gioco.py`

Operazioni:

1. Sostituire nel `dati_report` l'uso diretto di `premi_gia_assegnati` con:
   - `storico_premi`
   - `numeri_estratti`
   - statistiche sintetiche del giocatore umano
   - eventuale lista premi vinti dall'umano
2. Mantenere compatibilita col renderer corrente finche non viene aggiornato.
3. Non introdurre side effect nel flusso di fine partita.

Struttura minima attesa del nuovo payload:

```python
{
    "turni_giocati": int,
    "conteggio_estratti": int,
    "numeri_estratti": list[int],
    "storico_premi": list[dict[str, Any]],
    "vincitore_tombola": str,
    "giocatori": list[str],
    "riepilogo_umano": dict[str, Any],
}
```

Commit previsto:
`feat(presentation): arricchisce dati_report finale della partita`

---

### Fase D — Renderer e pannello finale

**File**: `bingo_game/ui/renderers/renderer_wx.py`

Operazioni:

1. Aggiornare `mostra_report_finale()` per vocalizzare dati leggibili da
   `storico_premi` invece che da `premi_gia_assegnati`.
2. Costruire un sommario iniziale breve e un dettaglio piu ricco nel log.
3. Allineare `_wx_mostra_report_finale()` e `PannelloRiepilogoFinale` al
   nuovo contratto.

Commit previsto:
`feat(ui): aggiorna riepilogo finale con storico premi leggibile`

---

## 5. Test Plan

### Test unitari

- `tests/test_partita.py`
  - `storico_premi` inizialmente vuoto
  - `storico_premi` cresce dopo una verifica premi valida
  - `ultimo_premio_evento` coincide con l'ultimo elemento dello storico
  - co-vittorie registrate come elementi distinti

- `tests/test_comandi_partita.py`
  - `dettaglio_premi()` restituisce fallback se lo storico e vuoto
  - `dettaglio_premi()` include premio, vincitore e cartella
  - l'ordine segue la sequenza logica dei premi

### Test manuali NVDA

- Durante la partita, `Ctrl+I` legge i vincitori reali e non solo i tipi.
- A fine partita, il riepilogo vocale non contiene stringhe `? per ?`.
- Il pannello finale mostra i premi in forma leggibile.

### Validazioni minime

- `python -m py_compile` sui file modificati
- test mirati su `partita` e `comandi_partita`

---

## 6. Rischi operativi

- Possibile impatto sui test che assumono la struttura attuale dei premi.
- Necessita di decidere se il `turno` va salvato nello storico direttamente in
  `Partita` o passato dal layer superiore.
- Possibile crescita del testo finale se si vocalizza tutto lo storico in una
  sola frase: va mantenuto un sommario breve.

---

## 7. Criteri di completamento

- [ ] `storico_premi` introdotto e valorizzato correttamente
- [ ] `Ctrl+I` legge vincitori reali
- [ ] report finale senza chiavi opache
- [ ] riepilogo finale visivo allineato al nuovo payload
- [ ] test mirati verdi
- [ ] changelog e API aggiornati