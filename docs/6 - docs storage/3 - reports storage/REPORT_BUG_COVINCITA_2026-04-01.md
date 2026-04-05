# REPORT_BUG_COVINCITA_2026-04-01

---

**Tipo:** Bug Analysis — Co-vincita simultanea  
**Data:** 2026-04-01  
**Agente:** Agent-Analyze (read-only)  
**Stato:** COMPLETATO — no codice correttivo prodotto  

---

## Executive Summary

Quando il giocatore umano e uno o più bot raggiungono lo stesso tipo di premio
nello stesso turno, il premio viene assegnato solo al bot. La causa principale è
un disallineamento di indicizzazione: il giocatore umano costruisce il proprio
reclamo usando `_indice_cartella_focus` che è **0-based** (0 per la prima
cartella), mentre `Partita.verifica_premi()` cerca la cartella per chiave
`cartella.indice` che è **1-based** (1 per la prima cartella, impostato da
`aggiungi_cartella()`). La ricerca restituisce `None` e il reclamo umano viene
scartato silenziosamente, senza alcun errore visibile. Il bot non soffre del
problema perché costruisce il proprio reclamo usando `cartella.indice`
direttamente. I test esistenti non coprono questo percorso perché impostano
`reclamo_turno` bypassando `annuncia_vittoria()`.

---

## Percorso del reclamo umano — passo per passo

**Precondizioni d'uso**: la partita è in fase `attesa_reclami` (dopo che
`esegui_fase_estrazione()` ha già estratto il numero e i bot hanno già
registrato i propri reclami).

| Passo | Metodo | File | Riga approssimativa | Dettaglio |
|-------|--------|------|----------------------|-----------|
| 1 | Tastiera: F1..F5 | `finestra_gioco.py` | 161-165 | L'utente preme un tasto funzione. `tipo = _TIPI_VITTORIA[indice]` è calcolato come `key - wx.WXK_F1` (0..4), mappato a `["ambo", "terno", "quaterna", "cinquina", "tombola"]`. |
| 2 | `FinestraGioco._on_char_hook()` | `finestra_gioco.py` | 165 | Chiama `fg._comandi.annuncia_vittoria(tipo, fg._turno_corrente)`. |
| 3 | `ComandiGiocatoreUmano.annuncia_vittoria()` | `comandi_partita.py` | 409-412 | Facade: delega a `self._giocatore.annuncia_vittoria(tipo, numero_turno)`. |
| 4 | `GiocatoreUmano.annuncia_vittoria()` | `giocatore_umano.py` | 2244 | Controlla che non esista già un reclamo per il turno (`esito_reclamo_turno_libero`). |
| 5 | — | `giocatore_umano.py` | 2282-2296 | **Per tombola**: costruisce `ReclamoVittoria.tombola(indice_cartella=self._indice_cartella_focus)`. `_indice_cartella_focus` è 0-based (0 per la prima cartella). **Per premi di riga**: costuisce anche `indice_riga=self._indice_riga_focus` che è 0-based (0 per la prima riga). |
| 6 | — | `giocatore_umano.py` | 2297 | `self.reclamo_turno = reclamo`. Il reclamo viene salvato sull'oggetto giocatore. |
| 7 | Pulsante "Ho finito" | `finestra_gioco.py` | 351-352 | L'utente preme il pulsante. `_fase_turno_ui == "attesa_reclami"` → chiama `self._comandi_sistema.esegui_fase_verifica(self._partita)`. |
| 8 | `ComandiSistema.esegui_fase_verifica()` | `comandi_partita.py` | 131-146 | Delega a `esegui_fase_verifica_sicura(partita)`. |
| 9 | `esegui_fase_verifica_sicura()` | `game_controller.py` | 571 | Chiama `partita.esegui_fase_verifica()`. |
| 10 | `Partita.esegui_fase_verifica()` | `partita.py` | 752 | Chiama `self.verifica_premi()`. |
| 11 | `Partita.verifica_premi()` | `partita.py` | 598 | Ciclo su tutti i giocatori. Per il giocatore umano: `reclamo_turno` non è None → prosegue. |
| 12 | — | `partita.py` | 603-608 | **PUNTO DI FALLIMENTO**: cerca la cartella con `next((c for c in giocatore.get_cartelle() if c.indice == reclamo.indice_cartella), None)`. `reclamo.indice_cartella = 0` (0-based), `c.indice = 1` (1-based) → `1 == 0` → False → `cartella = None`. |
| 13 | — | `partita.py` | 609 | `if cartella is None: continue` — reclamo umano scartato silenziosamente. |

---

## Percorso del reclamo bot — passo per passo

