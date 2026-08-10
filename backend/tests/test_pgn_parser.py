import pytest
from app.services.pgn_parser import PGNParser

# PGN de exemplo para testes
SAMPLE_PGN = """[Event "Test Game"]
[Site "Test Site"]
[Date "2024.01.15"]
[Round "1"]
[White "Player One"]
[Black "Player Two"]
[Result "1-0"]
[ECO "C20"]
[WhiteElo "2000"]
[BlackElo "1900"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4 5. c3 Ba5 6. d4 exd4 7. O-O d3 8. Qxd3 Qe7 9. e5 Nge7 10. Re1 O-O 1-0
"""

INVALID_PGN = "This is not a valid PGN"

class TestPGNParser:
    def test_parse_pgn_valid(self):
        """Testa parsing de um PGN válido"""
        result = PGNParser.parse_pgn(SAMPLE_PGN)

        assert result["white"] == "Player One"
        assert result["black"] == "Player Two"
        assert result["result"] == "1-0"
        assert result["eco"] == "C20"
        assert result["move_count"] == 20
        assert len(result["moves"]) == 20

    def test_parse_pgn_invalid(self):
        """Testa parsing de um PGN inválido"""
        with pytest.raises(ValueError):
            PGNParser.parse_pgn(INVALID_PGN)

    def test_get_fen_at_move(self):
        """Testa extração de FEN em um movimento específico"""
        fen = PGNParser.get_fen_at_move(SAMPLE_PGN, 1)
        assert fen is not None
        assert "rnbqkbnr" in fen  # Contém peças pretas na posição inicial

    def test_get_fen_at_move_invalid(self):
        """Testa extração de FEN com movimento inválido"""
        fen = PGNParser.get_fen_at_move(SAMPLE_PGN, 999)
        assert fen is None

    def test_get_all_fens(self):
        """Testa extração de todas as FENs"""
        fens = PGNParser.get_all_fens(SAMPLE_PGN)

        assert len(fens) == 21  # Posição inicial + 20 movimentos
        assert fens[0][0] == 0  # Primeira é a posição inicial
        assert fens[-1][0] == 20  # Última é o movimento 20

    def test_get_move_san(self):
        """Testa extração de movimento em SAN"""
        san = PGNParser.get_move_san(SAMPLE_PGN, 1)
        assert san == "e4"

    def test_get_moves_with_san(self):
        """Testa extração de todos os movimentos com SAN"""
        moves = PGNParser.get_moves_with_san(SAMPLE_PGN)

        assert len(moves) == 20
        assert moves[0]["san"] == "e4"
        assert moves[0]["number"] == 1
        assert "fen_before" in moves[0]
        assert "fen_after" in moves[0]

    def test_validate_pgn_valid(self):
        """Testa validação de PGN válido"""
        is_valid, message = PGNParser.validate_pgn(SAMPLE_PGN)
        assert is_valid is True

    def test_validate_pgn_invalid(self):
        """Testa validação de PGN inválido"""
        is_valid, message = PGNParser.validate_pgn(INVALID_PGN)
        assert is_valid is False

    def test_get_game_summary(self):
        """Testa geração de resumo do jogo"""
        summary = PGNParser.get_game_summary(SAMPLE_PGN)

        assert summary["white_player"] == "Player One"
        assert summary["black_player"] == "Player Two"
        assert summary["result"] == "1-0"
        assert summary["result_text"] == "Brancas venceram"
        assert summary["total_moves"] == 20
        assert "final_fen" in summary

    def test_extract_opening_phase(self):
        """Testa extração da fase de abertura"""
        opening = PGNParser.extract_opening_phase(SAMPLE_PGN, max_moves=5)

        assert len(opening) == 5
        assert opening[0]["san"] == "e4"

    def test_parse_multiple_pgns(self):
        """Testa parsing de múltiplos PGNs"""
        multi_pgn = SAMPLE_PGN + "\n\n" + SAMPLE_PGN
        games = PGNParser.parse_multiple_pgns(multi_pgn)

        assert len(games) == 2
        assert games[0]["white"] == "Player One"
        assert games[1]["white"] == "Player One"