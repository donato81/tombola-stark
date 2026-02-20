# 📚 API.md - Tombola Stark

> **Riferimento API pubblico per tombola-stark**  
> Versione: v0.8.0  
> Ultimo aggiornamento: 2026-02-20

---

## 📋 Scopo del Documento

Questo documento fornisce la **guida di riferimento alle API pubbliche** tra i livelli del sistema.
L'obiettivo è documentare le interfacce che altri livelli o componenti chiamano, non i dettagli implementativi interni.

**Target**:
- Sviluppatori che lavorano tra i livelli (Dominio ↔ Controller ↔ Interfaccia)
- Manutentori che necessitano dei contratti API senza leggere il sorgente completo
- Assistenti AI (Copilot) per suggerire utilizzi corretti
- Il futuro te stesso che ricorderà come i componenti interagiscono

**Cosa c'è qui**:
- Metodi pubblici delle classi principali (Tabellone, Cartella, Partita, Giocatori, GameController)
- Firme dei metodi con parametri, tipi di ritorno ed esempi
- Gerarchia delle eccezioni personalizzate
- Pattern di naming e gestione degli errori
- Esempi di utilizzo reali

**Cosa NON c'è qui**:
- Metodi privati/interni (prefissati con `_`)
- Dettagli implementativi (vedere codice sorgente)
- Architettura (vedere `ARCHITECTURE.md`)
- Handler UI specifici

**Filosofia**: *"Se non viene chiamato da altri livelli, non viene documentato qui."*

---

## 🗂️ Indice Rapido

### Per Modulo

