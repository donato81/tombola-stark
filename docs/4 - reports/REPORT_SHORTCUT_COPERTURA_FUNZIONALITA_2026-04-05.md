# Analisi Shortcut Tastiera e Copertura Funzionalità GiocatoreUmano

**Data:** 2026-04-05
**Agente:** Agent-Analyze
**Scope:** `bingo_game/ui/finestra_gioco.py`,
           `bingo_game/comandi_partita.py` classe `ComandiGiocatoreUmano`,
           `bingo_game/players/giocatore_umano.py`,
           `bingo_game/ui/dialogo_ricerca.py`

---

## 1. Obiettivi

1. Elencare tutti i tasti rapidi attivi per il testing manuale in gioco.
2. Verificare la correttezza della mappatura shortcut → metodo facade → metodo dominio.
3. Identificare funzionalità di `GiocatoreUmano` non raggiungibili da tastiera.

---

## 2. Architettura binding tastiera

La `FinestraGioco` espone tre livelli di binding:

**Categoria A** — `EVT_KEY_DOWN` sul `PannelloGriglia` (widget con focus).
Intercetta navigazione, segnazione, vittorie. Non blocca propagazione a wxPython.

**Categoria B** — `EVT_CHAR_HOOK` sul frame, codici che restituiscono senza `event.Skip()`.
Intercetta prima che il messaggio raggiunga altri widget o NVDA.

**Categoria C** — `EVT_CHAR_HOOK` con combinazioni `[NVDA-VERIFY]`.
Funziona correttamente in ambienti headless / con NVDA disabilitato.
Potenziale conflitto con shortcut globali NVDA (documentato inline).

---

## 3. Elenco completo shortcut attivi

### 3.1 Categoria A — Pannello griglia (EVT_KEY_DOWN)

| Shortcut           | Metodo facade                    | Metodo GiocatoreUmano                        | Funzione                            |
|--------------------|----------------------------------|----------------------------------------------|-------------------------------------|
| Freccia Su         | `riga_su()`                      | `sposta_focus_riga_su_semplice()`            | Riga precedente (semplice)          |
| Freccia Giù        | `riga_giu()`                     | `sposta_focus_riga_giu_semplice()`           | Riga successiva (semplice)          |
| Freccia Sinistra   | `colonna_sinistra()`             | `sposta_focus_colonna_sinistra()`            | Colonna sinistra (semplice)         |
| Freccia Destra     | `colonna_destra()`               | `sposta_focus_colonna_destra()`              | Colonna destra (semplice)           |
| 1 … 9              | `vai_a_colonna(n)`               | `vai_a_colonna_avanzata(n)`                  | Salta a colonna n (1-based)         |
| Spazio             | `segna_numero(num_in_focus)`     | `segna_numero_manuale(num, tabellone)`       | Segna numero attualmente in focus   |
| V                  | `visualizza_semplice()`          | `visualizza_cartella_corrente_semplice()`    | Vista semplice cartella in focus    |
| Shift+V            | `visualizza_avanzata()`          | `visualizza_cartella_corrente_avanzata()`    | Vista avanzata cartella in focus    |
| Shift+Ctrl+V       | `visualizza_tutte_avanzate()`    | `visualizza_tutte_cartelle_avanzata()`       | Vista avanzata di tutte le cartelle |
| S                  | `stato_focus()`                  | `stato_focus_corrente()`                     | Stato corrente del focus            |
| R                  | `riepilogo_cartella_corrente()`  | `riepilogo_cartella_corrente()`              | Riepilogo cartella in focus         |
| A                  | `leggi_posizione_avanzata()`     | `leggi_riga_avanzata()` / `leggi_colonna_avanzata()` | Lettura avanzata riga o colonna |
| F1                 | `annuncia_vittoria("ambo", t)`   | `annuncia_vittoria("ambo", t)`               | Reclamo ambo                        |
| F2                 | `annuncia_vittoria("terno", t)`  | `annuncia_vittoria("terno", t)`              | Reclamo terno                       |
| F3                 | `annuncia_vittoria("quaterna", t)` | `annuncia_vittoria("quaterna", t)`         | Reclamo quaterna                    |
| F4                 | `annuncia_vittoria("cinquina", t)` | `annuncia_vittoria("cinquina", t)`         | Reclamo cinquina                    |
| F5                 | `annuncia_vittoria("tombola", t)` | `annuncia_vittoria("tombola", t)`           | Reclamo tombola                     |
| F6                 | `renderer.ripeti_ultimo_annuncio()` | —                                         | Ripete l'ultimo annuncio vocale     |
| Escape             | `btn_principale.SetFocus()`      | —                                            | Sposta focus al pulsante principale |

