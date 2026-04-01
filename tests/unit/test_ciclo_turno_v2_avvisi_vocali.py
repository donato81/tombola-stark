"""
Test unitari per i nuovi annunci vocali del Ciclo Turno V2.

Usa un renderer stub per verificare che i tre nuovi metodi astratti vengano
chiamati correttamente, senza dipendere da wx o accessible_output2.

Task C-4.
"""
from __future__ import annotations

import unittest

from bingo_game.ui.renderers.base_renderer import BaseRenderer, StatoConfigurazione
from bingo_game.events.eventi import EsitoAzione


class _RendererStub(BaseRenderer):
    """Implementazione minimale di BaseRenderer per i test degli avvisi vocali."""

    def __init__(self) -> None:
        self.chiamate: list[tuple[str, object]] = []

    # --- Metodi astratti obbligatori (stub no-op) ---
    def render_esito(self, esito: EsitoAzione) -> None:
        self.chiamate.append(("render_esito", esito))

    def mostra_schermata_configurazione(self, stato: StatoConfigurazione) -> None:
        self.chiamate.append(("mostra_schermata_configurazione", stato))

    def mostra_report_finale(self, dati_partita: dict) -> None:
        self.chiamate.append(("mostra_report_finale", dati_partita))

    def mostra_messaggio_sistema(self, testo: str) -> None:
        self.chiamate.append(("mostra_messaggio_sistema", testo))

    def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
        self.chiamate.append(("annuncia_numero_estratto", (numero, numero_turno)))

    def annuncia_premi_turno(self, premi: list) -> None:
        self.chiamate.append(("annuncia_premi_turno", premi))

    def annuncia_fase_turno(self, testo_fase: str) -> None:
        self.chiamate.append(("annuncia_fase_turno", testo_fase))

    # --- Nuovi metodi V2 ---
    def annuncia_avviso_timeout(self, secondi_rimanenti: int, livello: int = 80) -> None:
        self.chiamate.append(("annuncia_avviso_timeout", (secondi_rimanenti, livello)))

    def annuncia_avvio_pausa_turno(self, secondi: int) -> None:
        self.chiamate.append(("annuncia_avvio_pausa_turno", secondi))

    def annuncia_tutti_pronti(self) -> None:
        self.chiamate.append(("annuncia_tutti_pronti", None))


class TestAvvisiVocali(unittest.TestCase):

    def setUp(self) -> None:
        self.renderer = _RendererStub()

    def test_annuncia_avviso_timeout_viene_chiamato(self) -> None:
        """annuncia_avviso_timeout() viene chiamato con i secondi rimanenti e il livello."""
        self.renderer.annuncia_avviso_timeout(24, livello=80)

        nomi = [c[0] for c in self.renderer.chiamate]
        self.assertIn("annuncia_avviso_timeout", nomi)

        idx = nomi.index("annuncia_avviso_timeout")
        self.assertEqual(self.renderer.chiamate[idx][1], (24, 80))

    def test_annuncia_avvio_pausa_viene_chiamato(self) -> None:
        """annuncia_avvio_pausa_turno() viene chiamato con la durata pausa."""
        self.renderer.annuncia_avvio_pausa_turno(5)

        nomi = [c[0] for c in self.renderer.chiamate]
        self.assertIn("annuncia_avvio_pausa_turno", nomi)

        idx = nomi.index("annuncia_avvio_pausa_turno")
        self.assertEqual(self.renderer.chiamate[idx][1], 5)

    def test_annuncia_tutti_pronti_viene_chiamato(self) -> None:
        """annuncia_tutti_pronti() viene chiamato senza argomenti."""
        self.renderer.annuncia_tutti_pronti()

        nomi = [c[0] for c in self.renderer.chiamate]
        self.assertIn("annuncia_tutti_pronti", nomi)

    def test_stub_non_solleva_eccezioni(self) -> None:
        """Tutti e tre i nuovi metodi non sollevano eccezioni."""
        try:
            self.renderer.annuncia_avviso_timeout(10)
            self.renderer.annuncia_avvio_pausa_turno(5)
            self.renderer.annuncia_tutti_pronti()
        except Exception as exc:
            self.fail(f"Metodo ha sollevato eccezione inattesa: {exc}")

    def test_renderer_istanziabile_con_metodi_v2(self) -> None:
        """Il renderer stub (che implementa i nuovi metodi) è istanziabile."""
        renderer = _RendererStub()
        self.assertIsNotNone(renderer)
