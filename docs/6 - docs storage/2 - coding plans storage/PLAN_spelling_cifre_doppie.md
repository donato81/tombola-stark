# PLAN — Spelling cifre doppie nei numeri estratti

**Versione target:** post-alfa
**Data:** 2026-04-14
**Autore:** Agent-Plan / Agent-Orchestrator
**Riferimento design:** `docs/2 - projects/DESIGN_spelling_cifre_doppie.md`
**Riferimento analisi:** `docs/4 - reports/REPORT_ANALISI_spelling_cifre_doppie_2026-04-14.md`
**Status:** READY

---

## 1. Prerequisiti

**Dipendenza temporale (non tecnica):**
Il fix del messaggio di benvenuto NVDA (feature `fix_benvenuto_interrupt_nvda`,
piano `PLAN_fix_benvenuto_interrupt_nvda_v0.12.4.md`) deve essere completato
e committato prima di questa feature.

Motivazione: entrambe le feature modificano il flusso di annunci vocali in
`finestra_gioco.py`. Implementarle in parallelo genera conflitti di merge e
difficoltà nel test manuale. Lo spelling degli estratti va costruito su un
flusso di annunci già stabile.

---

## 2. Passi di implementazione

### Passo 1 — Aggiungere il dizionario verbale in `locales/it.py`

**File:** `bingo_game/ui/locales/it.py`

**Cosa aggiungere:**
Una costante `CIFRE_VERBALI` di tipo `dict[int, str]` (o equivalente
`MappingProxyType`) che mappa ogni cifra da 0 a 9 alla sua forma verbale
italiana minuscola:

```
0 → "zero"
1 → "uno"
2 → "due"
3 → "tre"
4 → "quattro"
5 → "cinque"
6 → "sei"
7 → "sette"
8 → "otto"
9 → "nove"
```

La costante va inserita nella sezione delle strutture dati di supporto,
con un commento descrittivo che specifica lo scopo (spelling vocale delle
cifre per annunci NVDA) e il range valido (0–9).

**Commit:** `feat(locales): aggiungi dizionario CIFRE_VERBALI per spelling NVDA`

---

### Passo 2 — Aggiungere la chiave template spelling in `locales/it.py`

**File:** `bingo_game/ui/locales/it.py`

**Cosa aggiungere:**
Una chiave nel dizionario `MESSAGGI_EVENTI` (o in un dizionario loop
equivalente già presente) con nome `LOOP_SPELLING_NUMERO_ESTRATTO`.

Valore: tupla con una sola stringa contenente due placeholder:
`("{decina}. {unita}.",)`

Il commento sopra la chiave deve specificare:
- Scopo: secondo annuncio NVDA dopo la lettura del numero estratto
- Quando viene emessa: solo per numeri a due cifre (10–90)
- Placeholder: `{decina}` = forma verbale della decina, `{unita}` = forma
  verbale dell'unità
- Esempio output: per il numero 61 → "Sei. Uno."

**Commit:** Stesso commit del Passo 1 (i due passi in `locales/it.py` formano
un'unica modifica atomica al file).
Commit message consolidato: `feat(locales): aggiungi CIFRE_VERBALI e LOOP_SPELLING_NUMERO_ESTRATTO`

---

### Passo 3 — Aggiungere la funzione di spelling in `finestra_gioco.py`

**File:** `bingo_game/ui/finestra_gioco.py`

**Cosa aggiungere:**
Una funzione pura a livello di modulo (non metodo di classe) chiamata
`_spelling_numero(n: int) -> str` che:

1. Calcola la decina: `decina = n // 10`
2. Calcola l'unità: `unita = n % 10`
3. Legge `CIFRE_VERBALI[decina]` e `CIFRE_VERBALI[unita]` da `locales/it.py`
4. Legge il template `LOOP_SPELLING_NUMERO_ESTRATTO` dal catalogo `it.py`
5. Restituisce la stringa formattata, ad esempio `"Sei. Uno."`

La funzione deve avere type hints (`int → str`) e non deve dipendere da
stato globale o da istanze di classe. Il catalogo `it.py` viene importato
puntualmente o via l'import già presente nel modulo.

Posizionamento: nel file, sopra la definizione della classe principale o
nella sezione delle helper function a livello modulo, prima delle binding
della finestra.

**Import da aggiungere in `finestra_gioco.py`:**
`from bingo_game.ui.locales.it import CIFRE_VERBALI, MESSAGGI_EVENTI`
(o il nome esatto usato nella struttura dati che ospita il template)

**Commit:** `feat(ui): aggiungi funzione _spelling_numero per spelling NVDA`

---

### Passo 4 — Aggiungere la chiamata spelling nel Punto A (estrazione turno principale)

**File:** `bingo_game/ui/finestra_gioco.py`
**Posizione:** Metodo che gestisce l'estrazione nel turno principale (intorno
alla riga 928–929 nel sorgente attuale).

**Cosa modificare:**
Subito dopo la riga:
```python
self._renderer.annuncia_numero_estratto(numero, self._turno_corrente)
```

Aggiungere, condizionato a `isinstance(numero, int) and numero >= 10`:
```python
self._renderer.mostra_messaggio_sistema(_spelling_numero(numero))
```

