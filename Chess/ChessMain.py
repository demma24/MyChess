import pygame as p
from Chess import ChessEngine
from Chess.StockfishInterface import StockfishInterface
from Chess.MoveHistory import MoveHistory, drawMoveHistory


# Board dimensions
DIMENSION = 8
LABEL_SIZE = 20  # Size for the labels area
BASE_BOARD_SIZE = 512
HEIGHT = BASE_BOARD_SIZE + LABEL_SIZE
SQ_SIZE = (HEIGHT - LABEL_SIZE) // DIMENSION

# Evaluation bar constants
EVAL_BAR_WIDTH = 20
EVAL_BAR_HEIGHT = HEIGHT
EVAL_BAR_X = 0
EVAL_BAR_Y = 0
MAX_EVAL = 10.0  # Maximum evaluation value to show (clip values beyond this)

# Move history panel constants
HISTORY_WIDTH = 200
HISTORY_Y = 0
HISTORY_HEIGHT = HEIGHT  # Same height as board
HISTORY_MOVE_HEIGHT = 30  # Height for each move row
HISTORY_FONT_SIZE = 16
MOVE_LIST_OFFSET = 10  # Padding inside history panel

# Calculate total board width and position
BOARD_WIDTH = BASE_BOARD_SIZE + LABEL_SIZE + EVAL_BAR_WIDTH
WIDTH = BOARD_WIDTH + HISTORY_WIDTH
HISTORY_X = BOARD_WIDTH  # Position history panel right of the board
BOARD_OFFSET = LABEL_SIZE + EVAL_BAR_WIDTH  # Offset the board by label size + eval bar
BOARD_OFFSET_Y = 0

# Button layout constants
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 120
EVAL_BUTTON_WIDTH = 120
ENGINE_BUTTON_WIDTH = 120
BUTTON_SPACING = 20
TOTAL_BUTTONS_WIDTH = EVAL_BUTTON_WIDTH + ENGINE_BUTTON_WIDTH + BUTTON_SPACING
EVAL_BUTTON_X = BOARD_WIDTH // 2 - TOTAL_BUTTONS_WIDTH // 2  # Center buttons under board
ENGINE_BUTTON_X = EVAL_BUTTON_X + EVAL_BUTTON_WIDTH + BUTTON_SPACING
BUTTON_Y = HEIGHT + 10

# Move display area
MOVE_DISPLAY_HEIGHT = 80
WINDOW_HEIGHT = max(HEIGHT + BUTTON_HEIGHT + MOVE_DISPLAY_HEIGHT + 30, HISTORY_HEIGHT)

# Animation constants
ANIMATE_SPEED = 2
MAX_FPS = 15

