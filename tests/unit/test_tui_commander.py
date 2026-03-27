"""
Test unitari per bingo_game/ui/tui/tui_commander.py — v0.10.0

Copertura:
1.  leggi_tasto(): tasto semplice (1 byte).
2.  leggi_tasto(): tasto esteso con prefisso \\xe0 (2 byte).
3.  leggi_tasto(): tasto esteso con prefisso \\x00 (2 byte).
4.  comando_da_tasto(): AZIONE_DIRETTA — frecce direzionali.
5.  comando_da_tasto(): AZIONE_DIRETTA — lettere alfabetiche (spot-check).
6.  comando_da_tasto(): SELEZIONA_CARTELLA per tasti 1-6 (tutti i valori).
7.  comando_da_tasto(): RICHIEDE_PROMPT_NUM — tasti R, C, E, N, S, V.
8.  comando_da_tasto(): RICHIEDE_CONFERMA — tasto X.
9.  comando_da_tasto(): TASTO_NON_VALIDO per stringa sconosciuta.
10. ComandoTasto è immutabile (frozen dataclass).
11. TipoComando espone tutti e 5 i valori attesi.
12. Tasto cartella trasporta il valore numerico 1-based corretto.
13. Tasto non in mappa ritorna sempre _CMD_NON_VALIDO (singleton stabile).
"""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Assicura msvcrt mockato prima di qualsiasi import del modulo tui_commander
# (msvcrt è disponibile solo su Windows: in ambienti non-Windows l'import
#  fallirebbe senza questo mock a livello di sys.modules).
# ---------------------------------------------------------------------------
if "msvcrt" not in sys.modules:
    sys.modules["msvcrt"] = MagicMock()


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_msvcrt():
    """Resetta il mock msvcrt prima di ogni test per evitare side-effect."""
    msvcrt_mock = sys.modules["msvcrt"]
    msvcrt_mock.reset_mock()
    yield


# ---------------------------------------------------------------------------
# Test 1 — leggi_tasto: tasto semplice (1 byte)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_leggi_tasto_semplice():
    """leggi_tasto deve restituire il singolo carattere per un tasto ordinario."""
    from bingo_game.ui.tui.tui_commander import leggi_tasto

    with patch("bingo_game.ui.tui.tui_commander.msvcrt") as mock_msvcrt:
        mock_msvcrt.getwch.return_value = "a"
        risultato = leggi_tasto()

    assert risultato == "a"
    mock_msvcrt.getwch.assert_called_once()


# ---------------------------------------------------------------------------
# Test 2 — leggi_tasto: tasto esteso con prefisso \xe0
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_leggi_tasto_esteso_prefisso_xe0():
    """leggi_tasto deve leggere il secondo byte dopo il prefisso \\xe0."""
    from bingo_game.ui.tui.tui_commander import leggi_tasto

    with patch("bingo_game.ui.tui.tui_commander.msvcrt") as mock_msvcrt:
        mock_msvcrt.getwch.side_effect = ["\xe0", "H"]
        risultato = leggi_tasto()

    assert risultato == "\xe0H", (
        f"Atteso '\\xe0H' per freccia su, ottenuto: {risultato!r}"
    )
    assert mock_msvcrt.getwch.call_count == 2, (
        "Attese 2 chiamate getwch per tasto esteso, "
        f"ottenute: {mock_msvcrt.getwch.call_count}"
    )


# ---------------------------------------------------------------------------
# Test 3 — leggi_tasto: tasto esteso con prefisso \x00
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_leggi_tasto_esteso_prefisso_x00():
    """leggi_tasto deve leggere il secondo byte anche dopo il prefisso \\x00."""
    from bingo_game.ui.tui.tui_commander import leggi_tasto

    with patch("bingo_game.ui.tui.tui_commander.msvcrt") as mock_msvcrt:
        mock_msvcrt.getwch.side_effect = ["\x00", "P"]
        risultato = leggi_tasto()

    assert risultato == "\x00P", (
        f"Atteso '\\x00P', ottenuto: {risultato!r}"
    )
    assert mock_msvcrt.getwch.call_count == 2


