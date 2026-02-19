"""Costanti-chiave per la localizzazione del menu di configurazione TUI.

Definisce 9 costanti stringa usate come chiavi in MESSAGGI_CONFIGURAZIONE (it.py).
Pattern di riferimento: bingo_game/events/codici_errori.py
Version: v0.7.0
"""
from __future__ import annotations

# Alias di tipo: ogni costante è una stringa ordinaria
Codici_Configurazione = str

# Chiave: messaggio di benvenuto iniziale
CONFIG_BENVENUTO: Codici_Configurazione = "CONFIG_BENVENUTO"

# Chiave: messaggio di conferma e avvio partita
CONFIG_CONFERMA_AVVIO: Codici_Configurazione = "CONFIG_CONFERMA_AVVIO"

# Chiave: prompt richiesta nome giocatore
CONFIG_RICHIESTA_NOME: Codici_Configurazione = "CONFIG_RICHIESTA_NOME"

# Chiave: prompt richiesta numero di bot
CONFIG_RICHIESTA_BOT: Codici_Configurazione = "CONFIG_RICHIESTA_BOT"

# Chiave: prompt richiesta numero di cartelle
CONFIG_RICHIESTA_CARTELLE: Codici_Configurazione = "CONFIG_RICHIESTA_CARTELLE"

# Chiave: errore nome vuoto dopo strip
CONFIG_ERRORE_NOME_VUOTO: Codici_Configurazione = "CONFIG_ERRORE_NOME_VUOTO"

# Chiave: errore nome superiore a 15 caratteri
CONFIG_ERRORE_NOME_TROPPO_LUNGO: Codici_Configurazione = "CONFIG_ERRORE_NOME_TROPPO_LUNGO"

# Chiave: errore numero bot fuori range (1–7)
CONFIG_ERRORE_BOT_RANGE: Codici_Configurazione = "CONFIG_ERRORE_BOT_RANGE"

# Chiave: errore numero cartelle fuori range (1–6)
CONFIG_ERRORE_CARTELLE_RANGE: Codici_Configurazione = "CONFIG_ERRORE_CARTELLE_RANGE"
