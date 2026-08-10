import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { ChessboardComponent } from '../components/Chessboard'
import { MoveList } from '../components/MoveList'
import { GameService } from '../services/gameService'
import api from '../services/api'
import './GameDetail.css'

interface Game {
  id: number
  white_player: string
  black_player: string
  event: string
  date: string
  result: string
  pgn: string
  created_at: string
}

export const GameDetail: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>()
  const navigate = useNavigate()
  const [game, setGame] = useState<Game | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fenSequence, setFenSequence] = useState<string[]>([])
  const [currentMoveIndex, setCurrentMoveIndex] = useState(0)
  const [moves, setMoves] = useState<string[]>([])

  useEffect(() => {
    loadGame()
  }, [gameId])

  useEffect(() => {
    if (game) {
      const fens = GameService.getFENSequence(game.pgn)
      setFenSequence(fens)
      setCurrentMoveIndex(0)

      // Extrair movimentos em notação algébrica
      const moveRegex = /(\d+)\.\s+(\S+)\s+(\S+)?/g
      const extractedMoves: string[] = []
      let match

      const cleanPGN = game.pgn
        .replace(/|$$.*?$$|/g, '')
        .replace(/\{.*?\}/g, '')
        .trim()

      while ((match = moveRegex.exec(cleanPGN)) !== null) {
        extractedMoves.push(match[2])
        if (match[3]) {
          extractedMoves.push(match[3])
        }
      }

      setMoves(extractedMoves)
    }
  }, [game])

  const loadGame = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.get(`/api/games/${gameId}`)
      setGame(response.data)
    } catch (err: any) {
      setError('Erro ao carregar partida')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleMoveClick = (index: number) => {
    setCurrentMoveIndex(index)
  }

  const handleNextMove = () => {
    if (currentMoveIndex < fenSequence.length - 1) {
      setCurrentMoveIndex(currentMoveIndex + 1)
    }
  }

  const handlePreviousMove = () => {
    if (currentMoveIndex > 0) {
      setCurrentMoveIndex(currentMoveIndex - 1)
    }
  }

  const handleFirstMove = () => {
    setCurrentMoveIndex(0)
  }

  const handleLastMove = () => {
    setCurrentMoveIndex(fenSequence.length - 1)
  }

  if (isLoading) {
    return (
      <div className="game-detail">
        <Navbar />
        <div className="loading">Carregando partida...</div>
      </div>
    )
  }

  if (error || !game) {
    return (
      <div className="game-detail">
        <Navbar />
        <div className="error-container">
          <p>{error || 'Partida não encontrada'}</p>
          <button onClick={() => navigate('/dashboard')} className="btn-back">
            ← Voltar ao Dashboard
          </button>
        </div>
      </div>
    )
  }

  const currentFen = fenSequence[currentMoveIndex] || 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

  return (
    <div className="game-detail">
      <Navbar />

      <div className="game-detail-container">
        <button onClick={() => navigate('/dashboard')} className="btn-back">
          ← Voltar
        </button>

        <div className="game-detail-header">
          <h2>
            {game.white_player} vs {game.black_player}
          </h2>
          <span className={`result result-${game.result.replace(/[\/\-]/g, '')}`}>
            {game.result}
          </span>
        </div>

        <div className="game-detail-info">
          <div className="info-item">
            <strong>Evento:</strong>
            <span>{game.event || 'N/A'}</span>
          </div>
          <div className="info-item">
            <strong>Data:</strong>
            <span>{game.date || 'N/A'}</span>
          </div>
          <div className="info-item">
            <strong>Importado:</strong>
            <span>{new Date(game.created_at).toLocaleDateString()}</span>
          </div>
        </div>

        <div className="game-board-section">
          <div className="board-column">
            <ChessboardComponent fen={currentFen} readOnly={true} />

            <div className="board-controls">
              <button onClick={handleFirstMove} className="control-btn" title="Início">
                ⏮️
              </button>
              <button onClick={handlePreviousMove} className="control-btn" title="Anterior">
                ⏪
              </button>
              <span className="move-counter">
                {currentMoveIndex + 1} / {fenSequence.length}
              </span>
              <button onClick={handleNextMove} className="control-btn" title="Próximo">
                ⏩
              </button>
              <button onClick={handleLastMove} className="control-btn" title="Fim">
                ⏭️
              </button>
            </div>
          </div>

          <div className="moves-column">
            <MoveList
              moves={moves}
              currentMoveIndex={currentMoveIndex}
              onMoveClick={handleMoveClick}
            />
          </div>
        </div>

        <div className="game-pgn-section">
          <h3>PGN Completo</h3>
          <pre className="pgn-content">{game.pgn}</pre>
        </div>

        <div className="game-actions">
          <button className="btn-analyze">Analisar Partida</button>
          <button className="btn-export">Exportar PGN</button>
        </div>
      </div>
    </div>
  )
}