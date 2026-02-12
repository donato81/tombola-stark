from __future__ import annotations

from bingo_game.events.eventi import EsitoAzione
from bingo_game.tabellone import Tabellone


def esito_tabellone_disponibile(tabellone: object) -> EsitoAzione:
    """
    Verifica che l'oggetto tabellone sia disponibile e coerente per le azioni di partita.

    Scopo:
    - Rendere robusti i metodi del giocatore (es. segna numero) quando ricevono oggetti
      dall'esterno (Partita / GameController).
    - Evitare eccezioni e stringhe libere nel dominio: in caso di problema, ritorna
      un EsitoAzione con un codice errore standardizzato.

    Parametri:
    - tabellone (object): l'oggetto tabellone passato al metodo chiamante.

    Ritorna:
    - EsitoAzione(ok=True) se tabellone è presente ed è un'istanza di Tabellone.
    - EsitoAzione(ok=False, errore="TABELLONE_NON_DISPONIBILE") altrimenti.
    """

    # Caso 1: tabellone non passato (None).
    if tabellone is None:
        return EsitoAzione(
            ok=False,
            errore="TABELLONE_NON_DISPONIBILE",
            evento=None
        )

    # Caso 2: tabellone passato ma di tipo errato (incoerenza di integrazione).
    if not isinstance(tabellone, Tabellone):
        return EsitoAzione(
            ok=False,
            errore="TABELLONE_NON_DISPONIBILE",
            evento=None
        )

    return EsitoAzione(
        ok=True,
        errore=None,
        evento=None
    )


def esito_coordinate_numero_coerenti(cartella, numero: int) -> EsitoAzione:
    """
    Validazione difensiva: verifica che la cartella sia in uno stato coerente
    rispetto alla localizzazione di un numero nella griglia.

    Quando usarlo:
    - Dopo aver già stabilito che "numero" è presente nella cartella (es. tramite get_numeri_cartella()).
    - Prima di produrre un evento che richiede coordinate (riga/colonna) o prima di eseguire
      un'azione che assume l'esistenza di quelle coordinate.

    Perché serve:
    - In una cartella ben formata, se un numero risulta "presente", allora deve anche esistere
      una coppia di coordinate (riga, colonna) nella griglia 3x9.
    - Se get_coordinate_numero(numero) restituisce None, significa che i dati interni
      della cartella sono incoerenti (caso raro, ma possibile per bug o dati corrotti).

    Contratto di ritorno (stile progetto):
    - Se lo stato è coerente: ritorna EsitoAzione(ok=True) senza evento (evento=None).
    - Se lo stato è incoerente: ritorna EsitoAzione(ok=False) con errore "CARTELLA_STATO_INCOERENTE".
    """
    # 1) Validazione minima del tipo numero:
    #    questa funzione è pensata per un numero "già validato", ma restiamo robusti.
    if type(numero) is not int:
        return EsitoAzione(
            ok=False,
            errore="INPUTNONVALIDO",  # codice già presente nei tuoi errori UI
            evento=None
        )

    # 2) Prova a ricavare le coordinate dal metodo ufficiale della cartella.
    #    Se torna None, la cartella è in stato incoerente (dato presente ma non localizzabile).
    coordinate = cartella.get_coordinate_numero(numero)
    if coordinate is None:
        return EsitoAzione(
            ok=False,
            errore="CARTELLA_STATO_INCOERENTE",
            evento=None
        )

    # 3) Caso normale: tutto coerente.
    #    Non ritorniamo coordinate per scelta di design (evitiamo verbosità e payload non necessario).
    return EsitoAzione(
        ok=True,
        errore=None,
        evento=None
    )
