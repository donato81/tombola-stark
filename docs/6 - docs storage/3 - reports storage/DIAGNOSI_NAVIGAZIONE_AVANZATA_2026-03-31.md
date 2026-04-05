# Diagnosi navigazione avanzata — Alt+Frecce

**Data**: 31 marzo 2026  
**Agente**: Agent-Analyze  
**Scope**: sola lettura — nessun file modificato

---

## Sintomo segnalato

Quando il giocatore usa Alt+Freccia (Su, Giù, Sinistra, Destra),
NVDA legge un testo identico a quello della navigazione semplice (Freccia senza
modificatore). La modalità "avanzata" risulta inudibile.

---

## File 1: `bingo_game/players/giocatore_umano.py`

### Metodi semplici

| Metodo | Riga | Evento prodotto | Payload chiave |
|--------|------|-----------------|----------------|
| `sposta_focus_riga_su_semplice` | 542 | `EventoNavigazioneRiga` | `riga_semplice` (9 celle int/`"-"`) |
| `sposta_focus_riga_giu_semplice` | 671 | `EventoNavigazioneRiga` | `riga_semplice` |
| `sposta_focus_colonna_sinistra` | 1041 | `EventoNavigazioneColonna` | `colonna_semplice` (3 celle int/`"-"`) |
| `sposta_focus_colonna_destra` | 1160 | `EventoNavigazioneColonna` | `colonna_semplice` |

### Metodi avanzati

| Metodo | Riga | Evento prodotto | Payload chiave |
|--------|------|-----------------|----------------|
| `sposta_focus_riga_su_avanzata` | 807 | `EventoNavigazioneRigaAvanzata` | `riga_semplice` + `stato_riga` + `numeri_segnati_riga_ordinati` |
| `sposta_focus_riga_giu_avanzata` | 916 | `EventoNavigazioneRigaAvanzata` | `riga_semplice` + `stato_riga` + `numeri_segnati_riga_ordinati` |
| `sposta_focus_colonna_sinistra_avanzata` | 1281 | `EventoNavigazioneColonnaAvanzata` | `colonna_semplice` + `stato_colonna` + `numeri_segnati_colonna_ordinati` |
| `sposta_focus_colonna_destra_avanzata` | 1403 | `EventoNavigazioneColonnaAvanzata` | `colonna_semplice` + `stato_colonna` + `numeri_segnati_colonna_ordinati` |

### Cosa fa concretamente in più la versione avanzata

I metodi avanzati chiamano `cartella_in_focus.get_dati_visualizzazione_riga_avanzata(indice)`
(o il corrispondente per colonna) che restituisce un pacchetto a tre elementi:

```python
# riga avanzata, linea ~852
dati_riga_avanzati = cartella_in_focus.get_dati_visualizzazione_riga_avanzata(nuova_riga)
# dati_riga_avanzati = (riga_semplice, stato_riga, numeri_segnati_riga_ordinati)
```

I metodi semplici chiamano invece solo `cartella_in_focus.get_riga_semplice(indice)`,
che restituisce le 9 celle senza stato di segnatura.

### Verdetto su giocatore_umano.py

**Nessun problema.** I messaggi semplice e avanzato sono costruiti su tipi evento
distinti (`EventoNavigazioneRiga` vs `EventoNavigazioneRigaAvanzata`). Il dominio
produce dati corretti e differenziati. Il livello applicativo è sano.

---

## File 2: `bingo_game/ui/renderers/renderer_wx.py`

### Dispatcher (righe ~179-225)

Il dispatcher distingue correttamente i due tipi:

```python
# riga ~193
elif isinstance(evento, EventoNavigazioneRiga):
    self._handle_navigazione_riga(evento)
elif isinstance(evento, EventoNavigazioneRigaAvanzata):
    self._handle_navigazione_riga_avanzata(evento)
```

Stessa logica per le colonne. I due tipi evento sono `@dataclass(frozen=True)` separati
senza relazioni di ereditarietà, quindi l'ordine `isinstance` non introduce rischi
di intercettazione prematura.

### Testi prodotti a confronto

#### Navigazione riga

