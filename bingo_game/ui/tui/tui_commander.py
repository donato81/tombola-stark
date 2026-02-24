"""
tui_commander.py — Modulo di input rapido per la TUI della partita (v0.10.0).

Responsabilità:
- Leggere un singolo tasto tramite msvcrt (Windows-only), gestendo
  correttamente i tasti estesi a 2 byte (frecce, PagSu, PagGiu).
- Classificare il tasto in un ComandoTasto che descrive:
    * il tipo di azione attesa (diretta, prompt numerico, conferma S/N,
      selezione cartella, tasto non valido);
    * il nome identificativo del comando (stringa costante);
    * un valore opzionale (usato solo per SELEZIONA_CARTELLA).
- Non eseguire comandi e non accedere al dominio.
  L'esecuzione dei comandi avviene esclusivamente in tui_partita.py.

Struttura del modulo:
    TipoComando  — enum con le 5 classificazioni di comportamento atteso.
    ComandoTasto — dataclass (frozen) che descrive comando + tipo + valore.
    leggi_tasto() -> str
        Legge 1 o 2 byte con msvcrt.getwch e restituisce la stringa-chiave
        corrispondente ai valori definiti in codici_tasti_tui.py.
    comando_da_tasto(tasto: str) -> ComandoTasto
        Mappa la stringa-tasto al ComandoTasto corrispondente.

Nota nomenclatura nomi comandi:
    I valori stringa di ComandoTasto.nome corrispondono 1:1 ai nomi dei metodi
    di GiocatoreUmano (o wrapper) che tui_partita.py dovrà invocare.
    Eccezioni: "esci" (azione loop), "non_valido" (sentinel).

Avvertenza piattaforma:
    msvcrt è disponibile solo su Windows. In ambienti di test non-Windows
    il modulo deve essere mockato.

Riferimenti:
    - documentations/2 - project/DESIGN_tasti-rapidi-tui.md (Gruppi 1-10)
    - documentations/3 - planning/PLAN_tasti-rapidi-tui_v0.10.0.md (Fase 2)
    - bingo_game/ui/tui/codici_tasti_tui.py (costanti tasti)
"""

from __future__ import annotations

import enum
import logging
import msvcrt
from dataclasses import dataclass
from typing import Optional

from bingo_game.ui.tui.codici_tasti_tui import (
    FRECCIA_GIU,
    FRECCIA_SINISTRA,
    FRECCIA_DESTRA,
    FRECCIA_SU,
    PAG_GIU,
    PAG_SU,
    PREFISSO_TASTO_ESTESO,
    TASTI_CARTELLE,
    TASTO_1,
    TASTO_2,
    TASTO_3,
    TASTO_4,
    TASTO_5,
    TASTO_6,
    TASTO_A,
    TASTO_C,
    TASTO_D,
    TASTO_E,
    TASTO_F,
    TASTO_G,
    TASTO_H,
    TASTO_I,
    TASTO_L,
    TASTO_N,
    TASTO_O,
    TASTO_P,
    TASTO_PUNTO_INTERROGATIVO,
    TASTO_Q,
    TASTO_R,
    TASTO_S,
    TASTO_U,
    TASTO_V,
    TASTO_W,
    TASTO_X,
    TASTO_Z,
)

_logger_tui = logging.getLogger("tombola_stark.tui")

# ---------------------------------------------------------------------------
# TipoComando
# ---------------------------------------------------------------------------


