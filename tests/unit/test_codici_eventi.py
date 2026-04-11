"""Test di contratto per i sette moduli codici_*.py — Gruppo A.

Verifica importabilita', valori stringa esatti e coerenza con Literal.
Nessuna dipendenza da wx, mock o filesystem.
"""
from __future__ import annotations

import unittest
from typing import get_args

from bingo_game.events import codici_configurazione
from bingo_game.events import codici_controller
from bingo_game.events import codici_errori
from bingo_game.events import codici_eventi
from bingo_game.events import codici_loop
from bingo_game.events import codici_messaggi_sistema
from bingo_game.events import codici_output_ui_umani


# ---------------------------------------------------------------------------
# 1. codici_configurazione
# ---------------------------------------------------------------------------

class TestCodiciConfigurazione(unittest.TestCase):
    """Contratto del modulo bingo_game.events.codici_configurazione."""

    def test_importazione_modulo(self) -> None:
        import bingo_game.events.codici_configurazione as m
        self.assertIsNotNone(m)

    def test_config_benvenuto(self) -> None:
        self.assertEqual(codici_configurazione.CONFIG_BENVENUTO, "CONFIG_BENVENUTO")

    def test_config_conferma_avvio(self) -> None:
        self.assertEqual(codici_configurazione.CONFIG_CONFERMA_AVVIO, "CONFIG_CONFERMA_AVVIO")

    def test_config_richiesta_nome(self) -> None:
        self.assertEqual(codici_configurazione.CONFIG_RICHIESTA_NOME, "CONFIG_RICHIESTA_NOME")

    def test_config_richiesta_bot(self) -> None:
        self.assertEqual(codici_configurazione.CONFIG_RICHIESTA_BOT, "CONFIG_RICHIESTA_BOT")

    def test_config_richiesta_cartelle(self) -> None:
        self.assertEqual(
            codici_configurazione.CONFIG_RICHIESTA_CARTELLE, "CONFIG_RICHIESTA_CARTELLE"
        )

    def test_config_errore_nome_vuoto(self) -> None:
        self.assertEqual(
            codici_configurazione.CONFIG_ERRORE_NOME_VUOTO, "CONFIG_ERRORE_NOME_VUOTO"
        )

    def test_config_errore_nome_troppo_lungo(self) -> None:
        self.assertEqual(
            codici_configurazione.CONFIG_ERRORE_NOME_TROPPO_LUNGO,
            "CONFIG_ERRORE_NOME_TROPPO_LUNGO",
        )

    def test_config_errore_bot_range(self) -> None:
        self.assertEqual(
            codici_configurazione.CONFIG_ERRORE_BOT_RANGE, "CONFIG_ERRORE_BOT_RANGE"
        )

    def test_config_errore_cartelle_range(self) -> None:
        self.assertEqual(
            codici_configurazione.CONFIG_ERRORE_CARTELLE_RANGE,
            "CONFIG_ERRORE_CARTELLE_RANGE",
        )

    def test_insieme_costanti_attese(self) -> None:
        attese = {
            "CONFIG_BENVENUTO",
            "CONFIG_CONFERMA_AVVIO",
            "CONFIG_RICHIESTA_NOME",
            "CONFIG_RICHIESTA_BOT",
            "CONFIG_RICHIESTA_CARTELLE",
            "CONFIG_ERRORE_NOME_VUOTO",
            "CONFIG_ERRORE_NOME_TROPPO_LUNGO",
            "CONFIG_ERRORE_BOT_RANGE",
            "CONFIG_ERRORE_CARTELLE_RANGE",
        }
        presenti = {
            name
            for name in dir(codici_configurazione)
            if name.startswith("CONFIG_")
            and isinstance(getattr(codici_configurazione, name), str)
        }
        self.assertEqual(presenti, attese)


# ---------------------------------------------------------------------------
# 2. codici_controller
# ---------------------------------------------------------------------------