# Dictionary to store piece images
IMAGES = {}

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, WINDOW_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    engine_interface = StockfishInterface()
    position_eval = None
    best_moves_info = None  # Will store multiple moves
    move_history = MoveHistory(HISTORY_HEIGHT)

    move_history = MoveHistory(HISTORY_HEIGHT)
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False
    lastPosition = None  # For caching valid moves

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    highlightSquares = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                engine_interface.close()

            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()

                if HISTORY_X <= location[0] <= HISTORY_X + HISTORY_WIDTH:
                    if e.button == 4:  # Mouse wheel up
                        move_history.scroll(-move_history.MOVE_HEIGHT)
                    elif e.button == 5:  # Mouse wheel down
                        move_history.scroll(move_history.MOVE_HEIGHT)
                    else:  # Move selection
                        click_y = location[1] - HISTORY_Y - 30 + move_history.scroll_y
                        clicked_index = click_y // move_history.MOVE_HEIGHT
                        if 0 <= clicked_index < len(move_history.moves):
                            move_history.selected_index = clicked_index
                            # TODO: Implement position replay
                    continue  # Skip rest of click handling if clicking on history

                if gameOver:
                    # Check for "Play Again" button click
                    play_again_rect = p.Rect(WIDTH // 4, HEIGHT // 2 + 30, WIDTH // 2, 50)
                    if play_again_rect.collidepoint(location):
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False
                        gameOver = False
                        position_eval = None
                        best_moves_info = None
                        clear_move_display_area(screen)
                        continue

                if not gameOver:
                    location = p.mouse.get_pos()

                    # Check evaluation button click
                    eval_button_rect = p.Rect(EVAL_BUTTON_X, BUTTON_Y, EVAL_BUTTON_WIDTH, BUTTON_HEIGHT)
                    if eval_button_rect.collidepoint(location):
                        result = engine_interface.get_best_moves(gs, num_moves=1)
                        if result and result[0]:
                            _, eval_score, _ = result[0]
                            position_eval = eval_score
                        continue

                    # Check engine button click
                    engine_button_rect = p.Rect(ENGINE_BUTTON_X, BUTTON_Y, ENGINE_BUTTON_WIDTH, BUTTON_HEIGHT)
                    if engine_button_rect.collidepoint(location):
                        best_moves_info = engine_interface.get_best_moves(gs, num_moves=2)
                        # Clear the area below buttons before drawing new moves
                        clear_move_display_area(screen)
                        continue

                    # Handle board clicks
                    if location[1] < HEIGHT:
                        col = (location[0] - BOARD_OFFSET) // SQ_SIZE
                        row = (location[1] - BOARD_OFFSET_Y) // SQ_SIZE
                        if 0 <= row < 8 and 0 <= col < 8:
                            if sqSelected == (row, col):
                                sqSelected = ()
                                playerClicks = []
                                highlightSquares = []
                            else:
                                sqSelected = (row, col)
                                playerClicks.append(sqSelected)

                                if len(playerClicks) == 1:
                                    highlightSquares = []
                                    for move in validMoves:
                                        if move.startRow == row and move.startCol == col:
                                            highlightSquares.append((move.endRow, move.endCol))

                                if len(playerClicks) == 2:
                                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                                    for validMove in validMoves:
                                        if move == validMove:
                                            if validMove.isPawnPromotion:
                                                promotedPiece = getPromotionChoice(screen)
                                                if promotedPiece:
                                                    gs.makeMove(validMove, promotedPiece)
                                                else:
                                                    # If no choice made (e.g., user cancelled), default to Queen
                                                    gs.makeMove(validMove, 'Q')
                                            else:
                                                gs.makeMove(validMove)  # Regular move without promotion
                                            moveMade = True
                                            animate = True
                                            sqSelected = ()
                                            playerClicks = []
                                            highlightSquares = []
                                            position_eval = None
                                            best_moves_info = None  # Clear best moves when a move is made
                                            # Clear the move display area
                                            clear_move_display_area(screen)

                                    if not moveMade:
                                        playerClicks = [sqSelected]
                                        highlightSquares = []
                                        for move in validMoves:
                                            if move.startRow == row and move.startCol == col:
                                                highlightSquares.append((move.endRow, move.endCol))

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if len(gs.moveLog) > 0:
                        move_history.moves.pop()
                        if len(gs.moveLog) % 2 == 0:
                            move_history.moves[-1]['black'] = ''
                    position_eval = None
                    best_moves_info = None
                    clear_move_display_area(screen)  # Clear move display on undo
                if e.key == p.K_r:  # Reset when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    move_history.clear()
                    position_eval = None
                    best_moves_info = None
                    clear_move_display_area(screen)  # Clear move display on reset

        if moveMade:
            if len(gs.moveLog) > 0:  # Only add move if there is one
                move_history.add_move(gs.moveLog[-1], len(gs.moveLog))
            position_eval = None  # Clear evaluation when a move is made
            if animate:
                animateMove(screen, gs.moveLog[-1], gs.board, clock)
                animate = False

            # Only recompute valid moves if position changed
            currentPosition = str(gs.board)
            if currentPosition != lastPosition:
                validMoves = gs.getValidMoves()
                lastPosition = currentPosition
            moveMade = False

            # Check for game end conditions
            if len(validMoves) == 0:
                if gs.inCheck:
                    gameOver = True
                    position_eval = None
                    best_moves_info = None
                elif gs.isStalemate():
                    gameOver = True
                    position_eval = None
                    best_moves_info = None
            elif gs.isDraw():
                gameOver = True
                position_eval = None
                best_moves_info = None

        drawGameState(screen, gs, validMoves, sqSelected, highlightSquares, position_eval)
        drawMoveHistory(screen, move_history, HISTORY_X, HISTORY_Y, HISTORY_WIDTH, HISTORY_HEIGHT)
        drawButtons(screen, position_eval, best_moves_info, gs)

        if gameOver:
            drawEndGameText(screen, gs)

        clock.tick(MAX_FPS)
        p.display.flip()


def loadImages():
    """
    Load images for chess pieces.
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def clear_move_display_area(screen):
    """Clear the area where best moves are displayed"""
    move_display_rect = p.Rect(0, BUTTON_Y + BUTTON_HEIGHT, WIDTH, MOVE_DISPLAY_HEIGHT)
    screen.fill(p.Color("white"), move_display_rect)

def drawButton(screen, text, x, y, width, height, bg_color=p.Color('lightgray'), text_color=p.Color('black')):
    """Draw a button with optional custom colors"""
    button = p.Rect(x, y, width, height)
    p.draw.rect(screen, bg_color, button)
    p.draw.rect(screen, p.Color('darkgray'), button, 2)

    font = p.font.Font(None, 24)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=button.center)
    screen.blit(text_surface, text_rect)

    return button

def drawButtons(screen, position_eval, best_moves_info, gs):
    """Draw evaluation and engine buttons with their results"""
    # Draw evaluation button/result
    if position_eval is not None:
        if position_eval > 0:
            bg_color = p.Color('white')
            text_color = p.Color('black')
        else:
            bg_color = p.Color('black')
            text_color = p.Color('white')
        eval_text = f"Eval: {position_eval:+.1f}"
    else:
        bg_color = p.Color('lightgray')
        text_color = p.Color('black')
        eval_text = "Get Eval"

    drawButton(screen, eval_text, EVAL_BUTTON_X, BUTTON_Y, EVAL_BUTTON_WIDTH, BUTTON_HEIGHT,
               bg_color=bg_color, text_color=text_color)

    # Draw engine button
    engine_text = "Get Moves"
    drawButton(screen, engine_text, ENGINE_BUTTON_X, BUTTON_Y, ENGINE_BUTTON_WIDTH, BUTTON_HEIGHT)

    # Draw best moves information if available
    if best_moves_info:
        font = p.font.Font(None, 24)
        move_display_y = BUTTON_Y + BUTTON_HEIGHT + 10

        for i, (move, eval_score, _) in enumerate(best_moves_info):
            if move:
                # Convert UCI move to standard notation
                start_square = move[:2]
                end_square = move[2:]
                move_obj = ChessEngine.Move(
                    (8 - int(start_square[1]), ord(start_square[0]) - ord('a')),
                    (8 - int(end_square[1]), ord(end_square[0]) - ord('a')),
                    gs.board
                )
                notation = move_obj.getChessNotation()

                # Determine text color based on evaluation
                if eval_score > 0:
                    text_color = p.Color('black')
                else:
                    text_color = p.Color('darkgray')

                # Create move text with rank and evaluation
                rank_text = "Best move:" if i == 0 else "Second best:"
                move_text = f"{rank_text} {notation} ({eval_score:+.1f})"

                # Render text
                text_surface = font.render(move_text, True, text_color)
                screen.blit(text_surface, (EVAL_BUTTON_X, move_display_y + i * 25))


def drawEndGameText(screen, gs):
    """Draw end game text and Play Again button"""
    # Create semi-transparent overlay
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.fill(p.Color('black'))
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    font = p.font.Font(None, 64)

    # Determine game end condition and text
    if len(gs.getValidMoves()) == 0:
        if gs.inCheck:
            text = "Black Wins!" if gs.whiteToMove else "White Wins!"
        else:
            text = "Stalemate!"
    else:
        return  # If game isn't over, don't draw anything

    # Draw game over text
    text_surface = font.render(text, True, p.Color('white'))
    text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(text_surface, text_rect)

    # Draw Play Again button
    play_again_font = p.font.Font(None, 36)
    play_again_text = play_again_font.render("Play Again", True, p.Color('white'))
    play_again_rect = play_again_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))

    # Draw button background
    button_rect = p.Rect(WIDTH // 4, HEIGHT // 2 + 30, WIDTH // 2, 50)
    p.draw.rect(screen, p.Color('darkgray'), button_rect)
    p.draw.rect(screen, p.Color('white'), button_rect, 2)  # Button border

    # Draw button text
    screen.blit(play_again_text, play_again_rect)

def drawGameState(screen, gs, validMoves, sqSelected, highlightSquares, position_eval):
    drawBoard(screen)  # Draw squares on the board
    highlightSquares = highlightSquare(screen, gs, validMoves, sqSelected, highlightSquares)
    drawPieces(screen, gs.board)  # Draw pieces on top of squares
    drawEvalBar(screen, position_eval)  # Draw evaluation bar


def drawBoard(screen):
    """
    Draw the squares on the board and add labels.
    """
    colors = [p.Color("white"), p.Color("gray")]
    font = p.font.Font(None, 24)

    # Draw squares
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(
                c * SQ_SIZE + BOARD_OFFSET,
                r * SQ_SIZE + BOARD_OFFSET_Y,
                SQ_SIZE,
                SQ_SIZE))

    # Draw row labels (1-8)
    for r in range(DIMENSION):
        text = font.render(str(8 - r), True, p.Color("black"))
        text_rect = text.get_rect(
            center=(LABEL_SIZE // 2 + EVAL_BAR_WIDTH,
                    r * SQ_SIZE + SQ_SIZE // 2 + BOARD_OFFSET_Y))
        screen.blit(text, text_rect)

    # Draw column labels (a-h)
    for c in range(DIMENSION):
        text = font.render(chr(ord('a') + c), True, p.Color("black"))
        text_rect = text.get_rect(
            center=(c * SQ_SIZE + SQ_SIZE // 2 + BOARD_OFFSET,
                    HEIGHT - LABEL_SIZE // 2))
        screen.blit(text, text_rect)


def drawEvalBar(screen, evaluation):
    """
    Draw a vertical evaluation bar showing the current position evaluation.
    Positive values indicate white advantage, negative values indicate black advantage.
    """
    # Draw background
    bar_bg = p.Rect(EVAL_BAR_X, EVAL_BAR_Y, EVAL_BAR_WIDTH, EVAL_BAR_HEIGHT)
    p.draw.rect(screen, p.Color('gray20'), bar_bg)

    if evaluation is not None:
        # Clip evaluation to max value
        clipped_eval = min(max(evaluation, -MAX_EVAL), MAX_EVAL)

        # Convert evaluation to height percentage (0.0 to 1.0)
        # Center point (eval = 0.0) should be at middle of bar
        eval_percent = 0.5 - (clipped_eval / (2 * MAX_EVAL))
        bar_height = int(EVAL_BAR_HEIGHT * eval_percent)

        # Draw white's portion (bottom half)
        white_rect = p.Rect(EVAL_BAR_X, bar_height,
                            EVAL_BAR_WIDTH, EVAL_BAR_HEIGHT - bar_height)
        p.draw.rect(screen, p.Color('white'), white_rect)

        # Draw evaluation text
        font = p.font.Font(None, 16)
        eval_text = f"{abs(evaluation):+.1f}"
        text_color = p.Color('black') if evaluation >= 0 else p.Color('white')
        text_surface = font.render(eval_text, True, text_color)
        text_rect = text_surface.get_rect(center=(EVAL_BAR_X + EVAL_BAR_WIDTH // 2,
                                                  EVAL_BAR_HEIGHT // 2))
        screen.blit(text_surface, text_rect)

    # Draw center line
    center_y = EVAL_BAR_HEIGHT // 2
    p.draw.line(screen, p.Color('gray60'),
                (EVAL_BAR_X, center_y),
                (EVAL_BAR_X + EVAL_BAR_WIDTH, center_y), 1)


def highlightSquare(screen, gs, validMoves, sqSelected, highlightSquares):
    """
    Highlight square selected and valid moves for piece selected.
    """
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('mediumaquamarine'))
            screen.blit(s, (c * SQ_SIZE + BOARD_OFFSET, r * SQ_SIZE + BOARD_OFFSET_Y))

    # Highlight previous move
    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('bisque'))
        screen.blit(s, (
            lastMove.endCol * SQ_SIZE + BOARD_OFFSET,
            lastMove.endRow * SQ_SIZE + BOARD_OFFSET_Y))
        screen.blit(s, (
            lastMove.startCol * SQ_SIZE + BOARD_OFFSET,
            lastMove.startRow * SQ_SIZE + BOARD_OFFSET_Y))

    return highlightSquares

def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game state.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Not empty square
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE + BOARD_OFFSET,
                    r*SQ_SIZE + BOARD_OFFSET_Y,
                    SQ_SIZE,
                    SQ_SIZE))


def animateMove(screen, move, board, clock):
    """
    Animate the movement of pieces.
    """
    colors = [p.Color("white"), p.Color("gray")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = ANIMATE_SPEED
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount,
                move.startCol + dC * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)

        # Erase piece from ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(
            move.endCol * SQ_SIZE + BOARD_OFFSET,
            move.endRow * SQ_SIZE + BOARD_OFFSET_Y,
            SQ_SIZE,
            SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        # Draw moving piece
        if move.pieceCaptured != '--':
            if not move.isEnpassantMove:
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(
            c * SQ_SIZE + BOARD_OFFSET,
            r * SQ_SIZE + BOARD_OFFSET_Y,
            SQ_SIZE,
            SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def getPromotionChoice(screen):
    """
    Let player choose promotion piece.
    """
    # Create a small menu for promotion choices
    choices = ['Q', 'R', 'B', 'N']
    menu_height = 200
    menu_width = 100
    menu = p.Surface((menu_width, menu_height))
    menu.fill(p.Color('white'))

    # Draw choices
    for i, piece in enumerate(choices):
        text = p.font.Font(None, 36).render(piece, True, p.Color('black'))
        rect = text.get_rect(center=(menu_width/2, (i+0.5)*menu_height/len(choices)))
        menu.blit(text, rect)

    # Position menu in center of screen
    menu_x = (WIDTH - menu_width) // 2
    menu_y = (HEIGHT - menu_height) // 2
    screen.blit(menu, (menu_x, menu_y))
    p.display.flip()

    # Wait for user choice
    while True:
        e = p.event.wait()
        if e.type == p.MOUSEBUTTONDOWN:
            mouse_pos = p.mouse.get_pos()
            if menu_x <= mouse_pos[0] <= menu_x + menu_width:
                relative_y = mouse_pos[1] - menu_y
                if 0 <= relative_y <= menu_height:
                    choice = choices[int(relative_y // (menu_height/len(choices)))]
                    return choice
        elif e.type == p.QUIT:
            return None
        elif e.type == p.KEYDOWN and e.key == p.K_ESCAPE:
            return None

if __name__ == "__main__":
    main()