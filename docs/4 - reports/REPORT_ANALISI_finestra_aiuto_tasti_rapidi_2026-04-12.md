# REPORT — Analisi di fattibilita: Finestra di aiuto tasti rapidi

**Data**: 2026-04-12
**Autore**: Agent-Analyze
**Stato**: DRAFT — solo analisi, nessuna modifica al codice
**Obiettivo**: Valutare la fattibilita di una finestra di aiuto che
mostri l'elenco completo dei tasti rapidi, accessibile con NVDA,
apribile da qualsiasi punto della finestra di gioco.

---

## Sommario esecutivo

La funzionalita e fattibile e a basso rischio. Il tasto di apertura
consigliato e **Ctrl+H** perche completamente libero in tutti i
contesti. La finestra puo essere implementata come `wx.Dialog` modale
con contenuto statico, navigabile con Tab e frecce, chiudibile con
Escape. Non richiede modifiche al dominio ne al controller.

**Fattibilita**: ALTA — nessuna ristrutturazione architetturale necessaria.
**Rischio**: BASSO — la finestra e un componente isolato, puramente di
presentazione, senza interazione con timer, stati di gioco o logica di
dominio.
**Complessita stimata**: BASSA — componente UI statico con contenuto fisso.

---

## 1. Inventario completo dei tasti rapidi

Inventario verificato direttamente dal codice sorgente di
`finestra_gioco.py` (classi PannelloGriglia e FinestraGioco) e
`finestra_principale.py`.

### 1.1 Navigazione nella cartella

- **Freccia su** — riga precedente
- **Freccia giu** — riga successiva
- **Freccia sinistra** — colonna a sinistra
- **Freccia destra** — colonna a destra
- **Alt+Freccia su** — navigazione avanzata riga precedente (lettura completa)
- **Alt+Freccia giu** — navigazione avanzata riga successiva (lettura completa)
- **Alt+Freccia sinistra** — navigazione avanzata colonna a sinistra
- **Alt+Freccia destra** — navigazione avanzata colonna a destra
- **1..9** — vai direttamente alla colonna indicata
- **Alt+1..3** — vai direttamente alla riga indicata
- **Ctrl+1..6** — salta alla cartella indicata
- **Tab** — passa al controllo successivo della finestra
- **Shift+Tab** — passa al controllo precedente della finestra
- **Escape** — esci dalla griglia (focus al pulsante principale)

### 1.2 Azioni di gioco

- **Spazio** — segna il numero attualmente in focus
- **Ctrl+Enter** — passa turno (equivale al pulsante principale)
- **F1** — dichiara ambo (solo con focus sulla griglia)
- **F2** — dichiara terno (solo con focus sulla griglia)
- **F3** — dichiara quaterna (solo con focus sulla griglia)
- **F4** — dichiara cinquina (solo con focus sulla griglia)
- **F5** — dichiara tombola (solo con focus sulla griglia)
- **Ctrl+F** — apri ricerca numero nelle cartelle
- **Ctrl+P** — metti in pausa / riprendi il gioco

### 1.3 Informazioni e consultazione

- **R** — riepilogo rapido della cartella corrente (solo con focus sulla griglia)
- **A** — lettura avanzata della posizione corrente (solo con focus sulla griglia)
- **S** — stato focus corrente (solo con focus sulla griglia)
- **V** — visualizzazione semplice della cartella (solo con focus sulla griglia)
- **Shift+V** — visualizzazione avanzata della cartella (solo con focus sulla griglia)
- **Shift+Ctrl+V** — visualizzazione avanzata di tutte le cartelle (solo con focus sulla griglia)
- **F6** — ripeti ultimo annuncio vocale (solo con focus sulla griglia)
- **Ctrl+T** — ultimo numero estratto
- **Ctrl+L** — lista completa numeri estratti
- **Ctrl+U** — ultimi 5 numeri estratti
- **Ctrl+R** — riepilogo tabellone
- **Ctrl+E** — consulta cronologia annunci (log)
- **Ctrl+G** — stato premi sintetico (ultima vittoria e prossimo premio)
- **Ctrl+I** — dettaglio premi completo (lista vincitori)

### 1.4 Menu principale (finestra_principale.py)

- **Ctrl+N** — nuova partita
- **Ctrl+I** — impostazioni (placeholder)
- **Ctrl+G** — guida (placeholder)
- **Ctrl+Q** — esci