### 3.2 Categoria B — Frame (EVT_CHAR_HOOK, blocca propagazione)

| Shortcut           | Metodo facade                     | Metodo GiocatoreUmano                          | Funzione                              |
|--------------------|-----------------------------------|------------------------------------------------|---------------------------------------|
| Alt+Freccia Su     | `riga_su_avanzata()`              | `sposta_focus_riga_su_avanzata()`              | Riga precedente (avanzata)            |
| Shift+Freccia Su   | `riga_su_avanzata()`              | `sposta_focus_riga_su_avanzata()`              | Riga precedente (avanzata) — alias    |
| Alt+Freccia Giù    | `riga_giu_avanzata()`             | `sposta_focus_riga_giu_avanzata()`             | Riga successiva (avanzata)            |
| Shift+Freccia Giù  | `riga_giu_avanzata()`             | `sposta_focus_riga_giu_avanzata()`             | Riga successiva (avanzata) — alias    |
| Alt+Freccia Sx     | `colonna_sinistra_avanzata()`     | `sposta_focus_colonna_sinistra_avanzata()`     | Colonna sinistra (avanzata)           |
| Shift+Freccia Sx   | `colonna_sinistra_avanzata()`     | `sposta_focus_colonna_sinistra_avanzata()`     | Colonna sinistra (avanzata) — alias   |
| Alt+Freccia Dx     | `colonna_destra_avanzata()`       | `sposta_focus_colonna_destra_avanzata()`       | Colonna destra (avanzata)             |
| Shift+Freccia Dx   | `colonna_destra_avanzata()`       | `sposta_focus_colonna_destra_avanzata()`       | Colonna destra (avanzata) — alias     |
| Ctrl+P             | `_on_pulsante_principale()`       | `dichiara_fine_turno()` (via pulsante)         | Passa il turno / dichiara fine turno  |
| Ctrl+F             | apre `DialogoRicercaNumero`       | `cerca_numero()` (nel dialog)                  | Ricerca numero nelle cartelle         |
| Ctrl+1 … Ctrl+6    | `imposta_focus_cartella(n)`       | `imposta_focus_cartella(n)`                    | Salta direttamente a cartella n       |
| Alt+1 … Alt+3      | `vai_a_riga(n)`                   | `vai_a_riga_avanzata(n)`                       | Salta direttamente a riga n           |

### 3.3 Categoria C — Frame (EVT_CHAR_HOOK, NVDA-VERIFY)

| Shortcut  | Metodo facade               | Metodo GiocatoreUmano                          | Funzione                          | Note conflitto NVDA |
|-----------|-----------------------------|------------------------------------------------|-----------------------------------|---------------------|
| Ctrl+T    | `ultimo_numero_estratto()`  | `comunica_ultimo_numero_estratto(tabellone)`   | Ultimo numero estratto            | Ctrl+T = titolo finestra in NVDA |
| Ctrl+U    | `ultimi_numeri_estratti()`  | `visualizza_ultimi_numeri_estratti(tabellone)` | Ultimi 5 numeri estratti          | Possibile conflitto  |
| Ctrl+L    | `lista_numeri_estratti()`   | `lista_numeri_estratti(tabellone)`             | Lista completa numeri estratti    | Ctrl+L = link in NVDA Browse Mode |
| Ctrl+R    | `riepilogo_tabellone()`     | `riepilogo_tabellone(tabellone)`               | Riepilogo stato tabellone         | Possibile conflitto  |
| Ctrl+E    | `_consulta_log()`           | —                                              | Focus e vocalizzazione area log   | Generalmente sicuro  |

---

## 4. Metodi GiocatoreUmano — verifica copertura completa

La seguente tabella elenca tutti i 29 metodi pubblici esposti da `ComandiGiocatoreUmano`
con lo stato di copertura da tastiera.

Legenda:
- **Coperto** — shortcut diretto nel frame.
- **Indiretto** — raggiungibile solo tramite dialog o click pulsante.
- **Non coperto** — nessun percorso tastiera nel frame corrente.
- **Interno** — metodo di guardia/stato, non richiede shortcut utente.

