#!/bin/bash
# Working toggle script for LinuxST

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PID_FILE="/tmp/linuxst_recording.pid"
LOG_FILE="/tmp/linuxst_recorder.log"

# Find any running recorder
find_recorder() {
    pgrep -f "python3.*working_recorder.py" | head -1
}

# Main toggle
RECORDER_PID=$(find_recorder)

if [ -n "$RECORDER_PID" ]; then
    # Stop recording
    echo "Stopping recording (PID: $RECORDER_PID)"
    
    # Send SIGTERM to trigger transcription
    kill -TERM "$RECORDER_PID" 2>/dev/null
    
    # Notification handled by recorder
    
    # Wait for process to complete (up to 45 seconds for transcription and clipboard operations)
    count=0
    while kill -0 "$RECORDER_PID" 2>/dev/null && [ $count -lt 450 ]; do
        sleep 0.1
        count=$((count + 1))
        # Show progress every 2 seconds
        if [ $((count % 20)) -eq 0 ]; then
            echo "Waiting for transcription... ($((count/10))s)"
        fi
    done
    
    # If still running after 45 seconds, force kill
    if kill -0 "$RECORDER_PID" 2>/dev/null; then
        echo "Force killing after timeout (45s)"
        kill -9 "$RECORDER_PID" 2>/dev/null
    fi
    
    rm -f "$PID_FILE"
    echo "Recording stopped"
    
else
    # Start recording
    echo "Starting recording..."
    
    # Clean up any zombies first (silently)
    pkill -9 -f "python.*recorder" 2>/dev/null
    rm -f "$PID_FILE"
    sleep 0.1
    
    # Start new recording
    cd "$SCRIPT_DIR"
    python3 "$SCRIPT_DIR/working_recorder.py" > "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    
    # Verify it started
    if kill -0 "$NEW_PID" 2>/dev/null; then
        # Save PID
        echo "$NEW_PID" > "$PID_FILE"
        echo "Recording started (PID: $NEW_PID)"
        # Notification handled by recorder
    else
        echo "Failed to start recording"
        notify-send "LinuxST" "Failed to start" -t 2000
    fi
fi