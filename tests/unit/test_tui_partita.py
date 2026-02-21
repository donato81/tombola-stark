"""
Test unitari per bingo_game/ui/tui/tui_partita.py — v0.9.0

Copertura:
1.  _gestisci_quit ritorna True con risposta 's'.
2.  _gestisci_quit ritorna False con risposta 'n'.
3.  _gestisci_quit ritorna False con risposta vuota.
4.  _gestisci_quit logga WARNING quando confermato.
5.  _gestisci_segna ritorna errore con argomento non numerico.
6.  _gestisci_segna ritorna errore con argomento vuoto.
7.  _gestisci_help contiene tutte le righe di LOOP_HELP_COMANDI.
8.  _gestisci_help include la riga del focus cartella.
9.  _costruisci_report_finale include il nome vincitore se presente.
10. _costruisci_report_finale include 'nessun vincitore' se assente.
11. _costruisci_report_finale include intestazione, turni, estratti, premi.
12. _gestisci_riepilogo_tabellone ritorna almeno 2 righe.
13. Comando non riconosciuto non solleva eccezioni.
14. Focus auto impostato su cartella indice 0 all'avvio del loop.
"""
from __future__ import annotations

from unittest.mock import patch, MagicMock

import pytest


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def partita_mock():
    """Partita mock che supera isinstance(partita, Partita)."""
    from bingo_game.partita import Partita
    mock = MagicMock()
    mock.__class__ = Partita
    mock.get_stato_partita.return_value = "in_corso"
    mock.is_terminata.return_value = False
    mock.get_giocatori.return_value = []
    mock.tabellone = MagicMock()
    return mock


@pytest.fixture
def partita_mock_con_giocatore(partita_mock):
    """Partita mock con un GiocatoreUmano configurato."""
    from bingo_game.players.giocatore_umano import GiocatoreUmano
    from bingo_game.events.eventi import EsitoAzione
    from bingo_game.events.eventi_output_ui_umani import EventoStatoFocusCorrente
    mock_giocatore = MagicMock(spec=GiocatoreUmano)
    mock_giocatore.__class__ = GiocatoreUmano
    mock_giocatore._indice_cartella_focus = 0
    mock_giocatore.nome = "TestPlayer"
    # Configura stato_focus_corrente per ritornare il focus su cartella 1
    evento_focus = MagicMock(spec=EventoStatoFocusCorrente)
    evento_focus.numero_cartella = 1
    mock_giocatore.stato_focus_corrente.return_value = EsitoAzione(
        ok=True, errore=None, evento=evento_focus
    )
    mock_giocatore.imposta_focus_cartella.return_value = MagicMock()
    partita_mock.get_giocatori.return_value = [mock_giocatore]
    return partita_mock, mock_giocatore


# ---------------------------------------------------------------------------
# Test 1 — _gestisci_quit: True con 's'
# ---------------------------------------------------------------------------

def test_gestisci_quit_si(partita_mock):
    """_gestisci_quit deve ritornare True quando l'utente conferma con 's'."""
    from bingo_game.ui.tui.tui_partita import _gestisci_quit
    with patch("builtins.input", return_value="s"):
        with patch("bingo_game.ui.tui.tui_partita._stampa"):
            risultato = _gestisci_quit(partita_mock, turno=3)
    assert risultato is True


# ---------------------------------------------------------------------------
# Test 2 — _gestisci_quit: False con 'n'
# ---------------------------------------------------------------------------

def test_gestisci_quit_no(partita_mock):
    """_gestisci_quit deve ritornare False quando l'utente digita 'n'."""
    from bingo_game.ui.tui.tui_partita import _gestisci_quit
    with patch("builtins.input", return_value="n"):
        with patch("bingo_game.ui.tui.tui_partita._stampa"):
            risultato = _gestisci_quit(partita_mock, turno=3)
    assert risultato is False


# ---------------------------------------------------------------------------
# Test 3 — _gestisci_quit: False con risposta vuota
# ---------------------------------------------------------------------------

def test_gestisci_quit_vuoto(partita_mock):
    """_gestisci_quit deve ritornare False con risposta vuota."""
    from bingo_game.ui.tui.tui_partita import _gestisci_quit
    with patch("builtins.input", return_value=""):
        with patch("bingo_game.ui.tui.tui_partita._stampa"):
            risultato = _gestisci_quit(partita_mock, turno=0)
    assert risultato is False


# ---------------------------------------------------------------------------
# Test 4 — _gestisci_quit: logga WARNING se confermato
# ---------------------------------------------------------------------------

def test_gestisci_quit_logga_warning(partita_mock):
    """_gestisci_quit deve loggare un WARNING su tombola_stark.tui se confermato."""
    from bingo_game.ui.tui.tui_partita import _gestisci_quit
    with patch("bingo_game.ui.tui.tui_partita._logger_tui") as mock_logger:
        with patch("builtins.input", return_value="s"):
            with patch("bingo_game.ui.tui.tui_partita._stampa"):
                _gestisci_quit(partita_mock, turno=7)
    mock_logger.warning.assert_called()
    call_args = str(mock_logger.warning.call_args)
    assert "ALERT" in call_args and "7" in call_args, (
        f"Atteso log WARNING con ALERT e turno 7, ottenuto: {call_args}"
    )


