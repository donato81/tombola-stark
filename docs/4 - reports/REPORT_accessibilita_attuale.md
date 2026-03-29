## Metadati

tipo: report
titolo: Analisi accessibilita attuale — Vocalizzatore con Accessible Output 2
data_creazione: 2026-03-29
agente: Agent-Analyze
stato: definitivo
scopo: preparazione piano di test

---

## 1. Componenti analizzati

### File principale

- `my_lib/vocalizzatore.py` — modulo unico di vocalizzazione, basato su `accessible_output2`

### Dipendenza esterna

- Libreria: `accessible-output2==0.17`
- Import usato: `from accessible_output2.outputs.auto import Auto`
- Classe AO2 istanziata: `Auto()` (backend automatico, sceglie il technology layer disponibile: NVDA, JAWS, SAPI5, ecc.)

---

## 2. Inventario metodi pubblici

### Metodi di base (wrapper AO2)

- `vocalizza_testo(testo: str)` — invia testo generico a `Auto.speak()`
- `vocalizza_numero(numero: int)` — produce la stringa `"Numero estratto: {numero}"` e chiama `vocalizza_testo()`
- `vocalizza_errore(messaggio: str)` — produce la stringa `"Attenzione, errore: {messaggio}"` e chiama `vocalizza_testo()`

### Metodi dominio Tabellone

- `messaggio_inizializzazione()` — stringa fissa: `"Inizializzazione del tabellone."`
- `messaggio_errore_numeri_terminati()` — stringa fissa via `vocalizza_errore()`: `"Tutti i numeri sono stati estratti."`
- `messaggio_numero_estratto(numero: int)` — delega a `vocalizza_numero()`
- `messaggio_reset_tabellone()` — stringa fissa: `"Reset del tabellone."`

### Metodi dominio Lista Numeri

- `vocalizza_numeri_estratti(numeri: list[int])` — se lista vuota: `"Nessun numero è stato estratto."`; altrimenti formatta con `_formatta_numeri_per_vocalizzazione()` e chiama `vocalizza_testo()`
- `vocalizza_numeri_disponibili(numeri: list[int])` — se lista vuota: `"Non ci sono numeri disponibili."`; altrimenti come sopra

### Metodo privato

- `_formatta_numeri_per_vocalizzazione(numeri: list[int]) -> str` — trasforma ogni intero in `"numero N"` e li unisce con `"; "` (pausa lunga) per produrre ritmo leggibile via screen reader

---

## 3. Analisi strutturale

### Architettura

- La classe `Vocalizzatore` non appartiene a nessun layer Clean Architecture: risiede in `my_lib/`, che è una cartella di utilita generica esterna ai 4 layer.
- Non e ancora integrata in nessun layer applicativo o di presentazione: nessun file Python del progetto importa `Vocalizzatore`.
- Tutte le chiamate vocali passano da `Auto.speak()`, unico punto di accoppiamento verso AO2.

### Aspetti positivi

- API semplice e coerente: tutti i metodi pubblici sono di alto livello e descrivono il dominio (es. `messaggio_numero_estratto`).
- Il metodo privato di formattazione e ben separato e riutilizzabile internamente.
- Le stringhe vocalizzate sono statiche o quasi-statiche: facili da testare.
- Il backend `Auto` di AO2 gestisce in autonomia la selezione dello screen reader: nessuna logica condizionale nel modulo.

### Problemi rilevati

- Nessun test esistente: il file non ha un corrispettivo in `tests/` ne in `tests/unit/`.
- Nessuna gestione eccezioni: se AO2 non e disponibile (screen reader non attivo, libreria non installata), `Auto()` solleva eccezione non catturata.
- Nessun meccanismo di silenzio opzionale (es. flag `muto`): impossibile disabilitare la vocalizzazione durante i test automatici senza mock.
- `vocalizza_numero` e `messaggio_numero_estratto` sono ridondanti: entrambi producono la medesima stringa `"Numero estratto: {numero}"`.
- I commenti inline sono verbosi e ridondanti rispetto al nome del metodo (non conformi allo standard `python.instructions.md` che richiede docstring, non commenti).
- Mancano type hints su `__init__` (manca `-> None`).
- La classe mescola metodi di base (layer infrastrutturale) con metodi di dominio specifici (Tabellone, Liste), senza separazione logica internas tramite sezioni chiare o classi distinte.

