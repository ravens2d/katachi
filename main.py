from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame
import pyaudio
import numpy as np
import threading

from transforms import BounceController, BlinkController
from audio import AudioController, VOICE_THRESHOLD


WINDOW_WIDTH, WINDOW_HEIGHT = 720, 720
AVATAR_SCALE = 0.9

STATES = [
    "idle",
    "talking",
    "idle_blink",
    "talking_blink",
]

class Avatar:
    def __init__(self):
        self.x = (WINDOW_WIDTH - WINDOW_WIDTH * AVATAR_SCALE) // 2
        self.y = (WINDOW_HEIGHT - WINDOW_HEIGHT * AVATAR_SCALE)

        self.images = {}
        for state in STATES:
            self.images[state] = pygame.image.load(f"images/{state}.png")
            self.images[state] = pygame.transform.smoothscale(self.images[state], (WINDOW_WIDTH * AVATAR_SCALE, WINDOW_HEIGHT * AVATAR_SCALE))

        self.bounce = BounceController()
        self.blink = BlinkController()

        self.audio = AudioController()
        self.talking = False
        self.volume = 0

    def update(self, delta_time):
        self.bounce.update(delta_time)
        self.blink.update(delta_time)

        talking, volume = self.audio.get_data()
        if talking != self.talking and not self.talking:
            self.bounce.trigger()

        self.talking = talking
        self.volume = volume

    def draw(self, screen):
        base_state = ''
        if self.talking:
            base_state = 'talking'
        else:
            base_state = 'idle'

        if self.blink.get_blinking():
            base_state += '_blink'

        bounce_x, bounce_y = self.bounce.get_transform()
        screen.blit(self.images[base_state], (self.x + bounce_x, self.y + bounce_y))
        self.draw_ui(screen)
    
    def draw_ui(self, screen):
        font = pygame.font.Font(None, 36)

        state = f"Talking: {self.talking}, Blinking: {self.blink.get_blinking()}"
        text_surface = font.render(state, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))

        pygame.draw.rect(screen, (100, 100, 100), (10, 40, 300, 20))
        pygame.draw.rect(screen, (0, 255, 0), (10, 40, min(self.volume, 1000) / 1000 * 300, 20))
        pygame.draw.line(screen, (255, 255, 255), (VOICE_THRESHOLD / 1000 * 300, 40), (VOICE_THRESHOLD / 1000 * 300, 60), 2)

    def stop(self):
        self.audio.stop()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Katachi")

    clock = pygame.time.Clock()
    ticks = 0

    avatar = Avatar()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                avatar.stop()
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    avatar.bounce.trigger()
    
        new_ticks = pygame.time.get_ticks()
        delta_time = (new_ticks - ticks) / 1000
        ticks = new_ticks

        avatar.update(delta_time)

        screen.fill((0, 188, 0))
        avatar.draw(screen)
        pygame.display.flip()