"""Placeholder temporaneo dell'entry point di Tombola Stark."""

import argparse

from bingo_game.logging import GameLogger


def _parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments with debug flag.
    """
    parser = argparse.ArgumentParser(
        description="Tombola Stark - Gioco della tombola italiana accessibile"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Attiva modalità DEBUG per tracciatura dettagliata (livello logging DEBUG)"
    )
    return parser.parse_args()


def _build_placeholder_message() -> str:
    """Restituisce il messaggio temporaneo mostrato all'avvio."""
    return (
        "Tombola Stark: interfaccia utente non ancora disponibile.\n"
        "Il progetto e' in transizione verso una nuova UI.\n"
        "Il motore applicativo e il logging restano disponibili per lo sviluppo."
    )


def main() -> None:
    """Avvia il placeholder temporaneo dell'applicazione."""
    args = _parse_args()

    GameLogger.initialize(debug_mode=args.debug)

    try:
        print(_build_placeholder_message())
    finally:
        GameLogger.shutdown()


if __name__ == "__main__":
    main()
