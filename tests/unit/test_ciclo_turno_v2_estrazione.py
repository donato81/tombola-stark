"""
Test unitari — Fase F-1 del Ciclo Turno V2.

Verifica che dopo esegui_fase_estrazione() nessun giocatore automatico
abbia reclamo_turno impostato: i bot non ricevono più il reclamo
automatico durante l'estrazione (disaccoppiamento, Fase A).

Task F-1.
"""
from __future__ import annotations

import unittest

from bingo_game.cartella import Cartella
from bingo_game.partita import Partita
from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
from bingo_game.tabellone import Tabellone


def _crea_partita_con_bot(num_bot: int = 2) -> Partita:
    """Crea una partita avviata con un umano e num_bot bot."""
    tabellone = Tabellone()
    umano = GiocatoreUmano("Tester")
    umano.aggiungi_cartella(Cartella())
    bots = []
    for i in range(num_bot):
        bot = GiocatoreAutomatico(f"Bot{i + 1}")
        bot.aggiungi_cartella(Cartella())
        bots.append(bot)
    partita = Partita(tabellone, [umano] + bots)
    partita.avvia_partita()
    return partita


class TestEstrazioneNonImpostaReclaSoBot(unittest.TestCase):
    """
    Dopo esegui_fase_estrazione(), i bot non hanno reclamo_turno impostato
    automaticamente: il reclamo è responsabilità di dichiara_fine_fase_azione().
    """

    def test_bot_reclamo_turno_none_dopo_estrazione(self) -> None:
        """Nessun bot ha reclamo_turno != None subito dopo l'estrazione."""
        partita = _crea_partita_con_bot(num_bot=3)
        partita.esegui_fase_estrazione()

        bots = [g for g in partita.giocatori if g.is_automatico()]
        for bot in bots:
            self.assertIsNone(
                bot.reclamo_turno,
                f"Bot {bot.nome} ha reclamo_turno={bot.reclamo_turno!r} dopo estrazione.",
            )

    def test_bot_turno_dichiarato_concluso_false_dopo_estrazione(self) -> None:
        """Dopo l'estrazione i bot non hanno ancora dichiarato fine turno."""
        partita = _crea_partita_con_bot(num_bot=2)
        partita.esegui_fase_estrazione()

        bots = [g for g in partita.giocatori if g.is_automatico()]
        for bot in bots:
            self.assertFalse(
                bot.turno_dichiarato_concluso,
                f"Bot {bot.nome} ha turno_dichiarato_concluso=True dopo estrazione.",
            )

    def test_tutti_hanno_dichiarato_fine_false_dopo_estrazione(self) -> None:
        """tutti_hanno_dichiarato_fine() è False subito dopo l'estrazione."""
        partita = _crea_partita_con_bot(num_bot=1)
        partita.esegui_fase_estrazione()

        self.assertFalse(
            partita.tutti_hanno_dichiarato_fine(),
            "tutti_hanno_dichiarato_fine() deve essere False subito dopo l'estrazione.",
        )

    def test_bot_dichiarano_fine_dopo_estrazione(self) -> None:
        """Dopo estrazione i bot possono dichiarare fine con dichiara_fine_fase_azione()."""
        partita = _crea_partita_con_bot(num_bot=2)
        partita.esegui_fase_estrazione()

        bots = [g for g in partita.giocatori if g.is_automatico()]
        premi = partita.premi_gia_assegnati

        for bot in bots:
            bot.dichiara_fine_fase_azione(premi)
            self.assertTrue(bot.turno_dichiarato_concluso)

    def test_estrazione_multipla_no_reclami_accumulati(self) -> None:
        """Dopo più estrazioni i bot non accumulano reclami automatici."""
        partita = _crea_partita_con_bot(num_bot=2)
        bots = [g for g in partita.giocatori if g.is_automatico()]

        for _ in range(5):
            partita.esegui_fase_estrazione()
            for bot in bots:
                self.assertIsNone(
                    bot.reclamo_turno,
                    "Bot ha accumulato reclamo_turno dopo estrazione ripetuta.",
                )
            # Verifica e reset dello stato turno per il ciclo successivo
            partita.esegui_fase_verifica()

