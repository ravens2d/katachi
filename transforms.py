import math
import random


BOUNCE_TIME = 0.4
BOUNCE_HEIGHT = 30

BLINK_DURATION = 0.15
BLINK_INTERVAL_MIN = 1.0
BLINK_INTERVAL_MAX = 4.0

BREATHING_HEIGHT = 10
BREATHING_SPEED = 0.5


class BounceController:
    def __init__(self):
        self.timer = 0
        self.x = 0
        self.y = 0

    def trigger(self):
        self.timer = BOUNCE_TIME

    def update(self, delta_time):
        self.timer -= delta_time
        if self.timer < 0:
            self.timer = 0

    def get_transform(self) -> tuple[float, float]:
        progress = (BOUNCE_TIME - self.timer) / BOUNCE_TIME
        return 0, -BOUNCE_HEIGHT * math.sin(progress * math.pi) * (1 - progress)


class BlinkController:
    def __init__(self):
        self.timer = random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
        self.duration_timer = BLINK_DURATION
        self.blinking = False

    def update(self, delta_time):
        if self.blinking:
            self.duration_timer -= delta_time
            if self.duration_timer < 0:
                self.blinking = False
        else:
            self.timer -= delta_time
            if self.timer < 0:
                self.timer = random.uniform(BLINK_INTERVAL_MIN, BLINK_INTERVAL_MAX)
                self.duration_timer = BLINK_DURATION
                self.blinking = True

    def get_blinking(self) -> bool:
        return self.blinking
    

class BreathingController:
    def __init__(self):
        self.timer = 0
        self.x = 0
        self.y = 0

    def update(self, delta_time):
        self.timer += delta_time
        self.y = math.sin(self.timer * BREATHING_SPEED * math.pi) * BREATHING_HEIGHT

    def get_transform(self) -> tuple[float, float]:
        return self.x, self.y