# ---------------------------------------------------------------------------
# Test 5 — _gestisci_segna: errore con argomento non numerico
# ---------------------------------------------------------------------------

def test_gestisci_segna_arg_non_numerico(partita_mock):
    """_gestisci_segna con 'xyz' deve ritornare messaggio errore."""
    from bingo_game.ui.tui.tui_partita import _gestisci_segna
    righe = _gestisci_segna(partita_mock, "xyz")
    assert len(righe) > 0
    testo = " ".join(righe).lower()
    assert "errore" in testo or "tipo" in testo or "valido" in testo


# ---------------------------------------------------------------------------
# Test 6 — _gestisci_segna: prompt interattivo con argomento vuoto
# ---------------------------------------------------------------------------

def test_gestisci_segna_arg_vuoto(partita_mock):
    """_gestisci_segna con stringa vuota deve chiedere il numero interattivamente [v0.9.1]."""
    from bingo_game.ui.tui.tui_partita import _gestisci_segna
    with patch("builtins.input", return_value="abc"):
        with patch("bingo_game.ui.tui.tui_partita._stampa") as mock_stampa:
            righe = _gestisci_segna(partita_mock, "")
    # Deve aver mostrato il prompt interattivo
    mock_stampa.assert_called_once()
    prompt_text = mock_stampa.call_args[0][0]
    assert "1-90" in prompt_text or "numero" in prompt_text.lower()
    # Deve ritornare un errore (input non numerico)
    assert len(righe) > 0
    testo = " ".join(righe).lower()
    assert "errore" in testo or "tipo" in testo or "valido" in testo


# ---------------------------------------------------------------------------
# Test 7 — _gestisci_help: contiene tutte le righe LOOP_HELP_COMANDI
# ---------------------------------------------------------------------------

def test_gestisci_help_contiene_comandi(partita_mock):
    """_gestisci_help deve contenere tutte le righe di LOOP_HELP_COMANDI."""
    from bingo_game.ui.tui.tui_partita import _gestisci_help
    from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI
    righe_attese = MESSAGGI_OUTPUT_UI_UMANI["LOOP_HELP_COMANDI"]
    with patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None):
        righe = _gestisci_help(partita_mock)
    for attesa in righe_attese:
        assert attesa in righe, f"Riga attesa mancante nell'help: {attesa!r}"


# ---------------------------------------------------------------------------
# Test 8 — _gestisci_help: include riga focus cartella
# ---------------------------------------------------------------------------

def test_gestisci_help_include_focus(partita_mock_con_giocatore):
    """_gestisci_help deve includere la riga del focus cartella."""
    from bingo_game.ui.tui.tui_partita import _gestisci_help
    partita, giocatore = partita_mock_con_giocatore
    righe = _gestisci_help(partita)
    testo = " ".join(righe)
    assert "Cartella in focus" in testo or "focus" in testo.lower()


# ---------------------------------------------------------------------------
# Test 9 — _costruisci_report_finale: include nome vincitore
# ---------------------------------------------------------------------------

def test_costruisci_report_finale_con_vincitore():
    """_costruisci_report_finale deve includere il nome del vincitore."""
    from bingo_game.ui.tui.tui_partita import _costruisci_report_finale
    stato = {
        "numeri_estratti": list(range(1, 50)),
        "giocatori": [
            {"nome": "Mario", "ha_tombola": True},
            {"nome": "Bot 1", "ha_tombola": False},
        ],
        "premi_gia_assegnati": ["ambo", "terno"],
    }
    righe = _costruisci_report_finale(stato)
    testo = "\n".join(righe)
    assert "Mario" in testo, "Il nome del vincitore non è nel report finale"


# ---------------------------------------------------------------------------
# Test 10 — _costruisci_report_finale: nessun vincitore
# ---------------------------------------------------------------------------

def test_costruisci_report_finale_senza_vincitore():
    """_costruisci_report_finale deve includere il messaggio 'nessun vincitore'."""
    from bingo_game.ui.tui.tui_partita import _costruisci_report_finale
    stato = {
        "numeri_estratti": list(range(1, 91)),
        "giocatori": [{"nome": "Bot 1", "ha_tombola": False}],
        "premi_gia_assegnati": [],
    }
    righe = _costruisci_report_finale(stato)
    testo = "\n".join(righe)
    assert "tombola" in testo.lower() or "vincitore" in testo.lower()


# ---------------------------------------------------------------------------
# Test 11 — _costruisci_report_finale: struttura completa
# ---------------------------------------------------------------------------

