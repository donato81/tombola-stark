# Report Analisi — Uscita automatica dal dialog di ricerca

**tipo:** analisi  
**data:** 2026-04-09  
**agente:** Agent-Analyze (via Agent-Orchestrator)  
**stato:** COMPLETATO — in attesa di input utente per fase Design/Plan  

---

## 1. Contesto e obiettivo

L'utente segnala che la funzionalità di ricerca numero (Ctrl+F) richiede la pressione
di ESC per tornare al gioco dopo aver ascoltato i risultati. Questo rallenta il flusso
di gioco per un utente non vedente con NVDA.

**obiettivo della modifica richiesta:**  
Dopo che il sistema ha annunciato i risultati della ricerca, il dialog deve chiudersi
automaticamente e il focus deve posizionarsi sulla cartella/riga/colonna del primo
risultato trovato. Se il numero non è trovato, il dialog rimane aperto o si chiude
senza navigare.

---

## 2. Flusso attuale — descrizione codice

### 2.1 Catena di chiamata

```
FinestraGioco._on_char_hook()         ← Ctrl+F intercettato qui
  └─ _apri_ricerca_numero()           ← bingo_game/ui/finestra_gioco.py:610
       ├─ DialogoRicercaNumero(parent, renderer, comandi)
       ├─ dlg.ShowModal()             ← BLOCCA fino a ESC/Chiudi
       ├─ dlg.Destroy()
       └─ _pannello_griglia.SetFocus()  ← focus ripristinato DOPO chiusura dialog
```

### 2.2 Flusso interno al dialog (bingo_game/ui/dialogo_ricerca.py)

```
DialogoRicercaNumero._on_cerca()
  ├─ self._comandi.cerca_numero(numero)
  │     → EsitoAzione(ok=True, evento=EventoRicercaNumeroInCartelle)
  ├─ self._renderer.render_esito(esito)
  │     → _handle_ricerca_numero_in_cartelle(evento)
  │          → _wx_aggiorna_output(testo)   ← aggiorna log testuale
  │          → _ao2_vocalizza(testo)        ← vocalizza via NVDA
  ├─ self._lbl_risultato.SetLabel(testo_risultato)
  └─ self._input_ctrl.SetFocus()            ← focus rimane sull'input → attende ESC
```

**Il dialog non chiama mai EndModal() dopo la ricerca.**  
Il comportamento attuale è esplicitamente verificato da un test:  
`tests/unit/test_dialogo_ricerca_persistente.py::test_on_cerca_non_chiama_end_modal`

---

## 3. Struttura dati rilevante

### 3.1 EsitoAzione (bingo_game/events/eventi.py)

```python
@dataclass(frozen=True)
class EsitoAzione:
    ok: bool
    errore: Optional[Codici_Errori] = None
    evento: Optional[EventoAzione] = None
```

L'oggetto `esito` restituito da `cerca_numero()` è direttamente disponibile
nel metodo `_on_cerca()` del dialog. Contiene `esito.evento` di tipo
`EventoRicercaNumeroInCartelle`.

### 3.2 EventoRicercaNumeroInCartelle (bingo_game/events/eventi_output_ui_umani.py)

```python
@dataclass(frozen=True)
class EventoRicercaNumeroInCartelle:
    id_giocatore: Optional[int]
    nome_giocatore: str
    numero: int
    totale_cartelle: int
    esito: Literal["trovato", "non_trovato"]
    risultati: tuple[RisultatoRicercaNumeroInCartella, ...]
```

`risultati` è una tupla già **ordinata per indice_cartella** (garantito dal factory
`trovato()`) e vuota se `esito == "non_trovato"`.

### 3.3 RisultatoRicercaNumeroInCartella

```python
@dataclass(frozen=True)
class RisultatoRicercaNumeroInCartella:
    indice_cartella: int    # 0-based
    numero_cartella: int    # 1-based (= indice_cartella + 1)
    indice_riga: int        # 0-based
    indice_colonna: int     # 0-based
    segnato: bool
```

### 3.4 Comandi di navigazione disponibili (già esistenti, nessuna aggiunta necessaria)

