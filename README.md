# LinuxST - Fast Speech-to-Text for Linux

A lightweight, blazing-fast speech-to-text tool for Linux that records audio, transcribes it using Whisper.cpp, and automatically pastes the text at your cursor position.

## Features

- **Simple Toggle**: Start/stop recording with a single keybind (Super+R by default)
- **Ultra-Fast Transcription**: Uses Whisper.cpp for ~0.3 second transcription (10x faster than original Whisper)
- **Auto-Paste**: Automatically types the transcribed text at your cursor position (X11) or copies to clipboard (Wayland)
- **Minimal Notifications**: Clean, simple feedback ("Recording", "Transcribing", "Ready to paste")
- **Works on Wayland and X11**: Auto-paste on X11, clipboard copy on Wayland (no security popups)

## Requirements

### System Dependencies
```bash
# For Fedora/RHEL/CentOS
sudo dnf install python3 python3-pip portaudio-devel xdotool

# For Ubuntu/Debian
sudo apt install python3 python3-pip portaudio19-dev xdotool

# For Arch Linux
sudo pacman -S python python-pip portaudio xdotool
```

### Python Dependencies
```bash
# For fast recorder only (recommended)
pip install -r requirements-minimal.txt

# For both fast and fallback recorder
pip install -r requirements.txt
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/metahleon/linuxst.git
cd linuxst
```

2. Install dependencies:
```bash
# Recommended: Fast recorder only
pip install -r requirements-minimal.txt

# Optional: Include fallback recorder
pip install -r requirements.txt
```

3. Make the toggle script executable:
```bash
chmod +x working_toggle.sh
```

4. Copy the toggle script to your local bin:
```bash
cp working_toggle.sh ~/.local/bin/linuxst-toggle
```

5. Set up the keybinding (GNOME):
```bash
# Create custom keybinding
gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/linuxst-recorder/']"

# Set the command
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/linuxst-recorder/ command '/home/$USER/.local/bin/linuxst-toggle'

# Set the name
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/linuxst-recorder/ name 'LinuxST Recorder'

# Set the keybinding (Super+R)
gsettings set org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/linuxst-recorder/ binding '<Super>r'
```

## Usage

1. Press **Super+R** to start recording
   - You'll see a notification: "Recording"
   
2. Speak clearly into your microphone

3. Press **Super+R** again to stop recording
   - You'll see a notification: "Transcribing"
   - After transcription, the text will be automatically typed at your cursor position
   - You'll see a notification: "Pasted" (or "Copied (Ctrl+V to paste)" on some Wayland systems)

## Performance

- **Transcription Speed**: ~0.3 seconds for short sentences
- **Model Size**: 74MB (tiny model, downloaded on first run)
- **CPU Usage**: Minimal, uses 4 threads for transcription
- **Memory**: ~200MB when loaded

## File Structure

- `fast_recorder.py` - Fast recorder using Whisper.cpp for ultra-fast transcription
- `working_recorder.py` - Original recorder using OpenAI Whisper (fallback)
- `working_toggle.sh` - Toggle script that manages starting/stopping the recorder
- `requirements.txt` - Python dependencies

## Configuration

### Change Audio Device
Edit `fast_recorder.py` line 74 (or `working_recorder.py` if using fallback) to change the audio input device:
```python
input_device_index=10,  # Change this to your microphone's device index
```

To find your device index, run:
```bash
python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(i, p.get_device_info_by_index(i)['name']) for i in range(p.get_device_count())]"
```

### Change Whisper Model
For fast_recorder.py (default), edit line 36:
```python
self.model = Model('tiny', n_threads=4)  # Options: tiny, base, small
```

For working_recorder.py (fallback), edit line 37:
```python
self.model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

### Choose Recorder
The toggle script automatically uses `fast_recorder.py` if available. To force the original recorder:
```bash
mv fast_recorder.py fast_recorder.py.disabled
```

## Troubleshooting

### No Audio Recorded
- Check your microphone permissions
- Verify the correct audio device index in `working_recorder.py`
- Check if the microphone is working with other applications

### Auto-paste Not Working
- On Wayland: Some applications may not support virtual keyboard input. The text will be copied to clipboard - press Ctrl+V to paste manually
- Make sure xdotool is installed: `sudo dnf install xdotool`

### Transcription Takes Too Long
- Make sure `fast_recorder.py` is being used (check `/tmp/linuxst_recorder.log`)
- The first run downloads the Whisper.cpp model (~74MB for tiny)
- If still slow, check CPU usage - the model uses 4 threads by default

### First Run Downloads Model
- Whisper.cpp will download the tiny model (~74MB) on first use
- Models are cached in `~/.local/share/pywhispercpp/models/`
- This is a one-time download

## Files Created

- `/tmp/linuxst_recording.pid` - PID file for managing single instance
- `/tmp/linuxst_recorder.log` - Log file for debugging
- `/tmp/linuxst_last_transcription.txt` - Last transcribed text (backup)

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.