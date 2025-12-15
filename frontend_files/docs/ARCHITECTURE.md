# 🏗️ System Architecture Overview

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                           │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              React Frontend (Port 3000)                    │  │
│  │                                                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │  │
│  │  │ FileUpload  │  │  SignList   │  │  SignCard   │       │  │
│  │  │ Component   │  │  Component  │  │  Component  │       │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │  │
│  │                                                             │  │
│  │  Features:                                                  │  │
│  │  • Drag & Drop Upload                                      │  │
│  │  • Real-time Processing Status                             │  │
│  │  • Sign Grid Display                                       │  │
│  │  • CSV Export                                               │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP Requests (axios)
                                │ POST /api/upload
                                │ GET /api/sign-image
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Flask Backend (Port 5000)                     │
│                                                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      app.py                                │  │
│  │                                                             │  │
│  │  Endpoints:                                                 │  │
│  │  • POST /api/upload      → Process PDF                     │  │
│  │  • GET  /api/sign-image  → Serve sign images              │  │
│  │  • GET  /api/health      → Health check                    │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Calls existing pipeline
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              Your Existing Sign Processing Pipeline              │
│                     (Sign_processing/)                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Step 1: Map Extraction                                  │    │
│  │  ┌──────────────────────────────────────────┐           │    │
│  │  │  MapExtractor + ORB_maps                 │           │    │
│  │  │  • Converts PDF pages to images          │           │    │
│  │  │  • Filters duplicate maps                │           │    │
│  │  └──────────────────────────────────────────┘           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                        │
│                          ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Step 2: Sign Detection                                  │    │
│  │  ┌──────────────────────────────────────────┐           │    │
│  │  │  Sign_extractor_class                    │           │    │
│  │  │  • Detects red borders                   │           │    │
│  │  │  • Extracts sign regions                 │           │    │
│  │  │  • Crops and saves signs                 │           │    │
│  │  └──────────────────────────────────────────┘           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                          │                                        │
│                          ▼                                        │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Step 3: Sign Classification                             │    │
│  │  ┌──────────────────────────────────────────┐           │    │
│  │  │  CNNPredictor (cnn.py)                   │           │    │
│  │  │  • Loads trained model                   │           │    │
│  │  │  • Classifies each sign                  │           │    │
│  │  │  • Returns class & confidence            │           │    │
│  │  └──────────────────────────────────────────┘           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ Results (JSON)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Response to Browser                         │
│                                                                   │
│  {                                                                │
│    "message": "Successfully processed 5 signs",                  │
│    "session_id": "abc-123",                                      │
│    "signs": [                                                    │
│      {                                                            │
│        "filename": "sign_001.png",                               │
│        "predicted_class": "362_60",                              │
│        "confidence": 0.95,                                       │
│        "image_path": "signs/sign_001.png"                        │
│      },                                                           │
│      ...                                                          │
│    ]                                                              │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Upload Flow
```
1. User drops PDF → FileUpload.jsx
2. FileUpload sends FormData → Flask /api/upload
3. Flask saves PDF to temp_uploads/{session_id}/
4. Flask calls process_pdf()
   ├─ MapExtractor.pdf_To_image()
   ├─ For each page:
   │  └─ Sign_extractor_class.extract_signs()
   └─ For each sign:
      └─ CNNPredictor.predict()
5. Flask returns JSON response
6. React displays results in SignList/SignCard
```

### Image Serving Flow
```
1. SignCard needs image → requests /api/sign-image/{session}/{path}
2. Flask serves from temp_uploads/{session}/{path}
3. Browser displays in <img> tag
```

## File Organization

### Frontend Code (NEW)
```
app.py                          ← Flask API server
requirements-backend.txt        ← Flask dependencies
frontend/                       ← React application
  ├── src/
  │   ├── main.jsx             ← React entry
  │   ├── App.jsx              ← Main component
  │   ├── App.css              ← Styles
  │   └── components/
  │       ├── FileUpload.jsx   ← Upload UI
  │       ├── SignList.jsx     ← Results list
  │       └── SignCard.jsx     ← Individual sign
  ├── package.json             ← NPM config
  └── vite.config.js           ← Build config
```

### Backend Code (EXISTING - UNCHANGED)
```
main.py                         ← Original CLI script
Sign_processing/
  ├── Map_extractor.py         ← PDF → Images
  ├── Sign_extractor.py        ← Image → Signs
  ├── cnn.py                   ← Sign → Class
  └── demo/
      ├── cnn.pth              ← Trained model
      └── classes.json         ← Class names
```

### Helper Scripts (NEW)
```
start-dev.sh                   ← Start both servers (Linux/Mac)
start-dev.bat                  ← Start both servers (Windows)
test_backend.py                ← Test Flask API
demo_upload.py                 ← Demo upload script
check_installation.py          ← Verify setup
```

## Technology Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool & dev server
- **Axios** - HTTP client
- **CSS3** - Styling (no framework, custom styles)

### Backend
- **Flask 3** - Web framework
- **flask-cors** - CORS support
- **Werkzeug** - WSGI utilities

### Processing (Your existing code)
- **OpenCV** - Image processing
- **PyTorch** - Deep learning
- **pdf2image** - PDF conversion
- **pytesseract** - OCR

## Communication Protocol

### Request Format
```http
POST /api/upload HTTP/1.1
Host: localhost:5000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="plan.pdf"
Content-Type: application/pdf

[PDF binary data]
------WebKitFormBoundary--
```

### Response Format
```json
{
  "message": "Successfully processed 3 signs",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "signs": [
    {
      "filename": "page_1_sign_1.png",
      "predicted_class": "110",
      "confidence": 0.9245,
      "image_path": "signs/page_1_sign_1.png"
    }
  ]
}
```

## Deployment Considerations

### Development
- Frontend: `npm run dev` (Vite dev server with HMR)
- Backend: `python app.py` (Flask debug mode)
- Separate processes, CORS enabled

### Production
- Frontend: `npm run build` → static files in `frontend/dist/`
- Backend: Flask serves static files AND API
- Single process on port 5000
- Consider: Gunicorn/uWSGI for production WSGI server

### Scaling
- Add nginx reverse proxy
- Use Redis for session management
- Add task queue (Celery) for long-running jobs
- Database for persistent storage
- CDN for static assets

## Security Notes

⚠️ **Current Implementation** (Development)
- No authentication
- No rate limiting
- Files stored locally
- CORS wide open
- Debug mode enabled

✅ **Production Recommendations**
- Add user authentication (JWT, OAuth)
- Implement rate limiting
- Use secure file storage (S3, Azure Blob)
- Configure CORS properly
- Disable debug mode
- Add HTTPS
- Sanitize file names
- Validate file types strictly
- Set file size limits
- Add CSRF protection

## Performance Characteristics

### Bottlenecks
1. **PDF Processing** (MapExtractor) - IO bound
2. **Sign Detection** (Sign_extractor) - CPU bound
3. **CNN Inference** (CNNPredictor) - GPU/CPU bound

### Optimization Options
- Use GPU for CNN inference (CUDA)
- Parallel page processing
- Async job queue
- Caching frequently processed PDFs
- Compress sign images
- Progressive result streaming

## Error Handling

### Frontend
- Network errors → "Cannot connect" message
- Server errors → Display error.message
- No signs → "No signs detected" info box
- Invalid file → Validation before upload

### Backend
- Invalid file type → 400 Bad Request
- Processing errors → 500 Internal Server Error
- File too large → 413 Payload Too Large
- All errors return JSON with error field

## Session Management

Each upload gets a unique UUID session:
```
temp_uploads/
  └── {session-id}/
      ├── uploaded_file.pdf
      ├── maps/
      │   ├── page_1.jpg
      │   └── page_2.jpg
      └── signs/
          ├── page_1_sign_1.png
          └── page_1_sign_2.png
```

This allows:
- Multiple concurrent users
- Isolated processing
- Easy cleanup
- Image serving by session

## Monitoring & Logging

### Current Logging
- Flask console output
- Browser console (React)

### Production Recommendations
- Structured logging (JSON)
- Log aggregation (ELK, CloudWatch)
- Error tracking (Sentry)
- Performance monitoring (APM)
- Usage analytics