| Comando | Parametro | Note |
|---------|-----------|------|
| `ComandiGiocatoreUmano.imposta_focus_cartella(n)` | 1-based | salta alla cartella n |
| `ComandiGiocatoreUmano.vai_a_riga(n)` | 1-based | salta alla riga n nella cartella corrente |
| `ComandiGiocatoreUmano.vai_a_colonna(n)` | 1-based | salta alla colonna n nella riga corrente |

**Conversione necessaria:**  
`numero_cartella` già 1-based.  
`indice_riga + 1` → 1-based per `vai_a_riga`.  
`indice_colonna + 1` → 1-based per `vai_a_colonna`.

---

## 4. Opzioni di implementazione

### Opzione A — Auto-chiusura sincrona con risultato esposto come attributo

**Meccanismo:**  
Dopo `render_esito()`, il dialog controlla se `evento.esito == "trovato"`.  
Se sì, salva il primo risultato in `self._primo_risultato` e chiama `EndModal(wx.ID_OK)`.  
`_apri_ricerca_numero()` in `FinestraGioco` legge `dlg._primo_risultato` dopo
`ShowModal()` e dispatcha i tre comandi di navigazione.

**Modifiche richieste:**
- `dialogo_ricerca.py`: aggiungere `self._primo_risultato` e `EndModal(wx.ID_OK)` nel ramo trovato di `_on_cerca()`
- `finestra_gioco.py`: leggere `dlg._primo_risultato` dopo `ShowModal()` e fare dispatch

**Impatto test:**
- `test_on_cerca_non_chiama_end_modal` → da aggiornare: ora `EndModal` deve essere chiamata nel ramo trovato
- Aggiungere test: `test_on_cerca_chiama_end_modal_se_trovato`
- Aggiungere test: `test_on_cerca_non_chiama_end_modal_se_non_trovato`

**PRO:**
- Minimo impatto architetturale (2 file, nessun nuovo parametro pubblico)
- Nessuna modifica al domain layer
- Logica chiara e testabile
- Comportamento prevedibile per NVDA: focus cambia dopo chiusura dialog

**CON:**
- NVDA potrebbe interrompere la lettura del risultato quando il focus si sposta:
  la voce parte su dialog, poi il dialog si chiude e il focus torna al pannello griglia.
  Dipende dalla velocità di sintesi e dalla reattività di NVDA.

---

### Opzione B — Auto-chiusura con ritardo (wx.CallLater per NVDA)

**Meccanismo:**  
Uguale a Opzione A, ma `EndModal()` viene chiamata tramite `wx.CallLater(400, self.EndModal, wx.ID_OK)`
anziché in modo sincrono. Il ritardo di 400ms lascia il tempo a NVDA di iniziare
la lettura del risultato prima che il focus cambi.

**Modifiche richieste:** le stesse di Opzione A con un `wx.CallLater`.

**Impatto test:** uguale ad A (i test mockano `EndModal`, non il timer).  
Nota: `wx.CallLater` non è facilmente testabile in unit test senza wx; può restare
non coperto o vanno aggiunti test di integrazione.

**PRO:**
- Risolve il rischio NVDA identificato in Opzione A: la voce ha tempo di partire
- Non cambia il flusso architetturale rispetto ad A

**CON:**
- Il ritardo (400ms) è empirico; potrebbe richiedere aggiustamenti in base al sintetizzatore
- Se l'utente preme ESC o Chiudi prima dei 400ms, `EndModal` viene chiamata due volte
  (la prima da ESC, la seconda dal CallLater): questo è **sicuro** in wxPython perché
  il secondo `EndModal` su un dialog già chiuso viene ignorato, ma va documentato.

---

### Opzione C — Dialog non-modale (non-blocking Show)

**Meccanismo:**  
Cambiare `ShowModal()` con `Show()` rendendo il dialog non bloccante.
L'utente può interagire con la finestra di gioco senza chiudere il dialog.
Il dialog si auto-chiude (o no) dopo il risultato.

