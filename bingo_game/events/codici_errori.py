from __future__ import annotations

from typing import Literal

#codici errori generici utilizzati un po ovunque
Codici_Errori_Generici = Literal[
    # Generici / infrastrutturali
    "NON_IMPLEMENTATO",
    "ERRORE_INTERNO",
]

#codici errori per ui, focus navigazione
Codici_Errori_Ui = Literal[
    # Input / prerequisiti (tipicamente lato giocatore/UI)
    "INPUT_NON_VALIDO",
    "NUMERO_NON_VALIDO",
    "NUMERO_TIPO_NON_VALIDO",
    # Helper / focus / navigazione (prefissi per area)
    "TABELLONE_NON_DISPONIBILE",
    "CARTELLA_STATO_INCOERENTE",
    "CARTELLE_NESSUNA_ASSEGNATA",
    "FOCUS_CARTELLA_NON_IMPOSTATO",
    "FOCUS_CARTELLA_FUORI_RANGE",
    "NUMERO_CARTELLA_FUORI_RANGE",
    "NUMERO_CARTELLA_TIPO_NON_VALIDO",
    "FOCUS_RIGA_NON_IMPOSTATA",
    "FOCUS_RIGA_FUORI_RANGE",
    "FOCUS_COLONNA_NON_IMPOSTATA",
    "FOCUS_COLONNA_FUORI_RANGE",
    # Annuncio vincite (prerequisiti specifici)
    "ANNUNCIO_CARTELLA_NON_SELEZIONATA",
    "ANNUNCIO_RIGA_NON_SELEZIONATA",
    "TIPO_VITTORIA_NON_VALIDO",
]


#codici di errori specifici per la partita
Codici_Errori_Partita = Literal[
    # Errori "strutturali" sul reclamo (indici, riferimenti)
    "RECLAMO_GIA_PRESENTE",
    "RECLAMO_ASSENTE",
    "CARTELLA_NON_TROVATA",
    "RIGA_NON_VALIDA",
    # Esiti di validazione in Partita
    "PREMIO_GIA_ASSEGNATO",
    "PREMIO_NON_DISPONIBILE",
    "VERIFICA_FALLITA",
    "PREREQUISITI_MANCANTI",
    "NUMERO_RIGA_FUORI_RANGE",
    "NUMERO_COLONNA_FUORI_RANGE",
]


#alias da riutilizzare per importare i vari tipi di errori definiti
Codici_Errori = Codici_Errori_Generici | Codici_Errori_Ui | Codici_Errori_Partita