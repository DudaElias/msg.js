"""LED handler for responding to game events."""

from pc.events import EventBus, EventType, GameEvent
from pc.hardware import PicoLink


class LEDHandler:
    """Handles LED control in response to game events."""

    def __init__(self, pico_link: PicoLink) -> None:
        """Initialize LED handler.

        Args:
            pico_link: Serial link to Pico board
        """
        self.pico_link = pico_link

    def register(self, event_bus: EventBus) -> None:
        """Register handlers with the event bus.

        Args:
            event_bus: The event bus to register with
        """
        event_bus.subscribe(EventType.GAME_STARTED, self.on_game_started)
        event_bus.subscribe(EventType.ROUND_STARTED, self.on_round_started)
        event_bus.subscribe(EventType.CORRECT_GUESS, self.on_correct_guess)
        event_bus.subscribe(EventType.INCORRECT_GUESS, self.on_incorrect_guess)
        event_bus.subscribe(EventType.GAME_OVER, self.on_game_over)

    def on_game_started(self, event: GameEvent) -> None:
        """Handle game start event.

        Args:
            event: The game event
        """
        self.pico_link.send("READY")

    def on_round_started(self, event: GameEvent) -> None:
        """Handle round start event.

        Args:
            event: The game event
        """
        self.pico_link.send("READY")

    def on_correct_guess(self, event: GameEvent) -> None:
        """Handle correct guess event.

        Args:
            event: The game event
        """
        total_correct = event.data.get("total_correct", 0)
        self.pico_link.send("HIT")
        self.pico_link.send(f"SCORE {total_correct}")

    def on_incorrect_guess(self, event: GameEvent) -> None:
        """Handle incorrect guess event.

        Args:
            event: The game event
        """
        self.pico_link.send("MISS")

    def on_game_over(self, event: GameEvent) -> None:
        """Handle game over event.

        Args:
            event: The game event
        """
        self.pico_link.send("GAME_OVER")
