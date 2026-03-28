---
type: design
feature: fix_unicode_print
agent: Agent-Design
status: REVIEWED
version: v0.9.1
date: 2026-03-28
---

# DESIGN fix_unicode_print

## Idea in 3 righe

Il fix rimuove output `print()` informativi e con Unicode emoji dal perimetro
runtime di `bingo_game/comandi_partita.py` e dai test informativi in
`tests/test_game_controller.py`.

L'obiettivo architetturale e' eliminare side effect su stdout da un modulo di
orchestrazione applicativa e ridurre il rumore test/CI, mantenendo invariati
contratti pubblici, logica e struttura.

Il cambiamento e' una rimozione pura: nessuna sostituzione con logger, nessuna
variazione di firme, nessun refactor di flusso.

## Attori e Concetti

- `ComandiSistema` in `bingo_game/comandi_partita.py`: facade di orchestration a
  livello application verso `game_controller`.
- `game_controller`: sorgente della logica di business delegata dai comandi.
- `stdout`: canale non strutturato, inadatto per dominio/application e rumoroso
  per terminale, CI e screen reader.
- Test suite in `tests/test_game_controller.py`: deve esprimere comportamento
  tramite assert, non tramite output informativo.
- Logger semantico o eventi strutturati: canali ammessi per diagnostica futura,
  fuori dallo scope di questo fix.
- NVDA e pipeline CI: consumatori indiretti penalizzati da emoji e output
  verboso non deterministico.

## Flussi Concettuali

1. Un chiamante invoca un metodo di `ComandiSistema`.
2. Il metodo valida l'input, delega a `game_controller` o a `Partita` e ritorna
   il valore di dominio/applicazione calcolato.
3. Il metodo non deve emettere testo su stdout: il layer applicativo coordina
   casi d'uso, non presenta output umano.
4. I test verificano stato e ritorni con assert espliciti; nessun `print()`
   informativo deve contribuire alla semantica del test.
5. Il risultato atteso del fix e' la stessa semantica funzionale con meno side
   effect osservabili e meno rumore assistivo in console.

## Decisioni Architetturali

### Motivazione architetturale

`print()` non appartiene al dominio/application layer perche' introduce un side
effect di presentazione direttamente dentro codice che dovrebbe limitarsi a
validare input, orchestrare dipendenze e restituire risultati. Il layer
application deve restare indipendente dal canale di output umano: se serve
diagnostica, va instradata tramite logging semantico o eventi strutturati,
non tramite stdout ad hoc.

I test non devono contenere `print()` informativi perche' l'osservabilita' del
test deve stare negli assert. Un `print()` non migliora la verifica, introduce
rumore nei log di CI, peggiora l'accessibilita' con NVDA e crea output non
necessario che puo' mascherare errori reali durante la lettura della suite.

### Perimetro e righe da rimuovere

Il design limita il fix a rimozione pura delle seguenti righe.

#### bingo_game/comandi_partita.py

- Riga 72: `print(f"✅ Partita creata: {nome_umano} vs {num_bot} bot")`
- Riga 76: `print(f"❌ Errore creazione partita: {exc}")`
- Riga 91: `print("❌ Parametro non è Partita valida")`
- Riga 96: `print("🚀 Partita AVVIATA - Buon divertimento!")`
- Riga 111: `print("❌ Parametro non è Partita valida")`
- Riga 117: `print(f"🎲 Estratto numero: {numero}")`
- Riga 119: `print(f"   🏆 {len(risultato['premi_nuovi'])} nuovi premi!")`
- Riga 121: `print("   🎉 TOMBOLA RILEVATA!")`
- Riga 136: `print("❌ Parametro non è Partita valida")`
- Riga 141: `print(f"📊 Stato: {stato['stato_partita']} - {len(stato['numeri_estratti'])} estratti")`
- Riga 144: `print(f"❌ Errore stato partita: {exc}")`
- Riga 159: `print("❌ Parametro non è Partita valida")`
- Riga 164: `print("🎉 TOMBOLA presente nella partita!")`
- Riga 179: `print("❌ Parametro non è Partita valida")`
- Riga 184: `print("🏁 Partita TERMINATA")`
- Riga 199: `print("❌ Parametro non è Partita valida")`
- Riga 204: `print("🛑 Partita TERMINATA forzatamente")`
- Riga 207: `print(f"❌ Errore terminazione: {exc}")`

#### tests/test_game_controller.py

- Riga 470: `print("✅ Test numeri esauriti: simulazione OK (test manuale consigliato)")`
- Riga 780: `print(f"✅ Stato '{stato_target}': controller={controller_result}, partita={partita_result}")`

### Strategia di modifica

- Rimuovere esclusivamente le chiamate `print()` indicate.
- Non introdurre logger, eventi o refactor nello stesso task.
- Lasciare invariati rami condizionali, ritorni e gestione eccezioni.
- Trattare il fix come pulizia architetturale a impatto comportamentale nullo.

## Criteri di Accettazione

- Il perimetro del fix resta limitato a `bingo_game/comandi_partita.py` e
  `tests/test_game_controller.py`.
- Tutte e sole le 20 righe elencate vengono rimosse.
- Nessuna firma pubblica cambia.
- Nessuna logica di business o di controllo cambia.
- Nessuna docstring viene modificata.
- Nessun blocco `setup` o `teardown` viene introdotto, rimosso o alterato.
- Nessuna struttura di classe cambia.
- Nessuna dipendenza nuova viene introdotta.
- La suite finale attesa e' verde con target: 351 OK, 0 ERROR, 1 Skipped,
  0 FAIL.

## Rischi e Vincoli

### Vincoli

- Nessuna modifica a firme.
- Nessuna modifica a logica.
- Nessuna modifica a docstring.
- Nessuna modifica a setup/teardown.
- Nessuna modifica a struttura classi.
- Nessuna modifica a dipendenze.

### Rischi

Nessun rischio atteso: il fix e' una rimozione pura di output informativo non
contrattuale e non usato dagli assert.
