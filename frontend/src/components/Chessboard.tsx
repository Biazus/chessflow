import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import './Chessboard.css'

interface ChessboardProps {
  fen: string
  onMove?: (move: string) => void
  readOnly?: boolean
}

export const ChessboardComponent: React.FC<ChessboardProps> = ({
  fen,
  onMove,
  readOnly = true,
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

  return (
    <div className="chessboard-container">
      <Chessboard
        position={fen}
        onPieceDrop={handlePieceDrop}
        boardWidth={400}
        customBoardStyle={{
          borderRadius: '4px',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
        }}
      />
    </div>
  )
}