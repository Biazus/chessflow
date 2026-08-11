import type { PositionAnalysis } from './gameService'

const CACHE_PREFIX = 'chessflow_analysis_'
const CACHE_VERSION = 1

interface CachedAnalysis {
  version: number
  pgnHash: string
  analyses: PositionAnalysis[]
}

// Hash simples só para invalidar o cache se o PGN mudar; não precisa ser
// criptográfico, é apenas uma checagem de integridade local.
function hashString(str: string): string {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i)
    hash |= 0
  }
  return hash.toString(36)
}

export const AnalysisCache = {
  save(gameId: number, pgn: string, analyses: PositionAnalysis[]): void {
    const data: CachedAnalysis = {
      version: CACHE_VERSION,
      pgnHash: hashString(pgn),
      analyses,
    }
    try {
      localStorage.setItem(`${CACHE_PREFIX}${gameId}`, JSON.stringify(data))
    } catch (e) {
      console.warn('Não foi possível salvar análise no localStorage', e)
    }
  },

  load(gameId: number, pgn: string): PositionAnalysis[] | null {
    try {
      const raw = localStorage.getItem(`${CACHE_PREFIX}${gameId}`)
      if (!raw) return null

      const data: CachedAnalysis = JSON.parse(raw)
      if (data.version !== CACHE_VERSION) return null
      if (data.pgnHash !== hashString(pgn)) return null

      return data.analyses
    } catch (e) {
      return null
    }
  },
}