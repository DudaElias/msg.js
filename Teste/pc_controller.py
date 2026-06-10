"""Pygame reaction game that sends simple serial commands to a Raspberry Pi Pico.

Usage:
    python pc_controller.py COM5

Install dependencies first:
    pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from dataclasses import dataclass

import pygame
import serial
from serial.tools import list_ports


WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
TARGET_RADIUS = 36
TARGET_LIFETIME_SECONDS = 1.0
GAME_DURATION_SECONDS = 30
TARGET_SCORE = 10
BACKGROUND_COLOR = (18, 18, 28)
PANEL_COLOR = (34, 34, 48)
TEXT_COLOR = (240, 240, 245)
ACCENT_COLOR = (90, 190, 255)
TARGET_COLOR = (255, 90, 90)
GOOD_COLOR = (90, 220, 140)
BAD_COLOR = (255, 170, 80)


@dataclass
class Target:
    x: int
    y: int
    expires_at: float


class PicoLink:
    def __init__(self, port: str | None, baud: int) -> None:
        self.connection = None
        if port:
            try:
                self.connection = serial.Serial(port, baud, timeout=0.05)
                time.sleep(2)
            except serial.SerialException as exc:
                print(f"Could not open {port}: {exc}", file=sys.stderr)
                self.connection = None

    def send(self, command: str) -> None:
        if self.connection is None:
            return
        try:
            self.connection.write((command + "\n").encode())
        except serial.SerialException:
            self.connection = None

    def read_messages(self) -> list[str]:
        messages: list[str] = []
        if self.connection is None:
            return messages

        try:
            while self.connection.in_waiting:
                message = self.connection.readline().decode(errors="replace").strip()
                if message:
                    messages.append(message)
        except serial.SerialException:
            self.connection = None

        return messages

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None


class ReactionGame:
    def __init__(self, link: PicoLink) -> None:
        self.link = link
        self.score = 0
        self.misses = 0
        self.game_over = False
        self.start_time = time.time()
        self.target = self.spawn_target()
        self.flash_message = ""
        self.flash_until = 0.0

    def spawn_target(self) -> Target:
        x = random.randint(TARGET_RADIUS + 20, WINDOW_WIDTH - TARGET_RADIUS - 20)
        y = random.randint(130, WINDOW_HEIGHT - TARGET_RADIUS - 20)
        expires_at = time.time() + TARGET_LIFETIME_SECONDS
        return Target(x=x, y=y, expires_at=expires_at)

    def reset(self) -> None:
        self.score = 0
        self.misses = 0
        self.game_over = False
        self.start_time = time.time()
        self.target = self.spawn_target()
        self.flash_message = ""
        self.flash_until = 0.0
        self.link.send("READY")

    def show_flash(self, message: str, color: tuple[int, int, int]) -> None:
        self.flash_message = message
        self.flash_until = time.time() + 0.7
        self.flash_color = color

    def handle_click(self, position: tuple[int, int]) -> None:
        if self.game_over:
            return

        distance_x = position[0] - self.target.x
        distance_y = position[1] - self.target.y
        if distance_x * distance_x + distance_y * distance_y <= TARGET_RADIUS * TARGET_RADIUS:
            self.score += 1
            self.link.send("HIT")
            self.link.send(f"SCORE {self.score}")
            self.show_flash("HIT", GOOD_COLOR)
            self.target = self.spawn_target()
            if self.score >= TARGET_SCORE:
                self.game_over = True
                self.link.send("GAME_OVER")
                self.show_flash("YOU WIN", ACCENT_COLOR)

    def update(self) -> None:
        if self.game_over:
            return

        now = time.time()
        if now >= self.target.expires_at:
            self.misses += 1
            self.link.send("MISS")
            self.show_flash("MISS", BAD_COLOR)
            self.target = self.spawn_target()

        elapsed = now - self.start_time
        if elapsed >= GAME_DURATION_SECONDS:
            self.game_over = True
            self.link.send("GAME_OVER")
            self.show_flash("TIME UP", BAD_COLOR)

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, small_font: pygame.font.Font) -> None:
        screen.fill(BACKGROUND_COLOR)

        pygame.draw.rect(screen, PANEL_COLOR, pygame.Rect(0, 0, WINDOW_WIDTH, 100), border_radius=0)
        pygame.draw.circle(screen, TARGET_COLOR, (self.target.x, self.target.y), TARGET_RADIUS)
        pygame.draw.circle(screen, (255, 255, 255), (self.target.x, self.target.y), TARGET_RADIUS, 3)

        title = font.render("Pico Reaction Game", True, TEXT_COLOR)
        score_text = small_font.render(f"Score: {self.score} / {TARGET_SCORE}", True, TEXT_COLOR)
        miss_text = small_font.render(f"Misses: {self.misses}", True, TEXT_COLOR)
        time_left = max(0, GAME_DURATION_SECONDS - int(time.time() - self.start_time))
        timer_text = small_font.render(f"Time: {time_left}s", True, TEXT_COLOR)
        help_text = small_font.render("Click the red target. Press R to restart. ESC to quit.", True, TEXT_COLOR)

        screen.blit(title, (24, 18))
        screen.blit(score_text, (24, 58))
        screen.blit(miss_text, (220, 58))
        screen.blit(timer_text, (360, 58))
        screen.blit(help_text, (24, WINDOW_HEIGHT - 36))

        if self.flash_message and time.time() <= self.flash_until:
            flash_surface = font.render(self.flash_message, True, self.flash_color)
            flash_rect = flash_surface.get_rect(center=(WINDOW_WIDTH // 2, 90))
            screen.blit(flash_surface, flash_rect)

        if self.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            if self.score >= TARGET_SCORE:
                message = "You won"
            elif time_left <= 0:
                message = "Time up"
            else:
                message = "Game over"

            game_over_text = font.render(message, True, TEXT_COLOR)
            detail_text = small_font.render(f"Final score: {self.score}", True, TEXT_COLOR)
            restart_text = small_font.render("Press R to play again", True, TEXT_COLOR)

            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
            detail_rect = detail_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 18))
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 52))
            screen.blit(game_over_text, game_over_rect)
            screen.blit(detail_text, detail_rect)
            screen.blit(restart_text, restart_rect)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pygame reaction game that sends serial commands to a Pico.")
    parser.add_argument("port", help="Serial port, for example COM5")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate")
    return parser.parse_args()


def print_available_ports() -> None:
    ports = [port.device for port in list_ports.comports()]
    if ports:
        print("Available serial ports:")
        for port in ports:
            print(f"  {port}")
    else:
        print("No serial ports were detected.")


def main() -> int:
    args = parse_args()
    pygame.init()
    pygame.display.set_caption("Pico Reaction Game")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 28)
    link = PicoLink(args.port, args.baud)
    if link.connection is None:
        print_available_ports()
        pygame.quit()
        return 1

    game = ReactionGame(link)
    game.reset()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    game.reset()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos)

        game.update()
        for message in link.read_messages():
            print(f"PICO: {message}")
        game.draw(screen, font, small_font)
        pygame.display.flip()
        clock.tick(60)

    link.send("GAME_OVER")
    link.close()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
