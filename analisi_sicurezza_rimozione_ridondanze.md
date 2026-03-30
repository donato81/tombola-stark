# Analisi sicurezza rimozione ridondanze — giocatore_umano.py
Data: 30 marzo 2026
Analista: Agent-Analyze
Prerequisito: analisi_ridondanze_focus_giocatore_umano.md (report precedente)

---

## Premessa: come leggere questo report

Il report precedente ha identificato 6 punti nel codice dove un controllo
è scritto due volte. Questo report risponde alla domanda:
"se rimuovo quella riga inutile, cosa cambia? I test reggono?"

---

## Come si protegge ogni metodo oggi

Ogni metodo ha una struttura in tre fasi:

1. Salva il fatto che il punto di partenza era assente (variabile `era_none`)
2. Chiama un meccanismo esterno che GARANTISCE l'impostazione del valore
3. Usa la variabile salvata al punto 1 per i calcoli successivi

Il punto chiave è che al momento del passo 3, il valore è già garantito
presente dal passo 2. Il secondo controllo "se è ancora assente, impostalo"
dentro il blocco del passo 3 non può mai scattare.

---

## Verifica test per ciascuno dei 6 metodi

### 1. sposta_focus_riga_giu_semplice (riga 671)

Test dedicato al primo utilizzo: `test_sposta_focus_riga_giu_semplice_auto_inizializzazione`

Cosa verifica: parte da assenza di punto di partenza, chiama il metodo,
controlla che il risultato sia la seconda riga (indice 1, valore 1-based = 2).

Flusso reale oggi:
- Meccanismo esterno: imposta la partenza a riga 0
- Blocco primo utilizzo: il check interno non scatta (già 0), avanza a 1
- Risultato: riga 1 → numera come "2" → test verde

Flusso dopo rimozione del check interno:
- Meccanismo esterno: imposta la partenza a riga 0
- Blocco primo utilizzo: usa direttamente 0, avanza a 1
- Risultato: identico → test verde

**Verdetto: rimozione sicura. Test non rotto.**

---

### 2. sposta_focus_riga_giu_avanzata (riga 919)

Test dedicato: `test_sposta_focus_riga_giu_avanzata_auto_inizializzazione`

Struttura identica al precedente, stesso ragionamento, stesso flusso.

**Verdetto: rimozione sicura. Test non rotto.**

---

### 3. sposta_focus_colonna_sinistra (riga 1047)

Test dedicato: `test_sposta_focus_colonna_sinistra_semplice_auto_inizializzazione`

Cosa verifica: parte senza colonna impostata, chiama il metodo,
controlla che il risultato sia la colonna 4 (indice 3, valore 1-based = 4).

Flusso reale oggi:
- Meccanismo esterno: imposta la partenza a colonna 4
- Blocco primo utilizzo: il check interno avrebbe impostato 4 (stesso valore) → non cambia nulla, poi va a sinistra → colonna 3
- Risultato: colonna 3 → numera come "4" → test verde

Flusso dopo rimozione del check interno:
- Meccanismo esterno: imposta la partenza a colonna 4
- Blocco primo utilizzo: usa direttamente 4, va a sinistra → colonna 3
- Risultato: identico → test verde

**Verdetto: rimozione sicura. Test non rotto.**

---

### 4. sposta_focus_colonna_destra (riga 1169) — CASO SPECIALE

Test dedicato: `test_sposta_focus_colonna_destra_semplice_auto_inizializzazione`

Cosa verifica: parte senza colonna impostata, chiama il metodo,
controlla che il risultato sia la colonna 6 (indice 5, valore 1-based = 6).

Flusso reale oggi:
- Meccanismo esterno: imposta la partenza a colonna 4
- Blocco primo utilizzo: il check interno AVREBBE impostato 0 (valore sbagliato!),
  ma non scatta mai → usa 4 esistente, va a destra → colonna 5
- Risultato: colonna 5 → numera come "6" → test verde

Flusso dopo rimozione del check interno:
- Meccanismo esterno: imposta la partenza a colonna 4
- Blocco primo utilizzo: usa direttamente 4, va a destra → colonna 5
- Risultato: identico → test verde

