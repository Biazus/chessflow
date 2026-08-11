import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import './Chessboard.css'

interface ChessboardProps {
  fen: string
  onMove?: (move: string) => void
  readOnly?: boolean
  bestMove?: string | null // formato UCI, ex: "e2e4"
}

function parseUciMove(uci?: string | null): { from: string; to: string } | null {
  if (!uci || uci.length < 4) return null
  return { from: uci.slice(0, 2), to: uci.slice(2, 4) }
}

export const ChessboardComponent: React.FC<ChessboardProps> = ({
  fen,
  onMove,
  readOnly = true,
  bestMove,
}) => {
  const game = new Chess(fen)

  const handlePieceDrop = (sourceSquare: string, targetSquare: string) => {
    if (readOnly) return false

    const move = game.moves({ verbose: true }).find(
      (m) => m.from === sourceSquare && m.to === targetSquare
    )

    if (move) {
      game.move(move)
      onMove?.(game.fen())
      return true
    }

    return false
  }

  const highlight = parseUciMove(bestMove)
  const arrows = highlight ? [[highlight.from, highlight.to]] : []

  return (
    <div className="chessboard-container">
      <Chessboard
        position={fen}
        onPieceDrop={handlePieceDrop}
        boardWidth={400}
        customArrows={arrows as any}
        customArrowColor="rgb(21, 128, 61)"
        customBoardStyle={{
          borderRadius: '4px',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
        }}
      />
    </div>
  )
}