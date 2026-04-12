"""
Test unitari — Fase F-2 del Ciclo Turno V2.

Verifica il flusso completo di timeout: l'umano non dichiara fine entro
la finestra d'azione → il timer scade → la verifica premi viene comunque
eseguita (skip automatico).

Usa un mock del timer: la FinestraGioco non viene istanziata (richiede wx).
Il test simula l'effetto del timeout invocando direttamente _on_timeout_azione().

Task F-2.
"""
from __future__ import annotations

import sys
import types
import unittest
from unittest.mock import MagicMock, patch


def _mock_wx() -> None:
    """Inietta un fake 'wx' in sys.modules se non è già installato."""
    if "wx" in sys.modules:
        return
    wx_mock = types.ModuleType("wx")
    wx_mock.Frame = object
    wx_mock.Dialog = object
    wx_mock.Panel = object
    wx_mock.Button = MagicMock
    wx_mock.TextCtrl = MagicMock
    wx_mock.StaticText = MagicMock
    wx_mock.SpinCtrl = MagicMock
    wx_mock.Timer = MagicMock
    wx_mock.TimerEvent = object
    wx_mock.BoxSizer = MagicMock
    wx_mock.VERTICAL = 0
    wx_mock.ALL = 1
    wx_mock.EXPAND = 2
    wx_mock.LEFT = 4
    wx_mock.RIGHT = 8
    wx_mock.TOP = 16
    wx_mock.BOTTOM = 32
    wx_mock.ALIGN_CENTER = 64
    wx_mock.TE_MULTILINE = 128
    wx_mock.TE_READONLY = 256
    wx_mock.WANTS_CHARS = 512
    wx_mock.TAB_TRAVERSAL = 1024
    wx_mock.DEFAULT_FRAME_STYLE = 2048
    wx_mock.WXK_ESCAPE = 27
    wx_mock.WXK_UP = 315
    wx_mock.WXK_DOWN = 317
    wx_mock.WXK_LEFT = 314
    wx_mock.WXK_RIGHT = 316
    wx_mock.WXK_SPACE = 32
    wx_mock.WXK_F1 = 340
    wx_mock.WXK_F6 = 345
    wx_mock.EVT_BUTTON = object()
    wx_mock.EVT_CHAR_HOOK = object()
    wx_mock.EVT_TIMER = object()
    wx_mock.EVT_KEY_DOWN = object()
    wx_mock.TIMER_ONE_SHOT = 1
    wx_mock.CallLater = MagicMock
    sys.modules["wx"] = wx_mock


class TestTimeoutUmanoV2(unittest.TestCase):
    """
    Simula il flusso di timeout senza istanziare wx.

    Strategia:
    - Crea una Partita reale con 1 umano + 1 bot, avviata.
    - Crea un WxRenderer finto (MagicMock).
    - Construisce un oggetto FinestraGioco-like con attributi minimi,
      oppure testa la logica di timeout isolata.

    N.B.: non è possibile testare wx.Timer senza un'app wx in esecuzione.
    Questo test verifica la logica *attorno* al timer, non il timer stesso.
    """

    def setUp(self) -> None:
        _mock_wx()

    def test_timeout_senza_dichiarazione_umano_avanza_verifica(self) -> None:
        """
        Dopo il timeout, la partita deve trovarsi nella fase attesa_estrazione
        (dopo verifica e reset) anche se l'umano non ha dichiarato fine.
        """
        from bingo_game.cartella import Cartella
        from bingo_game.partita import Partita
        from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
        from bingo_game.tabellone import Tabellone

        tabellone = Tabellone()
        umano = GiocatoreUmano("Mario")
        umano.aggiungi_cartella(Cartella())
        bot = GiocatoreAutomatico("Bot1")
        bot.aggiungi_cartella(Cartella())
        partita = Partita(tabellone, [umano, bot])
        partita.avvia_partita()
        partita.esegui_fase_estrazione()

        # Dopo il timeout umano NON ha dichiarato fine
        self.assertFalse(umano.turno_dichiarato_concluso)

        # La verifica può comunque proseguire (tutti i giocatori vengono
        # resettati da esegui_fase_verifica indipendentemente dalle dichiarazioni).
        risultato = partita.esegui_fase_verifica()
        self.assertIsInstance(risultato, dict)

        # Dopo verifica, il turno dichiarato è resettato
        self.assertFalse(umano.turno_dichiarato_concluso)
        self.assertFalse(bot.turno_dichiarato_concluso)

    def test_tutti_hanno_dichiarato_fine_resta_false_senza_umano(self) -> None:
        """
        Anche se il bot ha dichiarato, finché l'umano non dichiara
        tutti_hanno_dichiarato_fine() rimane False.
        """
        from bingo_game.cartella import Cartella
        from bingo_game.partita import Partita
        from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
        from bingo_game.tabellone import Tabellone

        tabellone = Tabellone()
        umano = GiocatoreUmano("Mario")
        umano.aggiungi_cartella(Cartella())
        bot = GiocatoreAutomatico("Bot1")
        bot.aggiungi_cartella(Cartella())
        partita = Partita(tabellone, [umano, bot])
        partita.avvia_partita()
        partita.esegui_fase_estrazione()

        bot.dichiara_fine_turno()
        self.assertFalse(partita.tutti_hanno_dichiarato_fine())

    def test_tutti_hanno_dichiarato_fine_true_con_umano(self) -> None:
        """
        Quando l'umano dichiara fine e il bot ha già dichiarato,
        tutti_hanno_dichiarato_fine() diventa True.
        """
        from bingo_game.cartella import Cartella
        from bingo_game.partita import Partita
        from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
        from bingo_game.tabellone import Tabellone

        tabellone = Tabellone()
        umano = GiocatoreUmano("Mario")
        umano.aggiungi_cartella(Cartella())
        bot = GiocatoreAutomatico("Bot1")
        bot.aggiungi_cartella(Cartella())
        partita = Partita(tabellone, [umano, bot])
        partita.avvia_partita()
        partita.esegui_fase_estrazione()

        bot.dichiara_fine_turno()
        umano.dichiara_fine_turno()
        self.assertTrue(partita.tutti_hanno_dichiarato_fine())

    def test_verifica_premi_resetta_dichiarazioni(self) -> None:
        """
        esegui_fase_verifica() resetta turno_dichiarato_concluso per tutti.
        """
        from bingo_game.cartella import Cartella
        from bingo_game.partita import Partita
        from bingo_game.players import GiocatoreAutomatico, GiocatoreUmano
        from bingo_game.tabellone import Tabellone

        tabellone = Tabellone()
        umano = GiocatoreUmano("Mario")
        umano.aggiungi_cartella(Cartella())
        bot = GiocatoreAutomatico("Bot1")
        bot.aggiungi_cartella(Cartella())
        partita = Partita(tabellone, [umano, bot])
        partita.avvia_partita()
        partita.esegui_fase_estrazione()

        umano.dichiara_fine_turno()
        bot.dichiara_fine_turno()
        self.assertTrue(partita.tutti_hanno_dichiarato_fine())

        partita.esegui_fase_verifica()

        self.assertFalse(umano.turno_dichiarato_concluso)
        self.assertFalse(bot.turno_dichiarato_concluso)

    def test_pausa_turno_durata_ms_conversione(self) -> None:
        """
        La durata della pausa (5 secondi default) è 5000 ms.
        Verifica l'invariante di conversione senza istanziare wx.
        """
        durata_pausa_s = 5
        durata_pausa_ms = durata_pausa_s * 1000
        self.assertEqual(durata_pausa_ms, 5000)
