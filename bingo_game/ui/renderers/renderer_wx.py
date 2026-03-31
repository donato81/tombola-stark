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
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    import wx

from my_lib.vocalizzatore import IVocalizzatore
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
        finestra_principale: "wx.Frame",
        vocalizzatore: IVocalizzatore,
    ) -> None:
        self._finestra: Any = finestra_principale
        self._vocalizzatore: IVocalizzatore = vocalizzatore
        # Stato locale
        self._ultimo_annuncio: str = ""
        self._log_text_ctrl: Optional[Any] = None
        self.numero_in_focus: Optional[int] = None

    # ---------------------------------------------------------------
    # Metodi pubblici — contratto BaseRenderer
    # ---------------------------------------------------------------

    def aggiorna_finestra(self, nuova_finestra: Any) -> None:
        """Aggiorna il riferimento al frame corrente dopo una transizione."""
        self._finestra = nuova_finestra

    def imposta_widget_log(self, ctrl: Any) -> None:
        """Imposta il widget TextCtrl del log annunci per la finestra corrente."""
        self._log_text_ctrl = ctrl

    def ripeti_ultimo_annuncio(self) -> None:
        """Vocalizza nuovamente l'ultimo testo annunciato (F6)."""
        if self._ultimo_annuncio:
            self._vocalizzatore.vocalizza_testo(self._ultimo_annuncio, interrompi=True)
        else:
            self._vocalizzatore.vocalizza_testo("Nessun annuncio precedente.", interrompi=True)

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
        testo = self._formatta_testo_da_catalogo(
            "EVENTO_FOCUS_AUTO_IMPOSTATO",
            tipo=evento.tipo_focus,
            numero=evento.indice + 1,
        )
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_focus_cartella_impostato(self, evento: EventoFocusCartellaImpostato) -> None:
        testo = f"Cartella {evento.numero_cartella} selezionata."
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_stato_focus_corrente(self, evento: EventoStatoFocusCorrente) -> None:
        parti = []
        if evento.numero_cartella is not None:
            parti.append(f"Cartella {evento.numero_cartella}")
        if evento.numero_riga is not None:
            parti.append(f"riga {evento.numero_riga}")
        if evento.numero_colonna is not None:
            parti.append(f"colonna {evento.numero_colonna}")
            self.numero_in_focus = evento.numero_colonna
        testo = ", ".join(parti) + "." if parti else "Focus non impostato."
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    # ---------------------------------------------------------------
    # Handler famiglia: visualizzazione cartelle
    # ---------------------------------------------------------------

    def _handle_riepilogo_cartella_corrente(self, evento: EventoRiepilogoCartellaCorrente) -> None:
        testo = self._formatta_testo_da_catalogo(
            "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_1",
            numero_cartella=evento.numero_cartella,
            numeri_segnati=evento.numeri_segnati,
            totale_numeri=evento.totale_numeri,
            mancanti=evento.mancanti,
            percentuale=round(evento.percentuale, 1),
        )
        if evento.numeri_non_segnati:
            lista = ", ".join(str(n) for n in evento.numeri_non_segnati)
            testo2 = self._formatta_testo_da_catalogo(
                "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_LISTA", lista=lista
            )
        else:
            testo2 = self._formatta_testo_da_catalogo(
                "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_NESSUNO"
            )
        testo_completo = f"{testo} {testo2}"
        self._wx_aggiorna_output(testo_completo)
        self._ao2_vocalizza(testo_completo)

    def _handle_limite_navigazione_cartelle(self, evento: EventoLimiteNavigazioneCartelle) -> None:
        if evento.limite == "minimo":
            testo = self._formatta_testo_da_catalogo(
                "UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MINIMO",
                totale_cartelle=evento.totale_cartelle,
            )
        else:
            testo = self._formatta_testo_da_catalogo(
                "UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MASSIMO",
                totale_cartelle=evento.totale_cartelle,
            )
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_visualizza_cartella_semplice(self, evento: EventoVisualizzaCartellaSemplice) -> None:
        righe = []
        for i, riga in enumerate(evento.griglia_semplice):
            celle = "  ".join(str(c).rjust(2) if c != "-" else " -" for c in riga if c != "-" or True)
            righe.append(f"Riga {i+1}: {celle}")
        testo = f"Cartella {evento.numero_cartella}/{evento.totale_cartelle}.\n" + "\n".join(righe)
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_visualizza_cartella_avanzata(self, evento: EventoVisualizzaCartellaAvanzata) -> None:
        righe = []
        segnati_set = set(evento.numeri_segnati_ordinati)
        for i, riga in enumerate(evento.griglia_semplice):
            celle = "  ".join(
                (f"[{c}]" if isinstance(c, int) and c in segnati_set else str(c).rjust(2))
                for c in riga
            )
            righe.append(f"Riga {i+1}: {celle}")
        testo = f"Cartella {evento.numero_cartella}/{evento.totale_cartelle} (avanzata).\n" + "\n".join(righe)
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_visualizza_tutte_cartelle_semplice(
        self, evento: EventoVisualizzaTutteCartelleSemplice
    ) -> None:
        parti = []
        for numero_c, griglia in evento.cartelle:
            parti.append(f"Cartella {numero_c}:")
            for i, riga in enumerate(griglia):
                celle = "  ".join(str(c) for c in riga)
                parti.append(f"  Riga {i+1}: {celle}")
        testo = "\n".join(parti)
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(f"Tutte le {evento.totale_cartelle} cartelle mostrate.")

    def _handle_visualizza_tutte_cartelle_avanzata(
        self, evento: EventoVisualizzaTutteCartelleAvanzata
    ) -> None:
        self._wx_aggiorna_output(f"Tutte le {evento.totale_cartelle} cartelle (avanzata).")
        self._ao2_vocalizza(f"Tutte le {evento.totale_cartelle} cartelle mostrate in modalità avanzata.")

    # ---------------------------------------------------------------
    # Handler famiglia: navigazione riga
    # ---------------------------------------------------------------

    def _handle_navigazione_riga(self, evento: EventoNavigazioneRiga) -> None:
        if evento.esito == "limite":
            codice = ("UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO"
                      if evento.limite == "minimo" else "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO")
            testo = self._formatta_testo_da_catalogo(codice)
        else:
            celle = "  ".join(str(c) for c in (evento.riga_semplice or []))
            testo = f"Riga {evento.numero_riga_corrente}: {celle}"
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_navigazione_riga_avanzata(self, evento: EventoNavigazioneRigaAvanzata) -> None:
        if evento.esito == "limite":
            codice = ("UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO"
                      if evento.limite == "minimo" else "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO")
            testo = self._formatta_testo_da_catalogo(codice)
        else:
            segnati_set = set(evento.numeri_segnati_riga_ordinati or [])
            celle = "  ".join(
                f"[{c}]" if isinstance(c, int) and c in segnati_set else str(c)
                for c in (evento.riga_semplice or [])
            )
            testo = f"Riga {evento.numero_riga_corrente} avanzata: {celle}"
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_vai_a_riga_avanzata(self, evento: EventoVaiARigaAvanzata) -> None:
        if evento.esito == "limite":
            codice = ("UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO"
                      if evento.limite == "minimo" else "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO")
            testo = self._formatta_testo_da_catalogo(codice)
        else:
            celle = "  ".join(str(c) for c in (evento.riga_semplice or []))
            testo = f"Riga {evento.numero_riga_corrente}: {celle}"
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    # ---------------------------------------------------------------
    # Handler famiglia: navigazione colonna
    # ---------------------------------------------------------------

    def _handle_navigazione_colonna(self, evento: EventoNavigazioneColonna) -> None:
        if evento.esito == "limite":
            codice = ("UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO"
                      if evento.limite == "minimo" else "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO")
            testo = self._formatta_testo_da_catalogo(codice)
        else:
            celle = " / ".join(str(c) for c in (evento.colonna_semplice or []))
            testo = f"Colonna {evento.numero_colonna_corrente}: {celle}"
            # Aggiorna il numero in focus per la segnazione (Spazio)
            # Cerca il primo numero valido nelle celle
            for c in (evento.colonna_semplice or []):
                if isinstance(c, int):
                    self.numero_in_focus = c
                    break
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_navigazione_colonna_avanzata(self, evento: EventoNavigazioneColonnaAvanzata) -> None:
        if evento.esito == "limite":
            codice = ("UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO"
                      if evento.limite == "minimo" else "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO")
            testo = self._formatta_testo_da_catalogo(codice)
        else:
            segnati_set = set(evento.numeri_segnati_colonna_ordinati or [])
            celle = " / ".join(
                f"[{c}]" if isinstance(c, int) and c in segnati_set else str(c)
                for c in (evento.colonna_semplice or [])
            )
            testo = f"Colonna {evento.numero_colonna_corrente} avanzata: {celle}"
            for c in (evento.colonna_semplice or []):
                if isinstance(c, int):
                    self.numero_in_focus = c
                    break
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_vai_a_colonna_avanzata(self, evento: EventoVaiAColonnaAvanzata) -> None:
        if evento.esito == "limite":
            codice = ("UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO"
                      if evento.limite == "minimo" else "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO")
            testo = self._formatta_testo_da_catalogo(codice)
        else:
            celle = " / ".join(str(c) for c in (evento.colonna_semplice or []))
            testo = f"Colonna {evento.numero_colonna_corrente}: {celle}"
            for c in (evento.colonna_semplice or []):
                if isinstance(c, int):
                    self.numero_in_focus = c
                    break
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    # ---------------------------------------------------------------
    # Handler famiglia: segnazione e ricerca
    # ---------------------------------------------------------------

    def _handle_segnazione_numero(self, evento: EventoSegnazioneNumero) -> None:
        esito = evento.esito
        if esito == "segnato":
            testo = self._formatta_testo_da_catalogo(
                "UMANI_SEGNAZIONE_NUMERO_SEGNATO",
                numero=evento.numero,
                numero_riga=(evento.indice_riga + 1 if evento.indice_riga is not None else "?"),
                numero_colonna=(evento.indice_colonna + 1 if evento.indice_colonna is not None else "?"),
            )
        elif esito == "gia_segnato":
            testo = self._formatta_testo_da_catalogo(
                "UMANI_SEGNAZIONE_NUMERO_GIA_SEGNATO",
                numero=evento.numero,
                numero_cartella=evento.numero_cartella,
            )
        elif esito == "non_presente":
            testo = self._formatta_testo_da_catalogo(
                "UMANI_SEGNAZIONE_NUMERO_NON_PRESENTE",
                numero=evento.numero,
                numero_cartella=evento.numero_cartella,
            )
        else:  # non_estratto
            testo = self._formatta_testo_da_catalogo(
                "UMANI_SEGNAZIONE_NUMERO_NON_ESTRATTO",
                numero=evento.numero,
            )
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_ricerca_numero_in_cartelle(self, evento: EventoRicercaNumeroInCartelle) -> None:
        if evento.esito == "non_trovato":
            testo = self._formatta_testo_da_catalogo(
                "UMANI_RICERCA_NUMERO_NON_TROVATO", numero=evento.numero
            )
        else:
            parti = [f"Numero {evento.numero} trovato in:"]
            for r in evento.risultati:
                stati = "già segnato" if r.segnato else "non segnato"
                parti.append(
                    f"  Cartella {r.numero_cartella}, riga {r.indice_riga + 1}, colonna {r.indice_colonna + 1} ({stati})."
                )
            testo = "\n".join(parti)
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    # ---------------------------------------------------------------
    # Handler famiglia: tabellone
    # ---------------------------------------------------------------

    def _handle_verifica_numero_estratto(self, evento: EventoVerificaNumeroEstratto) -> None:
        stato = "estratto" if evento.estratto else "NON ancora estratto"
        testo = f"Numero {evento.numero}: {stato}."
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_ultimo_numero_estratto(self, evento: EventoUltimoNumeroEstratto) -> None:
        if evento.ultimo_numero is not None:
            testo = f"Ultimo numero estratto: {evento.ultimo_numero}."
        else:
            testo = "Nessun numero estratto finora."
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_ultimi_numeri_estratti(self, evento: EventoUltimiNumeriEstratti) -> None:
        if evento.visualizzati == 0:
            testo = "Nessun numero estratto finora."
        else:
            lista = ", ".join(str(n) for n in evento.numeri)
            testo = f"Ultimi {evento.visualizzati} estratti: {lista}."
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_riepilogo_tabellone(self, evento: EventoRiepilogoTabellone) -> None:
        testo = (
            f"Tabellone: {evento.totale_estratti} su {evento.totale_numeri} estratti "
            f"({round(evento.percentuale_estrazione, 1)}%)."
        )
        if evento.ultimo_estratto is not None:
            testo += f" Ultimo: {evento.ultimo_estratto}."
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_lista_numeri_estratti(self, evento: EventoListaNumeriEstratti) -> None:
        if evento.totale_estratti == 0:
            testo = "Nessun numero estratto finora."
        else:
            lista = ", ".join(str(n) for n in evento.numeri_estratti)
            testo = f"{evento.totale_estratti} estratti: {lista}."
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    # ---------------------------------------------------------------
    # Handler famiglia: flusso partita
    # ---------------------------------------------------------------

    def _handle_reclamo_vittoria(self, evento: EventoReclamoVittoria) -> None:
        tipo = evento.reclamo.tipo
        testo = (
            f"Reclamo {tipo} registrato per {evento.nome_giocatore}."
            " Sarà validato a fine turno."
        )
        _ui_logger.debug(
            "reclamo vittoria: %s tipo=%s turno=%d",
            evento.nome_giocatore, tipo, evento.numero_turno,
        )
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_esito_reclamo_vittoria(self, evento: EventoEsitoReclamoVittoria) -> None:
        tipo = evento.reclamo.tipo
        if evento.ok:
            testo = (
                f"Vittoria accettata! {tipo.capitalize()}"
                f" confermato per {evento.nome_giocatore}."
            )
        else:
            testo = f"Reclamo {tipo} rifiutato per {evento.nome_giocatore}."
        _ui_logger.debug(
            "esito reclamo: %s ok=%s", evento.nome_giocatore, evento.ok
        )
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)

    def _handle_fine_turno(self, evento: EventoFineTurno) -> None:
        testo = f"Fine turno {evento.numero_turno}."
        if evento.reclamo_turno is not None:
            testo += f" Reclamo {evento.reclamo_turno.tipo} allegato."
        _ui_logger.debug(
            "fine turno: %s turno=%d", evento.nome_giocatore, evento.numero_turno
        )
        self._wx_aggiorna_output(testo)
        self._ao2_vocalizza(testo)
        if hasattr(self._finestra, "aggiorna_stato_pulsante"):
            self._finestra.aggiorna_stato_pulsante(primo_turno_eseguito=True)

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
        """Aggiorna il frame corrente via duck typing (mostra_testo + aggiungi_a_log)."""
        if self._finestra is None:
            return
        if hasattr(self._finestra, "mostra_testo"):
            self._finestra.mostra_testo(testo)  # type: ignore[union-attr]
        if hasattr(self._finestra, "aggiungi_a_log"):
            self._finestra.aggiungi_a_log(testo)  # type: ignore[union-attr]

    def _wx_aggiorna_cartella(self, numero_cartella: int, righe: list[str]) -> None:
        # stub: aggiornamento pannello cartella rimandato al ciclo successivo
        pass

    def _wx_aggiorna_tabellone(self, numeri_estratti: list[int]) -> None:
        # stub: aggiornamento pannello tabellone rimandato al ciclo successivo
        pass

    def _wx_mostra_configurazione(self, stato: StatoConfigurazione) -> None:
        testo = self._formatta_testo_da_catalogo(stato.codice_messaggio)
        if self._finestra is not None and hasattr(self._finestra, "mostra_testo"):
            self._finestra.mostra_testo(testo)  # type: ignore[union-attr]

    def _wx_mostra_report_finale(self, dati_partita: dict[str, Any]) -> None:
        turni = dati_partita.get("turni_giocati", "?")
        testo = f"Partita terminata. Turni giocati: {turni}."
        if self._finestra is not None and hasattr(self._finestra, "mostra_testo"):
            self._finestra.mostra_testo(testo)  # type: ignore[union-attr]

    # ---------------------------------------------------------------
    # Layer voce (_ao2_*)
    # ---------------------------------------------------------------

    def _ao2_vocalizza(self, testo: str) -> None:
        self._ultimo_annuncio = testo
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