**Precondizioni d'uso**: il bot registra il proprio reclamo durante
`esegui_fase_estrazione()`, ossia nella stessa chiamata che estrae il numero,
PRIMA che l'utente possa interagire.

| Passo | Metodo | File | Riga approssimativa | Dettaglio |
|-------|--------|------|----------------------|-----------|
| 1 | `Partita.esegui_fase_estrazione()` | `partita.py` | 723-729 | Dopo `estrai_prossimo_numero()`, ciclo sui giocatori automatici. |
| 2 | `GiocatoreAutomatico._valuta_potenziale_reclamo()` | `giocatore_automatico.py` | 86 | Il bot scansiona tutte le proprie cartelle. Per ogni cartella, usa `cartella.indice` (1-based) direttamente. |
| 3 | — | `giocatore_automatico.py` | 144-152 | Costruisce `ReclamoVittoria(tipo="tombola", indice_cartella=cartella.indice, ...)`. `cartella.indice = 1` per la prima cartella. |
| 4 | — | `partita.py` | 730-731 | `if reclamo is not None: giocatore.reclamo_turno = reclamo`. Reclamo bot salvato. |
| 5 | *(fase attesa_reclami)* | — | — | Nessuna azione del bot durante questa fase: il reclamo è già stato registrato. |
| 6 | `Partita.esegui_fase_verifica()` | `partita.py` | 752 | Chiama `self.verifica_premi()`. |
| 7 | `Partita.verifica_premi()` | `partita.py` | 598 | Ciclo su tutti i giocatori. Per il bot: `reclamo_turno` non è None → prosegue. |
| 8 | — | `partita.py` | 603-608 | Cerca la cartella con `c.indice == reclamo.indice_cartella`. `reclamo.indice_cartella = 1`, `c.indice = 1` → `1 == 1` → True → cartella trovata. |
| 9 | — | `partita.py` | 611 | `stato_cartella = self.verifica_premi_per_cartella(cartella)` → analisi della cartella. |
| 10 | — | `partita.py` | 615-626 | Per tombola: costruisce la chiave, verifica `premi_tipo_chiusi` e `premi_gia_assegnati`, aggiunge a `candidati_per_tipo["tombola"]`. |
| 11 | — | `partita.py` | 648-660 | Seconda passata: assegna il premio al bot, aggiunge l'evento a `nuovi_eventi`, chiude il tipo `"tombola"` in `premi_tipo_chiusi`. |

---

## Punto di divergenza

I due percorsi si separano al **passo 12 del percorso umano** (equivalente al
passo 8 del percorso bot), cioè nella ricerca della cartella all'interno di
`Partita.verifica_premi()`:

```python
# partita.py — verifica_premi() — riga ~605
cartella = next(
    (c for c in giocatore.get_cartelle() if c.indice == reclamo.indice_cartella),
    None
)
if cartella is None:
    continue  # ← reclamo umano eliminato qui
```

**Umano**: `reclamo.indice_cartella = 0` (da `_indice_cartella_focus`, 0-based)  
**Bot**: `reclamo.indice_cartella = 1` (da `cartella.indice`, 1-based)  
**Cartella reale**: ha sempre `indice = 1` (impostato da `aggiungi_cartella()`)

La lookup `c.indice == 0` non trova corrispondenza. Il reclamo umano viene
scartato, il bot prosegue.

---

## Problemi trovati

---

### PROBLEMA 1 — Off-by-one critico nel reclamo umano (causa principale)

**File**: `bingo_game/players/giocatore_umano.py`  
**Metodo**: `annuncia_vittoria()`  
**Riga**: ~2282-2296  

**Comportamento attuale**:  
`ReclamoVittoria` viene costruito con:
```python
indice_cartella=self._indice_cartella_focus  # 0-based: 0 per prima cartella
```
Il campo `_indice_cartella_focus` è l'indice interno della lista `self.cartelle`
(0-based). Con una sola cartella, vale sempre `0`.

**Comportamento atteso**:  
`indice_cartella` deve contenere `cartella.indice`, che `aggiungi_cartella()`
imposta a partire da `_prossimo_indice_cartella = 1` (1-based). Con una sola
cartella, deve valere `1`.

**Effetto**: `Partita.verifica_premi()` cerca `c.indice == 0`, non trova
risultato, scarta il reclamo silenziosamente. Il giocatore umano non riceve
mai premi, indipendentemente da quante cartelle abbia o da quale premio
stia reclamando.

**Nota sull'`indice_riga`**: il campo `_indice_riga_focus` è anch'esso 0-based,
ma i dizionari interni di `verifica_premi_per_cartella()` usano `range(3)` come
chiavi (0, 1, 2), quindi non c'è disallineamento per la riga. Solo
`indice_cartella` è affetto dal problema.

