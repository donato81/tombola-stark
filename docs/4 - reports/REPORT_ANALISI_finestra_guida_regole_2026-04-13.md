# REPORT — Analisi di fattibilita: Finestra guida regole del gioco

**Data**: 2026-04-13
**Autore**: Agent-Analyze
**Stato**: DRAFT — solo analisi, nessuna modifica al codice
**Obiettivo**: Valutare la fattibilita di una finestra di guida navigabile
a pagine che spieghi le regole del gioco della Tombola, accessibile con
NVDA, estensibile con nuovi capitoli senza modifiche al codice UI.

---

## Sommario esecutivo

La funzionalita e fattibile e a rischio basso. Il progetto dispone gia
di un pattern collaudato per dialog modali accessibili (`FinestraAiutoTastiRapidi`,
`DialogoRicercaNumero`) e di un catalogo locale strutturato (`locales/it.py`).
La finestra guida e un componente di presentazione puro, senza interazione
con timer, stati di gioco o logica di dominio.

**Fattibilita**: ALTA — nessuna ristrutturazione architetturale necessaria.
**Rischio**: BASSO — componente isolato, puramente di presentazione.
**Complessita stimata**: MEDIA-BASSA — navigazione a pagine con annuncio
NVDA al cambio pagina aggiunge logica rispetto a un TextCtrl statico,
ma resta contenuta.

---

## 1. Inventario del codice esistente rilevante

### 1.1 Pattern apertura dialog in `finestra_gioco.py`

La `FinestraGioco` apre dialog modali con un pattern costante, visibile
nel metodo `_on_char_hook` (linee 876-883):

```python
if ctrl and key == ord("H"):
    dlg = FinestraAiutoTastiRapidi(self)
    dlg.ShowModal()
    dlg.Destroy()
    self._pannello_griglia.SetFocus()
    return
```

Il pattern e: (1) creazione dialog con `parent=self`, (2) `ShowModal()`,
(3) `Destroy()`, (4) ripristino focus su `_pannello_griglia`. Questo
stesso pattern andra replicato per la finestra guida.

Un secondo pattern analogo e presente per il dialog di ricerca (`Ctrl+F`),
che crea un `DialogoRicercaNumero` modale con renderer e comandi come
dipendenze. La finestra guida non necessita di queste dipendenze perche
e puramente informativa.

### 1.2 Struttura del dizionario `locales/it.py`

Il file `locales/it.py` contiene diversi dizionari immutabili
(`MappingProxyType`) con chiavi stringa costanti e valori tupla di
stringhe. Convenzioni osservate:

- **Chiavi**: stringhe maiuscole con prefisso di categoria e underscore
  (es. `UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_1`)
- **Valori**: `tuple[str, ...]` — ogni elemento e una riga del messaggio
- **Placeholder**: formato `{nome}` (standard str.format)
- **Raggruppamento**: i dizionari sono raggruppati per scopo
  (`MESSAGGI_ERRORI`, `MESSAGGI_EVENTI`, `MESSAGGI_OUTPUT_UI_UMANI`,
  `MESSAGGI_SISTEMA`, `MESSAGGI_CONFIGURAZIONE`, `MESSAGGI_CONTROLLER`)
- **Import**: ogni dizionario importa i propri codici da moduli dedicati
  in `bingo_game/events/`
- **Immutabilita**: tutti i dizionari sono wrappati in `MappingProxyType`

Per `it_guida.py` si replicano le stesse convenzioni: dizionario
immutabile con chiavi stringa maiuscole prefissate `GUIDA_`.

### 1.3 Dialog modali gia esistenti

- **FinestraAiutoTastiRapidi** (`finestra_aiuto_tasti_rapidi.py`, 119 righe):
  `wx.Dialog` modale con `wx.TextCtrl` read-only. Contiene testo statico
  inline. Focus iniziale sul TextCtrl, chiusura con Escape o pulsante Chiudi.
  E il riferimento piu diretto per la finestra guida.

- **DialogoRicercaNumero** (`dialogo_ricerca.py`, ~170 righe):
  `wx.Dialog` modale con input, ricerca e risultati. Piu complesso perche
  interattivo, ma dimostra il pattern `EVT_CHAR_HOOK` per intercettare
  Escape/Enter nel contesto modale.

