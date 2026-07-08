"""Data models for the game."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class InformationType(Enum):
    """Types of information clues."""

    WORD = "word" # Single word
    AUDIO = "audio"  # Audio file
    PHRASE = "phrase"  # Text description/phrase
    IMAGE = "image"  # Image file


@dataclass
class Clue:
    """A single clue for a word."""

    clue_type: InformationType
    content: str

    def display_name(self) -> str:
        """Get the display name for the clue type.

        Returns:
            Display name
        """
        names = {
            InformationType.AUDIO: "🔊 Áudio",
            InformationType.WORD: "📝 Palavra",
            InformationType.PHRASE: "💬 Frase",
            InformationType.IMAGE: "🖼️ Imagem",
        }
        return names.get(self.clue_type, self.clue_type.value)


@dataclass
class PlayerSection:
    """One player's section with their single clue."""

    player_id: int
    clue: Clue
    revealed: bool = False

    def toggle_clue(self) -> None:
        """Toggle visibility of the clue."""
        self.revealed = not self.revealed

    def hide_clue(self) -> None:
        """Hide the clue."""
        self.revealed = False


@dataclass
class Round:
    """A single game round."""

    round_number: int
    word: str
    clue_type: Optional[InformationType] = None
    player_sections: List[PlayerSection] = field(default_factory=list)
    guessed: bool = False
    correct_guess: bool = False


@dataclass
class GameState:
    """Tracks the overall game state."""

    current_round: int = 1
    rounds: List[Round] = field(default_factory=list)
    guess_input: str = ""
    game_message: str = ""
    message_type: str = "info"  # 'info', 'success', 'error'
    game_over: bool = False
    total_correct: int = 0

    def get_current_round_data(self) -> Optional[Round]:
        """Get the current round data.

        Returns:
            Current Round or None if doesn't exist
        """
        if 1 <= self.current_round <= len(self.rounds):
            return self.rounds[self.current_round - 1]
        return None

    def next_round(self) -> None:
        """Move to next round."""
        self.current_round += 1
        self.guess_input = ""
        self.game_message = ""

    def add_guess_char(self, char: str) -> None:
        """Add a character to the current guess.

        Args:
            char: Character to add
        """
        if len(self.guess_input) < 20:  # Limit guess length
            self.guess_input += char.upper()

    def remove_guess_char(self) -> None:
        """Remove the last character from the guess."""
        if self.guess_input:
            self.guess_input = self.guess_input[:-1]

    def clear_guess(self) -> None:
        """Clear the entire guess input."""
        self.guess_input = ""

    def check_guess(self) -> bool:
        """Check if current guess is correct.

        Returns:
            True if guess matches the word
        """
        current_round = self.get_current_round_data()
        if current_round:
            # Normalize both strings: uppercase, strip whitespace
            guess_normalized = self.guess_input.strip().upper()
            word_normalized = current_round.word.strip().upper()

            if guess_normalized == word_normalized:
                current_round.correct_guess = True
                current_round.guessed = True
                self.total_correct += 1
                return True

        return False

    def set_message(self, message: str, msg_type: str = "info") -> None:
        """Set a game message.

        Args:
            message: Message to display
            msg_type: Type of message ('info', 'success', 'error')
        """
        self.game_message = message
        self.message_type = msg_type
