"""
Comandi per la gestione della partita di tombola
===============================================

Modulo: bingo_game.comandi_partita

Questo modulo definisce due classi principali per gestire tutti i comandi
dell'interfaccia, separando chiaramente le responsabilità:

1. ComandiSistema: gestione globale della partita (creazione, avvio, turni)
2. ComandiGiocatoreUmano: comandi personali del giocatore umano (cartelle, segni)

Ogni classe espone metodi pubblici semplici che l'interfaccia può chiamare
senza conoscere i dettagli interni del game_controller o della Partita.
"""

from __future__ import annotations
from typing import Optional, Dict, Any
from bingo_game.game_controller import (
    crea_partita_standard,
    avvia_partita_sicura,
    esegui_turno_sicuro,
    ottieni_stato_sintetico,
    ha_partita_tombola,
    partita_terminata,
    ottieni_giocatore_umano,
)
from bingo_game.partita import Partita
from bingo_game.players.giocatore_umano import GiocatoreUmano
from bingo_game.events.eventi import EsitoAzione


class ComandiSistema:
    """
    Classe che gestisce i comandi di sistema per la partita.

    Questa classe incapsula tutte le operazioni globali che riguardano
    la partita nel suo insieme: creazione, avvio, esecuzione turni,
    controllo stato, terminazione.

    Ogni metodo è progettato per essere chiamato direttamente dall'interfaccia
    (terminale, screen reader, GUI) senza conoscere i dettagli del game_controller.

    STRUTTURA METODI:
    - Input semplici (stringhe, interi)
    - Output chiari (Partita, bool, dict, messaggi di stato)
    - Gestione errori interna (no eccezioni verso interfaccia)
    """

    def crea_nuova_partita(
        self, 
        nome_umano: str, 
        num_cartelle_umano: int = 1, 
        num_bot: int = 1
    ) -> Optional[Partita]:
        """
        Crea una nuova partita completa con giocatore umano e bot.

        Parametri:
        - nome_umano: str - Nome del giocatore umano
        - num_cartelle_umano: int - Cartelle per umano (default 1)
        - num_bot: int - Numero bot (default 1, minimo 1, massimo 7)

        Ritorna:
        - Partita: partita pronta se successo
        - None: se parametri invalidi
        """
        try:
            # Delega al game_controller (già validato)
            partita = crea_partita_standard(
                nome_giocatore_umano=nome_umano,
                num_cartelle_umano=num_cartelle_umano,
                num_bot=num_bot
            )
            return partita
            
        except Exception as exc:
            return None

    def avvia_partita(self, partita: Partita) -> bool:
        """
        Avvia la partita (cambia stato da non_iniziata → in_corso).

        Parametri:
        - partita: Partita - Partita da avviare

        Ritorna:
        - True: avviata con successo
        - False: errore (giocatori insufficienti, già avviata)
        """
        if not isinstance(partita, Partita):
            return False
        
        successo = avvia_partita_sicura(partita)
        return successo

    def esegui_turno(self, partita: Partita) -> Optional[Dict[str, Any]]:
        """
        Esegue un turno completo: estrae numero, aggiorna bot, verifica premi.

        Parametri:
        - partita: Partita - Partita in corso

        Ritorna:
        - dict: dettagli turno (numero estratto, premi nuovi, tombola?)
        - None: errore (partita non in corso, numeri finiti)
        """
        if not isinstance(partita, Partita):
            return None
        
        risultato = esegui_turno_sicuro(partita)
        return risultato

    def stato_partita(self, partita: Partita) -> Optional[Dict[str, Any]]:
        """
        Ritorna stato completo della partita.

        Parametri:
        - partita: Partita - Partita esistente

        Ritorna:
        - dict: stato completo (numeri estratti, giocatori, premi)
        - None: errore parametro
        """
        if not isinstance(partita, Partita):
            return None
        
        try:
            stato = ottieni_stato_sintetico(partita)
            return stato
        except Exception as exc:
            return None

    def ha_tombola(self, partita: Partita) -> bool:
        """
        Controlla se c'è tombola nella partita.

        Parametri:
        - partita: Partita - Partita esistente

        Ritorna:
        - True: tombola presente
        - False: nessuna tombola
        """
        if not isinstance(partita, Partita):
            return False
        
        tombola = ha_partita_tombola(partita)
        return tombola

    def is_terminata(self, partita: Partita) -> bool:
        """
        Controlla se partita è terminata (condizione uscita loop).

        Parametri:
        - partita: Partita - Partita esistente

        Ritorna:
        - True: partita terminata, ferma loop
        - False: partita continua
        """
        if not isinstance(partita, Partita):
            return False
        
        terminata = partita_terminata(partita)
        return terminata

    def termina_partita(self, partita: Partita) -> bool:
        """
        Termina forzatamente la partita.

        Parametri:
        - partita: Partita - Partita da terminare

        Ritorna:
        - True: terminata con successo
        - False: errore parametro
        """
        if not isinstance(partita, Partita):
            return False
        
        try:
            partita.termina_partita()
            return True
        except Exception as exc:
            return False


