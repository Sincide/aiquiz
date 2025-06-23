# CISSP Quiz Application

This project provides a local-only CISSP quiz tool with optional integration to a local Ollama instance for explanations.

## Features
- Load CISSP questions from local JSON files (supports multiple choice and ordering questions).
- Randomized quizzes with optional domain filtering.
- Local result storage in SQLite (no web storage or telemetry).
- Mark questions as favorites for later review.
- Request explanations from a locally running Ollama model.
- Simple Tkinter interface with keyboard navigation and dark theme.

## Usage
1. Ensure Python 3 is installed (no additional pip packages required).
2. Place your question JSON files in the `data/` directory (create it if missing).
3. Run the application:
   ```bash
   python -m quiz_app.main
   ```
4. The app will detect available Ollama models from `localhost:11434`.

All data and configuration remain on your machine.

See `DEVLOG.md` for a history of development steps and `PLANNED_FEATURES.md` for upcoming improvements.

