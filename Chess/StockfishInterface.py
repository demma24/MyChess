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
        stockfish_path = self._get_stockfish_path()
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
            self.depth = depth
            print("Successfully initialized Stockfish")
        except Exception as e:
            print(f"Failed to initialize Stockfish: {e}")
            self.engine = None

    def _get_stockfish_path(self):
        """
        Return the appropriate Stockfish path based on operating system.
        """
        if os.name == 'nt':  # Windows
            # Try multiple common Windows paths
            possible_paths = [
                "stockfish/stockfish-windows-x86-64-bmi2.exe",
                "stockfish/stockfish/stockfish-windows-x86-64-bmi2.exe",
                "stockfish-windows-x86-64-bmi2.exe",
                "engine/stockfish-windows-x86-64-bmi2.exe",
                r"C:\Program Files\Stockfish\stockfish-windows-x86-64-bmi2.exe"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            raise FileNotFoundError(f"Stockfish not found in any of: {possible_paths}")
        else:  # Linux/Mac
            possible_paths = [
                "stockfish/stockfish",
                "/usr/local/bin/stockfish",
                "/usr/bin/stockfish"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            raise FileNotFoundError(f"Stockfish not found in any of: {possible_paths}")

    def get_best_move(self, game_state, time_limit=2.0):
        """
        Get the best move for the current position.
        """
        if not self.engine:
            print("Engine not initialized")
            return None

        try:
            board = self._convert_to_chess_board(game_state)

            # Get the best move using play rather than analyse
            result = self.engine.play(board, chess.engine.Limit(time=time_limit))

            if result.move is None:
                print("No legal moves available")
                return None

            # Convert the move to algebraic notation
            from_square = chess.square_name(result.move.from_square)
            to_square = chess.square_name(result.move.to_square)
            move_str = from_square + to_square

            # Get the evaluation
            info = self.engine.analyse(board, chess.engine.Limit(time=0.1))
            score = info["score"].relative.score(mate_score=100000)

            return (move_str, score / 100 if score else 0, [str(result.move)])

        except Exception as e:
            print(f"Error getting best move: {e}")
            return None

    def _convert_to_chess_board(self, game_state):
        """
        Convert our GameState to chess.Board format
        """
        try:
            board = chess.Board()
            board.clear()

            # Place pieces on the board
            for row in range(8):
                for col in range(8):
                    piece = game_state.board[row][col]
                    if piece != "--":
                        color = chess.WHITE if piece[0] == 'w' else chess.BLACK
                        piece_type = piece[1].lower()  # Convert to lowercase for consistency
                        square = chess.square(col, 7 - row)  # Convert coordinates

                        # Map piece types to chess.Piece symbols
                        piece_map = {'p': 'p', 'r': 'r', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k'}
                        if piece_type.lower() in piece_map:
                            piece_symbol = piece_map[piece_type.lower()]
                            if color == chess.WHITE:
                                piece_symbol = piece_symbol.upper()
                            board.set_piece_at(square, chess.Piece.from_symbol(piece_symbol))

            # Set turn
            board.turn = game_state.whiteToMove
            return board

        except Exception as e:
            print(f"Error converting board: {e}")
            raise

    def close(self):
        """
        Properly close the engine.
        """
        if self.engine:
            try:
                self.engine.quit()
                print("Engine closed successfully")
            except Exception as e:
                print(f"Error closing engine: {e}")