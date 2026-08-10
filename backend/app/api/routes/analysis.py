from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.position import Position
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.services.chess_engine import ChessEngineService
from app.services.game_parser import GameParserService
from app.api.dependencies import get_current_user

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

@router.post("/game/{game_id}")
async def analyze_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    depth: int = 20
):
    """
    Analisa todas as posições de uma partida
    Nota: Implementação síncrona. Logo farei assíncrona com Celery TODO
    """
    from app.models.game import Game

    game = db.query(Game).filter(
        Game.id == game_id,
        Game.user_id == current_user.id
    ).first()

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada"
        )

    try:
        positions = db.query(Position).filter(
            Position.game_id == game_id
        ).all()

        analyzed_count = 0

        for position in positions:
            # Verificar se já foi analisada
            existing_analysis = db.query(Analysis).filter(
                Analysis.position_id == position.id
            ).first()

            if existing_analysis:
                analyzed_count += 1
                continue

            result = engine_service.analyze_position(position.fen, depth)

            if result["success"]:
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
                    position_id=position.id,
                    depth=depth,
                    best_move=result["best_move"],
                    evaluation=eval_value,
                    is_mate=is_mate,
                    top_moves=result["top_moves"],
                    processing_time=result["processing_time"]
                )

                db.add(analysis)
                analyzed_count += 1

        db.commit()

        game.analysis_status = "completed"
        db.commit()

        return {
            "status": "completed",
            "game_id": game_id,
            "positions_analyzed": analyzed_count,
            "total_positions": len(positions),
            "message": f"{analyzed_count} posições analisadas"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao analisar partida: {str(e)}"
        )