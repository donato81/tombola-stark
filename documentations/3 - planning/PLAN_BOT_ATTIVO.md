# 📋 PLAN_BOT_ATTIVO.md - Tombola Stark

> **Piano di implementazione: funzionalità Bot Attivo**
> Versione: v1.0.0
> Creato: 2026-02-19

---

## 📌 Obiettivo

Estendere `GiocatoreAutomatico` affinché, al termine di ogni estrazione, valuti autonomamente
se ha conseguito un premio e lo dichiari alla `Partita` tramite un `ReclamoVittoria`,
esattamente come farebbe un giocatore umano.

Il bot deve:
- analizzare lo stato delle proprie cartelle dopo ogni numero estratto,
- costruire un `ReclamoVittoria` coerente con le convenzioni del dominio,
- consegnarlo alla `Partita` all'interno del flusso `esegui_turno`,
- ricevere un esito (successo / rigetto) che confluisce nel dizionario risultato del turno.

---

## 🏗️ Architettura della soluzione

La soluzione rispetta rigorosamente le regole architetturali esistenti (ARCHITECTURE.md):

```
GiocatoreAutomatico.valuta_potenziale_reclamo(premi_gia_assegnati: set[str])
    └─ Legge le proprie cartelle (Cartella.verifica_*_riga, verifica_cartella_completa)
    └─ Costruisce ReclamoVittoria tramite factory (tombola / vittoria_di_riga)
    └─ Ritorna Optional[ReclamoVittoria]

Partita.esegui_turno()  [fase estesa]
    ├─ estrai_prossimo_numero()        ← invariato
    ├─ [NUOVO] ciclo Bot:
    │      bot.valuta_potenziale_reclamo(premi_gia_assegnati)
    │      → memorizza il reclamo su bot.reclamo_turno
    ├─ verifica_premi()                ← invariato, rimane l'unico arbitro
    ├─ [NUOVO] confronto reclami bot vs premi_nuovi → esiti reclami
    ├─ [NUOVO] reset reclamo_turno per ogni bot
    ├─ has_tombola() / termina_partita()  ← invariato
    └─ return dict + chiave "reclami_bot"  ← nuova, backward-compatible

GameController.esegui_turno_sicuro()  [fase estesa]
    └─ legge "reclami_bot" dal risultato
    └─ logga su tombola_stark.prizes ogni reclamo con esito
```

**Regola chiave**: `verifica_premi()` rimane l'unico ground truth.
I reclami del bot sono una sovrastruttura UX/log, non sostituiscono la validazione.

---

## 📂 File coinvolti

| File | Tipo di modifica | Rischio |
|---|---|---|
| `bingo_game/players/giocatore_automatico.py` | Aggiunta metodo interno | 🟢 Basso |
| `bingo_game/partita.py` | Estensione `esegui_turno()` | 🟡 Medio |
| `bingo_game/game_controller.py` | Aggiunta logging reclami bot | 🟢 Basso |
| `tests/` | Aggiunta test unitari e di integrazione | 🟢 Basso |
| `documentations/API.md` | Aggiornamento sezione GiocatoreAutomatico + esegui_turno | 🟢 Basso |
| `documentations/ARCHITECTURE.md` | Aggiornamento flusso turno | 🟢 Basso |

---

## 🔢 Fasi di implementazione

### FASE 1 — Dominio: logica di introspezione del Bot

**File**: `bingo_game/players/giocatore_automatico.py`

#### Task 1.1 — Implementare `valuta_potenziale_reclamo()`

Questo è il metodo centrale della feature. È un metodo **interno** al bot
(prefissato con `_` secondo le convenzioni di progetto), non fa parte dell'API pubblica.

**Firma**:
```
_valuta_potenziale_reclamo(premi_gia_assegnati: set[str]) -> Optional[ReclamoVittoria]
```

**Algoritmo**:
1. Definire la gerarchia di premi in ordine decrescente:
   `["tombola", "cinquina", "quaterna", "terno", "ambo"]`