class TestCodiciController(unittest.TestCase):
    """Contratto del modulo bingo_game.events.codici_controller."""

    def test_importazione_modulo(self) -> None:
        import bingo_game.events.codici_controller as m
        self.assertIsNotNone(m)

    def test_ctrl_avvio_fallito_generico(self) -> None:
        self.assertEqual(
            codici_controller.CTRL_AVVIO_FALLITO_GENERICO,
            "ctrl.avvio_fallito_generico",
        )

    def test_ctrl_turno_non_in_corso(self) -> None:
        self.assertEqual(
            codici_controller.CTRL_TURNO_NON_IN_CORSO, "ctrl.turno_non_in_corso"
        )

    def test_ctrl_numeri_esauriti(self) -> None:
        self.assertEqual(codici_controller.CTRL_NUMERI_ESAURITI, "ctrl.numeri_esauriti")

    def test_ctrl_turno_fallito_generico(self) -> None:
        self.assertEqual(
            codici_controller.CTRL_TURNO_FALLITO_GENERICO,
            "ctrl.turno_fallito_generico",
        )

    def test_insieme_valori_attesi(self) -> None:
        attesi = {
            "ctrl.avvio_fallito_generico",
            "ctrl.turno_non_in_corso",
            "ctrl.numeri_esauriti",
            "ctrl.turno_fallito_generico",
        }
        presenti = {
            getattr(codici_controller, name)
            for name in dir(codici_controller)
            if name.startswith("CTRL_")
            and isinstance(getattr(codici_controller, name), str)
        }
        self.assertEqual(presenti, attesi)


# ---------------------------------------------------------------------------
# 3. codici_errori
# ---------------------------------------------------------------------------

class TestCodiciErrori(unittest.TestCase):
    """Contratto del modulo bingo_game.events.codici_errori."""

    def test_importazione_modulo(self) -> None:
        import bingo_game.events.codici_errori as m
        self.assertIsNotNone(m)

    def test_codici_errori_generici_contenuto(self) -> None:
        attesi = {"NON_IMPLEMENTATO", "ERRORE_INTERNO"}
        self.assertEqual(set(get_args(codici_errori.Codici_Errori_Generici)), attesi)

    def test_codici_errori_ui_contenuto(self) -> None:
        attesi = {
            "INPUT_NON_VALIDO",
            "NUMERO_NON_VALIDO",
            "NUMERO_TIPO_NON_VALIDO",
            "TABELLONE_NON_DISPONIBILE",
            "CARTELLA_STATO_INCOERENTE",
            "CARTELLE_NESSUNA_ASSEGNATA",
            "FOCUS_CARTELLA_NON_IMPOSTATO",
            "FOCUS_CARTELLA_FUORI_RANGE",
            "NUMERO_CARTELLA_FUORI_RANGE",
            "NUMERO_CARTELLA_TIPO_NON_VALIDO",
            "FOCUS_RIGA_NON_IMPOSTATA",
            "FOCUS_RIGA_FUORI_RANGE",
            "FOCUS_COLONNA_NON_IMPOSTATA",
            "FOCUS_COLONNA_FUORI_RANGE",
            "ANNUNCIO_CARTELLA_NON_SELEZIONATA",
            "ANNUNCIO_RIGA_NON_SELEZIONATA",
            "TIPO_VITTORIA_NON_VALIDO",
        }
        self.assertEqual(set(get_args(codici_errori.Codici_Errori_Ui)), attesi)

    def test_codici_errori_partita_contenuto(self) -> None:
        attesi = {
            "RECLAMO_GIA_PRESENTE",
            "RECLAMO_ASSENTE",
            "CARTELLA_NON_TROVATA",
            "RIGA_NON_VALIDA",
            "PREMIO_GIA_ASSEGNATO",
            "PREMIO_NON_DISPONIBILE",
            "VERIFICA_FALLITA",
            "PREREQUISITI_MANCANTI",
            "NUMERO_RIGA_FUORI_RANGE",
            "NUMERO_COLONNA_FUORI_RANGE",
        }
        self.assertEqual(set(get_args(codici_errori.Codici_Errori_Partita)), attesi)

    def test_nessuna_sovrapposizione_generici_ui(self) -> None:
        generici = set(get_args(codici_errori.Codici_Errori_Generici))
        ui = set(get_args(codici_errori.Codici_Errori_Ui))
        self.assertEqual(generici & ui, set())

    def test_nessuna_sovrapposizione_generici_partita(self) -> None:
        generici = set(get_args(codici_errori.Codici_Errori_Generici))
        partita = set(get_args(codici_errori.Codici_Errori_Partita))
        self.assertEqual(generici & partita, set())

    def test_nessuna_sovrapposizione_ui_partita(self) -> None:
        ui = set(get_args(codici_errori.Codici_Errori_Ui))
        partita = set(get_args(codici_errori.Codici_Errori_Partita))
        self.assertEqual(ui & partita, set())

    def test_unione_tre_gruppi_uguale_contratto_globale(self) -> None:
        generici = set(get_args(codici_errori.Codici_Errori_Generici))
        ui = set(get_args(codici_errori.Codici_Errori_Ui))
        partita = set(get_args(codici_errori.Codici_Errori_Partita))
        unione = generici | ui | partita
        # Estrae i valori dall'alias aggregato Codici_Errori (Union di tre Literal).
        # get_args restituisce i tipi costituenti; per ognuno si estraggono i valori.
        union_args = get_args(codici_errori.Codici_Errori)
        contratto_globale: set[str] = set()
        for literal_type in union_args:
            contratto_globale.update(get_args(literal_type))
        self.assertEqual(unione, contratto_globale)


