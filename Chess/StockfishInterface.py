import chess
import chess.engine
import os
from pathlib import Path


class StockfishInterface:
    def __init__(self, depth=15):
        """
        Initialize Stockfish interface.
        :param depth: How deep Stockfish should analyze (higher = stronger but slower)
        """
        # Path to Stockfish executable - needs to be adjusted for your system
        stockfish_path = self._get_stockfish_path()
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
            self.depth = depth
        except Exception as e:
            print(f"Failed to initialize Stockfish: {e}")
            self.engine = None

    def _get_stockfish_path(self):
        """
        Return the appropriate Stockfish path based on operating system.
        You'll need to modify these paths based on where Stockfish is installed.
        """
        if os.name == 'nt':  # Windows
            return "stockfish/stockfish-windows-x86-64.exe"
        elif os.name == 'posix':  # Linux/Mac
            return "stockfish/stockfish"
        else:
            raise OSError("Unsupported operating system")

    def get_best_move(self, game_state, time_limit=2.0):
        """
        Get the best move for the current position.
        :param game_state: Current GameState object
        :param time_limit: Time limit for analysis in seconds
        :return: tuple (best_move, evaluation, principal_variation)
        """
        if not self.engine:
            return None, None, None

        # Convert our game state to chess.Board
        board = self._convert_to_chess_board(game_state)

        try:
            # Get analysis from Stockfish
            result = self.engine.analyse(
                board,
                chess.engine.Limit(time=time_limit),
                info=chess.engine.INFO_ALL
            )

            # Extract best move and evaluation
            best_move = result["pv"][0]
            score = result["score"].relative.score(mate_score=100000)

            # Convert move to our format
            from_square = chess.square_name(best_move.from_square)
            to_square = chess.square_name(best_move.to_square)

            # Get principal variation (next best moves)
            pv = [move for move in result["pv"][:3]]  # Get top 3 moves

            return (from_square + to_square, score / 100, pv)

        except Exception as e:
            print(f"Error getting best move: {e}")
            return None, None, None

    def _convert_to_chess_board(self, game_state):
        """
        Convert our GameState to chess.Board format
        """
        # Create a new chess board
        board = chess.Board()
        board.clear()

        # Piece mapping from our format to FEN format
        piece_mapping = {
            'p': 'p', 'R': 'r', 'N': 'n', 'B': 'b', 'Q': 'q', 'K': 'k',
            'P': 'P', 'R': 'R', 'N': 'N', 'B': 'B', 'Q': 'Q', 'K': 'K'
        }

        # Place pieces on the board
        for row in range(8):
            for col in range(8):
                piece = game_state.board[row][col]
                if piece != "--":
                    color = chess.WHITE if piece[0] == 'w' else chess.BLACK
                    piece_type = piece_mapping[piece[1]]
                    square = chess.square(col, 7 - row)  # Convert coordinates
                    board.set_piece_at(square, chess.Piece.from_symbol(piece_type), color)

        # Set turn
        board.turn = game_state.whiteToMove

        return board

    def close(self):
        """
        Properly close the engine.
        """
        if self.engine:
            self.engine.quit()