- **FinestraConfigurazione** (`finestra_configurazione.py`):
  E un `wx.Frame`, non un `wx.Dialog`. Non e un riferimento diretto
  per il pattern, ma conferma il pattern di label esplicite, focus
  iniziale e logging delle azioni UI.

### 1.4 Menu principale — voce "Guida" gia presente

La `FinestraPrincipale` ha gia un pulsante "Guida (Ctrl+G)" con handler
`_on_guida()` che attualmente mostra un placeholder:
```python
def _on_guida(self, event: wx.Event) -> None:
    self._renderer.mostra_messaggio_sistema("Funzione non ancora disponibile.")
```
Questo handler e il punto di aggancio naturale per aprire la finestra
guida dal menu principale. L'acceleratore `Ctrl+G` e gia configurato.

---

## 2. Struttura proposta per `it_guida.py`

### 2.1 File: `bingo_game/ui/locales/it_guida.py`

```python
from __future__ import annotations

from collections.abc import Sequence
from types import MappingProxyType

# Ogni capitolo e una coppia (titolo, testo).
# Il testo e una tupla di righe: il renderer fa "\n".join(righe).
# Per aggiungere un capitolo: inserire una nuova entry in GUIDA_CAPITOLI
# nello stesso formato. Il codice della finestra itera automaticamente
# sull'elenco senza necessita di modifiche.

GUIDA_CAPITOLI: Sequence[tuple[str, tuple[str, ...]]] = (
    (
        "Introduzione alla Tombola",
        (
            "La Tombola e un gioco di societa...",
            "...",
        ),
    ),
    (
        "La cartella",
        (
            "Ogni giocatore possiede da 1 a 6 cartelle...",
            "...",
        ),
    ),
    (
        "I premi in ordine",
        (
            "Nella Tombola i premi vanno dichiarati in ordine...",
            "Ambo: 2 numeri sulla stessa riga...",
            "...",
        ),
    ),
    (
        "Come si svolge un turno",
        (
            "A ogni turno viene estratto un numero dal tabellone...",
            "...",
        ),
    ),
    (
        "I bot avversari",
        (
            "I bot sono giocatori automatici gestiti dal computer...",
            "...",
        ),
    ),
)

# Etichette UI della finestra guida (pulsanti, annunci NVDA).
GUIDA_UI: MappingProxyType[str, str] = MappingProxyType({
    "TITOLO_FINESTRA": "Guida alle regole del gioco",
    "BTN_PRECEDENTE": "Precedente",
    "BTN_SUCCESSIVO": "Successivo",
    "BTN_CHIUDI": "Chiudi",
    "ANNUNCIO_PAGINA": "Pagina {corrente} di {totale}. {titolo}.",
})
```

### 2.2 Formato delle chiavi

- `GUIDA_CAPITOLI`: sequenza ordinata di tuple `(titolo, righe_testo)`.
  L'ordine nella sequenza determina l'ordine delle pagine.
- `GUIDA_UI`: dizionario con etichette dell'interfaccia della finestra.
  Chiavi prefissate per chiarezza.

### 2.3 Come aggiungere un capitolo in futuro

Per aggiungere un capitolo (es. "Modalita multiplayer"):

1. Aprire `bingo_game/ui/locales/it_guida.py`
2. Aggiungere una nuova tupla `(titolo, testo)` in `GUIDA_CAPITOLI`
   nella posizione desiderata
3. Non serve toccare il codice della finestra guida

La finestra legge `len(GUIDA_CAPITOLI)` per calcolare il totale pagine
e itera sull'indice corrente. L'aggiunta di una voce alla sequenza
e sufficiente.

---

## 3. Struttura della finestra a pagine

### 3.1 Layout proposto

```
+---------------------------------------------+
|  Guida alle regole del gioco        [X]     |  <- titolo finestra
+---------------------------------------------+
|  [StaticText: titolo capitolo corrente]      |  <- leggibile da NVDA
|                                              |
|  [TextCtrl read-only: testo capitolo]        |  <- navigabile con frecce
|                                              |
|                                              |
+---------------------------------------------+
|  [Precedente]  Pagina 1 di 5  [Successivo]  |
|                   [Chiudi]                   |
+---------------------------------------------+
```

