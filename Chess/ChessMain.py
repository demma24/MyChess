import pygame as p
from Chess import ChessEngine
from Chess.StockfishInterface import StockfishInterface

ANIMATE_SPEED = 2
LABEL_SIZE = 20  # Size for the labels area
BOARD_OFFSET = LABEL_SIZE  # Offset the board by label size
BOARD_OFFSET_Y = 0
WIDTH = 512 + LABEL_SIZE
HEIGHT = 512 + LABEL_SIZE
DIMENSION = 8
SQ_SIZE = (HEIGHT - LABEL_SIZE) // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Button dimensions
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 120
EVAL_BUTTON_WIDTH = 120
ENGINE_BUTTON_WIDTH = 120
BUTTON_SPACING = 20
TOTAL_BUTTONS_WIDTH = EVAL_BUTTON_WIDTH + ENGINE_BUTTON_WIDTH + BUTTON_SPACING
EVAL_BUTTON_X = WIDTH // 2 - TOTAL_BUTTONS_WIDTH // 2
ENGINE_BUTTON_X = EVAL_BUTTON_X + EVAL_BUTTON_WIDTH + BUTTON_SPACING
BUTTON_Y = HEIGHT + 10

WINDOW_HEIGHT = HEIGHT + BUTTON_HEIGHT + 20


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, WINDOW_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    engine_interface = StockfishInterface()
    position_eval = None
    best_move_info = None

    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False
    gameOver = False

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
                if not gameOver:
                    location = p.mouse.get_pos()

                    # Check evaluation button click
                    eval_button_rect = p.Rect(EVAL_BUTTON_X, BUTTON_Y, EVAL_BUTTON_WIDTH, BUTTON_HEIGHT)
                    if eval_button_rect.collidepoint(location):
                        result = engine_interface.get_best_move(gs)
                        if result:
                            _, eval_score, _ = result
                            position_eval = eval_score
                        continue

                    # Check engine button click
                    engine_button_rect = p.Rect(ENGINE_BUTTON_X, BUTTON_Y, ENGINE_BUTTON_WIDTH, BUTTON_HEIGHT)
                    if engine_button_rect.collidepoint(location):
                        result = engine_interface.get_best_move(gs)
                        if result:
                            best_move_info = result
                        continue

                    # Handle board clicks
                    if location[1] < HEIGHT:  # Only process clicks on the board
                        col = (location[0] - BOARD_OFFSET) // SQ_SIZE
                        row = (location[1] - BOARD_OFFSET_Y) // SQ_SIZE
                        # Make sure the click is within the board
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
                                                    gs.board[validMove.endRow][validMove.endCol] = validMove.pieceMoved[
                                                                                                       0] + promotedPiece
                                            gs.makeMove(validMove)
                                            moveMade = True
                                            animate = True
                                            sqSelected = ()
                                            playerClicks = []
                                            highlightSquares = []
                                            position_eval = None
                                            best_move_info = None

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
                    position_eval = None
                    best_move_info = None
                if e.key == p.K_r:  # Reset when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    position_eval = None
                    best_move_info = None

        if moveMade:
            if animate:
                animateMove(screen, gs.moveLog[-1], gs.board, clock)
                animate = False
            validMoves = gs.getValidMoves()
            moveMade = False

            # Check for checkmate or stalemate
            if len(validMoves) == 0:
                gameOver = True
                if gs.inCheck:
                    drawEndGameText(screen, True, gs)
                else:
                    drawEndGameText(screen, False, gs)

        drawGameState(screen, gs, validMoves, sqSelected, highlightSquares)
        drawButtons(screen, position_eval, best_move_info, gs)

        if gameOver:
            drawEndGameText(screen, gs.inCheck, gs)

        clock.tick(MAX_FPS)
        p.display.flip()


def loadImages():
    """
    Load images for chess pieces.
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


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


def drawButtons(screen, position_eval, best_move_info, gs):
    """Draw evaluation and engine buttons with their results"""
    # Draw evaluation button/result
    if position_eval is not None:
        # Determine colors based on evaluation
        if position_eval > 0:  # Better for white
            bg_color = p.Color('white')
            text_color = p.Color('black')
        else:  # Better for black
            bg_color = p.Color('black')
            text_color = p.Color('white')
        eval_text = f"Eval: {position_eval:+.1f}"
    else:
        bg_color = p.Color('lightgray')
        text_color = p.Color('black')
        eval_text = "Get Eval"

    drawButton(screen, eval_text, EVAL_BUTTON_X, BUTTON_Y, EVAL_BUTTON_WIDTH, BUTTON_HEIGHT,
               bg_color=bg_color, text_color=text_color)

    # Draw engine button/result (using default colors)
    if best_move_info:
        move, eval_score, _ = best_move_info
        if move:
            # Convert UCI move to preferred notation
            start_square = move[:2]
            end_square = move[2:]
            move_obj = ChessEngine.Move(
                (8 - int(start_square[1]), ord(start_square[0]) - ord('a')),
                (8 - int(end_square[1]), ord(end_square[0]) - ord('a')),
                gs.board
            )
            notation = move_obj.getChessNotation(notation_type = "standard")
            engine_text = f"Best: {notation}"
        else:
            engine_text = "Get Move"
    else:
        engine_text = "Get Move"
    drawButton(screen, engine_text, ENGINE_BUTTON_X, BUTTON_Y, ENGINE_BUTTON_WIDTH, BUTTON_HEIGHT)


def drawEndGameText(screen, inCheck, gs):
    """Draw end game text"""
    font = p.font.Font(None, 36)
    if inCheck:
        text = "Black Wins!" if gs.whiteToMove else "White Wins!"
    else:
        text = "Stalemate"

    # Create semi-transparent overlay
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.fill(p.Color('black'))
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))

    # Draw text
    text_surface = font.render(text, True, p.Color('white'))
    text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    screen.blit(text_surface, text_rect)

def drawGameState(screen, gs, validMoves, sqSelected, highlightSquares):
    """
    Draw the complete game state.
    """
    drawBoard(screen)  # Draw squares on the board
    highlightSquares = highlightSquare(screen, gs, validMoves, sqSelected, highlightSquares)
    drawPieces(screen, gs.board)  # Draw pieces on top of squares


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
            center=(LABEL_SIZE // 2,
                    r * SQ_SIZE + SQ_SIZE // 2 + BOARD_OFFSET_Y))
        screen.blit(text, text_rect)

    # Draw column labels (a-h)
    for c in range(DIMENSION):
        text = font.render(chr(ord('a') + c), True, p.Color("black"))
        text_rect = text.get_rect(
            center=(c * SQ_SIZE + SQ_SIZE // 2 + BOARD_OFFSET,
                    HEIGHT - LABEL_SIZE // 2))
        screen.blit(text, text_rect)


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