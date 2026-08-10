from stockfish import Stockfish
from app.config import get_settings
import time

settings = get_settings()

class ChessEngineService:
    def __init__(self):
        self.engine = Stockfish(
            path=settings.STOCKFISH_PATH,
            depth=settings.DEFAULT_ANALYSIS_DEPTH,
            parameters={
                "Threads": 4,
                "Hash": 256,
                "MultiPV": 5
            }
        )

    def analyze_position(self, fen: str, depth: int = None) -> dict:
        """Analisa uma posição FEN"""
        if depth is None:
            depth = settings.DEFAULT_ANALYSIS_DEPTH

        try:
            self.engine.set_fen_position(fen)
            self.engine.set_depth(depth)

            start_time = time.time()
            best_move = self.engine.get_best_move()
            evaluation = self.engine.get_evaluation()
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
        """Verifica se é xeque-mate"""
        self.engine.set_fen_position(fen)
        return self.engine.is_checkmate()

    def is_stalemate(self, fen: str) -> bool:
        """Verifica se é empate por afogamento"""
        self.engine.set_fen_position(fen)
        return self.engine.is_stalemate()