| # | Metodo facade                  | Stato          | Shortcut / Note                              |
|---|-------------------------------|----------------|----------------------------------------------|
| 1 | `imposta_focus_cartella(n)`   | Coperto        | Ctrl+1 … Ctrl+6                             |
| 2 | `cartella_precedente()`       | **Non coperto**| Nessun shortcut nel frame                    |
| 3 | `cartella_successiva()`       | **Non coperto**| Nessun shortcut nel frame                    |
| 4 | `riepilogo_cartella_corrente()` | Coperto      | R                                            |
| 5 | `visualizza_semplice()`       | Coperto        | V                                            |
| 6 | `visualizza_avanzata()`       | Coperto        | Shift+V                                      |
| 7 | `visualizza_tutte_semplice()` | **Non coperto**| Nessun shortcut (Shift+Ctrl+V → avanzata)    |
| 8 | `visualizza_tutte_avanzate()` | Coperto        | Shift+Ctrl+V                                 |
| 9 | `riga_su()`                   | Coperto        | Freccia Su                                   |
| 10 | `riga_giu()`                 | Coperto        | Freccia Giù                                  |
| 11 | `riga_su_avanzata()`         | Coperto        | Alt+Freccia Su / Shift+Freccia Su            |
| 12 | `riga_giu_avanzata()`        | Coperto        | Alt+Freccia Giù / Shift+Freccia Giù          |
| 13 | `vai_a_riga(n)`              | Coperto        | Alt+1 … Alt+3                               |
| 14 | `colonna_sinistra()`         | Coperto        | Freccia Sinistra                             |
| 15 | `colonna_destra()`           | Coperto        | Freccia Destra                               |
| 16 | `colonna_sinistra_avanzata()` | Coperto       | Alt+Freccia Sx / Shift+Freccia Sx            |
| 17 | `colonna_destra_avanzata()`  | Coperto        | Alt+Freccia Dx / Shift+Freccia Dx            |
| 18 | `vai_a_colonna(n)`           | Coperto        | Tasti 1 … 9 (senza modificatori)             |
| 19 | `segna_numero(num)`          | Coperto        | Spazio (usa numero in focus dal renderer)    |
| 20 | `cerca_numero(num)`          | Indiretto      | Ctrl+F → `DialogoRicercaNumero`              |
| 21 | `ultimo_numero_estratto()`   | Coperto (C)    | Ctrl+T [NVDA-VERIFY]                         |
| 22 | `ultimi_numeri_estratti()`   | Coperto (C)    | Ctrl+U [NVDA-VERIFY]                         |
| 23 | `riepilogo_tabellone()`      | Coperto (C)    | Ctrl+R [NVDA-VERIFY]                         |
| 24 | `lista_numeri_estratti()`    | Coperto (C)    | Ctrl+L [NVDA-VERIFY]                         |
| 25 | `stato_focus()`              | Coperto        | S                                            |
| 26 | `leggi_posizione_avanzata()` | Coperto        | A (adatta a riga o colonna in base al contesto) |
| 27 | `annuncia_vittoria(tipo, t)` | Coperto        | F1 (ambo) F2 (terno) F3 (quaterna) F4 (cinquina) F5 (tombola) |
| 28 | `turno_gia_dichiarato()`     | Interno        | Usato internamente dal timer; non esposto    |
| 29 | `dichiara_fine_turno(p)`     | Indiretto      | Ctrl+P / click pulsante principale           |

---

## 5. Gap identificati

### GAP-1 — Navigazione sequenziale tra cartelle non disponibile da tastiera

