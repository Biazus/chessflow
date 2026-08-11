# test_pgn_parser.py
import pytest
from io import StringIO
from app.models.game import GameResult
from app.services.game_parser import GameParserService

class TestGameParserService:
    """Testes para o GameParserService"""

    # PGN de exemplo: partida simples
    SIMPLE_PGN = """[Event "Test Game"]
[Site "?"]
[Date "2024.01.15"]
[Round "1"]
[White "Player A"]
[Black "Player B"]
[Result "1-0"]
[ECO "C20"]
[Opening "Italian Game"]

1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. b4 Bxb4 5. c3 Ba5 6. d4 exd4 7. cxd4 Bb6 8. d5 Na5 9. Nxb4 Nxb4 10. Bf4 d6 11. d6 Qe7 12. Qd5 c6 13. dxc6 bxc6 14. Qxd8+ Kxd8 15. O-O Kc7 16. Nc3 Nf6 17. Rfd1 Rd8 18. Rd4 Nxe4 19. Nxe4 Rxd4 20. Nxd4 Kd7 21. Bf4 Kc7 22. Rc1 Kb7 23. Rc3 a6 24. Rc4 Nd6 25. Rc7+ Ka8 26. Rxe7 Nxe7 27. Nxc6 Nf5 28. Bf1 Nd4 29. Bd3 Kb7 30. Nd8+ Kc8 31. Nxf7 Nf5 32. Bxf5 Kd7 33. Nd6 Ke6 34. Bf4 Kf6 35. Bd4+ Kg5 36. h4+ Kh5 37. Nf7 Kg4 38. Nxd8 Kxf4 39. Nf7 Kg3 40. Nd6 Kxf2 41. Nf5 Kg3 42. Nd4 Kxh4 43. Nf3 Kg4 44. Nd2 Kxf3 45. Nf3 Kg3 46. Nd4 Kf4 47. Nf3 Ke3 48. Nd4 Kd3 49. Nf3 Kc3 50. Nd4 Kb3 51. Nf3 Ka3 52. Nd4 Ka4 53. Nf3 Kb5 54. Nd4+ Kc5 55. Nf3 Kd5 56. Nd4 Ke4 57. Nf3 Kf4 58. Nd4 Kg3 59. Nf3 Kxf3 60. Kf1 Kg3 61. Kg1 Kh3 62. Kh1 a5 63. Kg1 a4 64. Kf1 a3 65. Ke1 a2 66. Kd1 a1=Q# 0-1"""

    DRAW_PGN = """[Event "Draw Game"]
[White "Player C"]
[Black "Player D"]
[Result "1/2-1/2"]

1. e4 e5 2. Nf3 Nf6 3. Nxe5 d6 4. Nf3 Nxe4 5. d4 d5 6. Bd3 Bg4 7. O-O Be7 8. Re1 O-O 9. c3 Nc6 10. h3 Bh5 11. Nbd2 Nf6 12. Nf1 Bg6 13. Ne3 Nh4 14. Nxh4 Bxh4 15. g3 Bg4 16. hxg4 Nxg4 17. Nxg4 Bxg4 18. Qd3 Bxd1 19. Rexd1 Qd7 20. Bf4 Rfe8 21. Rad1 Re6 22. Bxd6 Rxd6 23. Qxd6 Qxd6 24. Rxd6 a6 25. Rdd1 Kf8 26. Kf1 Ke7 27. Ke2 Kd6 28. Kd3 c6 29. Rf1 Ke5 30. Rf3 f6 31. Rg3 g6 32. Rg4 h5 33. Rg5 Kf4 34. Rxh5 Kg3 35. Rh1 Kxf2 36. Rf1+ Ke2 37. Rf4 Kd3 38. Rf3 Kc2 39. Rf2+ Kd3 40. Rf3 Kc2 1/2-1/2"""

    BLACK_WIN_PGN = """[Event "Black Win"]
[White "Player E"]
[Black "Player F"]
[Result "0-1"]

1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. Bg5 e6 7. f4 Be7 8. Qf3 Nbd7 9. O-O-O b5 10. a3 Bb7 11. Bxf6 Nxf6 12. g4 b4 13. axb4 Nxe4 14. Qg3 Nxc3 15. bxc3 Rc8 16. Kb1 Rxc3 17. Qxc3 Bxf4 18. Qf3 Bxf3 19. gxf3 Qc7 20. Bd3 Qc1+ 21. Ka2 Qa1# 0-1"""

    MINIMAL_PGN = "1. e4 e5 2. Nf3 Nc6"

    def test_parse_pgn_valid(self):
        """Testa parsing de um PGN válido"""
        result = GameParserService.parse_pgn(self.SIMPLE_PGN)

        assert result is not None
        assert result["white_player"] == "Player A"
        assert result["black_player"] == "Player B"
        assert result["result"] == GameResult.WHITE_WIN
        assert len(result["moves"]) > 0
        assert result["eco_code"] == "C20"
        assert result["opening_name"] == "Italian Game"

    def test_parse_pgn_draw(self):
        """Testa parsing de um PGN com resultado de empate"""
        result = GameParserService.parse_pgn(self.DRAW_PGN)

        assert result is not None
        assert result["result"] == GameResult.DRAW
        assert result["white_player"] == "Player C"
        assert result["black_player"] == "Player D"

    def test_parse_pgn_black_win(self):
        """Testa parsing de um PGN com vitória das pretas"""
        result = GameParserService.parse_pgn(self.BLACK_WIN_PGN)

        assert result is not None
        assert result["result"] == GameResult.BLACK_WIN

    def test_parse_pgn_invalid_no_moves(self):
        """
        Testa parsing de um PGN com headers válidos e bem formatados,
        mas sem nenhum lance no corpo do texto.
        """
        invalid_pgn = """[Event "No Moves"]
[White "A"]
[Black "B"]
[Result "*"]

"""
        result = GameParserService.parse_pgn(invalid_pgn)
        assert result is None

    def test_parse_pgn_invalid_malformed_headers(self):
        """Testa parsing de um PGN com headers concatenados/malformados"""
        invalid_pgn = "[Event \"No Moves\"][White \"A\"][Black \"B\"][Result \"*\"]"
        result = GameParserService.parse_pgn(invalid_pgn)
        assert result is None

    def test_parse_pgn_empty(self):
        """Testa parsing de um PGN vazio"""
        result = GameParserService.parse_pgn("")
        assert result is None

    def test_parse_multiple_pgns(self):
        """Testa parsing de múltiplas partidas"""
        combined_pgn = self.SIMPLE_PGN + "\n\n" + self.DRAW_PGN
        results = GameParserService.parse_multiple_pgns(combined_pgn)

        assert len(results) == 2
        assert results[0]["white_player"] == "Player A"
        assert results[1]["white_player"] == "Player C"

    def test_parse_multiple_pgns_preserves_original_text(self):
        """Testa se o texto original de cada partida é preservado ao parsear múltiplos PGNs"""
        combined_pgn = self.SIMPLE_PGN + "\n\n" + self.DRAW_PGN
        results = GameParserService.parse_multiple_pgns(combined_pgn)

        assert results[0]["pgn"].strip() == self.SIMPLE_PGN.strip()
        assert results[1]["pgn"].strip() == self.DRAW_PGN.strip()

    def test_parse_multiple_pgns_empty(self):
        """Testa parsing de múltiplas partidas vazio"""
        results = GameParserService.parse_multiple_pgns("")
        assert len(results) == 0

    def test_parse_result_white_win(self):
        """Testa conversão de resultado para vitória das brancas"""
        result = GameParserService._parse_result("1-0")
        assert result == GameResult.WHITE_WIN

    def test_parse_result_black_win(self):
        """Testa conversão de resultado para vitória das pretas"""
        result = GameParserService._parse_result("0-1")
        assert result == GameResult.BLACK_WIN

    def test_parse_result_draw(self):
        """Testa conversão de resultado para empate"""
        result = GameParserService._parse_result("1/2-1/2")
        assert result == GameResult.DRAW

    def test_parse_result_unknown(self):
        """Testa conversão de resultado desconhecido"""
        result = GameParserService._parse_result("*")
        assert result == GameResult.UNKNOWN

    def test_validate_fen_valid(self):
        """Testa validação de FEN válida"""
        valid_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert GameParserService.validate_fen(valid_fen) is True

    def test_validate_fen_invalid(self):
        """Testa validação de FEN inválida"""
        invalid_fen = "invalid fen string"
        assert GameParserService.validate_fen(invalid_fen) is False

    def test_validate_fen_empty(self):
        """Testa validação de FEN vazia"""
        assert GameParserService.validate_fen("") is False

    def test_get_position_fen_first_move(self):
        """Testa extração de FEN após o primeiro movimento"""
        moves = ["e4", "c5"]
        fen = GameParserService.get_position_fen(moves, 0)

        assert fen is not None
        assert GameParserService.validate_fen(fen)
        # Após e4, deve ser turno das pretas
        assert " b " in fen

    def test_get_position_fen_second_move(self):
        """Testa extração de FEN após o segundo movimento"""
        moves = ["e4", "c5"]
        fen = GameParserService.get_position_fen(moves, 1)

        assert fen is not None
        assert GameParserService.validate_fen(fen)
        # Após c5, deve ser turno das brancas
        assert " w " in fen

    def test_get_position_fen_middle_game(self):
        """Testa extração de FEN no meio da partida"""
        result = GameParserService.parse_pgn(self.SIMPLE_PGN)
        moves = result["moves"][:10]

        fen = GameParserService.get_position_fen(moves, 5)
        assert fen is not None
        assert GameParserService.validate_fen(fen)

    def test_get_position_fen_invalid_index_too_large(self):
        """Testa extração de FEN com índice muito grande"""
        moves = ["e4", "c5"]
        fen = GameParserService.get_position_fen(moves, 10)
        assert fen is None

    def test_get_position_fen_invalid_index_negative(self):
        """Testa extração de FEN com índice negativo"""
        moves = ["e4", "c5"]
        fen = GameParserService.get_position_fen(moves, -1)
        assert fen is None

    def test_get_position_fen_empty_moves(self):
        """Testa extração de FEN com lista de movimentos vazia"""
        fen = GameParserService.get_position_fen([], 0)
        assert fen is None

    def test_get_position_fen_all_moves(self):
        """Testa extração de FEN para todos os movimentos de uma partida"""
        result = GameParserService.parse_pgn(self.SIMPLE_PGN)
        moves = result["moves"]

        for i in range(len(moves)):
            fen = GameParserService.get_position_fen(moves, i)
            assert fen is not None, f"FEN inválida no movimento {i}"
            assert GameParserService.validate_fen(fen), f"FEN inválida no movimento {i}: {fen}"

    def test_moves_extraction(self):
        """Testa se os movimentos são extraídos corretamente"""
        result = GameParserService.parse_pgn(self.SIMPLE_PGN)
        moves = result["moves"]

        assert moves[0] == "e4"
        assert moves[1] == "e5"
        assert moves[2] == "Nf3"
        assert moves[3] == "Nc6"

    def test_pgn_preservation(self):
        """Testa se o PGN original é preservado ao parsear uma única partida"""
        result = GameParserService.parse_pgn(self.SIMPLE_PGN)
        assert result["pgn"] == self.SIMPLE_PGN

    def test_date_extraction(self):
        """Testa extração da data"""
        result = GameParserService.parse_pgn(self.SIMPLE_PGN)
        assert result["date"] == "2024.01.15"

    def test_missing_headers_defaults(self):
        """Testa parsing com headers faltando (usa valores padrão do chess.pgn)"""
        result = GameParserService.parse_pgn(self.MINIMAL_PGN)

        assert result is not None
        assert result["white_player"] == "Unknown"
        assert result["black_player"] == "Unknown"
        assert result["date"] is None
        assert result["eco_code"] is None
        assert result["opening_name"] is None

    def test_partial_headers(self):
        """Testa parsing com alguns headers presentes"""
        pgn_with_partial_headers = """[White "Alice"]
[Black "Bob"]

1. e4 e5 2. Nf3 Nc6"""

        result = GameParserService.parse_pgn(pgn_with_partial_headers)
        assert result is not None
        assert result["white_player"] == "Alice"
        assert result["black_player"] == "Bob"
        assert result["date"] is None

    def test_fen_consistency(self):
        """Testa se FENs geradas são consistentes"""
        moves = ["e4", "c5", "Nf3", "d6", "d4", "cxd4"]

        fen1 = GameParserService.get_position_fen(moves, 5)
        fen2 = GameParserService.get_position_fen(moves, 5)

        assert fen1 == fen2

    def test_fen_progression(self):
        """Testa se a progressão de FENs é lógica"""
        moves = ["e4", "e5"]

        fen_after_e4 = GameParserService.get_position_fen(moves, 0)
        fen_after_e5 = GameParserService.get_position_fen(moves, 1)

        # Devem ser diferentes
        assert fen_after_e4 != fen_after_e5

        # Ambas devem ser válidas
        assert GameParserService.validate_fen(fen_after_e4)
        assert GameParserService.validate_fen(fen_after_e5)