**Handler semplice** (`_handle_navigazione_riga`, linea ~360):
```python
celle = "  ".join(self._formatta_cella(c) for c in (evento.riga_semplice or []))
testo = f"Riga {evento.numero_riga_corrente}: {celle}"
# Esempio: "Riga 2: vuoto  12  vuoto  vuoto  34  vuoto  67  vuoto  vuoto"
```

**Handler avanzato** (`_handle_navigazione_riga_avanzata`, linea ~374):
```python
segnati_set = set(evento.numeri_segnati_riga_ordinati or [])
celle = "  ".join(
    self._formatta_cella(c, evidenziata=isinstance(c, int) and c in segnati_set)
    for c in (evento.riga_semplice or [])
)
testo = f"Riga {evento.numero_riga_corrente} avanzata: {celle}"
# Esempio: "Riga 2 avanzata: vuoto  [12]  vuoto  vuoto  [34]  vuoto  67  vuoto  vuoto"
```

#### Navigazione colonna

**Handler semplice** (`_handle_navigazione_colonna`, linea ~413):
```python
testo = f"Colonna {evento.numero_colonna_corrente}: {celle}"
```

**Handler avanzato** (`_handle_navigazione_colonna_avanzata`, linea ~424):
```python
testo = f"Colonna {evento.numero_colonna_corrente} avanzata: {celle}"
```

### Dove si perde la differenza udibile

#### Problema A — parentesi quadre NVDA-inaudibili (CRITICO)

La differenza di contenuto tra semplice e avanzato si riduce alla notazione `[N]`
sui numeri segnati (`_formatta_cella` con `evidenziata=True`):

```python
# base_renderer.py → _formatta_cella
def _formatta_cella(self, cella: int | str, *, evidenziata: bool = False) -> str:
    if cella == "-":
        return self._formatta_testo_da_catalogo("UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA")
    testo = str(cella)
    if evidenziata:
        return f"[{testo}]"   # <-- parentesi quadre
    return testo
```

NVDA con profilo di punteggiatura impostato su "Qualcosa", "La maggior parte" o
"Nessuna" NON pronuncia le parentesi quadre. Il risultato è che `[12]` viene letto
esattamente come `12`. Questa è la differenza principale tra semplice e avanzato,
e risulta completamente inudibile.

#### Problema B — parola "avanzata" troncata da interrupt (SECONDARIO)

L'unica differenza verbale rimanente è la parola " avanzata" inserita nel prefisso
(es. "Riga 2 avanzata: ..."). Questa parola c'è, ma compare **dopo** il numero di riga
e **prima** del lungo elenco di celle. Con navigazione rapida (tasto premuto
ripetutamente), NVDA interrompe la lettura precedente a ogni nuova vocalizze.
Il testo viene pronunciato da sinistra: "Riga 2" viene sempre sentito, poi NVDA
viene quasi sempre interrotto prima di arrivare a " avanzata". In pratica la parola
distinguente sparisce nell'uso normale.

#### Riepilogo del percorso del testo verso NVDA

```
evento.riga_semplice + evento.numeri_segnati_riga_ordinati
     ↓
_handle_navigazione_riga_avanzata (renderer_wx.py, ~374)
     ↓
testo = "Riga N avanzata: [X]  Y  ..."
     ↓
_ao2_vocalizza(testo) → vocalizzatore.vocalizza_testo(testo) → AO2
     ↓
NVDA legge: "Riga N X Y ..."   ← parentesi quadre silenti, "avanzata" troncato
```

Il testo arriva **integralmente** ad AO2 senza filtri né troncamenti.
La perdita di informazione avviene a livello di lettura da parte di NVDA.

### Verdetto su renderer_wx.py

Il renderer riceve i dati corretti e costruisce testi nominalmente diversi.
Il problema non è un bug logico nel renderer, ma una **scelta di encoding visuale
(`[N]`) che NVDA rende inaudibile**. L'architettura testo→voce è funzionante,
ma il vocabolario usato per distinguere "segnato" da "non segnato" presuppone
che il sistema di lettura pronunci i delimitatori, ipotesi falsa con NVDA.

---

## File 3: `bingo_game/comandi_partita.py`

