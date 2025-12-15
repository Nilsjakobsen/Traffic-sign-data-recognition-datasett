// ============================================
// FRONTEND CODE - Sign List Component
// ============================================

import SignCard from './SignCard'

const SignList = ({ signs, sessionId }) => {
  const downloadCSV = () => {
    // Create CSV content
    const headers = ['Filename', 'Predicted Class', 'Confidence']
    const rows = signs.map(sign => [
      sign.filename,
      sign.predicted_class,
      (sign.confidence * 100).toFixed(2) + '%'
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n')

    // Create download link
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'sign_predictions.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="sign-list-container">
      <div className="sign-list-header">
        <h2>🎯 Detected Signs ({signs.length})</h2>
        <button onClick={downloadCSV} className="download-button">
          📥 Download CSV
        </button>
      </div>

      <div className="sign-grid">
        {signs.map((sign, index) => (
          <SignCard 
            key={index} 
            sign={sign} 
            sessionId={sessionId}
          />
        ))}
      </div>

      <div className="summary">
        <h3>Summary</h3>
        <p>Total signs detected: <strong>{signs.length}</strong></p>
        <p>Average confidence: <strong>
          {(signs.reduce((acc, s) => acc + s.confidence, 0) / signs.length * 100).toFixed(2)}%
        </strong></p>
      </div>
    </div>
  )
}

export default SignList