---

## 4. Copertura di dominio attuale

| Evento di gioco | Metodo dedicato | Stringa prodotta |
|---|---|---|
| Inizializzazione tabellone | `messaggio_inizializzazione()` | `"Inizializzazione del tabellone."` |
| Reset tabellone | `messaggio_reset_tabellone()` | `"Reset del tabellone."` |
| Numero estratto | `messaggio_numero_estratto(n)` | `"Numero estratto: N"` |
| Numeri terminati | `messaggio_errore_numeri_terminati()` | `"Attenzione, errore: Tutti i numeri sono stati estratti."` |
| Lista numeri estratti | `vocalizza_numeri_estratti(lista)` | `"Numeri estratti: numero N; numero M; ..."` |
| Lista numeri disponibili | `vocalizza_numeri_disponibili(lista)` | `"Numeri disponibili: numero N; numero M; ..."` |
| Testo generico | `vocalizza_testo(testo)` | testo passato direttamente |
| Errore generico | `vocalizza_errore(msg)` | `"Attenzione, errore: {msg}"` |

### Eventi di gioco NON ancora coperti (candidati per estensione)

- Cartella aggiornata (numero segnato)
- Premio ottenuto (ambo, terno, quaterna, cinquina, tombola)
- Inizio e fine partita
- Cambio di turno / prossimo giocatore
- Focus su riga o colonna cartella
- Reclamo valido / non valido

---

## 5. Rischi per i test

- Il costruttore `__init__` chiama `Auto()` direttamente alla creazione dell'istanza, quindi ogni test che istanzia `Vocalizzatore` senza mock tenta di inizializzare il backend di AO2 — questo puo causare errori o comportamento non deterministico in ambienti CI senza screen reader.
- `Auto.speak()` e una chiamata I/O a sistema: deve sempre essere mockato nei test unitari.
- Non esiste interfaccia astratta (`Protocol` o `ABC`) davanti ad AO2: il mock deve essere applicato direttamente sul metodo `speak` dell'istanza `Auto`.

---

## 6. Raccomandazioni per il piano di test

### Alta priorita

- Testare ogni metodo pubblico in isolamento con `unittest.mock.patch` su `Auto.speak`.
- Verificare le stringhe esatte prodotte da ciascun metodo (contratto vocale).
- Testare casi limite: lista vuota, lista con un solo elemento, numero 0, numero 90.
- Testare che `vocalizza_errore` anteponga sempre il prefisso `"Attenzione, errore: "`.

### Media priorita

- Testare `_formatta_numeri_per_vocalizzazione` in isolamento (e un metodo privato ma e il nucleo della formattazione).
- Verificare che `messaggio_numero_estratto` e `vocalizza_numero` producano la medesima stringa.

### Bassa priorita

- Test di integrazione con AO2 reale (solo su macchina sviluppatore con NVDA/SAPI5 attivo, mai in CI).
- Test che verifichino che `Auto()` venga istanziato una sola volta (potenziale ottimizzazione futura).

### Pattern di mock suggerito

```python
from unittest.mock import MagicMock, patch
import unittest
from my_lib.vocalizzatore import Vocalizzatore

class TestVocalizzatore(unittest.TestCase):

    def setUp(self):
        with patch("my_lib.vocalizzatore.Auto") as mock_auto_cls:
            mock_auto_cls.return_value = MagicMock()
            self.voc = Vocalizzatore()
            self.mock_speak = self.voc.speaker.speak

    def test_vocalizza_testo_chiama_speak(self):
        self.voc.vocalizza_testo("ciao")
        self.mock_speak.assert_called_once_with("ciao")
```

---

## 7. Riepilogo finding

- Metodi pubblici analizzati: 10
- Metodi privati: 1
- Test esistenti: 0
- Consumer nel codebase: 0 (modulo non integrato)
- Rischio CI senza mock: alto (chiamata I/O in `__init__`)
- Copertura dominio di gioco: parziale (6 eventi su circa 12 rilevanti)
- Conformita standard codice (type hints, docstring, no commenti ridondanti): parziale

---

## 8. Prossimo passo suggerito

Creare `tests/unit/test_vocalizzatore.py` con suite `unittest.TestCase` che copra tutti i metodi pubblici tramite mock di `Auto.speak`. Candidato per Agent-Plan (PLAN) + Agent-Code.
