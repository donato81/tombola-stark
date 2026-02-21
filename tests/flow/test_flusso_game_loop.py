"""
Test di flusso end-to-end per il Game Loop interattivo v0.9.0.

Scenari testati:
1.  Flusso `p`: avanza turno → numero estratto vocalizzato.
2.  Flusso `q` + conferma 's' → WARNING loggato con numero turno.
3.  Flusso `q` + annulla 'n' → loop continua, nessun WARNING sulla prima uscita.
4.  Flusso `q` + input invalido → trattato come annullato.
5.  Flusso `s abc` con argomento non numerico → messaggio errore.
6.  Flusso `s` senza argomento → messaggio errore.
7.  Comando sconosciuto 'zzz' → messaggio errore, nessun crash.
8.  Flusso partita completa → report finale con vincitore (tombola).
9.  Flusso partita completa → report finale senza vincitore.
10. Flusso `s <N>` su numero estratto → segnazione (no crash).
11. Flusso `c` → riepilogo cartella (no crash).
12. Flusso `v` → riepilogo tabellone (almeno 2 righe).
"""
from __future__ import annotations

from unittest.mock import patch, MagicMock, call

import pytest

from bingo_game.ui.tui.tui_partita import _loop_partita


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _crea_stato_mock(estratti=None, vincitore=None, premi=None):
    """Costruisce un dizionario stato-partita per i mock."""
    return {
        "numeri_estratti": estratti or [],
        "ultimo_numero_estratto": estratti[-1] if estratti else None,
        "giocatori": [{"nome": vincitore, "ha_tombola": True}] if vincitore else [],
        "premi_gia_assegnati": premi or [],
        "stato_partita": "terminata" if vincitore else "in_corso",
    }


@pytest.fixture
def partita_mock():
    """Partita mock compatibile con isinstance(partita, Partita)."""
    from bingo_game.partita import Partita
    mock = MagicMock()
    mock.__class__ = Partita
    mock.get_stato_partita.return_value = "in_corso"
    mock.is_terminata.return_value = False
    mock.get_giocatori.return_value = []
    mock.tabellone = MagicMock()
    return mock


# ---------------------------------------------------------------------------
# Scenario 1 — Flusso `p`: avanza turno → numero estratto vocalizzato
# ---------------------------------------------------------------------------

def test_flusso_p_avanza_turno(partita_mock, capsys):
    """Premendo 'p' il loop deve estrarre un numero e vocalizzarlo."""
    risultato_turno = {
        "numero_estratto": 42,
        "tombola_rilevata": False,
        "partita_terminata": False,
        "premi_nuovi": [],
    }
    inputs = iter(["p", "q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.esegui_turno_sicuro", return_value=risultato_turno),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock([42])),
    ):
        _loop_partita(partita_mock)

    out = capsys.readouterr().out
    assert "42" in out, f"Numero estratto 42 non trovato nell'output: {out!r}"


# ---------------------------------------------------------------------------
# Scenario 2 — Flusso `q` + conferma → WARNING loggato
# ---------------------------------------------------------------------------

def test_flusso_q_conferma_log_warning(partita_mock):
    """Flusso 'q' + 's': deve loggare un WARNING su tombola_stark.tui."""
    inputs = iter(["q", "s"])
    with (
        patch("bingo_game.ui.tui.tui_partita._logger_tui") as mock_logger,
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", return_value=False),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock()),
    ):
        _loop_partita(partita_mock)

    mock_logger.warning.assert_called()
    call_args = str(mock_logger.warning.call_args_list)
    assert "ALERT" in call_args, (
        f"Atteso WARNING con ALERT, ottenuto: {call_args}"
    )


# ---------------------------------------------------------------------------
# Scenario 3 — Flusso `q` + annulla → loop continua, nessun WARNING sulla prima uscita
# ---------------------------------------------------------------------------

