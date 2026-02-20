"""Entry point dell'applicazione Tombola Stark."""
import argparse
from bingo_game.logging import GameLogger
from bingo_game.ui.ui_terminale import TerminalUI


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


def main() -> None:
    """Main application entry point."""
    args = _parse_args()
    
    # Inizializza il sistema di logging come prima cosa
    GameLogger.initialize(debug_mode=args.debug)
    
    try:
        tui = TerminalUI()
        tui.avvia()
    finally:
        # Assicura sempre la chiusura pulita del logger
        GameLogger.shutdown()


if __name__ == "__main__":
    main()
