import threading
import pyaudio
import numpy as np


VOICE_THRESHOLD = 200
BUFFER_SIZE = 32


class AudioController:
    def __init__(self):
        self.running = True

        self.talking = False
        self.volume = 0

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=BUFFER_SIZE,
            input_device_index=None  # Use default
        )

        self.thread = threading.Thread(target=self.loop)
        self.thread.daemon = True
        self.thread.start()

    def loop(self):
        while self.running:
            data = self.stream.read(BUFFER_SIZE, exception_on_overflow=False)
            audio_data = np.frombuffer(data, dtype=np.int16)

            if len(audio_data) == 0:
                continue

            squared_data = audio_data.astype(np.float64) ** 2
            mean_squared = np.mean(squared_data)
            
            if mean_squared > 0 and not np.isnan(mean_squared) and not np.isinf(mean_squared):
                self.volume = np.sqrt(mean_squared)
            
            self.talking = self.volume > VOICE_THRESHOLD
    
    def get_data(self):
        return self.talking, self.volume
    
    def stop(self):
        self.running = False
        self.thread.join()
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()