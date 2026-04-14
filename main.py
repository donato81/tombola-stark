"""Entry point di Tombola Stark — avvio interfaccia wxPython."""

import argparse

import wx

from bingo_game.logging import GameLogger
from bingo_game.ui.finestra_principale import FinestraPrincipale
from bingo_game.ui.renderers.renderer_wx import WxRenderer
from my_lib.vocalizzatore import Vocalizzatore


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Tombola Stark - Gioco della tombola italiana accessibile"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Attiva modalità DEBUG per tracciatura dettagliata (livello logging DEBUG)",
    )
    return parser.parse_args()


def main() -> None:
    """Avvia l'applicazione wxPython aprendo la finestra di configurazione."""
    args = _parse_args()
    GameLogger.initialize(debug_mode=args.debug)

    try:
        app = wx.App(redirect=False)
        vocalizzatore = Vocalizzatore()

        # Il renderer viene creato con un frame temporaneo nullo;
        # FinestraConfigurazione chiama aggiorna_finestra nel proprio __init__.
        renderer: WxRenderer = WxRenderer.__new__(WxRenderer)
        renderer._finestra = None  # type: ignore[assignment]
        renderer._vocalizzatore = vocalizzatore
        renderer._ultimo_annuncio = ""
        renderer._log_text_ctrl = None
        renderer.numero_in_focus = None

        finestra = FinestraPrincipale(renderer=renderer)
        finestra.Show()
        app.MainLoop()
    except Exception:
        import traceback
        from pathlib import Path
        crash_path = Path(__file__).parent / "crash_log.txt"
        with open(crash_path, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
    finally:
        GameLogger.shutdown()


if __name__ == "__main__":
    main()
