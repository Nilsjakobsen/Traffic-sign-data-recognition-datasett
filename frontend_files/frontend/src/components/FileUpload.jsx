// ============================================
// FRONTEND CODE - File Upload Component
// ============================================

import { useState, useRef } from 'react'
import axios from 'axios'

const FileUpload = ({ onUploadSuccess, onUploadError, onLoading, onReset, hasResults }) => {
  const [selectedFile, setSelectedFile] = useState(null)
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file)
    } else {
      onUploadError('Please select a valid PDF file')
    }
  }

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0]
      if (file.type === 'application/pdf') {
        setSelectedFile(file)
      } else {
        onUploadError('Please drop a valid PDF file')
      }
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      onUploadError('Please select a file first')
      return
    }

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      onLoading(true)
      onUploadError(null)

      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes timeout
      })

      onUploadSuccess(response.data)
    } catch (error) {
      if (error.response) {
        onUploadError(error.response.data.error || 'Upload failed')
      } else if (error.request) {
        onUploadError('No response from server. Please check your connection.')
      } else {
        onUploadError('Error uploading file: ' + error.message)
      }
    } finally {
      onLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    onReset()
  }

  return (
    <div className="file-upload-container">
      <div
        className={`drop-zone ${dragActive ? 'active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          style={{ display: 'none' }}
        />
        
        <div className="drop-zone-content">
          <span className="upload-icon">📄</span>
          {selectedFile ? (
            <>
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">
                {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </>
          ) : (
            <>
              <p>Drag and drop a PDF file here</p>
              <p className="or-text">or</p>
              <button type="button" className="browse-button">
                Browse Files
              </button>
            </>
          )}
        </div>
      </div>

      <div className="button-group">
        {selectedFile && !hasResults && (
          <button onClick={handleUpload} className="upload-button">
            🚀 Process PDF
          </button>
        )}
        
        {(selectedFile || hasResults) && (
          <button onClick={handleReset} className="reset-button">
            🔄 Upload New File
          </button>
        )}
      </div>
    </div>
  )
}

export default FileUpload