class TipoComando(enum.Enum):
    """Classificazione del comportamento atteso dal game loop dopo un tasto.

    Valori:
        AZIONE_DIRETTA       — Il comando si esegue immediatamente senza
                               ulteriore input utente.
        RICHIEDE_PROMPT_NUM  — Prima di eseguire il comando il loop deve
                               chiedere all'utente un numero intero tramite
                               input(). Input non valido produce un messaggio
                               di errore e un nuovo prompt.
        RICHIEDE_CONFERMA    — Prima di eseguire il loop deve chiedere
                               conferma S/N. Usato solo per TASTO_X (uscita).
        SELEZIONA_CARTELLA   — Imposta il focus sulla cartella il cui numero
                               (1-based) è in ComandoTasto.valore. Non serve
                               prompt aggiuntivo.
        TASTO_NON_VALIDO     — Tasto non riconosciuto. Il loop deve mostrare
                               il messaggio di tasto non valido e continuare.
    """

    AZIONE_DIRETTA = "azione_diretta"
    RICHIEDE_PROMPT_NUM = "richiede_prompt_num"
    RICHIEDE_CONFERMA = "richiede_conferma"
    SELEZIONA_CARTELLA = "seleziona_cartella"
    TASTO_NON_VALIDO = "tasto_non_valido"


# ---------------------------------------------------------------------------
# ComandoTasto
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ComandoTasto:
    """Struttura dati immutabile che descrive il comando associato a un tasto.

    Attributi:
        tipo  (TipoComando): classificazione del comportamento atteso.
        nome  (str): nome identificativo del comando; corrisponde al nome del
                     metodo GiocatoreUmano che tui_partita.py deve invocare.
                     "esci" e "non_valido" sono eccezioni (gestite nel loop).
        valore (int | None): usato esclusivamente da SELEZIONA_CARTELLA per
                             trasportare il numero cartella 1-based.
    """

    tipo: TipoComando
    nome: str
    valore: Optional[int] = None


# ---------------------------------------------------------------------------
# Istanze singleton per ogni comando (evitano allocazioni ripetute)
# ---------------------------------------------------------------------------

# -- Gruppo 1: navigazione riga semplice --
_CMD_FRECCIA_SU = ComandoTasto(TipoComando.AZIONE_DIRETTA, "sposta_focus_riga_su_semplice")
_CMD_FRECCIA_GIU = ComandoTasto(TipoComando.AZIONE_DIRETTA, "sposta_focus_riga_giu_semplice")

# -- Gruppo 2: navigazione riga avanzata --
_CMD_A = ComandoTasto(TipoComando.AZIONE_DIRETTA, "sposta_focus_riga_su_avanzata")
_CMD_Z = ComandoTasto(TipoComando.AZIONE_DIRETTA, "sposta_focus_riga_giu_avanzata")

# -- Gruppo 3: navigazione colonna semplice --
_CMD_FRECCIA_SINISTRA = ComandoTasto(TipoComando.AZIONE_DIRETTA, "sposta_focus_colonna_sinistra")
_CMD_FRECCIA_DESTRA = ComandoTasto(TipoComando.AZIONE_DIRETTA, "sposta_focus_colonna_destra")

# -- Gruppo 4: navigazione colonna avanzata --
_CMD_Q = ComandoTasto(TipoComando.AZIONE_DIRETTA, "sposta_focus_colonna_sinistra_avanzata")
_CMD_W = ComandoTasto(TipoComando.AZIONE_DIRETTA, "sposta_focus_colonna_destra_avanzata")

# -- Gruppo 5: salto diretto con prompt numerico --
_CMD_R = ComandoTasto(TipoComando.RICHIEDE_PROMPT_NUM, "vai_a_riga_avanzata")
_CMD_C = ComandoTasto(TipoComando.RICHIEDE_PROMPT_NUM, "vai_a_colonna_avanzata")

# -- Gruppo 6: navigazione cartella (PagSu / PagGiu) --
# I tasti 1-6 sono gestiti dinamicamente in comando_da_tasto (valore variabile).
_CMD_PAG_SU = ComandoTasto(TipoComando.AZIONE_DIRETTA, "riepilogo_cartella_precedente")
_CMD_PAG_GIU = ComandoTasto(TipoComando.AZIONE_DIRETTA, "riepilogo_cartella_successiva")

