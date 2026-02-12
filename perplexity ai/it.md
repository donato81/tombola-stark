from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

#import moduli di progetto
from bingo_game.events.codici_errori import Codici_Errori
from bingo_game.events.codici_eventi import Codici_Eventi
from bingo_game.events.codici_messaggi_sistema import Codici_Messaggi_Sistema
from bingo_game.events.codici_output_ui_umani import Codici_Output_Ui_Umani 


#strutture dati per utilizzo con renderer da riportare al utente finale 

# Messaggi associati ai CodiceErrore.
# Ogni entry è una tupla di righe: il renderer potrà fare "\n".join(righe) per stampare.
MESSAGGI_ERRORI: Mapping[Codici_Errori, tuple[str, ...]] = MappingProxyType({
    # CARTELLE_NESSUNA_ASSEGNATA:
    # Usato come guardia di base in molte azioni (navigazione, annunci, ecc.).
    # Messaggio generico e riusabile, non legato a un comando specifico.
    "CARTELLE_NESSUNA_ASSEGNATA": (
        "Errore: Nessuna cartella assegnata.",
        "Avvia una partita o assegna una cartella al giocatore.",
    ),

    # FOCUS_CARTELLA_NON_IMPOSTATO:
    # Il giocatore ha cartelle, ma non è stata selezionata alcuna cartella attiva.
    # Messaggio generico e riusabile (non legato a un comando specifico).
    "FOCUS_CARTELLA_NON_IMPOSTATO": (
        "Errore: Nessuna cartella selezionata.",
        "Seleziona una cartella prima di continuare.",
    ),

    # FOCUS_CARTELLA_FUORI_RANGE:
    # Il focus cartella è impostato, ma punta fuori dai limiti della lista cartelle.
    # In pratica: la cartella “selezionata” non esiste più (stato non coerente) e va riselezionata.
    "FOCUS_CARTELLA_FUORI_RANGE": (
        "Errore: La cartella selezionata non è più disponibile.",
        "Seleziona una cartella valida per continuare.",
    ),

    # FOCUS_RIGA_NON_IMPOSTATA:
    # La cartella in focus è valida, ma non è stata selezionata alcuna riga.
    # Questo è un prerequisito tipico per azioni “rigorose” (es. annuncia ambo/terno/quaterna/cinquina),
    # dove la riga deve essere scelta esplicitamente dall’utente e non viene auto-impostata.
    "FOCUS_RIGA_NON_IMPOSTATA": (
        "Errore: Nessuna riga selezionata.",
        "Seleziona una riga prima di continuare.",
    ),

    # FOCUS_RIGA_FUORI_RANGE:
    # La riga in focus è impostata, ma non è coerente con le righe disponibili
    # nella cartella attualmente in focus (indice fuori dai limiti).
    # In pratica: la riga “selezionata” non esiste più e va selezionata di nuovo.
    "FOCUS_RIGA_FUORI_RANGE": (
        "Errore: La riga selezionata non è più disponibile.",
        "Seleziona una riga valida per continuare.",
    ),

    # FOCUS_COLONNA_NON_IMPOSTATA:
    # Non è stata selezionata alcuna colonna (focus colonna assente).
    "FOCUS_COLONNA_NON_IMPOSTATA": (
        "Errore: Nessuna colonna selezionata.",
        "Seleziona una colonna per continuare.",
    ),

    # FOCUS_COLONNA_FUORI_RANGE:
    # La colonna in focus è impostata, ma non è coerente con le colonne disponibili
    # nella cartella attualmente in focus (indice fuori dai limiti).
    # In pratica: la colonna “selezionata” non esiste più e va selezionata di nuovo.
    "FOCUS_COLONNA_FUORI_RANGE": (
        "Errore: La colonna selezionata non è più disponibile.",
        "Seleziona una colonna valida per continuare.",
    ),
})


# Messaggi associati agli eventi (successi/feedback).
# Anche qui il valore è sempre una tupla di righe.
# Nota: le righe possono contenere placeholder (es. "{numero}") che verranno sostituiti dal renderer.
MESSAGGI_EVENTI: Mapping[Codici_Eventi, tuple[str, ...]] = MappingProxyType({
    # EVENTO_FOCUS_AUTO_IMPOSTATO:
    # Quando un helper imposta automaticamente un focus mancante.
    # Placeholder disponibili:
    # - {tipo}: "cartella" / "riga" / "colonna"
    # - {numero}: indice convertito in numero umano (1-based)
    "EVENTO_FOCUS_AUTO_IMPOSTATO": (
        "{tipo} selezionata automaticamente: {numero}.",
    ),
})