def test_flusso_q_annulla_nessun_warning(partita_mock):
    """Flusso 'q' + 'n': il primo quit non deve emettere WARNING."""
    inputs = iter(["q", "n", "q", "s"])
    with (
        patch("bingo_game.ui.tui.tui_partita._logger_tui") as mock_logger,
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock()),
    ):
        _loop_partita(partita_mock)

    # Solo 1 WARNING (il secondo quit confermato); il primo ('n') non ne genera
    alert_calls = [
        c for c in mock_logger.warning.call_args_list
        if "ALERT" in str(c)
    ]
    assert len(alert_calls) == 1, (
        f"Atteso 1 ALERT (per il secondo quit confermato), trovati {len(alert_calls)}"
    )


# ---------------------------------------------------------------------------
# Scenario 4 — Flusso `q` + input invalido → trattato come annullato
# ---------------------------------------------------------------------------

def test_flusso_q_input_invalido_annullato(partita_mock):
    """Flusso 'q' + 'x' (input non valido): deve trattare come annullato."""
    inputs = iter(["q", "x", "q", "s"])
    with (
        patch("bingo_game.ui.tui.tui_partita._logger_tui") as mock_logger,
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock()),
    ):
        _loop_partita(partita_mock)

    # Il primo quit ('x') è annullato; il secondo ('s') è confermato
    alert_calls = [
        c for c in mock_logger.warning.call_args_list
        if "ALERT" in str(c)
    ]
    assert len(alert_calls) == 1, (
        f"Il primo quit invalido doveva essere annullato; trovati {len(alert_calls)} ALERT"
    )


# ---------------------------------------------------------------------------
# Scenario 5 — Flusso `s abc`: argomento non numerico → errore
# ---------------------------------------------------------------------------

def test_flusso_s_arg_non_numerico_errore(partita_mock, capsys):
    """Flusso 's abc': deve stampare un messaggio di errore."""
    inputs = iter(["s abc", "q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock()),
    ):
        _loop_partita(partita_mock)

    out = capsys.readouterr().out
    assert "Errore" in out or "Tipo" in out or "valido" in out, (
        f"Messaggio di errore atteso per 's abc', output: {out!r}"
    )


# ---------------------------------------------------------------------------
# Scenario 6 — Flusso `s` senza argomento → errore
# ---------------------------------------------------------------------------

def test_flusso_s_senza_argomento_errore(partita_mock, capsys):
    """Flusso 's' senza numero: deve stampare un messaggio di errore."""
    inputs = iter(["s", "q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock()),
    ):
        _loop_partita(partita_mock)

    out = capsys.readouterr().out
    assert "Errore" in out or "Tipo" in out or "valido" in out, (
        f"Messaggio di errore atteso per 's' senza argomento, output: {out!r}"
    )


# ---------------------------------------------------------------------------
# Scenario 7 — Comando sconosciuto → messaggio errore, nessun crash
# ---------------------------------------------------------------------------

def test_flusso_comando_sconosciuto_no_crash(partita_mock, capsys):
    """Comando sconosciuto 'zzz': deve stampare errore senza crash."""
    inputs = iter(["zzz", "q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock()),
    ):
        _loop_partita(partita_mock)

    out = capsys.readouterr().out
    assert "riconosciuto" in out.lower() or "aiuto" in out.lower(), (
        f"Messaggio comando sconosciuto atteso, output: {out!r}"
    )


# ---------------------------------------------------------------------------
# Scenario 8 — Partita completa con vincitore → report finale con nome vincitore
# ---------------------------------------------------------------------------

def test_flusso_partita_completa_con_vincitore(partita_mock, capsys):
    """Partita terminata per tombola: il report finale deve contenere il nome del vincitore."""
    stato_finale = _crea_stato_mock(
        estratti=list(range(1, 60)),
        vincitore="Mario",
        premi=["ambo", "tombola"],
    )
    inputs = iter(["p"])
    risultato_turno = {
        "numero_estratto": 59,
        "tombola_rilevata": True,
        "partita_terminata": True,
        "premi_nuovi": [],
    }
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", return_value=False),
        patch("bingo_game.ui.tui.tui_partita.esegui_turno_sicuro", return_value=risultato_turno),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=stato_finale),
    ):
        _loop_partita(partita_mock)

    out = capsys.readouterr().out
    assert "Mario" in out, f"Nome vincitore 'Mario' non trovato nel report finale: {out!r}"
    assert "FINE PARTITA" in out, f"Intestazione report finale mancante: {out!r}"


# ---------------------------------------------------------------------------
# Scenario 9 — Partita completa senza vincitore → report finale
# ---------------------------------------------------------------------------

def test_flusso_partita_completa_senza_vincitore(partita_mock, capsys):
    """Partita terminata senza tombola: il report finale non deve contenere un vincitore."""
    stato_finale = _crea_stato_mock(
        estratti=list(range(1, 91)),
        vincitore=None,
        premi=["ambo", "terno"],
    )
    inputs = iter(["p"])
    risultato_turno = {
        "numero_estratto": 90,
        "tombola_rilevata": False,
        "partita_terminata": True,
        "premi_nuovi": [],
    }
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", return_value=False),
        patch("bingo_game.ui.tui.tui_partita.esegui_turno_sicuro", return_value=risultato_turno),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=stato_finale),
    ):
        _loop_partita(partita_mock)

    out = capsys.readouterr().out
    assert "FINE PARTITA" in out, f"Intestazione report finale mancante: {out!r}"
    assert "tombola" in out.lower(), f"Messaggio senza vincitore mancante: {out!r}"