# ---------------------------------------------------------------------------
# 4. codici_eventi
# ---------------------------------------------------------------------------

class TestCodiciEventi(unittest.TestCase):
    """Contratto del modulo bingo_game.events.codici_eventi."""

    def test_importazione_modulo(self) -> None:
        import bingo_game.events.codici_eventi as m
        self.assertIsNotNone(m)

    def test_evento_focus_auto_impostato_valore(self) -> None:
        self.assertEqual(
            codici_eventi.EVENTO_FOCUS_AUTO_IMPOSTATO,
            "EVENTO_FOCUS_AUTO_IMPOSTATO",
        )

    def test_allineamento_costante_literal(self) -> None:
        costanti = {
            codici_eventi.EVENTO_FOCUS_AUTO_IMPOSTATO,
            codici_eventi.TURNO_AVVISO_60,
            codici_eventi.TURNO_AVVISO_80,
            codici_eventi.TURNO_AVVISO_95,
            codici_eventi.TURNO_TIMEOUT_SALTATO,
            codici_eventi.TURNO_TUTTI_PRONTI,
            codici_eventi.TURNO_PAUSA_INIZIO,
            codici_eventi.TURNO_PAUSA_COUNTDOWN,
            codici_eventi.PAUSA_ATTIVATA,
            codici_eventi.PAUSA_DISATTIVATA,
        }
        literal_vals = set(get_args(codici_eventi.Codici_Eventi))
        self.assertEqual(costanti, literal_vals)


# ---------------------------------------------------------------------------
# 5. codici_loop
# ---------------------------------------------------------------------------

class TestCodiciLoop(unittest.TestCase):
    """Contratto del modulo bingo_game.events.codici_loop."""

    def test_importazione_modulo(self) -> None:
        import bingo_game.events.codici_loop as m
        self.assertIsNotNone(m)

    def test_loop_turno_avanzato(self) -> None:
        self.assertEqual(codici_loop.LOOP_TURNO_AVANZATO, "LOOP_TURNO_AVANZATO")

    def test_loop_numero_estratto(self) -> None:
        self.assertEqual(codici_loop.LOOP_NUMERO_ESTRATTO, "LOOP_NUMERO_ESTRATTO")

    def test_loop_segnazione_ok(self) -> None:
        self.assertEqual(codici_loop.LOOP_SEGNAZIONE_OK, "LOOP_SEGNAZIONE_OK")

    def test_loop_report_finale(self) -> None:
        self.assertEqual(codici_loop.LOOP_REPORT_FINALE, "LOOP_REPORT_FINALE")

    def test_loop_quit_confermato(self) -> None:
        self.assertEqual(codici_loop.LOOP_QUIT_CONFERMATO, "LOOP_QUIT_CONFERMATO")

    def test_loop_quit_annullato(self) -> None:
        self.assertEqual(codici_loop.LOOP_QUIT_ANNULLATO, "LOOP_QUIT_ANNULLATO")

    def test_loop_help(self) -> None:
        self.assertEqual(codici_loop.LOOP_HELP, "LOOP_HELP")

    def test_loop_focus_auto(self) -> None:
        self.assertEqual(codici_loop.LOOP_FOCUS_AUTO, "LOOP_FOCUS_AUTO")

    def test_allineamento_costanti_literal(self) -> None:
        costanti = {
            codici_loop.LOOP_TURNO_AVANZATO,
            codici_loop.LOOP_NUMERO_ESTRATTO,
            codici_loop.LOOP_SEGNAZIONE_OK,
            codici_loop.LOOP_REPORT_FINALE,
            codici_loop.LOOP_QUIT_CONFERMATO,
            codici_loop.LOOP_QUIT_ANNULLATO,
            codici_loop.LOOP_HELP,
            codici_loop.LOOP_FOCUS_AUTO,
        }
        literal_vals = set(get_args(codici_loop.Codici_Loop))
        self.assertEqual(costanti, literal_vals)


