# Report Analisi: fix definitivo del messaggio di benvenuto NVDA all'avvio della FinestraGioco

- Data: 2026-04-14
- Agente: Agent-Design
- Ambito: FinestraGioco, sequenza Show/SetFocus, renderer AO2, comportamento NVDA
- Stato: definitivo proposto per sostituire l'approccio v0.12.3

---

## Sintomo

Il messaggio di benvenuto della FinestraGioco continua a non risultare affidabile
all'avvio, anche dopo il tentativo documentato per v0.12.3. In pratica il testo
puo essere troncato, sovrascritto o non arrivare affatto all'utente, mentre NVDA
pronuncia invece gli annunci nativi di finestra o di focus.

---

## Root cause verificata

La causa radice non e soltanto l'assenza di `interrupt=True`, ma il fatto che
`_pannello_griglia.SetFocus()` venga eseguito subito dopo la vocalizzazione del
benvenuto. Questo genera un evento nativo NVDA di gainFocus che compete con il
parlato AO2 sullo stesso sintetizzatore finale.

Poiche i due canali convergono sul medesimo sintetizzatore, l'ultimo evento vince:

- AO2 avvia il benvenuto
- il focus sulla griglia genera subito dopo un annuncio NVDA nativo
- il gainFocus nativo interrompe o sovrascrive il parlato AO2

Il risultato e che il benvenuto non e stabile e non puo essere considerato
risolto in modo definitivo.

---

## Sequenza eventi NVDA/AO2 osservata

### Sequenza difettosa

```
1. FinestraGioco completa la fase iniziale di setup
2. renderer.mostra_messaggio_benvenuto(...)
3. AO2 inizia a parlare
4. _pannello_griglia.SetFocus()
5. NVDA genera gainFocus nativo sulla griglia
6. il sintetizzatore riceve l'evento piu recente
7. il benvenuto viene interrotto o sostituito
```

### Sequenza obiettivo

```
1. FinestraGioco completa la fase iniziale di setup
2. _pannello_griglia.SetFocus()
3. NVDA genera gli annunci nativi legati al focus
4. wx.CallLater(350, ...)
5. allo scadere del delay AO2 emette il benvenuto con interrupt=True
6. nessun ulteriore cambio focus segue immediatamente
7. il benvenuto resta il messaggio finale udibile
```

---

## Soluzione proposta

La soluzione definitiva richiesta da questo task e composta da due passi
inseparabili:

1. eseguire prima `SetFocus()` sulla griglia, cosi il focus reale della finestra
   si stabilizza subito e gli annunci nativi di NVDA vengono generati prima del
   benvenuto applicativo;
2. usare `wx.CallLater(350, ...)` per emettere il messaggio di benvenuto con
   `interrupt=True`, quando il focus e gia fermo e non deve piu produrre un nuovo
   gainFocus immediato.

Questa soluzione cambia il modello mentale della fix:

- v0.12.3 tentava di far vincere il benvenuto nella competizione con il focus;
- il fix definitivo evita la competizione, facendo parlare AO2 solo dopo che il
  focus ha gia terminato di produrre i suoi effetti nativi.

---

## Decisioni tecniche

- Il delay di 350 ms viene trattato come valore operativo esplicito della fix.
- `interrupt=True` resta obbligatorio nel percorso del benvenuto.
- Nessuna modifica e richiesta a `my_lib/vocalizzatore.py`: il supporto tecnico
  esiste gia.
- La fix resta confinata al layer presentation e alla sequenza di bootstrap UI.

---

## Rischi

- Il valore 350 ms e empirico e va convalidato su runtime Windows con NVDA reale.
- Un eventuale nuovo cambio focus dopo il callback reintrodurrebbe il problema.
- Il leggero ritardo del benvenuto e accettabile solo se il messaggio diventa
  finalmente affidabile e completo.
- Eventuali test automatici che assumono l'annuncio immediato vanno riallineati
  alla nuova sequenza temporale.

---

## Verifica manuale attesa

1. Avviare l'applicazione con NVDA attivo.
2. Entrare in FinestraGioco dalla configurazione standard.
3. Verificare che il focus iniziale sia sulla griglia senza ulteriori spostamenti.
4. Attendere il delay previsto e confermare che NVDA legga integralmente:
   "Sei nella finestra di gioco. Premi Inizia partita o Ctrl+Invio per estrarre
   il primo numero. Premi Ctrl+H per la guida ai tasti rapidi."
5. Verificare che il benvenuto non venga interrotto da "Griglia cartella" o da
   altri annunci di gainFocus successivi.
6. Verificare che subito dopo il messaggio la navigazione da tastiera parta gia
   dalla griglia senza regressioni.

---

## File di riferimento

- docs/2 - projects/DESIGN_fix_benvenuto_interrupt_nvda.md
- docs/4 - reports/REPORT_ANALISI_benvenuto_ancora_muto_2026-04-14.md
- bingo_game/ui/finestra_gioco.py
- bingo_game/ui/renderers/renderer_wx.py