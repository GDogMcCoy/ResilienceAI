"""
ResilienceAI - Voice Interface
Speech-to-text and text-to-speech integration for hands-free interaction.

File: src/nl_interface/voice_interface.py
"""

import io
import tempfile
from typing import Optional, BinaryIO, Callable
from dataclasses import dataclass
from pathlib import Path

# Optional imports for voice processing
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False


@dataclass
class VoiceConfig:
    """Configuration for voice interface."""
    stt_engine: str = "google"  # google, whisper, azure
    tts_engine: str = "gtts"    # gtts, pyttsx3, azure
    language: str = "en-US"
    speech_rate: int = 150      # words per minute
    voice_gender: str = "neutral"


@dataclass
class TranscriptionResult:
    """Result of speech-to-text transcription."""
    text: str
    confidence: float
    language: str
    is_final: bool = True
    alternatives: list = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class VoiceInterface:
    """
    Voice interface for hands-free interaction with ResilienceAI.
    
    Features:
    - Speech-to-text (multiple engines)
    - Text-to-speech
    - Wake word detection
    - Voice activity detection
    - Audio playback
    """
    
    # Wake words for activating voice interface
    WAKE_WORDS = ["resilience", "resilience ai", "hey resilience", "ok resilience"]
    
    def __init__(self, config: Optional[VoiceConfig] = None):
        """Initialize voice interface."""
        self.config = config or VoiceConfig()
        self.recognizer = None
        self.microphone = None
        self._is_listening = False
        self._wake_word_callback: Optional[Callable] = None
        
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
    
    def listen_for_wake_word(
        self,
        callback: Callable,
        timeout: Optional[int] = None
    ):
        """Start listening for wake word."""
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise RuntimeError("Speech recognition not available")
        
        self._wake_word_callback = callback
        self._is_listening = True
        
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
            while self._is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio).lower()
                    
                    if any(wake in text for wake in self.WAKE_WORDS):
                        callback()
                        return
                        
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    print("Speech recognition service unavailable")
                    break
    
    def transcribe(
        self,
        audio_source: Optional[BinaryIO] = None,
        duration: Optional[int] = None
    ) -> TranscriptionResult:
        """Transcribe speech to text."""
        if not SPEECH_RECOGNITION_AVAILABLE:
            raise RuntimeError("Speech recognition not available")
        
        if audio_source:
            with sr.AudioFile(audio_source) as source:
                audio = self.recognizer.record(source)
        else:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, phrase_time_limit=duration)
        
        if self.config.stt_engine == "google":
            return self._transcribe_google(audio)
        else:
            return self._transcribe_google(audio)
    
    def _transcribe_google(self, audio) -> TranscriptionResult:
        """Transcribe using Google Speech Recognition."""
        try:
            text = self.recognizer.recognize_google(
                audio,
                language=self.config.language
            )
            return TranscriptionResult(
                text=text,
                confidence=0.9,
                language=self.config.language
            )
        except sr.UnknownValueError:
            return TranscriptionResult(
                text="",
                confidence=0.0,
                language=self.config.language,
                error="Could not understand audio"
            )
        except sr.RequestError as e:
            return TranscriptionResult(
                text="",
                confidence=0.0,
                language=self.config.language,
                error=str(e)
            )
    
    def speak(
        self,
        text: str,
        output_file: Optional[str] = None,
        play_immediately: bool = True
    ) -> Optional[str]:
        """Convert text to speech."""
        if not GTTS_AVAILABLE:
            raise RuntimeError("Text-to-speech not available")
        
        tts = gTTS(text=text, lang=self.config.language[:2], slow=False)
        
        if output_file:
            audio_path = output_file
        else:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                audio_path = f.name
        
        tts.save(audio_path)
        
        if play_immediately and PYGAME_AVAILABLE:
            self._play_audio(audio_path)
        
        return audio_path
    
    def _play_audio(self, audio_path: str):
        """Play audio file."""
        if not PYGAME_AVAILABLE:
            return
        
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    
    def stop_listening(self):
        """Stop wake word detection."""
        self._is_listening = False
    
    def calibrate_microphone(self, duration: int = 2):
        """Calibrate microphone for ambient noise."""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return
        
        with sr.Microphone() as source:
            print(f"Calibrating for ambient noise... ({duration}s)")
            self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print(f"Energy threshold set to {self.recognizer.energy_threshold}")


class StreamlitVoiceComponent:
    """Streamlit component for voice interface."""
    
    def __init__(self, voice_interface: VoiceInterface):
        self.voice = voice_interface
    
    def render(self, key: str = "voice_interface"):
        """Render voice interface in Streamlit."""
        import streamlit as st
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("Mic", key=f"{key}_mic"):
                with st.spinner("Listening..."):
                    result = self.voice.transcribe(duration=10)
                    if result.text:
                        st.session_state[f"{key}_transcription"] = result.text
                        st.success(f"Heard: {result.text}")
                    else:
                        st.error("Could not understand")
        
        with col2:
            if f"{key}_transcription" in st.session_state:
                st.text_input(
                    "Transcription",
                    value=st.session_state[f"{key}_transcription"],
                    key=f"{key}_input"
                )