### 3.2 Componenti wx

- **`wx.Dialog`** modale con `style=wx.DEFAULT_DIALOG_STYLE`
- **`wx.StaticText`** per il titolo del capitolo corrente — aggiornato
  a ogni cambio pagina
- **`wx.TextCtrl`** con `wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL`
  per il testo del capitolo — aggiornato a ogni cambio pagina
- **`wx.Button` "Precedente"** — disabilitato sulla prima pagina
- **`wx.Button` "Successivo"** — disabilitato sull'ultima pagina
- **`wx.StaticText`** indicatore pagina "Pagina N di M" — aggiornato
  a ogni cambio pagina
- **`wx.Button` "Chiudi"** — chiude il dialog con `EndModal`

### 3.3 Comportamento navigazione

- **Cambio pagina**: i pulsanti Precedente/Successivo aggiornano l'indice
  corrente, ridisegnano titolo e testo, e disabilitano il pulsante
  appropriato ai limiti
- **Annuncio NVDA al cambio pagina**: dopo l'aggiornamento del testo,
  il focus viene spostato sul titolo del capitolo (StaticText). NVDA
  legge automaticamente il contenuto del controllo che riceve il focus.
  Alternativa piu robusta: usare `wx.Accessible` o
  `wx.CallAfter(ctrl.SetFocus)` per forzare la rilettura
- **Focus iniziale**: sul TextCtrl del testo, come nella finestra
  tasti rapidi. NVDA annuncia il titolo del dialog all'apertura
  (`SetTitle` del dialog), poi l'utente legge il testo con le frecce.
  Alternativa: focus sul titolo del capitolo per avere subito
  l'annuncio "Introduzione alla Tombola"
- **Chiusura**: Escape o pulsante Chiudi. Focus ripristinato sulla griglia

### 3.4 Binding tastiera nel dialog

- **Escape**: chiude il dialog (comportamento nativo `wx.Dialog`)
- **Alt+Freccia sinistra** o **Alt+P**: pagina precedente (opzionale,
  per navigazione rapida senza Tab fino al pulsante)
- **Alt+Freccia destra** o **Alt+S**: pagina successiva (opzionale)
- **Tab/Shift+Tab**: ciclo tra TextCtrl, pulsanti, chiudi

Nota: l'uso di Alt+Frecce nel dialog non genera conflitti perche il
dialog e modale e i binding della FinestraGioco non sono attivi.

### 3.5 Punto di apertura

Due punti di apertura coesistenti:

1. **Da `FinestraPrincipale`**: il pulsante "Guida (Ctrl+G)" gia
   presente. L'handler `_on_guida()` va modificato per aprire la
   finestra guida invece di mostrare il placeholder.

2. **Da `FinestraGioco`**: serve un nuovo binding. Due opzioni analizzate:

   - **Ctrl+H dedicato alla guida regole**: richiederebbe spostare
     la finestra tasti rapidi su un altro tasto (rottura di abitudine
     per utenti che gia la usano). Non raccomandato.
   - **Nuovo tasto (es. Ctrl+G)**: nella FinestraGioco, Ctrl+G e gia
     mappato a "stato premi sintetico". Conflitto.
   - **F7**: libero in tutti i contesti, ma poco intuitivo.
   - **Ctrl+Shift+H**: libero, semanticamente vicino a Ctrl+H (Help).
     Mantiene Ctrl+H per i tasti rapidi.

   **Raccomandazione**: usare **Ctrl+Shift+H** nella FinestraGioco
   per aprire la guida regole. Ctrl+H resta per i tasti rapidi.
   Nella FinestraPrincipale, la guida si apre da Ctrl+G (gia configurato).

---

## 4. Accessibilita NVDA

### 4.1 Apertura del dialog

Quando il dialog si apre con `ShowModal()`:
- NVDA annuncia automaticamente il titolo della finestra
  ("Guida alle regole del gioco") perche e un `wx.Dialog` modale
