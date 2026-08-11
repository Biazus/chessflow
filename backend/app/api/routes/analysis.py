from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.game import Game
from app.models.position import Position
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, GameAnalysisStatusResponse
from app.services.chess_engine import ChessEngineService
from app.services.game_parser import GameParserService
from app.api.dependencies import get_current_user
from app.tasks.analysis_tasks import analyze_game_task
from app.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/analysis", tags=["analysis"])

# Instância global do engine (reutilizar entre requisições)
engine_service = ChessEngineService()

@router.post("/position", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def analyze_position(
    analysis_data: AnalysisCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analisa uma posição FEN específica com Stockfish
    """

    if not GameParserService.validate_fen(analysis_data.fen):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="FEN inválida"
        )
    print("DEPTH: ", analysis_data)
    try:
        result = engine_service.analyze_position(analysis_data.fen, analysis_data.depth)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao analisar: {result['error']}"
            )

        evaluation = result["evaluation"]
        eval_value = None
        is_mate = None

        if evaluation:
            if "value" in evaluation:
                eval_value = evaluation["value"]
            if "mate" in evaluation:
                is_mate = evaluation["mate"]

        analysis = Analysis(
            user_id=current_user.id,
            position_id=None,
            depth=analysis_data.depth,
            best_move=result["best_move"],
            evaluation=eval_value,
            is_mate=is_mate,
            top_moves=result["top_moves"],
            processing_time=result["processing_time"]
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar análise: {str(e)}"
        )

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análise não encontrada"
        )

    return analysis


@router.post("/game/{game_id}", status_code=202)
async def trigger_game_analysis(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = (
        db.query(Game)
        .filter(Game.id == game_id, Game.user_id == current_user.id)
        .first()
    )
    if game is None:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    if game.analysis_status in ("analyzing", "completed"):
        return {"status": game.analysis_status}

    game.analysis_status = "pending"
    db.commit()

    analyze_game_task.delay(game_id, settings.DEFAULT_ANALYSIS_DEPTH)
    return {"status": "pending"}


@router.get("/game/{game_id}", response_model=GameAnalysisStatusResponse)
async def get_game_analysis(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = (
        db.query(Game)
        .filter(Game.id == game_id, Game.user_id == current_user.id)
        .first()
    )
    if game is None:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    positions = (
        db.query(Position)
        .filter(Position.game_id == game_id)
        .order_by(Position.move_number)
        .all()
    )
    analyses = (
        db.query(Analysis)
        .filter(Analysis.position_id.in_([p.id for p in positions]))
        .all()
    )
    by_position = {a.position_id: a for a in analyses}

    results = [
        {
            "move_number": p.move_number,
            "move_san": p.move_san,
            "fen": p.fen,
            "evaluation": by_position[p.id].evaluation if p.id in by_position else None,
            "is_mate": by_position[p.id].is_mate if p.id in by_position else None,
            "best_move": by_position[p.id].best_move if p.id in by_position else None,
            "top_moves": by_position[p.id].top_moves if p.id in by_position else None,
        }
        for p in positions
    ]

    return {
        "status": game.analysis_status,
        "total_positions": len(positions),
        "analyzed_positions": len(analyses),
        "analyses": results,
    }