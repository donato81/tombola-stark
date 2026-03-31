import unittest

from bingo_game.events.eventi_output_ui_umani import EventoNavigazioneColonna
from bingo_game.ui.renderers.renderer_wx import WxRenderer


class _FinestraFittizia:
    def __init__(self) -> None:
        self.testi: list[str] = []
        self.log: list[str] = []

    def mostra_testo(self, testo: str) -> None:
        self.testi.append(testo)

    def aggiungi_a_log(self, testo: str) -> None:
        self.log.append(testo)


class _VocalizzatoreFittizio:
    def __init__(self) -> None:
        self.testi: list[str] = []

    def vocalizza_testo(self, testo: str, interrompi: bool = False) -> None:
        self.testi.append(testo)


class TestWxRenderer(unittest.TestCase):
    def test_navigazione_colonna_legge_vuoto_e_non_barra(self) -> None:
        finestra = _FinestraFittizia()
        vocalizzatore = _VocalizzatoreFittizio()
        renderer = WxRenderer(finestra, vocalizzatore)

        evento = EventoNavigazioneColonna.mostra_colonna(
            id_giocatore=1,
            nome_giocatore="Mario",
            direzione="destra",
            totale_cartelle=1,
            numero_cartella_corrente=1,
            totale_colonne=9,
            indice_colonna_corrente=2,
            colonna_semplice=("-", 25, "-"),
        )

        renderer._handle_navigazione_colonna(evento)

        self.assertEqual(finestra.testi[-1], "Colonna 3: vuoto, 25, vuoto")
        self.assertEqual(vocalizzatore.testi[-1], "Colonna 3: vuoto, 25, vuoto")
