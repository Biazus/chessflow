// frontend/src/pages/GameDetail.tsx
import { useState, useEffect, useMemo, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { ChessboardComponent } from '../components/Chessboard'
import { MoveList } from '../components/MoveList'
import { AnalysisPanel } from '../components/AnalysisPanel'
import { GameService, PositionDto, PositionAnalysis } from '../services/gameService'
import { AnalysisCache } from '../services/analysisCache'
import api, { triggerGameAnalysis, getGameAnalysis } from '../services/api'
import './GameDetail.css'

interface Game {
  id: number
  white_player: string | null
  black_player: string | null
  result: string
  eco_code: string | null
  opening_name: string | null
  pgn: string
  imported_at: string
  played_at: string | null
  positions: PositionDto[]
}

type AnalysisStatus = 'idle' | 'pending' | 'analyzing' | 'completed' | 'failed'

const POLL_INTERVAL_MS = 2000

export const GameDetail: React.FC = () => {
  const { gameId } = useParams<{ gameId: string }>()
  const navigate = useNavigate()

  const [game, setGame] = useState<Game | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [currentMoveIndex, setCurrentMoveIndex] = useState(0)
  const [positionAnalyses, setPositionAnalyses] = useState<PositionAnalysis[]>([])
  const [analysisStatus, setAnalysisStatus] = useState<AnalysisStatus>('idle')

  const pollRef = useRef<number | null>(null)

  useEffect(() => {
    loadGame()
  }, [gameId])

  useEffect(() => {
    if (!game) return

    const cached = AnalysisCache.load(game.id, game.pgn)
    if (cached && cached.length === game.positions.length) {
      setPositionAnalyses(cached)
      setAnalysisStatus('completed')
      return
    }

    startAnalysisFlow(game)

    return () => {
      if (pollRef.current) {
        window.clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [game])

  const loadGame = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.get(`/api/games/${gameId}`)
      setGame(response.data)
    } catch (err) {
      setError('Erro ao carregar partida')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const mergeAnalysisResult = (g: Game, analyses: PositionAnalysis[], status: AnalysisStatus) => {
    setPositionAnalyses(analyses)
    setAnalysisStatus(status)
    if (status === 'completed') {
      AnalysisCache.save(g.id, g.pgn, analyses)
    }
  }

  const startPolling = (g: Game) => {
    if (pollRef.current) return
    pollRef.current = window.setInterval(async () => {
      try {
        const response = await getGameAnalysis(g.id)
        const { status, analyses } = response.data
        mergeAnalysisResult(g, analyses, status)

        if (status === 'completed' || status === 'failed') {
          if (pollRef.current) {
            window.clearInterval(pollRef.current)
            pollRef.current = null
          }
        }
      } catch (err) {
        console.error('Erro ao consultar status da análise', err)
      }
    }, POLL_INTERVAL_MS)
  }

  const startAnalysisFlow = async (g: Game) => {
    try {
      const response = await getGameAnalysis(g.id)
      const { status, analyses } = response.data

      if (status === 'completed') {
        mergeAnalysisResult(g, analyses, 'completed')
        return
      }

      setPositionAnalyses(analyses)
      setAnalysisStatus(status)

      if (status === 'analyzing') {
        startPolling(g)
        return
      }

      // status pending (nunca disparado) ou failed (tentar de novo)
      await triggerGameAnalysis(g.id)
      setAnalysisStatus('pending')
      startPolling(g)
    } catch (err) {
      console.error('Erro ao iniciar análise da partida', err)
      setAnalysisStatus('failed')
    }
  }

  const handleRetryAnalysis = () => {
    if (game) startAnalysisFlow(game)
  }

  const fenSequence = useMemo(
    () => (game ? GameService.buildFenSequence(game.positions) : ['rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1']),
    [game]
  )
  const moves = useMemo(
    () => (game ? GameService.buildMoveList(game.positions) : []),
    [game]
  )

  const currentFen = fenSequence[currentMoveIndex] || fenSequence[0]
  // positionAnalyses[i] corresponde a fenSequence[i + 1] (a posição inicial,
  // índice 0, não tem análise associada).
  const currentAnalysis = currentMoveIndex > 0 ? positionAnalyses[currentMoveIndex - 1] : undefined

  const analyzedCount = positionAnalyses.filter(
    (p) => p.evaluation !== null || p.is_mate !== null
  ).length
  const totalCount = positionAnalyses.length || game?.positions.length || 0

  const handleMoveClick = (index: number) => setCurrentMoveIndex(index + 1)
  const handleNextMove = () => setCurrentMoveIndex((i) => Math.min(i + 1, fenSequence.length - 1))
  const handlePreviousMove = () => setCurrentMoveIndex((i) => Math.max(i - 1, 0))
  const handleFirstMove = () => setCurrentMoveIndex(0)
  const handleLastMove = () => setCurrentMoveIndex(fenSequence.length - 1)

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

  return (
    <div className="game-detail">
      <Navbar />

      <div className="game-detail-container">
        <button onClick={() => navigate('/dashboard')} className="btn-back">
          ← Voltar
        </button>

        <div className="game-detail-header">
          <h2>
            {game.white_player || 'Unknown'} vs {game.black_player || 'Unknown'}
          </h2>
          <span className={`result result-${game.result.replace(/[\/\-]/g, '')}`}>
            {game.result}
          </span>
        </div>

        <div className="game-detail-info">
          <div className="info-item">
            <strong>Abertura:</strong>
            <span>{game.opening_name || 'N/A'}</span>
          </div>
          <div className="info-item">
            <strong>ECO:</strong>
            <span>{game.eco_code || 'N/A'}</span>
          </div>
          <div className="info-item">
            <strong>Data da partida:</strong>
            <span>{game.played_at ? new Date(game.played_at).toLocaleDateString() : 'N/A'}</span>
          </div>
          <div className="info-item">
            <strong>Importado:</strong>
            <span>{new Date(game.imported_at).toLocaleDateString()}</span>
          </div>
        </div>

        {(analysisStatus === 'pending' || analysisStatus === 'analyzing') && (
          <div className="analysis-banner analysis-banner-processing">
            Analisando a partida... {analyzedCount}/{totalCount} posições avaliadas
          </div>
        )}

        {analysisStatus === 'failed' && (
          <div className="analysis-banner analysis-banner-error">
            Falha ao analisar a partida.{' '}
            <button onClick={handleRetryAnalysis} className="btn-retry-analysis">
              Tentar novamente
            </button>
          </div>
        )}

        <div className="game-board-section">
          <div className="board-column">
            <ChessboardComponent
              fen={currentFen}
              readOnly={true}
              topMoves={currentAnalysis?.top_moves ?? []}
            />

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
              currentMoveIndex={currentMoveIndex - 1}
              onMoveClick={handleMoveClick}
            />
            <AnalysisPanel
              evaluation={currentAnalysis?.evaluation ?? null}
              isMate={currentAnalysis?.is_mate ?? null}
              topMoves={currentAnalysis?.top_moves ?? []}
              bestMove={currentAnalysis?.best_move ?? null}
              isLoading={
                currentMoveIndex > 0 &&
                !currentAnalysis &&
                (analysisStatus === 'pending' || analysisStatus === 'analyzing')
              }
            />
          </div>
        </div>

        <div className="game-pgn-section">
          <h3>PGN Completo</h3>
          <pre className="pgn-content">{game.pgn}</pre>
        </div>

        <div className="game-actions">
          <button className="btn-export">Exportar PGN</button>
        </div>
      </div>
    </div>
  )
}