- Subito dopo, NVDA legge il controllo che ha il focus iniziale

**Sequenza annunciata**: "Guida alle regole del gioco, dialogo" →
contenuto del controllo in focus (titolo capitolo o testo).

### 4.2 Navigazione tra capitoli con la tastiera

- **Tab**: dal TextCtrl al pulsante Precedente → Successivo → Chiudi → TextCtrl
- **Shift+Tab**: ciclo inverso
- **Precedente / Successivo**: attivabili con Spazio o Invio quando in focus
- **Alt+Freccia sinistra/destra** (opzionale): scorciatoia pagina
  senza lasciare il TextCtrl

L'utente non vedente naviga con Tab fino al pulsante Successivo, preme
Spazio, la pagina cambia. Il focus torna automaticamente sul titolo
del nuovo capitolo.

### 4.3 Lettura del testo del capitolo

Il `wx.TextCtrl` read-only e completamente navigabile da NVDA:
- **Freccia giu/su**: riga per riga
- **Ctrl+Home / Ctrl+End**: inizio / fine testo
- **Freccia sinistra/destra**: carattere per carattere
- **Ctrl+Freccia sinistra/destra**: parola per parola

Questo e lo stesso comportamento gia verificato nella finestra
tasti rapidi (`FinestraAiutoTastiRapidi`), dove il TextCtrl read-only
funziona perfettamente con NVDA.

### 4.4 Annuncio al cambio di pagina

Quando l'utente preme Precedente o Successivo:
1. Il testo del TextCtrl viene aggiornato con il nuovo capitolo
2. Il titolo del capitolo (StaticText) viene aggiornato
3. Il focus viene spostato sul titolo del capitolo con `wx.CallAfter`
4. NVDA legge il nuovo titolo (es. "La cartella")
5. L'utente puo poi premere Tab per andare al TextCtrl e leggere
   il contenuto con le frecce

**Implementazione annuncio**: la soluzione piu affidabile e spostare
il focus su un controllo aggiornato. `wx.CallAfter(titolo.SetFocus)`
garantisce che NVDA rilevi il cambio di contenuto e lo annunci.
In alternativa, si puo usare una stringa combinata
"Pagina 2 di 5. La cartella." come `AccessibleName` del titolo.

### 4.5 Chiusura del dialog

- **Escape**: chiude il dialog (comportamento nativo)
- **Pulsante Chiudi**: `EndModal(wx.ID_CANCEL)`
- Dopo la chiusura, `FinestraGioco` ripristina il focus su
  `_pannello_griglia` (stesso pattern della finestra tasti rapidi)
- NVDA annuncia il ritorno al contesto precedente ("Griglia cartella")

---

## 5. Integrazione con la finestra tasti rapidi

### 5.1 Opzione A — Due finestre separate (raccomandata)

Le due finestre hanno scopi diversi:
- **Tasti rapidi**: riferimento tecnico rapido, consultato durante il gioco
  per ricordare un binding specifico. Contenuto statico, una sola pagina.
- **Guida regole**: spiegazione concettuale del gioco, consultata
  prima di giocare o per capire le meccaniche. Contenuto multi-pagina,
  narrativo.

Mantenerle separate e la scelta corretta perche:
- L'utente non vedente ha un modello mentale chiaro: Ctrl+H = "che
  tasto premo?" vs Ctrl+Shift+H (o Ctrl+G dal menu) = "come si gioca?"
- La finestra tasti rapidi resta leggera e veloce da aprire/chiudere
- La finestra guida puo crescere con capitoli senza impattare
  il riferimento tasti rapidi

### 5.2 Opzione B — Finestra unificata con tab/pagine

Si potrebbe creare un'unica finestra con due sezioni (tasti rapidi
come prima pagina, poi i capitoli della guida). Tuttavia:
- Aumenta la complessita senza beneficio reale
- Rompe il pattern gia esistente e collaudato della finestra tasti rapidi
- L'utente che vuole solo ricordare un binding deve navigare oltre
  la struttura a pagine

**Raccomandazione**: mantenere le due finestre separate.

