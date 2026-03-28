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
    partita_terminata
)
from bingo_game.partita import Partita


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
    Classe per comandi specifici del giocatore umano.

    QUESTA CLASSE SARÀ IMPLEMENTATA NELLE PROSSIME SESSIONI
    quando avremo i metodi specifici in GiocatoreUmano.

    Per ora placeholder per futura espansione.
    """

    def __init__(self, partita: Partita):
        self.partita = partita
        # Troverà automaticamente il giocatore umano tra i giocatori
        pass

    def controlla_numero(self, numero: int) -> Dict[str, Any]:
        """Controlla se umano ha numero nelle sue cartelle."""
        pass

    def segna_numero(self, cartella_idx: int, riga: int, col: int, numero: int) -> bool:
        """Segna numero manualmente su cartella specifica."""
        pass

    def mostra_cartelle(self) -> str:
        """Mostra tutte le cartelle del giocatore umano."""
        pass

    def mostra_premi(self) -> str:
        """Mostra premi conseguiti dal giocatore umano."""
        pass
