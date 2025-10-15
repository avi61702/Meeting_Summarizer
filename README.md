# Meeting Summarizer

A web application to upload meeting audio files, transcribe them, and generate structured summaries and action items using AssemblyAI and Google Gemini APIs.

## Demo
![Demo]()

## Features
- Upload audio files (mp3, m4a, wav, ogg)
- Automatic transcription (AssemblyAI)
- AI-powered meeting summary and action items (Google Gemini)
- Clean web interface (Flask, Tailwind CSS)

## Installation

1. *Clone the repository*

bash
git clone <repo-url>
cd meeting_summariser


2. *Create a virtual environment (recommended)*

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


3. *Install dependencies*

bash
pip install -r requirnments.txt


4. *Set API Keys*

- Get an [AssemblyAI API key](https://www.assemblyai.com/) and a [Google Gemini API key](https://ai.google.dev/).
- Set them as environment variables:

bash
export ASSEMBLYAI_API_KEY=your_assemblyai_key
export GEMINI_API_KEY=your_gemini_key
# On Windows (CMD):
set ASSEMBLYAI_API_KEY=your_assemblyai_key
set GEMINI_API_KEY=your_gemini_key


## Running the App

bash
python app.py


- Open your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000)

## File Structure
- app.py — Main Flask app
- processors/audio_processor.py — Audio transcription logic
- processors/summary.py — AI summary logic
- templates/ — HTML templates
- static/ — CSS and static files

## Notes
- Uploaded files are processed synchronously and deleted after processing.
- Summaries and transcripts are stored in memory (not persistent).

## License
MIT License