# ---------------------------------------------------------------------------
# Scenario 10 — Flusso `s <N>` su numero estratto → segnazione (no crash)
# ---------------------------------------------------------------------------

def test_flusso_s_numero_estratto_no_crash(partita_mock, capsys):
    """Flusso 's 42' su numero estratto: non deve causare crash."""
    from bingo_game.events.eventi import EsitoAzione
    mock_esito = EsitoAzione(ok=True, errore=None, evento=None)

    mock_giocatore = MagicMock()
    mock_giocatore.segna_numero_manuale.return_value = mock_esito

    inputs = iter(["s 42", "q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=mock_giocatore),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock([42])),
    ):
        _loop_partita(partita_mock)

    mock_giocatore.segna_numero_manuale.assert_called_once_with(42, partita_mock.tabellone)


# ---------------------------------------------------------------------------
# Scenario 11 — Flusso `c` → riepilogo cartella (no crash)
# ---------------------------------------------------------------------------

def test_flusso_c_riepilogo_cartella_no_crash(partita_mock, capsys):
    """Flusso 'c': riepilogo cartella non deve causare crash."""
    from bingo_game.events.eventi import EsitoAzione
    mock_esito = EsitoAzione(ok=False, errore="CARTELLE_NESSUNA_ASSEGNATA", evento=None)

    inputs = iter(["c", "q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=_crea_stato_mock()),
    ):
        _loop_partita(partita_mock)

    # Nessun crash, output contiene il messaggio di errore cartelle
    out = capsys.readouterr().out
    assert "cartell" in out.lower() or "selezion" in out.lower(), (
        f"Messaggio cartella atteso nell'output: {out!r}"
    )


# ---------------------------------------------------------------------------
# Scenario 12 — Flusso `v` → riepilogo tabellone (almeno 2 righe)
# ---------------------------------------------------------------------------

def test_flusso_v_riepilogo_tabellone_almeno_due_righe(partita_mock, capsys):
    """Flusso 'v': deve stampare almeno 2 righe di riepilogo tabellone."""
    stato = _crea_stato_mock(estratti=[5, 10, 15])
    inputs = iter(["v", "q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value=stato),
    ):
        _loop_partita(partita_mock)

    out = capsys.readouterr().out
    righe_non_vuote = [r for r in out.splitlines() if r.strip()]
    # Almeno la riga tabellone + riga ultimo estratto
    assert len(righe_non_vuote) >= 2, (
        f"Attese almeno 2 righe di output, trovate {len(righe_non_vuote)}: {out!r}"
    )
