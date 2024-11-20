import pygame as p
from Chess import ChessEngine
from Chess import ChessEvaluator

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Add button dimensions
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 120
BUTTON_X = WIDTH // 2 - BUTTON_WIDTH // 2
BUTTON_Y = HEIGHT + 10  # Place button below the board

# Modify window size to accommodate button
WINDOW_HEIGHT = HEIGHT + BUTTON_HEIGHT + 20  # Extra space for button and padding

def loadImages():
    """
    Load images for chess pieces.
    """
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def drawButton(screen, text, x, y, width, height, evaluation=None):
    """
    Draw the evaluation button and display current evaluation if available.
    """
    # Draw button background
    button = p.Rect(x, y, width, height)
    p.draw.rect(screen, p.Color('lightgray'), button)
    p.draw.rect(screen, p.Color('darkgray'), button, 2)

    # Prepare button text
    font = p.font.Font(None, 24)
    if evaluation is None:
        button_text = font.render(text, True, p.Color('black'))
    else:
        # Format evaluation score
        eval_text = f"{text}: {evaluation / 100:.2f}"  # Convert centipawns to pawns
        button_text = font.render(eval_text, True, p.Color('black'))

    # Center text on button
    text_rect = button_text.get_rect(center=button.center)
    screen.blit(button_text, text_rect)

    return button


def main():
    """
    Main driver - handle user input and update graphics.
    """
    p.init()
    screen = p.display.set_mode((WIDTH, WINDOW_HEIGHT))  # Modified height
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    evaluator = ChessEvaluator.ChessEvaluator()  # Create evaluator instance
    current_evaluation = None  # Store current evaluation

    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    highlightSquares = []

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()

                # Check if evaluation button was clicked
                button_rect = p.Rect(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
                if button_rect.collidepoint(location):
                    current_evaluation = evaluator.evaluate_position(gs)
                    continue

                # Handle board clicks
                if location[1] < HEIGHT:  # Only process clicks on the board
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE

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
                                    current_evaluation = None  # Reset evaluation after move

                            if not moveMade:
                                playerClicks = [sqSelected]
                                highlightSquares = []
                                for move in validMoves:
                                    if move.startRow == row and move.startCol == col:
                                        highlightSquares.append((move.endRow, move.endCol))

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    highlightSquares = []
                    current_evaluation = None  # Reset evaluation after undo
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    highlightSquares = []
                    current_evaluation = None  # Reset evaluation after reset

        if moveMade:
            if animate:
                animateMove(screen, gs.moveLog[-1], gs.board, clock)
                animate = False
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected, highlightSquares)
        # Draw evaluation button
        drawButton(screen, "Evaluate", BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, current_evaluation)

        clock.tick(MAX_FPS)
        p.display.flip()


def drawEndGameText(screen, inCheck, gs):
    """
    Draw end game text and play again button.
    """
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

    # Draw game over text
    text_surface = font.render(text, True, p.Color('white'))
    text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20))
    screen.blit(text_surface, text_rect)

    # Draw "Play Again" button
    button_width = WIDTH // 2
    button_height = 30
    button_x = WIDTH // 4
    button_y = HEIGHT // 2 + 20

    p.draw.rect(screen, p.Color('white'),
                p.Rect(button_x, button_y, button_width, button_height))

    play_again_text = font.render("Play Again?", True, p.Color('black'))
    play_again_rect = play_again_text.get_rect(
        center=(WIDTH / 2, button_y + button_height / 2))
    screen.blit(play_again_text, play_again_rect)

def drawGameState(screen, gs, validMoves, sqSelected, highlightSquares):
    """
    Draw the complete game state.
    """
    drawBoard(screen)  # Draw squares on the board
    highlightSquares = highlightSquare(screen, gs, validMoves, sqSelected, highlightSquares)
    drawPieces(screen, gs.board)  # Draw pieces on top of squares

def drawBoard(screen):
    """
    Draw the squares on the board.
    """
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquare(screen, gs, validMoves, sqSelected, highlightSquares):
    """
    Highlight square selected and valid moves for piece selected.
    """
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # Selected a piece that can be moved
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Transparency value -> 0 transparent; 255 opaque
            s.fill(p.Color('mediumaquamarine'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # Highlight valid moves
            #s.fill(p.Color('yellow'))
            #for move in validMoves:
            #    if move.startRow == r and move.startCol == c:
            #        screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
    
    # Highlight previous move
    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('bisque'))
        screen.blit(s, (lastMove.endCol*SQ_SIZE, lastMove.endRow*SQ_SIZE))
        screen.blit(s, (lastMove.startCol*SQ_SIZE, lastMove.startRow*SQ_SIZE))
    
    return highlightSquares

def drawPieces(screen, board):
    """
    Draw the pieces on the board using the current game state.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(screen, move, board, clock):
    """
    Animate the movement of pieces.
    """
    colors = [p.Color("white"), p.Color("gray")]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 2  # Frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # Erase piece from ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Draw moving piece
        if move.pieceCaptured != '--':
            if not move.isEnpassantMove:
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
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