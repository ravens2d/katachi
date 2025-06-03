import pyaudio
import struct
import math


VOICE_THRESHOLD = 200
BUFFER_SIZE = 1024


class AudioController:
    def __init__(self):
        self.talking = False
        self.volume = 0
        self.threshold = VOICE_THRESHOLD

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=BUFFER_SIZE,
            input_device_index=None  # Use default
        )

    def update(self):
        available_frames = self.stream.get_read_available()
        if available_frames > 0:
            data = self.stream.read(available_frames, exception_on_overflow=False)
            if len(data) > 0:
                audio_data = struct.unpack(f'{len(data)//2}h', data)

                sum_squared = sum(sample * sample for sample in audio_data)
                mean_squared = sum_squared / len(audio_data)                
                if mean_squared > 0:
                    self.volume = math.sqrt(mean_squared)
                
                self.talking = self.volume > self.threshold
    
    def set_threshold(self, new_threshold):
        self.threshold = new_threshold
    
    def get_data(self):
        return self.talking, self.volume
    
    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()