#!/usr/bin/env python3
"""
Fast recorder with whisper.cpp for quick transcription.
Optimized for short utterances with sub-second processing.
"""

import sys
import os
import time
import signal
import wave
import tempfile
import subprocess
import threading
import argparse

try:
    import pyaudio
    import numpy as np
    from pywhispercpp.model import Model
except ImportError as e:
    print(f"Missing dependency: {e}")
    sys.exit(1)


class FastRecorder:
    def __init__(self):
        self.recording = True
        self.frames = []
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.model = None
        self.should_stop = False
        
        # Preload whisper.cpp model (tiny for speed)
        print("Loading Whisper.cpp model...", flush=True)
        try:
            # Use tiny model for fastest processing
            self.model = Model('tiny', n_threads=4)
            print("Model ready!", flush=True)
        except Exception as e:
            print(f"Failed to load model: {e}", flush=True)
            # Fall back to base if tiny fails
            try:
                self.model = Model('base', n_threads=4)
                print("Using base model", flush=True)
            except:
                print("Could not load any model", flush=True)
                sys.exit(1)
        
        # Signal handler
        signal.signal(signal.SIGTERM, self.handle_stop)
        signal.signal(signal.SIGINT, self.handle_stop)
    
    def handle_stop(self, signum, frame):
        """Handle stop signal - set flag to stop recording."""
        print(f"\nStop signal received (signal {signum})", flush=True)
        self.should_stop = True
        self.recording = False
    
    def notify(self, message):
        """Send notification."""
        try:
            subprocess.run(
                ["notify-send", "LinuxST", message, "-t", "2000"],
                capture_output=True
            )
        except:
            pass
    
    def record(self, max_duration=60):
        """Record audio until stopped."""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=10,
                frames_per_buffer=CHUNK
            )
            
            print("Recording started - speak now!", flush=True)
            self.notify("Recording")
            
            start_time = time.time()
            
            # Recording loop
            while self.recording and not self.should_stop:
                elapsed = time.time() - start_time
                
                if elapsed >= max_duration:
                    print(f"\nMax duration reached ({max_duration}s)", flush=True)
                    break
                
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    self.frames.append(data)
                    
                    # Simple progress indicator
                    if int(elapsed) % 2 == 0:
                        sys.stdout.write(".")
                        sys.stdout.flush()
                        
                except:
                    break
            
            print(f"\nRecording stopped after {time.time() - start_time:.1f}s", flush=True)
            
            # Stop and close stream
            self.stream.stop_stream()
            self.stream.close()
            
            # Save audio
            if len(self.frames) > 5:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    filename = f.name
                
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(self.frames))
                
                print(f"Audio saved: {filename}", flush=True)
                return filename
                
        except Exception as e:
            print(f"Recording error: {e}", flush=True)
            return None
    
    def transcribe(self, audio_file):
        """Transcribe the audio file using whisper.cpp."""
        try:
            print("Starting transcription...", flush=True)
            self.notify("Transcribing")
            
            start_time = time.time()
            
            # Transcribe with whisper.cpp
            segments = self.model.transcribe(audio_file, language='en')
            
            # Combine all segments
            text = ""
            for segment in segments:
                text += segment.text + " "
            text = text.strip()
            
            transcription_time = time.time() - start_time
            print(f"Transcription took {transcription_time:.2f}s", flush=True)
            
            # Clean up
            try:
                os.unlink(audio_file)
            except:
                pass
            
            if text and text != "[BLANK_AUDIO]":
                print(f"Transcription: '{text}'", flush=True)
                return text
            else:
                print("No speech detected", flush=True)
                return None
                
        except Exception as e:
            print(f"Transcription error: {e}", flush=True)
            return None
    
    def copy_and_paste(self, text):
        """Copy to clipboard and paste."""
        print(f"Copying text: '{text[:50]}...'", flush=True)
        
        # First, save to file immediately
        try:
            with open("/tmp/linuxst_last_transcription.txt", "w") as f:
                f.write(text)
            print("Saved to /tmp/linuxst_last_transcription.txt", flush=True)
        except Exception as e:
            print(f"Failed to save file: {e}", flush=True)
        
        # Detect if we're on Wayland
        is_wayland = os.environ.get('WAYLAND_DISPLAY') is not None
        print(f"Display server: {'Wayland' if is_wayland else 'X11'}", flush=True)
        
        # Copy to clipboard
        clipboard_copied = False
        
        # Try simple echo pipe to wl-copy first
        try:
            result = subprocess.run(
                ["wl-copy"],
                input=text.encode(),
                capture_output=True,
                timeout=1
            )
            if result.returncode == 0:
                clipboard_copied = True
                print("Copied to clipboard via wl-copy", flush=True)
            else:
                print(f"wl-copy failed with code {result.returncode}", flush=True)
        except subprocess.TimeoutExpired:
            print("wl-copy timeout", flush=True)
        except FileNotFoundError:
            print("wl-copy not found", flush=True)
        except Exception as e:
            print(f"wl-copy error: {e}", flush=True)
        
        # Try xclip as fallback
        if not clipboard_copied:
            try:
                result = subprocess.run(["xclip", "-selection", "clipboard"], 
                                      input=text.encode(), capture_output=True, timeout=1)
                if result.returncode == 0:
                    clipboard_copied = True
                    print("Copied via xclip (X11)", flush=True)
            except FileNotFoundError:
                print("xclip not found", flush=True)
            except Exception as e:
                print(f"xclip error: {e}", flush=True)
        
        if clipboard_copied:
            print("Clipboard copy successful", flush=True)
        else:
            print("Failed to copy to clipboard", flush=True)
        
        # On Wayland, auto-paste triggers security warnings, so skip it
        # The text is already saved to file and clipboard (when possible)
        paste_success = False
        
        if not is_wayland:
            # Only attempt auto-paste on X11
            time.sleep(0.5)
            try:
                result = subprocess.run(["xdotool", "key", "ctrl+v"], 
                                      capture_output=True, timeout=1)
                if result.returncode == 0:
                    paste_success = True
                    print("Auto-pasted with xdotool", flush=True)
                else:
                    print(f"xdotool paste failed: {result.returncode}", flush=True)
            except Exception as e:
                print(f"Auto-paste error: {e}", flush=True)
        
        # Notify user
        if paste_success:
            self.notify("Pasted")
        elif clipboard_copied or os.path.exists("/tmp/linuxst_last_transcription.txt"):
            # On Wayland, always just notify about clipboard/file
            self.notify("Ready to paste (Ctrl+V)")
        else:
            self.notify("Saved to file")
    
    def run(self):
        """Main flow."""
        print("Starting recording flow...", flush=True)
        
        # Record
        audio_file = self.record(60)
        
        if not audio_file:
            print("No audio recorded", flush=True)
            return
        
        # Transcribe
        text = self.transcribe(audio_file)
        
        if text:
            # Output - copy and paste the text
            self.copy_and_paste(text)
            print(f"SUCCESS: {text}", flush=True)
        else:
            print("No transcription", flush=True)
            self.notify("No speech")
        
        print("Flow complete", flush=True)
    
    def cleanup(self):
        """Clean up."""
        if self.audio:
            self.audio.terminate()


def main():
    recorder = FastRecorder()
    try:
        recorder.run()
    finally:
        recorder.cleanup()
        print("Exiting cleanly", flush=True)


if __name__ == "__main__":
    main()