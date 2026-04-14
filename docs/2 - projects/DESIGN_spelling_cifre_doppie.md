# DESIGN — Spelling cifre doppie nei numeri estratti

**Versione target:** post-alfa
**Data:** 2026-04-14
**Autore:** Agent-Design / Agent-Orchestrator
**Riferimento analisi:** `docs/4 - reports/REPORT_ANALISI_spelling_cifre_doppie_2026-04-14.md`
**Status:** REVIEWED

---

## 1. Obiettivo

Dopo ogni estrazione di un numero a due cifre (10–90), NVDA deve leggere
prima la parola intera del numero e poi, come secondo annuncio separato,
le due cifre che lo compongono in forma verbale italiana.

Esempio per il numero 61:
> "Turno 5. Numero estratto: sessantuno."
> pausa NVDA
> "Sei. Uno."

L'utente percepisce tre frasi distinte grazie ai punti fermi, ognuna
preceduta dalla pausa naturale prodotta da NVDA. Il pattern è familiare
agli screen reader user e riduce l'ambiguità sulla seconda cifra senza
aggiungere ridondanza eccessiva.

---

## 2. Comportamento attuale vs comportamento atteso

| Numero | Lettura attuale (NVDA) | Lettura attesa (NVDA) |
|--------|----------------------|----------------------|
| 10 | "Turno N. Numero estratto: 10." | "Turno N. Numero estratto: dieci." → "Uno. Zero." |
| 21 | "Turno N. Numero estratto: 21." | "Turno N. Numero estratto: ventuno." → "Due. Uno." |
| 45 | "Turno N. Numero estratto: 45." | "Turno N. Numero estratto: quarantacinque." → "Quattro. Cinque." |
| 61 | "Turno N. Numero estratto: 61." | "Turno N. Numero estratto: sessantuno." → "Sei. Uno." |
| 90 | "Turno N. Numero estratto: 90." | "Turno N. Numero estratto: novanta." → "Nove. Zero." |

Nota: il primo annuncio continua a essere prodotto dal renderer con il
numero come cifra (NVDA lo verbalizzerà in forma letterale automaticamente).
Il secondo annuncio è la stringa dello spelling, preformattata in italiano.

---

## 3. Forma dello spelling

### 3.1 Formato output

```
"<decina_verbale>. <unità_verbale>."
```

Esempi:
- 10 → `"Uno. Zero."`
- 21 → `"Due. Uno."`
- 45 → `"Quattro. Cinque."`
- 61 → `"Sei. Uno."`
- 90 → `"Nove. Zero."`

### 3.2 Mappa verbale delle decine (prima cifra)

| Cifra | Forma verbale |
|-------|--------------|
| 1 | uno |
| 2 | due |
| 3 | tre |
| 4 | quattro |
| 5 | cinque |
| 6 | sei |
| 7 | sette |
| 8 | otto |
| 9 | nove |

Nota: la cifra delle decine non è mai 0 per i numeri 10–90.

### 3.3 Mappa verbale delle unità (seconda cifra)

| Cifra | Forma verbale |
|-------|--------------|
| 0 | zero |
| 1 | uno |
| 2 | due |
| 3 | tre |
| 4 | quattro |
| 5 | cinque |
| 6 | sei |
| 7 | sette |
| 8 | otto |
| 9 | nove |

### 3.4 Separatore

Il punto fermo (`.`) è l'unico separatore. Non si usano virgole, trattini
o spazi aggiuntivi come separatore tra le due frasi cifra.

---

## 4. Dove vive la logica

### 4.1 `bingo_game/ui/locales/it.py`

Vengono aggiunte due strutture:

1. **Dizionario (o mapping) verbale delle cifre**
   Una costante immutabile che mappa l'intero 0–9 alla sua forma verbale
   italiana. Viene definita nel modulo `it.py` come dato del catalogo.
   Chiave suggerita: `CIFRE_VERBALI` (dizionario `int → str`).

