import unittest

from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.eventi_output_ui_umani import (
    EventoNavigazioneColonna,
    EventoVaiAColonnaAvanzata,
    EventoVaiARigaAvanzata,
)
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

    def test_render_esito_vai_a_colonna_avanzata_non_lancia_eccezioni(self) -> None:
        finestra = _FinestraFittizia()
        vocalizzatore = _VocalizzatoreFittizio()
        renderer = WxRenderer(finestra, vocalizzatore)

        evento = EventoVaiAColonnaAvanzata.crea_da_dati_colonna_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_colonna=5,
            dati_colonna_avanzati=(("-", 25, 44), {"segnati": 1}, (25,)),
        )

        renderer.render_esito(EsitoAzione(ok=True, errore=None, evento=evento))

        self.assertEqual(finestra.testi[-1], "Colonna 5: vuoto, [25], 44")
        self.assertEqual(vocalizzatore.testi[-1], "Colonna 5: vuoto, [25], 44")

    def test_render_esito_vai_a_riga_avanzata_non_lancia_eccezioni(self) -> None:
        finestra = _FinestraFittizia()
        vocalizzatore = _VocalizzatoreFittizio()
        renderer = WxRenderer(finestra, vocalizzatore)

        evento = EventoVaiARigaAvanzata.crea_da_dati_riga_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_riga=2,
            dati_riga_avanzati=((10, "-", 33), {"segnati": 1}, (33,)),
        )

        renderer.render_esito(EsitoAzione(ok=True, errore=None, evento=evento))

        self.assertEqual(finestra.testi[-1], "Riga 2: 10  vuoto  [33]")
        self.assertEqual(vocalizzatore.testi[-1], "Riga 2: 10  vuoto  [33]")