**Metodi interessati:** `cartella_precedente()` (#2), `cartella_successiva()` (#3)

**Situazione attuale:**
Il frame espone solo salto diretto a cartella n tramite Ctrl+N (Ctrl+1..6).
Non esiste shortcut per "cartella precedente" e "cartella successiva" in sequenza.
L'utente con più cartelle non può navigare avanti/indietro tra esse con un singolo tasto.

**Impatto:** Basso — Ctrl+1..6 permette di selezionare qualunque cartella direttamente.
Per partite con 1 cartella (configurazione default) l'impatto è nullo.
Per partite con 2+ cartelle, il salto diretto è sempre disponibile.

**Possibili shortcut futuri:** Ctrl+Freccia Sinistra / Ctrl+Freccia Destra (non ancora usati).

---

### GAP-2 — Visualizzazione semplice di tutte le cartelle non disponibile da tastiera

**Metodo interessato:** `visualizza_tutte_semplice()` (#7)

**Situazione attuale:**
Esiste Shift+Ctrl+V per la versione avanzata di tutte le cartelle.
Non esiste shortcut per la versione semplice.

**Impatto:** Basso — la versione avanzata fornisce un sovrainsieme delle informazioni
della versione semplice. Per uso quotidiano con screen reader la versione avanzata
è preferibile (include stato numeri segnati).

**Possibili shortcut futuri:** Ctrl+Shift+B o simili (da verificare conflitti NVDA).

---

### GAP-3 — Shortcut Categoria C non verificati con NVDA attivo

**Shortcut interessati:** Ctrl+T, Ctrl+U, Ctrl+L, Ctrl+R

**Situazione attuale:**
Il file `finestra_gioco.py` marca esplicitamente questi shortcut con
`[NVDA-VERIFY: potenziale conflitto]`. Il codice è implementato ma il comportamento
con NVDA+Windows in modalità focus non è stato verificato operativamente.

**Rischio:** Medio — NVDA intercetta Ctrl+T (titolo finestra), Ctrl+L (link in
Browse Mode), possibilmente Ctrl+R. In modalità "focus mode" (applicazione wx),
wxPython riceve il tasto prima di NVDA per la maggior parte dei casi, ma alcune
combinazioni sono gestite direttamente da NVDA a livello di driver.

**Azione consigliata:** Test manuale in sessione live NVDA + Windows 11
per ciascuno dei 4 shortcut.

---

### NOTA-1 — Doppio trigger per navigazione avanzata (Alt e Shift)

**Situazione:**
In `_on_char_hook` la condizione è `if not ctrl and (alt or shift)`.
Questo significa che ENTRAMBE le combinazioni Alt+Freccia e Shift+Freccia
attivano la modalità avanzata.

Il docstring in testa al file documenta solo "Alt+Frecce", omettendo Shift+Frecce.

**Impatto accessibilità:** Positivo — Shift+Freccia può essere più comodo per
alcuni screen reader. Non è un bug ma andrebbe documentato.

---

## 6. Sommario copertura

| Categoria               | Totale | Coperti | Indiretti | Non coperti | Interni |
|------------------------|--------|---------|-----------|-------------|---------|
| Navigazione cartelle   | 4      | 2       | 0         | 2           | 0       |
| Visualizzazione        | 4      | 3       | 0         | 1           | 0       |
| Navigazione riga       | 5      | 5       | 0         | 0           | 0       |
| Navigazione colonna    | 5      | 5       | 0         | 0           | 0       |
| Segnazione e ricerca   | 2      | 1       | 1         | 0           | 0       |
| Consultazione tabellone| 4      | 4 (C)   | 0         | 0           | 0       |
| Focus e stato          | 2      | 2       | 0         | 0           | 0       |
| Vittoria               | 1      | 1       | 0         | 0           | 0       |
| Turno                  | 2      | 0       | 1         | 0           | 1       |
| **Totale**             | **29** | **23**  | **2**     | **3**       | **1**   |

Copertura tastiera diretta: **23/28** metodi esposti (82%).
Metodi senza percorso tastiera: **3** (GAP-1 e GAP-2, impatto basso).

---

## 7. Shortcut rapida per il testing manuale

Sequenza consigliata per verifica funzionale completa in sessione di test:

```
1.  Ctrl+1            — imposta focus cartella 1
2.  Freccia Su / Giù  — naviga righe (semplice)
3.  Alt+Freccia Su/Giù — naviga righe (avanzata)
4.  Alt+1..3          — salta a riga diretta
5.  Freccia Sx/Dx     — naviga colonne (semplice)
6.  Alt+Freccia Sx/Dx — naviga colonne (avanzata)
7.  1..9              — salta a colonna diretta
8.  S                 — verifica stato focus (cartella/riga/colonna)
9.  A                 — lettura avanzata posizione corrente
10. Spazio            — segna numero in focus
11. R                 — riepilogo cartella corrente
12. V                 — visualizza semplice cartella
13. Shift+V           — visualizza avanzata cartella
14. Shift+Ctrl+V      — visualizza avanzata tutte le cartelle
15. Ctrl+F → Invio    — ricerca numero nel dialog (premi Escape per chiudere)
16. Ctrl+T            — ultimo numero estratto [NVDA-test]
17. Ctrl+U            — ultimi 5 estratti [NVDA-test]
18. Ctrl+L            — lista numeri estratti [NVDA-test]
19. Ctrl+R            — riepilogo tabellone [NVDA-test]
20. Ctrl+E            — consulta log annunci
21. F1..F5            — reclamo vittoria (ambo/terno/quaterna/cinquina/tombola)
22. F6                — ripeti ultimo annuncio
23. Ctrl+P            — passa turno (equivale a click pulsante)
24. Escape            — sposta focus a pulsante principale
```

---

## 8. File analizzati

- `bingo_game/ui/finestra_gioco.py` (righe 1–650)
- `bingo_game/comandi_partita.py` (classe `ComandiGiocatoreUmano`, righe 240–450)
- `bingo_game/players/giocatore_umano.py` (righe 1–2300+)
- `bingo_game/ui/dialogo_ricerca.py` (righe 1–140)

---

*Fine report.*
