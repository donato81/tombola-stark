import unittest

from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.eventi_output_ui_umani import (
    EventoNavigazioneColonna,
    EventoVisualizzaTutteCartelleAvanzata,
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
            dati_colonna_avanzati=(("-", 25, 44), {"numeri_segnati": 1, "numeri_totali": 2}, (25,)),
        )

        renderer.render_esito(EsitoAzione(ok=True, errore=None, evento=evento))

        self.assertEqual(finestra.testi[-1], "Avanzata colonna 5, 1 segnato su 2: vuoto, 25 segnato, 44")
        self.assertEqual(vocalizzatore.testi[-1], "Avanzata colonna 5, 1 segnato su 2: vuoto, 25 segnato, 44")

    def test_render_esito_vai_a_riga_avanzata_non_lancia_eccezioni(self) -> None:
        finestra = _FinestraFittizia()
        vocalizzatore = _VocalizzatoreFittizio()
        renderer = WxRenderer(finestra, vocalizzatore)

        evento = EventoVaiARigaAvanzata.crea_da_dati_riga_avanzati(
            id_giocatore=1,
            nome_giocatore="Mario",
            numero_riga=2,
            dati_riga_avanzati=((10, "-", 33), {"numeri_segnati": 1, "numeri_totali": 2}, (33,)),
        )

        renderer.render_esito(EsitoAzione(ok=True, errore=None, evento=evento))

        self.assertEqual(finestra.testi[-1], "Avanzata riga 2, 1 segnato su 2: 10  vuoto  33 segnato")
        self.assertEqual(vocalizzatore.testi[-1], "Avanzata riga 2, 1 segnato su 2: 10  vuoto  33 segnato")

    def test_render_esito_visualizza_tutte_cartelle_avanzata_legge_contenuto_completo(self) -> None:
        finestra = _FinestraFittizia()
        vocalizzatore = _VocalizzatoreFittizio()
        renderer = WxRenderer(finestra, vocalizzatore)

        evento = EventoVisualizzaTutteCartelleAvanzata(
            totale_cartelle=1,
            cartelle=(
                (
                    1,
                    ((10, "-", 33), ("-", 25, "-"), (44, "-", "-")),
                    {"numeri_segnati": 2, "numeri_totali": 4},
                    (25, 33),
                ),
            ),
        )

        renderer.render_esito(EsitoAzione(ok=True, errore=None, evento=evento))

        atteso = (
            "Cartella 1:\n"
            "  Riga 1: 10  vuoto  33 segnato\n"
            "  Riga 2: vuoto  25 segnato  vuoto\n"
            "  Riga 3: 44  vuoto  vuoto"
        )
        self.assertEqual(finestra.testi[-1], atteso)
        self.assertEqual(vocalizzatore.testi[-1], atteso)


class TestMostraReportFinale(unittest.TestCase):
    """Verifica la costruzione del testo accessibile in mostra_report_finale."""

    def _crea_renderer(self) -> tuple:
        finestra = _FinestraFittizia()
        vocalizzatore = _VocalizzatoreFittizio()
        renderer = WxRenderer(finestra, vocalizzatore)
        return renderer, finestra, vocalizzatore

    def test_testo_base_con_turni_e_estratti(self) -> None:
        renderer, _, vocalizzatore = self._crea_renderer()
        dati = {
            "turni_giocati": 15,
            "conteggio_estratti": 30,
            "premi_gia_assegnati": [],
            "vincitore_tombola": "—",
        }
        renderer.mostra_report_finale(dati)
        testo = vocalizzatore.testi[-1]
        self.assertIn("Turni giocati: 15", testo)
        self.assertIn("Numeri estratti: 30 su 90", testo)

    def test_con_vincitore_tombola_include_frase_vinta(self) -> None:
        renderer, _, vocalizzatore = self._crea_renderer()
        dati = {
            "turni_giocati": 20,
            "conteggio_estratti": 45,
            "premi_gia_assegnati": [],
            "vincitore_tombola": "Alice",
        }
        renderer.mostra_report_finale(dati)
        testo = vocalizzatore.testi[-1]
        self.assertIn("Tombola vinta da: Alice", testo)

    def test_senza_vincitore_non_include_frase_vinta(self) -> None:
        renderer, _, vocalizzatore = self._crea_renderer()
        dati = {
            "turni_giocati": 10,
            "conteggio_estratti": 20,
            "premi_gia_assegnati": [],
            "vincitore_tombola": "—",
        }
        renderer.mostra_report_finale(dati)
        testo = vocalizzatore.testi[-1]
        self.assertNotIn("Tombola vinta da", testo)

    def test_premi_lista_vuota_non_include_premi_assegnati(self) -> None:
        renderer, _, vocalizzatore = self._crea_renderer()
        dati = {
            "turni_giocati": 5,
            "conteggio_estratti": 10,
            "premi_gia_assegnati": [],
            "vincitore_tombola": "—",
        }
        renderer.mostra_report_finale(dati)
        testo = vocalizzatore.testi[-1]
        self.assertNotIn("Premi assegnati", testo)

    def test_premi_dict_inclusi_nel_testo(self) -> None:
        renderer, _, vocalizzatore = self._crea_renderer()
        dati = {
            "turni_giocati": 25,
            "conteggio_estratti": 50,
            "premi_gia_assegnati": [
                {"premio": "ambo", "giocatore": "Mario"},
                {"premio": "tombola", "giocatore": "Alice"},
            ],
            "vincitore_tombola": "Alice",
        }
        renderer.mostra_report_finale(dati)
        testo = vocalizzatore.testi[-1]
        self.assertIn("Premi assegnati", testo)
        self.assertIn("ambo per Mario", testo)
        self.assertIn("tombola per Alice", testo)

    def test_premi_oggetto_con_attributi_inclusi(self) -> None:
        class _Premio:
            def __init__(self, tipo: str, giocatore: str) -> None:
                self.tipo = tipo
                self.giocatore = giocatore

        renderer, _, vocalizzatore = self._crea_renderer()
        dati = {
            "turni_giocati": 30,
            "conteggio_estratti": 60,
            "premi_gia_assegnati": [_Premio("terno", "Luigi")],
            "vincitore_tombola": "—",
        }
        renderer.mostra_report_finale(dati)
        testo = vocalizzatore.testi[-1]
        self.assertIn("terno per Luigi", testo)

    def test_chiama_mostra_riepilogo_finale_sulla_finestra(self) -> None:
        class _FinestraConRiepilogo(_FinestraFittizia):
            def __init__(self) -> None:
                super().__init__()
                self.riepilogo_chiamato: bool = False
                self.dati_ricevuti: dict = {}

            def mostra_riepilogo_finale(self, dati: dict) -> None:
                self.riepilogo_chiamato = True
                self.dati_ricevuti = dati

        finestra = _FinestraConRiepilogo()
        vocalizzatore = _VocalizzatoreFittizio()
        renderer = WxRenderer(finestra, vocalizzatore)
        dati = {
            "turni_giocati": 8,
            "conteggio_estratti": 16,
            "premi_gia_assegnati": [],
            "vincitore_tombola": "—",
        }
        renderer.mostra_report_finale(dati)
        self.assertTrue(finestra.riepilogo_chiamato)
        self.assertEqual(finestra.dati_ricevuti["turni_giocati"], 8)