# -- Gruppo 7: visualizzazione cartella --
_CMD_D = ComandoTasto(TipoComando.AZIONE_DIRETTA, "visualizza_cartella_corrente_semplice")
_CMD_F = ComandoTasto(TipoComando.AZIONE_DIRETTA, "visualizza_cartella_corrente_avanzata")
_CMD_G = ComandoTasto(TipoComando.AZIONE_DIRETTA, "visualizza_tutte_cartelle_semplice")
_CMD_H = ComandoTasto(TipoComando.AZIONE_DIRETTA, "visualizza_tutte_cartelle_avanzata")

# -- Gruppo 8: consultazione tabellone --
_CMD_U = ComandoTasto(TipoComando.AZIONE_DIRETTA, "comunica_ultimo_numero_estratto")
_CMD_I = ComandoTasto(TipoComando.AZIONE_DIRETTA, "visualizza_ultimi_numeri_estratti")
_CMD_O = ComandoTasto(TipoComando.AZIONE_DIRETTA, "riepilogo_tabellone")
_CMD_L = ComandoTasto(TipoComando.AZIONE_DIRETTA, "lista_numeri_estratti")
_CMD_E = ComandoTasto(TipoComando.RICHIEDE_PROMPT_NUM, "verifica_numero_estratto")
_CMD_N = ComandoTasto(TipoComando.RICHIEDE_PROMPT_NUM, "cerca_numero_nelle_cartelle")

# -- Gruppo 9: orientamento --
_CMD_PUNTO_INTERROGATIVO = ComandoTasto(TipoComando.AZIONE_DIRETTA, "stato_focus_corrente")

# -- Gruppo 10: azioni di gioco --
_CMD_S = ComandoTasto(TipoComando.RICHIEDE_PROMPT_NUM, "segna_numero_manuale")
_CMD_V = ComandoTasto(TipoComando.RICHIEDE_PROMPT_NUM, "annuncia_vittoria")
_CMD_P = ComandoTasto(TipoComando.AZIONE_DIRETTA, "passa_turno")
_CMD_X = ComandoTasto(TipoComando.RICHIEDE_CONFERMA, "esci")

# -- Sentinel per tasto non valido --
_CMD_NON_VALIDO = ComandoTasto(TipoComando.TASTO_NON_VALIDO, "non_valido")

# ---------------------------------------------------------------------------
# Tabella di mappatura principale: tasto (str) → ComandoTasto
# I tasti numerici 1-6 (SELEZIONA_CARTELLA) NON sono in questa tabella:
# vengono gestiti con valore dinamico in comando_da_tasto().
# ---------------------------------------------------------------------------

_MAPPA_TASTI: dict[str, ComandoTasto] = {
    # Gruppo 1
    FRECCIA_SU: _CMD_FRECCIA_SU,
    FRECCIA_GIU: _CMD_FRECCIA_GIU,
    # Gruppo 2
    TASTO_A: _CMD_A,
    TASTO_Z: _CMD_Z,
    # Gruppo 3
    FRECCIA_SINISTRA: _CMD_FRECCIA_SINISTRA,
    FRECCIA_DESTRA: _CMD_FRECCIA_DESTRA,
    # Gruppo 4
    TASTO_Q: _CMD_Q,
    TASTO_W: _CMD_W,
    # Gruppo 5
    TASTO_R: _CMD_R,
    TASTO_C: _CMD_C,
    # Gruppo 6
    PAG_SU: _CMD_PAG_SU,
    PAG_GIU: _CMD_PAG_GIU,
    # Gruppo 7
    TASTO_D: _CMD_D,
    TASTO_F: _CMD_F,
    TASTO_G: _CMD_G,
    TASTO_H: _CMD_H,
    # Gruppo 8
    TASTO_U: _CMD_U,
    TASTO_I: _CMD_I,
    TASTO_O: _CMD_O,
    TASTO_L: _CMD_L,
    TASTO_E: _CMD_E,
    TASTO_N: _CMD_N,
    # Gruppo 9
    TASTO_PUNTO_INTERROGATIVO: _CMD_PUNTO_INTERROGATIVO,
    # Gruppo 10
    TASTO_S: _CMD_S,
    TASTO_V: _CMD_V,
    TASTO_P: _CMD_P,
    TASTO_X: _CMD_X,
}

