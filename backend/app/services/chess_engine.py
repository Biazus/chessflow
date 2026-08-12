from stockfish import Stockfish
from app.config import get_settings
import time
from typing import Dict, List, Optional

settings = get_settings()

class ChessEngineService:
    """Serviço para análise de posições com Stockfish"""

    def __init__(self):
        try:
            self.engine = Stockfish(
                path=settings.STOCKFISH_PATH,
                depth=settings.DEFAULT_ANALYSIS_DEPTH,
                parameters={
                    "Threads": 4,
                    "Hash": 256,
                    "MultiPV": 1
                }
            )
        except Exception as e:
            print(f"Erro ao inicializar Stockfish: {e}")
            self.engine = None

    def analyze_position(self, fen: str, depth: int = None) -> Dict:
        """
        Analisa uma posição FEN
        Retorna dict com melhor movimento, avaliação e top moves
        """
        if self.engine is None:
            return {
                "success": False,
                "error": "Stockfish não disponível"
            }

        if depth is None:
            depth = settings.DEFAULT_ANALYSIS_DEPTH

        try:
            self.engine.set_fen_position(fen)
            self.engine.set_depth(depth)

            start_time = time.time()

            # Obter melhor movimento
            best_move = self.engine.get_best_move()

            evaluation = self.engine.get_evaluation()

            # Obter top 5 movimentos
            top_moves = self.engine.get_top_moves(5)

            processing_time = time.time() - start_time

            return {
                "best_move": best_move,
                "evaluation": evaluation,
                "top_moves": top_moves,
                "processing_time": processing_time,
                "success": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def is_checkmate(self, fen: str) -> bool:
        """Verifica se a posição é xeque-mate"""
        if self.engine is None:
            return False

        try:
            self.engine.set_fen_position(fen)
            return self.engine.is_checkmate()
        except Exception as e:
            print(f"Erro ao verificar xeque-mate: {e}")
            return False

    def is_stalemate(self, fen: str) -> bool:
        """Verifica se a posição é empate por afogamento"""
        if self.engine is None:
            return False

        try:
            self.engine.set_fen_position(fen)
            return self.engine.is_stalemate()
        except Exception as e:
            print(f"Erro ao verificar afogamento: {e}")
            return False

    def is_check(self, fen: str) -> bool:
        """Verifica se há xeque"""
        if self.engine is None:
            return False

        try:
            self.engine.set_fen_position(fen)
            return self.engine.is_check()
        except Exception as e:
            print(f"Erro ao verificar xeque: {e}")
            return False

    def get_best_moves_line(self, fen: str, depth: int = None, num_moves: int = 3) -> List[str]:
        """
        Retorna as melhores linhas de jogo
        """
        if self.engine is None:
            return []

        if depth is None:
            depth = settings.DEFAULT_ANALYSIS_DEPTH

        try:
            self.engine.set_fen_position(fen)
            self.engine.set_depth(depth)
            top_moves = self.engine.get_top_moves(num_moves)

            lines = []
            for move_info in top_moves:
                if "Line" in move_info:
                    lines.append(move_info["Line"])

            return lines
        except Exception as e:
            print(f"Erro ao obter linhas: {e}")
            return []