# ---------------------------------------------------------------------------
# Test 4 — comando_da_tasto: AZIONE_DIRETTA per le frecce direzionali
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("costante,nome_atteso", [
    ("\xe0H", "sposta_focus_riga_su_semplice"),
    ("\xe0P", "sposta_focus_riga_giu_semplice"),
    ("\xe0K", "sposta_focus_colonna_sinistra"),
    ("\xe0M", "sposta_focus_colonna_destra"),
    ("\xe0I", "riepilogo_cartella_precedente"),
    ("\xe0Q", "riepilogo_cartella_successiva"),
])
def test_comando_da_tasto_azione_diretta_tasti_estesi(costante, nome_atteso):
    """comando_da_tasto deve restituire AZIONE_DIRETTA con nome corretto per tasti estesi."""
    from bingo_game.ui.tui.tui_commander import TipoComando, comando_da_tasto

    cmd = comando_da_tasto(costante)

    assert cmd.tipo == TipoComando.AZIONE_DIRETTA, (
        f"Tasto {costante!r}: atteso AZIONE_DIRETTA, ottenuto {cmd.tipo}"
    )
    assert cmd.nome == nome_atteso, (
        f"Tasto {costante!r}: atteso nome={nome_atteso!r}, ottenuto {cmd.nome!r}"
    )


# ---------------------------------------------------------------------------
# Test 5 — comando_da_tasto: AZIONE_DIRETTA per lettere (spot-check)
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("tasto,nome_atteso", [
    ("a", "sposta_focus_riga_su_avanzata"),
    ("z", "sposta_focus_riga_giu_avanzata"),
    ("q", "sposta_focus_colonna_sinistra_avanzata"),
    ("w", "sposta_focus_colonna_destra_avanzata"),
    ("d", "visualizza_cartella_corrente_semplice"),
    ("f", "visualizza_cartella_corrente_avanzata"),
    ("g", "visualizza_tutte_cartelle_semplice"),
    ("h", "visualizza_tutte_cartelle_avanzata"),
    ("u", "comunica_ultimo_numero_estratto"),
    ("i", "visualizza_ultimi_numeri_estratti"),
    ("o", "riepilogo_tabellone"),
    ("l", "lista_numeri_estratti"),
    ("p", "passa_turno"),
])
def test_comando_da_tasto_azione_diretta_lettere(tasto, nome_atteso):
    """comando_da_tasto restituisce AZIONE_DIRETTA corretto per ciascuna lettera."""
    from bingo_game.ui.tui.tui_commander import TipoComando, comando_da_tasto

    cmd = comando_da_tasto(tasto)

    assert cmd.tipo == TipoComando.AZIONE_DIRETTA, (
        f"Tasto {tasto!r}: atteso AZIONE_DIRETTA, ottenuto {cmd.tipo}"
    )
    assert cmd.nome == nome_atteso, (
        f"Tasto {tasto!r}: atteso nome={nome_atteso!r}, ottenuto {cmd.nome!r}"
    )


# ---------------------------------------------------------------------------
# Test 6 — comando_da_tasto: SELEZIONA_CARTELLA per tasti "1"-"6"
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("tasto_str", ["1", "2", "3", "4", "5", "6"])
def test_comando_da_tasto_seleziona_cartella_tutti(tasto_str):
    """comando_da_tasto restituisce SELEZIONA_CARTELLA con valore numerico 1-based."""
    from bingo_game.ui.tui.tui_commander import TipoComando, comando_da_tasto

    cmd = comando_da_tasto(tasto_str)

    assert cmd.tipo == TipoComando.SELEZIONA_CARTELLA, (
        f"Tasto {tasto_str!r}: atteso SELEZIONA_CARTELLA, ottenuto {cmd.tipo}"
    )
    assert cmd.nome == "imposta_focus_cartella", (
        f"Tasto {tasto_str!r}: nome atteso 'imposta_focus_cartella', ottenuto {cmd.nome!r}"
    )
    assert cmd.valore == int(tasto_str), (
        f"Tasto {tasto_str!r}: valore atteso {int(tasto_str)}, ottenuto {cmd.valore}"
    )


# ---------------------------------------------------------------------------
# Test 7 — comando_da_tasto: RICHIEDE_PROMPT_NUM
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("tasto,nome_atteso", [
    ("r", "vai_a_riga_avanzata"),
    ("c", "vai_a_colonna_avanzata"),
    ("e", "verifica_numero_estratto"),
    ("n", "cerca_numero_nelle_cartelle"),
    ("s", "segna_numero_manuale"),
    ("v", "annuncia_vittoria"),
])
def test_comando_da_tasto_richiede_prompt_num(tasto, nome_atteso):
    """comando_da_tasto restituisce RICHIEDE_PROMPT_NUM per tasti che richiedono input."""
    from bingo_game.ui.tui.tui_commander import TipoComando, comando_da_tasto

    cmd = comando_da_tasto(tasto)

    assert cmd.tipo == TipoComando.RICHIEDE_PROMPT_NUM, (
        f"Tasto {tasto!r}: atteso RICHIEDE_PROMPT_NUM, ottenuto {cmd.tipo}"
    )
    assert cmd.nome == nome_atteso, (
        f"Tasto {tasto!r}: atteso nome={nome_atteso!r}, ottenuto {cmd.nome!r}"
    )