# ---------------------------------------------------------------------------
# API pubblica
# ---------------------------------------------------------------------------


def leggi_tasto() -> str:
    """Legge un singolo tasto dalla tastiera usando msvcrt (Windows-only).

    Gestione tasti estesi (2 byte):
        Su Windows, msvcrt.getwch() restituisce il prefisso ``\\xe0`` (o ``\\x00``)
        per i tasti speciali (frecce, PagSu, PagGiu, Ins, Del, ecc.).
        In quel caso viene letto immediatamente un secondo byte per ottenere
        la sequenza completa, coerente con le costanti in codici_tasti_tui.py.

    Ritorna:
        str: Stringa di 1 o 2 caratteri che identifica il tasto premuto.
             Corrisponde a una delle costanti in codici_tasti_tui.py.

    Note:
        Questa funzione è bloccante: attende la pressione di un tasto.
        Non richiede la pressione di Invio.

    Avvertenza:
        msvcrt non è disponibile su Linux/macOS. Nei test unitari mockare
        questa funzione con unittest.mock.patch.
    """
    primo_byte: str = msvcrt.getwch()

    if primo_byte in ("\x00", PREFISSO_TASTO_ESTESO):
        secondo_byte: str = msvcrt.getwch()
        tasto = primo_byte + secondo_byte
        _logger_tui.debug("leggi_tasto: tasto esteso letto — %r", tasto)
        return tasto

    _logger_tui.debug("leggi_tasto: tasto semplice letto — %r", primo_byte)
    return primo_byte


def comando_da_tasto(tasto: str) -> ComandoTasto:
    """Mappa una stringa-tasto al ComandoTasto corrispondente.

    Regole di mapping:
        1. Se il tasto è uno dei tasti numerici di cartella (1-6), restituisce
           un ComandoTasto di tipo SELEZIONA_CARTELLA con valore = numero cartella
           1-based (int). Un'istanza distinta viene creata per ogni tasto cartella
           così da trasportare il numero corretto nel campo valore.
        2. Per tutti gli altri tasti riconosciuti usa la tabella _MAPPA_TASTI
           che restituisce istanze singleton (nessuna allocazione).
        3. Se il tasto non è riconosciuto restituisce _CMD_NON_VALIDO.

    Parametri:
        tasto (str): stringa di 1 o 2 caratteri restituita da leggi_tasto().

    Ritorna:
        ComandoTasto: istanza frozen che descrive l'azione attesa dal loop.

    Esempio:
        >>> cmd = comando_da_tasto(FRECCIA_SU)
        >>> cmd.tipo == TipoComando.AZIONE_DIRETTA
        True
        >>> cmd.nome
        'sposta_focus_riga_su_semplice'

        >>> cmd = comando_da_tasto("3")
        >>> cmd.tipo == TipoComando.SELEZIONA_CARTELLA
        True
        >>> cmd.valore
        3
    """
    # Caso speciale: tasti numerici 1-6 per selezione diretta cartella.
    if tasto in TASTI_CARTELLE:
        numero_cartella = int(tasto)
        _logger_tui.debug(
            "comando_da_tasto: selezione cartella %d", numero_cartella
        )
        return ComandoTasto(
            TipoComando.SELEZIONA_CARTELLA,
            "imposta_focus_cartella",
            numero_cartella,
        )

    # Lookup nella tabella principale.
    comando = _MAPPA_TASTI.get(tasto, _CMD_NON_VALIDO)

    if comando is _CMD_NON_VALIDO:
        _logger_tui.debug("comando_da_tasto: tasto non riconosciuto — %r", tasto)
    else:
        _logger_tui.debug(
            "comando_da_tasto: %r -> tipo=%s nome=%s",
            tasto,
            comando.tipo.value,
            comando.nome,
        )

    return comando
