// frontend/src/components/AnalysisPanel.tsx
import './AnalysisPanel.css'

export interface TopMove {
  Move: string
  Centipawn: number
  Mate: number | null
}

interface AnalysisPanelProps {
  evaluation: number | null
  isMate: number | null
  topMoves: TopMove[]
  bestMove: string | null
  isLoading: boolean
}

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({
  evaluation,
  isMate,
  topMoves,
  bestMove,
  isLoading,
}) => {
  const getEvaluationColor = (evalScore: number | null) => {
    if (evalScore === null) return '#95a5a6'
    if (evalScore > 300) return '#27ae60'
    if (evalScore > 100) return '#2ecc71'
    if (evalScore > -100) return '#f39c12'
    if (evalScore > -300) return '#e67e22'
    return '#c0392b'
  }

  const formatEvaluation = (evalScore: number | null, mate: number | null) => {
    if (mate !== null) return `M${Math.abs(mate)}`
    if (evalScore === null) return '-'
    return (evalScore / 100).toFixed(1)
  }

  const getEvaluationLabel = (evalScore: number | null, mate: number | null) => {
    if (mate !== null) return mate > 0 ? 'Branco vence' : 'Preto vence'
    if (evalScore === null) return 'Sem análise'
    if (evalScore > 300) return 'Branco vencendo'
    if (evalScore > 100) return 'Branco melhor'
    if (evalScore > -100) return 'Equilibrado'
    if (evalScore > -300) return 'Preto melhor'
    return 'Preto vencendo'
  }

  if (isLoading) {
    return (
      <div className="analysis-loading">
        <p>Analisando posição...</p>
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <>
      <div className="evaluation-section">
        <div
          className="evaluation-bar"
          style={{ backgroundColor: getEvaluationColor(evaluation) }}
        >
          <span className="evaluation-value">{formatEvaluation(evaluation, isMate)}</span>
        </div>
        <p className="evaluation-label">{getEvaluationLabel(evaluation, isMate)}</p>
      </div>

      {bestMove && (
        <div className="best-move-section">
          <h4>Melhor Movimento</h4>
          <div className="best-move-box">
            <span className="move-notation">{bestMove}</span>
          </div>
        </div>
      )}

      {topMoves && topMoves.length > 0 && (
        <div className="top-moves-section">
          <h4>Principais Movimentos</h4>
          <div className="top-moves-list">
            {topMoves.map((move, index) => (
              <div key={index} className={`top-move-item ${move.Move === bestMove ? 'best' : ''}`}>
                <span className="move-rank">#{index + 1}</span>
                <span className="move-notation">{move.Move}</span>
                <span className="move-eval">
                  {move.Mate !== null ? `M${Math.abs(move.Mate)}` : (move.Centipawn / 100).toFixed(1)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}