# Messaggi "di output" per la UI del giocatore umano.
# Servono a rendere eventi ricchi di dati (dataclass) prodotti dai metodi del giocatore umano
# (es. riepiloghi, letture) senza usare i messaggi di sistema.
MESSAGGI_OUTPUT_UI_UMANI: Mapping[Codici_Output_Ui_Umani, tuple[str, ...]] = MappingProxyType({
    # Riepilogo cartella corrente - riga 1 (sintesi)
    # Placeholder:
    # - {numero_cartella}
    # - {numeri_segnati}
    # - {totale_numeri}
    # - {mancanti}
    # - {percentuale}
    "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_1": (
        "Cartella {numero_cartella}. "
        "Segnati {numeri_segnati}/{totale_numeri}. "
        "Mancanti {mancanti}. "
        "Completamento {percentuale}%.",
    ),

    # Riepilogo cartella corrente - riga 2 quando non ci sono numeri da segnare
    "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_NESSUNO": (
        "Da segnare: nessuno.",
    ),

    # Riepilogo cartella corrente - riga 2 quando ci sono numeri da segnare
    # Placeholder:
    # - {lista}
    "UMANI_RIEPILOGO_CARTELLA_CORRENTE_RIGA_2_LISTA": (
        "Da segnare: {lista}.",
    ),

    # Limite minimo: si è già sulla prima cartella (1 riga).
    # Placeholder:
    # - {totale_cartelle}
    "UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MINIMO": (
        "Sei già sulla prima cartella (1 di {totale_cartelle}).",
    ),

    # Limite massimo: si è già sull'ultima cartella (1 riga).
    # Placeholder:
    # - {totale_cartelle}
    "UMANI_LIMITE_NAVIGAZIONE_CARTELLE_MASSIMO": (
        "Sei già sull'ultima cartella ({totale_cartelle} di {totale_cartelle}).",
    ),

    "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MINIMO": (
        "Sei già sulla prima riga.",
    ),

    "UMANI_LIMITE_NAVIGAZIONE_RIGHE_MASSIMO": (
        "Sei già sull'ultima riga.",
    ),

    # Intestazione per la visualizzazione della cartella semplice.
    # Placeholder:
    # - {numero_cartella} (1-based)
    # - {totale_cartelle}
    "UMANI_CARTELLA_SEMPLICE_INTESTAZIONE": (
        "Cartella {numero_cartella} di {totale_cartelle}.",
    ),

    # Prefisso per ogni riga della cartella semplice.
    # Placeholder:
    # - {numero_riga} (1, 2, 3)
    #
    # Il renderer potrà usare questo prefisso e poi aggiungere i numeri / celle vuote.
    "UMANI_CARTELLA_SEMPLICE_PREFISSO_RIGA": (
        "Riga {numero_riga}: ",
    ),

    # Testo da usare quando una cella della cartella è vuota (corrisponde a "-").
    # Il renderer:
    # - se trova "-" nella griglia dell'evento, userà questa parola,
    # - se trova un int, userà il numero così com'è.
    "UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA": (
        "vuoto",
    ),

    # Intestazione specifica per visualizzazione AVANZATA.
    # Placeholder: {numero_cartella}, {totale_cartelle}
    "UMANI_CARTELLA_AVVANZATA_INTESTAZIONE": (
        "Cartella {numero_cartella} di {totale_cartelle} - visualizzazione avanzata.",
    ),

    # Etichetta per i segnati a fine riga: "Segnati: 5, 24"
    # Placeholder: {lista_segnati} (lista numeri segnati della riga, dal renderer)
    "UMANI_CARTELLA_AVVANZATA_ETICHETTA_SEGNATI_RIGA": (
        "Segnati: {lista_segnati}.",
    ),

    # Caso "nessun segnato" a fine riga: "Segnati: nessuno"
    "UMANI_CARTELLA_AVVANZATA_SEGNATI_RIGA_NESSUNO": (
        "Segnati: nessuno.",
    ),

    # Footer riepilogo globale: "Totale segnati: 4 su 15 (26.7%)"
    # Placeholder: {numeri_segnati}, {numeri_totali}, {percentuale}
    "UMANI_CARTELLA_AVVANZATA_FOOTER_RIEPILOGO": (
        "Totale segnati: {numeri_segnati} su {numeri_totali} ({percentuale}%).",
    ),

})