La guardia `numero >= 10` esclude i numeri da 1 a 9 (che nella tombola
napoletana standard non sono presenti sul tabellone, ma la guardia è buona
pratica difensiva).

**Commit:** Questo passo e il Passo 5 formano un commit atomico unico.

---

### Passo 5 — Aggiungere la chiamata spelling nel Punto B (azione automatica / bot)

**File:** `bingo_game/ui/finestra_gioco.py`
**Posizione:** Secondo punto di chiamata a `annuncia_numero_estratto` (intorno
alla riga 1421–1423 nel sorgente attuale), simmetrico al Punto A.

**Cosa modificare:**
Stessa modifica del Passo 4: aggiungere subito dopo l'annuncio principale
la chiamata a `mostra_messaggio_sistema` con lo spelling, con la stessa
guardia condizionale.

**Commit consolidato per Passo 4 + Passo 5:**
`feat(ui): aggiungi spelling cifre doppie post-annuncio estratto`

---

## 3. Struttura della funzione di spelling (concettuale)

**Input:** un intero `n` nel range 10–90 (inclusi).
**Output:** una stringa nel formato `"<decina_verbale>. <unità_verbale>."`.

**Procedura:**
1. Dividi `n` per 10 con divisione intera → ottieni la cifra delle decine (1–9).
2. Calcola il resto di `n` diviso per 10 → ottieni la cifra delle unità (0–9).
3. Recupera la parola verbale per la cifra delle decine da `CIFRE_VERBALI`.
4. Recupera la parola verbale per la cifra delle unità da `CIFRE_VERBALI`.
5. Componi la stringa formattata secondo il template del catalogo, con
   la prima lettera della decina maiuscola (la capitalizzazione può essere
   applicata nel template stesso o nella funzione).

**Esempio traccia:**
- Input: 61
- Decina: 61 // 10 = 6 → "sei"
- Unità: 61 % 10 = 1 → "uno"
- Output: "Sei. Uno."

**Esempio traccia per multiplo di 10:**
- Input: 70
- Decina: 70 // 10 = 7 → "sette"
- Unità: 70 % 10 = 0 → "zero"
- Output: "Sette. Zero."

---

## 4. Template in `locales/it.py`

**Chiave:** `LOOP_SPELLING_NUMERO_ESTRATTO`

**Scopo:** Fornire il formato stringa del secondo annuncio NVDA (spelling
delle due cifre del numero estratto).

**Placeholder necessari:**
- `{decina}` — parola verbale della cifra delle decine (es. "Sei")
- `{unita}` — parola verbale della cifra delle unità (es. "Uno")

**Esempio valore atteso nel catalogo:**
```python
"LOOP_SPELLING_NUMERO_ESTRATTO": (
    "{decina}. {unita}.",
),
```

Il renderer e la funzione di spelling si occupano di capitalizzare la prima
lettera (`{decina}` in maiuscolo) prima di sostituire il placeholder. In
alternativa, il dizionario `CIFRE_VERBALI` può contenere già le forme
con iniziale maiuscola — dettaglio da decidere in fase di implementazione
purché il comportamento finale sia coerente.

---

## 5. Test manuale con NVDA

**Prerequisito:** NVDA attivo, partita avviata con almeno un giocatore umano
e un bot.

### Test 5.1 — Multiplo di 10 (unità = zero)

1. Avviare la partita.
2. Premere Ctrl+Enter per estrarre numeri fino a che esce un multiplo di 10
   (es. 20, 30, 40, 50, 60, 70, 80, 90). Se nessuno esce nei primi turni,
   continuare.
3. Al momento dell'estrazione, NVDA deve annunciare:
   - Primo annuncio: "Turno N. Numero estratto: [numero]."
   - Secondo annuncio: "[decina_verbale]. Zero."
   Esempio per 50: "Cinque. Zero."

### Test 5.2 — Numero con decina intermedia e unità significativa

1. Estrarre numeri fino a che esce un numero del tipo XY con Y ≠ 0 e X ≥ 3
   (es. 45, 67, 38).
2. NVDA deve annunciare le due cifre separate da pausa.
   Esempio per 67: "Sei. Sette."

### Test 5.3 — Numero 90

1. Continuare la partita fino all'estrazione del 90 (o usare un setup di test
   che garantisce l'estrazione forzata).
2. NVDA deve annunciare: "Nove. Zero."

### Test 5.4 — Nessuna regressione

1. Verificare che dopo ogni spelling il gioco prosegua normalmente:
   il pulsante "Passa turno" rimane attivo, la griglia si aggiorna,
   i bot rispondono nella finestra d'azione.
2. Controllare `logs/stderr_capture.txt`: deve essere vuoto o senza
   nuove eccezioni.

---

## 6. Criterio di completamento

La feature si considera conclusa quando:

1. I quattro test manuali con NVDA (5.1–5.4) sono superati senza anomalie.
2. Nessuna regressione nei test automatici esistenti (`py -m unittest tests/`
   o equivalente per l'ambiente).
3. Le modifiche a `locales/it.py` e `finestra_gioco.py` sono committate con
   i messaggi di commit indicati in questo piano.
4. `CHANGELOG.md` sezione `[Unreleased]` riporta la voce:
   `Added: spelling cifre doppie post-annuncio nel flusso di estrazione (accessibilità NVDA)`