# ---------------------------------------------------------------------------
# 6. codici_messaggi_sistema
# ---------------------------------------------------------------------------

class TestCodiciMessaggiSistema(unittest.TestCase):
    """Contratto del modulo bingo_game.events.codici_messaggi_sistema."""

    def test_importazione_modulo(self) -> None:
        import bingo_game.events.codici_messaggi_sistema as m
        self.assertIsNotNone(m)

    def test_sistema_errore_codice_mancante(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_ERRORE_CODICE_MANCANTE,
            "SISTEMA_ERRORE_CODICE_MANCANTE",
        )

    def test_sistema_errore_messaggio_non_disponibile(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_ERRORE_MESSAGGIO_NON_DISPONIBILE,
            "SISTEMA_ERRORE_MESSAGGIO_NON_DISPONIBILE",
        )

    def test_sistema_errore_codice_non_mappato_debug(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_ERRORE_CODICE_NON_MAPPATO_DEBUG,
            "SISTEMA_ERRORE_CODICE_NON_MAPPATO_DEBUG",
        )

    def test_sistema_selezione_automatica_effettuata(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_SELEZIONE_AUTOMATICA_EFFETTUATA,
            "SISTEMA_SELEZIONE_AUTOMATICA_EFFETTUATA",
        )

    def test_sistema_tipo_focus_non_previsto_debug(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_TIPO_FOCUS_NON_PREVISTO_DEBUG,
            "SISTEMA_TIPO_FOCUS_NON_PREVISTO_DEBUG",
        )

    def test_sistema_template_evento_mancante_debug(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_TEMPLATE_EVENTO_MANCANTE_DEBUG,
            "SISTEMA_TEMPLATE_EVENTO_MANCANTE_DEBUG",
        )

    def test_sistema_placeholder_template_mancante_debug(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_PLACEHOLDER_TEMPLATE_MANCANTE_DEBUG,
            "SISTEMA_PLACEHOLDER_TEMPLATE_MANCANTE_DEBUG",
        )

    def test_sistema_focus_cartella_impostato(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_FOCUS_CARTELLA_IMPOSTATO,
            "SISTEMA_FOCUS_CARTELLA_IMPOSTATO",
        )

    def test_sistema_focus_reset_riga_colonna(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_FOCUS_RESET_RIGA_COLONNA,
            "SISTEMA_FOCUS_RESET_RIGA_COLONNA",
        )

    def test_sistema_turno_passato(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_TURNO_PASSATO, "SISTEMA_TURNO_PASSATO"
        )

    def test_sistema_reclamo_associato_tombola(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_RECLAMO_ASSOCIATO_TOMBOLA,
            "SISTEMA_RECLAMO_ASSOCIATO_TOMBOLA",
        )

    def test_sistema_reclamo_associato_riga(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_RECLAMO_ASSOCIATO_RIGA,
            "SISTEMA_RECLAMO_ASSOCIATO_RIGA",
        )

    def test_sistema_reclamo_associato_riga_non_disponibile(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_RECLAMO_ASSOCIATO_RIGA_NON_DISPONIBILE,
            "SISTEMA_RECLAMO_ASSOCIATO_RIGA_NON_DISPONIBILE",
        )

    def test_sistema_reclamo_inviato(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_RECLAMO_INVIATO,
            "SISTEMA_RECLAMO_INVIATO",
        )

    def test_sistema_riferimento_tombola(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_RIFERIMENTO_TOMBOLA,
            "SISTEMA_RIFERIMENTO_TOMBOLA",
        )

    def test_sistema_riferimento_riga(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_RIFERIMENTO_RIGA,
            "SISTEMA_RIFERIMENTO_RIGA",
        )

    def test_sistema_riferimento_riga_non_disponibile(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_RIFERIMENTO_RIGA_NON_DISPONIBILE,
            "SISTEMA_RIFERIMENTO_RIGA_NON_DISPONIBILE",
        )

    def test_sistema_esito_reclamo(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_ESITO_RECLAMO,
            "SISTEMA_ESITO_RECLAMO",
        )

    def test_sistema_esito_reclamo_motivo(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_ESITO_RECLAMO_MOTIVO,
            "SISTEMA_ESITO_RECLAMO_MOTIVO",
        )

    def test_sistema_esito_reclamo_turno(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_ESITO_RECLAMO_TURNO,
            "SISTEMA_ESITO_RECLAMO_TURNO",
        )

    def test_sistema_esito_reclamo_numero_estratto(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_ESITO_RECLAMO_NUMERO_ESTRATTO,
            "SISTEMA_ESITO_RECLAMO_NUMERO_ESTRATTO",
        )

    def test_sistema_evento_non_supportato(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_EVENTO_NON_SUPPORTATO,
            "SISTEMA_EVENTO_NON_SUPPORTATO",
        )

    def test_sistema_evento_non_supportato_debug(self) -> None:
        self.assertEqual(
            codici_messaggi_sistema.SISTEMA_EVENTO_NON_SUPPORTATO_DEBUG,
            "SISTEMA_EVENTO_NON_SUPPORTATO_DEBUG",
        )

    def test_allineamento_costanti_literal(self) -> None:
        costanti = {
            codici_messaggi_sistema.SISTEMA_ERRORE_CODICE_MANCANTE,
            codici_messaggi_sistema.SISTEMA_ERRORE_MESSAGGIO_NON_DISPONIBILE,
            codici_messaggi_sistema.SISTEMA_ERRORE_CODICE_NON_MAPPATO_DEBUG,
            codici_messaggi_sistema.SISTEMA_SELEZIONE_AUTOMATICA_EFFETTUATA,
            codici_messaggi_sistema.SISTEMA_TIPO_FOCUS_NON_PREVISTO_DEBUG,
            codici_messaggi_sistema.SISTEMA_TEMPLATE_EVENTO_MANCANTE_DEBUG,
            codici_messaggi_sistema.SISTEMA_PLACEHOLDER_TEMPLATE_MANCANTE_DEBUG,
            codici_messaggi_sistema.SISTEMA_FOCUS_CARTELLA_IMPOSTATO,
            codici_messaggi_sistema.SISTEMA_FOCUS_RESET_RIGA_COLONNA,
            codici_messaggi_sistema.SISTEMA_TURNO_PASSATO,
            codici_messaggi_sistema.SISTEMA_RECLAMO_ASSOCIATO_TOMBOLA,
            codici_messaggi_sistema.SISTEMA_RECLAMO_ASSOCIATO_RIGA,
            codici_messaggi_sistema.SISTEMA_RECLAMO_ASSOCIATO_RIGA_NON_DISPONIBILE,
            codici_messaggi_sistema.SISTEMA_RECLAMO_INVIATO,
            codici_messaggi_sistema.SISTEMA_RIFERIMENTO_TOMBOLA,
            codici_messaggi_sistema.SISTEMA_RIFERIMENTO_RIGA,
            codici_messaggi_sistema.SISTEMA_RIFERIMENTO_RIGA_NON_DISPONIBILE,
            codici_messaggi_sistema.SISTEMA_ESITO_RECLAMO,
            codici_messaggi_sistema.SISTEMA_ESITO_RECLAMO_MOTIVO,
            codici_messaggi_sistema.SISTEMA_ESITO_RECLAMO_TURNO,
            codici_messaggi_sistema.SISTEMA_ESITO_RECLAMO_NUMERO_ESTRATTO,
            codici_messaggi_sistema.SISTEMA_EVENTO_NON_SUPPORTATO,
            codici_messaggi_sistema.SISTEMA_EVENTO_NON_SUPPORTATO_DEBUG,
        }
        literal_vals = set(get_args(codici_messaggi_sistema.Codici_Messaggi_Sistema))
        self.assertEqual(costanti, literal_vals)


