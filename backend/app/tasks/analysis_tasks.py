# backend/app/tasks/analysis_tasks.py
import logging
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.game import Game
from app.models.position import Position
from app.models.analysis import Analysis
from app.services.chess_engine import ChessEngineService

logger = logging.getLogger(__name__)


@celery_app.task(name="analyze_game", bind=True)
def analyze_game_task(self, game_id: int, depth: int = 20):
    """
    Analisa todas as posições de uma partida, uma vez, e persiste o
    resultado no banco. Reentrante: posições já analisadas na mesma
    profundidade são puladas, então re-executar a task não duplica trabalho.
    """
    db = SessionLocal()
    try:
        game = db.query(Game).filter(Game.id == game_id).first()
        if game is None:
            logger.warning(f"Jogo {game_id} não encontrado para análise")
            return

        game.analysis_status = "analyzing"
        db.commit()

        positions = (
            db.query(Position)
            .filter(Position.game_id == game_id)
            .order_by(Position.move_number)
            .all()
        )

        engine = ChessEngineService()

        for position in positions:
            already_done = (
                db.query(Analysis)
                .filter(
                    Analysis.position_id == position.id,
                    Analysis.depth == depth,
                )
                .first()
            )
            if already_done:
                continue

            result = engine.analyze_position(position.fen, depth=depth)

            if not result.get("success"):
                logger.warning(
                    f"Falha ao analisar posição {position.id} (jogo {game_id}): "
                    f"{result.get('error')}"
                )
                continue

            evaluation = result.get("evaluation")
            eval_value = None
            is_mate = None

            if evaluation:
                if "value" in evaluation:
                    eval_value = evaluation["value"]
                if "mate" in evaluation:
                    is_mate = evaluation["mate"]

            db.add(
                Analysis(
                    user_id=game.user_id,
                    position_id=position.id,
                    depth=depth,
                    best_move=result.get("best_move"),
                    evaluation=eval_value,
                    is_mate=is_mate,
                    top_moves=result.get("top_moves"),
                    processing_time=result.get("processing_time"),
                )
            )
            db.commit()

        game.analysis_status = "completed"
        db.commit()


    except Exception:
        logger.exception(f"Erro ao analisar jogo {game_id}")
        db.rollback()
        game = db.query(Game).filter(Game.id == game_id).first()
        if game:
            game.analysis_status = "failed"
            db.commit()
    finally:
        db.close()