"""Game rendering for Rise of Babel."""

from __future__ import annotations

import os
from typing import List, Optional, Tuple
import pygame

from .background import BackgroundRenderer
from ..utils.config import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    BAD_COLOR,
    GOOD_COLOR,
    PANEL_COLOR,
    SECTION_BG,
    SECTION_BORDER,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    WHITE,
)
from ..core import BabelGame


class Renderer:
    """Handles all game rendering and tracks clickable areas."""

    def __init__(self) -> None:
        """Initialize renderer with pixel art style fonts."""
        self.font_title = pygame.font.SysFont("courier", 48, bold=True)
        self.font_large = pygame.font.SysFont("courier", 40, bold=True)
        self.font_normal = pygame.font.SysFont("courier", 32)
        self.font_small = pygame.font.SysFont("courier", 24)
        self.font_tiny = pygame.font.SysFont("courier", 20)
        self.clickable_areas = {}  # Store button positions
        self.tooltip_rects = {}  # Store tooltip info for hover detection
        self.next_round_button = None  # Store next round button position
        self.image_cache = {}  # Cache loaded images
        self.current_sound = None  # Track currently playing sound
        self.image_modal_open = False  # Track if image modal is open
        self.modal_image_path = None  # Track which image is being shown in modal
        self.modal_close_button = None  # Store close button position
        self.image_clickable_areas = {}  # Store clickable image areas
        self.background = BackgroundRenderer()  # Background renderer
        # Initialize audio support if available
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Warning: Could not initialize pygame mixer")
        # Get path to project root (msg.js folder)
        current_dir = os.path.dirname(os.path.abspath(__file__))  # src/pc
        self.project_root = os.path.dirname(os.path.dirname(current_dir))  # msg.js

    def draw(self, screen: pygame.Surface, game: BabelGame) -> None:
        """Draw the game frame.

        Args:
            screen: Pygame surface to draw on
            game: BabelGame instance
        """
        # Draw pixel art background
        self.background.draw(screen)

        self.clickable_areas = {}  # Reset clickable areas
        self.tooltip_rects = {}  # Reset tooltip areas
        self.next_round_button = None  # Reset next round button
        self.image_clickable_areas = {}  # Reset image clickable areas

        # Draw header
        self._draw_header(screen, game)

        # Draw player sections
        self._draw_player_sections(screen, game)

        # Draw guess area
        self._draw_guess_area(screen, game)

        # Draw message
        self._draw_message(screen, game)

        # Draw next round button if round is guessed
        self._draw_next_round_button(screen, game)

        # Draw tooltips if mouse is hovering
        self._draw_tooltips(screen)

        # Draw image modal if open
        if self.image_modal_open:
            self._draw_image_modal(screen)

        # Draw game over overlay if needed
        if game.state.game_over:
            self._draw_game_over_screen(screen, game)

    def _draw_image_modal(self, screen: pygame.Surface) -> None:
        """Draw an image modal with enlarged image and close button.

        Args:
            screen: Pygame surface to draw on
        """
        # Semi-transparent dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Load full-size image
        if self.modal_image_path:
            image = self._load_image(self.modal_image_path, max_width=700, max_height=600, keep_ratio=True)
            if image:
                # Modal background
                modal_width = 800
                modal_height = 700
                modal_x = (WINDOW_WIDTH - modal_width) // 2
                modal_y = (WINDOW_HEIGHT - modal_height) // 2

                pygame.draw.rect(screen, SECTION_BG, pygame.Rect(modal_x, modal_y, modal_width, modal_height))
                pygame.draw.rect(screen, ACCENT_COLOR, pygame.Rect(modal_x, modal_y, modal_width, modal_height), 3)

                # Draw image centered in modal
                image_rect = image.get_rect(center=(WINDOW_WIDTH // 2, modal_y + modal_height // 2 - 30))
                screen.blit(image, image_rect)

                # Close button
                button_width = 150
                button_height = 50
                button_x = (WINDOW_WIDTH - button_width) // 2
                button_y = modal_y + modal_height - 70

                pygame.draw.rect(screen, BAD_COLOR, pygame.Rect(button_x, button_y, button_width, button_height))
                pygame.draw.rect(screen, WHITE, pygame.Rect(button_x, button_y, button_width, button_height), 2)

                close_text = self.font_small.render("Fechar", True, BACKGROUND_COLOR)
                close_text_rect = close_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
                screen.blit(close_text, close_text_rect)

                # Store button position
                self.modal_close_button = pygame.Rect(button_x, button_y, button_width, button_height)

    def _draw_header(self, screen: pygame.Surface, game: BabelGame) -> None:
        """Draw the header with title and round info.

        Args:
            screen: Pygame surface to draw on
            game: BabelGame instance
        """
        # Background bar with pixel art style border
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 90)
        pygame.draw.rect(screen, (35, 30, 45), header_rect)  # Tower shadow color
        pygame.draw.rect(screen, (240, 190, 90), header_rect, 3)  # Tower window color border

        # Title with shadow (pixel art style)
        title_shadow = self.font_title.render("RISE OF BABEL", True, (35, 30, 45))
        title_shadow_rect = title_shadow.get_rect(center=(WINDOW_WIDTH // 2 + 1, 32))
        screen.blit(title_shadow, title_shadow_rect)

        title = self.font_title.render("RISE OF BABEL", True, (240, 190, 90))  # Tower window color
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        screen.blit(title, title_rect)

        # Round info and clue type
        current_round = game.state.get_current_round_data()
        if current_round:
            clue_type_name = current_round.clue_type.value.upper()
            round_text = self.font_tiny.render(
                f"Rodada {game.state.current_round} de {len(game.state.rounds)} | Tipo: {clue_type_name}",
                True,
                (200, 200, 220)
            )
        else:
            round_text = self.font_tiny.render(
                f"Rodada {game.state.current_round} de {len(game.state.rounds)}",
                True,
                (200, 200, 220)
            )
        round_rect = round_text.get_rect(topleft=(20, 60))
        screen.blit(round_text, round_rect)

        # Score
        score_text = self.font_tiny.render(
            f"Acertos: {game.state.total_correct}",
            True,
            (90, 220, 140)  # Green
        )
        score_rect = score_text.get_rect(topright=(WINDOW_WIDTH - 20, 60))
        screen.blit(score_text, score_rect)

    def _draw_player_sections(self, screen: pygame.Surface, game: BabelGame) -> None:
        """Draw the three player sections with clues.

        Args:
            screen: Pygame surface to draw on
            game: BabelGame instance
        """
        current_round = game.state.get_current_round_data()
        if not current_round:
            return

        section_width = (WINDOW_WIDTH - 60) // 3
        section_height = 250
        start_y = 100
        start_x = 20

        for i, section in enumerate(current_round.player_sections):
            x = start_x + i * (section_width + 20)
            self._draw_section(screen, game, section, x, start_y, section_width, section_height, i)

    def _draw_section(self, screen: pygame.Surface, game: BabelGame, section, x: int, y: int,
                      width: int, height: int, section_id: int) -> None:
        """Draw a single player section.

        Args:
            screen: Pygame surface to draw on
            game: BabelGame instance
            section: PlayerSection object
            x, y: Top-left position
            width, height: Dimensions
            section_id: Section index (0-2)
        """
        # Background with pixel art border
        pygame.draw.rect(screen, (50, 50, 70), pygame.Rect(x, y, width, height))
        pygame.draw.rect(screen, (90, 190, 255), pygame.Rect(x, y, width, height), 3)  # Accent color border

        # Player label
        player_text = self.font_normal.render(f"Player {section_id + 1}", True, (240, 190, 90))  # Tower window color
        player_rect = player_text.get_rect(center=(x + width // 2, y + 18))
        screen.blit(player_text, player_rect)

        # Show/Hide button with pixel art style
        button_height = 50
        button_width = width - 20
        button_x = x + 10
        button_y = y + 60

        # Button background color
        if section.revealed:
            button_color = (90, 220, 140)  # Green
            button_text = "MOSTRAR"
        else:
            button_color = (255, 170, 80)  # Orange
            button_text = "OCULTO"

        # Draw button with thick border (pixel art style)
        pygame.draw.rect(screen, button_color, pygame.Rect(button_x, button_y, button_width, button_height))
        pygame.draw.rect(screen, WHITE, pygame.Rect(button_x, button_y, button_width, button_height), 3)

        # Button text
        btn_text = self.font_small.render(button_text, True, (18, 18, 28))
        btn_text_rect = btn_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        screen.blit(btn_text, btn_text_rect)

        # Store clickable area
        self.clickable_areas[section_id] = pygame.Rect(button_x, button_y, button_width, button_height)

        # Store tooltip info
        self.tooltip_rects[section_id] = {
            "rect": pygame.Rect(button_x, button_y, button_width, button_height),
            "player": section_id + 1
        }

        # Clue content (shown when revealed)
        clue_y = button_y + button_height + 20
        if section.revealed:
            clue_box_height = height - (clue_y - y) - 10
            # Clue background with pixel art border
            pygame.draw.rect(screen, (50, 50, 70), pygame.Rect(x + 10, clue_y, width - 20, clue_box_height))
            pygame.draw.rect(screen, (90, 220, 140), pygame.Rect(x + 10, clue_y, width - 20, clue_box_height), 2)  # Green border

            # Display content based on type
            if section.clue.clue_type.value == "image":
                # Load and display image
                image = self._load_image(section.clue.content, width - 30, clue_box_height - 20)
                if image:
                    image_rect = image.get_rect(center=(x + width // 2, clue_y + clue_box_height // 2))
                    screen.blit(image, image_rect)

                    # Store image rect for click detection
                    self.image_clickable_areas[section_id] = {
                        "rect": image_rect,
                        "path": section.clue.content
                    }

                    # Add hint text that image is clickable
                    hint_text = self.font_tiny.render("Clique para ampliar", True, (90, 220, 140))  # Green
                    hint_rect = hint_text.get_rect(center=(x + width // 2, clue_y + clue_box_height - 15))
                    screen.blit(hint_text, hint_rect)
                else:
                    # Fallback text if image not found
                    error_text = self.font_tiny.render("Imagem não encontrada", True, (255, 170, 80))
                    error_rect = error_text.get_rect(center=(x + width // 2, clue_y + 20))
                    screen.blit(error_text, error_rect)
            elif section.clue.clue_type.value in {"sound", "audio"}:
                # Show sound indicator
                sound_text = self.font_normal.render("SOUND", True, (240, 190, 90))  # Tower window color
                sound_rect = sound_text.get_rect(center=(x + width // 2, clue_y + 20))
                screen.blit(sound_text, sound_rect)

                info_text = self.font_tiny.render("CLIQUE PARA OUVIR", True, (200, 200, 220))
                info_rect = info_text.get_rect(center=(x + width // 2, clue_y + 55))
                screen.blit(info_text, info_rect)
            else:
                # Text/Phrase clues with wrapping
                clue_text_lines = self._wrap_text(section.clue.content, self.font_tiny, width - 30)
                text_y = clue_y + 10
                for line in clue_text_lines:
                    text_surface = self.font_tiny.render(line, True, (200, 200, 220))
                    text_rect = text_surface.get_rect(topleft=(x + 15, text_y))
                    screen.blit(text_surface, text_rect)
                    text_y += 25

    def _wrap_text(self, text: str, font: pygame.font.Font, max_width: int) -> List[str]:
        """Wrap text to fit within a maximum width.

        Args:
            text: Text to wrap
            font: Font to use
            max_width: Maximum width in pixels

        Returns:
            List of text lines
        """
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            text_width = font.size(test_line)[0]

            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.strip())

        return lines

    def _draw_guess_area(self, screen: pygame.Surface, game: BabelGame) -> None:
        """Draw the word guessing area.

        Args:
            screen: Pygame surface to draw on
            game: BabelGame instance
        """
        guess_y = 380
        pygame.draw.line(screen, (90, 190, 255), (50, guess_y), (WINDOW_WIDTH - 50, guess_y), 3)  # Accent color

        # Label
        label = self.font_normal.render("QUAL EH A PALAVRA?", True, (240, 190, 90))  # Tower window color
        label_rect = label.get_rect(center=(WINDOW_WIDTH // 2, guess_y + 30))
        screen.blit(label, label_rect)

        # Input box with pixel art border
        input_box_width = 400
        input_box_x = (WINDOW_WIDTH - input_box_width) // 2
        input_box_y = guess_y + 70
        pygame.draw.rect(screen, (50, 50, 70), pygame.Rect(input_box_x, input_box_y, input_box_width, 50))
        pygame.draw.rect(screen, (90, 220, 140), pygame.Rect(input_box_x, input_box_y, input_box_width, 50), 3)  # Green border

        # Input text
        guess_text = self.font_large.render(game.state.guess_input, True, (90, 220, 140))  # Green
        guess_rect = guess_text.get_rect(center=(WINDOW_WIDTH // 2, input_box_y + 25))
        screen.blit(guess_text, guess_rect)

        # Instructions
        instructions = self.font_tiny.render(
            "DIGITE E PRESSIONE ENTER | BACKSPACE PARA APAGAR",
            True,
            (150, 150, 180)
        )
        instructions_rect = instructions.get_rect(center=(WINDOW_WIDTH // 2, input_box_y + 65))
        screen.blit(instructions, instructions_rect)

    def _draw_message(self, screen: pygame.Surface, game: BabelGame) -> None:
        """Draw the game message.

        Args:
            screen: Pygame surface to draw on
            game: BabelGame instance
        """
        if not game.state.game_message:
            return

        message_y = WINDOW_HEIGHT - 60

        # Message background
        msg_color = {
            "success": (90, 220, 140),  # Green
            "error": (255, 170, 80),  # Orange
            "info": (90, 190, 255)  # Cyan
        }.get(game.state.message_type, (200, 200, 220))

        message_text = self.font_normal.render(game.state.game_message, True, msg_color)
        message_rect = message_text.get_rect(center=(WINDOW_WIDTH // 2, message_y))
        screen.blit(message_text, message_rect)

    def _draw_game_over_screen(self, screen: pygame.Surface, game: BabelGame) -> None:
        """Draw the game over overlay.

        Args:
            screen: Pygame surface to draw on
            game: BabelGame instance
        """
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Game over message with shadow
        game_over_shadow = self.font_title.render("FIM DE JOGO", True, (35, 30, 45))
        game_over_shadow_rect = game_over_shadow.get_rect(center=(WINDOW_WIDTH // 2 + 1, WINDOW_HEIGHT // 2 - 59))
        screen.blit(game_over_shadow, game_over_shadow_rect)

        game_over_text = self.font_title.render("FIM DE JOGO", True, (240, 190, 90))  # Tower window color
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        screen.blit(game_over_text, game_over_rect)

        # Score
        score_text = self.font_large.render(
            f"ACERTOS: {game.state.total_correct}/{len(game.state.rounds)}",
            True,
            (90, 220, 140)  # Green
        )
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        screen.blit(score_text, score_rect)

        # Instructions
        instructions = self.font_small.render(
            "R: JOGAR NOVAMENTE | ESC: SAIR",
            True,
            (200, 200, 220)
        )
        instructions_rect = instructions.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
        screen.blit(instructions, instructions_rect)

    def _draw_next_round_button(self, screen: pygame.Surface, game: BabelGame) -> None:
        """Draw the next round button in the bottom right corner.

        Args:
            screen: Pygame surface to draw on
            game: BabelGame instance
        """
        current_round = game.state.get_current_round_data()
        if current_round and current_round.guessed and not game.state.game_over:
            # Draw button in bottom right corner
            button_width = 200
            button_height = 60
            button_x = WINDOW_WIDTH - button_width - 20
            button_y = WINDOW_HEIGHT - button_height - 20

            # Button background with pixel art style border
            pygame.draw.rect(screen, (90, 220, 140), pygame.Rect(button_x, button_y, button_width, button_height))  # Green
            pygame.draw.rect(screen, WHITE, pygame.Rect(button_x, button_y, button_width, button_height), 4)  # Thick border

            # Button text
            button_text = self.font_small.render("PROXIMA", True, (18, 18, 28))
            button_text_rect = button_text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
            screen.blit(button_text, button_text_rect)

            # Store button position for click detection
            self.next_round_button = pygame.Rect(button_x, button_y, button_width, button_height)

    def _draw_tooltips(self, screen: pygame.Surface) -> None:
        """Draw tooltips when mouse hovers over clue buttons.

        Args:
            screen: Pygame surface to draw on
        """
        mouse_pos = pygame.mouse.get_pos()

        for section_id, tooltip_info in self.tooltip_rects.items():
            button_rect = tooltip_info["rect"]
            player_num = tooltip_info["player"]

            if button_rect.collidepoint(mouse_pos):
                # Draw tooltip
                tooltip_text = f"⚠️ Apenas Jogador {player_num} pode olhar!"
                tooltip_surface = self.font_small.render(tooltip_text, True, WHITE)

                # Tooltip background
                tooltip_padding = 10
                tooltip_bg_rect = tooltip_surface.get_rect()
                tooltip_bg_rect.inflate_ip(tooltip_padding * 2, tooltip_padding)
                tooltip_bg_rect.center = (button_rect.centerx, button_rect.bottom + 30)

                # Draw background
                pygame.draw.rect(screen, BAD_COLOR, tooltip_bg_rect)
                pygame.draw.rect(screen, WHITE, tooltip_bg_rect, 2)

                # Draw text
                tooltip_text_rect = tooltip_surface.get_rect(center=tooltip_bg_rect.center)
                screen.blit(tooltip_surface, tooltip_text_rect)

                # Draw arrow pointing to button (above the tooltip)
                arrow_points = [
                    (tooltip_bg_rect.centerx, tooltip_bg_rect.top),
                    (tooltip_bg_rect.centerx - 10, tooltip_bg_rect.top + 15),
                    (tooltip_bg_rect.centerx + 10, tooltip_bg_rect.top + 15),
                ]
                pygame.draw.polygon(screen, BAD_COLOR, arrow_points)

    def _load_image(self, image_path: str, max_width: int = 180, max_height: int = 120, keep_ratio: bool = False) -> Optional[pygame.Surface]:
        """Load and cache an image, scaled to fit.

        Args:
            image_path: Path to image file (relative to project root)
            max_width: Maximum width for the image
            max_height: Maximum height for the image
            keep_ratio: If True, maintain aspect ratio; if False, stretch to fill

        Returns:
            Scaled pygame Surface or None if image not found
        """
        cache_key = f"{image_path}_{max_width}_{max_height}_{keep_ratio}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        full_path = os.path.join(self.project_root, image_path)
        try:
            image = pygame.image.load(full_path)

            if keep_ratio:
                # Scale maintaining aspect ratio
                image.set_colorkey(None)
                image_width, image_height = image.get_size()
                aspect_ratio = image_width / image_height

                if image_width / max_width > image_height / max_height:
                    # Width is limiting factor
                    new_width = max_width
                    new_height = int(max_width / aspect_ratio)
                else:
                    # Height is limiting factor
                    new_height = max_height
                    new_width = int(max_height * aspect_ratio)

                image = pygame.transform.scale(image, (new_width, new_height))
            else:
                # Scale image to fit exactly
                image = pygame.transform.scale(image, (max_width, max_height))

            self.image_cache[cache_key] = image
            return image
        except (pygame.error, FileNotFoundError):
            print(f"Warning: Could not load image {full_path}")
            return None

    def _stop_sound(self) -> None:
        """Stop the currently playing sound."""
        if self.current_sound:
            self.current_sound.stop()

    def _play_sound(self, sound_path: str) -> None:
        """Play a sound file.

        Args:
            sound_path: Path to sound file (relative to project root)
        """
        # Stop any currently playing sound
        if self.current_sound:
            self.current_sound.stop()

        candidates = []
        if sound_path:
            candidates.append(sound_path)
            candidates.append(os.path.join("src", sound_path))
            candidates.append(os.path.join("src", "assets", sound_path))
            candidates.append(os.path.join(self.project_root, sound_path))
            candidates.append(os.path.join(self.project_root, "src", sound_path))
            candidates.append(os.path.join(self.project_root, "src", "assets", sound_path))

        for candidate in candidates:
            if os.path.exists(candidate):
                try:
                    self.current_sound = pygame.mixer.Sound(candidate)
                    self.current_sound.play()
                    return
                except (pygame.error, FileNotFoundError):
                    print(f"Warning: Could not load sound {candidate}")

        print(f"Warning: Could not find sound file for {sound_path}")
        self.current_sound = None

    def handle_click(self, game: BabelGame, pos: Tuple[int, int]) -> bool:
        """Handle mouse clicks on buttons.

        Args:
            game: BabelGame instance
            pos: Mouse position (x, y)

        Returns:
            True if next round button was clicked, False otherwise
        """
        # Check if modal close button was clicked
        if self.image_modal_open:
            if self.modal_close_button and self.modal_close_button.collidepoint(pos):
                self.image_modal_open = False
                self.modal_image_path = None
                self.modal_close_button = None
                return False

        # Check if image was clicked to open modal
        for section_id, image_info in self.image_clickable_areas.items():
            if image_info["rect"].collidepoint(pos):
                self.image_modal_open = True
                self.modal_image_path = image_info["path"]
                return False

        # Check if next round button was clicked
        if self.next_round_button and self.next_round_button.collidepoint(pos):
            return True

        # Check if clue buttons were clicked
        for section_id, button_rect in self.clickable_areas.items():
            if button_rect.collidepoint(pos):
                current_round = game.state.get_current_round_data()
                if current_round:
                    section = current_round.player_sections[section_id]
                    # If revealing a sound, play it
                    if not section.revealed and section.clue.clue_type.value in {"sound", "audio"}:
                        self._play_sound(section.clue.content)
                    # If hiding a sound, stop it
                    elif section.revealed and section.clue.clue_type.value in {"sound", "audio"}:
                        self._stop_sound()
                game.toggle_clue(section_id)
                break

        return False
