#!/usr/bin/fish
# CISSP Quiz Launcher Script
# Launches the quiz application and opens browser automatically

echo "🚀 Starting CISSP Quiz Application..."

# Change to the quiz directory
cd /home/martin/aiquiz

# Check if required dependencies are available
if not type -q python
    echo "❌ Python not found. Please install python."
    exit 1
end

if not python -c "import flask" 2>/dev/null
    echo "❌ Flask not found. Please install python-flask."
    exit 1
end

# Start the application in background
echo "📚 Loading questions and starting server..."
python app.py &
set server_pid $last_pid

# Wait a moment for server to start
sleep 3

# Open browser
echo "🌐 Opening browser..."
if type -q xdg-open
    xdg-open http://localhost:5000 &
else if type -q brave
    brave http://localhost:5000 &
else if type -q firefox
    firefox http://localhost:5000 &
else if type -q chromium
    chromium http://localhost:5000 &
else if type -q google-chrome
    google-chrome http://localhost:5000 &
else
    echo "🔗 Server running at: http://localhost:5000"
    echo "Please open this URL in your browser"
end

echo "✅ CISSP Quiz is now running!"
echo "📝 Press Ctrl+C to stop the server"

# Wait for the server process
wait $server_pid 