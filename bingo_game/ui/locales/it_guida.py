"""bingo_game/ui/locales/it_guida.py

Testi della Finestra guida regole del gioco (FinestraGuidaRegole).
Cinque capitoli a scorrimento. Il renderer unisce le righe con '\\n'.join(righe).
"""
from __future__ import annotations

from collections.abc import Sequence
from types import MappingProxyType

GUIDA_CAPITOLI: Sequence[tuple[str, tuple[str, ...]]] = (
    (
        "Introduzione alla Tombola",
        (
            "La Tombola è un classico gioco di società italiano. L'obiettivo è",
            "segnare i numeri estratti sulla propria cartella e dichiarare i premi",
            "nel giusto ordine, prima degli avversari.",
            "",
            "In Tombola Stark giochi contro uno o più bot controllati dal computer.",
            "Il gioco estrae un numero alla volta dal tabellone, che contiene tutti",
            "i numeri da 1 a 90. Ogni numero può essere estratto una sola volta",
            "per partita.",
            "",
            "Vince chi dichiara la Tombola per primo, cioè chi completa tutte e",
            "tre le righe della propria cartella.",
        ),
    ),
    (
        "La cartella",
        (
            "La cartella è la tua scheda di gioco. È composta da tre righe e nove",
            "colonne, per un totale di ventisette caselle. Di queste, solo quindici",
            "contengono numeri: le altre dodici sono vuote.",
            "",
            "I numeri sono distribuiti per decine: la prima colonna contiene numeri",
            "tra 1 e 9, la seconda tra 10 e 19, e così via fino alla nona colonna",
            "che contiene numeri tra 80 e 90.",
            "",
            "Puoi giocare con una sola cartella o con più cartelle, fino a un",
            "massimo di sei. Puoi scegliere il numero di cartelle nella schermata",
            "di configurazione prima di iniziare la partita. Il gioco ti mostra",
            "una cartella alla volta: puoi passare da una all'altra con i tasti",
            "Ctrl+1, Ctrl+2 fino a Ctrl+6.",
        ),
    ),
    (
        "I premi in ordine",
        (
            "I premi della Tombola si dichiarano in ordine crescente. Non puoi",
            "saltare un premio: devi vincere l'ambo prima di poter dichiarare",
            "il terno, e così via.",
            "",
            "L'ordine dei premi è il seguente:",
            "",
            "Ambo: due numeri segnati sulla stessa riga.",
            "Terno: tre numeri segnati sulla stessa riga.",
            "Quaterna: quattro numeri segnati sulla stessa riga.",
            "Cinquina: cinque numeri segnati sulla stessa riga, cioè una riga completa.",
            "Tombola: tutti e quindici i numeri segnati, cioè tutte e tre le righe complete.",
            "",
            "Ogni premio può essere vinto una sola volta per partita. Se un bot",
            "dichiara un premio prima di te, quel premio è perso: non puoi più",
            "dichiararlo. La partita termina quando qualcuno dichiara la Tombola.",
        ),
    ),
    (
        "Come si svolge un turno",
        (
            "All'inizio di ogni turno, il gioco estrae automaticamente un numero",
            "dal tabellone e lo annuncia ad alta voce. Se quel numero è presente",
            "su una delle tue cartelle, puoi segnarlo.",
            "",
            "Hai 60 secondi per trovare il numero sulla tua cartella e segnarlo",
            "con il tasto Spazio. Se non fai nulla entro i 60 secondi, il turno",
            "passa automaticamente al successivo. Puoi anche decidere di passare",
            "subito il turno con Ctrl+Invio, senza aspettare.",
            "",
            "Se dopo aver segnato un numero hai raggiunto una combinazione",
            "vincente, puoi dichiarare il premio con i tasti F1 (ambo), F2",
            "(terno), F3 (quaterna), F4 (cinquina) o F5 (tombola). Ricorda:",
            "i premi vanno dichiarati in ordine. Il gioco segnala automaticamente",
            "se la dichiarazione non è corretta.",
        ),
    ),
    (
        "I bot avversari",
        (
            "I bot sono giocatori automatici controllati dal computer. Per",
            "impostazione predefinita c'è un solo bot, chiamato Bot 1. Puoi",
            "scegliere di aggiungerne altri nella schermata di configurazione",
            "prima di iniziare.",
            "",
            "I bot giocano in modo autonomo: segnano i numeri estratti sulle",
            "loro cartelle e dichiarano i premi quando ne hanno diritto. Non",
            "devi fare nulla per farli giocare.",
            "",
            "I bot possono vincere i premi prima di te. Se Bot 1 dichiara",
            "l'ambo prima che tu lo faccia, l'ambo è assegnato a lui e tu non",
            "puoi più dichiararlo. Tieni d'occhio i messaggi vocali: il gioco",
            "annuncia ogni vittoria dei bot non appena avviene.",
        ),
    ),
)

GUIDA_UI: MappingProxyType[str, str] = MappingProxyType(
    {
        "TITOLO_FINESTRA": "Guida alle regole del gioco",
        "BTN_PRECEDENTE": "Precedente",
        "BTN_SUCCESSIVO": "Successivo",
        "BTN_CHIUDI": "Chiudi",
        "ANNUNCIO_PAGINA": "Pagina {corrente} di {totale}",
    }
)
