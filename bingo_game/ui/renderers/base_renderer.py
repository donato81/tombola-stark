"""
Contratto astratto del layer di presentazione.

Definisce:
- StatoConfigurazione: stato immutabile per la schermata di configurazione.
- BaseRenderer: interfaccia astratta per tutti i renderer del progetto.

path: bingo_game/ui/renderers/base_renderer.py
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Optional

from bingo_game.events.codici_configurazione import Codici_Configurazione
from bingo_game.events.codici_messaggi_sistema import SISTEMA_ERRORE_CODICE_MANCANTE
from bingo_game.events.eventi import EsitoAzione
from bingo_game.ui.locales import (
    MESSAGGI_CONFIGURAZIONE,
    MESSAGGI_ERRORI,
    MESSAGGI_EVENTI,
    MESSAGGI_OUTPUT_UI_UMANI,
    MESSAGGI_SISTEMA,
)

_error_logger = logging.getLogger("error")


@dataclass(frozen=True)
class StatoConfigurazione:
    """
    Stato immutabile passato dal controller al renderer durante la schermata
    di configurazione iniziale.

    Il renderer visualizza lo stato ricevuto, ma non governa la sequenza dei passi.
    """

    fase_corrente: Literal["nome", "bot", "cartelle", "conferma"]
    codice_messaggio: Codici_Configurazione
    codice_errore: Optional[Codici_Configurazione] = None
    nome_giocatore: Optional[str] = None
    numero_bot: Optional[int] = None
    numero_cartelle: Optional[int] = None


class BaseRenderer(ABC):
    """
    Contratto astratto per il layer di presentazione.

    Regole di implementazione concreta:
    - Il renderer non governa la logica di gioco ne' la sequenza dei passi.
    - Nessuna stringa hardcoded: ogni testo passa da _formatta_testo_da_catalogo().
    - Ordine fisso handler: testo -> widget -> voce.
    - Sincronizzazione visivo/voce: il testo mostrato e il testo vocalizzato devono coincidere.
    """

    @abstractmethod
    def render_esito(self, esito: EsitoAzione) -> None:
        """
        Renderizza il risultato di un'azione del controller.

        Casi gestiti:
        - esito.ok=False: visualizza e vocalizza l'errore.
        - esito.ok=True, esito.evento=None: successo silenzioso, nessuna azione.
        - esito.ok=True, esito.evento valorizzato: smista al dispatcher interno.
        """
        ...

    @abstractmethod
    def mostra_schermata_configurazione(self, stato: StatoConfigurazione) -> None:
        """
        Mostra la schermata di configurazione per il passo corrente.

        Il controller costruisce lo stato e lo passa qui.
        Il renderer visualizza il pannello corretto e vocalizza il messaggio
        corrispondente al codice_messaggio.
        La decisione sul passo successivo resta fuori dal renderer.
        """
        ...

    @abstractmethod
    def mostra_report_finale(self, dati_partita: dict[str, Any]) -> None:
        """
        Presenta il riepilogo finale della partita.

        Chiavi attese in `dati_partita`:
        - `turni_giocati`: int
        - `stato_partita`: str
        - `numeri_estratti`: list[int]
        - `premi_gia_assegnati`: list[str]
        - `giocatori`: list[dict]

        Chiavi facoltative ma consigliate:
        - `conteggio_estratti`: int
        - `conteggio_premi`: int
        - `conteggio_giocatori`: int
        - `vincitore_tombola`: str | None

        Nota:
        - `DatiReportFinale` e' un refactor futuro raccomandato, fuori scope
          in questo ciclo.
        """
        ...

    @abstractmethod
    def mostra_messaggio_sistema(self, testo: str) -> None:
        """
        Mostra un messaggio di sistema generico (es. avvio partita, reset).

        Il testo deve essere gia' risolto dal controller tramite catalogo.
        """
        ...

    @abstractmethod
    def annuncia_numero_estratto(self, numero: int, numero_turno: int) -> None:
        """
        Vocalizza il numero estratto nel contesto del turno corrente, senza premi.

        Parametri:
        - numero: numero estratto dal tabellone.
        - numero_turno: numero progressivo del turno corrente.
        """
        ...

    @abstractmethod
    def annuncia_premi_turno(self, premi: list) -> None:
        """
        Vocalizza i premi assegnati nel turno corrente.

        Parametri:
        - premi: lista di dizionari evento-premio da verifica_premi().
          Lista vuota = nessun premio questo turno.
        """
        ...

    @abstractmethod
    def annuncia_fase_turno(self, testo_fase: str) -> None:
        """
        Vocalizza la fase corrente del turno (testo già risolto dal chiamante).

        Usato dopo SetLabel del pulsante per garantire il re-announce NVDA.

        Parametri:
        - testo_fase: etichetta human-readable della fase (es. "Passa turno").
        """
        ...

    @abstractmethod
    def annuncia_avviso_timeout(self, secondi_rimanenti: int, livello: int = 80) -> None:
        """
        Vocalizza un avviso progressivo durante la finestra d'azione (fase 2 V2).

        Chiamato ai valori percentuali 60%, 80%, 95% del tempo trascorso.
        Il testo vocale dipende dal livello e usa le chiavi TURNO_AVVISO_*.

        Parametri:
        - secondi_rimanenti: secondi ancora disponibili all'utente.
        - livello: soglia percentuale raggiunta (60, 80 o 95). Default: 80.
        """
        ...

    @abstractmethod
    def annuncia_avvio_pausa_turno(self, secondi: int) -> None:
        """
        Vocalizza l'annuncio di avvio della pausa tra turni (fase 4 V2).

        Parametri:
        - secondi: durata della pausa in secondi.
        """
        ...

    @abstractmethod
    def annuncia_tutti_pronti(self) -> None:
        """
        Vocalizza il messaggio di terminazione anticipata della fase 2 V2:
        tutti i giocatori hanno dichiarato fine prima della scadenza del timer.
        """
        ...

    def _formatta_testo_da_catalogo(self, chiave: str, **kwargs: Any) -> str:
        """
        Cerca la chiave nei cataloghi nell'ordine canonico e restituisce il
        testo formattato con i kwargs forniti.

        Ordine di ricerca:
        1. MESSAGGI_ERRORI
        2. MESSAGGI_EVENTI
        3. MESSAGGI_OUTPUT_UI_UMANI
        4. MESSAGGI_SISTEMA
        5. MESSAGGI_CONFIGURAZIONE

        Comportamento:
        - Se il valore e' una tupla/lista, le righe vengono unite con "\\n".
        - Se la formattazione fallisce (placeholder mancante), si usa il fallback.
        - Fallback finale: SISTEMA_ERRORE_CODICE_MANCANTE da MESSAGGI_SISTEMA.
        - Non ha effetti collaterali: puro lookup + formattazione.
        - In caso di chiave mancante o format fallito, registra avviso nel log errori.
        """
        cataloghi = (
            MESSAGGI_ERRORI,
            MESSAGGI_EVENTI,
            MESSAGGI_OUTPUT_UI_UMANI,
            MESSAGGI_SISTEMA,
            MESSAGGI_CONFIGURAZIONE,
        )
        for catalogo in cataloghi:
            valore = catalogo.get(chiave)
            if valore is None:
                continue
            if isinstance(valore, (list, tuple)):
                testo_raw = "\n".join(str(v) for v in valore)
            else:
                testo_raw = str(valore)
            if not kwargs:
                return testo_raw
            try:
                return testo_raw.format(**kwargs)
            except (KeyError, IndexError) as exc:
                _error_logger.warning(
                    "Placeholder mancante nel catalogo per chiave=%s: %s",
                    chiave,
                    exc,
                )
                break

        # Chiave non trovata in nessun catalogo o formattazione fallita.
        _error_logger.warning("Chiave catalogo non trovata: %s", chiave)
        fallback = MESSAGGI_SISTEMA.get(SISTEMA_ERRORE_CODICE_MANCANTE)
        if fallback is None:
            return ""
        if isinstance(fallback, (list, tuple)):
            return "\n".join(str(v) for v in fallback)
        return str(fallback)
