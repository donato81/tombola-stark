from __future__ import annotations

from bingo_game.events.eventi import EsitoAzione
from bingo_game.events.codici_errori import Codici_Errori


def esito_numero_intero(numero: object) -> EsitoAzione:
    """
    Verifica che il valore passato sia un numero intero (int).

    Scopo:
    - Centralizzare la validazione del tipo, riutilizzabile in più punti del progetto.
    - Non produce stringhe e non lancia eccezioni: ritorna EsitoAzione con codice errore.

    Parametri:
    - numero (object): valore da validare (tipicamente input utente già parsato).

    Ritorna:
    - EsitoAzione(ok=True) se numero è un int.
    - EsitoAzione(ok=False, errore="NUMERO_TIPO_NON_VALIDO") altrimenti.
    """

    # Controllo del tipo: deve essere int.
    if type(numero) is not int:
        return EsitoAzione(
            ok=False,
            errore="NUMERO_TIPO_NON_VALIDO",
            evento=None
        )

    return EsitoAzione(
        ok=True,
        errore=None,
        evento=None
    )


def esito_numero_in_range_1_90(numero: object) -> EsitoAzione:
    """
    Verifica che il valore passato sia un intero compreso tra 1 e 90 (inclusi).

    Strategia:
    - Prima valida il tipo (int) usando esito_numero_intero.
    - Poi valida il range 1..90.

    Parametri:
    - numero (object): valore da validare.

    Ritorna:
    - EsitoAzione(ok=True) se numero è un int e 1 <= numero <= 90.
    - EsitoAzione(ok=False, errore="NUMERO_TIPO_NON_VALIDO") se non è un int.
    - EsitoAzione(ok=False, errore="NUMERO_NON_VALIDO") se è int ma fuori range.
    """

    # 1) Validazione tipo (riusabile e separata).
    esito_tipo = esito_numero_intero(numero)
    if not esito_tipo.ok:
        return esito_tipo

    # 2) Validazione range 1..90.
    numero_int = int(numero)
    if numero_int < 1 or numero_int > 90:
        return EsitoAzione(
            ok=False,
            errore="NUMERO_NON_VALIDO",
            evento=None
        )

    return EsitoAzione(
        ok=True,
        errore=None,
        evento=None
    )


def esito_numero_riga_in_range_1_3(numero: object) -> EsitoAzione:
    """
    Verifica che il valore passato sia un intero compreso tra 1 e 3 (inclusi).

    Strategia:
    - Prima valida il tipo (int) usando esito_numero_intero.
    - Poi valida il range 1..3.

    Parametri:
    - numero (object): valore da validare.

    Ritorna:
    - EsitoAzione(ok=True) se numero è un int e 1 <= numero <= 3.
    - EsitoAzione(ok=False, errore="NUMERO_TIPO_NON_VALIDO") se non è un int.
    - EsitoAzione(ok=False, errore="NUMERO_NON_VALIDO") se è int ma fuori range.
    """

    # 1) Validazione tipo (riusabile e separata).
    esito_tipo = esito_numero_intero(numero)
    if not esito_tipo.ok:
        return esito_tipo

    # 2) Validazione range 1..3.
    numero_int = int(numero)
    if numero_int < 1 or numero_int > 3:
        return EsitoAzione(
            ok=False,
            errore="NUMERO_RIGA_FUORI_RANGE",
            evento=None
        )

    return EsitoAzione(
        ok=True,
        errore=None,
        evento=None
    )


def esito_numero_colonna_in_range_1_9(numero: object) -> EsitoAzione:
    """
    Verifica che il valore passato sia un intero compreso tra 1 e 9 (inclusi).

    Strategia:
    - Prima valida il tipo (int) usando esito_numero_intero.
    - Poi valida il range 1..9.

    Parametri:
    - numero (object): valore da validare.

    Ritorna:
    - EsitoAzione(ok=True) se numero è un int e 1 <= numero <= 9.
    - EsitoAzione(ok=False, errore="NUMERO_TIPO_NON_VALIDO") se non è un int.
    - EsitoAzione(ok=False, errore="NUMERO_NON_VALIDO") se è int ma fuori range.
    """

    # 1) Validazione tipo (riusabile e separata).
    esito_tipo = esito_numero_intero(numero)
    if not esito_tipo.ok:
        return esito_tipo

    # 2) Validazione range 1..9.
    numero_int = int(numero)
    if numero_int < 1 or numero_int > 9:
        return EsitoAzione(
            ok=False,
            errore="NUMERO_COLONNA_FUORI_RANGE",
            evento=None
        )

    return EsitoAzione(
        ok=True,
        errore=None,
        evento=None
    )


def esito_reclamo_turno_libero(reclamo_turno: object) -> EsitoAzione:
    """
    Verifica che nel turno corrente NON sia già stato registrato un reclamo.

    Scopo:
    - Tenere GiocatoreUmano pulito: qui facciamo solo una validazione “pura”.
    - Uniformare il comportamento: un solo reclamo per turno.

    Parametri:
    - reclamo_turno (object): tipicamente Optional[ReclamoVittoria], ma lo teniamo
      generico per evitare accoppiamenti inutili al dominio (qui basta sapere se è None).

    Ritorna:
    - EsitoAzione(ok=True) se reclamo_turno è None (nessun reclamo ancora presente).
    - EsitoAzione(ok=False, errore="RECLAMO_GIA_PRESENTE") se reclamo_turno non è None.
    """

    # Regola: un solo reclamo per turno.
    if reclamo_turno is not None:
        return EsitoAzione(
            ok=False,
            errore="RECLAMO_GIA_PRESENTE",
            evento=None
        )

    return EsitoAzione(
        ok=True,
        errore=None,
        evento=None
    )


def esito_tipo_vittoria_supportato(tipo_vittoria: object) -> EsitoAzione:
    """
    Verifica che il tipo di vittoria richiesto sia tra quelli supportati dal progetto.

    Scopo:
    - Validazione input “pura” (no focus, no stato): qui controlliamo solo il valore.
    - Centralizzare la whitelist per evitare duplicazioni tra comandi/metodi.

    Parametri:
    - tipo_vittoria (object): valore da validare (tipicamente una stringa / Literal Tipo_Vittoria).

    Ritorna:
    - EsitoAzione(ok=True) se tipo_vittoria è uno tra:
      "tombola", "ambo", "terno", "quaterna", "cinquina".
    - EsitoAzione(ok=False, errore="TIPO_VITTORIA_NON_VALIDO") altrimenti.

    Nota:
    - Questa funzione NON decide se serve il focus riga o meno: quello resta responsabilità
      del chiamante (es. GiocatoreUmano), per rimanere coerenti con l’architettura.
    """

    # Whitelist centralizzata (stabile e facile da aggiornare).
    tipi_supportati = {"tombola", "ambo", "terno", "quaterna", "cinquina"}

    # Validazione difensiva: se arriva qualcosa di diverso (tipo errato o stringa sconosciuta),
    # non permettiamo di proseguire.
    if tipo_vittoria not in tipi_supportati:
        return EsitoAzione(
            ok=False,
            errore="TIPO_VITTORIA_NON_VALIDO",
            evento=None
        )

    return EsitoAzione(
        ok=True,
        errore=None,
        evento=None
    )