# ---------------------------------------------------------------------------
# Test 8 — comando_da_tasto: RICHIEDE_CONFERMA per tasto X
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_comando_da_tasto_richiede_conferma_x():
    """comando_da_tasto deve restituire RICHIEDE_CONFERMA per il tasto 'x'."""
    from bingo_game.ui.tui.tui_commander import TipoComando, comando_da_tasto

    cmd = comando_da_tasto("x")

    assert cmd.tipo == TipoComando.RICHIEDE_CONFERMA, (
        f"Tasto 'x': atteso RICHIEDE_CONFERMA, ottenuto {cmd.tipo}"
    )
    assert cmd.nome == "esci", (
        f"Tasto 'x': atteso nome='esci', ottenuto {cmd.nome!r}"
    )


# ---------------------------------------------------------------------------
# Test 9 — comando_da_tasto: TASTO_NON_VALIDO per stringa sconosciuta
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.parametrize("tasto_sconosciuto", ["@", "#", "7", "8", "zzz", "", " "])
def test_comando_da_tasto_non_valido(tasto_sconosciuto):
    """comando_da_tasto deve restituire TASTO_NON_VALIDO per tasti non riconosciuti."""
    from bingo_game.ui.tui.tui_commander import TipoComando, comando_da_tasto

    cmd = comando_da_tasto(tasto_sconosciuto)

    assert cmd.tipo == TipoComando.TASTO_NON_VALIDO, (
        f"Tasto {tasto_sconosciuto!r}: atteso TASTO_NON_VALIDO, ottenuto {cmd.tipo}"
    )
    assert cmd.nome == "non_valido", (
        f"Tasto {tasto_sconosciuto!r}: atteso nome='non_valido', ottenuto {cmd.nome!r}"
    )


# ---------------------------------------------------------------------------
# Test 10 — ComandoTasto è immutabile (frozen dataclass)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_comando_tasto_frozen():
    """ComandoTasto deve essere immutabile: qualsiasi assegnazione solleva FrozenInstanceError."""
    from bingo_game.ui.tui.tui_commander import ComandoTasto, TipoComando

    cmd = ComandoTasto(TipoComando.AZIONE_DIRETTA, "test_nome")

    with pytest.raises((AttributeError, TypeError)):
        cmd.nome = "altro_nome"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Test 11 — TipoComando ha esattamente 5 valori
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tipo_comando_ha_cinque_valori():
    """TipoComando deve esporre esattamente i 5 tipi di classificazione attesi."""
    from bingo_game.ui.tui.tui_commander import TipoComando

    valori_attesi = {
        "AZIONE_DIRETTA",
        "RICHIEDE_PROMPT_NUM",
        "RICHIEDE_CONFERMA",
        "SELEZIONA_CARTELLA",
        "TASTO_NON_VALIDO",
    }
    valori_reali = {membro.name for membro in TipoComando}

    assert valori_reali == valori_attesi, (
        f"TipoComando non ha i valori attesi.\n"
        f"Attesi: {valori_attesi}\nOttenuti: {valori_reali}"
    )


# ---------------------------------------------------------------------------
# Test 12 — Tasto cartella trasporta il valore 1-based corretto
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tasto_cartella_valore_1based():
    """Il campo valore di SELEZIONA_CARTELLA deve essere l'intero 1-based del tasto."""
    from bingo_game.ui.tui.tui_commander import comando_da_tasto

    for numero in range(1, 7):
        cmd = comando_da_tasto(str(numero))
        assert cmd.valore == numero, (
            f"Tasto '{numero}': valore atteso {numero}, ottenuto {cmd.valore}"
        )


# ---------------------------------------------------------------------------
# Test 13 — Tasto non in mappa ritorna sentinel stabile (non crea nuovi oggetti)
# ---------------------------------------------------------------------------


@pytest.mark.unit
def test_tasto_non_valido_ritorna_sentinel_stabile():
    """Tasti sconosciuti diversi devono ritornare lo stesso oggetto _CMD_NON_VALIDO."""
    from bingo_game.ui.tui.tui_commander import TipoComando, comando_da_tasto

    cmd1 = comando_da_tasto("@")
    cmd2 = comando_da_tasto("#")

    # Entrambi devono essere il medesimo singleton (is identity)
    assert cmd1 is cmd2, (
        "Due tasti non validi devono restituire lo stesso oggetto sentinel."
    )
    assert cmd1.tipo == TipoComando.TASTO_NON_VALIDO