---

### PROBLEMA 2 — I test non coprono il percorso di produzione del reclamo umano

**File**: `tests/test_partita.py`, `tests/unit/test_fase_verifica_co_vincita.py`  
**Metodo**: `_assegna_reclamo_riga()`, `_assegna_reclamo_tombola()`  
**Riga**: test_partita.py ~80-96; test_co_vincita.py ~28-42  

**Comportamento attuale**:  
I test impostano direttamente `giocatore.reclamo_turno` usando `cartella.indice`
(il valore 1-based corretto), bypassando completamente il metodo
`GiocatoreUmano.annuncia_vittoria()`.

```python
# Nei test — usa il valore CORRETTO direttamente
giocatore_1.reclamo_turno = ReclamoVittoria.vittoria_di_riga(
    tipo="ambo",
    indice_cartella=cartella_1.indice,  # ← 1-based, corretto
    indice_riga=0,
)
```

**Comportamento atteso**:  
Dovrebbe esistere almeno un test di integrazione che simuli il flusso
`GiocatoreUmano.imposta_focus_cartella(1)` →
`GiocatoreUmano.annuncia_vittoria("ambo", turno)` →
`Partita.verifica_premi()` → assegnazione premio. Questo test avrebbe rilevato
il bug.

**Effetto**: il bug esiste in produzione ma non viene catturato dalla test suite.

---

### PROBLEMA 3 — Asimmetria sistematica nel momento del reclamo

**File**: `bingo_game/partita.py`  
**Metodo**: `esegui_fase_estrazione()` vs interazione UI  
**Riga**: ~723-731  

**Comportamento attuale**:  
Il bot registra il proprio reclamo durante `esegui_fase_estrazione()`, nello
stesso ciclo che estrae il numero. L'utente può registrare il proprio reclamo
solo nella finestra `attesa_reclami`, successiva. I bot reclamano quindi sempre
PRIMA dell'utente, con la stessa vista di `premi_gia_assegnati` e
`premi_tipo_chiusi`.

**Comportamento atteso**:  
Questo non è di per sé un bug: il turno bifasico è by design. Tuttavia,
l'asimmetria produce un effetto secondario: se un tipo di premio fosse già chiuso
in `premi_tipo_chiusi` al momento della verifica (per un turno precedente), il
bot lo rileva durante `esegui_fase_estrazione()` e si astiene dal reclamare,
mentre l'utente potrebbe comunque farlo inutilmente. L'esito è corretto (nessuno
riceve un premio già chiuso) ma l'utente non riceve un feedback immediato
(solo silenzio al momento della verifica).

**Impatto**: medio-basso. Non causa perdita di premi validi, causa solo
asimmetria informativa.

---

### PROBLEMA 4 — `break` nella logica row-prizes previene fallback a premi inferiori

**File**: `bingo_game/partita.py`  
**Metodo**: `verifica_premi()`  
**Riga**: ~633-644  

**Comportamento attuale**:  
Nel ciclo che cerca il premio più alto sulla riga:
```python
for tipo in ["cinquina", "quaterna", "terno", "ambo"]:
    if premi_riga.get(tipo, False):
        chiave = ...
        if tipo not in self.premi_tipo_chiusi and chiave not in self.premi_gia_assegnati:
            # aggiunge ai candidati
        break  # ← always breaks when highest prize is found on row
```

Il `break` è nella posizione correttamente indentata (dentro il primo `if`), ma
il suo effetto è che se il tipo più alto sulla riga è già in `premi_tipo_chiusi`,
il giocatore NON può reclamare il tipo inferiore disponibile. Esempio: la riga
ha "terno" (che implica "ambo"). Se "terno" è già chiuso perché assegnato in un
turno precedente, il giocatore non potrà ricevere neanche "ambo" (che potrebbe
non essere chiuso).

**Comportamento atteso**:  
Se il tipo più alto sulla riga è già chiuso, il ciclo dovrebbe continuare a
cercare il tipo successivo disponibile.

**Impatto**: basso in gioco normale (un tipo di premio viene chiuso solo quando
viene assegnato per la prima volta, dopodiché nessuno può ottenerlo). Il caso si
manifesta solo se la stessa riga ha già ricevuto un premio in un turno
precedente e il giocatore vuole reclamare un premio "inferiore". Nella tombola
italiana classica questo scenario non si verifica (ogni riga può ottenere premi
progressivi), ma con le regole attuali dove il tipo viene chiuso a livello
globale potrebbe essere rilevante.

---

### PROBLEMA 5 — `passa_turno()` definito ma non chiamato, con side effect nascosto

