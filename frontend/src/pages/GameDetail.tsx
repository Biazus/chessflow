// frontend/src/pages/GameDetail.tsx
import { useState, useEffect, useMemo, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { ChessboardComponent } from '../components/Chessboard'
import { MoveList } from '../components/MoveList'
import { AnalysisPanel } from '../components/AnalysisPanel'
import { PgnModal } from '../components/PgnModal'
import { GameService, PositionDto, PositionAnalysis } from '../services/gameService'
import { AnalysisCache } from '../services/analysisCache'
import { ExpandableCard } from '../components/ExpandableCard'

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
  const [isPgnModalOpen, setIsPgnModalOpen] = useState(false)

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
  const currentAnalysis = currentMoveIndex > 0 ? positionAnalyses[currentMoveIndex - 1] : undefined

   const isAnalysisLoading =
  currentMoveIndex > 0 &&
  !currentAnalysis &&
  (analysisStatus === 'pending' || analysisStatus === 'analyzing')

    const analysisBadge =
      currentAnalysis && !isAnalysisLoading
        ? currentAnalysis.is_mate !== null
          ? `M${Math.abs(currentAnalysis.is_mate)}`
          : currentAnalysis.evaluation !== null
          ? (currentAnalysis.evaluation / 100).toFixed(1)
          : null
        : null

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
        <div className="game-header-row">
  <button onClick={() => navigate('/dashboard')} className="btn-back">
    ← Voltar
  </button>

  <div className="game-summary-card">
    <div className="game-summary-title">
      <h2>
        {game.white_player || 'Unknown'} vs {game.black_player || 'Unknown'}
      </h2>
      <span className={`result result-${game.result.replace(/[\/\-]/g, '')}`}>
        {game.result}
      </span>
    </div>

    <div className="game-summary-meta">
      <span>
        <strong>Abertura:</strong> {game.opening_name || 'N/A'}
      </span>
      <span>
        <strong>ECO:</strong> {game.eco_code || 'N/A'}
      </span>
      <span>
        <strong>Data:</strong>{' '}
        {game.played_at ? new Date(game.played_at).toLocaleDateString() : 'N/A'}
      </span>
      <span>
        <strong>Importado:</strong> {new Date(game.imported_at).toLocaleDateString()}
      </span>
      <button className="btn-pgn-link" onClick={() => setIsPgnModalOpen(true)}>
        Ver PGN original
      </button>
    </div>
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
            <div className="board-frame">
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
          </div>

          <div className="moves-column">
              <ExpandableCard
                title="Movimentos"
                defaultOpen={true}
                headerExtra={<span className="card-header-badge">{moves.length} lances</span>}
              >
                <MoveList
                  moves={moves}
                  currentMoveIndex={currentMoveIndex - 1}
                  onMoveClick={handleMoveClick}
                />
              </ExpandableCard>

              <ExpandableCard
                title="Análise"
                defaultOpen={true}
                headerExtra={
                  analysisBadge ? <span className="card-header-badge">{analysisBadge}</span> : null
                }
              >
                <AnalysisPanel
                  evaluation={currentAnalysis?.evaluation ?? null}
                  isMate={currentAnalysis?.is_mate ?? null}
                  topMoves={currentAnalysis?.top_moves ?? []}
                  bestMove={currentAnalysis?.best_move ?? null}
                  isLoading={isAnalysisLoading}
                />
              </ExpandableCard>
            </div>
        </div>

        <div className="game-actions">
          <button className="btn-export">Exportar PGN</button>
        </div>
      </div>

      <PgnModal
        pgn={game.pgn}
        isOpen={isPgnModalOpen}
        onClose={() => setIsPgnModalOpen(false)}
      />
    </div>
  )
}