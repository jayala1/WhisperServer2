from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from . import app, db
from .models import User, AudioRecord
from flask_login import login_user, login_required, logout_user,current_user
from werkzeug.utils import secure_filename
from .transcription_service import transcribe_audio_file
from gpt4all import GPT4All
import logging
import os

model = GPT4All("orca-mini-3b-gguf2-q4_0.gguf")
logging.basicConfig(level=logging.INFO)

# Configuration for uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'UPLOAD_FOLDER')  # You should change this to a folder on your server
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'flac', 'ogg'}  # Extend this set with supported file types

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        result = User.create_user(email, password)
        if result == 'email_exists':
            flash('That email is already registered. Please choose another one.', 'error')
        elif result == 'error':
            flash('An unexpected error occurred. Please try again.', 'error')
        else:
            flash('Account created!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))  # Replace 'dashboard' with your dashboard view function
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Assuming the current_user is imported from flask_login
    from flask_login import current_user
    # Query for audio records if your model is set up for it
    audio_records = AudioRecord.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', name=current_user.email, audio_records=audio_records)

@app.route('/transcribe_audio', methods=['POST'])
@login_required
def transcribe_audio():
    # Check if the post request has the file part
    if 'audio_file' not in request.files:
        flash('No file part in the request', 'error')
        return redirect(url_for('dashboard'))

    file = request.files['audio_file']
    # If the user does not select a file, the browser submits an
    # empty part without a filename
    if file.filename == '':
        flash('No file selected for uploading', 'error')
        return redirect(url_for('dashboard'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Call the transcription function
        result = transcribe_audio_file(filepath)
        transcription = result.get('text') if result and 'text' in result else None
        
        # Check if transcription was successful
        if transcription:
            # Create a new audio record with the transcription
            new_record = AudioRecord(title=filename, transcription=transcription, summary="", user_id=current_user.id)
            db.session.add(new_record)
            db.session.commit()
            flash('File successfully uploaded and transcribed!', 'success')
        else:
            flash('Transcription failed.', 'error')

        return redirect(url_for('dashboard'))
    else:
        flash('Allowed file types are - wav, mp3, flac, ogg', 'error')
        return redirect(url_for('dashboard'))


@app.route('/summarize_transcription/<int:record_id>', methods=['POST'])
@login_required
def summarize_transcription(record_id):
    audio_record = AudioRecord.query.get_or_404(record_id)

    # Formulating a more directive prompt for summarization using an f-string for consistency
    prompt = f"Please summarize the following text: {audio_record.transcription}"

    logging.info("Sending prompt to model: %s", prompt)

    try:
        summary_result = model.generate(prompt, max_tokens=128)
        # Assuming the summary is the first element in the result
        summary = summary_result[0]['generated_text'] if summary_result else "Summary generation failed"
        logging.info("Model response: %s", summary)
        
        # Check if summary generation was successful
        if summary != "Summary generation failed":
            audio_record.summary = summary
            db.session.commit()
            flash('Summary generated successfully!', 'success')
        else:
            flash('Summary generation failed.', 'error')
    except Exception as e:
        logging.error("Error during summary generation: %s", str(e))
        flash('An error occurred during summary generation.', 'error')

    return redirect(url_for('dashboard'))

@app.route('/delete_record/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    record = AudioRecord.query.get_or_404(record_id)

    # Ensure the current user owns the record
    if record.user_id != current_user.id:
        flash('Unauthorized to delete this record.', 'error')
        return redirect(url_for('dashboard'))

    db.session.delete(record)
    db.session.commit()
    flash('Record deleted successfully.', 'success')
    return redirect(url_for('dashboard'))
