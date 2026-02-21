"""
Test di regressione per Bug 1 v0.9.1:
`imposta_focus_cartella` chiamava `reset_focus_riga_e_colonna` (senza underscore)
invece di `_reset_focus_riga_e_colonna` (con underscore).

Verifica che dopo `imposta_focus_cartella(1)` il focus sia impostato correttamente
senza sollevare AttributeError.

Test di regressione per Anomalia A v0.9.1:
`sposta_focus_riga_giu_avanzata` chiamava `_inizializza_focus_riga_se_manca` (inesistente)
invece di `_esito_inizializza_focus_riga_se_manca`.
"""
from __future__ import annotations

import pytest

from bingo_game.cartella import Cartella
from bingo_game.players.giocatore_umano import GiocatoreUmano


def test_imposta_focus_cartella_non_solleva_eccezioni():
    """imposta_focus_cartella(1) non deve sollevare AttributeError (regressione Bug 1 v0.9.1)."""
    giocatore = GiocatoreUmano("TestReg", id_giocatore=1)
    giocatore.aggiungi_cartella(Cartella())

    # Non deve sollevare eccezioni
    esito = giocatore.imposta_focus_cartella(1)

    assert esito.ok, f"imposta_focus_cartella(1) deve avere successo, errore: {esito.errore}"


def test_imposta_focus_cartella_imposta_indice_zero():
    """Dopo imposta_focus_cartella(1), _indice_cartella_focus deve essere 0."""
    giocatore = GiocatoreUmano("TestReg", id_giocatore=1)
    giocatore.aggiungi_cartella(Cartella())

    giocatore.imposta_focus_cartella(1)

    assert giocatore._indice_cartella_focus == 0


def test_imposta_focus_cartella_cambio_cartella_non_solleva_eccezioni():
    """imposta_focus_cartella(2) su 2 cartelle non deve sollevare AttributeError (reset riga/colonna)."""
    giocatore = GiocatoreUmano("TestReg", id_giocatore=1)
    giocatore.aggiungi_cartella(Cartella())
    giocatore.aggiungi_cartella(Cartella())

    # Prima imposta su cartella 1
    giocatore.imposta_focus_cartella(1)
    # Poi cambia a cartella 2 — triggera il reset riga/colonna (il bug precedente qui)
    esito = giocatore.imposta_focus_cartella(2)

    assert esito.ok, f"Cambio focus cartella deve avere successo, errore: {esito.errore}"
    assert giocatore._indice_cartella_focus == 1


def test_sposta_focus_riga_giu_avanzata_con_riga_focus_none_non_solleva_eccezioni():
    """sposta_focus_riga_giu_avanzata() con _indice_riga_focus=None non deve sollevare
    AttributeError (regressione Anomalia A v0.9.1)."""
    giocatore = GiocatoreUmano("TestAnomaliaA", id_giocatore=1)
    giocatore.aggiungi_cartella(Cartella())
    giocatore.imposta_focus_cartella(1)
    giocatore._indice_riga_focus = None

    esito = giocatore.sposta_focus_riga_giu_avanzata()

    assert esito.ok, (
        f"sposta_focus_riga_giu_avanzata() deve avere successo con riga_focus=None, "
        f"errore: {esito.errore}"
    )


def test_imposta_focus_cartella_fallback_imposta_indice_zero():
    """imposta_focus_cartella_fallback() imposta _indice_cartella_focus a 0 [v0.9.1 Anomalia B]."""
    giocatore = GiocatoreUmano("TestFallback", id_giocatore=1)
    giocatore.aggiungi_cartella(Cartella())

    giocatore.imposta_focus_cartella_fallback()

    assert giocatore._indice_cartella_focus == 0


def test_imposta_focus_cartella_fallback_senza_cartelle_non_modifica():
    """imposta_focus_cartella_fallback() non modifica stato se cartelle è vuoto [v0.9.1 Anomalia B]."""
    giocatore = GiocatoreUmano("TestFallback", id_giocatore=1)

    giocatore.imposta_focus_cartella_fallback()

    assert giocatore._indice_cartella_focus is None
