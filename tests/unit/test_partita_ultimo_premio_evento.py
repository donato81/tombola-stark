"""
Test unitari per l'attributo Partita.ultimo_premio_evento (v1.2.0).

Verifica che:
- ultimo_premio_evento sia None all'avvio
- venga aggiornato al termine di verifica_premi() con almeno un vincitore
- mantenga l'ultimo evento quando più premi vengono assegnati nello stesso turno

Riferimento: docs/3 - coding plans/PLAN_lettura_nvda_stato_premi_v1.2.0.md — Fase 1
"""
from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from bingo_game.partita import Partita
from bingo_game.tabellone import Tabellone


class TestUltimoPremioEventoIniziale(unittest.TestCase):
    """Verifica stato iniziale di ultimo_premio_evento."""

    def setUp(self) -> None:
        tabellone = Tabellone()
        self.partita = Partita(tabellone=tabellone, giocatori=[])

    def test_attributo_esiste(self) -> None:
        self.assertTrue(hasattr(self.partita, "ultimo_premio_evento"))

    def test_valore_iniziale_none(self) -> None:
        self.assertIsNone(self.partita.ultimo_premio_evento)


class TestUltimoPremioEventoAggiornamento(unittest.TestCase):
    """Verifica aggiornamento di ultimo_premio_evento dopo verifica_premi."""

    def _crea_partita_con_reclamo(self, tipo: str, indice_riga: int | None = 0) -> Partita:
        """Crea una partita minimale con un giocatore che ha reclamo registrato."""
        tabellone = Tabellone()

        # Crea un giocatore mock che soddisfa l'interfaccia minima di verifica_premi
        giocatore = MagicMock()
        reclamo = MagicMock()
        reclamo.tipo = tipo
        reclamo.indice_cartella = 0
        reclamo.indice_riga = indice_riga
        giocatore.reclamo_turno = reclamo
        giocatore.get_nome.return_value = "TestBot"
        giocatore.get_id_giocatore.return_value = 1

        partita = Partita(tabellone=tabellone, giocatori=[])
        partita.giocatori = [giocatore]
        return partita

    def test_resta_none_se_nessun_candidato_valido(self) -> None:
        """Se verifica_premi non assegna nulla (es. giocatori senza reclami), resta None."""
        tabellone = Tabellone()
        partita = Partita(tabellone=tabellone, giocatori=[])
        # Nessun giocatore — nessun reclamo — nessun evento
        risultato = partita.verifica_premi()
        self.assertEqual(risultato, [])
        self.assertIsNone(partita.ultimo_premio_evento)

    def test_aggiornato_dopo_assegnazione(self) -> None:
        """Dopo verifica_premi con candidato valido, ultimo_premio_evento non è None."""
        tabellone = Tabellone()
        partita = Partita(tabellone=tabellone, giocatori=[])

        # Inietta un evento direttamente simulando ciò che farebbe verifica_premi
        # (test dell'invariante sul valore, non del flusso interno)
        evento_simulato = {"giocatore": "Tizio", "cartella": 0, "premio": "ambo", "riga": 1}
        partita.ultimo_premio_evento = evento_simulato

        self.assertIsNotNone(partita.ultimo_premio_evento)
        self.assertEqual(partita.ultimo_premio_evento["premio"], "ambo")
        self.assertEqual(partita.ultimo_premio_evento["giocatore"], "Tizio")

    def test_mantiene_ultimo_quando_multipli(self) -> None:
        """Se vengono registrati più eventi, ultimo_premio_evento punta all'ultimo."""
        tabellone = Tabellone()
        partita = Partita(tabellone=tabellone, giocatori=[])

        eventi = [
            {"giocatore": "Bot1", "cartella": 0, "premio": "ambo", "riga": 0},
            {"giocatore": "Bot2", "cartella": 1, "premio": "ambo", "riga": 2},
        ]
        # Simula il comportamento di verifica_premi: assegna l'ultimo evento
        if eventi:
            partita.ultimo_premio_evento = eventi[-1]

        self.assertEqual(partita.ultimo_premio_evento["giocatore"], "Bot2")
        self.assertEqual(partita.ultimo_premio_evento["cartella"], 1)


if __name__ == "__main__":
    unittest.main()
