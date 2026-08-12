import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import './Dashboard.css'

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

export const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [games, setGames] = useState<Game[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)

  useEffect(() => {
    loadGames()
  }, [])

  const loadGames = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.get('/api/games')
      setGames(response.data)
    } catch (err: any) {
      setError('Erro ao carregar partidas')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
    }
  }

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) return

    setIsUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      await api.post('/api/games/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setSelectedFile(null)
      await loadGames()
    } catch (err: any) {
      setError('Erro ao importar PGN')
      console.error(err)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="dashboard">
      <Navbar />

      <div className="dashboard-container">
        <div className="dashboard-header">
          <h2>Minhas Partidas</h2>
          <p>Bem-vindo, {user?.full_name || user?.username}!</p>
        </div>

        <div className="dashboard-content">
          <div className="upload-section">
            <h3>Importar Partida (PGN)</h3>
            <form onSubmit={handleUpload} className="upload-form">
              <div className="file-input-wrapper">
                <input
                  type="file"
                  accept=".pgn"
                  onChange={handleFileSelect}
                  id="pgn-file"
                  disabled={isUploading}
                />
                <label htmlFor="pgn-file">
                  {selectedFile ? selectedFile.name : 'Selecione um arquivo PGN'}
                </label>
              </div>
              <button
                type="submit"
                disabled={!selectedFile || isUploading}
                className="btn-upload"
              >
                {isUploading ? 'Importando...' : 'Importar'}
              </button>
            </form>
            {error && <div className="error-message">{error}</div>}
          </div>

          <div className="games-section">
            <h3>Partidas ({games.length})</h3>

            {isLoading ? (
              <div className="loading">Carregando partidas...</div>
            ) : games.length === 0 ? (
              <div className="empty-state">
                <p>Nenhuma partida importada ainda.</p>
                <p>Importe um arquivo PGN para começar!</p>
              </div>
            ) : (
              <div className="games-list">
                {games.map((game) => (
                  <div
                    key={game.id}
                    className="game-card"
                    onClick={() => navigate(`/games/${game.id}`)}
                  >
                    <div className="game-header">
                      <h4>
                        {game.white_player} vs {game.black_player}
                      </h4>
                      <span className={`result result-${game.result.replace(/[\/\-]/g, '')}`}>
                        {game.result}
                      </span>
                    </div>
                    <div className="game-info">
                      <p>
                        <strong>Evento:</strong> {game.event || 'N/A'}
                      </p>
                      <p>
                        <strong>Data:</strong> {game.date || 'N/A'}
                      </p>
                      <p>
                        <strong>Importado:</strong> {new Date(game.imported_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="game-action">
                      <span className="view-link">Ver detalhes →</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}