export interface TopMoveDto {
  Move: string
  Centipawn: number | null
  Mate: number | null
}

export interface PositionDto {
  move_number: number
  move_san: string
  fen: string
}

export interface PositionAnalysis extends PositionDto {
  evaluation: number | null
  is_mate: number | null
  best_move: string | null
  top_moves: TopMoveDto[]
}

const START_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

export class GameService {
  static buildFenSequence(positions: PositionDto[]): string[] {
    return [START_FEN, ...positions.map((p) => p.fen)]
  }

  static buildMoveList(positions: PositionDto[]): string[] {
    return positions.map((p) => p.move_san)
  }
}