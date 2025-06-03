import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame

from transforms import BounceController, BlinkController, BreathingController, BREATHING_HEIGHT
from audio import AudioController, VOICE_THRESHOLD


WINDOW_WIDTH, WINDOW_HEIGHT = 720, 720
AVATAR_SCALE = 0.9

VOLUME_BAR_WIDTH = 500
VOLUME_BAR_HEIGHT = 20
VOLUME_MAX = 2000

STATES = [
    "idle",
    "talking",
    "idle_blink",
    "talking_blink",
]


class Avatar:
    def __init__(self):
        self.x = (WINDOW_WIDTH - WINDOW_WIDTH * AVATAR_SCALE) // 2
        self.y = (WINDOW_HEIGHT - WINDOW_HEIGHT * AVATAR_SCALE) - BREATHING_HEIGHT

        self.images = {}
        for state in STATES:
            self.images[state] = pygame.image.load(f"images/{state}.png")
            self.images[state] = pygame.transform.smoothscale(self.images[state], (WINDOW_WIDTH * AVATAR_SCALE, WINDOW_HEIGHT * AVATAR_SCALE))

        self.bounce = BounceController()
        self.blink = BlinkController()
        self.breathing = BreathingController()
        self.audio = AudioController()

    def update(self, delta_time):
        self.bounce.update(delta_time)
        self.blink.update(delta_time)
        self.breathing.update(delta_time)

        self.audio.update()
        if self.audio.talking and not self.audio.previous_talking:
            self.bounce.trigger()

    def draw(self, screen):
        base_state = ''
        if self.audio.talking:
            base_state = 'talking'
        else:
            base_state = 'idle'

        if self.blink.get_blinking():
            base_state += '_blink'

        bounce_x, bounce_y = self.bounce.get_transform()
        breathing_x, breathing_y = self.breathing.get_transform()
        screen.blit(self.images[base_state], (self.x + bounce_x + breathing_x, self.y + bounce_y + breathing_y))
        self.draw_ui(screen)
    
    def draw_ui(self, screen):
        bar_color = (0, 255, 0)
        if self.audio.talking:
            bar_color = (255, 0, 0)

        pygame.draw.rect(screen, (100, 100, 100), (10, 10, VOLUME_BAR_WIDTH, VOLUME_BAR_HEIGHT))
        pygame.draw.rect(screen, bar_color, (10, 10, min(self.audio.volume, VOLUME_MAX) / VOLUME_MAX * VOLUME_BAR_WIDTH, VOLUME_BAR_HEIGHT))
        pygame.draw.line(screen, (255, 255, 255), (self.audio.threshold / VOLUME_MAX * VOLUME_BAR_WIDTH + 10, 10), (self.audio.threshold / VOLUME_MAX * VOLUME_BAR_WIDTH + 10, 30), 2)
    
    def handle_volume_bar_click(self, mouse_pos):
        mouse_x, mouse_y = mouse_pos
        if 10 <= mouse_x <= 10 + VOLUME_BAR_WIDTH and 10 <= mouse_y <= 10 + VOLUME_BAR_HEIGHT:
            new_threshold = (mouse_x - 10) / VOLUME_BAR_WIDTH * VOLUME_MAX
            self.audio.threshold = new_threshold

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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # left
                    avatar.handle_volume_bar_click(event.pos)
    
        new_ticks = pygame.time.get_ticks()
        delta_time = (new_ticks - ticks) / 1000
        ticks = new_ticks

        avatar.update(delta_time)

        screen.fill((0, 188, 0))
        avatar.draw(screen)
        pygame.display.flip()