# ---------------------------------------------------------------------------
# 7. codici_output_ui_umani
# ---------------------------------------------------------------------------

class TestCodiciOutputUiUmani(unittest.TestCase):
    """Contratto del modulo bingo_game.events.codici_output_ui_umani."""

    _CHIAVI_ATTESE: frozenset[str] = frozenset({
        "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_1",
        "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_NESSUNO",
        "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_LISTA",
        "UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MINIMO",
        "UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MASSIMO",
        "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO",
        "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO",
        "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO",
        "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO",
        "UMANI_CARTELLA_SEMPLICE_INTESTAZIONE",
        "UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA",
        "UMANI_CARTELLA_SEMPLICE_PREFISSO_COLONNA",
        "UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA",
        "UMANI_CARTELLA_AVANZATA_INTESTAZIONE",
        "UMANI_RIGA_AVANZATA_INTESTAZIONE",
        "UMANI_COLONNA_AVANZATA_INTESTAZIONE",
        "UMANI_CARTELLA_AVANZATA_ETICHETTA_SEGNATI_RIGA",
        "UMANI_COLONNA_AVANZATA_ETICHETTA_SEGNATI",
        "UMANI_CARTELLA_AVANZATA_SEGNATI_RIGA_NESSUNO",
        "UMANI_COLONNA_AVANZATA_SEGNATI_NESSUNO",
        "UMANI_CARTELLA_AVANZATA_FOOTER_RIEPILOGO",
        "UMANI_COLONNA_AVANZATA_FOOTER_RIEPILOGO",
        "UMANI_SEGNAZIONE_NUMERO_SEGNATO",
        "UMANI_SEGNAZIONE_NUMERO_GIA_SEGNATO",
        "UMANI_SEGNAZIONE_NUMERO_NON_PRESENTE",
        "UMANI_SEGNAZIONE_NUMERO_NON_ESTRATTO",
        "UMANI_RICERCA_NUMERO_INTESTAZIONE",
        "UMANI_RICERCA_NUMERO_NON_TROVATO",
        "UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_SINGOLARE",
        "UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_PLURALE",
        "UMANI_RICERCA_NUMERO_RISULTATO_RIGA",
        "UMANI_RICERCA_NUMERO_STATO_SEGNATO",
        "UMANI_RICERCA_NUMERO_STATO_DA_SEGNARE",
        "UMANI_VERIFICA_NUMERO_ESTRATTO_SI",
        "UMANI_VERIFICA_NUMERO_ESTRATTO_NO",
        "UMANI_ULTIMO_NUMERO_ESTRATTO_PRESENTE",
        "UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO",
        "UMANI_ULTIMI_NUMERI_ESTRATTI_PRESENTI",
        "UMANI_ULTIMI_NUMERI_ESTRATTI_NESSUNO",
        "UMANI_RIEPILOGO_TABELLONE_RIGA_1",
        "UMANI_LISTA_NUMERI_ESTRATTI_INTESTAZIONE",
        "UMANI_LISTA_NUMERI_ESTRATTI_DECINA_LISTA",
        "UMANI_STATO_FOCUS_CORRENTE_CARTELLA_PRESENTE",
        "UMANI_STATO_FOCUS_CORRENTE_CARTELLA_NESSUNA",
        "UMANI_STATO_FOCUS_CORRENTE_RIGA_PRESENTE",
        "UMANI_STATO_FOCUS_CORRENTE_RIGA_NESSUNA",
        "UMANI_STATO_FOCUS_CORRENTE_COLONNA_PRESENTE",
        "UMANI_STATO_FOCUS_CORRENTE_COLONNA_NESSUNA",
        "UMANI_RECLAMO_VITTORIA_TOMBOLA_REGISTRATO",
        "UMANI_RECLAMO_VITTORIA_RIGA_REGISTRATO",
        "UMANI_RECLAMO_VITTORIA_NOTA_VALIDAZIONE",
        "UMANI_FINE_TURNO_PASSATO",
        "UMANI_FINE_TURNO_PASSATO_CON_RECLAMO",
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
    })

    def test_importazione_modulo(self) -> None:
        import bingo_game.events.codici_output_ui_umani as m
        self.assertIsNotNone(m)

    def test_contenuto_literal_uguale_atteso(self) -> None:
        dichiarate = set(get_args(codici_output_ui_umani.Codici_Output_Ui_Umani))
        self.assertEqual(dichiarate, self._CHIAVI_ATTESE)

    def test_nessun_duplicato(self) -> None:
        sequenza = get_args(codici_output_ui_umani.Codici_Output_Ui_Umani)
        self.assertEqual(len(sequenza), len(set(sequenza)))


if __name__ == "__main__":
    unittest.main()
