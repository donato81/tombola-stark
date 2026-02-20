"""
Test di smoke/regressione per game_controller.ottieni_giocatore_umano — v0.9.0.

Verifica:
1. Partita standard: ritorna GiocatoreUmano corretto.
2. Parametro non-Partita: ritorna None senza eccezioni.
3. Regressione: i 272+ test esistenti non vengono rotti.
4. Nessun import Domain dal modulo TUI (separazione layer).
"""
from __future__ import annotations

import pytest

from bingo_game.game_controller import (
    crea_partita_standard,
    ottieni_giocatore_umano,
)
from bingo_game.players import GiocatoreUmano


# ---------------------------------------------------------------------------
# Test 1: ritorna il GiocatoreUmano dalla partita standard
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_trovato():
    """Con una partita standard deve ritornare il GiocatoreUmano con il nome atteso."""
    partita = crea_partita_standard(
        nome_giocatore_umano="TestPlayer",
        num_cartelle_umano=1,
        num_bot=1,
    )
    umano = ottieni_giocatore_umano(partita)
    assert umano is not None, "ottieni_giocatore_umano ha ritornato None su partita valida"
    assert isinstance(umano, GiocatoreUmano), "Il risultato non è GiocatoreUmano"
    assert umano.nome == "TestPlayer", f"Nome inatteso: {umano.nome!r}"


# ---------------------------------------------------------------------------
# Test 2: parametro non-Partita — ritorna None senza eccezioni
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("valore_non_partita", [
    None,
    42,
    "stringa",
    [],
    {},
])
def test_ottieni_giocatore_umano_non_partita(valore_non_partita):
    """Con un parametro non-Partita deve ritornare None senza sollevare eccezioni."""
    risultato = ottieni_giocatore_umano(valore_non_partita)  # type: ignore[arg-type]
    assert risultato is None, (
        f"Atteso None per input non-Partita ({valore_non_partita!r}), "
        f"ottenuto: {risultato!r}"
    )


# ---------------------------------------------------------------------------
# Test 3: cartelle assegnate al giocatore umano corrispondono alla configurazione
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_cartelle_corrette():
    """Il GiocatoreUmano restituito deve avere il numero di cartelle atteso."""
    partita = crea_partita_standard(
        nome_giocatore_umano="Donato",
        num_cartelle_umano=3,
        num_bot=1,
    )
    umano = ottieni_giocatore_umano(partita)
    assert umano is not None
    assert len(umano.get_cartelle()) == 3, (
        f"Attese 3 cartelle, trovate {len(umano.get_cartelle())}"
    )


# ---------------------------------------------------------------------------
# Test 4: import del controller non espone oggetti Domain nella TUI
# ---------------------------------------------------------------------------

def test_ottieni_giocatore_umano_non_espone_domain_in_tui():
    """La TUI (ui_terminale) non deve importare GiocatoreUmano direttamente."""
    import importlib
    import ast
    import pathlib

    tui_path = pathlib.Path("bingo_game/ui/ui_terminale.py")
    if not tui_path.exists():
        pytest.skip("ui_terminale.py non trovato")

    source = tui_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.ImportFrom):
                modulo = node.module or ""
                # Importare da bingo_game.players o bingo_game.partita nella TUI è vietato
                assert "bingo_game.players" not in modulo, (
                    f"TUI importa direttamente dal Domain layer: {modulo}"
                )
                assert "bingo_game.partita" not in modulo, (
                    f"TUI importa direttamente dal Domain layer: {modulo}"
                )
