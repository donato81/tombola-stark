# Report — Proposta Interfaccia Grafica Finestra di Gioco

**Autore analisi:** Agent-Analyze
**Data:** 11 aprile 2026
**Revisione:** 11 aprile 2026 (v2 — pulsanti navigazione, selezione diretta, premi)
**Oggetto:** Proposta completa per la veste grafica della finestra di gioco
**Versione motore:** attuale (post ciclo turno V2)
**Vincolo primario:** Zero regressioni sull'esperienza screen reader NVDA

---

## 1. Stato attuale dell'interfaccia

### 1.1 Cosa esiste oggi

L'applicazione ha tre finestre wx.Frame funzionanti:

- **FinestraPrincipale** (400x300): 4 pulsanti verticali senza stile, sfondo grigio di default wx.
- **FinestraConfigurazione** (500x430): form con label + controlli + pulsante conferma, nessuno stile visivo.
- **FinestraGioco** (700x500): pulsante principale, pulsante pausa, PannelloGriglia (un singolo wx.StaticText), area log (wx.TextCtrl read-only).

### 1.2 Carenze grafiche attuali

- Il PannelloGriglia non mostra alcuna rappresentazione visiva della cartella: e solo un'etichetta testuale.
- Il tabellone dei 90 numeri non e mai visualizzato graficamente.
- Non ci sono colori, font personalizzati, icone o separatori visivi.
- Nessuna indicazione visiva dello stato dei numeri (estratto/segnato/vuoto).
- Nessuna indicazione visiva dei premi ottenuti.
- Il layout e una pila verticale di BoxSizer senza gerarchia visiva.

### 1.3 Cosa funziona perfettamente e non va toccato

- Tutto il sistema di binding tastiera (Categorie A, B, C) in finestra_gioco.py.
- Il ciclo turno trifasico V2 (estrazione -> reclami -> pausa).
- Il dispatcher WxRenderer con 27 handler e sincronizzazione widget/voce.
- La vocalizzazione AO2 tramite Vocalizzatore.
- Il log annunci consultabile con Ctrl+E.
- Focus preservation, Escape per uscire dalla griglia, Tab per rientrare.

---

## 2. Principi guida per la veste grafica

### 2.1 Regola zero

Ogni modifica grafica deve essere **additiva**: aggiunge informazione visiva senza rimuovere o alterare alcun binding, flusso vocale o comportamento di navigazione esistente.

### 2.2 Dual-channel

La UI funziona su due canali paralleli e indipendenti:
- **Canale visivo**: colori, griglie, indicatori grafici per utenti vedenti.
- **Canale vocale**: AO2/NVDA per utenti non vedenti.

I due canali non si condizionano mai: il renderer aggiorna prima i widget visivi poi vocalizza lo stesso testo.

### 2.3 Compatibilita wx

Tutti i widget proposti sono componenti standard wxPython o custom panel con wx.BufferedPaintDC. Nessuna dipendenza esterna da librerie grafiche extra.

---

## 3. Proposta layout — Finestra di gioco

### 3.1 Schema strutturale complessivo

```
+==========================================================================+
|  BARRA TITOLO: "Tombola Stark — In gioco"                                |
+==========================================================================+
|  HEADER BAR (alto, fisso)                                                |
|  [Turno: 12]  [Ultimo estratto: 45]  [Premi: Ambo, Terno]               |
+--------------------------------------------------------------------------+
|                  |                                                       |
|  PANNELLO        |  AREA CARTELLA CON NAVIGAZIONE                        |
|  TABELLONE       |                                                       |
|  (griglia 9x10   |       "Cartella 1 di 3"                               |
|   numeri 1-90)   |                                                       |
|                  |  [<]  +---+---+---+---+---+---+---+---+---+  [>]      |
|  [ 1][ 2][ 3].. |       |   | 12|   | 34|   | 56|   | 78|   |           |
|  [10][11][12]..  |       | 3 |   | 25|   | 47|   | 68|   | 85|           |
|  ...             |       |   | 15|   | 38|   | 59|   | 72|   |           |
|  [80][81]...[90] |       +---+---+---+---+---+---+---+---+---+           |
|                  |                                                       |
|                  |  SELEZIONE DIRETTA CARTELLA                           |
|                  |  [1] [2] [3] [4] [5] [6]                              |
|                  |                                                       |
|                  |  PULSANTI AZIONE                                      |
|                  |  [Inizia partita]  [Metti in pausa]  [Torna al menu]  |
|                  |                                                       |
|                  |  PULSANTI PREMI                                       |
|                  |  [Ambo]  [Terno]  [Quaterna]  [Cinquina]  [Tombola]   |
+------------------+-------------------------------------------------------+
|  LOG ANNUNCI (basso, altezza fissa, scrollabile)                         |
|  Turno 1. Numero estratto: 45.                                          |
|  Nessun premio questo turno.                                            |
|  Turno 2. Numero estratto: 12.                                          |
|  Ambo per Bot Lucia.                                                    |
+==========================================================================+
```

