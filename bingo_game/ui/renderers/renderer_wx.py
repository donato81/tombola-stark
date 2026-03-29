"""
Renderer wxPython per il layer di presentazione accessibile.

Implementa BaseRenderer usando dependency injection per wx.Frame e Vocalizzatore.
Non crea la finestra ne' il backend AO2: li riceve dall'esterno.

Struttura handler:
- Ogni _handle_* costruisce testo, aggiorna widget (_wx_*), poi vocalizza (_ao2_*).
- Gli handler sono stub strutturali in questo ciclo; la logica widget
  verra' completata nel ciclo di sviluppo successivo.

path: bingo_game/ui/renderers/renderer_wx.py
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import wx

from my_lib.vocalizzatore import Vocalizzatore
from bingo_game.events.codici_messaggi_sistema import SISTEMA_ERRORE_CODICE_MANCANTE
from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.eventi_output_ui_umani import (
    EventoLimiteNavigazioneCartelle,
    EventoListaNumeriEstratti,
    EventoNavigazioneColonna,
    EventoNavigazioneColonnaAvanzata,
    EventoNavigazioneRiga,
    EventoNavigazioneRigaAvanzata,
    EventoRicercaNumeroInCartelle,
    EventoRiepilogoCartellaCorrente,
    EventoRiepilogoTabellone,
    EventoSegnazioneNumero,
    EventoStatoFocusCorrente,
    EventoUltimiNumeriEstratti,
    EventoUltimoNumeroEstratto,
    EventoVaiAColonnaAvanzata,
    EventoVaiARigaAvanzata,
    EventoVerificaNumeroEstratto,
    EventoVisualizzaCartellaAvanzata,
    EventoVisualizzaCartellaSemplice,
    EventoVisualizzaTutteCartelleAvanzata,
    EventoVisualizzaTutteCartelleSemplice,
)
from bingo_game.events.eventi_partita import (
    EventoEsitoReclamoVittoria,
    EventoFineTurno,
    EventoReclamoVittoria,
)
from bingo_game.events.eventi_ui import (
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
)
from bingo_game.ui.renderers.base_renderer import BaseRenderer, StatoConfigurazione

_ui_logger = logging.getLogger("ui")
_error_logger = logging.getLogger("error")


class WxRenderer(BaseRenderer):
    """
    Renderer concreto per interfaccia wxPython accessibile.

    Riceve wx.Frame e Vocalizzatore tramite dependency injection.
    Non crea la finestra ne' il backend AO2: li riceve dall'esterno.

    Struttura dispatcher:
    - Ogni famiglia evento ha un handler dedicato senza duplicazioni.
    - Famiglie: focus/navigazione, visualizzazione cartelle, navigazione
      riga, navigazione colonna, segnazione/ricerca, tabellone, flusso partita.

    Sincronizzazione visivo/voce:
    - Ogni handler chiama prima _wx_* (widget) poi _ao2_* (voce) con lo stesso testo.
    """

    def __init__(
        self,
        finestra_principale: wx.Frame,
        vocalizzatore: Vocalizzatore,
    ) -> None:
        self._finestra: wx.Frame = finestra_principale
        self._vocalizzatore: Vocalizzatore = vocalizzatore

    # ---------------------------------------------------------------
    # Metodi pubblici — contratto BaseRenderer
    # ---------------------------------------------------------------

    def render_esito(self, esito: EsitoAzione) -> None:
        """
        Renderizza il risultato di un'azione del controller.

        Casi:
        1. esito.ok=False -> _handle_errore (visualizza e vocalizza l'errore)
        2. esito.ok=True, evento=None -> successo silenzioso, nessuna azione
        3. esito.ok=True, evento valorizzato -> _dispatch_evento
        """
        if not esito.ok:
            self._handle_errore(esito)
            return
        if esito.evento is None:
            return
        self._dispatch_evento(esito.evento)

    def mostra_schermata_configurazione(self, stato: StatoConfigurazione) -> None:
        testo = self._formatta_testo_da_catalogo(stato.codice_messaggio)
        self._wx_mostra_configurazione(stato)
        self._ao2_vocalizza(testo)

    def mostra_report_finale(self, dati_partita: dict[str, Any]) -> None:
        """
        Presenta il riepilogo finale della partita.

        Chiavi attese: turni_giocati, stato_partita, numeri_estratti,
        premi_gia_assegnati, giocatori.
        Chiavi consigliate: conteggio_estratti, conteggio_premi,
        conteggio_giocatori, vincitore_tombola.

        TODO: refactoring futuro verso DatiReportFinale tipizzata.
        """
        self._wx_mostra_report_finale(dati_partita)
        testo = self._formatta_testo_da_catalogo(SISTEMA_ERRORE_CODICE_MANCANTE)
        self._ao2_vocalizza(testo)

    def mostra_messaggio_sistema(self, testo: str) -> None:
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    # ---------------------------------------------------------------
    # Dispatcher centrale
    # ---------------------------------------------------------------

    def _dispatch_evento(self, evento: object) -> None:
        """
        Smista l'evento al handler corretto in base al tipo.

        Ordine: focus/navigazione, cartelle, righe, colonne,
        segnazione/ricerca, tabellone, flusso partita.
        Ogni tipo evento ha un solo handler di destinazione.
        """
        # Famiglia: focus e navigazione
        if isinstance(evento, EventoFocusAutoImpostato):
            self._handle_focus_auto_impostato(evento)
        elif isinstance(evento, EventoFocusCartellaImpostato):
            self._handle_focus_cartella_impostato(evento)
        elif isinstance(evento, EventoStatoFocusCorrente):
            self._handle_stato_focus_corrente(evento)

        # Famiglia: visualizzazione cartelle
        elif isinstance(evento, EventoRiepilogoCartellaCorrente):
            self._handle_riepilogo_cartella_corrente(evento)
        elif isinstance(evento, EventoLimiteNavigazioneCartelle):
            self._handle_limite_navigazione_cartelle(evento)
        elif isinstance(evento, EventoVisualizzaCartellaSemplice):
            self._handle_visualizza_cartella_semplice(evento)
        elif isinstance(evento, EventoVisualizzaCartellaAvanzata):
            self._handle_visualizza_cartella_avanzata(evento)
        elif isinstance(evento, EventoVisualizzaTutteCartelleSemplice):
            self._handle_visualizza_tutte_cartelle_semplice(evento)
        elif isinstance(evento, EventoVisualizzaTutteCartelleAvanzata):
            self._handle_visualizza_tutte_cartelle_avanzata(evento)

        # Famiglia: navigazione riga
        elif isinstance(evento, EventoNavigazioneRiga):
            self._handle_navigazione_riga(evento)
        elif isinstance(evento, EventoNavigazioneRigaAvanzata):
            self._handle_navigazione_riga_avanzata(evento)
        elif isinstance(evento, EventoVaiARigaAvanzata):
            self._handle_vai_a_riga_avanzata(evento)

        # Famiglia: navigazione colonna
        elif isinstance(evento, EventoNavigazioneColonna):
            self._handle_navigazione_colonna(evento)
        elif isinstance(evento, EventoNavigazioneColonnaAvanzata):
            self._handle_navigazione_colonna_avanzata(evento)
        elif isinstance(evento, EventoVaiAColonnaAvanzata):
            self._handle_vai_a_colonna_avanzata(evento)

        # Famiglia: segnazione e ricerca
        elif isinstance(evento, EventoSegnazioneNumero):
            self._handle_segnazione_numero(evento)
        elif isinstance(evento, EventoRicercaNumeroInCartelle):
            self._handle_ricerca_numero_in_cartelle(evento)

        # Famiglia: tabellone
        elif isinstance(evento, EventoVerificaNumeroEstratto):
            self._handle_verifica_numero_estratto(evento)
        elif isinstance(evento, EventoUltimoNumeroEstratto):
            self._handle_ultimo_numero_estratto(evento)
        elif isinstance(evento, EventoUltimiNumeriEstratti):
            self._handle_ultimi_numeri_estratti(evento)
        elif isinstance(evento, EventoRiepilogoTabellone):
            self._handle_riepilogo_tabellone(evento)
        elif isinstance(evento, EventoListaNumeriEstratti):
            self._handle_lista_numeri_estratti(evento)

        # Famiglia: flusso partita
        elif isinstance(evento, EventoReclamoVittoria):
            self._handle_reclamo_vittoria(evento)
        elif isinstance(evento, EventoEsitoReclamoVittoria):
            self._handle_esito_reclamo_vittoria(evento)
        elif isinstance(evento, EventoFineTurno):
            self._handle_fine_turno(evento)

        else:
            self._handle_evento_sconosciuto(evento)

    # ---------------------------------------------------------------
    # Handler: gestione errore
    # ---------------------------------------------------------------

    def _handle_errore(self, esito: EsitoAzione) -> None:
        if esito.errore is not None:
            testo = self._formatta_testo_da_catalogo(str(esito.errore))
        else:
            testo = self._formatta_testo_da_catalogo(SISTEMA_ERRORE_CODICE_MANCANTE)
        _error_logger.debug("render errore: %s", esito.errore)
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    # ---------------------------------------------------------------
    # Handler famiglia: focus e navigazione
    # ---------------------------------------------------------------

    def _handle_focus_auto_impostato(self, evento: EventoFocusAutoImpostato) -> None:
        # TODO: costruire testo da catalogo e aggiornare widget focus
        pass

    def _handle_focus_cartella_impostato(self, evento: EventoFocusCartellaImpostato) -> None:
        # TODO: evidenziare cartella attiva nel pannello e vocalizzare
        pass

    def _handle_stato_focus_corrente(self, evento: EventoStatoFocusCorrente) -> None:
        # TODO: mostrare riepilogo focus corrente (cartella/riga/colonna)
        pass

    # ---------------------------------------------------------------
    # Handler famiglia: visualizzazione cartelle
    # ---------------------------------------------------------------

    def _handle_riepilogo_cartella_corrente(self, evento: EventoRiepilogoCartellaCorrente) -> None:
        # TODO: aggiornare StatBar o panel riepilogo con dati sintetici cartella
        pass

    def _handle_limite_navigazione_cartelle(self, evento: EventoLimiteNavigazioneCartelle) -> None:
        # TODO: vocalizzare "prima/ultima cartella" senza aggiornare widget di griglia
        pass

    def _handle_visualizza_cartella_semplice(self, evento: EventoVisualizzaCartellaSemplice) -> None:
        # TODO: aggiornare pannello cartella con griglia in modalita' semplice
        pass

    def _handle_visualizza_cartella_avanzata(self, evento: EventoVisualizzaCartellaAvanzata) -> None:
        # TODO: aggiornare pannello cartella con griglia avanzata (celle segnate evidenziate)
        pass

    def _handle_visualizza_tutte_cartelle_semplice(
        self, evento: EventoVisualizzaTutteCartelleSemplice
    ) -> None:
        # TODO: aggiornare tutti i pannelli cartelle in modalita' semplice
        pass

    def _handle_visualizza_tutte_cartelle_avanzata(
        self, evento: EventoVisualizzaTutteCartelleAvanzata
    ) -> None:
        # TODO: aggiornare tutti i pannelli cartelle in modalita' avanzata
        pass

    # ---------------------------------------------------------------
    # Handler famiglia: navigazione riga
    # ---------------------------------------------------------------

    def _handle_navigazione_riga(self, evento: EventoNavigazioneRiga) -> None:
        # TODO: aggiornare evidenziazione riga selezionata e vocalizzare contenuto
        pass

    def _handle_navigazione_riga_avanzata(self, evento: EventoNavigazioneRigaAvanzata) -> None:
        # TODO: evidenziare riga avanzata e vocalizzare con indicatori segnati
        pass

    def _handle_vai_a_riga_avanzata(self, evento: EventoVaiARigaAvanzata) -> None:
        # TODO: selezionare riga diretta e vocalizzare
        pass

    # ---------------------------------------------------------------
    # Handler famiglia: navigazione colonna
    # ---------------------------------------------------------------

    def _handle_navigazione_colonna(self, evento: EventoNavigazioneColonna) -> None:
        # TODO: aggiornare evidenziazione colonna selezionata e vocalizzare
        pass

    def _handle_navigazione_colonna_avanzata(self, evento: EventoNavigazioneColonnaAvanzata) -> None:
        # TODO: evidenziare colonna avanzata e vocalizzare con indicatori
        pass

    def _handle_vai_a_colonna_avanzata(self, evento: EventoVaiAColonnaAvanzata) -> None:
        # TODO: selezionare colonna diretta e vocalizzare
        pass

    # ---------------------------------------------------------------
    # Handler famiglia: segnazione e ricerca
    # ---------------------------------------------------------------

    def _handle_segnazione_numero(self, evento: EventoSegnazioneNumero) -> None:
        # TODO: aggiornare cella nella griglia (marcata/non marcata) e vocalizzare esito
        pass

    def _handle_ricerca_numero_in_cartelle(self, evento: EventoRicercaNumeroInCartelle) -> None:
        # TODO: mostrare pannello risultato ricerca e vocalizzare riassunto
        pass

    # ---------------------------------------------------------------
    # Handler famiglia: tabellone
    # ---------------------------------------------------------------

    def _handle_verifica_numero_estratto(self, evento: EventoVerificaNumeroEstratto) -> None:
        # TODO: aggiornare tabellone e vocalizzare stato estrazione del numero
        pass

    def _handle_ultimo_numero_estratto(self, evento: EventoUltimoNumeroEstratto) -> None:
        # TODO: evidenziare ultimo numero nel tabellone e vocalizzare
        pass

    def _handle_ultimi_numeri_estratti(self, evento: EventoUltimiNumeriEstratti) -> None:
        # TODO: mostrare lista breve degli ultimi estratti e vocalizzare
        pass

    def _handle_riepilogo_tabellone(self, evento: EventoRiepilogoTabellone) -> None:
        # TODO: aggiornare pannello tabellone con sintesi globale, ultimi estratti, ultimo
        pass

    def _handle_lista_numeri_estratti(self, evento: EventoListaNumeriEstratti) -> None:
        # TODO: aggiornare pannello lista completa estratti per decine e vocalizzare
        pass

    # ---------------------------------------------------------------
    # Handler famiglia: flusso partita
    # ---------------------------------------------------------------

    def _handle_reclamo_vittoria(self, evento: EventoReclamoVittoria) -> None:
        # TODO: mostrare conferma registrazione reclamo e nota sulla validazione a fine turno
        pass

    def _handle_esito_reclamo_vittoria(self, evento: EventoEsitoReclamoVittoria) -> None:
        # TODO: mostrare esito reclamo (accettato/rifiutato) con dettagli cartella/riga
        pass

    def _handle_fine_turno(self, evento: EventoFineTurno) -> None:
        # TODO: aggiornare stato partita e vocalizzare conferma fine turno
        pass

    def _handle_evento_sconosciuto(self, evento: object) -> None:
        testo = self._formatta_testo_da_catalogo(SISTEMA_ERRORE_CODICE_MANCANTE)
        _error_logger.warning(
            "Evento sconosciuto non gestito dal dispatcher: %s",
            type(evento).__name__,
        )
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    # ---------------------------------------------------------------
    # Layer widget (_wx_*)
    # ---------------------------------------------------------------

    def _wx_aggiorna_output(self, testo: str) -> None:
        # TODO: aggiornare widget output principale (es. TextCtrl di log)
        pass

    def _wx_aggiorna_cartella(self, numero_cartella: int, righe: list[str]) -> None:
        # TODO: aggiornare le celle del pannello cartella specificato
        pass

    def _wx_aggiorna_tabellone(self, numeri_estratti: list[int]) -> None:
        # TODO: aggiornare il pannello tabellone con i numeri estratti correnti
        pass

    def _wx_mostra_configurazione(self, stato: StatoConfigurazione) -> None:
        # TODO: mostrare pannello configurazione per la fase corrente
        pass

    def _wx_mostra_report_finale(self, dati_partita: dict[str, Any]) -> None:
        # TODO: popolare pannello riepilogo finale con i dati della partita
        pass

    # ---------------------------------------------------------------
    # Layer voce (_ao2_*)
    # ---------------------------------------------------------------

    def _ao2_vocalizza(self, testo: str) -> None:
        self._vocalizzatore.vocalizza_testo(testo)

    # ---------------------------------------------------------------
    # Helper puri
    # ---------------------------------------------------------------

    @staticmethod
    def _indice_umano(indice_zero_based: int) -> int:
        """Converte indice interno 0-based in numero 1-based per la UI."""
        return indice_zero_based + 1

    @staticmethod
    def _raggruppa_numeri_per_decine(
        numeri: list[int],
    ) -> dict[tuple[int, int], list[int]]:
        """
        Raggruppa i numeri estratti per fasce di decine.

        Fasce: (1,9), (10,19), (20,29), (30,39), (40,49),
               (50,59), (60,69), (70,79), (80,90).
        Restituisce solo le fasce non vuote.
        """
        fasce: list[tuple[int, int]] = [
            (1, 9),
            (10, 19),
            (20, 29),
            (30, 39),
            (40, 49),
            (50, 59),
            (60, 69),
            (70, 79),
            (80, 90),
        ]
        result: dict[tuple[int, int], list[int]] = {}
        for fascia in fasce:
            minimo, massimo = fascia
            gruppo = [n for n in numeri if minimo <= n <= massimo]
            if gruppo:
                result[fascia] = gruppo
        return result

    @staticmethod
    def _segnati_set(numeri_segnati: list[int]) -> set[int]:
        """
        Converte la lista dei numeri segnati in set per lookup O(1).

        Utile nei renderer avanzati per determinare velocemente se una cella
        e' gia' segnata senza iterare la lista intera.
        """
        return set(numeri_segnati)
