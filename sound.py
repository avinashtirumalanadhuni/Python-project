"""
Procedural sound synthesis engine for Pygame UI feedback without external audio assets.
"""

import io
import math
import struct
import wave
from typing import Callable, Optional
import pygame


def generate_wav_buffer(
    duration: float,
    freq_fn: Callable[[float, float], float],
    sample_rate: int = 44100,
    volume: float = 0.25,
    attack_ratio: float = 0.1,
    decay_ratio: float = 0.3,
) -> io.BytesIO:
    """Synthesizes a 16-bit mono PCM wave file into an in-memory BytesIO buffer."""
    num_samples = int(sample_rate * duration)
    buffer = io.BytesIO()

    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        raw_frames = bytearray()
        attack_len = duration * attack_ratio
        decay_len = duration * decay_ratio

        for i in range(num_samples):
            t = i / sample_rate
            freq = freq_fn(t, duration)

            # Amplitude envelope
            env = 1.0
            if t < attack_len and attack_len > 0:
                env = t / attack_len
            elif t > (duration - decay_len) and decay_len > 0:
                env = (duration - t) / decay_len
            env = max(0.0, min(1.0, env))

            # Sine wave sample
            sample_float = volume * env * 32767.0 * math.sin(2.0 * math.pi * freq * t)
            sample_int = int(max(-32768, min(32767, sample_float)))
            raw_frames.extend(struct.pack("<h", sample_int))

        wav_file.writeframes(raw_frames)

    buffer.seek(0)
    return buffer


class SoundEngine:
    """Manages synthesized sound effects and mute state."""

    def __init__(self):
        self.muted: bool = False
        self.initialized: bool = False
        self.sound_click: Optional[pygame.mixer.Sound] = None
        self.sound_toggle: Optional[pygame.mixer.Sound] = None
        self.sound_chime: Optional[pygame.mixer.Sound] = None
        self.sound_generate: Optional[pygame.mixer.Sound] = None

        self._init_mixer()

    def _init_mixer(self) -> None:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

            # Synthesize micro-click (0.025s)
            click_buf = generate_wav_buffer(
                0.025,
                lambda t, d: 1800 - 1000 * (t / d),
                volume=0.2,
                attack_ratio=0.05,
                decay_ratio=0.5,
            )
            self.sound_click = pygame.mixer.Sound(click_buf)

            # Synthesize toggle switch tone (0.04s)
            toggle_buf = generate_wav_buffer(
                0.04,
                lambda t, d: 650 + 400 * (t / d),
                volume=0.2,
                attack_ratio=0.1,
                decay_ratio=0.4,
            )
            self.sound_toggle = pygame.mixer.Sound(toggle_buf)

            # Synthesize pleasant chime for clipboard copy (0.22s)
            chime_buf = generate_wav_buffer(
                0.22,
                lambda t, d: 880 if t < 0.08 else 1320,
                volume=0.25,
                attack_ratio=0.05,
                decay_ratio=0.5,
            )
            self.sound_chime = pygame.mixer.Sound(chime_buf)

            # Synthesize generate whoosh / swoop (0.08s)
            gen_buf = generate_wav_buffer(
                0.08,
                lambda t, d: 450 + 650 * math.sin((t / d) * math.pi),
                volume=0.22,
                attack_ratio=0.15,
                decay_ratio=0.35,
            )
            self.sound_generate = pygame.mixer.Sound(gen_buf)

            self.initialized = True
        except Exception as e:
            print(f"[SoundEngine] Audio unavailable, operating in silent mode: {e}")
            self.initialized = False

    def toggle_mute(self) -> bool:
        self.muted = not self.muted
        return self.muted

    def play_click(self) -> None:
        if not self.muted and self.initialized and self.sound_click:
            try:
                self.sound_click.play()
            except Exception:
                pass

    def play_toggle(self) -> None:
        if not self.muted and self.initialized and self.sound_toggle:
            try:
                self.sound_toggle.play()
            except Exception:
                pass

    def play_chime(self) -> None:
        if not self.muted and self.initialized and self.sound_chime:
            try:
                self.sound_chime.play()
            except Exception:
                pass

    def play_generate(self) -> None:
        if not self.muted and self.initialized and self.sound_generate:
            try:
                self.sound_generate.play()
            except Exception:
                pass
