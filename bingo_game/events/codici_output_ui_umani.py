from __future__ import annotations

from typing import Literal, Optional

# Codici per i messaggi "di output" destinati alla UI del giocatore umano.
# Sono template testuali che il renderer userà quando riceve eventi di output
# (es. riepiloghi, letture, risultati di ricerca), senza mettere queste frasi
# nei messaggi di sistema.
Codici_Output_Ui_Umani = Literal[
    # Riepilogo cartella corrente (2 righe)
    "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_1",
    "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_NESSUNO",
    "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_LISTA",
    # Limiti navigazione cartelle (1 riga)
    "UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MINIMO",
    "UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MASSIMO",
    # Limiti navigazione righe (1 riga)
    "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO",
    "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO",
    #navigazione per colonne
    "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO",
    "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO",
    # Visualizzazione cartella semplice (più righe)
    "UMANI_CARTELLA_SEMPLICE_INTESTAZIONE",
    "UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA",
    "UMANI_CARTELLA_SEMPLICE_PREFISSO_COLONNA",
    "UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA",
    # Visualizzazione cartella AVANZATA (asterischi + riepilogo per riga + footer)
    "UMANI_CARTELLA_AVVANZATA_INTESTAZIONE",
    "UMANI_RIGA_AVVANZATA_INTESTAZIONE",
    "UMANI_COLONNA_AVVANZATA_INTESTAZIONE",
    "UMANI_CARTELLA_AVVANZATA_ETICHETTA_SEGNATI_RIGA",
    "UMANI_COLONNA_AVVANZATA_ETICHETTA_SEGNATI",
    "UMANI_CARTELLA_AVVANZATA_SEGNATI_RIGA_NESSUNO",
    "UMANI_COLONNA_AVVANZATA_SEGNATI_NESSUNO",
    "UMANI_CARTELLA_AVVANZATA_FOOTER_RIEPILOGO",
    "UMANI_COLONNA_AVVANZATA_FOOTER_RIEPILOGO",
    #codici per segnazione dei numeri in cartella
    "UMANI_SEGNAZIONE_NUMERO_SEGNATO",
    "UMANI_SEGNAZIONE_NUMERO_GIA_SEGNATO",
    "UMANI_SEGNAZIONE_NUMERO_NON_PRESENTE",
    "UMANI_SEGNAZIONE_NUMERO_NON_ESTRATTO",
    # Ricerca numero nelle cartelle (output accessibile, 1+ righe)
    "UMANI_RICERCA_NUMERO_INTESTAZIONE",
    "UMANI_RICERCA_NUMERO_NON_TROVATO",
    "UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_SINGOLARE",
    "UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_PLURALE",
    "UMANI_RICERCA_NUMERO_RISULTATO_RIGA",
    "UMANI_RICERCA_NUMERO_STATO_SEGNATO",
    "UMANI_RICERCA_NUMERO_STATO_DA_SEGNARE",
    # codici per chiedere se un numero è estratto nel tabellone
    "UMANI_VERIFICA_NUMERO_ESTRATTO_SI",
    "UMANI_VERIFICA_NUMERO_ESTRATTO_NO",
    #codici per verificare ultimo numero estratto dal tabellone
    "UMANI_ULTIMO_NUMERO_ESTRATTO_PRESENTE",
    "UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO",
    # codici per richiesta al tabellone degli ultimi 5 numeri estratti.
    "UMANI_ULTIMI_NUMERI_ESTRATTI_PRESENTI",
    "UMANI_ULTIMI_NUMERI_ESTRATTI_NESSUNO",
    #codice per prima riga di intestazione per riepilogo tabellone
    "UMANI_RIEPILOGO_TABELLONE_RIGA_1",
    #frasi per stampa dei numeri estratti unificati per decina
    "UMANI_LISTA_NUMERI_ESTRATTI_INTESTAZIONE",
    "UMANI_LISTA_NUMERI_ESTRATTI_DECINA_LISTA",
    # Stato focus corrente (3 righe, con varianti "presente/nessuno")
    "UMANI_STATO_FOCUS_CORRENTE_CARTELLA_PRESENTE",
    "UMANI_STATO_FOCUS_CORRENTE_CARTELLA_NESSUNA",
    "UMANI_STATO_FOCUS_CORRENTE_RIGA_PRESENTE",
    "UMANI_STATO_FOCUS_CORRENTE_RIGA_NESSUNA",
    "UMANI_STATO_FOCUS_CORRENTE_COLONNA_PRESENTE",
    "UMANI_STATO_FOCUS_CORRENTE_COLONNA_NESSUNA",
    #codici per messaggi di invio reclamo vittoria
    "UMANI_RECLAMO_VITTORIA_TOMBOLA_REGISTRATO",
    "UMANI_RECLAMO_VITTORIA_RIGA_REGISTRATO",
    "UMANI_RECLAMO_VITTORIA_NOTA_VALIDAZIONE",
    "UMANI_FINE_TURNO_PASSATO",
    "UMANI_FINE_TURNO_PASSATO_CON_RECLAMO",
    # -----------------------------------------------------------------------
    # Game Loop v0.9.0
    # -----------------------------------------------------------------------
    "LOOP_NUMERO_ESTRATTO",
    "LOOP_PROMPT_COMANDO",
    "LOOP_HELP_COMANDI",
    "LOOP_HELP_FOCUS",
    "LOOP_QUIT_CONFERMA",
    "LOOP_QUIT_ANNULLATO",
    "LOOP_REPORT_FINALE_INTESTAZIONE",
    "LOOP_REPORT_FINALE_TURNI",
    "LOOP_REPORT_FINALE_ESTRATTI",
    "LOOP_REPORT_FINALE_VINCITORE",
    "LOOP_REPORT_FINALE_NESSUN_VINCITORE",
    "LOOP_REPORT_FINALE_PREMI",
    "LOOP_COMANDO_NON_RICONOSCIUTO",
]
