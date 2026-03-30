# Verifica anomalie segnalate in giocatore_umano.py

Data: 2026-03-30
(File temporaneo — da cestinare dopo la lettura)

---

## Premessa

Ho analizzato il codice reale di giocatore_umano.py per ognuna delle tre anomalie
segnalate. Riporto qui il verdetto su ciascuna, spiegando cosa ho trovato e perché.

---

## Anomalia A — I quattro metodi di visualizzazione restituiscono None o una stringa

### Verdetto: CONFERMATA — BUG REALE

Questo è un errore autentico e presente in quattro metodi:
- visualizza_cartella_corrente_semplice
- visualizza_cartella_corrente_avanzata
- visualizza_tutte_cartelle_semplice
- visualizza_tutte_cartelle_avanzata

### Cosa fa il codice oggi

In caso di errore (es. nessuna cartella disponibile), tutti e quattro restituiscono:
    return None

In caso di successo, tutti e quattro restituiscono:
    return str(EsitoAzione(ok=True, errore=None, evento=evento))

### Perché è un problema

Chi chiama questi metodi — il controller di gioco, la UI, un test — si aspetta di
ricevere un oggetto EsitoAzione da cui poter leggere .ok, .errore e .evento.

Invece riceve:
- None in caso di errore: qualsiasi tentativo di usarlo (es. controllare .ok) causa
  un crash immediato.
- Una stringa di testo in caso di successo: str(EsitoAzione(...)) non è un EsitoAzione,
  è la sua rappresentazione testuale. Qualsiasi accesso a .ok, .evento, .errore fallisce.

### Cosa avrebbe dovuto fare il codice

Caso errore:
    return esito_focus   (propagare l'oggetto di errore già pronto, non restituire None)

Caso successo:
    return EsitoAzione(ok=True, errore=None, evento=evento)   (senza str(...))

### Gravità

Alta — questi metodi sono usati per mostrare la cartella al giocatore, una delle
operazioni più frequenti del gioco.

---

## Anomalia B — _esito_focus_riga_valido chiamato con un parametro che non esiste

### Verdetto: NON CONFERMATA — Falso positivo

Il report di Perplexity citava una versione precedente del bug. Ho verificato il
codice attuale e la situazione è diversa: il parametro auto_imposta=False è stato
già rimosso dalla chiamata.

### Cosa dice il codice oggi

In annuncia_vittoria (linea ~2250), la chiamata è:
    esito_focus_riga = self._esito_focus_riga_valido()

Nessun parametro passato. La chiamata è corretta rispetto alla firma del metodo,
che è definita senza parametri aggiuntivi:
    def _esito_focus_riga_valido(self) -> EsitoAzione:

### Nota a margine

Il bug del parametro auto_imposta=False era reale in una versione precedente del file,
ed era stato documentato nel report di pianificazione dei test come BUG-2. Nella versione
attuale del codice risulta già corretto. Perplexity ha letto una versione non aggiornata
oppure il codice è stato sistemato nel frattempo.

---

## Anomalia C — Doppio controllo ridondante in sposta_focus_riga_giu

### Verdetto: CONFERMATA — Ma non è un bug, è codice difensivo mal scritto

Ho verificato entrambi i metodi segnalati (semplice e avanzata). Il pattern è identico
in entrambi e funziona così:

1. L'helper _esito_inizializza_focus_riga_se_manca() viene chiamato. Se la riga era None,
   l'helper la imposta a 0 e ritorna ok=True.

2. Subito dopo, nel blocco del "primo utilizzo", compare:
       if self._indice_riga_focus is None:
           self._indice_riga_focus = 0

### Perché è ridondante

Quando si arriva al blocco "primo utilizzo", la riga è già stata inizializzata dall'helper
al punto 1. La condizione `if self._indice_riga_focus is None` non può mai essere vera in
quel punto, perché l'helper appena chiamato l'ha già impostata.

### Perché non rompe niente

Il codice funziona correttamente perché, quando la riga è già impostata (come succederà
sempre dopo l'helper), le due righe ridondanti vengono semplicemente ignorate. Non c'è
nessun caso in cui producano un risultato sbagliato.

### Il rischio segnalato da Perplexity

La preoccupazione è giusta concettualmente: se in futuro l'helper cambia comportamento
(ad esempio inizializza la riga a 1 invece che a 0), il doppio controllo potrebbe sovrascrivere
quella scelta riportando il valore a 0, creando un comportamento inatteso e difficile da
trovare. Non è un bug oggi, ma è un punto fragile da tenere a mente.

### Gravità

Bassa — non causa errori nel comportamento attuale del gioco.

---

## Riepilogo decisioni

| Anomalia | Confermata | Gravità | Azione consigliata |
|----------|------------|---------|-------------------|
| A — return None / return str(...) | SI | Alta | Correggere i 4 metodi di visualizzazione |
| B — parametro inesistente auto_imposta | NO | — | Nessuna azione, già corretto |
| C — doppio controllo ridondante | Parzialmente | Bassa | Pulizia consigliata, non urgente |
