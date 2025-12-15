// ============================================
// FRONTEND CODE - Sign Table Component (Table View)
// ============================================

const SignTable = ({ signs, sessionId }) => {
  // Group signs by class and count them
  const signSummary = signs.reduce((acc, sign) => {
    const className = sign.predicted_class;
    if (!acc[className]) {
      acc[className] = {
        count: 0,
        signs: [],
        totalConfidence: 0
      };
    }
    acc[className].count++;
    acc[className].signs.push(sign);
    acc[className].totalConfidence += sign.confidence;
    return acc;
  }, {});

  const downloadCSV = () => {
    // Create CSV with columns: Symbol, Skilt, Størrelse, Antall
    const headers = ['Symbol', 'Skilt', 'Størrelse', 'Antall'];
    const rows = Object.entries(signSummary).map(([className, data]) => [
      className,
      className,
      '',  // Størrelse (size) - empty for now
      data.count
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sign_summary.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="sign-table-container">
      <div className="sign-table-header">
        <h2>📋 Oppsummering av Skilt ({signs.length} totalt)</h2>
        <button onClick={downloadCSV} className="download-button">
          📥 Last ned CSV
        </button>
      </div>

      <div className="table-wrapper">
        <table className="sign-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Skilt</th>
              <th>Størrelse</th>
              <th>Antall</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(signSummary)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([className, data]) => {
                const firstSign = data.signs[0];
                const imageUrl = `/api/sign-image/${sessionId}/${firstSign.image_path}`;
                const avgConfidence = (data.totalConfidence / data.count * 100).toFixed(1);

                return (
                  <tr key={className}>
                    <td className="symbol-cell">
                      <div className="symbol-image-wrapper">
                        <img 
                          src={imageUrl} 
                          alt={className}
                          className="symbol-image"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                        <div className="symbol-placeholder" style={{display: 'none'}}>
                          🚦
                        </div>
                      </div>
                    </td>
                    <td className="skilt-cell">
                      <strong>{className}</strong>
                      <div className="confidence-indicator">
                        <small>{avgConfidence}% sikkerhet</small>
                      </div>
                    </td>
                    <td className="size-cell">-</td>
                    <td className="count-cell">
                      <span className="count-badge">{data.count}</span>
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>

      <div className="table-summary">
        <p><strong>Totalt antall skilt:</strong> {signs.length}</p>
        <p><strong>Unike skilttyper:</strong> {Object.keys(signSummary).length}</p>
      </div>
    </div>
  );
};

export default SignTable;
