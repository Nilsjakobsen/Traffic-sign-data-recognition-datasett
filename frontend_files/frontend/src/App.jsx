// ============================================
// FRONTEND CODE - Main React Application
// ============================================

import { useState } from 'react'
import './App.css'
import FileUpload from './components/FileUpload'
import SignList from './components/SignList'
import SignTable from './components/SignTable'

function App() {
  const [signs, setSigns] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [sessionId, setSessionId] = useState(null)
  const [viewMode, setViewMode] = useState('table') // 'table' or 'grid'

  const handleUploadSuccess = (data) => {
    setSigns(data.signs)
    setSessionId(data.session_id)
    setError(null)
  }

  const handleUploadError = (errorMessage) => {
    setError(errorMessage)
    setSigns([])
    setSessionId(null)
  }

  const handleReset = () => {
    setSigns([])
    setError(null)
    setSessionId(null)
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>🚦 Traffic Sign Recognition System</h1>
        <p>Upload a PDF containing traffic plans to extract and identify traffic signs</p>
      </header>

      <main className="App-main">
        <FileUpload 
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
          onLoading={setLoading}
          onReset={handleReset}
          hasResults={signs.length > 0}
        />

        {error && (
          <div className="error-message">
            <h3>❌ Error</h3>
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>Processing your PDF... This may take a moment.</p>
          </div>
        )}

        {signs.length > 0 && !loading && (
          <>
            <div className="view-toggle">
              <button 
                className={`toggle-btn ${viewMode === 'table' ? 'active' : ''}`}
                onClick={() => setViewMode('table')}
              >
                📋 Tabellvisning
              </button>
              <button 
                className={`toggle-btn ${viewMode === 'grid' ? 'active' : ''}`}
                onClick={() => setViewMode('grid')}
              >
                🎨 Rutenettvisning
              </button>
            </div>

            {viewMode === 'table' ? (
              <SignTable signs={signs} sessionId={sessionId} />
            ) : (
              <SignList signs={signs} sessionId={sessionId} />
            )}
          </>
        )}

        {!loading && !error && signs.length === 0 && sessionId && (
          <div className="no-signs-message">
            <h3>ℹ️ No Signs Detected</h3>
            <p>No traffic signs were found in the uploaded PDF.</p>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Powered by Computer Vision and Deep Learning</p>
      </footer>
    </div>
  )
}

export default App