**File**: `bingo_game/players/giocatore_umano.py`  
**Metodo**: `passa_turno()`, `_passa_turno_core()`  
**Riga**: ~2322-2337 (`passa_turno`), ~302-326 (`_passa_turno_core`)  

**Comportamento attuale**:  
`GiocatoreUmano.passa_turno()` è definito e documentato ma non viene mai
chiamato nel flusso di gioco effettivo (non in `partita.py`, non in
`game_controller.py`, non in `comandi_partita.py`, non in `finestra_gioco.py`).
Il metodo chiama `_passa_turno_core()` che, oltre a costruire l'evento
`EventoFineTurno`, **resetta `self.reclamo_turno = None`** come side effect.

Se `passa_turno()` venisse inavvertitamente richiamato prima di
`esegui_fase_verifica()`, il reclamo umano verrebbe azzerato prima che
`verifica_premi()` lo legga.

**Comportamento atteso**:  
Se il metodo non è parte del flusso, dovrebbe essere documentato come obsoleto o
rimosso. Se fa parte di un flusso alternativo (es. modalità TUI prevista),
il suo side effect di reset deve essere indicato esplicitamente.

**Impatto**: attualmente zero (il metodo non è chiamato). Rischio latente di
regressione future se reintegrato.

---

### PROBLEMA 6 — `tutti_hanno_dichiarato_fine()` definito ma non usato nel flusso UI

**File**: `bingo_game/partita.py`  
**Metodo**: `tutti_hanno_dichiarato_fine()`  
**Riga**: ~813  

**Comportamento attuale**:  
Il metodo esiste ma non viene chiamato né da `game_controller.py` né da
`finestra_gioco.py`. La UI usa un approccio "secondo clic = verifica" senza
attendere che il giocatore dichiari esplicitamente fine turno. Il metodo
`ComandiGiocatoreUmano.dichiara_fine_turno()` di `comandi_partita.py` è
anch'esso definito ma non usato nella UI.

**Comportamento atteso**:  
Se il design a due fasi prevede che l'utente debba dichiarare fine turno prima
che la verifica parta, il metodo deve essere integrato nel flusso. Altrimenti
è codice morto e dovrebbe essere rimosso o documentato come "non implementato".

**Impatto**: nessuno sul bug corrente. Può causare confusione durante la
manutenzione.

---

## Sintesi della seconda passata (logica co-vincita)

La doppia passata in `Partita.verifica_premi()` è **logicamente corretta**:
nella prima passata tutti i candidati per ogni tipo vengono raccolti senza
assegnazione, nella seconda passata tutti i candidati di ogni tipo ricevono
il premio. Questo meccanismo è in grado di gestire genuinamente la co-vincita
se entrambi i reclami arrivano alla verifica con i dati corretti.

Il problema non è nella logica della doppia passata — che funziona — ma nel
fatto che il reclamo del giocatore umano viene eliminato **prima** di entrare
nella prima passata, a causa del mismatch di indicizzazione.

Il test `test_fase_verifica_co_vincita.py` dimostra che la doppia passata
funziona correttamente quando entrambi i giocatori costruiscono il reclamo con
`cartella.indice` (1-based). Il bug è esclusivamente nel punto di costruzione
del reclamo umano.

---

## Conclusione

**Il problema è risolvibile con una modifica locale, senza refactoring.**

La causa principale (Problema 1) richiede una modifica di **una sola riga**
in `GiocatoreUmano.annuncia_vittoria()`: sostituire `self._indice_cartella_focus`
(indice 0-based) con `self.cartelle[self._indice_cartella_focus].indice`
(il `cartella.indice` del dominio, 1-based) nella costruzione di
`ReclamoVittoria`.

Occorre verificare anche i metodi `vittoria_di_riga` (per premi di riga) per
accertarsi che `indice_riga` non abbia lo stesso tipo di disallineamento (analisi
preliminare suggerisce che non ce l'ha, in quanto le righe della cartella usano
anch'esse 0-based internamente tramite `range(3)`).

La modifica va accompagnata da:
- Un test di integrazione che esercita il percorso completo
  `imposta_focus_cartella(1)` → `annuncia_vittoria()` → `verifica_premi()` per
  il giocatore umano.
- Un test specifico di co-vincita che usa `GiocatoreUmano` + `GiocatoreAutomatico`
  entrambi con tombola nello stesso turno.

Il Problema 4 (break loop) richiede una modifica di 2-3 righe nella stessa
funzione `verifica_premi()` e non blocca il fix principale.

I Problemi 5 e 6 (codice inutilizzato) possono essere affrontati in una fase
separata come cleanup.