2. Inizializzare `best_claim = None` e `best_rank = -1`.
3. Per ogni `cartella` in `self.get_cartelle()`:
   - **Tombola**: se `cartella.verifica_cartella_completa()` è True:
     - costruire la chiave: `f"cartella_{cartella.indice}_tombola"`
     - se la chiave NON è in `premi_gia_assegnati`:
       - creare `ReclamoVittoria.tombola(indice_cartella=cartella.indice)`
       - aggiornare `best_claim` se il rango tombola (4) > `best_rank`
   - **Premi di riga** (ambo/terno/quaterna/cinquina): per riga in [0, 1, 2]:
     - per tipo in ordine decrescente `["cinquina", "quaterna", "terno", "ambo"]`:
       - se `cartella.verifica_<tipo>_riga(riga)` è True:
         - costruire la chiave: `f"cartella_{cartella.indice}_riga_{riga}_{tipo}"`
         - se la chiave NON è in `premi_gia_assegnati`:
           - creare `ReclamoVittoria.vittoria_di_riga(tipo=tipo, indice_cartella=cartella.indice, indice_riga=riga)`
           - aggiornare `best_claim` se il rango > `best_rank`
4. Return `best_claim` (None se nessun premio reclamabile trovato).

**Nota implementativa**: il parametro `premi_gia_assegnati` è il `set` interno di `Partita`
**al momento della valutazione**, cioè **prima** che `verifica_premi()` lo aggiorni per questo turno.
In questo modo il bot valuta correttamente su base premi precedenti.

**Dipendenze**:
- `bingo_game.events.eventi_partita.ReclamoVittoria` (import già presente nella gerarchia)
- Metodi di `Cartella` già implementati: `verifica_ambo_riga`, `verifica_terno_riga`,
  `verifica_quaterna_riga`, `verifica_cinquina_riga`, `verifica_cartella_completa`

---

### FASE 2 — Dominio: integrazione nel ciclo di turno di Partita

**File**: `bingo_game/partita.py`

#### Task 2.1 — Aggiungere la fase Bot in `esegui_turno()`

Modificare `esegui_turno()` inserendo **una nuova fase** tra l'aggiornamento dei giocatori
e la chiamata a `verifica_premi()`.

**Flusso esteso di `esegui_turno()`**:

```
STEP 1: controllo stato in_corso               ← invariato
STEP 2: estrai_prossimo_numero()               ← invariato
         └─ aggiorna_giocatori_con_numero()    ← invariato
STEP 3: [NUOVO] fase reclami bot
         └─ per ogni GiocatoreAutomatico:
              reclamo = bot._valuta_potenziale_reclamo(self.premi_gia_assegnati)
              se reclamo: bot.reclamo_turno = reclamo
STEP 4: verifica_premi()                       ← invariato
STEP 5: [NUOVO] confronto reclami vs premi reali
         └─ per ogni bot con reclamo_turno valorizzato:
              controllare se il reclamo matcha un evento in premi_nuovi
              costruire struttura esito: {nome_bot, reclamo, successo: bool}
              aggiungere a lista reclami_bot
STEP 6: [NUOVO] reset reclami bot
         └─ per ogni GiocatoreAutomatico: bot.reset_reclamo_turno()
STEP 7: has_tombola() / termina_partita()      ← invariato
STEP 8: costruzione dizionario risultato       ← esteso con chiave "reclami_bot"
```

#### Task 2.2 — Aggiungere chiave `reclami_bot` al dizionario risultato

Il dizionario restituito da `esegui_turno()` viene arricchito con una chiave nuova
che non rompe nessun consumer esistente (backward-compatible):

```python
risultato_turno = {
    "numero_estratto": ...,           # invariato
    "stato_partita_prima": ...,       # invariato
    "stato_partita_dopo": ...,        # invariato
    "tombola_rilevata": ...,          # invariato
    "partita_terminata": ...,         # invariato
    "premi_nuovi": ...,               # invariato
    "reclami_bot": [                  # NUOVO — lista vuota se nessun bot ha reclamato
        {
            "nome_giocatore": str,    # nome del bot
            "id_giocatore": int,      # id del bot
            "reclamo": ReclamoVittoria,  # oggetto reclamo costruito dal bot
            "successo": bool          # True se il reclamo coincide con un premio reale
        },
        ...
    ]
}
```

