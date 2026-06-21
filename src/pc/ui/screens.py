"""Game screens (menu, instructions, etc)."""

import pygame

from .background import BackgroundRenderer
from ..utils.config import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    GOOD_COLOR,
    PANEL_COLOR,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    WHITE,
)


class StartScreen:
    """Start screen with instructions."""

    def __init__(self) -> None:
        """Initialize start screen."""
        # Pixel art style fonts (monospaced for retro feel)
        self.font_title = pygame.font.SysFont("courier", 64, bold=True)
        self.font_subtitle = pygame.font.SysFont("courier", 40, bold=True)
        self.font_normal = pygame.font.SysFont("courier", 28)
        self.font_small = pygame.font.SysFont("courier", 20)
        self.show_instructions = False
        self.start_button_rect = None
        self.instructions_button_rect = None
        self.background = BackgroundRenderer()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the start screen.

        Args:
            screen: Pygame surface to draw on
        """
        # Draw pixel art background
        self.background.draw(screen)

        if self.show_instructions:
            self._draw_instructions(screen)
        else:
            self._draw_menu(screen)

    def _draw_pixel_button(self, screen: pygame.Surface, rect: pygame.Rect, text: str,
                           color: tuple, text_color: tuple) -> None:
        """Draw a pixel art style button.

        Args:
            screen: Pygame surface to draw on
            rect: Button rectangle
            text: Button text
            color: Button color
            text_color: Text color
        """
        # Draw button with border (pixel art style)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, WHITE, rect, 4)  # Thick border for pixel art

        # Draw text
        text_surface = self.font_normal.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    def _draw_menu(self, screen: pygame.Surface) -> None:
        """Draw the main menu.

        Args:
            screen: Pygame surface to draw on
        """
        # Semi-transparent overlay for better text readability
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        # Title with pixel art style (double shadow)
        title_y = 60
        title = self.font_title.render("RISE OF BABEL", True, (240, 190, 90))  # Tower window color

        # Shadow effect (pixel art style - offset by 2 pixels)
        title_shadow = self.font_title.render("RISE OF BABEL", True, (35, 30, 45))
        title_shadow_rect = title_shadow.get_rect(center=(WINDOW_WIDTH // 2 + 2, title_y + 2))
        screen.blit(title_shadow, title_shadow_rect)

        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, title_y))
        screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_subtitle.render(
            "Um Jogo de Adivinhas",
            True,
            (140, 90, 100)  # Cloud color
        )
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, title_y + 70))
        screen.blit(subtitle, subtitle_rect)

        # Quick rules (compact layout)
        rules_y = 200
        rules = [
            "3 Jogadores | Pistas Diferentes",
            "Mostrar/Ocultar Estrategicamente",
            "Adivinhar Juntos a Palavra",
            "Acertos Acendem LEDs!",
        ]

        for i, rule in enumerate(rules):
            rule_text = self.font_small.render(rule, True, (200, 200, 220))
            rule_rect = rule_text.get_rect(center=(WINDOW_WIDTH // 2, rules_y + i * 40))
            screen.blit(rule_text, rule_rect)

        # Buttons area (more centered and spaced)
        button_y = 430
        button_width = 220
        button_height = 70

        # Start button (green - GOOD_COLOR)
        self.start_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 - button_width - 30, button_y, button_width, button_height
        )
        self._draw_pixel_button(screen, self.start_button_rect, "COMEÇAR", (90, 220, 140), (18, 18, 28))

        # Instructions button (orange - from tower color)
        self.instructions_button_rect = pygame.Rect(
            WINDOW_WIDTH // 2 + 30, button_y, button_width, button_height
        )
        self._draw_pixel_button(screen, self.instructions_button_rect, "INSTRUÇÕES", (240, 190, 90), (18, 18, 28))

        # Footer (simplified)
        footer = self.font_small.render(
            "SPACE: Começar | I: Instruções | ESC: Sair",
            True,
            (150, 150, 180)
        )
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        screen.blit(footer, footer_rect)

    def _draw_instructions(self, screen: pygame.Surface) -> None:
        """Draw the instructions screen.

        Args:
            screen: Pygame surface to draw on
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # Header with pixel art style
        header_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 70)
        pygame.draw.rect(screen, (35, 30, 45), header_rect)  # Tower shadow color
        pygame.draw.rect(screen, (240, 190, 90), header_rect, 3)  # Tower window color border

        title = self.font_subtitle.render("INSTRUÇÕES", True, (240, 190, 90))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 35))
        screen.blit(title, title_rect)

        # Instructions content
        instructions = [
            ("📋 OBJETIVO", "Adivinhe a palavra baseado nas pistas dos 3 jogadores"),
            ("", ""),
            ("👥 RODADAS", "Cada rodada tem 3 jogadores com pistas diferentes"),
            ("", ""),
            ("🔊 TIPOS DE PISTA", ""),
            ("   🔊 Som", "Descrição de um som relacionado à palavra"),
            ("   💬 Frase", "Uma frase que fornece uma dica"),
            ("   👆 Tato", "Como a coisa se sente ao tocar"),
            ("   🖼️ Imagem", "Como a coisa se parece visualmente"),
            ("", ""),
            ("🎮 COMO JOGAR", ""),
            ("   1. Leia as pistas de cada jogador", ""),
            ("   2. Clique nos botões para mostrar/ocultar", ""),
            ("   3. Quando pronto, digite sua resposta", ""),
            ("   4. Pressione ENTER para enviar", ""),
            ("", ""),
            ("⌨️ CONTROLES", ""),
            ("   A-Z: Digitar letras", ""),
            ("   ENTER: Enviar palpite", ""),
            ("   BACKSPACE: Apagar último caractere", ""),
            ("   DELETE: Limpar tudo", ""),
            ("   N: Próxima rodada (depois de acerto)", ""),
            ("   R: Reiniciar jogo (no fim)", ""),
            ("", ""),
            ("💡 DICA", "Trabalhe em equipe! Comuniquem-se enquanto revelam pistas"),
        ]

        content_y = 100
        for title_text, desc_text in instructions:
            if title_text:
                if title_text.startswith("   "):
                    # Sub-item
                    text = self.font_small.render(title_text + (" " + desc_text if desc_text else ""), True, (200, 200, 220))
                elif title_text[0].isdigit() or title_text.startswith("   "):
                    # Regular item
                    text = self.font_small.render(title_text + (" - " + desc_text if desc_text else ""), True, (200, 200, 220))
                else:
                    # Section header
                    text = self.font_normal.render(title_text, True, (90, 220, 140))  # Green
            else:
                text = self.font_small.render("", True, (200, 200, 220))

            text_rect = text.get_rect(topleft=(60, content_y))
            screen.blit(text, text_rect)
            content_y += 30

        # Footer
        footer = self.font_small.render(
            "SPACE: Começar | ESC: Voltar",
            True,
            (150, 150, 180)
        )
        footer_rect = footer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
        screen.blit(footer, footer_rect)

    def handle_input(self) -> tuple[bool, str]:
        """Handle input on start screen.

        Returns:
            Tuple of (continue_running, action) where action is 'start', 'quit', or 'wait'
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.show_instructions:
                        self.show_instructions = False
                    else:
                        return False, "quit"
                elif event.key == pygame.K_SPACE:
                    if self.show_instructions:
                        return True, "start"
                    else:
                        return True, "start"
                elif event.key == pygame.K_i:
                    self.show_instructions = not self.show_instructions
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check if clicking on buttons in menu
                    if not self.show_instructions:
                        if self.start_button_rect and self.start_button_rect.collidepoint(event.pos):
                            return True, "start"
                        elif self.instructions_button_rect and self.instructions_button_rect.collidepoint(event.pos):
                            self.show_instructions = True
                    else:
                        # In instructions screen, click to go back or space to start
                        # Can add back button here if needed
                        pass

        return True, "wait"
