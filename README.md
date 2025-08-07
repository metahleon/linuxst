# LinuxST - Simple Speech-to-Text for Linux

A lightweight, working speech-to-text tool for Linux that records audio, transcribes it using OpenAI's Whisper, and automatically pastes the text at your cursor position.

## Features

- **Simple Toggle**: Start/stop recording with a single keybind (Super+R by default)
- **Automatic Transcription**: Uses OpenAI's Whisper model for accurate speech recognition
- **Auto-Paste**: Automatically types the transcribed text at your cursor position
- **Minimal Notifications**: Clean, simple feedback ("Recording", "Transcribing", "Pasted")
- **Works on Wayland and X11**: Uses xdotool for typing text (works through XWayland on Wayland systems)

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

## File Structure

- `working_recorder.py` - Main recorder script that handles audio capture, transcription, and text insertion
- `working_toggle.sh` - Toggle script that manages starting/stopping the recorder
- `requirements.txt` - Python dependencies

## Configuration

### Change Audio Device
Edit `working_recorder.py` line 74 to change the audio input device:
```python
input_device_index=10,  # Change this to your microphone's device index
```

To find your device index, run:
```python
python3 -c "import pyaudio; p = pyaudio.PyAudio(); [print(i, p.get_device_info_by_index(i)['name']) for i in range(p.get_device_count())]"
```

### Change Whisper Model
Edit `working_recorder.py` line 37 to use a different Whisper model:
```python
self.model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
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
- The first run downloads the Whisper model (~140MB for base model)
- Consider using a smaller model like "tiny" for faster performance

## Files Created

- `/tmp/linuxst_recording.pid` - PID file for managing single instance
- `/tmp/linuxst_recorder.log` - Log file for debugging
- `/tmp/linuxst_last_transcription.txt` - Last transcribed text (backup)

## License

MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.