### 3.2 Dettaglio aree

#### Area 1 — Header Bar (alto)

- **Posizione**: striscia orizzontale fissa in cima alla finestra.
- **Contenuto**: tre indicatori testuali allineati orizzontalmente.
  - "Turno: N" (aggiornato ad ogni estrazione).
  - "Ultimo estratto: N" (evidenziato con colore accent).
  - "Premi assegnati: Ambo, Terno..." (lista compatta dei premi gia assegnati).
- **Stile**: sfondo scuro (#2C3E50), testo bianco (#ECEFF1), font bold 12pt.
- **Accessibilita**: le stesse informazioni sono gia vocalizzate; la barra e un visual-only plus.
- **Widget wx**: wx.Panel con 3 wx.StaticText.

#### Area 2 — Pannello Tabellone (sinistra)

- **Posizione**: colonna sinistra, larghezza fissa ~240px.
- **Contenuto**: griglia 10 righe x 9 colonne che mostra tutti i numeri da 1 a 90.
  - Riga 1: numeri 1-9
  - Riga 2: numeri 10-19
  - ...
  - Riga 10: numeri 81-90 (la colonna 10 contiene solo il numero 90)
- **Colori cella**:
  - Numero disponibile (non estratto): sfondo chiaro (#F5F5F5), testo grigio (#9E9E9E).
  - Numero estratto: sfondo accent rosso (#E53935), testo bianco (#FFFFFF), bold.
  - Numero estratto E presente in una cartella dell'umano: sfondo dorato (#FFB300), testo nero (#212121).
- **Aggiornamento**: ad ogni estrazione, la cella corrispondente cambia colore.
- **Widget wx**: custom wx.Panel con wx.BufferedPaintDC (disegno diretto per performance).
- **Accessibilita**: il tabellone visivo non ha focus keyboard e non riceve eventi tastiera. Le informazioni del tabellone sono consultabili via Ctrl+R (riepilogo vocale) e Ctrl+L (lista estratti vocale).

#### Area 3 — Pannello Cartella con navigazione (centro-destra)

- **Posizione**: lato destro del pannello principale, occupa lo spazio rimanente.
- **Struttura verticale**: titolo, freccine + griglia, selezione diretta, pulsanti azione, pulsanti premi.

##### 3a — Titolo cartella

- **Contenuto**: "Cartella N di T" (aggiornato con le frecce di navigazione, Ctrl+frecce, Ctrl+1..6 e pulsanti selezione diretta).
- **Widget wx**: wx.StaticText con font bold 13pt, centrato.

##### 3b — Frecce navigazione cartella + griglia

- **Layout**: orizzontale — pulsante freccia sinistra [<], griglia 3x9 al centro, pulsante freccia destra [>].
- **Pulsante [<] (Cartella precedente)**:
  - wx.Button quadrato (~40x40px) con label "<" o icona freccia sinistra.
  - Click: chiama `ComandiGiocatoreUmano.cartella_precedente()` e aggiorna la griglia visiva.
  - Disabilitato se l'utente e gia sulla prima cartella.
  - Equivalente tastiera: Ctrl+freccia sinistra.
- **Pulsante [>] (Cartella successiva)**:
  - wx.Button quadrato (~40x40px) con label ">" o icona freccia destra.
  - Click: chiama `ComandiGiocatoreUmano.cartella_successiva()` e aggiorna la griglia visiva.
  - Disabilitato se l'utente e gia sull'ultima cartella.
  - Equivalente tastiera: Ctrl+freccia destra.
- **Griglia 3x9**: PannelloCartellaVisiva (custom draw, invariato dal report precedente).
- **Colori cella** (invariati):
  - Cella vuota (None nella matrice): sfondo grigio neutro (#E0E0E0), nessun testo.
  - Numero presente, non segnato, non estratto: sfondo bianco (#FFFFFF), testo nero (#212121), font 14pt.
  - Numero presente, estratto ma non ancora segnato: sfondo giallo lampeggiante (#FFF176) per 2 secondi dopo l'estrazione, poi sfondo giallo fisso (#FFF9C4), testo nero.
  - Numero segnato: sfondo verde (#43A047), testo bianco (#FFFFFF), bold.
- **Animazione post-estrazione**: invariata.
- **Indicatore riga/colonna in focus**: invariato.
- **Widget griglia wx**: custom wx.Panel con wx.BufferedPaintDC.
- **Accessibilita**: il PannelloGriglia invisibile resta il ricevitore dei binding Categoria A. I pulsanti freccia sono accessibili via Tab per utenti vedenti ma non interferiscono con la navigazione NVDA, che usa Ctrl+frecce.

##### 3c — Selezione diretta cartella

- **Posizione**: riga orizzontale subito sotto la griglia.
- **Contenuto**: da 1 a 6 pulsanti numerati [1] [2] [3] [4] [5] [6], uno per ogni cartella assegnata al giocatore umano.
- **Layout**: wx.BoxSizer orizzontale centrato. Solo i pulsanti corrispondenti alle cartelle effettivamente assegnate vengono mostrati (se il giocatore ha 3 cartelle, appaiono solo [1] [2] [3]).
- **Click su [N]**: chiama `ComandiGiocatoreUmano.imposta_focus_cartella(N)` e aggiorna la griglia visiva.
- **Stato visivo**: il pulsante della cartella correttamente in focus ha sfondo accent blu (#1565C0) con testo bianco; gli altri hanno sfondo neutro (#E0E0E0) con testo scuro.
- **Equivalente tastiera**: Ctrl+1..6.
- **Stile**: wx.Button quadrato (~36x36px), font bold 11pt.
- **Accessibilita**: label accessibile "Cartella N" su ogni pulsante. NVDA legge la label al focus.

#### Area 4 — Pulsanti azione (sotto la selezione cartella)

- **Posizione**: riga orizzontale sotto i pulsanti di selezione diretta.
- **Contenuto**: pulsante principale a due stati + pulsante pausa/riprendi + pulsante torna al menu.
- **Layout**: wx.BoxSizer orizzontale con spaziatura 10px.
- **Stile pulsante principale**:
  - "Inizia partita": sfondo verde (#2E7D32), testo bianco, font bold 12pt.
  - "Passa turno": sfondo blu (#1565C0), testo bianco.
  - "Ho finito — avvia verifica": sfondo arancione (#E65100), testo bianco.
  - "Pausa in corso...": sfondo grigio (#757575), testo bianco, disabilitato.
  - "Gioco in pausa": sfondo grigio (#757575), testo bianco, disabilitato.
- **Pulsante pausa/riprendi** (sempre visibile):
  - Stato "Metti in pausa": sfondo grigio scuro (#424242), testo bianco.
  - Stato "Riprendi": sfondo verde (#388E3C), testo bianco.
  - Disabilitato prima del primo turno e durante la pausa tra turni (invariato).
  - Click: chiama `_toggle_pausa()`, equivalente tastiera Ctrl+P.
- **Pulsante "Torna al menu"**: sfondo neutro, nascosto durante la partita, visibile solo a fine partita (invariato).
- **Widget wx**: wx.Button standard con SetBackgroundColour/SetForegroundColour.

#### Area 5 — Pulsanti premi (sotto i pulsanti azione)

- **Posizione**: riga orizzontale sotto i pulsanti azione, prima del log.
- **Contenuto**: 5 pulsanti per la dichiarazione dei premi, uno per ciascun tipo.
- **Layout**: wx.BoxSizer orizzontale centrato con spaziatura 8px.
- **Pulsanti**:
  - **[Ambo]**: click chiama `ComandiGiocatoreUmano.annuncia_vittoria("ambo", turno)`. Equivalente: F1.
  - **[Terno]**: click chiama `ComandiGiocatoreUmano.annuncia_vittoria("terno", turno)`. Equivalente: F2.
  - **[Quaterna]**: click chiama `ComandiGiocatoreUmano.annuncia_vittoria("quaterna", turno)`. Equivalente: F3.
  - **[Cinquina]**: click chiama `ComandiGiocatoreUmano.annuncia_vittoria("cinquina", turno)`. Equivalente: F4.
  - **[Tombola]**: click chiama `ComandiGiocatoreUmano.annuncia_vittoria("tombola", turno)`. Equivalente: F5.
- **Stile**:
  - Sfondo: accent rosso (#E53935), testo bianco, font bold 11pt.
  - Il pulsante Tombola ha sfondo dorato (#FFB300) e testo nero per distinguersi dagli altri.
- **Stato**: i 5 pulsanti sono abilitati solo durante la fase "attesa_reclami" del turno. Nelle altre fasi (attesa_estrazione, pausa_turno, in_pausa, partita terminata) sono disabilitati.
- **Premio gia vinto**: quando un tipo di premio e stato gia assegnato nella partita (es. Ambo gia vinto da un altro giocatore), il pulsante corrispondente viene disabilitato permanentemente con sfondo grigio (#BDBDBD) e label barrata o con suffisso " (assegnato)".
- **Accessibilita**: label accessibile completa su ogni pulsante (es. "Dichiara ambo" per NVDA). I tasti rapidi F1-F5 restano invariati per l'utente non vedente.

#### Area 6 — Log Annunci (basso)

- **Posizione**: striscia bassa della finestra, altezza fissa 120px, scrollabile.
- **Contenuto**: wx.TextCtrl read-only come gia implementato.
- **Stile**: sfondo scuro (#263238), testo chiaro (#B0BEC5), font monospace 10pt.
- **Etichetta**: "Cronologia annunci (Ctrl+E)" sopra il log.
- **Accessibilita**: invariato — Ctrl+E porta il focus qui, Escape per tornare alla griglia.

### 3.3 Gerarchia verticale completa (lato destro)

L'area destra della finestra di gioco e organizzata in 6 sotto-zone verticali impilate:

```
1. Titolo cartella       "Cartella 1 di 3"
2. Frecce + griglia      [<]  [griglia 3x9]  [>]
3. Selezione diretta     [1] [2] [3]
4. Pulsanti azione       [Inizia partita] [Metti in pausa] [Torna al menu]
5. Pulsanti premi        [Ambo] [Terno] [Quaterna] [Cinquina] [Tombola]
6. (il log annunci e sotto, a tutta larghezza)
```

### 3.4 Proporzioni e ridimensionamento

- Dimensione minima consigliata: 1000x700 (up da 700x500).
- Il pannello tabellone ha larghezza fissa (240px); l'area cartella + pulsanti si espande proporzionalmente.
- Le righe di pulsanti hanno altezza fissa; l'espansione verticale va alla griglia cartella.
- Il log annunci ha altezza fissa 120px in fondo a tutta larghezza.
- Layout gestito con wx.BoxSizer nidificati (gia familiare al codebase).

### 3.5 Ordine Tab per utente vedente

L'ordine di navigazione Tab nella finestra di gioco e:

1. PannelloGriglia (riceve focus iniziale, binding Categoria A)
2. Pulsante [<] cartella precedente
3. Pulsante [>] cartella successiva
4. Pulsanti selezione diretta [1]..[6]
5. Pulsante principale (Inizia partita / Passa turno)
6. Pulsante pausa/riprendi
7. Pulsante torna al menu (quando visibile)
8. Pulsanti premi [Ambo]..[Tombola]
9. Area log annunci

Escape da qualsiasi posizione riporta il focus alla griglia.

---

## 4. Proposta layout — Finestra principale (menu)

### 4.1 Schema

```
+================================================+
|  TOMBOLA STARK                                  |
|  (titolo grande, 20pt, centrato)                |
|                                                 |
|  Immagine decorativa / ASCII art opzionale      |
|                                                 |
|  [  Nuova partita  ]                            |
|  [  Impostazioni   ]                            |
|  [     Guida       ]                            |
|  [      Esci       ]                            |
|                                                 |
|  v1.x.x                 Accessibile con NVDA    |
+================================================+
```

- **Sfondo**: gradiente scuro (#1A237E -> #283593) o colore piatto navy.
- **Titolo**: "TOMBOLA STARK" in font bold 20pt, colore dorato (#FFD54F).
- **Pulsanti**: sfondo accent (#E53935), testo bianco, bordi arrotondati, spaziatura 15px.
- **Footer**: versione e nota accessibilita in font 9pt grigio chiaro.

---

## 5. Proposta layout — Finestra configurazione

### 5.1 Schema

```
+=========================================================+
|  Tombola Stark — Configurazione partita                   |
+---------------------------------------------------------+
|                                                          |
|  Nome giocatore:     [___Giocatore___________]           |
|                                                          |
|  Bot avversari:      [1  v]  (1-7)                       |
|                                                          |
|  Cartelle:           [1  v]  (1-6)                       |
|                                                          |
|  Finestra azione:    [60 v]  secondi (5-300)             |
|                                                          |
|  Pausa tra turni:    [5  v]  secondi (1-30)              |
|                                                          |
|          [  Avvia partita  ]                              |
|                                                          |
|  (messaggio errore qui)                                  |
+---------------------------------------------------------+
```

- **Sfondo**: colore neutro caldo (#FAFAFA).
- **Label**: font 11pt, colore scuro (#333333).
- **Controlli**: bordi definiti, sfondo bianco.
- **Pulsante conferma**: sfondo verde (#2E7D32), testo bianco, font bold 12pt, acceleratore &A.
- **Campo errore**: testo rosso (#C62828) quando attivo.

---

## 6. Palette colori completa

### 6.1 Tema "Tombola Italiana"

Ispirazione: colori caldi mediterranei con accenti tradizionali.

| Ruolo | Codice | Uso |
|---|---|---|
| Primary dark | #1A237E | Sfondo header, sfondo menu principale |
| Primary | #283593 | Sfondo pannelli secondari |
| Accent rosso | #E53935 | Numeri estratti nel tabellone, pulsanti menu |
| Accent dorato | #FFB300 | Numeri interessanti (estratti + presenti in cartella), titolo |
| Verde conferma | #43A047 | Numeri segnati nella cartella, pulsante avvia |
| Verde scuro | #2E7D32 | Pulsante "Inizia partita" |
| Blu azione | #1565C0 | Pulsante "Passa turno", bordo focus |
| Arancione urgenza | #E65100 | Pulsante "Ho finito", avvisi timeout |
| Grigio neutro | #E0E0E0 | Celle vuote cartella |
| Grigio scuro | #424242 | Pulsante pausa, sfondo log |
| Sfondo chiaro | #F5F5F5 | Numeri non estratti tabellone |
| Testo primario | #212121 | Testo principale |
| Testo chiaro | #FFFFFF | Testo su sfondi scuri |
| Sfondo log | #263238 | Area log annunci |
| Testo log | #B0BEC5 | Testo nella cronologia |
| Giallo highlight | #FFF176 | Lampeggio post-estrazione |
| Giallo chiaro | #FFF9C4 | Numero estratto non ancora segnato |
| Errore | #C62828 | Messaggi errore |

### 6.2 Note contrast ratio

Tutti gli accoppiamenti sfondo/testo garantiscono un contrast ratio minimo 4.5:1 (WCAG AA) per testo normale e 3:1 per testo grande. Questo e verificabile con qualsiasi tools di contrast check.

---

## 7. Componenti grafici custom da implementare

### 7.1 PannelloTabellone (nuovo)

**Classe**: `PannelloTabellone(wx.Panel)`
**Responsabilita**: disegna la griglia 10x9 dei numeri 1-90 con colori a stato.
**Input**: set dei numeri estratti, set dei numeri presenti nelle cartelle dell'umano.
**Rendering**: wx.BufferedPaintDC nel metodo OnPaint.
**Aggiornamento**: metodo `aggiorna(numeri_estratti, numeri_in_cartelle_umano)` chiamato dal renderer dopo ogni estrazione.
**Focus**: No. Nessun binding tastiera. Solo display visivo.

### 7.2 PannelloCartellaVisiva (nuovo)

**Classe**: `PannelloCartellaVisiva(wx.Panel)`
**Responsabilita**: disegna la griglia 3x9 della cartella corrente con colori a stato.
**Input**: matrice 3x9 della cartella, set numeri segnati, set numeri estratti, posizione focus (riga, colonna).
**Rendering**: wx.BufferedPaintDC nel metodo OnPaint.
**Aggiornamento**: metodo `aggiorna(cartella, segnati, estratti, focus_riga, focus_colonna)` chiamato dal renderer ad ogni navigazione e ad ogni estrazione.
**Focus**: No. Il focus resta sul PannelloGriglia esistente, che funge da ricevitore invisibile di eventi tastiera. Il PannelloCartellaVisiva e puramente visivo.
**Animazione**: lampeggio cella via wx.Timer (2 secondi, toggle tra #FFF176 e #FFF9C4).

### 7.3 HeaderBar (nuovo)

**Classe**: `HeaderBar(wx.Panel)`
**Responsabilita**: mostra indicatori di turno, ultimo numero, premi assegnati.
**Aggiornamento**: metodo `aggiorna(turno, ultimo_numero, premi)`.

### 7.4 Integrazione con PannelloGriglia esistente

Il PannelloGriglia NON viene sostituito. Resta il ricevitore dei binding Categoria A. La sua etichetta `_etichetta` (wx.StaticText) viene minimizzata o nascosta per gli utenti vedenti, dato che l'informazione e ora rappresentata visivamente dal PannelloCartellaVisiva. Per NVDA, la label rimane accessibile tramite `SetName()`.

Il PannelloCartellaVisiva viene posizionato sopra/accanto al PannelloGriglia nello stesso sizer. Il PannelloGriglia mantiene dimensione minima 1x1 e resta focusable.

### 7.5 Pulsanti navigazione cartella (nuovo)

Due wx.Button con label "<" e ">" posizionati ai lati della griglia cartella.
- Click su "<": chiama `self._comandi.cartella_precedente()` tramite `self._dispatch()`.
- Click su ">": chiama `self._comandi.cartella_successiva()` tramite `self._dispatch()`.
- Disabilitazione automatica ai limiti (prima/ultima cartella) derivata dal conteggio cartelle.
- Stile: sfondo accent (#1565C0), testo bianco, dimensione 40x40px.
- Accessibilita: label "Cartella precedente" e "Cartella successiva" via `SetName()`.

### 7.6 Barra selezione diretta cartella (nuovo)

Da 1 a 6 wx.Button numerati, creati dinamicamente in base al numero di cartelle assegnate.
- Click su [N]: chiama `self._comandi.imposta_focus_cartella(N)` tramite `self._dispatch()`.
- Il pulsante della cartella in focus ha sfondo accent (#1565C0); gli altri sfondo neutro.
- Ridisegnati dal renderer ad ogni cambio cartella.

### 7.7 Barra pulsanti premi (nuovo)

5 wx.Button fissi: [Ambo] [Terno] [Quaterna] [Cinquina] [Tombola].
- Click su [Tipo]: chiama `self._comandi.annuncia_vittoria(tipo, self._turno_corrente)` tramite `self._dispatch()`.
- Abilitati solo durante fase "attesa_reclami".
- Disabilitati permanentemente per premi gia assegnati nella partita.
- Stile: accent rosso (#E53935), tranne Tombola dorato (#FFB300).
- Accessibilita: label estesa ("Dichiara ambo", "Dichiara terno", ecc.).

---

## 8. Aggiornamenti al WxRenderer

### 8.1 Nuovi metodi necessari nel renderer

Il WxRenderer avra bisogno di nuovi metodi per aggiornare i componenti visivi. Questi metodi non toccano la vocalizzazione e sono puramente additivi:

- `_wx_aggiorna_tabellone(numeri_estratti, numeri_in_cartelle)`: aggiorna PannelloTabellone.
- `_wx_aggiorna_cartella_visiva(matrice, segnati, estratti, focus)`: aggiorna PannelloCartellaVisiva.
- `_wx_aggiorna_header(turno, ultimo, premi)`: aggiorna HeaderBar.
- `_wx_evidenzia_numero_estratto(numero)`: trigger lampeggio nel PannelloCartellaVisiva e nel PannelloTabellone.
- `_wx_aggiorna_selezione_cartella(numero_corrente, totale)`: evidenzia il pulsante della cartella corrente nella barra di selezione diretta e aggiorna stato abilitazione frecce.
- `_wx_aggiorna_stato_pulsanti_premi(fase_turno, premi_assegnati)`: abilita/disabilita i pulsanti premi in base alla fase del turno e ai premi gia vinti.

### 8.2 Dove agganciare gli aggiornamenti

Ogni handler esistente del renderer chiama gia `_wx_aggiorna_output()`. I nuovi aggiornamenti visivi si aggiungono come chiamate aggiuntive all'interno degli handler senza modificare il flusso testo/voce:

```python
def _handle_navigazione_riga(self, evento):
    # ... codice esistente invariato ...
    self._wx_aggiorna_output(testo)       # invariato
    self._ao2_vocalizza(testo)            # invariato
    # NUOVO: aggiorna la cartella visiva con la posizione di focus aggiornata
    self._wx_aggiorna_cartella_visiva(...)
```

### 8.3 Hook post-estrazione

In `annuncia_numero_estratto()` si aggiunge:
```python
self._wx_aggiorna_tabellone(...)
self._wx_evidenzia_numero_estratto(numero)
self._wx_aggiorna_header(...)
```

### 8.4 Hook cambio cartella

Negli handler `_handle_focus_cartella_impostato()` e `_handle_riepilogo_cartella_corrente()` si aggiunge:
```python
self._wx_aggiorna_cartella_visiva(...)
self._wx_aggiorna_selezione_cartella(numero_corrente, totale)
```

### 8.5 Hook cambio fase turno

Nel metodo `_aggiorna_stato_pulsante()` di FinestraGioco si aggiunge l'aggiornamento dei pulsanti premi:
```python
self._renderer._wx_aggiorna_stato_pulsanti_premi(self._fase_turno_ui, self._partita.premi_tipo_chiusi)
```

---

## 9. Mappa delle modifiche per file

### 9.1 File da modificare

| File | Tipo modifica | Dettaglio |
|---|---|---|
| finestra_gioco.py | Layout _build_ui | Aggiunta header, pannello tabellone, pannello cartella visiva, frecce navigazione, barra selezione diretta, pulsanti premi, ridimensionamento a 1000x700 |
| finestra_gioco.py | Nuovi handler pulsanti | Handler click per [<] [>], [1]..[6], [Ambo]..[Tombola], tutti delegano a ComandiGiocatoreUmano |
| finestra_gioco.py | Nessun binding tastiera modificato | I binding Categoria A, B, C restano identici |
| finestra_principale.py | Stile visivo | Colori, font, dimensioni pulsanti |
| finestra_configurazione.py | Stile visivo | Colori, font, layout migliorato |
| renderer_wx.py | Metodi _wx_ aggiuntivi | Aggiornamento componenti visivi + selezione cartella + stato premi |

### 9.2 File nuovi

| File | Contenuto |
|---|---|
| bingo_game/ui/pannello_tabellone.py | Custom panel per la griglia 10x9 (1-90) |
| bingo_game/ui/pannello_cartella_visiva.py | Custom panel per la griglia 3x9 della cartella |
| bingo_game/ui/header_bar.py | Panel con indicatori di stato turno |
| bingo_game/ui/tema.py | Costanti palette colori, font, dimensioni |

### 9.3 File non toccati (protezione esplicita)

- Tutti i file in bingo_game/events/ — invariati.
- Tutti i file in bingo_game/players/ — invariati.
- bingo_game/partita.py — invariato.
- bingo_game/tabellone.py — invariato.
- bingo_game/cartella.py — invariato.
- bingo_game/game_controller.py — invariato.
- bingo_game/comandi_partita.py — invariato.
- my_lib/vocalizzatore.py — invariato.
- Tutti i binding tastiera — invariati.
- Il flusso _ao2_vocalizza — invariato.

---

## 10. Idee avanzate (fase successiva)

### 10.1 Effetti visivi opzionali

- **Animazione estrazione**: il numero estratto appare con un effetto "zoom in" al centro della finestra prima di posizionarsi nel tabellone (wx.Timer + scaling text).
- **Confetti su premio**: particelle colorate che partono dalla cartella quando si vince un premio (custom draw con wx.GCDC).
- **Pulsazione premio nella header**: quando si vince un premio, l'indicatore nella header pulsa per 3 secondi.
- **Transizione tra cartelle**: fade breve quando si cambia cartella con Ctrl+frecce.

### 10.2 Modalita cartelle affiancate (fuori scope iniziale)

- Due o tre cartelle mostrate contemporaneamente con griglie piu piccole.
- Attivabile con un toggle (es. Ctrl+M).
- Il focus resta su una sola cartella alla volta; le altre sono solo visive. 

### 10.3 Pannello giocatori (futuro)

- Lista laterale dei giocatori con indicatori di stato (icona premio, conteggio segnati).
- Utile in partite con molti bot per visualizzare chi sta vincendo.

### 10.4 Skin / temi (futuro)

- Tema chiaro e tema scuro selezionabili dalle impostazioni.
- La palette in tema.py viene commutata a runtime.

---

## 11. Rischi e mitigazioni

| Rischio | Probabilita | Mitigazione |
|---|---|---|
| BufferedPaintDC rallenta su hardware vecchio | Bassa | Le griglie sono piccole (90 celle + 27 celle); il ridisegno e veloce |
| Conflitto tra PannelloGriglia e PannelloCartellaVisiva per il focus | Media | PannelloCartellaVisiva non e mai focusable (nessun wx.WANTS_CHARS) |
| I colori personalizzati interferiscono con temi high-contrast Windows | Media | Usare wx.SystemSettings.GetColour per rilevare high-contrast e disabilitare il tema custom |
| L'animazione lampeggio distrae lo screen reader | Nulla | L'animazione e puramente visiva; non produce eventi wx ne testo AO2 |
| wx.BufferedPaintDC non disponibile in alcune versioni wx | Molto bassa | E disponibile da wxPython 2.8; il progetto usa wxPython 4.x |
| I pulsanti premi cliccati fuori dalla fase corretta | Bassa | Disabilitati via Enable(False) in tutte le fasi non "attesa_reclami"; doppia protezione nel handler click |
| Troppi pulsanti visibili creano confusione | Bassa | Gerarchia visiva chiara: navigazione sopra, azione al centro, premi sotto. Separatori o spaziatura generosa |
| Ordine Tab troppo lungo con i nuovi pulsanti | Media | L'utente non vedente non usa Tab per i premi (ha F1-F5); l'utente vedente ha un ordine logico top-down |

---

## 12. Piano di implementazione suggerito

### Fase 1 — Infrastruttura grafica (1 ciclo)

1. Creare `bingo_game/ui/tema.py` con palette colori e costanti.
2. Creare `PannelloTabellone` con rendering statico (tutti i numeri non estratti).
3. Creare `PannelloCartellaVisiva` con rendering statico (cartella di esempio).
4. Creare `HeaderBar` con testi placeholder.
5. Integrare i quattro componenti in `FinestraGioco._build_ui()`.

### Fase 2 — Pulsanti interattivi (1 ciclo)

1. Aggiungere frecce [<] [>] per navigazione cartella in FinestraGioco.
2. Aggiungere barra selezione diretta [1]..[6] con creazione dinamica.
3. Aggiungere barra pulsanti premi [Ambo]..[Tombola].
4. Collegare tutti i click ai metodi ComandiGiocatoreUmano via `_dispatch()`.
5. Implementare logica abilitazione/disabilitazione premi per fase turno.

### Fase 3 — Collegamento al renderer (1 ciclo)

1. Aggiungere metodi `_wx_aggiorna_*` nel WxRenderer.
2. Agganciare `_wx_aggiorna_tabellone` in `annuncia_numero_estratto()`.
3. Agganciare `_wx_aggiorna_cartella_visiva` negli handler di navigazione.
4. Agganciare `_wx_aggiorna_selezione_cartella` negli handler cambio cartella.
5. Agganciare `_wx_aggiorna_stato_pulsanti_premi` nei cambi di fase turno.
6. Agganciare `_wx_aggiorna_header` negli handler di flusso partita.

### Fase 4 — Stile finestre secondarie (1 ciclo)

1. Applicare palette colori a FinestraPrincipale.
2. Applicare palette colori a FinestraConfigurazione.
3. Applicare palette colori ai pulsanti di FinestraGioco.

### Fase 5 — Animazioni e rifinitura (1 ciclo)

1. Implementare lampeggio post-estrazione nel PannelloCartellaVisiva.
2. Implementare bordo focus nella cartella visiva.
3. Verificare ordine Tab e focus ring visivo.
4. Test empirico high-contrast Windows.
5. Test empirico performance ridisegno.

---

## 13. Conclusione

La proposta aggiunge un layer grafico completo e accattivante senza toccare alcun componente del motore di gioco, dei binding tastiera o del flusso vocale. I componenti nuovi (PannelloTabellone, PannelloCartellaVisiva, HeaderBar, tema.py) sono tutti puramente visivi e non intercettano mai il focus della tastiera.

La revisione v2 ha aggiunto tre gruppi di pulsanti per il giocatore vedente:

- **Frecce navigazione cartella** [<] [>]: consentono di scorrere le cartelle con il mouse, delegando a `cartella_precedente()` / `cartella_successiva()` gia presenti in ComandiGiocatoreUmano.
- **Selezione diretta cartella** [1]..[6]: equivalente visivo di Ctrl+1..6, delegano a `imposta_focus_cartella(N)`.
- **Pulsanti premi** [Ambo]..[Tombola]: equivalente visivo di F1..F5, delegano a `annuncia_vittoria(tipo, turno)`. Abilitati solo durante la finestra di reclamo.

Tutti i nuovi pulsanti chiamano metodi gia esistenti nella facade ComandiGiocatoreUmano, quindi non richiedono alcuna modifica al dominio. Il pulsante pausa/riprendi resta sempre visibile come gia implementato.

L'architettura dual-channel (visivo + vocale) garantisce che:
- Un utente vedente vede colori, griglie animate, pulsanti interattivi e indicatori di stato in tempo reale.
- Un utente con screen reader continua a navigare esclusivamente via tastiera con tutti gli annunci vocali invariati.
- Le due esperienze coesistono senza interferenze.

---

*Report generato in modalita analisi. Nessun file di produzione e stato modificato.*