2. **Template stringa spelling**
   Una chiave nel catalogo che descrive il formato dell'annuncio spelling.
   Forma: due placeholder `{decina}` e `{unita}` separati da punto fermo.
   Chiave suggerita: `LOOP_SPELLING_NUMERO_ESTRATTO`.

### 4.2 `bingo_game/ui/finestra_gioco.py`

Viene aggiunta una funzione pura (o closure) `_spelling_numero(n: int) -> str`
che:
1. Calcola la decina come `n // 10`
2. Calcola l'unità come `n % 10`
3. Legge i valori verbali dal dizionario `CIFRE_VERBALI` di `locales/it.py`
4. Restituisce la stringa formattata nel template `LOOP_SPELLING_NUMERO_ESTRATTO`

Nei due punti di chiamata a `annuncia_numero_estratto`, viene aggiunta
subito dopo la riga esistente una chiamata a `mostra_messaggio_sistema`
con la stringa prodotta da `_spelling_numero(numero)`.

Il renderer non viene toccato. `mostra_messaggio_sistema` è già disponibile
nel renderer come metodo pubblico e vocalizzia direttamente tramite `_ao2_vocalizza`.

---

## 5. Casi limite

| Caso | Numero | Decina | Unità verbale | Output spelling |
|------|--------|--------|---------------|-----------------|
| Minimo del range | 10 | 1 → "uno" | 0 → "zero" | "Uno. Zero." |
| Multiplo di 10 — bassa decina | 20 | 2 → "due" | 0 → "zero" | "Due. Zero." |
| Multiplo di 10 — alta decina | 80 | 8 → "otto" | 0 → "zero" | "Otto. Zero." |
| Massimo della tombola | 90 | 9 → "nove" | 0 → "zero" | "Nove. Zero." |
| Cifre identiche | 11 | 1 → "uno" | 1 → "uno" | "Uno. Uno." |
| Cifre identiche — alta | 55 | 5 → "cinque" | 5 → "cinque" | "Cinque. Cinque." |
| Massimo non multiplo | 89 | 8 → "otto" | 9 → "nove" | "Otto. Nove." |

---

## 6. Cosa NON cambia

- `bingo_game/ui/renderers/renderer_wx.py` — nessuna modifica
- `bingo_game/ui/renderers/base_renderer.py` — nessuna modifica
- La firma di `annuncia_numero_estratto` — nessuna modifica
- Il sistema eventi (`bingo_game/events/`) — nessuna modifica
- La logica di gioco (`bingo_game/comandi_partita.py`, `bingo_game/partita.py`) — nessuna modifica
- I modelli domain (`bingo_game/tabellone.py`, `bingo_game/cartella.py`) — nessuna modifica
- I test esistenti — nessuna modifica
- L'interfaccia utente visiva — nessuna modifica

---

## 7. Criteri di accettazione

I seguenti criteri sono verificabili manualmente con NVDA attivo:

**CA-1 — Spelling dopo annuncio principale**
Dopo ogni estrazione di un numero a due cifre, NVDA legge la parola intera
del numero (primo annuncio), poi si ferma, poi legge le due cifre separate
da pausa (secondo annuncio). Verificare su almeno 3 estrazioni consecutive.

**CA-2 — Multiplo di 10: seconda cifra è "zero"**
Estrarre un numero multiplo di 10 (es. 20, 50, 70). NVDA deve annunciare
la seconda cifra come "zero", non come assenza di cifra.
Esempio atteso per 70: "Sette. Zero."

**CA-3 — Formato senza artefatti**
La stringa dello spelling non deve contenere trattini, virgole, "e", o altre
connettive. Solo le due parole cifra seguite da punto fermo.
Esempio sbagliato: "Sei e Uno." — Esempio corretto: "Sei. Uno."

**CA-4 — Nessuna regressione sul flusso esistente**
Il primo annuncio (prodotto dal renderer) continua a funzionare invariato.
La griglia visiva si aggiorna normalmente. I pulsanti mantengono il loro stato.
Nessun errore Python nei log (`logs/stderr_capture.txt`).
