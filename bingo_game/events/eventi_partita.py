from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

#import file del progetto.
from bingo_game.events.codici_errori import Codici_Errori

# Tipi di dominio

Tipo_Vittoria = Literal[
    "ambo",
    "terno",
    "quaterna",
    "cinquina",
    "tombola"
]

Fase_Validazione_Reclamo = Literal[
    "ANTE_TURNO",  # warning: il giocatore può ancora cambiare idea
    "FINE_TURNO",  # decisione definitiva della Partita dopo il passa turno
]

@dataclass(frozen=True)
class ReclamoVittoria:
    """
    Reclamo di vittoria effettuato dal giocatore.

    Nota:
    - indice_cartella / indice_riga sono 0-based (indici interni).
    - Per tombola, indice_riga deve essere None.
    """
    tipo: Tipo_Vittoria
    indice_cartella: int
    indice_riga: Optional[int] = None

@classmethod
def tombola(
    cls,
    *,
    indice_cartella: int,
) -> "ReclamoVittoria":
    """
    Factory method per creare un reclamo di vittoria di tipo tombola.

    Scopo:
    - Rendere impossibile creare uno stato incoerente (tombola con riga valorizzata).
    - Centralizzare la convenzione: tombola è sempre riferita solo alla cartella.

    Nota:
    - Gli indici sono 0-based (interni).
    - La validazione di focus/range è demandata al chiamante (GiocatoreUmano),
      coerentemente con il resto del progetto: se non ci sono prerequisiti,
      il reclamo non deve proprio essere creato.
    """
    return cls(
        tipo="tombola",
        indice_cartella=indice_cartella,
        indice_riga=None,
    )


@classmethod
def vittoria_di_riga(
    cls,
    *,
    tipo: "Tipo_Vittoria",
    indice_cartella: int,
    indice_riga: int,
) -> "ReclamoVittoria":
    """
        Factory method per creare un reclamo di vittoria riferita a una riga
        (ambo/terno/quaterna/cinquina).

        Scopo:
        - Rendere esplicito che queste vittorie richiedono sempre una riga.
        - Evitare stati incoerenti (es. ambo con indice_riga=None).
        - Mantenere un solo punto “ufficiale” di costruzione per reclami di riga,
        come accade negli altri eventi con factory method dedicati. [file:131]

        Regole:
        - `tipo` NON deve essere "tombola" (tombola usa il factory `tombola`).
        - Gli indici sono 0-based (interni).

        Nota:
        - Anche qui la validazione di focus/range è demandata al chiamante.
        """
    return cls(
        tipo=tipo,
        indice_cartella=indice_cartella,
        indice_riga=indice_riga,
    )


@dataclass(frozen=True)
class EventoReclamoVittoria:
    """
    Evento "soft" di reclamo, usabile per warning ANTE_TURNO (non vincolante come
    il reclamo inviato con EventoFineTurno).
    """
    id_giocatore: Optional[int]
    nome_giocatore: str
    numero_turno: int
    reclamo: ReclamoVittoria
    fase: Fase_Validazione_Reclamo = "ANTE_TURNO"

@classmethod
def ante_turno(
    cls,
    *,
    id_giocatore: Optional[int],
    nome_giocatore: str,
    numero_turno: int,
    reclamo: ReclamoVittoria,
) -> "EventoReclamoVittoria":
    """
    Factory method per creare un EventoReclamoVittoria in fase ANTE_TURNO.

    Scopo:
    - Standardizzare la costruzione dell'evento "soft" che conferma alla UI
      che il reclamo è stato registrato (ma NON ancora validato dalla Partita).
    - Centralizzare la convenzione: `fase` deve essere sempre "ANTE_TURNO" in
      questo scenario.
    - Agganciare esplicitamente il reclamo al `numero_turno`, utile per log,
      debug e gestione coerente di più turni.

    Cosa NON fa volutamente:
    - Non valida l'esistenza della vittoria (questa è responsabilità della Partita).
    - Non valida focus/range (responsabilità del chiamante, es. GiocatoreUmano).
    - Non controlla la coerenza tombola/riga: ci si aspetta che il ReclamoVittoria
      sia stato creato tramite i suoi factory method (tombola/vittoria_di_riga).

    Parametri:
    - id_giocatore: identificativo opzionale (può essere None in contesti non assegnati).
    - nome_giocatore: nome descrittivo per UI/log.
    - numero_turno: numero del turno corrente (intero >= 1, convenzione di progetto).
    - reclamo: payload del reclamo (immutabile) da associare all'evento.

    Ritorna:
    - EventoReclamoVittoria con fase impostata a "ANTE_TURNO".
    """
    # Nota: la validazione rigorosa (tipo, range, prerequisiti) è demandata al chiamante,
    # coerentemente con lo stile del progetto (prima EsitoAzione, poi creazione evento).
    return cls(
        id_giocatore=id_giocatore,
        nome_giocatore=nome_giocatore,
        numero_turno=numero_turno,
        reclamo=reclamo,
        fase="ANTE_TURNO",
    )


