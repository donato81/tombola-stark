# Analisi ridondanze focus — giocatore_umano.py
Data: 30 marzo 2026
Analista: Agent-Analyze

---

## Verdetto rapido

**La segnalazione di Perplexity è confermata, ma parzialmente imprecisa nel conteggio.**
Ci sono **6 metodi** con la ridondanza (non tutti quelli nominati), e in più ho trovato
una **inconsistenza di valore** che Perplexity non aveva segnalato.

---

## Come funziona il meccanismo (spiegazione senza tecnicismi)

Ogni metodo di navigazione segue questa sequenza:

1. Registra se il focus era assente (variabile `era_none = True/False`)
2. Chiama un helper che, se il focus mancava, lo imposta subito a un valore di partenza
3. Usa la variabile registrata al punto 1 per decidere cosa fare al "primo utilizzo"

Il problema: dentro il blocco "primo utilizzo" (punto 3), alcuni metodi ricontrollano
se il focus è ancora assente — ma non lo sarà mai, perché l'helper del punto 2 l'ha
già impostato. Quel secondo controllo non può mai essere vero.

---

## Mappa delle ridondanze

### Metodi RIGA

| Metodo | Riga file | Ridondanza? | Valore usato nel blocco ridondante |
|--------|-----------|-------------|-------------------------------------|
| sposta_focus_riga_su_semplice    | 542 | NO  | — |
| sposta_focus_riga_giu_semplice   | 671 | **SÌ** | 0 |
| sposta_focus_riga_su_avanzata    | 810 | NO  | — |
| sposta_focus_riga_giu_avanzata   | 919 | **SÌ** | 0 |

I metodi "su" (direzione verso l'alto) sono stati scritti correttamente.
Solo i metodi "giù" hanno il doppio controllo.

### Metodi COLONNA

| Metodo | Riga file | Ridondanza? | Valore usato nel blocco ridondante |
|--------|-----------|-------------|-------------------------------------|
| sposta_focus_colonna_sinistra          | 1047 | **SÌ** | 4 |
| sposta_focus_colonna_destra            | 1169 | **SÌ** | 0 ← INCONGRUENTE |
| sposta_focus_colonna_sinistra_avanzata | 1296 | **SÌ** | 4 |
| sposta_focus_colonna_destra_avanzata   | 1421 | **SÌ** | 4 |

---

## Segnalazione extra non rilevata da Perplexity

Il metodo `sposta_focus_colonna_destra` (riga 1169) ha un **valore di partenza sbagliato**
nel blocco ridondante: usa 0 invece di 4.

Gli altri 3 metodi colonna usano 4, e l'helper stesso imposta il default a 4.
Questo metodo è l'unico che si discosta, e poiché il blocco è irraggiungibile il comportamento
non è compromesso — ma se mai il blocco venisse "liberato" (rimozione dell'helper esterno),
si comporterebbe in modo diverso dagli altri tre.

---

## Livello di rischio attuale

**Nessun rischio funzionale immediato.**
I blocchi ridondanti non vengono mai eseguiti in condizioni normali,
quindi il comportamento del gioco non ne è affetto.

L'unico rischio è di confusione futura: chi legge il codice potrebbe credere
che l'helper possa fallire silenziosamente e che il backup interno sia necessario.

---

## Raccomandazione

Rimuovere il doppio controllo da tutti e 6 i metodi elencati sopra.
Nei 4 metodi colonna, mantenere il valore 4 come default (coerente con l'helper),
correggendo anche l'incongruenza nel metodo `sposta_focus_colonna_destra`.

Prima di qualsiasi modifica: verificare che i test coprono i 6 metodi nel caso
"primo utilizzo" (focus inizialmente assente), così da avere una rete di sicurezza.