**Modifiche richieste:**
- `finestra_gioco.py`: cambio `ShowModal()` → `Show()`, gestione ciclo di vita dialog
- `dialogo_ricerca.py`: gestione focus non-modale, rimozione `EndModal`
- Potenziale conflitto: se l'utente apre due dialog sovrapposti (nessun blocco)

**PRO:**
- Massima flessibilità di interazione

**CON:**
- Cambio architetturale maggiore (ciclo di vita dialog non-modale più complesso)
- Rischio focus management NVDA: con dialog non-modale NVDA può non spostare
  il virtual cursor correttamente, rendendo il dialog inaccessibile
- Non raccomandato su Windows 11 con NVDA per wxPython senza test empirici approfonditi

---

### Opzione D — Ricerca inline senza dialog

**Meccanismo:**  
Rimuovere il dialog. Aggiungere un `wx.TextCtrl` nascosto nella `FinestraGioco`
che si attiva con Ctrl+F, riceve l'input, esegue la ricerca e naviga al risultato.

**Modifiche richieste:**
- Eliminare `dialogo_ricerca.py` (o mantenerlo come fallback)
- Aggiungere widget inline in `finestra_gioco.py`
- Ridisegnare il flusso di input Ctrl+F

**PRO:**
- Nessun dialog da chiudere: eliminata la frizione di ESC alla radice
- Flusso più snello

**CON:**
- Impatto architetturale maggiore (nuovo componente UI, riscrittura parziale di FinestraGioco)
- Richiede nuovo DESIGN.md / PLAN.md separato
- Aumenta complessità di `FinestraGioco` già articolata

---

## 5. Raccomandazione

**Opzione B** è la più coerente con l'architettura attuale e le esigenze di accessibilità NVDA.

Motivazioni:
- Minimo impatto: modifica circoscritta a `dialogo_ricerca.py` e `finestra_gioco.py`
- Nessun cambiamento al domain layer o ai comandi
- Il ritardo di `wx.CallLater` garantisce che NVDA inizi la lettura prima del cambio focus
- Il ramo "non trovato" mantiene il comportamento attuale (il dialog rimane aperto per permettere una nuova ricerca)
- Il ramo "trovato" naviga automaticamente al primo risultato nella cartella corretta

**Sequenza risultante per l'utente:**
1. Ctrl+F → dialog si apre, focus sull'input
2. Digita numero, premi Invio
3. NVDA annuncia: "Numero 42 trovato in: Cartella 2, riga 1, colonna 3 (non segnato)."
4. Dopo ~400ms: dialog si chiude automaticamente
5. Focus torna alla griglia, posizionato su Cartella 2, Riga 1, Colonna 3

---

## 6. File coinvolti dalla modifica

| File | Tipo modifica |
|------|--------------|
| `bingo_game/ui/dialogo_ricerca.py` | Aggiungere logica auto-chiusura con `wx.CallLater` |
| `bingo_game/ui/finestra_gioco.py` | Navigare al primo risultato dopo `ShowModal()` |
| `tests/unit/test_dialogo_ricerca_persistente.py` | Aggiornare test esistente + aggiungere 2 test |

**File NON coinvolti:**
- Nessun file in `bingo_game/events/`
- Nessun file in `bingo_game/players/`
- Nessun file in `bingo_game/comandi_partita.py`
- Nessun file in `bingo_game/ui/renderers/`

---

## 7. Nodo critico rilevato (NVDA race condition)

La transizione focus dialog → pannello griglia mentre NVDA sta leggendo il risultato
è il rischio principale. Il ritardo di `wx.CallLater` in Opzione B mitiga ma non elimina
il problema: la durata ottimale dipende dalla velocità del sintetizzatore e dal testo
da leggere (risultati plurimi = testo più lungo).

Una possibile estensione futura: calcolare il ritardo in base alla lunghezza del testo
(es. 50ms per carattere, minimo 400ms), oppure usare `wx.CallLater(600, ...)` per testi
con più di un risultato. Questo non è necessario nella prima iterazione.

---

*Fine report analisi — 2026-04-09*
