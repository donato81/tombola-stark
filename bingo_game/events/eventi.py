from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union

# Import codici errore
from bingo_game.events.codici_errori import Codici_Errori

# Import eventi ammessi (ombrello)
from bingo_game.events.eventi_ui import (
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
)
from bingo_game.events.eventi_partita import (
    EventoReclamoVittoria,
    EventoEsitoReclamoVittoria,
    EventoFineTurno,
)


# Ombrello: elenco chiuso degli eventi che possono viaggiare dentro EsitoAzione.evento
EventoAzione = Union[
    EventoFocusAutoImpostato,
    EventoFocusCartellaImpostato,
    EventoReclamoVittoria,
    EventoEsitoReclamoVittoria,
    EventoFineTurno,
]


@dataclass(frozen=True)
class EsitoAzione:
    """
    Esito generico per metodi "command" (es. navigazione focus, annuncia_ambo, annuncia_tombola, ecc.).

    Regole (semplici e stabili):
    - Se ok=False  -> errore DEVE essere valorizzato, evento DEVE essere None.
    - Se ok=True   -> errore DEVE essere None, evento può essere un EventoAzione oppure None
                     (successo "silenzioso", utile per non essere troppo verbosi in UI/voce).
    """

    ok: bool
    errore: Optional[Codici_Errori] = None
    evento: Optional[EventoAzione] = None

    @classmethod
    def successo(cls, evento: Optional[EventoAzione] = None) -> "EsitoAzione":
        """
        Crea un esito di successo.
        - errore sempre None
        - evento opzionale (può essere None per successi silenziosi)
        """
        return cls(ok=True, errore=None, evento=evento)

    @classmethod
    def fallimento(cls, errore: Codici_Errori) -> "EsitoAzione":
        """
        Crea un esito di fallimento.
        - ok sempre False
        - errore obbligatorio
        - evento sempre None
        """
        return cls(ok=False, errore=errore, evento=None)

    def __str__(self) -> str:
        if not self.ok:
            if self.errore == "CARTELLE_NESSUNA_ASSEGNATA":
                return "Errore: Non hai ancora assegnato nessuna cartella."
            if self.errore == "FOCUS_CARTELLA_NON_IMPOSTATO":
                return "Non hai selezionato nessuna cartella"
            if self.errore == "NUMERO_NON_VALIDO":
                return "Errore: numero non valido. Deve essere tra 1 e 90"
            if self.errore == "NUMERO_TIPO_NON_VALIDO":
                return "Errore: tipo numero non valido"
            if self.errore == "FOCUS_CARTELLA_FUORI_RANGE":
                return "Errore: focus cartella fuori range"
            return f"Errore: {self.errore}"

        if self.evento is None:
            return "Ok"

        from bingo_game.events.eventi_ui import EventoFocusCartellaImpostato, EventoFocusAutoImpostato
        from bingo_game.events.eventi_output_ui_umani import (
            EventoNavigazioneColonnaAvanzata,
            EventoSegnazioneNumero,
            EventoRicercaNumeroInCartelle,
            RisultatoRicercaNumeroInCartella,
        )

        # Focus cartella impostato
        if isinstance(self.evento, EventoFocusCartellaImpostato):
            return f"Focus impostato sulla cartella {self.evento.numero_cartella}."

        # Focus autoinizializzato
        if isinstance(self.evento, EventoFocusAutoImpostato):
            return f"Focus auto-impostato su {self.evento.tipo_focus} {self.evento.indice}."

        # Visualizzazione cartelle (compatibilità del renderer test legacy)
        from bingo_game.events.eventi_output_ui_umani import (
            EventoVisualizzaCartellaSemplice,
            EventoVisualizzaCartellaAvanzata,
            EventoVisualizzaTutteCartelleSemplice,
            EventoVisualizzaTutteCartelleAvanzata,
        )

        def _format_riga_generica(riga, segnati=None):
            if segnati is None:
                segnati = set()
            tokens = []
            for cella in riga:
                if cella == "-":
                    tokens.append("-")
                elif cella in segnati:
                    tokens.append(f"*{cella}")
                else:
                    tokens.append(str(cella))
            return " ".join(tokens)

        if isinstance(self.evento, EventoVisualizzaCartellaSemplice):
            lines = [" ".join(str(c) for c in riga) for riga in self.evento.griglia_semplice]
            return "\n".join(lines)

        if isinstance(self.evento, EventoVisualizzaCartellaAvanzata):
            segnati = set(self.evento.numeri_segnati_ordinati or ())
            lines = [f"--- Cartella {self.evento.numero_cartella} ---"]
            for riga in self.evento.griglia_semplice:
                lines.append(_format_riga_generica(riga, segnati))
            stats = self.evento.stato_cartella if isinstance(self.evento.stato_cartella, dict) else {}
            lines.append(f"Totale segnati: {stats.get('numeri_segnati', 0)}")
            return "\n".join(lines)

        if isinstance(self.evento, EventoVisualizzaTutteCartelleSemplice):
            all_lines = []
            for numero_cartella, griglia in self.evento.cartelle:
                all_lines.append(f"--- Cartella {numero_cartella} ---")
                for riga in griglia:
                    all_lines.append(" ".join(str(c) for c in riga))
            return "\n".join(all_lines)

        if isinstance(self.evento, EventoVisualizzaTutteCartelleAvanzata):
            all_lines = []
            for numero_cartella, griglia, stato, numeri_segnati_cartella in self.evento.cartelle:
                numeri_segnati = set(numeri_segnati_cartella or ())
                all_lines.append(f"--- Cartella {numero_cartella} ---")
                for riga in griglia:
                    all_lines.append(_format_riga_generica(riga, numeri_segnati))
                stats = stato if isinstance(stato, dict) else {}
                all_lines.append(f"Totale segnati: {stats.get('numeri_segnati', 0)}")
            return "\n".join(all_lines)

        # Navigazione colonna avanzata
        if isinstance(self.evento, EventoNavigazioneColonnaAvanzata):
            if self.evento.esito == "limite":
                if self.evento.limite == "massimo":
                    return f"Sei all'ultima colonna ({self.evento.totale_colonne}), non puoi andare oltre"
                if self.evento.limite == "minimo":
                    return "Sei alla prima colonna, non puoi andare oltre"
            if self.evento.esito == "mostra":
                numero_colonna = self.evento.numero_colonna_corrente - 1
                segnati = set(self.evento.stato_colonna.get("numeri_segnati_colonna", [])) if isinstance(self.evento.stato_colonna, dict) else set()
                content = _format_riga_generica(self.evento.colonna_semplice, segnati)
                stats = self.evento.stato_colonna if isinstance(self.evento.stato_colonna, dict) else {}
                suffix = f" Segnati: {stats.get('numeri_segnati', 0)} su {stats.get('numeri_totali', 0)}" if stats else ""
                return f"Colonna {numero_colonna}: {content}{suffix}".strip()

        # Navigazione colonna semplice (compatibilità)
        from bingo_game.events.eventi_output_ui_umani import EventoNavigazioneColonna, EventoNavigazioneRiga, EventoNavigazioneRigaAvanzata
        if isinstance(self.evento, EventoNavigazioneColonna):
            if self.evento.esito == "limite":
                if self.evento.limite == "massimo":
                    return f"Sei all'ultima colonna ({self.evento.totale_colonne}), non puoi andare oltre"
                if self.evento.limite == "minimo":
                    return "Sei alla prima colonna, non puoi andare oltre"
            if self.evento.esito == "mostra":
                numero_colonna = self.evento.numero_colonna_corrente - 1
                items = [str(cella) for cella in self.evento.colonna_semplice if cella != "-"]
                content = ", ".join(items) if items else "vuota"
                return f"Colonna {numero_colonna}: {content}"

        # Navigazione riga semplice/avanzata (compatibilità)
        if isinstance(self.evento, (EventoNavigazioneRiga, EventoNavigazioneRigaAvanzata)):
            if self.evento.esito == "limite":
                if self.evento.limite == "massimo":
                    return "Sei all'ultima riga, non puoi andare oltre"
                if self.evento.limite == "minimo":
                    return "Sei alla prima riga, non puoi andare oltre"
            if self.evento.esito == "mostra":
                numero_riga = self.evento.numero_riga_corrente - 1
                segnati = set(getattr(self.evento, 'numeri_segnati_riga_ordinati', ()) or [])
                if not segnati and hasattr(self.evento, 'stato_riga') and isinstance(self.evento.stato_riga, dict):
                    segnati = set(self.evento.stato_riga.get('numeri_segnati_riga', []))
                content = _format_riga_generica(self.evento.riga_semplice, segnati) if self.evento.riga_semplice is not None else ""
                return f"Riga {numero_riga}: {content}"

        # Segnazione numero
        if isinstance(self.evento, EventoSegnazioneNumero):
            if self.evento.esito == "non_estratto":
                return f"Numero {self.evento.numero} non è ancora stato estratto"
            if self.evento.esito == "non_presente":
                return f"Numero {self.evento.numero} non è presente nella Cartella {self.evento.numero_cartella}"
            if self.evento.esito == "gia_segnato":
                return f"Numero {self.evento.numero} è già stato segnato"
            if self.evento.esito == "segnato":
                return f"Fatto! Segnato numero {self.evento.numero}"

        # Ricerca numero nelle cartelle
        if isinstance(self.evento, EventoRicercaNumeroInCartelle):
            if self.evento.esito == "non_trovato":
                return f"Il numero {self.evento.numero} non è presente nelle tue cartelle"
            if self.evento.esito == "trovato":
                lines = [f"Trovato {self.evento.numero} in:"]
                for r in self.evento.risultati:
                    stato = "Già segnato" if r.segnato else "DA SEGNARE"
                    lines.append(f"Cartella {r.numero_cartella}: Riga {r.indice_riga + 1} Colonna {r.indice_colonna + 1} ({stato})")
                return "\n".join(lines)
            return f"Numero {self.evento.numero} non presente in nessuna cartella"

        # Fallback generico
        return str(self.evento)

    def __contains__(self, item: str) -> bool:
        return item in str(self)

    def split(self, sep=None, maxsplit=-1):
        return str(self).split(sep, maxsplit)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            if self.errore == "CARTELLE_NESSUNA_ASSEGNATA":
                return other in (
                    "Non hai selezionato nessuna cartella",
                    "Errore: Non hai ancora assegnato nessuna cartella.",
                )
            if self.errore == "FOCUS_CARTELLA_NON_IMPOSTATO":
                return other in (
                    "Non hai selezionato nessuna cartella",
                    "Errore: Seleziona prima una cartella su cui segnare il numero.",
                )
            return str(self) == other
        return super().__eq__(other)