La finestra guida puo contenere un capitolo finale "Tasti rapidi"
che e un duplicato del contenuto della finestra tasti rapidi. Questo
offre un punto di accesso alternativo senza eliminare il riferimento
veloce esistente. E opzionale e valutabile in futuro.

---

## 6. Impatto sul codice esistente

### 6.1 File nuovi da creare

| File | Scopo | Stima righe |
|---|---|---|
| `bingo_game/ui/locales/it_guida.py` | Dizionario capitoli guida | 120-180 |
| `bingo_game/ui/finestra_guida_regole.py` | Dialog modale a pagine | 130-180 |

### 6.2 File da modificare

| File | Modifica | Stima righe |
|---|---|---|
| `bingo_game/ui/finestra_gioco.py` | Aggiungere binding Ctrl+Shift+H in `_on_char_hook` + import | 8-12 |
| `bingo_game/ui/finestra_principale.py` | Aggiornare `_on_guida()` per aprire il dialog + import | 6-10 |

### 6.3 File di documentazione da aggiornare

- `docs/API.md` — aggiungere voce per la nuova classe
- `CHANGELOG.md` — aggiungere voce sotto [Unreleased]
- `bingo_game/ui/finestra_aiuto_tasti_rapidi.py` — aggiungere riga
  "Ctrl+Shift+H — apri guida alle regole del gioco" nel contenuto
  testuale (opzionale, ma consigliato per coerenza)

### 6.4 Stima totale

- **Codice nuovo**: 250-360 righe (dizionario + dialog)
- **Codice modificato**: 14-22 righe in file esistenti
- **Totale**: circa 270-380 righe

### 6.5 Rischi di regressione

**Nessun rischio significativo identificato.**

- Il dialog modale e un componente isolato senza dipendenze dal dominio
- Il binding Ctrl+Shift+H nel `_on_char_hook` segue lo stesso pattern
  degli altri binding: nessun impatto sui binding esistenti
- Ctrl+Shift+H e completamente libero in tutti i contesti del progetto
  (verificato con grep globale)
- La modifica a `_on_guida()` nella finestra principale sostituisce
  un placeholder con un dialog, senza effetti collaterali
- Il file `it_guida.py` e un nuovo modulo isolato senza side-effect
- I test esistenti non sono impattati

**Attenzione**: verificare empiricamente che Ctrl+Shift+H non sia
intercettato da NVDA in Browse Mode. Sulla base della documentazione
NVDA nota, questa combinazione non ha binding predefiniti, ma la
verifica pratica resta necessaria.

---

## 7. Raccomandazione

**La finestra guida regole del gioco e pienamente fattibile.** Il progetto
ha gia tutti i pattern necessari (dialog modali accessibili, catalogo
locale strutturato, binding tastiera nel `_on_char_hook`). L'unica
complessita aggiuntiva rispetto alla finestra tasti rapidi e la
navigazione a pagine con annuncio NVDA al cambio pagina, che e gestibile
con `wx.CallAfter` e spostamento focus.

### Giudizio sintetico

- **Fattibilita**: alta
- **Rischio**: basso
- **Complessita**: media-bassa
- **Tasto guida nella finestra di gioco**: Ctrl+Shift+H (consigliato)
- **Tasto guida nel menu principale**: Ctrl+G (gia configurato)
- **Approccio**: wx.Dialog modale con navigazione a pagine
- **Testi**: dizionario esterno in `it_guida.py`, struttura a sequenza
- **Finestra tasti rapidi**: resta separata (raccomandata)

### Passo successivo suggerito

Procedere con la creazione di un DESIGN document che definisca:
- Il contratto della classe `FinestraGuidaRegole`
- Il layout esatto dei controlli wx e l'ordine Tab
- Le specifiche di annuncio NVDA al cambio pagina
- Il contenuto testuale completo dei capitoli per la versione alfa
- La struttura del file `it_guida.py` con i testi finali

Dopodiche, un PLAN con 2-3 fasi implementative:
1. Creazione `it_guida.py` con testi capitoli
2. Creazione `finestra_guida_regole.py` con dialog a pagine
3. Integrazione binding in `finestra_gioco.py` e `finestra_principale.py`
