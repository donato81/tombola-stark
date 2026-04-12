"""
Test unitari per ComandiGiocatoreUmano.stato_premi() e .dettaglio_premi() (v1.2.0).

Verifica:
- stato_premi() con ultimo_premio_evento=None → testo "Nessun premio..."
- stato_premi() con evento presente → testo con tipo e vincitore
- stato_premi() con tutti i premi chiusi → "Tutti i premi..."
- dettaglio_premi() con premi_tipo_chiusi vuoto → fallback
- dettaglio_premi() con premi presenti → elenco formattato

Riferimento: docs/3 - coding plans/PLAN_lettura_nvda_stato_premi_v1.2.0.md — Fase 2
"""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from bingo_game.comandi_partita import ComandiGiocatoreUmano
from bingo_game.tabellone import Tabellone
from bingo_game.partita import Partita


def _crea_comandi(
    ultimo_premio: dict | None = None,
    premi_tipo_chiusi: set | None = None,
) -> ComandiGiocatoreUmano:
    """Crea un ComandiGiocatoreUmano con una Partita minimale configurata."""
    tabellone = Tabellone()
    partita = Partita(tabellone=tabellone, giocatori=[])
    partita.ultimo_premio_evento = ultimo_premio
    partita.premi_tipo_chiusi = premi_tipo_chiusi if premi_tipo_chiusi is not None else set()

    comandi = ComandiGiocatoreUmano.__new__(ComandiGiocatoreUmano)
    comandi._partita = partita
    comandi._giocatore = None
    comandi._tipo_navigazione_corrente = "riga"
    return comandi


class TestStatoPremiNessunPremio(unittest.TestCase):
    """stato_premi() con nessun premio assegnato."""

    def test_nessun_premio_prossimo_ambo(self) -> None:
        comandi = _crea_comandi()
        testo = comandi.stato_premi()
        self.assertIn("Nessun premio", testo)
        self.assertIn("ambo", testo)

    def test_nessun_premio_non_contiene_vincitore(self) -> None:
        comandi = _crea_comandi()
        testo = comandi.stato_premi()
        self.assertNotIn("vinto da", testo)


class TestStatoPremiConEvento(unittest.TestCase):
    """stato_premi() con ultimo_premio_evento valorizzato."""

    def test_contiene_tipo_e_vincitore(self) -> None:
        evento = {"giocatore": "Mario", "cartella": 0, "premio": "ambo", "riga": 1}
        comandi = _crea_comandi(
            ultimo_premio=evento,
            premi_tipo_chiusi={"ambo"},
        )
        testo = comandi.stato_premi()
        self.assertIn("ambo", testo)
        self.assertIn("Mario", testo)

    def test_prossimo_premio_terno_dopo_ambo(self) -> None:
        evento = {"giocatore": "Luigi", "cartella": 0, "premio": "ambo", "riga": 0}
        comandi = _crea_comandi(
            ultimo_premio=evento,
            premi_tipo_chiusi={"ambo"},
        )
        testo = comandi.stato_premi()
        self.assertIn("terno", testo)

    def test_prossimo_tombola_se_quasi_tutto_chiuso(self) -> None:
        evento = {"giocatore": "Pippo", "cartella": 0, "premio": "cinquina", "riga": 2}
        comandi = _crea_comandi(
            ultimo_premio=evento,
            premi_tipo_chiusi={"ambo", "terno", "quaterna", "cinquina"},
        )
        testo = comandi.stato_premi()
        self.assertIn("tombola", testo)


class TestStatoPremiTuttiChiusi(unittest.TestCase):
    """stato_premi() con tutti i premi chiusi."""

    def test_tutti_assegnati(self) -> None:
        comandi = _crea_comandi(
            premi_tipo_chiusi={"ambo", "terno", "quaterna", "cinquina", "tombola"},
        )
        testo = comandi.stato_premi()
        self.assertIn("Tutti i premi", testo)


class TestDettaglioPremiVuoto(unittest.TestCase):
    """dettaglio_premi() con nessun premio assegnato."""

    def test_fallback_nessun_premio(self) -> None:
        comandi = _crea_comandi()
        testo = comandi.dettaglio_premi()
        self.assertIn("Nessun premio", testo)


class TestDettaglioPremiConPremi(unittest.TestCase):
    """dettaglio_premi() con premi_tipo_chiusi valorizzato."""

    def test_contiene_header_e_tipi(self) -> None:
        comandi = _crea_comandi(
            premi_tipo_chiusi={"ambo", "terno"},
        )
        testo = comandi.dettaglio_premi()
        self.assertIn("Premi assegnati", testo)
        self.assertIn("ambo", testo)
        self.assertIn("terno", testo)

    def test_non_contiene_premi_non_assegnati(self) -> None:
        comandi = _crea_comandi(
            premi_tipo_chiusi={"ambo"},
        )
        testo = comandi.dettaglio_premi()
        self.assertNotIn("terno", testo)
        self.assertNotIn("quattro", testo)


if __name__ == "__main__":
    unittest.main()
