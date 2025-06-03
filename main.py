from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

import pygame
import pyaudio
import math
import random
import numpy as np
import threading


WINDOW_WIDTH, WINDOW_HEIGHT = 720, 720
AVATAR_SCALE = 0.9

BOUNCE_TIME = 0.4
BOUNCE_HEIGHT = 30

BLINK_DURATION = 0.15
BLINK_INTERVAL_MIN = 1.0
BLINK_INTERVAL_MAX = 4.0

STATES = [
    "idle",
    "talking",
    "idle_blink",
    "talking_blink",
]

VOICE_THRESHOLD = 200


class Audio:
    def __init__(self):
        self.running = True
        self.lock = threading.Lock()

        self.is_talking = False
        self.volume = 0

        self.audio = pyaudio.PyAudio()
        print('Using default input device:', self.audio.get_default_input_device_info()['name'])
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=64,
            input_device_index=None  # Use default
        )

        self.thread = threading.Thread(target=self.audio_loop)
        self.thread.daemon = True
        self.thread.start()
    
    def audio_loop(self):
        while self.running:
            data = self.stream.read(64, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            if len(audio_data) == 0:
                continue

            squared_data = audio_data.astype(np.float64) ** 2
            mean_squared = np.mean(squared_data)
            
            volume = 0
            if mean_squared > 0 and not np.isnan(mean_squared) and not np.isinf(mean_squared):
                volume = np.sqrt(mean_squared)
            
            self.volume = volume

            with self.lock:
                self.is_talking = volume > VOICE_THRESHOLD
        
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
    
    def get_data(self):
        with self.lock:
            return self.is_talking, self.volume

    def stop(self):
        with self.lock:
            self.running = False


class Avatar:
    def __init__(self):
        self.x = (WINDOW_WIDTH - WINDOW_WIDTH * AVATAR_SCALE) // 2
        self.y = (WINDOW_HEIGHT - WINDOW_HEIGHT * AVATAR_SCALE)

        self.images = {}
        for state in STATES:
            self.images[state] = pygame.image.load(f"images/{state}.png")
            self.images[state] = pygame.transform.smoothscale(self.images[state], (WINDOW_WIDTH * AVATAR_SCALE, WINDOW_HEIGHT * AVATAR_SCALE))

        self.talking = False
        self.blinking = False

        self.bounce_timer = 0
        self.bounce_y = 0

        self.blink_timer = 0
        self.blink_interval = random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)

        self.audio = Audio()
        self.volume = 0

    def update(self, delta_time):
        self.bounce_y = 0
        if self.bounce_timer > 0:
            self.bounce_timer -= delta_time

            bounce_progress = (BOUNCE_TIME - self.bounce_timer) / BOUNCE_TIME
            self.bounce_y = -BOUNCE_HEIGHT * math.sin(bounce_progress * math.pi) * (1 - bounce_progress)

        if self.blinking:
            self.blink_timer += delta_time
            if self.blink_timer >= BLINK_DURATION:
                self.blink_timer = 0
                self.blinking = False

        if not self.blinking:
            self.blink_timer += delta_time
            if self.blink_timer >= self.blink_interval:
                self.blink_timer = 0
                self.blink_interval = random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
                self.blinking = True
        
        talking, volume = self.audio.get_data()

        if talking != self.talking and not self.talking:
            self.bounce_timer = BOUNCE_TIME
        
        self.talking = talking
        self.volume = volume

    def draw(self, screen):
        base_state = ''
        if self.talking:
            base_state = 'talking'
        else:
            base_state = 'idle'

        if self.blinking:
            base_state += '_blink'

        screen.blit(self.images[base_state], (self.x, self.y + self.bounce_y))
        self.draw_ui(screen)
    
    def draw_ui(self, screen):
        font = pygame.font.Font(None, 36)

        state = f"Talking: {self.talking}, Blinking: {self.blinking}"
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
                    avatar.bounce_timer = BOUNCE_TIME
    
        new_ticks = pygame.time.get_ticks()
        delta_time = (new_ticks - ticks) / 1000
        ticks = new_ticks

        avatar.update(delta_time)

        screen.fill((0, 188, 0))

        avatar.draw(screen)

        pygame.display.flip()