**Nota**: Ctrl+G e Ctrl+I hanno significato diverso nella finestra
principale (impostazioni/guida) rispetto alla finestra di gioco
(premi). Non c'e conflitto tecnico perche operano su frame diversi.

**Totale tasti rapidi censiti**: 35 binding attivi.

---

## 2. Fattibilita della finestra di aiuto

### 2.1 Approccio tecnico consigliato

Un `wx.Dialog` modale con:

- Un `wx.TextCtrl` multiriga in sola lettura, oppure un
  `wx.ListBox` / `wx.html2.WebView` semplice con sezioni
  separate da intestazioni
- Il contenuto e statico (non dipende dallo stato della partita)
- Si chiude con Escape (comportamento nativo dei dialog wx) o con
  un pulsante "Chiudi"
- Il dialog e modale: blocca l'interazione con la finestra sottostante,
  evitando conflitti con i tasti di gioco

### 2.2 Accessibilita NVDA

- **wx.Dialog modale**: NVDA lo riconosce come dialog e annuncia il titolo
  automaticamente
- **wx.TextCtrl read-only**: NVDA consente la navigazione con frecce su/giu
  riga per riga, ed e la soluzione piu semplice e affidabile
- **Struttura a sezioni**: separare le categorie con righe vuote e titoli
  in maiuscolo (es. "NAVIGAZIONE", "AZIONI DI GIOCO") permette a NVDA di
  leggere il contenuto in modo chiaro e prevedibile
- **Tab**: il focus deve partire gia sul TextCtrl. Un singolo Tab porta al
  pulsante Chiudi. Un ulteriore Tab torna al TextCtrl. Ciclo semplice

### 2.3 Non interferenza con i tasti esistenti

Il dialog modale cattura tutti gli eventi tastiera. Quando il dialog e
aperto, nessun binding della FinestraGioco viene attivato. Non c'e
rischio di conflitto perche:

- Il dialog e modale: `ShowModal()` blocca il frame sottostante
- `EVT_CHAR_HOOK` della FinestraGioco non viene invocato durante il
  modale
- Escape chiude il dialog (comportamento nativo `wx.Dialog`), non
  l'applicazione

---

## 3. Scelta del tasto di apertura

### 3.1 Analisi di F1

F1 e attualmente mappato in `PannelloGriglia._on_key_down` come
"dichiara ambo" (Categoria A). Questo binding e attivo **solo quando
il focus e sul pannello griglia**. A livello frame (`_on_char_hook`),
F1 non e intercettato.

**Problema**: quando il giocatore e sulla griglia (situazione piu
frequente durante il gioco), F1 dichiarerebbe ambo invece di aprire
l'aiuto. Per un utente non vedente, premere accidentalmente F1
durante la navigazione potrebbe provocare un reclamo non voluto.

**Verdetto**: F1 non e utilizzabile in modo sicuro come tasto di aiuto.

### 3.2 Proposta: Ctrl+H

- Non e usato in nessun punto del codebase (verificato con ricerca
  globale su tutti i file UI)
- Non ha binding NVDA predefiniti noti in conflitto
- E uno standard de facto per "Help" in molte applicazioni
- Funziona in qualsiasi contesto: griglia, pulsante, log, dialog
- Semanticamente intuitivo (H = Help = aiuto)

**Verdetto**: **Ctrl+H e la scelta raccomandata**.

### 3.3 Alternative considerate

- **F7**: libero, ma non e intuitivo per "aiuto" e rompe la sequenza
  logica F1-F6 (premi + ripeti annuncio)
- **Ctrl+?** (Ctrl+Shift+/): poco pratico da digitare e poco standard
  su layout tastiera italiana
- **F12**: libero, ma lontano da F1-F6 e meno memorizzabile

---

## 4. Struttura consigliata del contenuto

Ordine cognitivo pensato per un giocatore non vedente che usa NVDA:
prima le azioni piu frequenti durante il gioco, poi le informazioni
di consultazione, infine i comandi di gestione.

