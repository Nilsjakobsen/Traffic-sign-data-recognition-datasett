// ============================================
// FRONTEND CODE - Sign Card Component
// ============================================

const SignCard = ({ sign, sessionId }) => {
  const imageUrl = `/api/sign-image/${sessionId}/${sign.image_path}`
  const confidencePercent = (sign.confidence * 100).toFixed(2)
  
  // Determine confidence level for styling
  const getConfidenceLevel = () => {
    if (sign.confidence >= 0.8) return 'high'
    if (sign.confidence >= 0.5) return 'medium'
    return 'low'
  }

  return (
    <div className="sign-card">
      <div className="sign-image-container">
        <img 
          src={imageUrl} 
          alt={sign.predicted_class}
          className="sign-image"
          onError={(e) => {
            e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect fill="%23ddd"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="%23999">No Image</text></svg>'
          }}
        />
      </div>
      
      <div className="sign-info">
        <h3 className="sign-class">{sign.predicted_class}</h3>
        
        <div className={`confidence-bar ${getConfidenceLevel()}`}>
          <div 
            className="confidence-fill" 
            style={{ width: `${confidencePercent}%` }}
          />
          <span className="confidence-text">{confidencePercent}%</span>
        </div>
        
        <p className="sign-filename">{sign.filename}</p>
      </div>
    </div>
  )
}

export default SignCard