**Regola di matching reclamo → premio reale**:
Un reclamo bot ha `successo=True` se esiste almeno un elemento in `premi_nuovi` tale che:
- `evento["cartella"] == reclamo.indice_cartella`
- `evento["premio"] == reclamo.tipo`
- `evento["riga"] == reclamo.indice_riga` (o entrambi None per tombola)

#### Task 2.3 — Import di GiocatoreAutomatico in partita.py

Attualmente `partita.py` lavora con `GiocatoreBase` e non distingue il tipo.
Per la fase Bot occorre filtrare solo i `GiocatoreAutomatico`.

**Strategia consigliata** (per evitare import circolari): usare `isinstance()` con
import protetto da `TYPE_CHECKING`, oppure aggiungere un metodo astratto/flag
`is_automatico()` in `GiocatoreBase` che `GiocatoreAutomatico` sovrascrive con `True`.
**Decidere la strategia prima di scrivere il codice.**

---

### FASE 3 — Controller: logging dei reclami bot

**File**: `bingo_game/game_controller.py`

#### Task 3.1 — Leggere `reclami_bot` in `esegui_turno_sicuro()`

Dopo aver ricevuto il dizionario risultato da `Partita.esegui_turno()`, aggiungere
la lettura opzionale della nuova chiave:

```
per ogni reclamo in risultato.get("reclami_bot", []):
  se reclamo["successo"] è True:
    log su tombola_stark.prizes:
      "[PRIZE] Bot '%s' (id=%d) dichiara %s — cartella=%d, riga=%s → ACCETTATO"
  altrimenti:
    log su tombola_stark.game:
      "[GAME]  Bot '%s' (id=%d) dichiara %s — cartella=%d, riga=%s → RIGETTATO"
```

**Nota**: il logging usa il pattern `_log_safe()` già esistente nel controller
(wrap silenzioso in try/except) per non interrompere mai il flusso di gioco.

#### Task 3.2 — Preparare struttura per il livello UI (futuro)

