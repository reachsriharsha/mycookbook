from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import os
import string
import random
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed extensions
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_random_prefix():
    """Generate a random 5-character prefix"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
    print(f"Created uploads directory: {app.config['UPLOAD_FOLDER']}")

@app.route('/')
def home():
    """Home page route"""
    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('home'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('home'))
    
    if file and allowed_file(file.filename):
        # Generate random prefix and create new filename
        random_prefix = generate_random_prefix()
        original_filename = secure_filename(file.filename)
        new_filename = f"{random_prefix}_{original_filename}"
        
        # Save file to uploads directory
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        file.save(filepath)
        
        # Store the uploaded filename in session for analysis
        session['uploaded_file'] = new_filename
        
        flash(f'File uploaded successfully as: {new_filename}', 'success')
        return redirect(url_for('home'))
    else:
        flash('Invalid file type. Please upload a CSV file.', 'danger')
        return redirect(url_for('home'))

@app.route('/analyze', methods=['POST'])
def analyze_data():
    """Analyze the uploaded CSV file"""
    try:
        # Check if there's an uploaded file in session
        if 'uploaded_file' not in session:
            return jsonify({'error': 'No file uploaded yet'}), 400
        
        filename = session['uploaded_file']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            return jsonify({'error': 'Uploaded file not found'}), 404
        
        # Read CSV file as dataframe
        df = pd.read_csv(filepath)
        
        # Get column information
        columns_info = {
            'columns': df.columns.tolist(),
            'shape': df.shape,
            'filename': filename
        }
        
        print(f"Analyzing file: {filename}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Shape: {df.shape}")
        
        return jsonify({
            'success': True,
            'data': columns_info,
            'message': 'Data analyzed successfully'
        })
        
    except Exception as e:
        print(f"Error analyzing data: {str(e)}")
        return jsonify({'error': f'Error analyzing data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)