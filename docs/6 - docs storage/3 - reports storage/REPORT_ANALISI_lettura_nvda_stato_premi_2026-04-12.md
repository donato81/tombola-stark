# REPORT — Analisi di fattibilita: Lettura NVDA stato premi (ultima vittoria e prossimo premio)

**Data**: 2026-04-12
**Autore**: Agent-Analyze
**Stato**: DRAFT — solo analisi, nessuna modifica al codice
**Obiettivo**: Verificare che il codebase attuale supporti l'aggiunta di
tasti rapidi per rileggere con NVDA l'ultima vittoria assegnata e il
prossimo premio da raggiungere durante la partita.

---

## Sommario esecutivo

La funzionalita richiesta e fattibile con impatto localizzato. I dati
necessari (premi gia assegnati e sequenza dei premi) sono gia presenti
nel dominio e accessibili dal layer di presentazione. Manca solamente
il collegamento: nessun tasto rapido consente attualmente di interrogare
queste informazioni in modo accessibile.

**Fattibilita**: ALTA — i dati esistono gia, serve solo il wiring.
**Rischio**: BASSO — le modifiche toccano solo il layer di presentazione
e il livello comandi, senza impattare la logica di dominio.
**Complessita stimata**: BASSA — due nuovi tasti rapidi con handler
semplici che leggono stato gia disponibile.

---

## 1. Contesto e motivazione

Durante una partita, la HeaderBar visiva mostra:

- Turno corrente
- Ultimo numero estratto
- Premi assegnati nel turno

Questi dati sono visibili a schermo ma non raggiungibili da tastiera con
NVDA. Il giocatore non vedente non ha modo di rileggere:

- Quale vittoria e stata assegnata per ultima (e a chi)
- Quale premio e il prossimo da raggiungere nella sequenza della tombola

Questa informazione e cruciale per decidere se reclamare un premio
(F1-F5) oppure passare il turno.

---

## 2. Dati gia disponibili nel dominio

### 2.1 Premi gia assegnati

- `Partita.premi_gia_assegnati` (set di stringhe chiave, es. `"cartella_0_riga_1_ambo"`)
- `Partita.premi_tipo_chiusi` (set di tipi chiusi, es. `{"ambo", "terno"}`)

Entrambi sono attributi pubblici di `Partita` (bingo_game/partita.py, righe 203-204).

### 2.2 Sequenza premi tombola

La sequenza fissa e definita implicitamente nel codice:

```
ambo -> terno -> quaterna -> cinquina -> tombola
```

Questa sequenza e coerente con `_TIPI_VITTORIA` in finestra_gioco.py (riga 75):

```python
_TIPI_VITTORIA = ["ambo", "terno", "quaterna", "cinquina", "tombola"]
```

### 2.3 Informazioni dettagliate sui vincitori

Il metodo `Partita.verifica_premi()` (partita.py, righe 576-662) restituisce
dizionari con chiavi `giocatore`, `cartella`, `premio`, `riga` per ogni
premio assegnato. Questi dati transitano fino al renderer tramite
`annuncia_premi_turno()`.

