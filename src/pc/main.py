"""Rise of Babel - A word guessing game with multi-sensory clues.

Usage:
    python main.py COM5
    python main.py --mock  # Test without serial connection

Install dependencies first:
    pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
from typing import Optional, Tuple
import sys

import pygame

from pc.utils.config import FRAME_RATE, WINDOW_HEIGHT, WINDOW_WIDTH
from pc.events import EventBus
from pc.core import BabelGame
from pc.handlers import LEDHandler
from pc.ui import Renderer, StartScreen
from pc.hardware import PicoLink


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Rise of Babel - Word guessing game with Pico integration"
    )
    parser.add_argument("port", nargs="?", default="COM5", help="Serial port (default: COM5)")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate")
    parser.add_argument("--mock", action="store_true", help="Use mock serial connection")
    return parser.parse_args()


def setup_pygame() -> Tuple[pygame.Surface, pygame.time.Clock]:
    """Initialize Pygame and create window.

    Returns:
        Tuple of (screen surface, clock)
    """
    pygame.init()
    pygame.display.set_caption("Rise of Babel")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    return screen, clock


def handle_game_events(game: BabelGame, renderer: "Renderer") -> bool:
    """Handle pygame events during gameplay.

    Args:
        game: BabelGame instance
        renderer: Renderer instance (for mouse clicks)

    Returns:
        False if quit event occurred, True otherwise
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.TEXTINPUT:
            if not game.state.game_over and event.text and event.text != " ":
                game.handle_key_input(0, event.text)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key == pygame.K_r and game.state.game_over:
                game.reset_game()
            elif event.key == pygame.K_SPACE:
                # Space is used for guess input during play and restart on game over
                if game.state.game_over:
                    game.reset_game()
                else:
                    game.handle_key_input(event.key, "")
            elif event.key in {pygame.K_BACKSPACE, pygame.K_RETURN, pygame.K_DELETE}:
                game.handle_key_input(event.key, "")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                next_round_clicked = renderer.handle_click(game, event.pos)
                if next_round_clicked:
                    game.next_round()

    return True


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    args = parse_args()

    # Setup serial connection
    if args.mock:
        print("Running in mock mode - simulating Pico connection")
        link = PicoLink(args.port, args.baud, use_mock=True)
    else:
        link = PicoLink(args.port, args.baud, use_mock=False)

    if link.connection is None:
        print("Failed to connect to serial port")
        if not args.mock:
            PicoLink.list_available_ports()
        return 1

    # Setup pygame
    screen, clock = setup_pygame()

    # Initialize event bus and LED handler
    event_bus = EventBus()
    led_handler = LEDHandler(link)
    led_handler.register(event_bus)

    # Initialize screens and game
    start_screen = StartScreen()
    game: Optional[BabelGame] = None
    renderer: Optional[Renderer] = None

    # Application state
    running = True
    in_menu = True

    # Main loop
    while running:
        if in_menu:
            # Show start screen
            running, action = start_screen.handle_input()

            if action == "start":
                # Start the game with event bus
                game = BabelGame(link, event_bus)
                renderer = Renderer()
                in_menu = False
            elif action == "quit":
                running = False

            start_screen.draw(screen)
        else:
            # Gameplay loop
            running = handle_game_events(game, renderer)

            # Draw game
            renderer.draw(screen, game)

        pygame.display.flip()
        clock.tick(FRAME_RATE)

    # Cleanup
    link.close()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
