import './MoveList.css'

interface Move {
  number: number
  white: string
  black?: string
}

interface MoveListProps {
  moves: string[]
  currentMoveIndex: number
  onMoveClick: (index: number) => void
}

export const MoveList: React.FC<MoveListProps> = ({
  moves,
  currentMoveIndex,
  onMoveClick,
}) => {
  // Converter movimentos em notação algébrica para pares (white, black)
  const movePairs: Move[] = []
  for (let i = 0; i < moves.length; i += 2) {
    movePairs.push({
      number: Math.floor(i / 2) + 1,
      white: moves[i],
      black: moves[i + 1],
    })
  }

  return (
    <div className="move-list">
      <h3>Movimentos</h3>
      <div className="moves-container">
        {movePairs.map((pair) => (
          <div key={pair.number} className="move-pair">
            <span className="move-number">{pair.number}.</span>
            <button
              className={`move-button ${
                currentMoveIndex === (pair.number - 1) * 2 ? 'active' : ''
              }`}
              onClick={() => onMoveClick((pair.number - 1) * 2)}
            >
              {pair.white}
            </button>
            {pair.black && (
              <button
                className={`move-button ${
                  currentMoveIndex === (pair.number - 1) * 2 + 1 ? 'active' : ''
                }`}
                onClick={() => onMoveClick((pair.number - 1) * 2 + 1)}
              >
                {pair.black}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}