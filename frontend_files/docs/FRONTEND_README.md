# Sign Recognition Web Application - Frontend Setup

## Overview
This is a React + Flask web application that allows users to upload PDF files containing traffic plans and receive a list of detected traffic signs with their classifications.

## Architecture
- **Backend**: Flask (Python) - Processes PDFs through the sign recognition pipeline
- **Frontend**: React with Vite - User interface for file upload and results display
- **Communication**: REST API

## Installation

### Backend Setup

1. Install Python dependencies:
```bash
# Install original requirements
pip install -r requirements.txt

# Install backend-specific requirements (Flask, CORS)
pip install -r requirements-backend.txt
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

## Running the Application

### Development Mode

1. Start the Flask backend (from project root):
```bash
python app.py
```
The backend will run on `http://localhost:5000`

2. In a separate terminal, start the React frontend:
```bash
cd frontend
npm run dev
```
The frontend will run on `http://localhost:3000`

3. Open your browser and navigate to `http://localhost:3000`

### Production Mode

1. Build the React frontend:
```bash
cd frontend
npm run build
```

2. The built files will be in `frontend/dist/`. Flask will serve these automatically.

3. Start the Flask server:
```bash
python app.py
```

4. Access the application at `http://localhost:5000`

## Usage

1. Open the web application in your browser
2. Upload a PDF file by dragging and dropping or clicking "Browse Files"
3. Click "Process PDF" to start the analysis
4. Wait for processing (may take 30 seconds to several minutes depending on PDF size)
5. View the detected signs with their classifications and confidence scores
6. Download results as CSV if needed
7. Upload a new file to process another PDF

## API Endpoints

### POST `/api/upload`
- Accepts PDF file upload
- Processes through sign recognition pipeline
- Returns JSON with detected signs

### GET `/api/sign-image/<session_id>/<image_path>`
- Retrieves extracted sign images
- Used by frontend to display sign thumbnails

### GET `/api/health`
- Health check endpoint
- Returns server status

## File Structure

```
Sign_recognition_project/
├── app.py                          # Flask backend (FRONTEND CODE)
├── requirements-backend.txt        # Backend dependencies (FRONTEND CODE)
├── frontend/                       # React frontend (ALL FRONTEND CODE)
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── components/
│           ├── FileUpload.jsx
│           ├── SignList.jsx
│           └── SignCard.jsx
├── temp_uploads/                   # Temporary upload storage (created automatically)
├── Sign_processing/                # Original pipeline code
└── Outputs/                        # Pipeline outputs
```

## Features

✅ Drag-and-drop file upload
✅ Real-time processing status
✅ Visual display of detected signs
✅ Confidence scores with color-coded bars
✅ CSV export functionality
✅ Responsive design for mobile and desktop
✅ Error handling and user feedback

## Troubleshooting

### Backend Issues
- Ensure all dependencies are installed: `pip install -r requirements.txt requirements-backend.txt`
- Check that port 5000 is not in use
- Verify model files exist in `Sign_processing/demo/`

### Frontend Issues
- Ensure Node.js is installed (v16 or higher)
- Run `npm install` in the frontend directory
- Clear browser cache if seeing old versions
- Check console for JavaScript errors

### Processing Errors
- Ensure PDF is valid and not corrupted
- Check that the PDF contains actual map images (not just text)
- Verify sufficient disk space for temporary files
- Check Flask logs for detailed error messages

## Notes

- Uploaded PDFs are stored temporarily in `temp_uploads/`
- Each upload gets a unique session ID
- Processing time depends on PDF size and number of pages
- Maximum file size: 50MB (configurable in `app.py`)