**Motore di Gioco** (`bingo_game/`):
- [Tabellone](#tabellone) – Gestione estrazioni numeri 1-90
- [Cartella](#cartella) – Cartella giocatore e verifica premi
- [Partita](#partita) – Coordinamento partita (tabellone + giocatori)
- [GiocatoreBase](#giocatorebase) – Classe base comune a tutti i giocatori
- [GiocatoreUmano](#giocatoreumano) – Giocatore umano
- [GiocatoreAutomatico](#giocatoreautomatico) – Bot automatico

**Controller** (`bingo_game/game_controller.py`):
- [game_controller](#game_controller) – Funzioni di orchestrazione di alto livello

**Eccezioni** (`bingo_game/exceptions/`):
- [Eccezioni Partita](#eccezioni-partita)
- [Eccezioni Giocatore](#eccezioni-giocatore)
- [Eccezioni Controller](#eccezioni-controller)

---

## 🏗️ Livello Dominio

### Tabellone

**File**: `bingo_game/tabellone.py`

**Scopo**: Gestisce il tabellone della tombola italiana (numeri da 1 a 90). Tiene traccia dei numeri disponibili, estratti e dello storico delle estrazioni.

**Costruttore**:
```python
Tabellone()
```
Nessun parametro. Inizializza automaticamente i numeri da 1 a 90 come disponibili.

**Esempio**:
```python
tabellone = Tabellone()
numero = tabellone.estrai_numero()  # Estrae un numero casuale tra 1 e 90
```

---

#### estrai_numero()

```python
def estrai_numero() -> int:
```

**Scopo**: Estrae un numero casuale tra quelli ancora disponibili, aggiorna lo stato interno e lo storico.

**Parametri**: Nessuno

**Ritorna**:
- `int`: Il numero estratto (tra 1 e 90)

**Side Effects**:
- Rimuove il numero da `numeri_disponibili`
- Aggiunge il numero a `numeri_estratti`
- Aggiorna `ultimo_numero_estratto`
- Appende il numero a `storico_estrazioni`

**Raises**:
- `ValueError`: Se tutti i numeri sono già stati estratti

**Esempio**:
```python
tabellone = Tabellone()
n = tabellone.estrai_numero()
print(f"Estratto: {n}")
```

---

#### is_numero_estratto()

```python
def is_numero_estratto(numero: int) -> bool:
```

**Scopo**: Verifica se un numero è già stato estratto.

**Parametri**:
- `numero` (int): Il numero da verificare

**Ritorna**:
- `bool`: `True` se il numero è già stato estratto, `False` altrimenti

**Esempio**:
```python
if tabellone.is_numero_estratto(45):
    print("45 già uscito!")
```

---

#### reset_tabellone()

```python
def reset_tabellone() -> None:
```

**Scopo**: Reinizializza completamente il tabellone (tutti i numeri tornano disponibili).

**Side Effects**: Azzera `numeri_estratti`, `storico_estrazioni`, `ultimo_numero_estratto`.

---

#### numeri_terminati()

```python
def numeri_terminati() -> bool:
```

**Ritorna**:
- `bool`: `True` se non ci sono più numeri disponibili

---

#### get_conteggio_estratti()

```python
def get_conteggio_estratti() -> int:
```

**Ritorna**:
- `int`: Numero di estrazioni effettuate (0–90)

---

#### get_conteggio_disponibili()

```python
def get_conteggio_disponibili() -> int:
```

**Ritorna**:
- `int`: Numero di numeri ancora da estrarre (0–90)

---

#### get_numeri_estratti()

```python
def get_numeri_estratti() -> List[int]:
```

**Ritorna**:
- `List[int]`: Lista ordinata dei numeri estratti finora

---

#### get_numeri_disponibili()

```python
def get_numeri_disponibili() -> List[int]:
```

**Ritorna**:
- `List[int]`: Lista ordinata dei numeri ancora disponibili

---

#### get_percentuale_avanzamento()

```python
def get_percentuale_avanzamento() -> float:
```

**Ritorna**:
- `float`: Percentuale di numeri estratti (0.0–100.0), arrotondata a un decimale

**Formula**: `(numeri_estratti / 90) * 100`

---

#### get_ultimo_numero_estratto()

```python
def get_ultimo_numero_estratto() -> Optional[int]:
```

**Ritorna**:
- `int`: Ultimo numero estratto in ordine temporale
- `None`: Se non è ancora stata effettuata alcuna estrazione

---

#### get_ultimi_numeri_estratti()

```python
def get_ultimi_numeri_estratti(n: int = 5) -> tuple[int, ...]:
```

**Parametri**:
- `n` (int): Quanti numeri recenti ritornare. Default: 5. Deve essere > 0.

**Ritorna**:
- `tuple[int, ...]`: Tupla immutabile con gli ultimi N numeri estratti in ordine temporale

**Raises**:
- `ValueError`: Se `n` non è intero o se `n <= 0`

---

#### get_stato_tabellone()

```python
def get_stato_tabellone() -> dict:
```

**Scopo**: Fotografia completa dello stato del tabellone, pronta per l'interfaccia.

**Ritorna**:
- `dict` con chiavi:
  - `totale_numeri` (int): sempre 90
  - `numeri_estratti` (int): quanti ne sono usciti
  - `numeri_disponibili` (int): quanti restano
  - `ultimi_numeri_estratti` (tuple): ultimi 5 estratti
  - `ultimo_numero_estratto` (int | None): l'ultimo uscito
  - `percentuale_avanzamento` (float): % completamento

**Esempio**:
```python
stato = tabellone.get_stato_tabellone()
print(f"Avanzamento: {stato['percentuale_avanzamento']}%")
print(f"Ultimo numero: {stato['ultimo_numero_estratto']}")
```

---

### Cartella

**File**: `bingo_game/cartella.py`

**Scopo**: Rappresenta una cartella della tombola (3 righe × 5 numeri = 15 numeri totali). Gestisce la marcatura dei numeri e la verifica dei premi (ambo, terno, quaterna, cinquina, tombola).

**Costruttore**:
```python
Cartella()
```
Genera automaticamente 15 numeri casuali organizzati in 3 righe da 5. Gli attributi `nome` e `indice` vengono assegnati da `GiocatoreBase.aggiungi_cartella()`.

**Attributi pubblici**:
- `nome` (str | None): Nome descrittivo assegnato dal giocatore
- `indice` (int | None): ID univoco assegnato dal giocatore

---

#### segna_numero()

```python
def segna_numero(numero: int) -> None:
```

**Scopo**: Segna un numero sulla cartella se presente.

**Parametri**:
- `numero` (int): Il numero da segnare (1–90)

---

#### verifica_ambo_riga()

```python
def verifica_ambo_riga(riga: int) -> bool:
```

**Parametri**:
- `riga` (int): Indice della riga (0, 1 o 2)

**Ritorna**:
- `bool`: `True` se almeno 2 numeri della riga sono stati segnati

---

#### verifica_terno_riga()

```python
def verifica_terno_riga(riga: int) -> bool:
```

**Ritorna**: `True` se almeno 3 numeri della riga sono segnati

---

#### verifica_quaterna_riga()

```python
def verifica_quaterna_riga(riga: int) -> bool:
```

**Ritorna**: `True` se almeno 4 numeri della riga sono segnati

---

#### verifica_cinquina_riga()

```python
def verifica_cinquina_riga(riga: int) -> bool:
```

**Ritorna**: `True` se tutti e 5 i numeri della riga sono segnati

---

#### verifica_cartella_completa()

```python
def verifica_cartella_completa() -> bool:
```

**Scopo**: Verifica se tutti i 15 numeri della cartella sono stati segnati (tombola).

**Ritorna**:
- `bool`: `True` se la cartella è completa

---

#### get_stato_cartella()

```python
def get_stato_cartella() -> dict:
```

**Scopo**: Ritorna una rappresentazione serializzabile dello stato della cartella.

**Ritorna**:
- `dict`: Stato completo della cartella (numeri segnati, righe, premi, ecc.)

---

### Partita

**File**: `bingo_game/partita.py`

**Scopo**: Coordina l'intera partita di tombola/bingo. Gestisce il tabellone, i giocatori, il ciclo delle estrazioni, la verifica dei premi e la determinazione di fine partita.

**Costanti di classe**:
- `MIN_GIOCATORI = 2`
- `MAX_GIOCATORI = 8`

**Costruttore**:
```python
Partita(tabellone: Tabellone, giocatori: Optional[List[GiocatoreBase]] = None)
```

**Parametri**:
- `tabellone` (Tabellone): Il tabellone da usare per le estrazioni
- `giocatori` (Optional[List[GiocatoreBase]]): Lista opzionale di giocatori già configurati

**Stato iniziale**: `"non_iniziata"`

**Esempio**:
```python
tabellone = Tabellone()
giocatori = [GiocatoreUmano("Mario"), GiocatoreAutomatico("Bot 1")]
partita = Partita(tabellone, giocatori)
```

---

#### get_giocatori()

```python
def get_giocatori() -> List[GiocatoreBase]:
```

**Ritorna**: La lista interna dei giocatori registrati

---

#### get_numero_giocatori()

```python
def get_numero_giocatori() -> int:
```

**Ritorna**: Numero totale di giocatori registrati

---

#### get_stato_partita()

```python
def get_stato_partita() -> str:
```

**Ritorna**:
- `"non_iniziata"`: Creata ma non avviata
- `"in_corso"`: Estrazioni in corso
- `"terminata"`: Partita conclusa (tombola o numeri esauriti)

---

#### is_pronta_per_iniziare()

```python
def is_pronta_per_iniziare() -> bool:
```

**Ritorna**: `True` se ci sono almeno `MIN_GIOCATORI` giocatori E stato è `"non_iniziata"`

---

#### aggiungi_giocatore()

```python
def aggiungi_giocatore(giocatore: GiocatoreBase) -> None:
```

**Raises**:
- `PartitaGiaIniziataException`: Se la partita non è in `"non_iniziata"`
- `PartitaGiocatoreTypeException`: Se l'oggetto non è `GiocatoreBase`
- `PartitaGiocatoreGiaPresenteException`: Se il giocatore è già nella lista
- `PartitaRosterPienoException`: Se si supera `MAX_GIOCATORI`

---

#### avvia_partita()

```python
def avvia_partita() -> None:
```

**Scopo**: Porta la partita dallo stato `"non_iniziata"` a `"in_corso"`.

**Raises**:
- `PartitaGiaIniziataException`: Se la partita non è in `"non_iniziata"`
- `PartitaGiocatoriInsufficientiException`: Se i giocatori sono meno di `MIN_GIOCATORI`

---

#### termina_partita()

```python
def termina_partita() -> str:
```

**Ritorna**: `"terminata"` (lo stato aggiornato)

**Raises**:
- `PartitaGiaTerminataException`: Se la partita è già terminata

---

#### estrai_prossimo_numero()

```python
def estrai_prossimo_numero() -> int:
```

**Scopo**: Estrae il prossimo numero dal tabellone, aggiorna `ultimo_numero_estratto` e notifica tutti i giocatori.

**Ritorna**:
- `int`: Il numero estratto

**Raises**:
- `PartitaNonInCorsoException`: Se la partita non è in `"in_corso"`
- `PartitaNumeriEsauritiException`: Se il tabellone ha esaurito tutti i numeri

---

#### aggiorna_giocatori_con_numero()

```python
def aggiorna_giocatori_con_numero(numero: int) -> None:
```

**Scopo**: Propaga un numero estratto a tutti i giocatori.

**Raises**:
- `PartitaNonInCorsoException`: Se la partita non è in `"in_corso"`

---

#### get_ultimo_numero_estratto()

```python
def get_ultimo_numero_estratto() -> Optional[int]:
```

**Ritorna**: L'ultimo numero estratto, oppure `None` se nessuna estrazione è avvenuta

---

#### verifica_premi_per_cartella()

```python
def verifica_premi_per_cartella(cartella: Cartella) -> Dict[str, Any]:
```

**Scopo**: Analizza una singola cartella e ritorna tutti i premi conseguiti.

**Ritorna**:
```python
{
    "tombola": bool,
    "righe": {
        0: {"ambo": bool, "terno": bool, "quaterna": bool, "cinquina": bool},
        1: {"ambo": bool, "terno": bool, "quaterna": bool, "cinquina": bool},
        2: {"ambo": bool, "terno": bool, "quaterna": bool, "cinquina": bool},
    }
}
```

---

#### verifica_premi()

```python
def verifica_premi() -> List[Dict[str, Any]]:
```

**Scopo**: Scansiona tutti i giocatori e le loro cartelle, ritorna solo i **nuovi** premi rispetto ai turni precedenti.

**Ritorna**:
- `List[dict]`: Lista di eventi di vincita. Ogni evento ha la forma:
```python
{
    "giocatore": str,        # nome del giocatore
    "id_giocatore": int | None,  # id del giocatore (v0.6.0+, per matching robusto)
    "cartella": int,         # indice della cartella
    "premio": str,           # "ambo" | "terno" | "quaterna" | "cinquina" | "tombola"
    "riga": int | None       # indice riga (0-2), None per tombola
}
```

**Nota (v0.6.0+)**: Il campo `id_giocatore` è stato aggiunto per consentire un matching robusto 
tra reclami bot e premi reali, anche quando più giocatori hanno lo stesso nome.

---

#### has_tombola()

```python
def has_tombola() -> bool:
```

**Ritorna**: `True` se almeno un giocatore ha completato una cartella (tombola)

---

#### esegui_turno()

```python
def esegui_turno() -> dict[str, Any]:
```

**Scopo**: Esegue un singolo passo del ciclo di gioco: estrazione + aggiornamento giocatori + verifica premi + eventuale fine partita.

**Flusso (v0.6.0+)**:
1. Estrae numero dal tabellone e aggiorna giocatori
2. **[NUOVO v0.6.0]** I bot valutano autonomamente i premi e costruiscono reclami
3. Verifica premi ufficiale (rimane l'unico arbitro)
4. **[NUOVO v0.6.0]** Confronta reclami bot con premi reali e costruisce esiti
5. **[NUOVO v0.6.0]** Reset reclami bot per il turno successivo
6. Verifica tombola e eventuale fine partita

**Ritorna**:
```python
{
    "numero_estratto": int,
    "stato_partita_prima": str,
    "stato_partita_dopo": str,
    "tombola_rilevata": bool,
    "partita_terminata": bool,
    "premi_nuovi": List[dict],
    "reclami_bot": List[dict]  # v0.6.0+ - Lista esiti reclami bot
}
```

**Struttura `reclami_bot` (v0.6.0+)**:
```python
[
    {
        "nome_giocatore": str,          # Nome del bot
        "id_giocatore": int | None,     # ID del bot
        "reclamo": ReclamoVittoria,     # Oggetto reclamo costruito dal bot
        "successo": bool                # True se il reclamo coincide con un premio reale
    },
    ...
]
```

**Note**:
- La chiave `reclami_bot` è **backward-compatible**: è sempre presente (lista vuota se nessun bot o nessun reclamo)
- I reclami bot sono una sovrastruttura UX/log: `verifica_premi()` rimane l'unico arbitro dei premi reali
- Un reclamo può avere `successo=False` se il premio è già stato assegnato ad altro giocatore nello stesso turno

**Raises**:
- `PartitaNonInCorsoException`: Se la partita non è in `"in_corso"`
- `PartitaNumeriEsauritiException`: Se il tabellone è esaurito

**Versione**:
- v0.1.0: Implementazione iniziale
- v0.6.0: Aggiunta chiave `reclami_bot` e fase reclami bot nel ciclo di turno

---

#### is_terminata()

```python
def is_terminata() -> bool:
```

**Ritorna**: `True` se `stato_partita == "terminata"`

---

#### get_stato_giocatori()

```python
def get_stato_giocatori() -> List[Dict[str, Any]]:
```

**Ritorna**: Lista di dizionari, uno per giocatore:
```python
{
    "nome": str,
    "id": int | None,
    "num_cartelle": int,
    "ha_tombola": bool
}
```

---

#### get_stato_completo()

```python
def get_stato_completo() -> Dict[str, Any]:
```

**Scopo**: Fotografia completa della partita per l'interfaccia o per il salvataggio.

**Ritorna**:
```python
{
    "stato_partita": str,
    "ultimo_numero_estratto": int | None,
    "numeri_estratti": List[int],
    "giocatori": List[dict],
    "premi_gia_assegnati": List[str]
}
```

---

### GiocatoreBase

**File**: `bingo_game/players/giocatore_base.py`

**Scopo**: Classe base comune a `GiocatoreUmano` e `GiocatoreAutomatico`. Gestisce identità, cartelle e aggiornamenti.

**Costruttore**:
```python
GiocatoreBase(nome: str, id_giocatore: Optional[int] = None)
```

**Raises**:
- `GiocatoreNomeTypeException`: Se `nome` non è `str`
- `GiocatoreNomeValueException`: Se `nome` è vuoto o solo spazi
- `GiocatoreIdTypeException`: Se `id_giocatore` non è `int` o `None`

---

#### get_nome()

```python
def get_nome() -> str:
```

**Ritorna**: Il nome del giocatore

---

#### get_id_giocatore()

```python
def get_id_giocatore() -> Optional[int]:
```

**Ritorna**: L'ID del giocatore (può essere `None`)

---

#### aggiungi_cartella()

```python
def aggiungi_cartella(cartella: Cartella) -> None:
```

**Scopo**: Aggiunge una cartella, assegnando nome (`"Cartella N"`) e indice progressivo.

**Raises**:
- `GiocatoreCartellaTypeException`: Se l'oggetto non è `Cartella`

---

#### get_cartelle()

```python
def get_cartelle() -> List[Cartella]:
```

**Ritorna**: Lista interna delle cartelle del giocatore

---

#### get_numero_cartelle()

```python
def get_numero_cartelle() -> int:
```

**Ritorna**: Numero totale di cartelle possedute

---

#### aggiorna_con_numero()

```python
def aggiorna_con_numero(numero: int) -> None:
```

**Scopo**: Chiama `cartella.segna_numero(numero)` su tutte le cartelle del giocatore.

**Raises**:
- `GiocatoreNumeroTypeException`: Se `numero` non è `int`
- `GiocatoreNumeroValueException`: Se `numero` non è nel range 1–90

---

#### get_stato_cartelle()

```python
def get_stato_cartelle() -> List[dict]:
```

**Ritorna**: Lista di dizionari `get_stato_cartella()` per ogni cartella

---

#### has_tombola()

```python
def has_tombola() -> bool:
```

**Ritorna**: `True` se almeno una cartella ha `verifica_cartella_completa() == True`

---

#### reset_reclamo_turno()

```python
def reset_reclamo_turno() -> None:
```

**Scopo**: Azzera `reclamo_turno` dopo che la Partita ha processato il turno.

---

#### is_automatico()

```python
def is_automatico() -> bool:
```

**Scopo**: Indica se il giocatore è un bot automatico.

**Ritorna**:
- `bool`: `False` per `GiocatoreBase` e `GiocatoreUmano`, `True` per `GiocatoreAutomatico`

**Nota**: Questo metodo permette a `Partita` di distinguere i bot dai giocatori umani
mantenendo il pattern "programma verso l'interfaccia", evitando l'uso di `isinstance()`.

**Versione**: v0.6.0+

---

### GiocatoreUmano

**File**: `bingo_game/players/giocatore_umano.py`

**Scopo**: Specializzazione di `GiocatoreBase` per il giocatore umano. Espone metodi per la gestione dell'interazione con l'interfaccia tramite il sistema di eventi.

**Costruttore**:
```python
GiocatoreUmano(nome: str, id_giocatore: Optional[int] = None)
```

---

### GiocatoreAutomatico

**File**: `bingo_game/players/giocatore_automatico.py`

**Scopo**: Bot di gioco. Eredita da `GiocatoreBase`, non richiede interazione umana.

**Funzionalità Bot Attivo (v0.6.0+)**: A partire dalla versione 0.6.0, il bot valuta autonomamente 
i premi conseguiti sulle proprie cartelle dopo ogni estrazione e li dichiara alla Partita tramite 
un `ReclamoVittoria`, esattamente come farebbe un giocatore umano.

**Costruttore**:
```python
GiocatoreAutomatico(nome: str, id_giocatore: Optional[int] = None)
```

---

#### is_automatico()

```python
def is_automatico() -> bool:
```

**Scopo**: Indica che questo giocatore è un bot automatico.

**Ritorna**:
- `bool`: Sempre `True` per `GiocatoreAutomatico`

**Nota**: Override di `GiocatoreBase.is_automatico()`. Permette a `Partita` di distinguere 
i bot dai giocatori umani senza usare `isinstance()`.

**Versione**: v0.6.0+

---

#### _valuta_potenziale_reclamo()

```python
def _valuta_potenziale_reclamo(premi_gia_assegnati: set[str]) -> Optional[ReclamoVittoria]:
```

**Scopo**: Valuta se il bot può reclamare un premio in base allo stato attuale delle sue cartelle.
Questo è un **metodo interno** (prefissato con `_`), non fa parte dell'API pubblica.

**Parametri**:
- `premi_gia_assegnati` (set[str]): Snapshot dei premi già assegnati nei turni precedenti.
  Formato chiavi: `"cartella_{idx}_tombola"` o `"cartella_{idx}_riga_{r}_{tipo}"`

**Ritorna**:
- `ReclamoVittoria`: Il reclamo del premio di rango più alto trovato
- `None`: Se nessun premio è reclamabile (tutti già assegnati o nessuno disponibile)

**Algoritmo**:
1. Analizza tutte le cartelle del bot
2. Per ogni cartella, verifica tombola e premi di riga (cinquina, quaterna, terno, ambo)
3. Seleziona il premio di rango più alto secondo la gerarchia: tombola > cinquina > quaterna > terno > ambo
4. Esclude premi già presenti in `premi_gia_assegnati`
5. Ritorna il miglior reclamo disponibile

**Nota**: Il metodo non modifica lo stato del bot. La validazione finale del reclamo è sempre
demandata a `Partita.verifica_premi()`, che rimane l'unico arbitro dei premi reali.

**Versione**: v0.6.0+

**Esempio**:
```python
# All'interno di Partita.esegui_turno()
for giocatore in self.giocatori:
    if giocatore.is_automatico():
        reclamo = giocatore._valuta_potenziale_reclamo(self.premi_gia_assegnati)
        if reclamo is not None:
            giocatore.reclamo_turno = reclamo
```

---

## 🎮 Livello Controller

### game_controller

**File**: `bingo_game/game_controller.py`

**Scopo**: Funzioni di alto livello per orchestrare la creazione e il ciclo di una partita. Fa da collante tra motore di gioco e interfaccia, gestendo tutte le eccezioni in modo sicuro.

**Invariante v0.8.0**: Il controller non scrive **mai** su stdout. Tutta la comunicazione verso l'utente avviene tramite i valori di ritorno (`bool`, `dict`, `None`) che la TUI legge e vocalizza usando `MESSAGGI_CONTROLLER`.

---

#### crea_tabellone_standard()

```python
def crea_tabellone_standard() -> Tabellone:
```

**Ritorna**: Un'istanza `Tabellone` con numeri 1–90 tutti disponibili

---

#### assegna_cartelle_a_giocatore()

```python
def assegna_cartelle_a_giocatore(giocatore: GiocatoreBase, num_cartelle: int) -> None:
```

**Raises**:
- `ControllerCartelleNegativeException`: Se `num_cartelle < 0`

---

#### crea_giocatore_umano()

```python
def crea_giocatore_umano(
    nome: str,
    num_cartelle: int = 1,
    id_giocatore: Optional[int] = None
) -> GiocatoreUmano:
```

**Raises**:
- `ControllerNomeGiocatoreException`: Se `nome` è vuoto
- `ControllerCartelleNegativeException`: Se `num_cartelle < 0`

---

#### crea_giocatori_automatici()

```python
def crea_giocatori_automatici(num_bot: int = 1) -> List[GiocatoreAutomatico]:
```

**Parametri**:
- `num_bot` (int): Numero di bot da creare (0–7). Default: 1.

**Raises**:
- `ControllerBotNegativeException`: Se `num_bot < 0`
- `ControllerBotExcessException`: Se `num_bot > 7`

---

#### crea_partita_standard()

```python
def crea_partita_standard(
    nome_giocatore_umano: str = "Giocatore 1",
    num_cartelle_umano: int = 1,
    num_bot: int = 1
) -> Partita:
```

**Scopo**: Crea una partita completamente configurata e pronta da avviare.

**Ritorna**: `Partita` nello stato `"non_iniziata"` con tutti i giocatori configurati

**Note v0.8.0**: Scrive log DEBUG via `_logger_game` per ogni sotto-passo. Nessun output su stdout.

**Esempio**:
```python
partita = crea_partita_standard(
    nome_giocatore_umano="Lucia",
    num_cartelle_umano=2,
    num_bot=3
)
avvia_partita_sicura(partita)
```

---

#### avvia_partita_sicura()

```python
def avvia_partita_sicura(partita: Partita) -> bool:
```

**Ritorna**:
- `True`: Avvio riuscito, partita ora in `"in_corso"`
- `False`: Avvio fallito (giocatori insufficienti, partita già iniziata, ecc.)

**Note v0.8.0**: Fallimenti loggati a WARNING via `_logger_errors` con tipo eccezione. Nessun output su stdout. La TUI legge `False` e mostra `MESSAGGI_CONTROLLER[CTRL_AVVIO_FALLITO_GENERICO]`.

---

#### esegui_turno_sicuro()

```python
def esegui_turno_sicuro(partita: Partita) -> Optional[Dict[str, Any]]:
```

**Ritorna**:
- `Dict[str, Any]`: Dizionario risultato turno se successo
- `None`: Se errore (partita non in corso, parametro non valido, eccezione imprevista)

**Chiavi garantite**: `numero_estratto`, `stato_partita_prima`, `stato_partita_dopo`, `tombola_rilevata`, `partita_terminata`, `premi_nuovi`, `reclami_bot` (v0.6.0+)

**Note v0.8.0**: Premi loggati a INFO via `_logger_prizes`. Errori loggati a WARNING/ERROR via `_logger_errors`. Nessun output su stdout.

---

#### ottieni_stato_sintetico()

```python
def ottieni_stato_sintetico(partita: Partita) -> Dict[str, Any]:
```

**Ritorna**: Dict con chiavi: `stato_partita`, `ultimo_numero_estratto`, `numeri_estratti`, `giocatori`, `premi_gia_assegnati`

**Raises**:
- `ValueError`: Se il parametro non è un oggetto `Partita` valido o lo stato è incompleto.

**Note v0.8.0**: La TUI cattura `ValueError` tramite l'helper `_ottieni_stato_sicuro`. Nessun output su stdout.

---

#### ha_partita_tombola()

```python
def ha_partita_tombola(partita: Partita) -> bool:
```

**Ritorna**: `True` se almeno un giocatore ha tombola

**Note v0.8.0**: Scrive log DEBUG via `_logger_game`. Nessun output su stdout.

---

#### partita_terminata()

```python
def partita_terminata(partita: Partita) -> bool:
```

**Note v0.8.0**: Scrive log DEBUG via `_logger_game`. Nessun output su stdout.

**Esempio tipico d'uso**:
```python
while not partita_terminata(partita):
    turno = esegui_turno_sicuro(partita)
    if turno and turno["tombola_rilevata"]:
        # La TUI mostra il messaggio da MESSAGGI_CONTROLLER
        break
```

---

## 🔧 Riferimento Eccezioni

### Eccezioni Partita

**File**: `bingo_game/exceptions/partita_exceptions.py`

| Eccezione | Descrizione |
|-----------|-------------|
| `PartitaException` | Base di tutte le eccezioni di partita |
| `PartitaStatoException` | Stato della partita non valido |
| `PartitaGiaIniziataException` | Operazione non consentita su partita già avviata |
| `PartitaNonInCorsoException` | Operazione richiede stato `"in_corso"` |
| `PartitaGiaTerminataException` | Operazione su partita già terminata |
| `PartitaRosterException` | Errore generico sul roster |
| `PartitaRosterPienoException` | Superato `MAX_GIOCATORI` |
| `PartitaGiocatoriInsufficientiException` | Meno di `MIN_GIOCATORI` giocatori |
| `PartitaGiocatoreTypeException` | Oggetto non è `GiocatoreBase` |
| `PartitaGiocatoreGiaPresenteException` | Giocatore duplicato |
| `PartitaNumeriEsauritiException` | Tabellone esaurito |

### Eccezioni Giocatore

**File**: `bingo_game/exceptions/giocatore_exceptions.py`

| Eccezione | Descrizione |
|-----------|-------------|
| `GiocatoreNomeTypeException` | `nome` non è `str` |
| `GiocatoreNomeValueException` | `nome` è vuoto |
| `GiocatoreIdTypeException` | `id_giocatore` non è `int` o `None` |
| `GiocatoreCartellaTypeException` | Oggetto non è `Cartella` |
| `GiocatoreNumeroTypeException` | `numero` non è `int` |
| `GiocatoreNumeroValueException` | `numero` fuori range 1–90 |

### Eccezioni Controller

**File**: `bingo_game/exceptions/game_controller_exceptions.py`

| Eccezione | Descrizione |
|-----------|-------------|
| `ControllerNomeGiocatoreException` | Nome giocatore vuoto |
| `ControllerCartelleNegativeException` | `num_cartelle < 0` |
| `ControllerBotNegativeException` | `num_bot < 0` |
| `ControllerBotExcessException` | `num_bot > 7` |

---

## 🔧 Pattern Comuni

### Naming Conventions

- `get_*()` – Getter puro senza side effects
- `is_*()` / `has_*()` – Query booleana senza side effects
- `verifica_*()` – Controlla condizioni di gioco
- `crea_*()` – Factory, costruisce e ritorna un oggetto configurato
- `avvia_*()` / `esegui_*()` – Azioni con side effects sul dominio
- `ottieni_*()` – Ritorna snapshot dello stato validato

### Pattern di Gestione Errori

**Dominio** solleva eccezioni specifiche:
```python
if self.stato_partita != "in_corso":
    raise PartitaNonInCorsoException("...")
```

**Controller** intercetta e ritorna valore sicuro (v0.8.0 — senza print):
```python
try:
    partita.avvia_partita()
    return True
except PartitaGiocatoriInsufficientiException as exc:
    _log_safe(f"[GAME] Avvio fallito: tipo='{type(exc).__name__}'.", logging.WARNING, logger=_logger_errors)
    return False
```

**Interfaccia** mostra messaggio all'utente:
```python
if not avvia_partita_sicura(partita):
    print(MESSAGGI_CONTROLLER[CTRL_AVVIO_FALLITO_GENERICO])
```

---

## 📚 Gallery Esempi

### Esempio 1: Flusso Completo di una Partita

```python
from bingo_game.game_controller import (
    crea_partita_standard,
    avvia_partita_sicura,
    esegui_turno_sicuro,
    partita_terminata,
    ha_partita_tombola
)

partita = crea_partita_standard(
    nome_giocatore_umano="Lucia",
    num_cartelle_umano=2,
    num_bot=2
)

avvia_partita_sicura(partita)

while not partita_terminata(partita):
    turno = esegui_turno_sicuro(partita)
    if turno:
        print(f"Estratto: {turno['numero_estratto']}")
        for evento in turno["premi_nuovi"]:
            print(f"🎉 {evento['giocatore']} ha fatto {evento['premio']}!")
        for reclamo in turno.get("reclami_bot", []):
            stato = "✅" if reclamo["successo"] else "❌"
            print(f"{stato} {reclamo['nome_giocatore']} dichiara {reclamo['reclamo'].tipo}!")
        if turno["tombola_rilevata"]:
            print("🏆 TOMBOLA!")
```

---

### Esempio 2: Snapshot Stato per Screen Reader

```python
from bingo_game.game_controller import ottieni_stato_sintetico

stato = ottieni_stato_sintetico(partita)
print(f"Partita: {stato['stato_partita']}")
print(f"Ultimo estratto: {stato['ultimo_numero_estratto']}")
for g in stato['giocatori']:
    print(f"- {g['nome']}: {g['num_cartelle']} cartelle, tombola={g['ha_tombola']}")
```

---

### Esempio 3: Creazione Manuale dei Componenti

```python
from bingo_game.tabellone import Tabellone
from bingo_game.cartella import Cartella
from bingo_game.players import GiocatoreUmano, GiocatoreAutomatico
from bingo_game.partita import Partita

tabellone = Tabellone()
umano = GiocatoreUmano("Mario")
bot = GiocatoreAutomatico("Bot 1")

for _ in range(2):
    umano.aggiungi_cartella(Cartella())
bot.aggiungi_cartella(Cartella())

partita = Partita(tabellone, [umano, bot])
partita.avvia_partita()

risultato = partita.esegui_turno()
print(f"Turno: {risultato['numero_estratto']}, premi: {risultato['premi_nuovi']}")
```

---

## 🔧 Infrastruttura di Logging

### GameLogger

**File**: `bingo_game/logging/game_logger.py`

**Scopo**: Sistema di logging centralizzato per Tombola Stark. Fornisce un Singleton che scrive su un file cumulativo con flush immediato e marcatori di sessione. Supporta modalità normale (INFO+) e dettagliata (DEBUG+).

**Pattern**: Singleton - una sola istanza per l'intera applicazione.

**Architettura**: Il logger è un'infrastruttura trasversale (cross-cutting concern) accessibile solo dal Controller e dall'Interfaccia. Il Dominio NON importa mai il logger (ADR-001, ADR-003).

---

#### initialize()

```python
@classmethod
def initialize(cls, debug_mode: bool = False) -> None:
```

**Scopo**: Inizializza il sistema di logging. Deve essere chiamato una sola volta all'avvio dell'applicazione, prima di qualsiasi altra operazione di logging.

**Parametri**:
- `debug_mode` (`bool`, opzionale): Se `True`, imposta il livello a DEBUG (modalità dettagliata con log di ogni turno). Se `False` (default), imposta il livello a INFO (solo eventi significativi).

**Side Effects**:
- Crea la directory `logs/` se non esiste
- Configura un `FlushingFileHandler` che scrive su `logs/tombola_stark.log` in modalità append
- Ogni riga è scritta immediatamente su disco (flush dopo ogni `emit()`)
- Scrive un marcatore di sessione AVVIATA con timestamp

**Raises**: Nessuna eccezione. Chiamate successive sono idempotenti (noop).

**Esempio**:
```python
from bingo_game.logging import GameLogger

# All'avvio dell'applicazione
GameLogger.initialize(debug_mode=False)  # Modalità normale

# Oppure modalità debug
GameLogger.initialize(debug_mode=True)   # Modalità dettagliata
```

---

#### get_instance()

```python
@classmethod
def get_instance(cls) -> logging.Logger:
```

**Scopo**: Restituisce il logger configurato per scrivere eventi.

**Parametri**: Nessuno

**Ritorna**:
- `logging.Logger`: L'istanza del logger `tombola_stark` configurato

**Raises**:
- `RuntimeError`: Se `initialize()` non è stato ancora chiamato

**Esempio**:
```python
logger = GameLogger.get_instance()
logger.info("Partita avviata")
logger.debug("Turno #1 — estratto: 42")
```

**Note**: 
- Nel codice di produzione, usare sempre il pattern `_log_safe()` per evitare che errori di logging interrompano il gioco
- I sub-logger (`tombola_stark.game`, `tombola_stark.prizes`, `tombola_stark.system`, `tombola_stark.errors`) ereditano automaticamente la configurazione

---

#### shutdown()

```python
@classmethod
def shutdown(cls) -> None:
```

**Scopo**: Scrive il marcatore di chiusura sessione e chiude correttamente tutti gli handler.

**Parametri**: Nessuno

**Side Effects**:
- Scrive un messaggio INFO di chiusura
- Scrive un marcatore di sessione CHIUSA con timestamp
- Chiama `logging.shutdown()` per chiudere tutti gli handler
- Resetta lo stato interno

**Esempio**:
```python
try:
    GameLogger.initialize(debug_mode=args.debug)
    # ... logica di gioco ...
finally:
    GameLogger.shutdown()  # Assicura chiusura pulita
```

---

### Sub-Logger per Categoria

Il sistema di logging utilizza una gerarchia di sub-logger per organizzare gli eventi per categoria:

- `tombola_stark.game` — Eventi del ciclo di vita della partita (`[GAME]`)
- `tombola_stark.prizes` — Eventi di premi assegnati (`[PRIZE]`)
- `tombola_stark.system` — Eventi di sistema e configurazione (`[SYS]`)
- `tombola_stark.errors` — Eccezioni e anomalie (`[ERR]`)

**Esempio**:
```python
import logging

logger_game = logging.getLogger("tombola_stark.game")
logger_game.info("[GAME] Partita creata — giocatore='Mario', cartelle=2")

logger_prizes = logging.getLogger("tombola_stark.prizes")
logger_prizes.info("[PRIZE] AMBO — giocatore='Mario', cartella=1, riga=0")
```

---

### Formato Log File

Il file `logs/tombola_stark.log` usa il formato:

```
YYYY-MM-DD HH:MM:SS | LEVEL    | LOGGER_NAME           | MESSAGE
```

**Esempio**:
```
2026-02-18 19:54:47 | INFO     | tombola_stark.game    | [GAME] Partita creata — giocatore='Mario'
2026-02-18 19:54:48 | DEBUG    | tombola_stark.game    | [GAME] Turno #1 — estratto: 42, avanzamento: 1.1%
2026-02-18 19:54:49 | INFO     | tombola_stark.prizes  | [PRIZE] AMBO — giocatore='Mario', cartella=1
```

---

### Pattern _log_safe()

Il controller utilizza un helper privato `_log_safe()` che garantisce che il logging non interrompa mai il gioco:

```python
def _log_safe(message: str, level: str = "info", *args,
              logger: logging.Logger | None = None) -> None:
    """Scrive nel log senza mai propagare eccezioni al chiamante."""
    try:
        target = logger or GameLogger.get_instance()
        getattr(target, level)(message, *args)
    except Exception:
        pass  # Silenzioso in caso di errore
```

---

## 🖥️ Livello Interfaccia — TerminalUI

### Modulo: `bingo_game/ui/ui_terminale.py`

**Versione introdotta**: v0.7.0

### Classe `TerminalUI`

Interfaccia da terminale accessibile (screen reader NVDA/JAWS/Orca) per la configurazione pre-partita. Implementa una macchina a stati sequenziale A→E.

**Dipendenze**: `game_controller.crea_partita_standard`, `game_controller.avvia_partita_sicura`, `MESSAGGI_CONFIGURAZIONE`, `MESSAGGI_CONTROLLER` (v0.8.0+), costanti `CTRL_*` (v0.8.0+)  
**Nota**: unico metodo pubblico consumabile da `main.py` è `avvia()`.

#### Metodo pubblico

```python
def avvia(self) -> None
```

**Descrizione**: Avvia il flusso di configurazione completo della partita.  
**Side effects**: stampa i prompt e i messaggi su `stdout`; delega la creazione e l'avvio della partita al `GameController`.  
**Dipendenze**: `crea_partita_standard()` + `avvia_partita_sicura()` (two-step obbligatorio).  
**Logging**:
- `INFO` all'inizio del flusso e al completamento della configurazione
- `DEBUG` ad ogni transizione di stato (A→B→C→D→E) e dopo ogni strip/validazione
- `WARNING` per ogni errore di input (nome vuoto, nome troppo lungo, bot fuori range, cartelle fuori range, tipo non intero)

**Validazioni integrate**:
- Nome: `strip()` obbligatorio → non vuoto → max 15 caratteri
- Bot: `int()` richiesto → range 1–7
- Cartelle: `int()` richiesto → range 1–6 (scelta UX, non vincolo del Controller)

**Gestione fallimenti controller (v0.8.0+)**:
- Se `avvia_partita_sicura()` ritorna `False`: mostra `MESSAGGI_CONTROLLER[CTRL_AVVIO_FALLITO_GENERICO]`
- Se `ottieni_stato_sintetico()` solleva `ValueError`: catturato dall'helper `_ottieni_stato_sicuro`

**Esempio di utilizzo** (in `main.py`):

```python
from bingo_game.ui.ui_terminale import TerminalUI

tui = TerminalUI()
tui.avvia()
```

---

## 🔄 Note di Versione

- **v0.8.0** — Silent Controller: rimozione ~22 `print()` da `game_controller.py` (Gruppi A/B/C/D), sostituzione con `_log_safe()` sui sub-logger con prefissi `[GAME]`/`[ERR]`/`[SYS]`. Aggiunta `codici_controller.py` (4 costanti `CTRL_*`), `MESSAGGI_CONTROLLER` in `it.py` (4 voci localizzate), guardie TUI in `ui_terminale.py`. 15 nuovi test `capsys` in `test_silent_controller.py`.
- **v0.7.0** — TUI Start Menu Fase 1: `TerminalUI` con macchina a stati A→E, 9 costanti `Codici_Configurazione`, `MESSAGGI_CONFIGURAZIONE` in `it.py`, 8 unit test. Entry point `main.py` aggiornato.
- **v0.6.0** – Bot Attivo: `GiocatoreAutomatico` valuta autonomamente i premi e li dichiara tramite `ReclamoVittoria`. Nuova chiave `reclami_bot` in `Partita.esegui_turno()` (backward-compatible). Campo `id_giocatore` aggiunto agli eventi premio per matching robusto con nomi duplicati. Metodi `is_automatico()` e `reset_reclamo_turno()` documentati in `GiocatoreBase`.
- **v0.5.0** – Sistema di logging Fase 2: copertura completa eventi di gioco (18 eventi distinti), sub-logger per categoria, riepilogo finale partita
- **v0.4.0** – Sistema di logging Fase 1: GameLogger singleton, file cumulativo con flush immediato, marcatori di sessione, flag `--debug`
- **v0.1.0** – Rilascio iniziale: Tabellone, Cartella, GiocatoreBase, GiocatoreUmano, GiocatoreAutomatico, Partita, game_controller
- Gerarchia eccezioni personalizzate per tutti i moduli
- Sistema eventi (`bingo_game/events/`) per vocalizzazione UI e reclami di vittoria

---

*Ultimo aggiornamento: 2026-02-20 (v0.8.0)*