def test_costruisci_report_finale_struttura_completa():
    """_costruisci_report_finale deve contenere intestazione, turni, estratti, premi."""
    from bingo_game.ui.tui.tui_partita import _costruisci_report_finale
    from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI
    stato = {
        "numeri_estratti": list(range(1, 11)),
        "giocatori": [],
        "premi_gia_assegnati": ["ambo"],
    }
    righe = _costruisci_report_finale(stato)
    testo = "\n".join(righe)

    assert MESSAGGI_OUTPUT_UI_UMANI["LOOP_REPORT_FINALE_INTESTAZIONE"][0] in righe
    # Deve contenere il contatore estratti (10)
    assert "10" in testo
    # Deve avere almeno 4 righe (intestazione, turni, estratti, esito-vincitore + premi)
    assert len(righe) >= 4


# ---------------------------------------------------------------------------
# Test 12 — _gestisci_riepilogo_tabellone: almeno 2 righe
# ---------------------------------------------------------------------------

def test_gestisci_riepilogo_tabellone_almeno_due_righe(partita_mock):
    """_gestisci_riepilogo_tabellone deve ritornare almeno 2 righe."""
    from bingo_game.ui.tui.tui_partita import _gestisci_riepilogo_tabellone
    stato_mock = {
        "numeri_estratti": [1, 2, 3],
        "ultimo_numero_estratto": 3,
        "premi_gia_assegnati": [],
        "giocatori": [],
        "stato_partita": "in_corso",
    }
    with patch(
        "bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico",
        return_value=stato_mock,
    ):
        righe = _gestisci_riepilogo_tabellone(partita_mock)
    assert len(righe) >= 2, f"Attese almeno 2 righe, ottenute {len(righe)}"


# ---------------------------------------------------------------------------
# Test 13 — Comando non riconosciuto non solleva eccezioni
# ---------------------------------------------------------------------------

def test_loop_comando_non_riconosciuto_no_crash(partita_mock, capsys):
    """Un comando sconosciuto nel loop non deve mai causare eccezioni."""
    from bingo_game.ui.tui.tui_partita import _loop_partita
    # Simula: comando sconosciuto 'zzz' poi 'q' + 's' per uscire
    inputs = iter(["zzz", "q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=None),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value={
            "numeri_estratti": [],
            "giocatori": [],
            "premi_gia_assegnati": [],
            "stato_partita": "in_corso",
            "ultimo_numero_estratto": None,
        }),
    ):
        # Non deve sollevare eccezioni
        _loop_partita(partita_mock)


# ---------------------------------------------------------------------------
# Test 14 — Focus auto impostato su cartella 0 all'avvio
# ---------------------------------------------------------------------------

def test_loop_focus_auto_impostato(partita_mock_con_giocatore):
    """_loop_partita deve impostare il focus su cartella 1 (1-based, indice 0 interno) all'avvio."""
    from bingo_game.ui.tui.tui_partita import _loop_partita
    partita, giocatore = partita_mock_con_giocatore

    # Simula uscita immediata con 'q' + 's'
    inputs = iter(["q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value={
            "numeri_estratti": [],
            "giocatori": [],
            "premi_gia_assegnati": [],
            "stato_partita": "in_corso",
            "ultimo_numero_estratto": None,
        }),
    ):
        _loop_partita(partita)

    # imposta_focus_cartella(1) deve essere stato chiamato
    giocatore.imposta_focus_cartella.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# Test 15 — Fallback focus su cartella singola quando imposta_focus_cartella solleva eccezione
# ---------------------------------------------------------------------------

def test_loop_focus_fallback_cartella_singola(partita_mock):
    """Se imposta_focus_cartella() solleva eccezione e il giocatore ha 1 cartella,
    _loop_partita deve chiamare imposta_focus_cartella_fallback() come fallback [v0.9.1]."""
    from bingo_game.ui.tui.tui_partita import _loop_partita

    mock_giocatore = MagicMock()
    mock_giocatore.imposta_focus_cartella.side_effect = AttributeError("metodo mancante")
    mock_giocatore.cartelle = [MagicMock()]  # esattamente 1 cartella

    partita_mock.get_giocatori.return_value = [mock_giocatore]

    inputs = iter(["q", "s"])
    with (
        patch("builtins.input", side_effect=inputs),
        patch("bingo_game.ui.tui.tui_partita.partita_terminata", side_effect=[False, False]),
        patch("bingo_game.ui.tui.tui_partita.ottieni_giocatore_umano", return_value=mock_giocatore),
        patch("bingo_game.ui.tui.tui_partita.ottieni_stato_sintetico", return_value={
            "numeri_estratti": [],
            "giocatori": [],
            "premi_gia_assegnati": [],
            "stato_partita": "in_corso",
            "ultimo_numero_estratto": None,
        }),
    ):
        _loop_partita(partita_mock)

    # Il fallback deve aver chiamato imposta_focus_cartella_fallback()
    mock_giocatore.imposta_focus_cartella_fallback.assert_called_once()