# Messaggi di sistema / fallback del renderer.
# Sono frasi "di sicurezza" usate quando:
# - manca un codice nel catalogo
# - arriva un evento non supportato
# - i template sono malformati
# Valore: tuple di righe (immutabile).
MESSAGGI_SISTEMA: Mapping[Codici_Messaggi_Sistema, tuple[str, ...]] = MappingProxyType({
    # Errori "strutturali" del dominio/esito
    "SISTEMA_ERRORE_CODICE_MANCANTE": (
        "Errore: stato non valido (codice mancante).",
        "Dettaglio: EsitoAzione.ok è False ma EsitoAzione.errore è None.",
    ),
    "SISTEMA_ERRORE_MESSAGGIO_NON_DISPONIBILE": (
        "Errore: messaggio non disponibile.",
    ),
    "SISTEMA_ERRORE_CODICE_NON_MAPPATO_DEBUG": (
        "Errore: messaggio non disponibile.",
        "Dettaglio tecnico: codice errore non mappato -> {codice}.",
    ),

    # Fallback focus auto-impostato
    "SISTEMA_SELEZIONE_AUTOMATICA_EFFETTUATA": (
        "Selezione automatica effettuata.",
    ),
    "SISTEMA_TIPO_FOCUS_NON_PREVISTO_DEBUG": (
        "Selezione automatica effettuata.",
        "Dettaglio tecnico: tipo_focus non previsto -> {tipo_focus}.",
    ),
    "SISTEMA_TEMPLATE_EVENTO_MANCANTE_DEBUG": (
        "{tipo} selezionata automaticamente: {numero}.",
        "Dettaglio tecnico: template {chiave_evento} non presente nel catalogo.",
    ),
    "SISTEMA_PLACEHOLDER_TEMPLATE_MANCANTE_DEBUG": (
        "Selezione automatica effettuata.",
        "Dettaglio tecnico: placeholder mancante nel template -> {exc}.",
    ),

    # Focus cartella impostato (testo standard)
    "SISTEMA_FOCUS_CARTELLA_IMPOSTATO": (
        "Focus impostato sulla cartella {numero_cartella}.",
    ),
    "SISTEMA_FOCUS_RESET_RIGA_COLONNA": (
        "Riga e colonna in focus sono state reimpostate.",
    ),

    # Fine turno
    "SISTEMA_TURNO_PASSATO": (
        "Turno passato.",
    ),
    "SISTEMA_RECLAMO_ASSOCIATO_TOMBOLA": (
        "Reclamo associato: {tipo} (cartella {cartella}).",
    ),
    "SISTEMA_RECLAMO_ASSOCIATO_RIGA": (
        "Reclamo associato: {tipo} (cartella {cartella}, riga {riga}).",
    ),
    "SISTEMA_RECLAMO_ASSOCIATO_RIGA_NON_DISPONIBILE": (
        "Reclamo associato: {tipo} (cartella {cartella}, riga non disponibile).",
    ),

    # Reclamo inviato / riferimento
    "SISTEMA_RECLAMO_INVIATO": (
        "Reclamo inviato: {tipo} (fase {fase}).",
    ),
    "SISTEMA_RIFERIMENTO_TOMBOLA": (
        "Riferimento: cartella {cartella}.",
    ),
    "SISTEMA_RIFERIMENTO_RIGA": (
        "Riferimento: cartella {cartella}, riga {riga}.",
    ),
    "SISTEMA_RIFERIMENTO_RIGA_NON_DISPONIBILE": (
        "Riferimento: cartella {cartella}, riga non disponibile.",
    ),

    # Esito reclamo
    "SISTEMA_ESITO_RECLAMO": (
        "Esito reclamo {esito}: {tipo} (fase {fase}).",
    ),
    "SISTEMA_ESITO_RECLAMO_MOTIVO": (
        "Motivo: {errore}.",
    ),
    "SISTEMA_ESITO_RECLAMO_TURNO": (
        "Turno: {indice_turno}.",
    ),
    "SISTEMA_ESITO_RECLAMO_NUMERO_ESTRATTO": (
        "Numero estratto: {numero_estratto}.",
    ),

    # Evento sconosciuto
    "SISTEMA_EVENTO_NON_SUPPORTATO": (
        "Evento non supportato dal renderer.",
    ),
    "SISTEMA_EVENTO_NON_SUPPORTATO_DEBUG": (
        "Evento non supportato dal renderer.",
        "Dettaglio tecnico: tipo evento -> {tipo_evento}.",
    ),
})
