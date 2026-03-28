"""
Test unitari per bingo_game/events/codici_loop.py — v0.9.0

Verifica:
1. Tutte le costanti sono stringhe non vuote.
2. Nessuna costante è duplicata.
3. Tutte le 13 chiavi LOOP_* sono presenti in MESSAGGI_OUTPUT_UI_UMANI.
4. I template con placeholder sono formattabili senza eccezioni.
5. L'import di codici_loop non produce side effect.
"""
from __future__ import annotations

import importlib
import sys
import unittest


# ---------------------------------------------------------------------------
# Test 1 — Le costanti sono stringhe non vuote
# ---------------------------------------------------------------------------

class TestCodiciLoop(unittest.TestCase):
    """Test unitari unittest per il modulo codici_loop."""

    CHIAVI_LOOP_ATTESE = [
        "LOOP_NUMERO_ESTRATTO",
        "LOOP_PROMPT_COMANDO",
        "LOOP_HELP_COMANDI",
        "LOOP_HELP_FOCUS",
        "LOOP_QUIT_CONFERMA",
        "LOOP_QUIT_ANNULLATO",
        "LOOP_REPORT_FINALE_INTESTAZIONE",
        "LOOP_REPORT_FINALE_TURNI",
        "LOOP_REPORT_FINALE_ESTRATTI",
        "LOOP_REPORT_FINALE_VINCITORE",
        "LOOP_REPORT_FINALE_NESSUN_VINCITORE",
        "LOOP_REPORT_FINALE_PREMI",
        "LOOP_COMANDO_NON_RICONOSCIUTO",
    ]

    def _costanti_loop(self) -> list[str]:
        from bingo_game.events.codici_loop import (
            LOOP_FOCUS_AUTO,
            LOOP_HELP,
            LOOP_NUMERO_ESTRATTO,
            LOOP_QUIT_ANNULLATO,
            LOOP_QUIT_CONFERMATO,
            LOOP_REPORT_FINALE,
            LOOP_SEGNAZIONE_OK,
            LOOP_TURNO_AVANZATO,
        )

        return [
            LOOP_TURNO_AVANZATO,
            LOOP_NUMERO_ESTRATTO,
            LOOP_SEGNAZIONE_OK,
            LOOP_REPORT_FINALE,
            LOOP_QUIT_CONFERMATO,
            LOOP_QUIT_ANNULLATO,
            LOOP_HELP,
            LOOP_FOCUS_AUTO,
        ]

    def test_costanti_loop_sono_stringhe_non_vuote(self) -> None:
        """Tutte le costanti in codici_loop sono str non vuote."""
        for costante in self._costanti_loop():
            self.assertIsInstance(costante, str, f"Costante non è str: {costante!r}")
            self.assertGreater(len(costante), 0, f"Costante è stringa vuota: {costante!r}")


# ---------------------------------------------------------------------------
# Test 2 — Nessuna costante duplicata
# ---------------------------------------------------------------------------

    def test_costanti_loop_nessun_duplicato(self) -> None:
        """Nessuna costante in codici_loop è duplicata."""
        costanti = self._costanti_loop()
        self.assertEqual(len(costanti), len(set(costanti)), "Costanti duplicate trovate in codici_loop")


    def test_chiavi_loop_presenti_in_messaggi_output_ui_umani(self) -> None:
        """Ogni chiave LOOP_* deve essere presente in MESSAGGI_OUTPUT_UI_UMANI."""
        from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI

        for chiave in self.CHIAVI_LOOP_ATTESE:
            with self.subTest(chiave=chiave):
                self.assertIn(
                    chiave,
                    MESSAGGI_OUTPUT_UI_UMANI,
                    f"Chiave mancante in MESSAGGI_OUTPUT_UI_UMANI: {chiave!r}",
                )


# ---------------------------------------------------------------------------
# Test 4 — I template con placeholder sono formattabili
# ---------------------------------------------------------------------------

    def test_template_placeholder_formattabili(self) -> None:
        """I template con placeholder non sollevano eccezioni se formattati con valori dummy."""
        from bingo_game.ui.locales.it import MESSAGGI_OUTPUT_UI_UMANI

        valori_dummy = {
            "numero": 42,
            "numero_cartella": 1,
            "turni": 10,
            "estratti": 45,
            "nome": "Mario",
            "premi": 3,
        }

        chiavi_con_placeholder = [
            "LOOP_NUMERO_ESTRATTO",
            "LOOP_HELP_FOCUS",
            "LOOP_REPORT_FINALE_TURNI",
            "LOOP_REPORT_FINALE_ESTRATTI",
            "LOOP_REPORT_FINALE_VINCITORE",
            "LOOP_REPORT_FINALE_PREMI",
        ]

        for chiave in chiavi_con_placeholder:
            for riga in MESSAGGI_OUTPUT_UI_UMANI[chiave]:
                with self.subTest(chiave=chiave, riga=riga):
                    try:
                        risultato = riga.format(**valori_dummy)
                    except KeyError as exc:
                        self.fail(
                            f"Placeholder mancante per chiave {chiave!r}, riga {riga!r}: {exc}"
                        )
                    self.assertIsInstance(risultato, str)


# ---------------------------------------------------------------------------
# Test 5 — L'import di codici_loop non produce side effect
# ---------------------------------------------------------------------------

    def test_import_codici_loop_no_side_effect(self) -> None:
        """L'import di codici_loop non deve produrre side effect visibili."""
        sys.modules.pop("bingo_game.events.codici_loop", None)
        modulo = importlib.import_module("bingo_game.events.codici_loop")
        self.assertTrue(hasattr(modulo, "LOOP_TURNO_AVANZATO"))
        self.assertTrue(hasattr(modulo, "LOOP_HELP"))
        self.assertTrue(hasattr(modulo, "LOOP_FOCUS_AUTO"))


if __name__ == "__main__":
    unittest.main()
