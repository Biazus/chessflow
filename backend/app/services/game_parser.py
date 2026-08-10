import chess
import chess.pgn
from io import StringIO
from typing import List, Dict, Optional
from app.models.game import GameResult

class GameParserService:
    """Serviço para parsear e validar arquivos PGN"""

    @staticmethod
    def parse_pgn(pgn_text: str) -> Optional[Dict]:
        """
        Parseia um arquivo PGN e extrai informações
        Retorna dict com dados da partida ou None se inválido
        """
        try:
            pgn_io = StringIO(pgn_text)
            game = chess.pgn.read_game(pgn_io)

            if game is None:
                return None

            # Extrair movimentos
            moves = []
            board = game.board()
            for move in game.mainline_moves():
                moves.append(board.san(move))
                board.push(move)

            # Extrair resultado
            result_str = game.headers.get("Result", "*")
            result = GameParserService._parse_result(result_str)

            # Extrair abertura (ECO)
            eco_code = game.headers.get("ECO", None)
            opening_name = game.headers.get("Opening", None)

            return {
                "white_player": game.headers.get("White", "Unknown"),
                "black_player": game.headers.get("Black", "Unknown"),
                "result": result,
                "moves": moves,
                "eco_code": eco_code,
                "opening_name": opening_name,
                "pgn": pgn_text,
                "date": game.headers.get("Date", None)
            }
        except Exception as e:
            print(f"Erro ao parsear PGN: {e}")
            return None

    @staticmethod
    def parse_multiple_pgns(pgn_text: str) -> List[Dict]:
        """Parseia múltiplas partidas em um arquivo PGN"""
        games = []
        pgn_io = StringIO(pgn_text)

        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break

            parsed = GameParserService.parse_pgn(str(game))
            if parsed:
                games.append(parsed)

        return games

    @staticmethod
    def _parse_result(result_str: str) -> GameResult:
        """Converte string de resultado para enum"""
        if result_str == "1-0":
            return GameResult.WHITE_WIN
        elif result_str == "0-1":
            return GameResult.BLACK_WIN
        elif result_str == "1/2-1/2":
            return GameResult.DRAW
        else:
            return GameResult.UNKNOWN

    @staticmethod
    def validate_fen(fen: str) -> bool:
        """Valida se uma FEN é válida"""
        try:
            chess.Board(fen)
            return True
        except:
            return False

    @staticmethod
    def get_position_fen(moves: List[str], move_number: int) -> Optional[str]:
        """
        Retorna a FEN de uma posição específica dado uma lista de movimentos
        move_number: índice do movimento (0-based)
        """
        try:
            board = chess.Board()

            if move_number >= len(moves):
                return None

            for i, move_san in enumerate(moves):
                move = board.parse_san(move_san)
                board.push(move)

                if i == move_number:
                    return board.fen()

            return None
        except Exception as e:
            print(f"Erro ao gerar FEN: {e}")
            return None