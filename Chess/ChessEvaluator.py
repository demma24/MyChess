class ChessEvaluator:
    # Piece values in centipawns
    PIECE_VALUES = {
        'p': 100,   # pawn
        'N': 320,   # knight
        'B': 330,   # bishop
        'R': 500,   # rook
        'Q': 900,   # queen
        'K': 20000  # king
    }
    
    # Piece position bonus tables
    PAWN_TABLE = [
        [0,  0,  0,  0,  0,  0,  0,  0],
        [50, 50, 50, 50, 50, 50, 50, 50],
        [10, 10, 20, 30, 30, 20, 10, 10],
        [5,  5, 10, 25, 25, 10,  5,  5],
        [0,  0,  0, 20, 20,  0,  0,  0],
        [5, -5,-10,  0,  0,-10, -5,  5],
        [5, 10, 10,-20,-20, 10, 10,  5],
        [0,  0,  0,  0,  0,  0,  0,  0]
    ]

    def evaluate_position(self, game_state):
        """
        Evaluates the current position in centipawns.
        Positive values favor white, negative values favor black.
        """
        if game_state is None:
            return 0
        
        score = 0
        
        # Material count
        score += self._evaluate_material(game_state.board)
        
        # Position evaluation
        score += self._evaluate_piece_positions(game_state.board)
        
        # Mobility (number of legal moves)
        mobility_score = self._evaluate_mobility(game_state)
        score += mobility_score
        
        # Pawn structure
        score += self._evaluate_pawn_structure(game_state.board)
        
        # If it's black's turn, negate the score
        if not game_state.whiteToMove:
            score = -score
            
        return score

    def _evaluate_material(self, board):
        """
        Calculates the material balance of the position.
        """
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != "--":
                    value = self.PIECE_VALUES[piece[1]]
                    if piece[0] == 'w':
                        score += value
                    else:
                        score -= value
        return score

    def _evaluate_piece_positions(self, board):
        """
        Evaluates piece positioning using piece-square tables.
        """
        score = 0
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != "--":
                    if piece[1] == 'p':
                        # Pawns
                        if piece[0] == 'w':
                            score += self.PAWN_TABLE[row][col]
                        else:
                            score -= self.PAWN_TABLE[7-row][col]
        return score

    def _evaluate_mobility(self, game_state):
        """
        Evaluates piece mobility (number of legal moves).
        """
        original_turn = game_state.whiteToMove
        
        # Get white mobility
        game_state.whiteToMove = True
        white_moves = len(game_state.getValidMoves())
        
        # Get black mobility
        game_state.whiteToMove = False
        black_moves = len(game_state.getValidMoves())
        
        # Restore original turn
        game_state.whiteToMove = original_turn
        
        return (white_moves - black_moves) * 10

    def _evaluate_pawn_structure(self, board):
        """
        Evaluates pawn structure (doubled, isolated, and passed pawns).
        """
        score = 0
        
        # Count pawns in each file
        white_pawn_files = [0] * 8
        black_pawn_files = [0] * 8
        
        for col in range(8):
            for row in range(8):
                piece = board[row][col]
                if piece == "wp":
                    white_pawn_files[col] += 1
                elif piece == "bp":
                    black_pawn_files[col] += 1
        
        # Penalize doubled pawns and reward passed pawns
        for col in range(8):
            # Doubled pawns penalty
            if white_pawn_files[col] > 1:
                score -= 20 * (white_pawn_files[col] - 1)
            if black_pawn_files[col] > 1:
                score += 20 * (black_pawn_files[col] - 1)
            
            # Passed pawns bonus
            if white_pawn_files[col] > 0 and col > 0 and col < 7:
                if black_pawn_files[col-1] == 0 and black_pawn_files[col] == 0 and black_pawn_files[col+1] == 0:
                    score += 50
            if black_pawn_files[col] > 0 and col > 0 and col < 7:
                if white_pawn_files[col-1] == 0 and white_pawn_files[col] == 0 and white_pawn_files[col+1] == 0:
                    score -= 50
                    
        return score

    def _evaluate_mating_potential(self, game_state):
        """
        Evaluate likelihood of checkmate based on piece positions
        and material advantage
        """

    def _evaluate_rook_position(self, board):
        """
        Evaluate rooks on open files and 7th/8th ranks
        """

    def _evaluate_bishop_pair(self, board):
        """
        Add bonus for having both bishops
        """

    def _evaluate_king_safety(self, board):
        """
        Evaluate king safety based on pawn shield and attacking pieces
        """

    def _get_game_phase(self, board):
        """
        Returns a value between 0 (opening) and 1 (endgame)
        based on remaining material
        """
