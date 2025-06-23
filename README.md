# CISSP Quiz Application

A comprehensive local-only CISSP quiz tool with AI-powered explanations and advanced study features.

## ✨ Features

### Core Functionality
- **Multiple Question Types**: Support for multiple choice and ordering questions
- **Domain Selection**: Choose specific CISSP domains for focused study sessions
- **Randomized Quizzes**: Questions are shuffled for varied practice sessions
- **Progress Tracking**: Visual progress bar and question numbering
- **Local Storage**: All data stored locally in SQLite (no web connectivity required)

### Study Tools
- **Favorites System**: Mark difficult questions for later review
- **Review Mode**: Study only your favorite questions
- **Performance Statistics**: Detailed analytics showing overall and per-domain accuracy
- **AI Explanations**: Get detailed explanations from local Ollama models

### User Experience
- **Modern Dark Theme**: Clean, professional interface optimized for long study sessions
- **Keyboard Navigation**: Use arrow keys and Enter for efficient navigation
- **Menu System**: Easy access to all features through organized menus
- **Error Handling**: Robust error handling with helpful user messages

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ 
- Tkinter GUI library (install with `sudo pacman -S tk` on Arch Linux)
- Optional: Ollama for AI explanations

### Installation
1. Clone or download this repository
2. Ensure you have question JSON files in the `data/` directory
3. Run the application:

```fish
# Method 1: Using the launcher
python quiz.py

# Method 2: Using the module directly  
python -m quiz_app.main

# Method 3: Make launcher executable
chmod +x quiz.py
./quiz.py
```

### First Run
1. The application will create a `data/` directory if it doesn't exist
2. Add your CISSP question JSON files to the `data/` directory
3. Optional: Start Ollama for AI explanations (`ollama serve`)
4. Launch the quiz application

## 📋 Question File Format

Questions should be stored as JSON files in the `data/` directory:

```json
[
  {
    "id": "1",
    "domain": "Security and Risk Management",
    "type": "mcq",
    "question": "Which security principle ensures that information is not disclosed to unauthorized individuals?",
    "choices": ["Integrity", "Availability", "Confidentiality", "Non-repudiation"],
    "answer": "Confidentiality",
    "explanation": "Confidentiality ensures information is only accessible to authorized users."
  },
  {
    "id": "2", 
    "domain": "Asset Security",
    "type": "ordering",
    "question": "Order the data lifecycle stages from first to last.",
    "choices": ["Store", "Create", "Use", "Archive", "Destroy"],
    "answer": ["Create", "Store", "Use", "Archive", "Destroy"]
  }
]
```

### Supported Question Types
- **MCQ (Multiple Choice)**: `"type": "mcq"` with string answer
- **Ordering**: `"type": "ordering"` with array answer showing correct sequence

## 🎯 How to Use

### Starting a Quiz
1. Launch the application
2. Select CISSP domains from the domain selection dialog
3. Click "Start Quiz" to begin

### During a Quiz
- **Navigate**: Use arrow keys or Previous/Next buttons
- **Submit**: Click Submit or press Enter
- **Mark Favorites**: Click the star button for difficult questions
- **Get Explanations**: Click the lightbulb button (requires Ollama)
- **View Progress**: Check the progress bar at the top

### Menu Options
- **Quiz → New Quiz**: Start a new domain-selected quiz
- **Quiz → Review Favorites**: Study only your marked favorite questions
- **Quiz → Statistics**: View detailed performance analytics
- **Quiz → Exit**: Close the application

### Keyboard Shortcuts
- `←/→` Arrow keys: Navigate between questions
- `Enter`: Submit answer or go to next question
- Mouse: Click to interact with all interface elements

## 🤖 AI Integration (Optional)

The application integrates with [Ollama](https://ollama.ai/) for AI-powered explanations:

1. **Install Ollama**: Follow instructions at https://ollama.ai/
2. **Download a Model**: `ollama pull llama3.2:1b` (or your preferred model)
3. **Start Ollama**: `ollama serve` 
4. **Launch Quiz**: The app will detect available models automatically

When Ollama is available, the "Explain" button will provide detailed explanations for each question.

## 📊 Data Storage

All application data is stored locally:
- **Questions**: JSON files in `data/` directory
- **Results**: `quiz_results.db` SQLite database
- **Favorites**: Stored in the same SQLite database
- **Configuration**: `quiz_config.json` file

No data is sent to external servers or services.

## 🔧 Configuration

The application creates a `quiz_config.json` file with default settings:

```json
{
  "data_dir": "data",
  "ollama_model": "llama2"
}
```

You can manually edit this file to customize:
- `data_dir`: Directory containing question JSON files
- `ollama_model`: Preferred Ollama model for explanations

## 🎓 CISSP Domains Supported

The application supports all 8 CISSP domains:
1. Security and Risk Management
2. Asset Security  
3. Security Architecture and Engineering
4. Communication and Network Security
5. Identity and Access Management (IAM)
6. Security Assessment and Testing
7. Security Operations
8. Software Development Security

## 📈 Performance Analytics

The Statistics view provides:
- **Overall Performance**: Total questions, correct answers, accuracy percentage
- **Domain Breakdown**: Per-domain statistics with individual accuracy rates
- **Progress Tracking**: Historical performance data
- **Color-coded Results**: Visual indicators for performance levels

## 🐛 Troubleshooting

### Common Issues

**"ImportError: libtk8.6.so: cannot open shared object file"**
- Install tkinter: `sudo pacman -S tk` (Arch Linux) or equivalent for your distro

**"No questions found"**
- Ensure JSON files are in the `data/` directory
- Verify JSON format matches the specification above

**"Ollama not available"**
- Check if Ollama is running: `ollama serve`
- Verify models are installed: `ollama list`

**Application won't start**
- Ensure you're in the project directory
- Check Python version: `python --version` (requires 3.7+)

### Getting Help
- Check the `DEVLOG.md` for development history
- Review `PLANNED_FEATURES.md` for upcoming improvements
- Ensure all files in the project directory are present

## 📝 Development

See `DEVLOG.md` for detailed development history and `PLANNED_FEATURES.md` for upcoming improvements.

---

**CISSP Quiz Application** - Your offline companion for CISSP certification preparation.