@dataclass(frozen=True)
class EventoEsitoReclamoVittoria:
    """
    Evento di risposta della Partita: esito di un reclamo.

    Regola chiave:
    - La Partita NON "promuove" un reclamo sbagliato (es. ambo -> terno).
      Se non corrisponde, ok=False con VERIFICA_FALLITA (solo in FINE_TURNO).
    """
    id_giocatore: Optional[int]
    nome_giocatore: str
    reclamo: ReclamoVittoria
    ok: bool
    errore: Optional[Codici_Errori] = None
    fase: Fase_Validazione_Reclamo = "FINE_TURNO"

    # Contesto opzionale (utile per UI/log/test, non obbligatorio da subito)
    indice_turno: Optional[int] = None
    numero_estratto: Optional[int] = None


    @classmethod
    def successo(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        reclamo: ReclamoVittoria,
        fase: Fase_Validazione_Reclamo = "FINE_TURNO",
        indice_turno: Optional[int] = None,
        numero_estratto: Optional[int] = None,
    ) -> "EventoEsitoReclamoVittoria":
        """
        Crea un esito di reclamo riuscito.
        Regola: se ok=True allora errore deve essere None.
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            reclamo=reclamo,
            ok=True,
            errore=None,
            fase=fase,
            indice_turno=indice_turno,
            numero_estratto=numero_estratto,
        )

    @classmethod
    def fallimento(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        reclamo: ReclamoVittoria,
        errore: Codici_Errori,
        fase: Fase_Validazione_Reclamo = "FINE_TURNO",
        indice_turno: Optional[int] = None,
        numero_estratto: Optional[int] = None,
    ) -> "EventoEsitoReclamoVittoria":
        """
        Crea un esito di reclamo fallito.
        Regola: se ok=False allora errore deve essere valorizzato.
        """
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            reclamo=reclamo,
            ok=False,
            errore=errore,
            fase=fase,
            indice_turno=indice_turno,
            numero_estratto=numero_estratto,
        )


@dataclass(frozen=True)
class EventoFineTurno:
    """
    Evento prodotto da un giocatore quando decide di passare il turno.

    Nota:
    - Non contiene messaggi per l'utente.
    - Il testo verrà generato da UI/Partita (o da un layer di rendering).
    - Contiene opzionalmente un reclamo di vittoria registrato nel turno.
    """
    id_giocatore: Optional[int]
    nome_giocatore: str
    numero_turno: int
    reclamo_turno: Optional["ReclamoVittoria"] = None

    @classmethod
    def crea(
        cls,
        *,
        id_giocatore: Optional[int],
        nome_giocatore: str,
        numero_turno: int,
        reclamo_turno: Optional["ReclamoVittoria"] = None,
    ) -> "EventoFineTurno":
        """
        Factory method per creare l'evento di fine turno.

        Scopo:
        - Standardizzare la costruzione dell'evento che verrà inviato alla Partita
          quando un giocatore conclude il turno.
        - Centralizzare la convenzione: il reclamo è opzionale e, se presente,
          deve essere già stato costruito/validato a monte (es. da GiocatoreUmano).
        - Tenere l'evento stabile: aggiunte future (es. nuovi campi) si gestiscono qui
          senza toccare tutti i punti chiamanti.

        Cosa NON fa volutamente:
        - Non valida la correttezza del reclamo (ambo vero, tombola vera, ecc.):
          quella è responsabilità della Partita.
        - Non valida numero_turno (>=1) o tipi: le validazioni restano a monte,
          coerentemente con lo stile del progetto (prima EsitoAzione, poi evento).

        Parametri:
        - id_giocatore: id opzionale del giocatore (può essere None in alcuni contesti).
        - nome_giocatore: nome descrittivo (UI/log).
        - numero_turno: turno corrente (convenzione: intero >= 1).
        - reclamo_turno: eventuale reclamo da allegare al passaggio turno.

        Ritorna:
        - EventoFineTurno immutabile pronto per essere processato dalla Partita.
        """

        # Nota funzionale: qui non "tocchiamo" reclamo_turno, lo incapsuliamo soltanto.
        return cls(
            id_giocatore=id_giocatore,
            nome_giocatore=nome_giocatore,
            numero_turno=numero_turno,
            reclamo_turno=reclamo_turno,
        )
