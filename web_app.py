#!/usr/bin/env python3
"""
Web Application Module
Flask-based web interface for the DDR Generator
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename

from config import config
from pdf_extractor import PDFExtractor
from ai_processor import AIProcessor
from report_generator import ReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask with explicit template folder path
# This resolves the TemplateNotFound error by using an absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Debug: Print paths to verify
print(f"Base directory: {BASE_DIR}")
print(f"Template directory: {TEMPLATE_DIR}")
print(f"Template directory exists: {os.path.exists(TEMPLATE_DIR)}")
print(f"Index.html exists: {os.path.exists(os.path.join(TEMPLATE_DIR, 'index.html'))}")

# Initialize Flask first, then set template folder
app = Flask(__name__)
app.template_folder = TEMPLATE_DIR

# Verify Flask can see the template
try:
    app.jinja_env.loader.list_templates()
    print("✅ Jinja2 loader initialized successfully")
except Exception as e:
    print(f"❌ Jinja2 loader error: {e}")
    # Force reload the Jinja environment with FileSystemLoader
    from jinja2 import FileSystemLoader
    app.jinja_env.loader = FileSystemLoader(TEMPLATE_DIR)
    print(f"🔧 Forced FileSystemLoader with path: {TEMPLATE_DIR}")
    try:
        app.jinja_env.loader.list_templates()
        print("✅ FileSystemLoader works!")
    except Exception as e2:
        print(f"❌ FileSystemLoader also failed: {e2}")

# Alternative template loading if the above doesn't work
if not os.path.exists(TEMPLATE_DIR):
    print(f"Warning: Template directory not found at {TEMPLATE_DIR}")
    # Try relative path
    TEMPLATE_DIR = 'templates'
    app.template_folder = TEMPLATE_DIR
    print(f"Trying relative template path: {TEMPLATE_DIR}")

# App configuration
app.secret_key = config.flask_secret_key
app.config['UPLOAD_FOLDER'] = config.upload_folder
app.config['OUTPUT_FOLDER'] = config.output_dir
app.config['MAX_CONTENT_LENGTH'] = config.max_content_length

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file uploads and report generation"""
    try:
        # Check if files exist in request
        if 'inspection_file' not in request.files or 'thermal_file' not in request.files:
            flash('Both inspection and thermal reports are required', 'error')
            return redirect(url_for('index'))
        
        inspection_file = request.files['inspection_file']
        thermal_file = request.files['thermal_file']
        
        # Check if filenames are empty
        if inspection_file.filename == '' or thermal_file.filename == '':
            flash('No selected file', 'error')
            return redirect(url_for('index'))
            
        # Validate file types
        if not (allowed_file(inspection_file.filename) and allowed_file(thermal_file.filename)):
            flash('Invalid file type. Please upload PDF files only.', 'error')
            return redirect(url_for('index'))

        # Process files
        inspection_filename = secure_filename(inspection_file.filename)
        thermal_filename = secure_filename(thermal_file.filename)
        
        inspection_path = os.path.join(app.config['UPLOAD_FOLDER'], inspection_filename)
        thermal_path = os.path.join(app.config['UPLOAD_FOLDER'], thermal_filename)
        
        inspection_file.save(inspection_path)
        thermal_file.save(thermal_path)
        
        logger.info(f"Files uploaded: {inspection_filename}, {thermal_filename}")

        # Initialize processors
        pdf_extractor = PDFExtractor()
        ai_processor = AIProcessor()
        report_generator = ReportGenerator()
        
        # Extract data
        logger.info("Extracting data from PDFs...")
        inspection_data = pdf_extractor.extract_from_pdf(inspection_path, "inspection")
        thermal_data = pdf_extractor.extract_from_pdf(thermal_path, "thermal")
        
        # Generate DDR content
        logger.info("Generating DDR content with AI...")
        ddr_content = ai_processor.generate_ddr(inspection_data, thermal_data)
        
        # Generate PDF Report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"DDR_Report_{timestamp}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        logger.info(f"Creating PDF report at {output_path}")
        report_generator.create_ddr_pdf(
            ddr_content=ddr_content,
            inspection_images=inspection_data.get('images', []),
            thermal_images=thermal_data.get('images', []),
            output_path=output_path
        )
        
        # Clean up uploaded files
        try:
            os.remove(inspection_path)
            os.remove(thermal_path)
            logger.info("Temporary upload files cleaned up")
        except Exception as e:
            logger.warning(f"Failed to clean up uploads: {e}")

        flash('DDR Report generated successfully!', 'success')
        return render_template('result.html',
                            ddr_content=ddr_content,
                            output_filename=output_filename,
                            inspection_images_count=len(inspection_data.get('images', [])),
                            thermal_images_count=len(thermal_data.get('images', [])))

    except Exception as e:
        logger.error(f"Error during processing: {str(e)}")
        flash(f'An error occurred: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    """Download the generated report"""
    try:
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        flash('File not found', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    print(f"Starting web server on http://127.0.0.1:5000...")
    print(f"Template folder: {TEMPLATE_DIR}")
    app.run(host='127.0.0.1', port=5000, debug=config.debug)