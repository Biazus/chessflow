from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.game import Game
from app.models.position import Position
from app.schemas.game import GameCreate, GameResponse, GameDetailResponse
from app.services.game_parser import GameParserService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/games", tags=["games"])

@router.post("/import", status_code=status.HTTP_202_ACCEPTED)
async def import_pgn(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Importa arquivo PGN com uma ou múltiplas partidas
    Retorna task_id para acompanhar o progresso
    """
    try:
        content = await file.read()
        pgn_text = content.decode('utf-8')

        games_data = GameParserService.parse_multiple_pgns(pgn_text)

        if not games_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo PGN inválido ou vazio"
            )

        saved_games = []
        for game_data in games_data:
            game = Game(
                user_id=current_user.id,
                pgn=game_data["pgn"],
                white_player=game_data["white_player"],
                black_player=game_data["black_player"],
                result=game_data["result"],
                eco_code=game_data["eco_code"],
                opening_name=game_data["opening_name"],
                moves=game_data["moves"],
                analysis_status="pending"
            )

            db.add(game)
            db.flush()  # Gera ID sem fazer commit

            # Criar posições para cada movimento
            for move_idx, move_san in enumerate(game_data["moves"]):
                fen = GameParserService.get_position_fen(game_data["moves"], move_idx)

                if fen:
                    position = Position(
                        game_id=game.id,
                        fen=fen,
                        move_number=move_idx + 1,
                        move_san=move_san
                    )
                    db.add(position)

            saved_games.append(game)

        db.commit()

        return {
            "status": "imported",
            "games_count": len(saved_games),
            "message": f"{len(saved_games)} partida(s) importada(s) com sucesso"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao importar PGN: {str(e)}"
        )

@router.get("", response_model=List[GameResponse])
async def list_games(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """Lista todas as partidas do usuário"""
    games = db.query(Game).filter(
        Game.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return games

@router.get("/{game_id}", response_model=GameDetailResponse)
async def get_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(
        Game.id == game_id,
        Game.user_id == current_user.id
    ).first()

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada"
        )

    return game

@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    game = db.query(Game).filter(
        Game.id == game_id,
        Game.user_id == current_user.id
    ).first()

    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida não encontrada"
        )

    db.delete(game)
    db.commit()

    return None