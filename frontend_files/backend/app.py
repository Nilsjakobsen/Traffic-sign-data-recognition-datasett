# ============================================
# FRONTEND CODE - Flask Backend API
# ============================================
# This file serves as the Flask backend that receives PDF uploads
# and processes them through the sign recognition pipeline

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
import tempfile
import shutil
import csv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import existing pipeline components
from Sign_processing.Map_extractor import MapExtractor, ORB_maps
from Sign_processing.Sign_extractor import Sign_extractor_class
from Sign_processing.cnn import CNNPredictor

app = Flask(__name__, static_folder='../frontend/dist')
CORS(app)  # Enable CORS for React frontend

# Configuration
UPLOAD_FOLDER = Path('../../temp_uploads')
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create necessary directories
UPLOAD_FOLDER.mkdir(exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def process_pdf(pdf_path, session_id):
    """
    Process uploaded PDF through the sign recognition pipeline
    Returns list of detected signs with predictions
    """
    # Create session-specific directories
    session_dir = UPLOAD_FOLDER / session_id
    output_dir_maps = session_dir / "maps"
    output_dir_signs = session_dir / "signs"
    
    output_dir_maps.mkdir(parents=True, exist_ok=True)
    output_dir_signs.mkdir(parents=True, exist_ok=True)
    
    try:
        # Step 1: Extract maps from PDF
        print(f"[DEBUG] Step 1: Starting PDF to image extraction for {pdf_path}")
        orb = ORB_maps(nfeatures=20000, ratio=0.75, min_good=12000)
        maps = MapExtractor(orb_matcher=orb, output_dir=output_dir_maps)
        maps.pdf_To_image(pdf_path)
        print(f"[DEBUG] Step 1: Completed PDF extraction")
        
        # Step 2: Extract signs from each map page
        files_sorted = sorted(
            output_dir_maps.glob("page_*.jpg"),
            key=lambda p: int(p.stem.split("_")[1])
        )
        print(f"[DEBUG] Step 2: Found {len(files_sorted)} map pages to process")
        
        for idx, image_path in enumerate(files_sorted, 1):
            print(f"[DEBUG] Step 2: Processing map page {idx}/{len(files_sorted)}: {image_path.name}")
            sign_extractor = Sign_extractor_class(
                image_path=image_path,
                output_dir=output_dir_signs
            )
            sign_extractor.extract_signs()
        print(f"[DEBUG] Step 2: Completed sign extraction")
        
        # Step 3: Run CNN predictions on extracted signs
        model_path = Path("../../Sign_processing/demo/cnn.pth")
        classes_path = Path("../../Sign_processing/demo/classes.json")
        print(f"[DEBUG] Step 3: Loading CNN model from {model_path}")
        predictor = CNNPredictor(model_path, classes_path)
        
        results = []
        sign_files = sorted(output_dir_signs.glob("*.png"))
        print(f"[DEBUG] Step 3: Found {len(sign_files)} signs to classify")
        
        for idx, sign_path in enumerate(sign_files, 1):
            print(f"[DEBUG] Step 3: Classifying sign {idx}/{len(sign_files)}: {sign_path.name}")
            prediction_results = predictor.predict(str(sign_path))
            if prediction_results:
                top_class, top_prob = prediction_results[0]
                results.append({
                    'filename': sign_path.name,
                    'predicted_class': top_class,
                    'confidence': float(top_prob),
                    'image_path': str(sign_path.relative_to(session_dir))
                })
        
        print(f"[DEBUG] Step 3: Completed processing. Total results: {len(results)}")
        return results, None
        
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] Processing failed: {error_details}")
        return None, str(e)
    

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to receive PDF file and process it
    Returns JSON with detected signs and their classifications
    """
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a PDF file.'}), 400
    
    try:
        # Generate unique session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        session_dir = UPLOAD_FOLDER / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        pdf_path = session_dir / filename
        file.save(pdf_path)
        
        # Process the PDF
        results, error = process_pdf(str(pdf_path), session_id)
        
        if error:
            return jsonify({'error': f'Processing failed: {error}'}), 500
        
        if not results:
            return jsonify({
                'message': 'No signs detected in the PDF',
                'signs': []
            }), 200
        
        return jsonify({
            'message': f'Successfully processed {len(results)} signs',
            'signs': results,
            'session_id': session_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/sign-image/<session_id>/<path:image_path>')
def get_sign_image(session_id, image_path):
    """Endpoint to retrieve extracted sign images"""
    try:
        full_path = UPLOAD_FOLDER / session_id / image_path
        return send_from_directory(full_path.parent, full_path.name)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


# Serve React frontend in production
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    """Serve React frontend static files"""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