I quattro metodi avanzati della classe `ComandiGiocatoreUmano` delegano
correttamente ai metodi avanzati del giocatore:

```python
# Righe ~307-326 di comandi_partita.py
def riga_su_avanzata(self) -> EsitoAzione:
    return self._giocatore.sposta_focus_riga_su_avanzata()       # ✓ avanzata

def riga_giu_avanzata(self) -> EsitoAzione:
    return self._giocatore.sposta_focus_riga_giu_avanzata()      # ✓ avanzata

def colonna_sinistra_avanzata(self) -> EsitoAzione:
    return self._giocatore.sposta_focus_colonna_sinistra_avanzata()  # ✓ avanzata

def colonna_destra_avanzata(self) -> EsitoAzione:
    return self._giocatore.sposta_focus_colonna_destra_avanzata()    # ✓ avanzata
```

**Nessun problema.** La facade non chiama accidentalmente i metodi semplici.

---

## Identificazione precisa del punto di perdita

```
giocatore_umano.py     →  SANO: tipi evento distinti, dati corretti
comandi_partita.py     →  SANO: delega ai metodi avanzati
renderer_wx.py         →  QUASI SANO: testo costruito correttamente,
                           ma la distinzione usa [N] che NVDA non pronuncia
AO2/NVDA               →  QUI SI PERDE: parentesi quadre silenti +
                           "avanzata" troncato per interrupt
```

---

## Giudizio finale

**Il problema è a livello di come il contenuto del messaggio viene costruito**
(scelta del delimitatore `[N]`) e **non nella pipeline applicativa**.
Dominio e renderer funzionano. L'informazione di stato (segnato/non segnato)
esiste nel payload dell'evento ed è trasmessa al renderer, ma viene codificata
in un formato (parentesi quadre) che NVDA rende invisibile all'ascolto.

La parola "avanzata" nel prefisso è presente, ma di fatto non raggiunge l'utente
per la dinamica di interrupt di NVDA durante la navigazione rapida.

La correzione appartiene al layer renderer: la modalità avanzata deve distinguersi
con testo pronunciabile (es. la parola "segnato" accanto al numero, o un prefisso
breve annunciato come utterance separata prima delle celle).

---

## Problemi secondari rilevati

### PS-1 — `_handle_vai_a_riga_avanzata` senza label "avanzata"

In `renderer_wx.py`, il handler per `EventoVaiARigaAvanzata` (linea ~390) produce:

```python
testo = f"Riga {evento.numero_riga}: {celle}"
```

La parola "avanzata" è **assente**, a differenza di `_handle_navigazione_riga_avanzata`
che la include. I numeri segnati SONO in `[N]` ma comunque inudibili.
Il comando `vai_a_riga(N)`, attivabile da Alt+1..3, risulta 100% identico al semplice.

### PS-2 — `_handle_vai_a_colonna_avanzata` senza label "avanzata"

Stessa situazione per `EventoVaiAColonnaAvanzata` (linea ~404):

```python
testo = f"Colonna {evento.numero_colonna}: {celle}"
```

Nessuna distinzione verbale rispetto alla colonna semplice.

### PS-3 — cella vuota: "vuoto" è udibile ma può confondere

La chiave `UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA` in `it.py` (linea 240) risolve
a `"vuoto"`. Sia la modalità semplice che quella avanzata la usano per le celle
senza numero. Con 5-6 celle vuote per riga, NVDA pronuncia "vuoto vuoto vuoto..."
ripetutamente, riducendo lo spazio sonoro per le informazioni di stato. Non è
un bug ma un elemento da considerare nella revisione del testo avanzato.

### PS-4 — `stato_riga` e `stato_colonna` mai usati dal renderer

I campi `stato_riga` (dict con totali/segnati/percentuale per riga) e `stato_colonna`
(analogo per colonna) sono presenti negli eventi avanzati ma il renderer non li
legge mai. Contengono informazioni potenzialmente utili (es. "2 segnati su 3 in
questa riga") che attualmente vengono silenziosamente scartate.
Questo è coerente con l'attuale stub del renderer, ma spiega perché la modalità
avanzata non offre un arricchimento informativo reale nel testo corrente.
