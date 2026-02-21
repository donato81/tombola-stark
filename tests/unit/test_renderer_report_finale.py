"""
Test unitari per TerminalRenderer — vocalizzazione gerarchica (Fase 4/5 v0.9.0)

Verifica i contratti di output dei metodi renderer critici per il Game Loop:
1.  _render_evento_riepilogo_tabellone → esattamente 3 righe.
2.  Tutte le righe di _render_evento_riepilogo_tabellone ≤ 120 caratteri.
3.  _render_evento_segnazione_numero esito 'segnato' → 1 riga con il numero.
4.  _render_evento_segnazione_numero esito 'gia_segnato' → 1 riga.
5.  _render_evento_segnazione_numero esito 'non_presente' → 1 riga.
6.  _render_evento_segnazione_numero esito 'non_estratto' → 1 riga.
7.  _render_evento_fine_turno senza reclamo → 1 riga.
8.  _render_evento_riepilogo_cartella_corrente → esattamente 2 righe.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def renderer():
    from bingo_game.ui.renderers.renderer_terminal import TerminalRenderer
    return TerminalRenderer()


@pytest.fixture
def evento_riepilogo_tabellone():
    """EventoRiepilogoTabellone con estratti presenti."""
    from bingo_game.events.eventi_output_ui_umani import EventoRiepilogoTabellone
    return EventoRiepilogoTabellone(
        id_giocatore=1,
        nome_giocatore="TestPlayer",
        totale_numeri=90,
        totale_estratti=10,
        totale_mancanti=80,
        percentuale_estrazione=11.1,
        ultimi_estratti=(5, 23, 42),
        ultimi_visualizzati=3,
        ultimo_estratto=42,
    )


@pytest.fixture
def evento_segnazione_segnato():
    """EventoSegnazioneNumero con esito 'segnato'."""
    from bingo_game.events.eventi_output_ui_umani import EventoSegnazioneNumero
    return EventoSegnazioneNumero(
        id_giocatore=1,
        nome_giocatore="TestPlayer",
        esito="segnato",
        numero=42,
        indice_cartella=0,
        numero_cartella=1,
        totale_cartelle=1,
        indice_riga=1,
        indice_colonna=2,
        numeri_segnati=5,
        totale_numeri=15,
        mancanti=10,
        percentuale=33.3,
    )


@pytest.fixture
def evento_segnazione_gia_segnato():
    """EventoSegnazioneNumero con esito 'gia_segnato'."""
    from bingo_game.events.eventi_output_ui_umani import EventoSegnazioneNumero
    return EventoSegnazioneNumero(
        id_giocatore=1,
        nome_giocatore="TestPlayer",
        esito="gia_segnato",
        numero=42,
        indice_cartella=0,
        numero_cartella=1,
        totale_cartelle=1,
        indice_riga=None,
        indice_colonna=None,
        numeri_segnati=5,
        totale_numeri=15,
        mancanti=10,
        percentuale=33.3,
    )


@pytest.fixture
def evento_segnazione_non_presente():
    """EventoSegnazioneNumero con esito 'non_presente'."""
    from bingo_game.events.eventi_output_ui_umani import EventoSegnazioneNumero
    return EventoSegnazioneNumero(
        id_giocatore=1,
        nome_giocatore="TestPlayer",
        esito="non_presente",
        numero=7,
        indice_cartella=0,
        numero_cartella=1,
        totale_cartelle=1,
        indice_riga=None,
        indice_colonna=None,
        numeri_segnati=5,
        totale_numeri=15,
        mancanti=10,
        percentuale=33.3,
    )


@pytest.fixture
def evento_segnazione_non_estratto():
    """EventoSegnazioneNumero con esito 'non_estratto'."""
    from bingo_game.events.eventi_output_ui_umani import EventoSegnazioneNumero
    return EventoSegnazioneNumero(
        id_giocatore=1,
        nome_giocatore="TestPlayer",
        esito="non_estratto",
        numero=88,
        indice_cartella=0,
        numero_cartella=1,
        totale_cartelle=1,
        indice_riga=None,
        indice_colonna=None,
        numeri_segnati=5,
        totale_numeri=15,
        mancanti=10,
        percentuale=33.3,
    )


@pytest.fixture
def evento_fine_turno():
    """EventoFineTurno senza reclamo."""
    from bingo_game.events.eventi_partita import EventoFineTurno
    return EventoFineTurno(
        id_giocatore=1,
        nome_giocatore="TestPlayer",
        numero_turno=5,
        reclamo_turno=None,
    )


@pytest.fixture
def evento_riepilogo_cartella():
    """EventoRiepilogoCartellaCorrente con numeri mancanti."""
    from bingo_game.events.eventi_output_ui_umani import EventoRiepilogoCartellaCorrente
    return EventoRiepilogoCartellaCorrente(
        id_giocatore=1,
        nome_giocatore="TestPlayer",
        indice_cartella=0,
        numero_cartella=1,
        numeri_segnati=3,
        totale_numeri=15,
        mancanti=12,
        percentuale=20.0,
        numeri_non_segnati=(10, 20, 30, 40),
    )


# ---------------------------------------------------------------------------
# Test 1 — _render_evento_riepilogo_tabellone: esattamente 3 righe
# ---------------------------------------------------------------------------

def test_riepilogo_tabellone_tre_righe(renderer, evento_riepilogo_tabellone):
    """_render_evento_riepilogo_tabellone deve ritornare esattamente 3 righe."""
    righe = renderer._render_evento_riepilogo_tabellone(evento_riepilogo_tabellone)
    assert len(righe) == 3, (
        f"Attese 3 righe, ottenute {len(righe)}: {righe}"
    )


# ---------------------------------------------------------------------------
# Test 2 — _render_evento_riepilogo_tabellone: tutte ≤ 120 caratteri
# ---------------------------------------------------------------------------

def test_riepilogo_tabellone_righe_max_120(renderer, evento_riepilogo_tabellone):
    """Tutte le righe di _render_evento_riepilogo_tabellone devono essere ≤ 120 caratteri."""
    righe = renderer._render_evento_riepilogo_tabellone(evento_riepilogo_tabellone)
    for i, riga in enumerate(righe):
        assert len(riga) <= 120, (
            f"Riga {i+1} supera 120 caratteri ({len(riga)}): {riga!r}"
        )


# ---------------------------------------------------------------------------
# Test 3 — _render_evento_segnazione_numero 'segnato': 1 riga con numero
# ---------------------------------------------------------------------------

def test_segnazione_segnato_una_riga_con_numero(renderer, evento_segnazione_segnato):
    """_render_evento_segnazione_numero esito 'segnato' deve produrre 1 riga con il numero."""
    righe = renderer._render_evento_segnazione_numero(evento_segnazione_segnato)
    assert len(righe) == 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}"
    assert "42" in righe[0], f"Numero 42 non trovato nella riga: {righe[0]!r}"


# ---------------------------------------------------------------------------
# Test 4 — _render_evento_segnazione_numero 'gia_segnato': 1 riga
# ---------------------------------------------------------------------------

def test_segnazione_gia_segnato_una_riga(renderer, evento_segnazione_gia_segnato):
    """_render_evento_segnazione_numero esito 'gia_segnato' deve produrre 1 riga."""
    righe = renderer._render_evento_segnazione_numero(evento_segnazione_gia_segnato)
    assert len(righe) == 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}"


# ---------------------------------------------------------------------------
# Test 5 — _render_evento_segnazione_numero 'non_presente': 1 riga
# ---------------------------------------------------------------------------

def test_segnazione_non_presente_una_riga(renderer, evento_segnazione_non_presente):
    """_render_evento_segnazione_numero esito 'non_presente' deve produrre 1 riga."""
    righe = renderer._render_evento_segnazione_numero(evento_segnazione_non_presente)
    assert len(righe) == 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}"


# ---------------------------------------------------------------------------
# Test 6 — _render_evento_segnazione_numero 'non_estratto': 1 riga
# ---------------------------------------------------------------------------

def test_segnazione_non_estratto_una_riga(renderer, evento_segnazione_non_estratto):
    """_render_evento_segnazione_numero esito 'non_estratto' deve produrre 1 riga."""
    righe = renderer._render_evento_segnazione_numero(evento_segnazione_non_estratto)
    assert len(righe) == 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}"


# ---------------------------------------------------------------------------
# Test 7 — _render_evento_fine_turno senza reclamo: 1 riga
# ---------------------------------------------------------------------------

def test_fine_turno_senza_reclamo_una_riga(renderer, evento_fine_turno):
    """_render_evento_fine_turno senza reclamo deve produrre 1 riga."""
    righe = renderer._render_evento_fine_turno(evento_fine_turno)
    assert len(righe) == 1, f"Attesa 1 riga, ottenute {len(righe)}: {righe}"


# ---------------------------------------------------------------------------
# Test 8 — _render_evento_riepilogo_cartella_corrente: esattamente 2 righe
# ---------------------------------------------------------------------------

def test_riepilogo_cartella_corrente_due_righe(renderer, evento_riepilogo_cartella):
    """_render_evento_riepilogo_cartella_corrente deve produrre esattamente 2 righe."""
    righe = renderer._render_evento_riepilogo_cartella_corrente(evento_riepilogo_cartella)
    assert len(righe) == 2, (
        f"Attese 2 righe, ottenute {len(righe)}: {righe}"
    )
