# game_parser.py
import logging
import chess
import chess.pgn
from io import StringIO
from typing import List, Dict, Optional
from app.models.game import GameResult

logger = logging.getLogger(__name__)


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

            # Se não há movimentos, é um PGN inválido
            if not moves:
                return None

            # Extrair resultado
            result_str = game.headers.get("Result", "*")
            result = GameParserService._parse_result(result_str)

            # Extrair abertura (ECO)
            eco_code = game.headers.get("ECO", None)
            opening_name = game.headers.get("Opening", None)

            # Limpar headers padrão do chess.pgn
            white_player = game.headers.get("White", "Unknown")
            black_player = game.headers.get("Black", "Unknown")
            date = game.headers.get("EventDate", None)

            event = game.headers.get("Event", None)

            # chess.pgn preenche com "?" quando falta header
            if white_player == "?":
                white_player = "Unknown"
            if black_player == "?":
                black_player = "Unknown"
            if date == "????.??.??":
                date = None

            return {
                "white_player": white_player,
                "black_player": black_player,
                "result": result,
                "moves": moves,
                "event": event,
                "eco_code": eco_code,
                "opening_name": opening_name,
                "pgn": pgn_text,
                "date": date
            }
        except Exception as e:
            logger.warning("Erro ao parsear PGN: %s", e)
            return None

    @staticmethod
    def parse_multiple_pgns(pgn_text: str) -> List[Dict]:
        """
        Parseia múltiplas partidas em um arquivo PGN.

        Preserva o texto original de cada partida no campo "pgn",
        recortando o trecho correspondente do texto de entrada,
        em vez de reserializar o objeto game (o que alteraria a
        formatação/quebras de linha originais).
        """
        games = []
        pgn_io = StringIO(pgn_text)

        while True:
            start_pos = pgn_io.tell()
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
            end_pos = pgn_io.tell()

            original_pgn = pgn_text[start_pos:end_pos].strip()
            parsed = GameParserService.parse_pgn(original_pgn)
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
        if not fen:
            return False
        try:
            chess.Board(fen)
            return True
        except (ValueError, IndexError):
            return False

    @staticmethod
    def get_position_fen(moves: List[str], move_number: int) -> Optional[str]:
        """
        Retorna a FEN de uma posição específica após o movimento no índice
        move_number: índice do movimento (0-based)
        Retorna None se o índice for inválido
        """
        if move_number < 0 or move_number >= len(moves):
            return None

        try:
            board = chess.Board()

            for i, move_san in enumerate(moves):
                move = board.parse_san(move_san)
                board.push(move)

                if i == move_number:
                    return board.fen()

            return None
        except Exception as e:
            logger.warning("Erro ao gerar FEN: %s", e)
            return None