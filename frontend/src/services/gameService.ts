import { Chess } from 'chess.js'

export interface GameMove {
  moveNumber: number
  white: string
  black?: string
  whiteFen: string
  blackFen?: string
}

export class GameService {
  static parsePGN(pgn: string): GameMove[] {
    const game = new Chess()
    const moves: GameMove[] = []

    const cleanPGN = pgn
      .replace(/|$$.*?$$|/g, '')
      .replace(/\{.*?\}/g, '')
      .trim()

    // Extrair movimentos
    const moveRegex = /(\d+)\.\s+(\S+)\s+(\S+)?/g
    let match

    while ((match = moveRegex.exec(cleanPGN)) !== null) {
      const moveNumber = parseInt(match[1])
      const whiteMove = match[2]
      const blackMove = match[3]

      game.reset()
      const tempGame = new Chess()

      // Reconstruir posição até este movimento
      for (const m of moves) {
        tempGame.move(m.white, { sloppy: true })
        if (m.black) {
          tempGame.move(m.black, { sloppy: true })
        }
      }

      // Adicionar movimento branco
      tempGame.move(whiteMove, { sloppy: true })
      const whiteFen = tempGame.fen()

      let blackFen: string | undefined
      if (blackMove) {
        tempGame.move(blackMove, { sloppy: true })
        blackFen = tempGame.fen()
      }

      moves.push({
        moveNumber,
        white: whiteMove,
        black: blackMove,
        whiteFen,
        blackFen,
      })
    }

    return moves
  }

  static getFENSequence(pgn: string): string[] {
    const game = new Chess()
    const fens: string[] = [game.fen()] // FEN inicial

    const cleanPGN = pgn
      .replace(/|$$.*?$$|/g, '')
      .replace(/\{.*?\}/g, '')
      .trim()

    const moveRegex = /(\d+)\.\s+(\S+)\s+(\S+)?/g
    let match

    while ((match = moveRegex.exec(cleanPGN)) !== null) {
      const whiteMove = match[2]
      const blackMove = match[3]

      try {
        game.move(whiteMove, { sloppy: true })
        fens.push(game.fen())

        if (blackMove) {
          game.move(blackMove, { sloppy: true })
          fens.push(game.fen())
        }
      } catch (e) {
        console.error(`Erro ao processar movimento: ${whiteMove}`)
      }
    }

    return fens
  }
}