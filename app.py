import os
import uuid
import json
from flask import Flask, request, redirect, url_for, render_template, abort
from werkzeug.utils import secure_filename
from processors import audio_processor, summary

# --- Configuration ---
# Use a simple dictionary for non-persistent storage (as per plan)
# Key: job_id (str), Value: {name, transcript, summary, actions}
RESULTS_DB = {}

# Folder where we temporarily save uploaded audio files
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp3', 'm4a', 'wav', 'ogg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function for allowed file types
def allowed_file(filename):
    """Check if the file extension is in the allowed list."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main upload form and lists recent jobs."""
    # Convert RESULTS_DB to a list for easy display
    jobs = [{'id': job_id, 'name': data['name']} for job_id, data in RESULTS_DB.items()]
    return render_template('index.html', jobs=jobs)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles file upload, synchronous processing, and redirection."""
    if 'audio_file' not in request.files:
        return 'No file part', 400
    
    file = request.files['audio_file']
    
    if file.filename == '' or not allowed_file(file.filename):
        return 'Invalid file type or no file selected', 400

    if file:
        # 1. Save File Locally
        job_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the file name for display purposes
        job_name = filename
        
        try:
            file.save(filepath)

            # --- SYNCHRONOUS WORKFLOW START ---
            
            # 2. Transcribe Audio (API Call 1 - MOCK)
            app.logger.info(f"[{job_id}] Starting transcription...")
            # NOTE: This call is BLOCKING and relies on the processor to call the ASR API.
            transcript = audio_processor.transcribe_audio(filepath)
            
            # 3. Summarize Transcript (API Call 2 - GEMINI)
            app.logger.info(f"[{job_id}] Starting summarization...")
            # NOTE: This call is BLOCKING and calls the LLM API.
            summary_data = summary.summarize_transcript(transcript)
            
            # 4. Update In-Memory DB
            app.logger.info(f"[{job_id}] Processing complete. Saving results.")
            
            # Merge transcript and parsed summary data
            RESULTS_DB[job_id] = {
                'name': job_name,
                'transcript': transcript,
                'status': 'COMPLETED',
                **summary_data
            }

            # --- SYNCHRONOUS WORKFLOW END ---
            
        except Exception as e:
            app.logger.error(f"[{job_id}] Processing failed: {e}")
            RESULTS_DB[job_id] = {'name': job_name, 'status': 'FAILED', 'error': str(e)}
        finally:
            # Clean up the file after processing (optional but recommended)
            if os.path.exists(filepath):
                 os.remove(filepath)
        
        # 5. Redirect to results page
        return redirect(url_for('view_summary', job_id=job_id))

@app.route('/summary/<job_id>')
def view_summary(job_id):
    """Renders the final summary page."""
    job_data = RESULTS_DB.get(job_id)
    
    if job_data is None:
        abort(404)
        
    return render_template('summary.html', job=job_data, job_id=job_id)

if __name__ == '__main__':
    # Initialize the Gemini API Key (replace with your actual API key handling)
    # The actual API key value will be provided at runtime in this environment.
    os.environ['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', '') 
    
    # Run the Flask app
    app.run(debug=True)
