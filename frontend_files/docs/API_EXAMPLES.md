# 🔌 API Usage Examples

This document shows how to interact with the Flask backend API programmatically.

## Table of Contents
- [Python Examples](#python-examples)
- [JavaScript/Node Examples](#javascriptnode-examples)
- [cURL Examples](#curl-examples)
- [Response Formats](#response-formats)

---

## Python Examples

### Basic Upload

```python
import requests

def upload_pdf(pdf_path):
    """Upload a PDF and get results"""
    url = 'http://localhost:5000/api/upload'
    
    with open(pdf_path, 'rb') as f:
        files = {'file': ('plan.pdf', f, 'application/pdf')}
        response = requests.post(url, files=files, timeout=300)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data['signs'])} signs")
        return data
    else:
        print(f"Error: {response.json()}")
        return None

# Usage
result = upload_pdf('my_plan.pdf')
```

### With Error Handling

```python
import requests
from pathlib import Path

def upload_with_error_handling(pdf_path):
    """Upload with comprehensive error handling"""
    
    # Validate file exists
    path = Path(pdf_path)
    if not path.exists():
        print(f"File not found: {pdf_path}")
        return None
    
    # Validate file type
    if path.suffix.lower() != '.pdf':
        print("Only PDF files are supported")
        return None
    
    # Check file size (50MB limit)
    if path.stat().st_size > 50 * 1024 * 1024:
        print("File too large (max 50MB)")
        return None
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {'file': (path.name, f, 'application/pdf')}
            response = requests.post(
                'http://localhost:5000/api/upload',
                files=files,
                timeout=300
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_data = response.json()
            print(f"Server error: {error_data.get('error', 'Unknown error')}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("Cannot connect to server. Is it running?")
        return None
    except requests.exceptions.Timeout:
        print("Request timed out. Try a smaller PDF.")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None

# Usage
result = upload_with_error_handling('plan.pdf')
if result:
    for sign in result['signs']:
        print(f"{sign['predicted_class']}: {sign['confidence']:.2%}")
```

### Save Results to CSV

```python
import csv
from pathlib import Path

def save_results_to_csv(result_data, output_path='results.csv'):
    """Save API results to CSV file"""
    
    if not result_data or 'signs' not in result_data:
        print("No data to save")
        return
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['filename', 'predicted_class', 'confidence']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        for sign in result_data['signs']:
            writer.writerow({
                'filename': sign['filename'],
                'predicted_class': sign['predicted_class'],
                'confidence': sign['confidence']
            })
    
    print(f"Saved {len(result_data['signs'])} results to {output_path}")

# Usage
result = upload_pdf('plan.pdf')
if result:
    save_results_to_csv(result)
```

### Download Sign Images

```python
import requests
from pathlib import Path

def download_sign_images(result_data, output_dir='downloaded_signs'):
    """Download all detected sign images"""
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    session_id = result_data['session_id']
    base_url = 'http://localhost:5000/api/sign-image'
    
    for sign in result_data['signs']:
        image_url = f"{base_url}/{session_id}/{sign['image_path']}"
        
        response = requests.get(image_url)
        if response.status_code == 200:
            save_path = output_path / sign['filename']
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {sign['filename']}")
        else:
            print(f"Failed to download: {sign['filename']}")

# Usage
result = upload_pdf('plan.pdf')
if result:
    download_sign_images(result)
```

### Batch Processing

```python
from pathlib import Path
import time

def batch_process_pdfs(pdf_directory, output_csv='batch_results.csv'):
    """Process multiple PDFs and combine results"""
    
    pdf_dir = Path(pdf_directory)
    all_results = []
    
    pdf_files = list(pdf_dir.glob('*.pdf'))
    print(f"Found {len(pdf_files)} PDF files")
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n[{i}/{len(pdf_files)}] Processing {pdf_path.name}...")
        
        result = upload_with_error_handling(str(pdf_path))
        
        if result and result.get('signs'):
            for sign in result['signs']:
                sign['source_pdf'] = pdf_path.name
                all_results.append(sign)
        
        # Be nice to the server
        time.sleep(2)
    
    # Save combined results
    if all_results:
        import csv
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['source_pdf', 'filename', 'predicted_class', 'confidence']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        print(f"\nProcessed {len(pdf_files)} PDFs")
        print(f"Found {len(all_results)} total signs")
        print(f"Results saved to {output_csv}")
    else:
        print("No signs detected in any PDFs")

# Usage
batch_process_pdfs('my_pdf_folder/')
```

---

## JavaScript/Node Examples

### Basic Upload with Axios

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function uploadPDF(pdfPath) {
  const formData = new FormData();
  formData.append('file', fs.createReadStream(pdfPath));

  try {
    const response = await axios.post(
      'http://localhost:5000/api/upload',
      formData,
      {
        headers: formData.getHeaders(),
        timeout: 300000, // 5 minutes
      }
    );

    console.log(`Found ${response.data.signs.length} signs`);
    return response.data;
  } catch (error) {
    if (error.response) {
      console.error('Server error:', error.response.data.error);
    } else if (error.request) {
      console.error('No response from server');
    } else {
      console.error('Error:', error.message);
    }
    return null;
  }
}

// Usage
uploadPDF('plan.pdf').then(result => {
  if (result) {
    result.signs.forEach(sign => {
      console.log(`${sign.predicted_class}: ${(sign.confidence * 100).toFixed(2)}%`);
    });
  }
});
```

### React Component Example

```jsx
import { useState } from 'react';
import axios from 'axios';

function PDFUploader() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 300000,
      });

      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" accept=".pdf" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? 'Processing...' : 'Upload'}
      </button>

      {error && <div className="error">{error}</div>}

      {results && (
        <div>
          <h3>Found {results.signs.length} signs</h3>
          {results.signs.map((sign, i) => (
            <div key={i}>
              <strong>{sign.predicted_class}</strong>: {(sign.confidence * 100).toFixed(2)}%
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Fetch API (Vanilla JavaScript)

```javascript
async function uploadPDF(pdfFile) {
  const formData = new FormData();
  formData.append('file', pdfFile);

  try {
    const response = await fetch('http://localhost:5000/api/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Upload failed');
    }

    const data = await response.json();
    console.log(`Processed: ${data.message}`);
    return data;
  } catch (error) {
    console.error('Error:', error.message);
    return null;
  }
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (file && file.type === 'application/pdf') {
    const result = await uploadPDF(file);
    if (result) {
      displayResults(result.signs);
    }
  }
});
```

---

## cURL Examples

### Basic Upload

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@path/to/your/file.pdf" \
  -H "Content-Type: multipart/form-data"
```

### Save Response to File

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@plan.pdf" \
  -o results.json
```

### Pretty Print JSON Response

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@plan.pdf" \
  | python -m json.tool
```

### Health Check

```bash
curl http://localhost:5000/api/health
```

### Download Sign Image

```bash
# Get session_id and image_path from upload response first
curl http://localhost:5000/api/sign-image/{session_id}/signs/sign_001.png \
  -o sign_001.png
```

### With Timeout

```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@plan.pdf" \
  --max-time 300
```

---

## Response Formats

### Successful Upload Response

```json
{
  "message": "Successfully processed 3 signs",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "signs": [
    {
      "filename": "page_1_sign_1.png",
      "predicted_class": "362_60",
      "confidence": 0.9456,
      "image_path": "signs/page_1_sign_1.png"
    },
    {
      "filename": "page_1_sign_2.png",
      "predicted_class": "110",
      "confidence": 0.8923,
      "image_path": "signs/page_1_sign_2.png"
    },
    {
      "filename": "page_2_sign_1.png",
      "predicted_class": "132g",
      "confidence": 0.7654,
      "image_path": "signs/page_2_sign_1.png"
    }
  ]
}
```

### No Signs Detected

```json
{
  "message": "No signs detected in the PDF",
  "signs": []
}
```

### Error Responses

#### No File Provided (400)
```json
{
  "error": "No file provided"
}
```

#### Invalid File Type (400)
```json
{
  "error": "Invalid file type. Please upload a PDF file."
}
```

#### Processing Failed (500)
```json
{
  "error": "Processing failed: [error details]"
}
```

#### File Too Large (413)
```json
{
  "error": "File too large. Maximum size is 50MB."
}
```

### Health Check Response

```json
{
  "status": "healthy"
}
```

---

## Tips & Best Practices

### 1. Timeout Handling
Processing can take several minutes for large PDFs. Set appropriate timeouts:
- Python requests: `timeout=300` (5 minutes)
- Axios: `timeout: 300000` (5 minutes in milliseconds)
- cURL: `--max-time 300`

### 2. Error Handling
Always check response status codes:
- `200` - Success
- `400` - Client error (bad request)
- `413` - File too large
- `500` - Server error

### 3. File Validation
Validate files before uploading:
- File type: PDF only
- File size: Max 50MB
- File exists and is readable

### 4. Progress Tracking
For large files, consider:
- Showing upload progress
- Polling status endpoint (if implemented)
- WebSocket connection for real-time updates

### 5. Result Storage
Session directories are temporary. Download results promptly:
- Save JSON responses
- Download sign images if needed
- Export to CSV for archiving

### 6. Rate Limiting
Be considerate when batch processing:
- Add delays between requests
- Process files sequentially
- Monitor server resources

---

## Testing

### Quick Test Script

```python
# test_api.py
import requests

def test_api():
    """Quick API test"""
    
    # Test health check
    r = requests.get('http://localhost:5000/api/health')
    assert r.status_code == 200
    print("✅ Health check passed")
    
    # Test upload endpoint (expect error without file)
    r = requests.post('http://localhost:5000/api/upload')
    assert r.status_code == 400
    print("✅ Upload validation working")
    
    print("\n🎉 All tests passed!")

if __name__ == '__main__':
    test_api()
```

---

## Support

For issues or questions:
1. Check Flask logs: `python app.py`
2. Check browser console (F12)
3. Review `FRONTEND_README.md` for troubleshooting
4. Test with `test_backend.py`

---

## Advanced Usage

### Custom Headers

```python
headers = {
    'X-Custom-Header': 'value',
    'User-Agent': 'My-App/1.0'
}
response = requests.post(url, files=files, headers=headers)
```

### Streaming Upload (Large Files)

```python
import requests

def upload_large_file(pdf_path):
    """Stream large file to avoid memory issues"""
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        
        # Stream the upload
        response = requests.post(
            'http://localhost:5000/api/upload',
            files=files,
            stream=True,
            timeout=300
        )
    
    return response.json()
```

### Retry Logic

```python
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def upload_with_retry(pdf_path, max_retries=3):
    """Upload with automatic retry on failure"""
    
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    
    with open(pdf_path, 'rb') as f:
        files = {'file': (Path(pdf_path).name, f, 'application/pdf')}
        response = session.post(
            'http://localhost:5000/api/upload',
            files=files,
            timeout=300
        )
    
    return response.json()
```
