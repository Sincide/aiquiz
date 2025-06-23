#!/usr/bin/fish
# CISSP Quiz Application Setup Script
# Runs after cloning the repo on a fresh Arch Linux installation
# Sets up dependencies, application launcher, and everything needed

set_color green
echo "🚀 CISSP Quiz Application Setup"
set_color normal
echo "Setting up your AI-powered CISSP certification quiz..."
echo ""

# Check if we're on Arch Linux
if not test -f /etc/arch-release
    set_color red
    echo "❌ This script is designed for Arch Linux"
    set_color normal
    echo "Please install dependencies manually for your distribution"
    exit 1
end

# Check if we're in the right directory
if not test -f app.py
    set_color red
    echo "❌ Please run this script from the aiquiz project directory"
    set_color normal
    echo "Expected files: app.py, quiz.json, etc."
    exit 1
end

set_color blue
echo "📦 Installing system dependencies..."
set_color normal

# Install Python dependencies via pacman (following user preference)
echo "Installing Python Flask and Requests..."
if not sudo pacman -S --needed --noconfirm python-flask python-requests
    set_color red
    echo "❌ Failed to install Python dependencies"
    set_color normal
    exit 1
end

# Check if Ollama is installed
if not type -q ollama
    set_color yellow
    echo "⚠️  Ollama not found. AI explanations will not be available."
    echo "To install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "Then run: ollama pull llama3.2:3b"
    set_color normal
else
    set_color green
    echo "✅ Ollama found"
    set_color normal
    
    # Check if the recommended model is available
    if not ollama list | grep -q "llama3.2:3b"
        set_color blue
        echo "📥 Downloading recommended AI model (llama3.2:3b)..."
        set_color normal
        echo "This may take a few minutes depending on your internet connection..."
        if ollama pull llama3.2:3b
            set_color green
            echo "✅ AI model downloaded successfully"
            set_color normal
        else
            set_color yellow
            echo "⚠️  Failed to download AI model. You can do this later with:"
            echo "ollama pull llama3.2:3b"
            set_color normal
        end
    else
        set_color green
        echo "✅ AI model (llama3.2:3b) already available"
        set_color normal
    end
end

set_color blue
echo "🔧 Setting up application launcher..."
set_color normal

# Create applications directory if it doesn't exist
mkdir -p ~/.local/share/applications

# Make launch scripts executable
chmod +x launch-quiz.fish launch-quiz-silent.fish launch-quiz-desktop.fish launch-quiz-wrapper.sh

# Create desktop entry
echo "Creating desktop entry..."
set desktop_file ~/.local/share/applications/cissp-quiz.desktop
echo '[Desktop Entry]
Version=1.0
Type=Application
Name=CISSP Quiz
Comment=AI-Powered CISSP Certification Quiz Application
Exec='(pwd)'/launch-quiz-wrapper.sh
Icon=applications-education
Terminal=false
Categories=Education;Development;
Keywords=cissp;security;quiz;certification;study;
StartupNotify=true
Path='(pwd) > $desktop_file

# Make desktop entry executable
chmod +x $desktop_file

# Update desktop database
if type -q update-desktop-database
    update-desktop-database ~/.local/share/applications/
    set_color green
    echo "✅ Desktop database updated"
    set_color normal
else
    set_color yellow
    echo "⚠️  update-desktop-database not found, but desktop entry created"
    set_color normal
end

set_color blue
echo "🧪 Testing application setup..."
set_color normal

# Test Python imports
if python -c "import flask, requests" 2>/dev/null
    set_color green
    echo "✅ Python dependencies working"
    set_color normal
else
    set_color red
    echo "❌ Python dependency test failed"
    set_color normal
    exit 1
end

# Check quiz data
if test -f quiz.json
    set question_count (python -c "import json; print(len(json.load(open('quiz.json'))))" 2>/dev/null)
    if test -n "$question_count"
        set_color green
        echo "✅ Quiz data loaded: $question_count questions"
        set_color normal
    else
        set_color red
        echo "❌ Failed to load quiz data"
        set_color normal
        exit 1
    end
else
    set_color red
    echo "❌ quiz.json not found"
    set_color normal
    exit 1
end

# Test database creation
if python -c "from quiz_app.db import init_db, get_db; init_db(); print('DB OK')" 2>/dev/null
    set_color green
    echo "✅ Database initialization successful"
    set_color normal
else
    set_color yellow
    echo "⚠️  Database test failed, but may work at runtime"
    set_color normal
end

set_color blue
echo "📝 Creating README for quick reference..."
set_color normal

# Create or update README with setup info
if not test -f SETUP_COMPLETE.md
    echo '# CISSP Quiz Setup Complete! 🎉

## Quick Start
- **Launch via Fuzzel**: Type "CISSP Quiz" in fuzzel
- **Launch via Terminal**: `./launch-quiz.fish`
- **Direct Python**: `python app.py` then visit http://localhost:5000

## Features Available
- ✅ 885 CISSP questions across 8 domains
- ✅ AI-powered explanations (if Ollama installed)
- ✅ Statistics tracking and favorites
- ✅ Web-based interface with dark theme
- ✅ Desktop launcher integration

## Dependencies Installed
- ✅ python-flask (web framework)  
- ✅ python-requests (HTTP client)
' > SETUP_COMPLETE.md

    if type -q ollama
        echo '- ✅ ollama (AI explanations)' >> SETUP_COMPLETE.md
    else
        echo '- ⚠️  ollama (not installed - AI explanations unavailable)' >> SETUP_COMPLETE.md
    end

    echo '
## Files Created
- `~/.local/share/applications/cissp-quiz.desktop` - Desktop entry
- `quiz_results.db` - SQLite database (created on first run)
- `SETUP_COMPLETE.md` - This file

## Troubleshooting
- **Port 5000 in use**: Change port in app.py or kill existing process
- **AI not working**: Install Ollama and run `ollama pull llama3.2:3b`
- **Launcher not appearing**: Run `update-desktop-database ~/.local/share/applications/`

---
Generated by setup.fish on '(date)' >> SETUP_COMPLETE.md
end

echo ""
set_color green
echo "🎉 CISSP Quiz Setup Complete!"
set_color normal
echo ""
echo "📚 You now have:"
echo "   • 885 CISSP questions with proper domain categorization"
echo "   • Web interface with AI explanations"
echo "   • Desktop launcher (search 'CISSP Quiz' in fuzzel)"
echo "   • Statistics tracking and favorites system"
echo ""
set_color blue
echo "🚀 Ready to launch:"
set_color normal
echo "   • Via fuzzel: Type 'CISSP Quiz'"
echo "   • Via terminal: ./launch-quiz.fish"
echo "   • Direct: python app.py"
echo ""
set_color yellow
echo "💡 Pro tip: The app will auto-open your browser at http://localhost:5000"
set_color normal
echo ""

# Offer to launch immediately
echo "Launch the quiz application now? [Y/n]"
read -l response
if test "$response" = "" -o "$response" = "y" -o "$response" = "Y"
    set_color green
    echo "🚀 Starting CISSP Quiz..."
    set_color normal
    ./launch-quiz.fish
end 