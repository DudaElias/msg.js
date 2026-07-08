"""Background renderer for Rise of Babel - Pixel Art style."""

import pygame

from ..utils.config import WINDOW_HEIGHT, WINDOW_WIDTH

# Resolução "Pixel Art" (Baixa resolução para dar o efeito)
VIRTUAL_WIDTH = 320
VIRTUAL_HEIGHT = 240

# Paleta de Cores (Estilo Retro/Dusk)
COLOR_SKY_TOP = (25, 20, 46)
COLOR_SKY_MID = (70, 45, 80)
COLOR_SKY_BOT = (190, 100, 75)

COLOR_MOUNTAIN = (45, 35, 55)
COLOR_TOWER_SHADOW = (35, 30, 45)
COLOR_TOWER_BODY = (65, 50, 65)
COLOR_TOWER_LIGHT = (95, 75, 85)
COLOR_WINDOW = (240, 190, 90)
COLOR_CLOUD = (140, 90, 100)


class BackgroundRenderer:
    """Renders a pixel art background of the Tower of Babel."""

    def __init__(self) -> None:
        """Initialize the background renderer."""
        self.canvas = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.fade_alpha = 0

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the background on the given screen.

        Args:
            screen: Pygame surface to draw on
        """
        self._draw_sky_gradient()
        self._draw_clouds()
        self._draw_mountains()
        self._draw_tower()

        # Scale the virtual canvas to window size and blit it with a slower, softer fade-in effect
        scaled_surface = pygame.transform.scale(self.canvas, (WINDOW_WIDTH, WINDOW_HEIGHT))
        if self.fade_alpha < 255:
            self.fade_alpha = min(255, self.fade_alpha + 4)
        if self.fade_alpha < 255:
            scaled_surface.set_alpha(self.fade_alpha)
        else:
            scaled_surface.set_alpha(255)
        screen.blit(scaled_surface, (0, 0))

    def _draw_sky_gradient(self) -> None:
        """Draw the gradient sky."""
        for y in range(VIRTUAL_HEIGHT):
            # Interpolação simples de cores para o gradiente
            if y < VIRTUAL_HEIGHT * 0.5:
                t = y / (VIRTUAL_HEIGHT * 0.5)
                r = int(COLOR_SKY_TOP[0] + t * (COLOR_SKY_MID[0] - COLOR_SKY_TOP[0]))
                g = int(COLOR_SKY_TOP[1] + t * (COLOR_SKY_MID[1] - COLOR_SKY_TOP[1]))
                b = int(COLOR_SKY_TOP[2] + t * (COLOR_SKY_MID[2] - COLOR_SKY_TOP[2]))
            else:
                t = (y - VIRTUAL_HEIGHT * 0.5) / (VIRTUAL_HEIGHT * 0.5)
                r = int(COLOR_SKY_MID[0] + t * (COLOR_SKY_BOT[0] - COLOR_SKY_MID[0]))
                g = int(COLOR_SKY_MID[1] + t * (COLOR_SKY_BOT[1] - COLOR_SKY_MID[1]))
                b = int(COLOR_SKY_MID[2] + t * (COLOR_SKY_BOT[2] - COLOR_SKY_MID[2]))
            pygame.draw.line(self.canvas, (r, g, b), (0, y), (VIRTUAL_WIDTH, y))

    def _draw_clouds(self) -> None:
        """Draw distant clouds."""
        cloud_rects = [
            pygame.Rect(20, 120, 80, 15),
            pygame.Rect(40, 115, 50, 10),
            pygame.Rect(200, 80, 100, 12),
            pygame.Rect(230, 75, 50, 10),
        ]
        for rect in cloud_rects:
            pygame.draw.rect(self.canvas, COLOR_CLOUD, rect)

    def _draw_mountains(self) -> None:
        """Draw mountains in the background."""
        mountain_points = [
            (0, 180),
            (60, 140),
            (120, 170),
            (180, 135),
            (260, 180),
            (320, 150),
            (320, 240),
            (0, 240),
        ]
        pygame.draw.polygon(self.canvas, COLOR_MOUNTAIN, mountain_points)

    def _draw_tower(self) -> None:
        """Draw the Tower of Babel."""
        # Parâmetros da torre
        base_y = VIRTUAL_HEIGHT - 20
        tier_height = 22
        total_tiers = 8
        start_width = 110

        # Chão/Base da torre
        pygame.draw.rect(self.canvas, COLOR_TOWER_SHADOW, (0, base_y, VIRTUAL_WIDTH, 20))

        for i in range(total_tiers):
            # Reduz a largura conforme sobe
            width = start_width - (i * 10)
            height = tier_height
            x = (VIRTUAL_WIDTH - width) // 2
            y = base_y - (i * height) - height

            # Corpo principal do andar (Sombra e Luz)
            pygame.draw.rect(
                self.canvas, COLOR_TOWER_SHADOW, (x, y, width // 2, height)
            )  # Lado esquerdo (Sombra)
            pygame.draw.rect(
                self.canvas, COLOR_TOWER_BODY, (x + width // 2, y, width // 2, height)
            )  # Lado direito

            # Detalhe de borda/relevo para parecer uma espiral ou andares definidos
            pygame.draw.rect(self.canvas, COLOR_TOWER_LIGHT, (x, y, width, 3))

        # Nuvem envolvendo o topo da Torre
        # Dando aquele efeito mitológico de que ela toca os céus
        top_y = base_y - (total_tiers * tier_height)
        pygame.draw.rect(self.canvas, COLOR_CLOUD, ((VIRTUAL_WIDTH // 2) - 40, top_y + 10, 80, 8))
        pygame.draw.rect(self.canvas, COLOR_CLOUD, ((VIRTUAL_WIDTH // 2) - 25, top_y + 5, 50, 6))