Il test funge anche da guardia implicita: se il check errato con valore 0
venisse mai raggiunto, il risultato sarebbe colonna 1 (indice 0+1=1, valore
1-based = 2) invece di 6. Il test FALLIREBBE. Questo conferma che il check
non viene mai raggiunto oggi, e dopo la rimozione non cambia nulla.

**Verdetto: rimozione sicura. Test non rotto. Il check errato era anche
pericoloso se mai fosse diventato raggiungibile.**

---

### 5. sposta_focus_colonna_sinistra_avanzata (riga 1296)

Test dedicato: `test_sposta_focus_colonna_sinistra_avanzata_auto_inizializzazione`

Struttura identica al metodo 3 (sposta_focus_colonna_sinistra), stessa analisi.

**Verdetto: rimozione sicura. Test non rotto.**

---

### 6. sposta_focus_colonna_destra_avanzata (riga 1421)

Test dedicato: `test_sposta_focus_colonna_destra_avanzata_auto_inizializzazione`

Struttura identica al metodo 4 (sposta_focus_colonna_destra), ma il check
interno usa il valore 4 (corretto, come il meccanismo esterno). La rimozione
rimane comunque sicura perché il valore inserito dal meccanismo esterno è già 4.

**Verdetto: rimozione sicura. Test non rotto.**

---

## Copertura test: c'è qualche scenario scoperto?

### Scenari testati per ciascun metodo (tutti e 6)
- Cartella assente → errore gestito
- Già al limite → evento limite
- Movimento normale (focus già impostato) → spostamento corretto
- Primo utilizzo da assenza (None) → auto-inizializzazione + spostamento

### Scenari non testati (ma non creati dalla rimozione)

Esiste un caso teorico non coperto da nessun test:
**"Primo utilizzo + cartella con una sola riga/colonna disponibile"**

In questo caso il metodo "giù" partirebbe da 0, ma l'unica riga è la 0
stessa (indice = totale-1), quindi restituirebbe "limite massimo" già al
primo utilizzo. Questo comportamento è corretto, ma non testato.

Questa lacuna esiste già oggi ed è indipendente dalle ridondanze.
Non peggiora dopo la rimozione.

---

## Sintesi decisionale

| Metodo | Test primo utilizzo | Safe per rimozione | Note |
|--------|---------------------|-------------------|------|
| sposta_focus_riga_giu_semplice | SÌ | SÌ | — |
| sposta_focus_riga_giu_avanzata | SÌ | SÌ | — |
| sposta_focus_colonna_sinistra | SÌ | SÌ | — |
| sposta_focus_colonna_destra | SÌ | SÌ | Check rimosso era anche logicamente sbagliato (valore 0 invece di 4) |
| sposta_focus_colonna_sinistra_avanzata | SÌ | SÌ | — |
| sposta_focus_colonna_destra_avanzata | SÌ | SÌ | — |

---

## Raccomandazione operativa

### Puoi procedere alla rimozione senza aggiungere test nuovi.

I 6 test di auto-inizializzazione esistenti sono già sufficienti come
rete di sicurezza. Coprono esattamente lo scenario in cui il check ridondante
si trovava.

### Sequenza suggerita

1. Eseguire i test attuali e verificare che siano tutti verdi (baseline)
2. Rimuovere i 6 blocchi ridondanti (una riga singola per ciascuno)
3. Eseguire di nuovo i test: devono restare tutti verdi
4. Per `sposta_focus_colonna_destra`: nella stessa operazione, rimuovi
   la riga con il valore errato 0. Non è necessario aggiungere test
   perché il test esistente di auto-inizializzazione già garantisce
   il comportamento corretto (si aspetta colonna 6, non colonna 2).

### Opzione aggiuntiva (facoltativa, non urgente)

Se vuoi coprire anche il caso "primo utilizzo con una sola riga disponibile",
potresti aggiungere un test per `sposta_focus_riga_giu_semplice` con una
cartella a una sola riga. Ma è un caso limite, non richiesto dalla rimozione.
