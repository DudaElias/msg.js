"""Game logic for Rise of Babel."""

from __future__ import annotations

from typing import Optional

from pc.events import EventBus, EventType, GameEvent
from .models import GameState, Round
from pc.hardware import PicoLink
from .game_data import create_game_rounds


class BabelGame:
    """Manages the Rise of Babel game logic."""

    def __init__(self, link: PicoLink, event_bus: Optional[EventBus] = None) -> None:
        """Initialize the game.

        Args:
            link: PicoLink instance for serial communication
            event_bus: Optional event bus for publishing events
        """
        self.link = link
        self.event_bus = event_bus or EventBus()
        self.state = GameState()
        self.state.rounds = create_game_rounds()
        self._publish_event(EventType.GAME_STARTED, {})

    def handle_key_input(self, key: int, text: str = "") -> None:
        """Handle keyboard input during gameplay.

        Args:
            key: pygame key code
            text: Optional text character from the key event
        """
        import pygame

        if key == pygame.K_BACKSPACE:
            self.state.remove_guess_char()
        elif key == pygame.K_RETURN:
            self.submit_guess()
        elif key == pygame.K_DELETE:
            self.state.clear_guess()
        elif key == pygame.K_SPACE:
            self.state.add_guess_char(" ")
        elif text:
            for char in text:
                if char.isprintable() and char != "\x00":
                    self.state.add_guess_char(char)

    def _publish_event(self, event_type: EventType, data: dict) -> None:
        """Publish a game event.

        Args:
            event_type: Type of event to publish
            data: Event data payload
        """
        event = GameEvent(event_type=event_type, data=data)
        self.event_bus.publish(event)

    def submit_guess(self) -> None:
        """Submit the current guess."""
        if not self.state.guess_input.strip():
            self.state.set_message("Digite uma palavra!", "error")
            return

        if self.state.check_guess():
            # Correct guess
            self._publish_event(
                EventType.CORRECT_GUESS,
                {"total_correct": self.state.total_correct, "round": self.state.current_round}
            )
            self.state.set_message(f"Correto! Clique em 'Próxima'", "success")
        else:
            # Incorrect guess
            self._publish_event(EventType.INCORRECT_GUESS, {"guess": self.state.guess_input})
            self.state.set_message("Incorreto. Tente novamente!", "error")

        # Clear input for next attempt
        self.state.clear_guess()

    def next_round(self) -> bool:
        """Move to the next round.

        Returns:
            True if there are more rounds, False if game is over
        """
        self.state.next_round()

        if self.state.get_current_round_data() is None:
            # Game over - all rounds completed
            self.state.game_over = True
            self._publish_event(
                EventType.GAME_OVER,
                {"total_correct": self.state.total_correct, "total_rounds": len(self.state.rounds)}
            )
            self.state.set_message(
                f"Jogo Finalizado! Acertos: {self.state.total_correct}/{len(self.state.rounds)}",
                "success"
            )
            return False

        # Publish round completed event
        self._publish_event(
            EventType.ROUND_COMPLETED,
            {"round": self.state.current_round - 1}
        )

        # Prepare new round
        current_round = self.state.get_current_round_data()
        if current_round:
            self._publish_event(
                EventType.ROUND_STARTED,
                {"round": self.state.current_round, "clue_type": current_round.clue_type.value}
            )
            self.state.set_message(f"Rodada {self.state.current_round}", "info")
            return True

        return False

    def toggle_clue(self, section_id: int) -> None:
        """Toggle visibility of a player's clue.

        Args:
            section_id: Player section ID (0-2)
        """
        current_round = self.state.get_current_round_data()
        if current_round and 0 <= section_id < len(current_round.player_sections):
            current_round.player_sections[section_id].toggle_clue()

    def hide_all_clues(self) -> None:
        """Hide all clues in the current round."""
        current_round = self.state.get_current_round_data()
        if current_round:
            for section in current_round.player_sections:
                section.hide_clue()

    def reset_game(self) -> None:
        """Reset the game to initial state."""
        self.state = GameState()
        self.state.rounds = create_game_rounds()
        self._publish_event(EventType.GAME_STARTED, {})