```
TOMBOLA STARK — TASTI RAPIDI
=============================

NAVIGAZIONE NELLA CARTELLA
Freccia su / giu: riga precedente / successiva
Freccia sinistra / destra: colonna a sinistra / destra
1 a 9: vai alla colonna indicata
Alt + 1 a 3: vai alla riga indicata
Ctrl + 1 a 6: salta alla cartella indicata
Alt + Frecce: navigazione avanzata con lettura completa

AZIONI DI GIOCO
Spazio: segna il numero in focus
Ctrl + Invio: passa turno
F1 a F5: dichiara premio (ambo, terno, quaterna, cinquina, tombola)
Ctrl + F: cerca un numero nelle cartelle
Ctrl + P: pausa / riprendi il gioco

LETTURA E CONSULTAZIONE
R: riepilogo cartella corrente
A: lettura avanzata posizione corrente
S: stato focus
V: visualizzazione cartella semplice
Shift + V: visualizzazione cartella avanzata
Shift + Ctrl + V: visualizzazione tutte le cartelle
F6: ripeti ultimo annuncio vocale

INFORMAZIONI ESTRATTI E PREMI
Ctrl + T: ultimo numero estratto
Ctrl + L: lista numeri estratti
Ctrl + U: ultimi 5 estratti
Ctrl + R: riepilogo tabellone
Ctrl + E: cronologia annunci
Ctrl + G: stato premi sintetico
Ctrl + I: dettaglio premi completo

NAVIGAZIONE FINESTRA
Tab / Shift + Tab: controllo successivo / precedente
Escape: esci dalla griglia
Ctrl + H: apri questa guida
```

### 4.1 Motivazione dell'ordine

- **Navigazione**: e la prima cosa che il giocatore fa a ogni turno
- **Azioni**: sono le operazioni piu frequenti durante il gioco
- **Lettura**: consultazione on-demand, meno frequente ma importante
- **Informazioni**: query di stato, usate occasionalmente
- **Navigazione finestra**: comandi di base, il giocatore li impara subito

---

## 5. Impatto sul codice esistente

### 5.1 File da modificare

- **`bingo_game/ui/finestra_gioco.py`**:
  - Aggiungere intercettazione `Ctrl+H` in `_on_char_hook` (3-5 righe)
  - Aggiungere metodo `_apri_aiuto_tasti()` che crea e mostra il dialog
    (5-8 righe)

### 5.2 File da creare

- **`bingo_game/ui/finestra_aiuto_tasti.py`** (nuovo):
  - Classe `FinestraAiutoTasti(wx.Dialog)` con TextCtrl read-only
  - Contenuto statico con i tasti raggruppati per sezione
  - Stima: 80-120 righe di codice totali (incluso il testo)

### 5.3 File da aggiornare (opzionali)

- **`bingo_game/ui/locales/it.py`**: se si vuole esternalizzare il testo
  dei tasti in un catalogo localizzato (non obbligatorio nella prima
  implementazione)
- **`docs/API.md`**: aggiungere voce per la nuova classe
- **`docs/ARCHITECTURE.md`**: nessuna modifica necessaria (non cambia
  l'architettura)
- **`CHANGELOG.md`**: aggiungere voce sotto [Unreleased]

### 5.4 Stima righe di codice

- Codice nuovo: circa 90-130 righe
- Codice modificato: circa 10-15 righe in `finestra_gioco.py`
- Totale: circa 100-145 righe

### 5.5 Rischi di regressione

**Nessun rischio significativo identificato.**

- Il dialog modale non interagisce con timer, stati o logica di gioco
- Il binding Ctrl+H e aggiunto in `_on_char_hook` con lo stesso pattern
  degli altri binding: nessun impatto sui binding esistenti
- Il nuovo file e un componente isolato senza dipendenze dal dominio
- I test esistenti non sono impattati (nessuna modifica a metodi
  esistenti, solo aggiunta di un ramo `if` in `_on_char_hook`)

**Unica attenzione**: verificare empiricamente che Ctrl+H non sia
intercettato da NVDA in nessuna modalita (Browse Mode, Focus Mode).
Sulla base della documentazione NVDA nota, Ctrl+H non ha binding
predefiniti, ma la verifica pratica resta necessaria.

---

## 6. Raccomandazione

**La finestra di aiuto tasti rapidi e pienamente fattibile.** La
complessita e bassa, il rischio di regressione e trascurabile e
l'impatto architetturale e nullo.

### Giudizio sintetico

- **Fattibilita**: alta
- **Rischio**: basso
- **Complessita**: bassa (componente UI statico, isolato)
- **Tasto consigliato**: Ctrl+H
- **Approccio**: wx.Dialog modale con wx.TextCtrl read-only

### Passo successivo suggerito

Procedere con la creazione di un DESIGN document che definisca il
contratto della classe `FinestraAiutoTasti`, il formato del testo
e le specifiche di accessibilita. Dopodiche un PLAN con una singola
fase implementativa (stimata come un singolo commit atomico).
