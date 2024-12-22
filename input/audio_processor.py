import numpy as np
import webrtcvad
from collections import deque
from typing import Optional

class AudioProcessor:
    def __init__(self, sample_rate=16000, frame_duration=30):
        self.vad = webrtcvad.Vad(3)  # Aggressiveness level 3
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int(sample_rate * frame_duration / 1000)
        self.buffer = deque(maxlen=50)  # About 1.5 seconds of audio
        
    def process_frame(self, frame_data: bytes) -> Optional[bytes]:
        is_speech = self.vad.is_speech(frame_data, self.sample_rate)
        
        if is_speech:
            self.buffer.append(frame_data)
            if len(self.buffer) >= self.buffer.maxlen:
                return self.get_audio_segment()
        elif len(self.buffer) > 0:
            return self.get_audio_segment()
            
        return None
        
    def get_audio_segment(self) -> bytes:
        audio_data = b''.join(self.buffer)
        self.buffer.clear()
        return audio_data
