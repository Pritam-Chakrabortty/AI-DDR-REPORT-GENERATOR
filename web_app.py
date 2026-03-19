#!/usr/bin/env python3
"""
Web Interface for AI-powered Detailed Diagnostic Report (DDR) Generator
Flask web application with file upload functionality
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import tempfile
import shutil
from datetime import datetime
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_extractor import PDFExtractor
from ai_processor import AIProcessor
from report_generator import ReportGenerator
from config import config, error_handler

app = Flask(__name__)
app.config['SECRET_KEY'] = config.flask_secret_key
app.config['MAX_CONTENT_LENGTH'] = config.max_content_length
app.config['UPLOAD_FOLDER'] = config.upload_folder
app.config['OUTPUT_FOLDER'] = config.output_dir

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file upload and processing"""
    try:
        # Check if files were uploaded
        if 'inspection_file' not in request.files or 'thermal_file' not in request.files:
            flash('Both Inspection Report and Thermal Report files are required!', 'error')
            return redirect(url_for('index'))
        
        inspection_file = request.files['inspection_file']
        thermal_file = request.files['thermal_file']
        
        # Check if files are selected
        if inspection_file.filename == '' or thermal_file.filename == '':
            flash('Please select both PDF files!', 'error')
            return redirect(url_for('index'))
        
        # Check file extensions
        if not (allowed_file(inspection_file.filename) and allowed_file(thermal_file.filename)):
            flash('Only PDF files are allowed!', 'error')
            return redirect(url_for('index'))
        
        # Save uploaded files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        inspection_filename = secure_filename(f"inspection_{timestamp}_{inspection_file.filename}")
        thermal_filename = secure_filename(f"thermal_{timestamp}_{thermal_file.filename}")
        
        inspection_path = os.path.join(app.config['UPLOAD_FOLDER'], inspection_filename)
        thermal_path = os.path.join(app.config['UPLOAD_FOLDER'], thermal_filename)
        
        inspection_file.save(inspection_path)
        thermal_file.save(thermal_path)
        
        # Process files
        flash('Files uploaded successfully! Processing...', 'success')
        return redirect(url_for('process_files', 
                             inspection_file=inspection_filename,
                             thermal_file=thermal_filename))
        
    except RequestEntityTooLarge:
        flash('Files too large! Maximum size is 50MB per file.', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        error_handler.log_error(f"Upload error: {str(e)}")
        flash(f'Upload failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/process')
def process_files():
    """Process uploaded files and generate DDR"""
    try:
        inspection_filename = request.args.get('inspection_file')
        thermal_filename = request.args.get('thermal_file')
        
        if not inspection_filename or not thermal_filename:
            flash('Missing file parameters!', 'error')
            return redirect(url_for('index'))
        
        inspection_path = os.path.join(app.config['UPLOAD_FOLDER'], inspection_filename)
        thermal_path = os.path.join(app.config['UPLOAD_FOLDER'], thermal_filename)
        
        # Check if files exist
        if not os.path.exists(inspection_path) or not os.path.exists(thermal_path):
            flash('Uploaded files not found!', 'error')
            return redirect(url_for('index'))
        
        # Initialize components
        pdf_extractor = PDFExtractor()
        ai_processor = AIProcessor()
        report_generator = ReportGenerator()
        
        # Step 1: Extract data from PDFs
        error_handler.log_info(f"Extracting data from {inspection_filename}")
        inspection_data = pdf_extractor.extract_from_pdf(inspection_path, "inspection")
        
        error_handler.log_info(f"Extracting data from {thermal_filename}")
        thermal_data = pdf_extractor.extract_from_pdf(thermal_path, "thermal")
        
        # Step 2: Process with AI
        error_handler.log_info("Processing data with AI to generate DDR...")
        ddr_content = ai_processor.generate_ddr(inspection_data, thermal_data)
        
        # Step 3: Generate report
        error_handler.log_info("Generating final DDR report...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"DDR_Report_{timestamp}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        report_generator.create_ddr_pdf(
            ddr_content=ddr_content,
            inspection_images=inspection_data['images'],
            thermal_images=thermal_data['images'],
            output_path=output_path
        )
        
        # Clean up uploaded files
        try:
            os.remove(inspection_path)
            os.remove(thermal_path)
        except:
            pass
        
        # Display results
        flash('DDR Report generated successfully!', 'success')
        return render_template('result.html', 
                             ddr_content=ddr_content,
                             output_filename=output_filename,
                             inspection_images_count=len(inspection_data['images']),
                             thermal_images_count=len(thermal_data['images']))
        
    except Exception as e:
        error_handler.log_error(f"Processing error: {str(e)}")
        flash(f'Processing failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated report"""
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            flash('File not found!', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        error_handler.log_error(f"Download error: {str(e)}")
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/cleanup')
def cleanup():
    """Clean up old files"""
    try:
        # Clean up old output files (keep last 10)
        output_dir = Path(app.config['OUTPUT_FOLDER'])
        if output_dir.exists():
            pdf_files = sorted(output_dir.glob("DDR_Report_*.pdf"), 
                              key=lambda x: x.stat().st_mtime, reverse=True)
            for old_file in pdf_files[10:]:
                old_file.unlink()
                error_handler.log_info(f"Cleaned up old file: {old_file}")
        
        # Clean up old upload files
        upload_dir = Path(app.config['UPLOAD_FOLDER'])
        if upload_dir.exists():
            for old_file in upload_dir.glob("*"):
                if old_file.is_file() and old_file.stat().st_mtime < (datetime.now().timestamp() - 3600):
                    old_file.unlink()
                    error_handler.log_info(f"Cleaned up old upload: {old_file}")
        
        return jsonify({'status': 'success', 'message': 'Cleanup completed'})
    except Exception as e:
        error_handler.log_error(f"Cleanup error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test AI connection
        ai_processor = AIProcessor()
        ai_status = ai_processor.test_api_connection()
        
        return jsonify({
            'status': 'healthy',
            'ai_connection': ai_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("🚀 Starting DDR Generator Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    print("📄 Upload Inspection Report and Thermal Report PDF files")
    print("🤖 AI will process and generate Detailed Diagnostic Report")
    
    app.run(debug=config.debug, host='127.0.0.1', port=5000)
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=config.debug, host='0.0.0.0', port=port)
