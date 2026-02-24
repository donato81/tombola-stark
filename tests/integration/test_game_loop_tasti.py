"""
Test di integrazione per il game loop con tasti rapidi — v0.10.0

Verifica il comportamento end-to-end di _loop_partita() con la catena
leggi_tasto → comando_da_tasto → dispatch.

Scenari:
A — Tasto non valido non blocca il loop.
B — Navigazione cartella con tasto numerico ("1").
C — Prompt numerico con input valido (tasto "s" + "42").
D — Prompt numerico con input non valido (tasto "s" + "abc").
E — Uscita con conferma S/N (tasto "x" + "s").
F — Scenario partita completa (sequenza realistica multi-tasto).

Importante piattaforma:
    msvcrt è disponibile solo su Windows. Prima di qualsiasi import dei moduli
    TUI, il mock viene registrato in sys.modules per garantire compatibilità
    su tutti gli ambienti CI/CD.
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock msvcrt a livello sys.modules — DEVE avvenire prima di qualsiasi import
# dei moduli TUI (tui_commander importa msvcrt a livello di modulo).
# ---------------------------------------------------------------------------
if "msvcrt" not in sys.modules:
    sys.modules["msvcrt"] = MagicMock()


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_partita():
    """Partita mock compatibile con isinstance(partita, Partita) con 1 giocatore umano."""
    from bingo_game.partita import Partita
    from bingo_game.players.giocatore_umano import GiocatoreUmano
    from bingo_game.events.eventi import EsitoAzione
    from bingo_game.events.eventi_output_ui_umani import EventoStatoFocusCorrente

    # Partita mock
    partita = MagicMock()
    partita.__class__ = Partita
    partita.tabellone = MagicMock()

    # Giocatore umano mock
    giocatore = MagicMock(spec=GiocatoreUmano)
    giocatore.__class__ = GiocatoreUmano
    giocatore.nome = "TestPlayer"
    giocatore._indice_cartella_focus = 0
    giocatore.cartelle = [MagicMock()]  # 1 cartella

    # imposta_focus_cartella → ok
    esito_focus = MagicMock(spec=EsitoAzione)
    esito_focus.ok = True
    giocatore.imposta_focus_cartella.return_value = esito_focus

    # stato_focus_corrente → ok, cartella 1
    evento_focus = MagicMock(spec=EventoStatoFocusCorrente)
    evento_focus.numero_cartella = 1
    giocatore.stato_focus_corrente.return_value = EsitoAzione(
        ok=True, errore=None, evento=evento_focus
    )

    partita.get_giocatori.return_value = [giocatore]
    return partita, giocatore


def _renderer_stub():
    """Ritorna un mock di _renderer che produce liste vuote (silenzioso)."""
    renderer = MagicMock()
    renderer.render_esito.return_value = []
    return renderer


# ---------------------------------------------------------------------------
# Scenario A — Tasto non valido non blocca il loop
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_scenario_a_tasto_non_valido(mock_partita):
    """Tasto non valido ("@") non deve bloccare il loop; mostra LOOP_TASTO_NON_VALIDO."""
    from bingo_game.ui.tui.tui_partita import _loop_partita
    from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI

    partita, giocatore = mock_partita
    messaggi: list = []
    messaggio_atteso = MESSAGGI_OUTPUT_UI_UMANI["LOOP_TASTO_NON_VALIDO"][0]

    # Sequenza: "@" (non valido) → "p" (passa turno, risultato interrompe loop)
    with (
        patch("bingo_game.ui.tui.tui_partita.leggi_tasto", side_effect=["@", "p"]),
        patch(
            "bingo_game.ui.tui.tui_partita.partita_terminata",
            side_effect=[False, False],
        ),
        patch(
            "bingo_game.ui.tui.tui_partita.esegui_turno_sicuro",
            return_value={"numero_estratto": 42, "tombola_rilevata": True, "partita_terminata": True},
        ),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=giocatore),
        patch("bingo_game.ui.tui.tui_partita._emetti_report_finale"),
        patch("bingo_game.ui.tui.tui_partita._stampa", side_effect=messaggi.append),
        patch("bingo_game.ui.tui.tui_partita._renderer", _renderer_stub()),
    ):
        # Non deve sollevare eccezioni
        _loop_partita(partita)

    assert messaggio_atteso in messaggi, (
        f"Messaggio LOOP_TASTO_NON_VALIDO atteso tra i messaggi stampati.\n"
        f"Atteso: {messaggio_atteso!r}\nStampati: {messaggi!r}"
    )


# ---------------------------------------------------------------------------
# Scenario B — Navigazione cartella con tasto numerico
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_scenario_b_selezione_cartella(mock_partita):
    """Tasto '1' deve chiamare imposta_focus_cartella(1) sul giocatore."""
    from bingo_game.ui.tui.tui_partita import _loop_partita

    partita, giocatore = mock_partita

    # Sequenza: "1" (seleziona cartella 1) → partita_terminata True al passo successivo
    with (
        patch("bingo_game.ui.tui.tui_partita.leggi_tasto", side_effect=["1"]),
        patch(
            "bingo_game.ui.tui.tui_partita.partita_terminata",
            side_effect=[False, True],
        ),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=giocatore),
        patch("bingo_game.ui.tui.tui_partita._emetti_report_finale"),
        patch("bingo_game.ui.tui.tui_partita._stampa"),
        patch("bingo_game.ui.tui.tui_partita._renderer", _renderer_stub()),
    ):
        _loop_partita(partita)

    # imposta_focus_cartella deve essere stata chiamata con 1
    # (una volta all'avvio + una volta per il tasto "1")
    calls = giocatore.imposta_focus_cartella.call_args_list
    valori = [c.args[0] for c in calls if c.args]
    assert 1 in valori, (
        f"imposta_focus_cartella(1) atteso dopo tasto '1'. Chiamate: {calls!r}"
    )


# ---------------------------------------------------------------------------
# Scenario C — Prompt numerico con input valido
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_scenario_c_prompt_numerico_valido(mock_partita):
    """Tasto 's' + input '42' deve chiamare segna_numero_manuale(42, tabellone)."""
    from bingo_game.ui.tui.tui_partita import _loop_partita
    from bingo_game.events.eventi import EsitoAzione

    partita, giocatore = mock_partita

    esito_ok = MagicMock(spec=EsitoAzione)
    esito_ok.ok = True
    giocatore.segna_numero_manuale = MagicMock(return_value=esito_ok)

    # Sequenza: "s" → input "42" → partita terminata
    with (
        patch("bingo_game.ui.tui.tui_partita.leggi_tasto", side_effect=["s"]),
        patch(
            "bingo_game.ui.tui.tui_partita.partita_terminata",
            side_effect=[False, True],
        ),
        patch("builtins.input", return_value="42"),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=giocatore),
        patch("bingo_game.ui.tui.tui_partita._emetti_report_finale"),
        patch("bingo_game.ui.tui.tui_partita._stampa"),
        patch("bingo_game.ui.tui.tui_partita._renderer", _renderer_stub()),
    ):
        _loop_partita(partita)

    giocatore.segna_numero_manuale.assert_called_once_with(42, partita.tabellone)


# ---------------------------------------------------------------------------
# Scenario D — Prompt numerico con input non valido
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_scenario_d_prompt_numerico_non_valido(mock_partita):
    """Tasto 's' + input non numerico deve stampare errore e NON chiamare segna_numero_manuale."""
    from bingo_game.ui.tui.tui_partita import _loop_partita
    from bingo_game.ui.locales.it import MESSAGGI_ERRORI

    partita, giocatore = mock_partita
    messaggi: list = []

    # Sequenza: "s" (input "abc" non valido) → "p" (passa turno e chiude loop)
    with (
        patch("bingo_game.ui.tui.tui_partita.leggi_tasto", side_effect=["s", "p"]),
        patch(
            "bingo_game.ui.tui.tui_partita.partita_terminata",
            side_effect=[False, False],
        ),
        patch("builtins.input", return_value="abc"),
        patch(
            "bingo_game.ui.tui.tui_partita.esegui_turno_sicuro",
            return_value={"numero_estratto": 15, "tombola_rilevata": True, "partita_terminata": True},
        ),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=giocatore),
        patch("bingo_game.ui.tui.tui_partita._emetti_report_finale"),
        patch("bingo_game.ui.tui.tui_partita._stampa", side_effect=messaggi.append),
        patch("bingo_game.ui.tui.tui_partita._renderer", _renderer_stub()),
    ):
        _loop_partita(partita)

    # segna_numero_manuale NON deve essere stato chiamato
    giocatore.segna_numero_manuale.assert_not_called()

    # Almeno un messaggio di errore must contenere una delle parole dell'errore tipo
    testo_output = " ".join(messaggi).lower()
    errore_atteso = MESSAGGI_ERRORI["NUMERO_TIPO_NON_VALIDO"][0].lower()
    assert errore_atteso in testo_output or any(
        parola in testo_output for parola in ("errore", "tipo", "valido")
    ), (
        f"Messaggio errore input non valido atteso nell'output.\n"
        f"Messaggi stampati: {messaggi!r}"
    )


# ---------------------------------------------------------------------------
# Scenario E — Uscita con conferma S/N
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_scenario_e_uscita_con_conferma(mock_partita):
    """Tasto 'x' + input 's' deve interrompere il loop e chiamare _emetti_report_finale."""
    from bingo_game.ui.tui.tui_partita import _loop_partita

    partita, giocatore = mock_partita

    con_report: list = []

    with (
        patch("bingo_game.ui.tui.tui_partita.leggi_tasto", side_effect=["x"]),
        patch(
            "bingo_game.ui.tui.tui_partita.partita_terminata",
            return_value=False,
        ),
        patch("builtins.input", return_value="s"),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=giocatore),
        patch(
            "bingo_game.ui.tui.tui_partita._emetti_report_finale",
            side_effect=lambda p: con_report.append(True),
        ),
        patch("bingo_game.ui.tui.tui_partita._stampa"),
        patch("bingo_game.ui.tui.tui_partita._renderer", _renderer_stub()),
    ):
        _loop_partita(partita)

    assert len(con_report) == 1, (
        "_emetti_report_finale deve essere chiamato esattamente una volta dopo 'x' + 's'."
    )


# ---------------------------------------------------------------------------
# Scenario F — Scenario partita completa (sequenza realistica)
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_scenario_f_partita_completa(mock_partita):
    """Sequenza realistica multi-tasto deve completare senza eccezioni e chiamare report finale."""
    from bingo_game.ui.tui.tui_partita import _loop_partita
    from bingo_game.events.eventi import EsitoAzione

    partita, giocatore = mock_partita

    # Configura risposte metodi del giocatore
    esito_ok = MagicMock(spec=EsitoAzione)
    esito_ok.ok = True
    giocatore.sposta_focus_riga_giu_semplice = MagicMock(return_value=esito_ok)
    giocatore.visualizza_cartella_corrente_semplice = MagicMock(return_value=esito_ok)
    giocatore.comunica_ultimo_numero_estratto = MagicMock(return_value=esito_ok)
    giocatore.segna_numero_manuale = MagicMock(return_value=esito_ok)

    report_chiamato: list = []

    # Sequenza:
    # "1" → seleziona cartella 1
    # "\xe0P" → freccia giù (sposta_focus_riga_giu_semplice)
    # "d" → visualizza_cartella_corrente_semplice
    # "p" → passa turno (primo turno, non interrompe)
    # "u" → comunica_ultimo_numero_estratto (con tabellone)
    # "s" → segna_numero_manuale, input "5"
    # "x" → esci, input "s"
    tasti = ["1", "\xe0P", "d", "p", "u", "s", "x"]
    input_values = iter(["5", "s"])

    # partita_terminata: False per i primi 7 tasti, True mai (loop termina per "x"+"s")
    terminata_values = [False] * 8  # abbondante, loop esce per break

    turno_result = {
        "numero_estratto": 5,
        "tombola_rilevata": False,
        "partita_terminata": False,
    }

    with (
        patch("bingo_game.ui.tui.tui_partita.leggi_tasto", side_effect=tasti),
        patch(
            "bingo_game.ui.tui.tui_partita.partita_terminata",
            side_effect=terminata_values,
        ),
        patch("builtins.input", side_effect=input_values),
        patch(
            "bingo_game.ui.tui.tui_partita.esegui_turno_sicuro",
            return_value=turno_result,
        ),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=giocatore),
        patch(
            "bingo_game.ui.tui.tui_partita._emetti_report_finale",
            side_effect=lambda p: report_chiamato.append(True),
        ),
        patch("bingo_game.ui.tui.tui_partita._stampa"),
        patch("bingo_game.ui.tui.tui_partita._renderer", _renderer_stub()),
    ):
        # Non deve sollevare eccezioni
        _loop_partita(partita)

    assert len(report_chiamato) == 1, (
        "_emetti_report_finale deve essere chiamato esattamente una volta al termine."
    )
    # La freccia giù deve aver chiamato il metodo corrispondente
    giocatore.sposta_focus_riga_giu_semplice.assert_called_once()
    # segna_numero_manuale deve essere stato chiamato con 5
    giocatore.segna_numero_manuale.assert_called_once_with(5, partita.tabellone)
