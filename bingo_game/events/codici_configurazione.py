from __future__ import annotations

from typing import Literal

# Chiavi informative (benvenuto e conferma avvio)
Codici_Configurazione_Info = Literal[
    "CONFIG_BENVENUTO",
    "CONFIG_CONFERMA_AVVIO",
]

# Chiavi prompt di input (3 campi sequenziali)
Codici_Configurazione_Prompt = Literal[
    "CONFIG_RICHIESTA_NOME",
    "CONFIG_RICHIESTA_BOT",
    "CONFIG_RICHIESTA_CARTELLE",
]

# Chiavi errori di validazione nome
Codici_Configurazione_Errori_Nome = Literal[
    "CONFIG_ERRORE_NOME_VUOTO",
    "CONFIG_ERRORE_NOME_TROPPO_LUNGO",
]

# Chiavi errori di validazione range numerico
Codici_Configurazione_Errori_Range = Literal[
    "CONFIG_ERRORE_BOT_RANGE",
    "CONFIG_ERRORE_CARTELLE_RANGE",
]

# Alias unificato da usare nelle annotazioni di tipo
Codici_Configurazione = (
    Codici_Configurazione_Info
    | Codici_Configurazione_Prompt
    | Codici_Configurazione_Errori_Nome
    | Codici_Configurazione_Errori_Range
)