Il renderer `WxRenderer` dispone di:
- `_ultimo_annuncio` (stringa dell'ultimo testo vocalizzato)
- Metodo `ripeti_ultimo_annuncio()` (collegato a F6)

Il renderer aggiorna anche la HeaderBar tramite `_wx_aggiorna_header()`
con la lista premi formattata.

---

## 3. Tasti rapidi attuali (Cat. C — EVT_CHAR_HOOK)

La tabella dei binding Categoria C nel frame (finestra_gioco.py, righe 33-38):

- Ctrl+T: ultimo numero estratto
- Ctrl+L: lista numeri estratti
- Ctrl+U: ultimi 5 estratti
- Ctrl+R: riepilogo tabellone
- Ctrl+E: consulta log annunci

**Tasti liberi candidate**: Ctrl+G, Ctrl+I, Ctrl+N, Ctrl+Q, Ctrl+W, Ctrl+Y
non sono attualmente in uso nel frame.

Nota: Ctrl+P e gia usato per pausa. Ctrl+F per ricerca. Ctrl+1-6 per
selezione cartella. Alt+1-3 per riga.

---

## 4. Proposta di implementazione

### 4.1 Due nuovi tasti rapidi

- **Ctrl+G** — "Stato premi": vocalizza l'ultima vittoria assegnata
  e il prossimo premio da raggiungere
- **Ctrl+I** — "Info premi dettagliata": vocalizza la lista completa
  dei premi gia assegnati con vincitori

### 4.2 Flusso dati per Ctrl+G (stato premi sintetico)

```
FinestraGioco._on_char_hook()
  -> key == ord("G") and ctrl
  -> legge self._partita.premi_tipo_chiusi
  -> calcola prossimo_premio dalla sequenza _TIPI_VITTORIA
  -> legge ultimo premio dalla HeaderBar o dal set premi_tipo_chiusi
  -> costruisce testo: "Ultimo premio: ambo. Prossimo: terno."
  -> self._renderer.mostra_messaggio_sistema(testo)
```

### 4.3 Flusso dati per Ctrl+I (lista premi dettagliata)

```
FinestraGioco._on_char_hook()
  -> key == ord("I") and ctrl
  -> legge self._partita.premi_gia_assegnati (set di chiavi)
  -> per ogni chiave, estrae tipo e giocatore
  -> costruisce testo: "Premi assegnati: ambo per Bot 1, terno per Giocatore."
  -> self._renderer.mostra_messaggio_sistema(testo)
```

### 4.4 Alternativa: singolo tasto con due livelli

Un unico tasto (es. Ctrl+G) che alla prima pressione da lo stato
sintetico, e alla seconda pressione consecutiva (entro 2 secondi) da
il dettaglio completo. Questa opzione riduce l'ingombro sulla tastiera
ma aggiunge complessita gestionale.

---

## 5. File coinvolti nella modifica

### Layer presentazione
- **bingo_game/ui/finestra_gioco.py**: aggiunta handler in `_on_char_hook()`,
  nuovo metodo privato `_vocalizza_stato_premi()` e `_vocalizza_dettaglio_premi()`
- **bingo_game/ui/renderers/renderer_wx.py**: eventuale nuovo metodo
  `annuncia_stato_premi()` per coerenza con l'API renderer

### Layer comandi (opzionale)
- **bingo_game/comandi_partita.py**: nuovo metodo `stato_premi()` in
  `ComandiGiocatoreUmano` per incapsulare la lettura dello stato premi

### Layer dominio
- **Nessuna modifica necessaria**: i dati `premi_tipo_chiusi` e
  `premi_gia_assegnati` sono gia esposti da `Partita`

### Layer eventi (opzionale)
- **bingo_game/events/codici_output_ui_umani.py**: aggiunta codici template
  (es. `"UMANI_STATO_PREMI_SINTETICO"`, `"UMANI_STATO_PREMI_DETTAGLIATO"`)
- **bingo_game/events/eventi_output_ui_umani.py**: nuovo dataclass
  `EventoStatoPremi` (opzionale, se si vuole passare per il pattern evento)

### Documentazione
- docs/API.md: aggiornamento sezione tasti rapidi
- CHANGELOG.md: voce "Added"

---

## 6. Rischi e considerazioni

### 6.1 Conflitti NVDA

I tasti Ctrl+G e Ctrl+I non risultano conflittuali con le combinazioni
standard NVDA. Tuttavia, Ctrl+I potrebbe collidere con la formattazione
corsivo in alcuni contesti NVDA. Alternativa: Ctrl+W o Ctrl+Y.

Raccomandazione: **test empirico con NVDA** prima di confermare la scelta,
come gia fatto per i tasti Categoria C esistenti.

### 6.2 Informazione prossimo premio

Il calcolo del "prossimo premio" richiede attenzione:

- Se tutti i premi sono chiusi tranne tombola, il prossimo e "tombola"
- Se la partita e terminata, il messaggio deve indicare "Partita terminata,
  tutti i premi assegnati"
- I premi chiusi sono per tipo (non per cartella), quindi il prossimo
  premio e il primo nella sequenza che non e in `premi_tipo_chiusi`

```python
_SEQUENZA_PREMI = ["ambo", "terno", "quaterna", "cinquina", "tombola"]

def _calcola_prossimo_premio(premi_chiusi: set) -> str:
    for premio in _SEQUENZA_PREMI:
        if premio not in premi_chiusi:
            return premio
    return "tutti assegnati"
```

### 6.3 Ultimo premio assegnato con vincitore

Il set `premi_gia_assegnati` contiene chiavi come `"cartella_0_riga_1_ambo"`,
non i nomi dei giocatori. Per avere il nome del vincitore dell'ultimo
premio serve una delle seguenti strategie:

- **Opzione A**: mantenere una lista ordinata di eventi premio (non solo
  un set di chiavi) a livello di Partita — richiede modifica minima al
  dominio
- **Opzione B**: il renderer traccia gli annunci premi nel log e li
  rilegge da li — zero modifiche al dominio, ma accoppia la lettura
  al formato del log
- **Opzione C**: aggiungere un attributo `ultimo_premio_evento` a Partita
  che memorizza il dizionario dell'ultimo premio assegnato — modifica
  minima, una sola riga di codice

Raccomandazione: **Opzione C** — aggiungere `self.ultimo_premio_evento: Optional[Dict] = None`
in `Partita.__init__()` e aggiornarlo in `verifica_premi()` alla riga 652.
Impatto minimo sul dominio, dati gia calcolati.

---

## 7. Stima impatto per layer

- Domain (partita.py): 1 attributo opzionale + 1 riga di aggiornamento
- Application (comandi_partita.py): 1-2 metodi nuovi
- Presentation (finestra_gioco.py): 2 handler + 2 metodi privati (~40 righe)
- Renderer (renderer_wx.py): 1-2 metodi nuovi (~20 righe)
- Eventi (opzionale): 2 codici + 1 dataclass
- Test: test unitari per il calcolo prossimo premio e per i nuovi comandi

---

## 8. Conclusioni e prossimi passi

La funzionalita e implementabile senza ristrutturazioni architetturali.
I dati necessari esistono gia nel dominio. L'intervento principale e nel
layer di presentazione (binding + vocalizzazione).

Prossimi passi consigliati:

1. Conferma scelta tasti rapidi (Ctrl+G / Ctrl+I o alternative) dopo test NVDA
2. Agent-Design per il DESIGN doc (se ritenuto necessario per la complessita)
3. Agent-Plan per il PLAN e il TODO
4. Agent-Code per l'implementazione
5. Agent-Validate per test e copertura

---

## Appendice — Mappa tasti rapidi attuale

### Categoria A (EVT_KEY_DOWN su pannello griglia)

- Frecce: navigazione riga/colonna
- Alt+Frecce: navigazione avanzata
- 1-9: vai a colonna diretta
- Spazio: segna numero
- R: riepilogo cartella corrente
- A: lettura avanzata posizione
- V: visualizza semplice
- Shift+V: visualizza avanzata
- Shift+Ctrl+V: visualizza tutte avanzata
- S: stato focus
- F1-F5: dichiara vittoria
- F6: ripeti ultimo annuncio
- Escape: esci dalla griglia

### Categoria B (EVT_CHAR_HOOK, blocca propagazione)

- Ctrl+Enter: passa turno
- Ctrl+F: ricerca numero
- Ctrl+1-6: salta a cartella N
- Alt+1-3: salta a riga N

### Categoria C (EVT_CHAR_HOOK, verificati su NVDA)

- Ctrl+T: ultimo numero estratto
- Ctrl+L: lista numeri estratti
- Ctrl+U: ultimi 5 estratti
- Ctrl+R: riepilogo tabellone
- Ctrl+E: consulta log annunci
- Ctrl+P: pausa/ripresa

### Proposti (nuovi)

- Ctrl+G: stato premi sintetico (ultima vittoria + prossimo premio)
- Ctrl+I: dettaglio premi completo (lista vincitori)
