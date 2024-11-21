

class GameState:
    """
    Represents the current state of a chess game, including valid moves and the move log.
    """

    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"p": self.getPawnMoves,
                              "R": self.getRookMoves,
                              "N": self.getKnightMoves,
                              "B": self.getBishopMoves,
                              "Q": self.getQueenMoves,
                              "K": self.getKingMoves,}

        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        # Add new fields for special moves
        self.enpassantPossible = ()  # Coordinates for the square where en passant capture is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(True, True, True, True)]

    def makeMove(self, move, promotionChoice='R'):
        """
        Make the move on the board and handle special cases
        promotionChoice should be 'Q', 'R', 'B', or 'N'
        """
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)

        # Handle pawn promotion
        if move.isPawnPromotion:
            # Default to queen if no choice specified
            promotionPiece = promotionChoice if promotionChoice in ['Q', 'R', 'B', 'N'] else 'Q'
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotionPiece

        # Handle en passant capture
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"  # Capturing the pawn

        # Update enpassantPossible
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:  # 2 square pawn advance
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # Handle castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # Kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:  # Queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        # Update castling rights
        self.updateCastlingRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                                 self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

        self.whiteToMove = not self.whiteToMove  # Swap players

        # Update king's position if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            # Update king position if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            # Undo en passant capture
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"  # Remove the pawn that did en passant
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # Puts the captured pawn back
                self.enpassantPossible = (move.endRow, move.endCol)

            # Undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # Undo castling rights
            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1]

            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # Kingside
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # Queenside
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

    def updateCastlingRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # Left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7:  # Right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # Left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7:  # Right rook
                    self.currentCastlingRights.bks = False

    def squareUnderAttack(self, r, c):
        """
        Determine if enemy can attack square r, c
        """
        self.whiteToMove = not self.whiteToMove  # Switch to opponent's turn

        # Get all opponent's moves without checking castling (to prevent recursion)
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[r])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[row][col][1]
                    if piece == 'p':
                        self.getPawnMoves(row, col, moves)
                    elif piece == 'R':
                        self.getRookMoves(row, col, moves)
                    elif piece == 'N':
                        self.getKnightMoves(row, col, moves)
                    elif piece == 'B':
                        self.getBishopMoves(row, col, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(row, col, moves)
                    elif piece == 'K':
                        # For king moves, don't check castling to prevent recursion
                        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
                        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
                        ally_color = "w" if self.whiteToMove else "b"
                        for i in range(8):
                            end_row = row + row_moves[i]
                            end_col = col + col_moves[i]
                            if 0 <= end_row < 8 and 0 <= end_col < 8:
                                end_piece = self.board[end_row][end_col]
                                if end_piece[0] != ally_color:
                                    moves.append(Move((row, col), (end_row, end_col), self.board))

        self.whiteToMove = not self.whiteToMove  # Switch turns back

        # Check if target square is under attack
        for move in moves:
            if move.endRow == r and move.endCol == c:  # Square is under attack
                return True
        return False

    def getValidMoves(self):
        """
        Get all valid moves, considering checks.
        """
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1: #only 1 check, can block or move king
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) #check[2&3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves)-1,-1,-1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()

        return moves

    def getAllPossibleMoves(self):
        """
        Get all possible moves without considering checks.
        """
        moves = []
        for r in range(len(self.board)):  # 8
            for c in range(len(self.board[r])):  # 8
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) #switch statement via dictionary
        return moves

    def getRookMoves(self, r, c, moves):
        """
        Get all valid Rook moves for the Rook located at row, col, and add these moves to the list.
        """
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # Don't remove pin if piece is a queen
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getBishopMoves(self, r, c, moves):
        """
        Get all valid Bishop moves for the bishop located at row, col, and add these moves to the list.
        """
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # Don't remove pin if piece is a queen
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getPawnMoves(self, r, c, moves):
        """
        Get all valid pawn moves for the pawn located at row, col, and add these moves to the list.
        """
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        # Regular pawn moves
        if self.board[r + moveAmount][c] == "--":
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((r, c), (r + moveAmount, c), self.board))
                if r == startRow and self.board[r + 2 * moveAmount][c] == "--":
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))

        # Captures and en passant
        for colOffset in [-1, 1]:
            if 0 <= c + colOffset <= 7:  # Check column bounds
                if not piecePinned or pinDirection == (moveAmount, colOffset):
                    # Regular capture
                    if self.board[r + moveAmount][c + colOffset][0] == enemyColor:
                        moves.append(Move((r, c), (r + moveAmount, c + colOffset), self.board))

                    # En passant
                    if (r + moveAmount, c + colOffset) == self.enpassantPossible:
                        capturingPiece = blockingPiece = False
                        if kingRow == r:
                            if kingCol < c:  # King is left of the pawn
                                insideRange = range(kingCol + 1, c)
                                outsideRange = range(c + 1, 8)
                            else:  # King is right of the pawn
                                insideRange = range(kingCol - 1, c, -1)
                                outsideRange = range(c - 1, -1, -1)

                            for i in insideRange:
                                if self.board[r][i] != "--":
                                    blockingPiece = True
                                    break

                            for i in outsideRange:
                                square = self.board[r][i]
                                if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                    capturingPiece = True
                                    break
                                elif square != "--":
                                    blockingPiece = True
                                    break

                        if not capturingPiece or blockingPiece:
                            moves.append(
                                Move((r, c), (r + moveAmount, c + colOffset), self.board, isEnpassantMove=True))

    def isCheckmate(self):
        """
        Verify if the current position is checkmate.
        """
        if not self.inCheck:
            return False
        return len(self.getValidMoves()) == 0

    def isStalemate(self):
        """
        Verify if the current position is stalemate.
        """
        if self.inCheck:
            return False
        return len(self.getValidMoves()) == 0

    def isDraw(self):
        """
        Check for draw conditions including stalemate and insufficient material.
        """
        if self.isStalemate():
            return True
        if self.hasInsufficientMaterial():
            return True
        return False

    def hasInsufficientMaterial(self):
        """
        Check if there is insufficient material for checkmate.
        """
        pieces = {'w': {'count': 0, 'B': 0, 'N': 0},
                  'b': {'count': 0, 'B': 0, 'N': 0}}
        bishops_white_square = {'w': False, 'b': False}
        bishops_black_square = {'w': False, 'b': False}

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != "--":
                    color = piece[0]
                    piece_type = piece[1]

                    if piece_type not in ('K', 'B', 'N'):
                        return False

                    pieces[color]['count'] += 1
                    if piece_type in ('B', 'N'):
                        pieces[color][piece_type] += 1

                        # Track bishop square colors
                        if piece_type == 'B':
                            square_color = (row + col) % 2
                            if square_color == 0:
                                bishops_white_square[color] = True
                            else:
                                bishops_black_square[color] = True

        # King vs King
        if pieces['w']['count'] == 1 and pieces['b']['count'] == 1:
            return True

        # King and Bishop vs King
        if (pieces['w']['count'] == 2 and pieces['w']['B'] == 1 and pieces['b']['count'] == 1) or \
                (pieces['b']['count'] == 2 and pieces['b']['B'] == 1 and pieces['w']['count'] == 1):
            return True

        # King and Knight vs King
        if (pieces['w']['count'] == 2 and pieces['w']['N'] == 1 and pieces['b']['count'] == 1) or \
                (pieces['b']['count'] == 2 and pieces['b']['N'] == 1 and pieces['w']['count'] == 1):
            return True

        # King and Bishop vs King and Bishop (same color squares)
        if pieces['w']['count'] == 2 and pieces['b']['count'] == 2 and \
                pieces['w']['B'] == 1 and pieces['b']['B'] == 1:
            white_bishop_square = bishops_white_square['w'] or bishops_black_square['w']
            black_bishop_square = bishops_white_square['b'] or bishops_black_square['b']
            if white_bishop_square == black_bishop_square:
                return True

        return False

    def getKnightMoves(self, r, c, moves):
        """
        Get all valid Rook moves for the Knight located at row, col, and add these moves to the list.
        """
        piecePinned = False
        for i in range(len(self.pins)-1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        knightMoves = ((-2,1), (-2,-1), (-1,2), (-1,-2), (1,2), (1,-2), (2,1), (2,-1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #empty or enemy
                        moves.append(Move((r, c), (endRow, endCol), self.board))


    def getQueenMoves(self, r, c, moves):
        """
        Get all valid Rook moves for the Queen located at row, col, and add these moves to the list.
        """
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        """
        Get all the king moves for the king located at row, col and add these moves to the list
        """
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # Check if end square is on board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:  # Not an ally piece - empty or enemy
                    # Place king on end square and check for checks
                    if ally_color == 'w':
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndChecks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # Move king back
                    if ally_color == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

        # Generate castling moves
        self.getCastleMoves(r, c, moves)

    def getCastleMoves(self, r, c, moves):
        """
        Generate all valid castle moves for the king at (r, c) and add them to the list of moves
        """
        if self.inCheck:
            return  # Can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (
                not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (
                not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        # Check if squares between king and rook are empty
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            # Check if squares king moves through are not under attack
            if not self.squareUnderAttack(r, c) and \
                    not self.squareUnderAttack(r, c + 1) and \
                    not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        # Check if squares between king and rook are empty
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            # Check if squares king moves through are not under attack
            if not self.squareUnderAttack(r, c) and \
                    not self.squareUnderAttack(r, c - 1) and \
                    not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


    def checkForPinsAndChecks(self):
        pins = []   #squares where the allied pinned piece is and direction pinned from
        checks = [] #squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        #check outward from king for pins and checks, keep track of pins
        directions = ((-1,0), (0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0<= j <=3 and type == 'R') or \
                                (4<= j <=7 and type == 'B') or \
                                (i==1 and type == 'p' and ((enemyColor == 'w' and 6<= j <=7) or (enemyColor == 'b' and 4<= j <=5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == (): #no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pins.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break

        knightMoves = ((-2,1), (-2,-1), (-1,2), (-1,-2), (1,2), (1,-2), (2,1), (2,-1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn promotion check - modified to be more explicit
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True

        # En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        # Castle move
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):  # overriding the equals method
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self, notation_type="standard"):
        """
        Get move in the specified chess notation format.

        notation_type options:
        - "standard": Standard Algebraic Notation (e.g., e4, Nf3, O-O)
        - "long": Long Algebraic Notation (e.g., e2-e4, Ng1-f3)
        - "coordinate": Coordinate Notation (e.g., e2e4, g1f3)
        - "uci": UCI Notation (e.g., e2e4, g1f3) - same as coordinate
        - "descriptive": Traditional Descriptive Notation (e.g., P-K4, N-KB3)
        """
        if notation_type == "standard":
            return self.getStandardAlgebraicNotation()

    def getStandardAlgebraicNotation(self):
        """
        Get move in standard algebraic notation (e.g., e4, Nf3, Bxe5).
        Most common notation used in chess literature.
        """
        if self.isCastleMove:
            if self.endCol - self.startCol == 2:  # Kingside castle
                return "O-O"
            else:  # Queenside castle
                return "O-O-O"

        # Get piece letter (empty for pawns)
        piece = self.pieceMoved[1].upper() if self.pieceMoved[1] != 'p' else ''

        # Add capture symbol if applicable
        capture = 'x' if self.pieceCaptured != '--' else ''

        # Get destination square
        destination = self.getRankFile(self.endRow, self.endCol)

        # For pawns, show file when capturing
        if not piece and capture:
            piece = self.colsToFiles[self.startCol]

        # Add promotion if applicable
        promotion = '=' + self.pieceMoved[1].upper() if self.isPawnPromotion else ''

        return f"{piece}{capture}{destination}{promotion}"

    def getRankFile(self, r, c):
        """
        Convert row, col to chess notation (e.g., 6, 4 -> e2).
        """
        return self.colsToFiles[c] + self.rowsToRanks[r]

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks  # white king side
        self.bks = bks  # black king side
        self.wqs = wqs  # white queen side
        self.bqs = bqs  # black queen side