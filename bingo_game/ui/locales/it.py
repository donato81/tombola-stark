from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

#import moduli di progetto
from bingo_game.events.codici_configurazione import Codici_Configurazione
from bingo_game.events.codici_controller import (
    CTRL_AVVIO_FALLITO_GENERICO,
    CTRL_TURNO_NON_IN_CORSO,
    CTRL_NUMERI_ESAURITI,
    CTRL_TURNO_FALLITO_GENERICO,
)
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
    # In pratica: la cartella \u201cselezionata\u201d non esiste più (stato non coerente) e va riselezionata.
    "FOCUS_CARTELLA_FUORI_RANGE": (
        "Errore: La cartella selezionata non è più disponibile.",
        "Seleziona una cartella valida per continuare.",
    ),

    # FOCUS_RIGA_NON_IMPOSTATA:
    # La cartella in focus è valida, ma non è stata selezionata alcuna riga.
    # Questo è un prerequisito tipico per azioni \u201crigorse\u201d (es. annuncia ambo/terno/quaterna/cinquina),
    # dove la riga deve essere scelta esplicitamente dall'utente e non viene auto-impostata.
    "FOCUS_RIGA_NON_IMPOSTATA": (
        "Errore: Nessuna riga selezionata.",
        "Seleziona una riga prima di continuare.",
    ),

    # FOCUS_RIGA_FUORI_RANGE:
    # La riga in focus è impostata, ma non è coerente con le righe disponibili
    # nella cartella attualmente in focus (indice fuori dai limiti).
    # In pratica: la riga \u201cselezionata\u201d non esiste più e va selezionata di nuovo.
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
    # In pratica: la colonna \u201cselezionata\u201d non esiste più e va selezionata di nuovo.
    "FOCUS_COLONNA_FUORI_RANGE": (
        "Errore: La colonna selezionata non è più disponibile.",
        "Seleziona una colonna valida per continuare.",
    ),

    #caso errore numero non valido
    "NUMERO_NON_VALIDO": (
        "Errore: Numero non valido.",
        "Inserisci un numero tra 1 e 90.",
    ),

    #caso errore tipo numero non intero
    "NUMERO_TIPO_NON_VALIDO": (
        "Errore: Tipo non valido.",
        "Inserisci un numero intero.",
    ),

    #caso tabellone non presente
    "TABELLONE_NON_DISPONIBILE": (
        "Errore: Tabellone non disponibile.",
        "Riprova oppure avvia una partita valida.",
    ),

    #errore per stato di cartella corrotto in qualche maniera
    "CARTELLA_STATO_INCOERENTE": (
        "Errore: La cartella risulta in uno stato non coerente.",
        "Riprova oppure riavvia la partita.",
    ),

    "NUMERO_RIGA_FUORI_RANGE": (
        "Errore: Numero riga non valido.",
        "Inserisci un numero tra 1 e 3.",
    ),

    "NUMERO_COLONNA_FUORI_RANGE": (
        "Errore: Numero colonna non valido.",
        "Inserisci un numero tra 1 e 9.",
    ),

    #frase per errore quando un reclamo è stato già richiamato in un turno.
    "RECLAMO_GIA_PRESENTE": (
        "Errore: Reclamo già registrato per questo turno.",
        "Attendi il prossimo turno prima di reclamare un'altra vittoria.",
    ),

    #messaggio che scatta quando si inserisce un tipo di vittoria non valido
    "TIPO_VITTORIA_NON_VALIDO": (
        "Errore: Tipo di vittoria non valido.",
        "Tipi supportati: ambo, terno, quaterna, cinquina, tombola.",
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

    # Limite minimo: si è già sulla prima colonna.
    "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MINIMO": (
        "Sei già sulla prima colonna.",
    ),

    # Limite massimo: si è già sull'ultima colonna.
    "UMANI_LIMITE_NAVIGAZIONE_COLONNE_MASSIMO": (
        "Sei già sull'ultima colonna.",
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

    # Prefisso per la visualizzazione della colonna in modalità semplice.
    # Placeholder:
    # - {numero_colonna} (1-based)
    #
    # Il renderer potrà usare questo prefisso e poi aggiungere le 3 celle
    # (numeri o "-" -> usando UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA).
    "UMANI_CARTELLA_SEMPLICE_PREFISSO_COLONNA": (
        "Colonna {numero_colonna}: ",
    ),

    # Testo da usare quando una cella della cartella è vuota (corrisponde a "-").
    # Il renderer:
    # - se trova "-" nella griglia dell'evento, userà questa parola,
    # - se trova un int, userà il numero così com'è.
    "UMANI_CARTELLA_SEMPLICE_CELLA_VUOTA": (
        "vuoto",
    ),

    #stampa della intestazione di riga in formato avanzato
    "UMANI_RIGA_AVVANZATA_INTESTAZIONE": (
        "Riga {numero_riga} - visualizzazione avanzata.",
    ),

    # Intestazione per la visualizzazione AVANZATA della colonna (navigazione colonna).
    # Placeholder:
    # - {numero_colonna} (1-based)
    "UMANI_COLONNA_AVVANZATA_INTESTAZIONE": (
        "Colonna {numero_colonna} - visualizzazione avanzata.",
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

    # Etichetta per i segnati a fine colonna: "Segnati: 5, 24"
    # Placeholder:
    # - {lista_segnati} (lista numeri segnati della colonna, dal renderer)
    "UMANI_COLONNA_AVVANZATA_ETICHETTA_SEGNATI": (
        "Segnati: {lista_segnati}.",
    ),

    # Caso "nessun segnato" a fine riga: "Segnati: nessuno"
    "UMANI_CARTELLA_AVVANZATA_SEGNATI_RIGA_NESSUNO": (
        "Segnati: nessuno.",
    ),

    # Caso "nessun segnato" a fine colonna: "Segnati: nessuno"
    "UMANI_COLONNA_AVVANZATA_SEGNATI_NESSUNO": (
        "Segnati: nessuno.",
    ),

    # Footer riepilogo globale: "Totale segnati: 4 su 15 (26.7%)"
    # Placeholder: {numeri_segnati}, {numeri_totali}, {percentuale}
    "UMANI_CARTELLA_AVVANZATA_FOOTER_RIEPILOGO": (
        "Totale segnati: {numeri_segnati} su {numeri_totali} ({percentuale}%).",
    ),

    # Footer riepilogo colonna: "Totale segnati: 1 su 3 (33.3%)"
    # Placeholder:
    # - {numeri_segnati}
    # - {numeri_totali}
    # - {percentuale}
    "UMANI_COLONNA_AVVANZATA_FOOTER_RIEPILOGO": (
        "Totale segnati: {numeri_segnati} su {numeri_totali} ({percentuale}%).",
    ),

    # Caso 1: segnato con successo.
    # Placeholder:
    # - {numero}: numero segnato
    # - {numero_riga}: riga in forma "umana" (1..3)
    # - {numero_colonna}: colonna in forma "umana" (1..9)
    "UMANI_SEGNAZIONE_NUMERO_SEGNATO": (
        "Numero {numero} segnato (riga {numero_riga}, colonna {numero_colonna}).",
    ),

    # Caso 2: già segnato.
    # Placeholder:
    # - {numero}: numero richiesto
    # - {numero_cartella}: cartella in forma "umana" (1..N)
    "UMANI_SEGNAZIONE_NUMERO_GIA_SEGNATO": (
        "Numero {numero} già segnato in cartella {numero_cartella}.",
    ),

    # Caso 3: non presente nella cartella.
    # Placeholder:
    # - {numero}: numero richiesto
    # - {numero_cartella}: cartella in forma "umana" (1..N)
    "UMANI_SEGNAZIONE_NUMERO_NON_PRESENTE": (
        "Numero {numero} non presente in cartella {numero_cartella}.",
    ),

    # Caso 4: non ancora estratto.
    # Placeholder:
    # - {numero}: numero richiesto
    "UMANI_SEGNAZIONE_NUMERO_NON_ESTRATTO": (
        "Numero {numero} non ancora estratto.",
    ),

    # Ricerca numero nelle cartelle - intestazione (sempre).
    # Placeholder:
    # - {numero}
    # - {totale_cartelle}
    "UMANI_RICERCA_NUMERO_INTESTAZIONE": (
        "Ricerca del numero {numero} nelle tue {totale_cartelle} cartelle.",
    ),

    # Ricerca numero nelle cartelle - esito: non trovato.
    # Placeholder:
    # - {numero}
    "UMANI_RICERCA_NUMERO_NON_TROVATO": (
        "Numero {numero} non presente in nessuna cartella.",
    ),

    # Ricerca numero nelle cartelle - esito: trovato (SINGOLARE).
    # Usare questo messaggio quando len(risultati) == 1.
    # Placeholder:
    # - {numero}
    "UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_SINGOLARE": (
        "Numero {numero} trovato in una cartella.",
    ),

    # Ricerca numero nelle cartelle - esito: trovato (PLURALE).
    # Usare questo messaggio quando len(risultati) != 1.
    # Placeholder:
    # - {numero}
    # - {conteggio_cartelle}
    "UMANI_RICERCA_NUMERO_TROVATO_RIEPILOGO_PLURALE": (
        "Numero {numero} trovato in {conteggio_cartelle} cartelle.",
    ),

    # Ricerca numero nelle cartelle - dettaglio: una riga per ogni risultato.
    # Placeholder:
    # - {numero_cartella}  (1-based, arriva già pronto dal RisultatoRicercaNumeroInCartella)
    # - {numero_riga}      (1..3, conversione nel renderer: indice_riga + 1)
    # - {numero_colonna}   (1..9, conversione nel renderer: indice_colonna + 1)
    # - {stato}            (testo preso dai messaggi UMANI_RICERCA_NUMERO_STATO_*)
    "UMANI_RICERCA_NUMERO_RISULTATO_RIGA": (
        "Cartella {numero_cartella}: riga {numero_riga}, colonna {numero_colonna} ({stato}).",
    ),

    # Ricerca numero - stato per il dettaglio risultato.
    "UMANI_RICERCA_NUMERO_STATO_SEGNATO": (
        "già segnato",
    ),

    # Ricerca numero - stato per il dettaglio risultato.
    "UMANI_RICERCA_NUMERO_STATO_DA_SEGNARE": (
        "da segnare",
    ),

    # Verifica numero estratto: caso "sì".
    # Placeholder:
    # - {numero}: numero richiesto dall'utente
    "UMANI_VERIFICA_NUMERO_ESTRATTO_SI": (
        "Numero {numero} è stato estratto.",
    ),

    # Verifica numero estratto: caso "no".
    # Placeholder:
    # - {numero}: numero richiesto dall'utente
    "UMANI_VERIFICA_NUMERO_ESTRATTO_NO": (
        "Numero {numero} non è ancora stato estratto.",
    ),

    # stringa da mostrare in caso di ultimo numero estratto presente
    # placeholder ultimo_numero
    "UMANI_ULTIMO_NUMERO_ESTRATTO_PRESENTE": (
        "Ultimo numero estratto: {ultimo_numero}.",
    ),

    # stringa da mostrare nel caso non ci siano numeri estratti
    "UMANI_ULTIMO_NUMERO_ESTRATTO_NESSUNO": (
        "Nessun numero estratto ancora.",
    ),

    # frase per evento ultimi numeri estratti 5
    "UMANI_ULTIMI_NUMERI_ESTRATTI_PRESENTI": (
        "Ultimi {visualizzati} numeri estratti: {lista}.",
    ),

    # caso ultimi numeri estratti nessuno estratto
    "UMANI_ULTIMI_NUMERI_ESTRATTI_NESSUNO": (
        "Nessun numero estratto ancora.",
    ),

    # Riepilogo tabellone - riga 1 (sintesi globale).
    # Placeholder:
    # - {totale_estratti}
    # - {totale_numeri}
    # - {totale_mancanti}
    # - {percentuale_estrazione}
    "UMANI_RIEPILOGO_TABELLONE_RIGA_1": (
        "Tabellone. "
        "Estratti {totale_estratti}/{totale_numeri}. "
        "Mancanti {totale_mancanti}. "
        "Avanzamento {percentuale_estrazione}%.",
    ),

    # Lista numeri estratti (tabellone) - intestazione.
    # Scopo:
    # - Annunciare subito quanti numeri sono stati estratti, prima di leggere le righe per decine.
    # Placeholder:
    # - {totale_estratti}
    "UMANI_LISTA_NUMERI_ESTRATTI_INTESTAZIONE": (
        "Sono stati estratti {totale_estratti} numeri.",
    ),

    # Lista numeri estratti (tabellone) - una riga per decina NON vuota.
    # Nota renderer:
    # - Questa riga viene emessa solo se la decina contiene almeno un numero estratto.
    # - Le decine vuote vengono saltate (scelta anti-verbosità per screen reader).
    # Placeholder:
    # - {da}     (inizio decina: 1, 10, 20, ..., 80)
    # - {a}      (fine decina: 9, 19, 29, ..., 90)
    # - {lista}  (lista formattata dal renderer, es. "10, 12, 19")
    "UMANI_LISTA_NUMERI_ESTRATTI_DECINA_LISTA": (
        "{da}\u2013{a}: {lista}.",
    ),

    # Stato focus corrente - cartella presente.
    # Placeholder:
    # - {numero_cartella}  (1-based)
    # - {totale_cartelle}
    "UMANI_STATO_FOCUS_CORRENTE_CARTELLA_PRESENTE": (
        "Cartella in focus: {numero_cartella} di {totale_cartelle}.",
    ),

    # Stato focus corrente - cartella non impostata.
    "UMANI_STATO_FOCUS_CORRENTE_CARTELLA_NESSUNA": (
        "Cartella in focus: nessuna.",
    ),

    # Stato focus corrente - riga presente.
    # Placeholder:
    # - {numero_riga} (1..3)
    "UMANI_STATO_FOCUS_CORRENTE_RIGA_PRESENTE": (
        "Riga in focus: {numero_riga}.",
    ),

    # Stato focus corrente - riga non impostata.
    "UMANI_STATO_FOCUS_CORRENTE_RIGA_NESSUNA": (
        "Riga in focus: nessuna.",
    ),

    # Stato focus corrente - colonna presente.
    # Placeholder:
    # - {numero_colonna} (1..9)
    "UMANI_STATO_FOCUS_CORRENTE_COLONNA_PRESENTE": (
        "Colonna in focus: {numero_colonna}.",
    ),

    # Stato focus corrente - colonna non impostata.
    "UMANI_STATO_FOCUS_CORRENTE_COLONNA_NESSUNA": (
        "Colonna in focus: nessuna.",
    ),

    # Reclamo vittoria - conferma registrazione (fase ANTE_TURNO).
    # Scopo: messaggio breve per l'utente, senza includere turno (anti-verbosità).
    "UMANI_RECLAMO_VITTORIA_TOMBOLA_REGISTRATO": (
        "Reclamo registrato: tombola.",
    ),

    # Reclamo vittoria di riga (ambo/terno/quaterna/cinquina).
    # Placeholder:
    # - {tipo}: stringa tipo vittoria (es. "ambo", "terno", "quaterna", "cinquina")
    "UMANI_RECLAMO_VITTORIA_RIGA_REGISTRATO": (
        "Reclamo registrato: {tipo}.",
    ),

    # Seconda riga standard (riusabile) per chiarire il flusso: registrazione ora, verifica dopo.
    # Nota: volutamente generica (vale per tutti i tipi di reclamo).
    "UMANI_RECLAMO_VITTORIA_NOTA_VALIDAZIONE": (
        "Il reclamo verrà verificato dalla partita a fine turno.",
    ),

    # Fine turno (output UI umano).
    # Caso: nessun reclamo associato al turno (reclamo_turno is None).
    "UMANI_FINE_TURNO_PASSATO": (
        "Turno passato.",
    ),

    # Fine turno (output UI umano).
    # Caso: reclamo associato al turno (reclamo_turno presente).
    # Placeholder:
    # - {tipo}: tipo di reclamo/vittoria (es. "ambo", "terno", "quaterna", "cinquina", "tombola")
    "UMANI_FINE_TURNO_PASSATO_CON_RECLAMO": (
        "Turno passato. Reclamo inviato: {tipo}.",
    ),

    # =========================================================================
    # Game Loop v0.9.0 — Messaggi interattivi del loop di partita
    # =========================================================================

    # Numero estratto nell'ultimo turno.
    # Placeholder: {numero}
    "LOOP_NUMERO_ESTRATTO": (
        "Numero estratto: {numero}.",
    ),

    # Prompt interattivo mostrato dopo ogni estrazione.
    "LOOP_PROMPT_COMANDO": (
        "Comando (p=prosegui  s=segna  c=cartella  v=tabellone  q=esci  ?=aiuto):",
    ),

    # Help comandi: tupla multi-riga, una riga per comando.
    "LOOP_HELP_COMANDI": (
        "p  — prosegui al prossimo turno.",
        "s <N>  — segna il numero N sulla cartella in focus.",
        "c  — riepilogo cartella in focus.",
        "v  — riepilogo tabellone (numeri estratti).",
        "q  — esci dalla partita (chiede conferma).",
        "?  — mostra questo aiuto.",
    ),

    # Riga aggiuntiva dell'help: cartella attualmente in focus.
    # Placeholder: {numero_cartella} (1-based)
    "LOOP_HELP_FOCUS": (
        "Cartella in focus: {numero_cartella}.",
    ),

    # Richiesta di conferma quit.
    "LOOP_QUIT_CONFERMA": (
        "Vuoi davvero uscire? La partita non verrà salvata. (s/n)",
    ),

    # Uscita annullata (utente ha risposto 'n').
    "LOOP_QUIT_ANNULLATO": (
        "Uscita annullata. Partita in corso.",
    ),

    # ---- Report finale ----

    # Intestazione del report finale.
    "LOOP_REPORT_FINALE_INTESTAZIONE": (
        "=== FINE PARTITA ===",
    ),

    # Turni giocati.
    # Placeholder: {turni}
    "LOOP_REPORT_FINALE_TURNI": (
        "Turni giocati: {turni}.",
    ),

    # Numeri estratti su 90.
    # Placeholder: {estratti}
    "LOOP_REPORT_FINALE_ESTRATTI": (
        "Numeri estratti: {estratti}/90.",
    ),

    # Vincitore tombola.
    # Placeholder: {nome}
    "LOOP_REPORT_FINALE_VINCITORE": (
        "Vincitore Tombola: {nome}!",
    ),

    # Nessun vincitore (numeri esauriti).
    "LOOP_REPORT_FINALE_NESSUN_VINCITORE": (
        "Partita terminata senza tombola.",
    ),

    # Premi totali assegnati.
    # Placeholder: {premi}
    "LOOP_REPORT_FINALE_PREMI": (
        "Premi assegnati: {premi}.",
    ),

    # Comando non riconosciuto.
    "LOOP_COMANDO_NON_RICONOSCIUTO": (
        "Comando non riconosciuto. Digita ? per l'aiuto.",
    ),

    # Prompt interattivo per il comando `s` senza argomento (Bug 2 v0.9.1).
    "LOOP_SEGNA_CHIEDI_NUMERO": (
        "Quale numero vuoi segnare? (1-90):",
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


# Messaggi per il flusso di configurazione della partita (TUI Start Menu).
# Chiavi definite in bingo_game/events/codici_configurazione.py.
# Ogni entry è una tupla di righe: il renderer chiama print() su ciascuna riga.
MESSAGGI_CONFIGURAZIONE: Mapping[Codici_Configurazione, tuple[str, ...]] = MappingProxyType({
    "CONFIG_BENVENUTO": (
        "Benvenuto in Tombola Stark!",
    ),
    "CONFIG_CONFERMA_AVVIO": (
        "Configurazione completata. Avvio partita...",
    ),
    "CONFIG_RICHIESTA_NOME": (
        "Inserisci il tuo nome (max 15 caratteri): ",
    ),
    "CONFIG_RICHIESTA_BOT": (
        "Inserisci il numero di bot (1-7): ",
    ),
    "CONFIG_RICHIESTA_CARTELLE": (
        "Inserisci il numero di cartelle (1-6): ",
    ),
    "CONFIG_ERRORE_NOME_VUOTO": (
        "Errore: Nome non valido.",
        "Inserisci almeno un carattere.",
    ),
    "CONFIG_ERRORE_NOME_TROPPO_LUNGO": (
        "Errore: Nome troppo lungo.",
        "Inserisci al massimo 15 caratteri.",
    ),
    "CONFIG_ERRORE_BOT_RANGE": (
        "Errore: Numero bot non valido.",
        "Inserisci un valore tra 1 e 7.",
    ),
    "CONFIG_ERRORE_CARTELLE_RANGE": (
        "Errore: Numero cartelle non valido.",
        "Inserisci un valore tra 1 e 6.",
    ),
})


MESSAGGI_CONTROLLER: dict[str, str] = {
    CTRL_AVVIO_FALLITO_GENERICO: "Impossibile avviare la partita. Riprova o riavvia l'applicazione.",
    CTRL_TURNO_NON_IN_CORSO: "Impossibile eseguire il turno: la partita non è in corso.",
    CTRL_NUMERI_ESAURITI: "Tutti i 90 numeri sono stati estratti. La partita termina senza vincitore.",
    CTRL_TURNO_FALLITO_GENERICO: "Errore durante l'esecuzione del turno. La partita potrebbe essere terminata.",
}
