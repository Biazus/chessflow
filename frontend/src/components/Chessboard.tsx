import { Chessboard } from 'react-chessboard'
import { Chess } from 'chess.js'
import './Chessboard.css'

interface TopMoveArrow {
  Move: string
  Centipawn: number | null
  Mate: number | null
}

interface ChessboardProps {
  fen: string
  onMove?: (move: string) => void
  readOnly?: boolean
  topMoves?: TopMoveArrow[]
}

function parseUciMove(uci?: string | null): { from: string; to: string } | null {
  if (!uci || uci.length < 4) return null
  return { from: uci.slice(0, 2), to: uci.slice(2, 4) }
}

// Cores sólidas (sem alpha), luminosidade decrescente no mesmo tom de verde
const ARROW_COLORS = [
  '#14532d', // 1º melhor - verde bem escuro
  '#22c55e', // 2º melhor - verde médio
  '#a7f3d0', // 3º melhor - verde bem claro
]

export const ChessboardComponent: React.FC<ChessboardProps> = ({
  fen,
  onMove,
  readOnly = true,
  topMoves = [],
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

  const arrows = topMoves
    .slice(0, 3)
    .map((m, i) => {
      const parsed = parseUciMove(m.Move)
      if (!parsed) return null
      return [parsed.from, parsed.to, ARROW_COLORS[i]] as [string, string, string]
    })
    .filter((a): a is [string, string, string] => a !== null)

  return (
    <div className="chessboard-container">
      <Chessboard
        position={fen}
        onPieceDrop={handlePieceDrop}
        boardWidth={400}
        customArrows={arrows as any}
        customBoardStyle={{
          borderRadius: '4px',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
        }}
      />
    </div>
  )
}