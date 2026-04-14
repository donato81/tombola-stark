# REPORT DI ANALISI — Spelling cifre doppie nei numeri estratti

**Data:** 2026-04-14
**Autore:** Agent-Analyze / Agent-Orchestrator
**Feature:** Spelling cifre doppie nei numeri estratti (NVDA)
**Stato:** APPROVATO

---

## 1. Descrizione del problema e opportunità

Quando Tombola Stark estrae un numero a due cifre, NVDA legge la parola
intera, ad esempio "sessantuno". In condizioni normali questa lettura è
sufficiente. Tuttavia, in contesti di distrazione, rumore ambientale o
affaticamento uditivo, la seconda cifra di un numero come "sessantuno",
"diciassette" o "quarantotto" può risultare ambigua o non chiaramente
percepita.

Lo spelling cifra per cifra è un pattern consolidato nell'esperienza degli
utenti screen reader: sentire "sessantuno. Sei. Uno." riduce l'ambiguità
senza appesantire l'annuncio, perché le due frasi aggiuntive conservano
il ritmo naturale delle pause vocali prodotte da NVDA quando incontra un
punto fermo.

I numeri da 1 a 9 non necessitano di spelling perché la singola cifra non
genera mai ambiguità.

---

## 2. Analisi del codice esistente

### 2.1 Flusso di annuncio del numero estratto

Il flusso parte da `bingo_game/ui/finestra_gioco.py`.
Esistono due punti di invocazione del metodo di annuncio:

**Punto A — Estrazione nel turno principale**
File: `bingo_game/ui/finestra_gioco.py`
Linee indicative: intorno alla riga 928–929

```python
numero = risultato_est.get("numero_estratto", "?")
self._renderer.annuncia_numero_estratto(numero, self._turno_corrente)
```

**Punto B — Estrazione nel turno bot / azione automatica**
File: `bingo_game/ui/finestra_gioco.py`
Linee indicative: intorno alla riga 1421–1423

```python
numero = risultato.get("numero_estratto", "?")
self._renderer.annuncia_numero_estratto(numero, self._turno_corrente)
```

### 2.2 Implementazione nel renderer

Il renderer (`bingo_game/ui/renderers/renderer_wx.py`, riga 195) implementa
`annuncia_numero_estratto` costruendo la stringa vocale direttamente, senza
usare il catalogo `locales/it.py`:

```python
def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
    testo = f"Turno {numero_turno}. Numero estratto: {numero}."
    self._wx_aggiorna_output(testo)
    self._wx_avvia_lampeggio(numero)
    self._wx_aggiorna_header(turno=numero_turno, ultimo_numero=numero)
    self._ao2_vocalizza(testo)
```

Il renderer ha un metodo pubblico `mostra_messaggio_sistema` che, a differenza
di `annuncia_numero_estratto`, accetta una stringa preformattata e la vocalizzia
tramite `_ao2_vocalizza`. Questo metodo è già utilizzato in `finestra_gioco.py`
per altri annunci e non richiede modifiche al renderer.

### 2.3 Catalogo stringhe locales/it.py

File: `bingo_game/ui/locales/it.py`

Chiave esistente correlata (Game Loop v0.9.0):
```python
"LOOP_NUMERO_ESTRATTO": (
    "Numero estratto: {numero}.",
),
```

Non esiste attualmente alcuna chiave per lo spelling delle cifre.

Le convenzioni del catalogo sono:
- Chiavi uppercase con prefisso contestuale (es. `LOOP_`, `UMANI_`, `SISTEMA_`)
- Valori come `tuple[str, ...]` con righe separate
- Placeholder nel formato `{nome}`
- Commento descrittivo sopra ogni entry con placeholder documentati

---

## 3. Soluzione identificata

Aggiungere, subito dopo la chiamata a `annuncia_numero_estratto`, una seconda
vocalizzazione con lo spelling delle cifre. Esempio per il numero 61:

> Annuncio 1: "Turno 5. Numero estratto: 61."
> Annuncio 2 (new): "Sei. Uno."

La forma scelta prevede che le due cifre siano vocalizzate come frasi separate
con punto fermo, in modo che NVDA produca pause naturali tra di esse.

La logica di spelling è pura: dato un intero da 10 a 90, divide la decina
e l'unità, le mappa in forma verbale italiana tramite un dizionario statico,
e restituisce una stringa del tipo `"<decina_verbale>. <unità_verbale>."`.

Il secondo annuncio viene emesso da `finestra_gioco.py` tramite il metodo
`mostra_messaggio_sistema` del renderer (già esistente, già usato, non va
modificato).

---

## 4. Perimetro della modifica

### File da modificare

| File | Modifica |
|------|---------|
| `bingo_game/ui/locales/it.py` | Aggiunta mappa verbale cifre e chiave stringa per lo spelling |
| `bingo_game/ui/finestra_gioco.py` | Aggiunta chiamata spelling nei due punti di annuncio estratto |

### File da NON toccare

| File | Motivazione |
|------|-------------|
| `bingo_game/ui/renderers/renderer_wx.py` | Il renderer non va modificato per questa feature |
| `bingo_game/ui/renderers/base_renderer.py` | Stessa motivazione |
| `bingo_game/comandi_partita.py` | Logica di gioco, fuori perimetro |
| `bingo_game/partita.py` | Modello domain, fuori perimetro |
| `bingo_game/tabellone.py` | Modello domain, fuori perimetro |
| `bingo_game/events/**` | Nessuna modifica al sistema eventi |
| `tests/**` | Nessun test automatico previsto per questa feature |

---

## 5. Stima della complessità

**Bassa.**

Motivazione:
- La logica di spelling è puramente matematica: divisione intera per 10
  (decina) e modulo 10 (unità), seguito da lookup in un dizionario statico.
- I due punti di modifica in `finestra_gioco.py` sono simmetrici e
  richiedono l'aggiunta di 3–4 righe ciascuno.
- Nessuna modifica a interfacce pubbliche, eventi, modelli o test esistenti.
- Il dizionario delle 10 decine e delle 10 unità è completamente enumerabile
  (10 + 10 = 20 entry).

---

## 6. Rischi

**Rischio 1 — Doppio annuncio percepito come ridondante**
Se l'utente conosce già bene il numero (es. lo ha appena sentito), le due
cifre aggiuntive potranno sembrare verbosità. Mitigazione: la funzione può
essere resa opzionale tramite una flag di configurazione in un ciclo futuro.
Per ora il comportamento è sempre attivo.

**Rischio 2 — Ritardo percettivo tra annuncio principale e spelling**
Se `mostra_messaggio_sistema` viene chiamato immediatamente dopo
`annuncia_numero_estratto`, NVDA potrebbe interrompere il secondo annuncio
se il focus cambia o arriva un altro evento. Mitigazione: da verificare
empiricamente con NVDA durante il test manuale.

**Rischio 3 — Numero 90 e multipli di 10**
La seconda cifra dei multipli di 10 è "zero". Va documentata esplicitamente
nella mappa verbale e verificata sul campo.

---

## 7. Conclusione

**Go.**

La feature è ben delimitata, a bassa complessità e a rischio controllato.
Il vincolo di non toccare il renderer è rispettabile usando il metodo
`mostra_messaggio_sistema` già disponibile. L'intera logica di spelling
risiede in `locales/it.py` (dati) e `finestra_gioco.py` (assemblaggio),
in piena coerenza con l'architettura esistente.

Si raccomanda di procedere con la fase di design.