Il controller può già preparare (nel dizionario risultato che espone verso l'interfaccia)
una chiave `messaggi_reclami_bot` con le stringhe strutturate pronte per la vocalizzazione TTS.
**Questa task è opzionale nella prima release** e può essere implementata quando
lo strato `bingo_game/ui/` sarà attivo.

---

## 🧪 Test da implementare

### Test unitari — GiocatoreAutomatico

| Test | Scenario | Atteso |
|---|---|---|
| `test_bot_reclama_ambo_disponibile` | Cartella con ambo in riga 0, premio non ancora assegnato | Reclamo con tipo=ambo, cartella e riga corretti |
| `test_bot_non_reclama_premio_gia_assegnato` | Ambo in riga 0 già presente in `premi_gia_assegnati` | Return None |
| `test_bot_sceglie_premio_piu_alto` | Stessa cartella ha ambo E terno sulla stessa riga | Reclamo con tipo=terno |
| `test_bot_reclama_tombola` | Cartella completata, tombola non assegnata | Reclamo con tipo=tombola, indice_riga=None |
| `test_bot_nessun_premio_disponibile` | Tutte le chiavi già in `premi_gia_assegnati` | Return None |
| `test_bot_sceglie_tra_piu_cartelle` | Due cartelle: una con ambo, una con cinquina | Reclamo con tipo=cinquina |

### Test di integrazione — Partita

| Test | Scenario | Atteso |
|---|---|---|
| `test_partita_reclami_bot_nel_risultato` | Turno in cui un bot fa ambo | `reclami_bot` contiene un elemento con `successo=True` |
| `test_reclamo_bot_rigettato_premio_gia_preso` | Due bot in gara per lo stesso ambo: il secondo perde | Il secondo bot ha `successo=False` in `reclami_bot` |
| `test_bot_tombola_termina_partita` | Bot completa la cartella | `tombola_rilevata=True`, `partita_terminata=True` |
| `test_reclami_bot_vuoto_se_nessun_premio` | Turno senza nessun premio conseguito | `reclami_bot` è lista vuota |
| `test_reset_reclamo_dopo_turno` | Dopo il turno, `reclamo_turno` di tutti i bot è None | Verifica stato interno dei bot |

---

## 📝 Aggiornamenti documentazione

### API.md

- Aggiungere sezione `GiocatoreAutomatico` → descrivere il nuovo comportamento
  "proattivo" introdotto con Bot Attivo.
- Aggiungere chiave `reclami_bot` al contratto del dizionario restituito da `Partita.esegui_turno()`.

### ARCHITECTURE.md

- Aggiornare il diagramma "Flusso Tipico: Esecuzione di un Turno" (sezione "Flusso dei Dati")
  aggiungendo il nuovo STEP 3 (fase reclami bot) e STEP 5 (confronto esiti).
- Aggiornare la versione del documento a v0.6.0.

### README.md

- Aggiornare la descrizione funzionale delle partite: i bot reclamano automaticamente
  i premi conseguiti, e questi reclami vengono annunciati tramite il sistema di logging
  e (in futuro) vocalizzati dallo strato UI/TTS.

---

## ⚠️ Decisione aperta prima di avviare il codice

> **Strategia di type-checking in `partita.py`**
>
> Per distinguere i `GiocatoreAutomatico` dai giocatori umani all'interno di `esegui_turno()`,
> sono possibili due approcci:
>
> **Opzione A** – `isinstance(giocatore, GiocatoreAutomatico)` con import protetto da `TYPE_CHECKING`
> - Pro: Pythonic, nessuna modifica all'API di `GiocatoreBase`.
> - Contro: introduce una dipendenza diretta da `GiocatoreAutomatico` in `partita.py`.
>
> **Opzione B** – Aggiungere metodo `is_automatico() -> bool` in `GiocatoreBase`
> (default `False`), sovrascritto a `True` in `GiocatoreAutomatico`
> - Pro: nessun import diretto di sottoclasse, più estensibile.
> - Contro: aggiunge un metodo a `GiocatoreBase` solo per questa feature.
>
> **Raccomandazione**: Opzione B, in linea con il pattern "programma verso l'interfaccia"
> già usato nel progetto. Da confermare prima di iniziare FASE 2.

---

## 📊 Ordine consigliato di implementazione

```
1. [FASE 1]  GiocatoreBase.is_automatico()           → GiocatoreBase + GiocatoreAutomatico
2. [FASE 1]  GiocatoreAutomatico._valuta_potenziale_reclamo()
3. [TEST]    Test unitari su GiocatoreAutomatico     → STEP 1 completato e verificato
4. [FASE 2]  Estensione Partita.esegui_turno()
5. [TEST]    Test di integrazione su Partita
6. [FASE 3]  Logging in game_controller.py
7. [DOC]     Aggiornamento API.md, ARCHITECTURE.md, README.md
```

---

## 🔗 Riferimenti

- `documentations/ARCHITECTURE.md` – Architettura a livelli e regole di dipendenza
- `documentations/API.md` – Contratti API pubblici di tutte le classi
- `bingo_game/events/eventi_partita.py` – Definizione di `ReclamoVittoria`, `EventoFineTurno`
- `bingo_game/partita.py` – Implementazione corrente di `esegui_turno()`, `verifica_premi()`
- `bingo_game/players/giocatore_base.py` – `reclamo_turno`, `reset_reclamo_turno()`
- `bingo_game/players/giocatore_automatico.py` – Classe da estendere

---

*Documento vivente — aggiornare ad ogni cambiamento di piano significativo.*
*Versione piano: 1.0.0 — 2026-02-19*
