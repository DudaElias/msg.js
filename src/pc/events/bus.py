"""Game event system for decoupled event handling."""

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class EventType(Enum):
    """Types of game events."""

    GAME_STARTED = "game_started"
    ROUND_STARTED = "round_started"
    CLUE_REVEALED = "clue_revealed"
    CLUE_HIDDEN = "clue_hidden"
    CORRECT_GUESS = "correct_guess"
    INCORRECT_GUESS = "incorrect_guess"
    ROUND_COMPLETED = "round_completed"
    GAME_OVER = "game_over"


@dataclass
class GameEvent:
    """Base game event."""

    event_type: EventType
    data: dict


class EventBus:
    """Central event bus for publishing and subscribing to events."""

    def __init__(self) -> None:
        """Initialize the event bus."""
        self.subscribers: dict[EventType, list[Callable]] = {}

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe to an event type.

        Args:
            event_type: The type of event to subscribe to
            handler: Callable that will be invoked when event is published
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: The type of event to unsubscribe from
            handler: The handler to remove
        """
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)

    def publish(self, event: GameEvent) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The event to publish
        """
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"Error in event handler for {event.event_type}: {e}")

    def clear(self) -> None:
        """Clear all subscriptions."""
        self.subscribers.clear()