class ComandiGiocatoreUmano:
    """
    Facade per i comandi del giocatore umano durante la partita.

    Incapsula l'accesso a GiocatoreUmano in modo che il layer UI
    non interagisca direttamente con il dominio. Ogni metodo delega
    al corrispondente metodo di GiocatoreUmano e restituisce EsitoAzione.
    """

    def __init__(self, partita: Partita) -> None:
        self._partita = partita
        self._giocatore: Optional[GiocatoreUmano] = ottieni_giocatore_umano(partita)
        # Traccia l'ultimo tipo di navigazione ("riga" o "colonna") per il tasto A.
        self._tipo_navigazione_corrente: str = "riga"

    def _esito_nessun_giocatore(self) -> EsitoAzione:
        return EsitoAzione.fallimento(errore="CARTELLE_NESSUNA_ASSEGNATA")

    # ------------------------------------------------------------------
    # Focus cartella
    # ------------------------------------------------------------------

    def imposta_focus_cartella(self, numero: int) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.imposta_focus_cartella(numero)

    # ------------------------------------------------------------------
    # Navigazione cartelle
    # ------------------------------------------------------------------

    def cartella_precedente(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.riepilogo_cartella_precedente()

    def cartella_successiva(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.riepilogo_cartella_successiva()

    def riepilogo_cartella_corrente(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.riepilogo_cartella_corrente()

    # ------------------------------------------------------------------
    # Visualizzazione cartella
    # ------------------------------------------------------------------

    def visualizza_semplice(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.visualizza_cartella_corrente_semplice()

    def visualizza_avanzata(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.visualizza_cartella_corrente_avanzata()

    def visualizza_tutte_semplice(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.visualizza_tutte_cartelle_semplice()

    def visualizza_tutte_avanzate(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.visualizza_tutte_cartelle_avanzata()

    # ------------------------------------------------------------------
    # Navigazione riga
    # ------------------------------------------------------------------

    def riga_su(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        self._tipo_navigazione_corrente = "riga"
        return self._giocatore.sposta_focus_riga_su_semplice()

    def riga_giu(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        self._tipo_navigazione_corrente = "riga"
        return self._giocatore.sposta_focus_riga_giu_semplice()

    def riga_su_avanzata(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.sposta_focus_riga_su_avanzata()

    def riga_giu_avanzata(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.sposta_focus_riga_giu_avanzata()

    def vai_a_riga(self, numero_riga: int) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.vai_a_riga_avanzata(numero_riga)

    # ------------------------------------------------------------------
    # Navigazione colonna
    # ------------------------------------------------------------------

    def colonna_sinistra(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        self._tipo_navigazione_corrente = "colonna"
        return self._giocatore.sposta_focus_colonna_sinistra()

    def colonna_destra(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        self._tipo_navigazione_corrente = "colonna"
        return self._giocatore.sposta_focus_colonna_destra()

    def colonna_sinistra_avanzata(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.sposta_focus_colonna_sinistra_avanzata()

    def colonna_destra_avanzata(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.sposta_focus_colonna_destra_avanzata()

    def vai_a_colonna(self, numero_colonna: int) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.vai_a_colonna_avanzata(numero_colonna)

    # ------------------------------------------------------------------
    # Segnazione e ricerca
    # ------------------------------------------------------------------

    def segna_numero(self, numero: int) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.segna_numero_manuale(numero, self._partita.tabellone)

    def cerca_numero(self, numero: int) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.cerca_numero_nelle_cartelle(numero)

    # ------------------------------------------------------------------
    # Consultazione tabellone
    # ------------------------------------------------------------------

    def ultimo_numero_estratto(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.comunica_ultimo_numero_estratto(self._partita.tabellone)

    def ultimi_numeri_estratti(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.visualizza_ultimi_numeri_estratti(self._partita.tabellone)

    def riepilogo_tabellone(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.riepilogo_tabellone(self._partita.tabellone)

    def lista_numeri_estratti(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.lista_numeri_estratti(self._partita.tabellone)

    def stato_focus(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.stato_focus_corrente()

    # ------------------------------------------------------------------
    # Vittoria
    # ------------------------------------------------------------------

    def leggi_posizione_avanzata(self) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        if self._tipo_navigazione_corrente == "colonna":
            return self._giocatore.leggi_colonna_avanzata()
        return self._giocatore.leggi_riga_avanzata()

    def annuncia_vittoria(self, tipo: str, numero_turno: int) -> EsitoAzione:
        if self._giocatore is None:
            return self._esito_nessun_giocatore()
        return self._giocatore.annuncia_vittoria(tipo, numero_turno)
