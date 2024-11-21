import pygame as p


class MoveHistory:
    def __init__(self, screen_height, move_height=30, font_size=16):
        self.moves = []  # List of moves
        self.scroll_y = 0  # Scroll position
        self.selected_index = -1  # Currently selected move
        self.visible_moves = screen_height // move_height
        self.MOVE_HEIGHT = move_height
        self.FONT_SIZE = font_size

    def add_move(self, move, current_move_number):
        """Add a move to the history"""
        if current_move_number % 2 == 1:  # White's move
            self.moves.append({
                'move_number': (current_move_number + 1) // 2,
                'white': move.getStandardAlgebraicNotation(),
                'black': ''
            })
        else:  # Black's move
            self.moves[-1]['black'] = move.getStandardAlgebraicNotation()

    def clear(self):
        """Clear the move history"""
        self.moves = []
        self.scroll_y = 0
        self.selected_index = -1

    def scroll(self, amount):
        """Scroll the move history"""
        max_scroll = max(0, len(self.moves) * self.MOVE_HEIGHT - self.screen_height + 20)
        self.scroll_y = max(0, min(self.scroll_y + amount, max_scroll))


def drawMoveHistory(screen, history, x, y, width, height):
    """Draw the move history panel"""
    # Draw background
    history_rect = p.Rect(x, y, width, height)
    p.draw.rect(screen, p.Color('white'), history_rect)
    p.draw.rect(screen, p.Color('black'), history_rect, 2)

    # Draw title
    font = p.font.Font(None, history.FONT_SIZE + 4)
    title = font.render("Move History", True, p.Color('black'))
    title_rect = title.get_rect(midtop=(x + width // 2, y + 5))
    screen.blit(title, title_rect)

    # Create clipping rect for moves
    moves_rect = p.Rect(x, y + 30, width, height - 30)
    screen.set_clip(moves_rect)

    # Draw moves
    font = p.font.Font(None, history.FONT_SIZE)
    y_pos = y + 30 - history.scroll_y

    for i, move_data in enumerate(history.moves):
        if y_pos + history.MOVE_HEIGHT < y + 30:
            y_pos += history.MOVE_HEIGHT
            continue

        if y_pos > y + height:
            break

        # Draw move number
        number_text = f"{move_data['move_number']}."
        number_surface = font.render(number_text, True, p.Color('black'))
        screen.blit(number_surface, (x + 5, y_pos + 5))

        # Draw white's move
        white_text = move_data['white']
        white_surface = font.render(white_text, True, p.Color('black'))
        screen.blit(white_surface, (x + 35, y_pos + 5))

        # Draw black's move
        black_text = move_data['black']
        black_surface = font.render(black_text, True, p.Color('black'))
        screen.blit(black_surface, (x + 110, y_pos + 5))

        # Highlight selected move
        if i == history.selected_index:
            highlight_rect = p.Rect(x + 2, y_pos, width - 4, history.MOVE_HEIGHT)
            p.draw.rect(screen, p.Color('lightblue'), highlight_rect, 2)

        y_pos += history.MOVE_HEIGHT

    screen.set_clip(None)

    # Draw scroll indicators if needed
    if len(history.moves) * history.MOVE_HEIGHT > height - 30:
        if history.scroll_y > 0:
            p.draw.polygon(screen, p.Color('black'), [
                (x + width - 15, y + 35),
                (x + width - 10, y + 40),
                (x + width - 5, y + 35)
            ])

        if history.scroll_y < (len(history.moves) * history.MOVE_HEIGHT - height + 30):
            p.draw.polygon(screen, p.Color('black'), [
                (x + width - 15, y + height - 5),
                (x + width - 10, y + height - 10),
                (x + width - 5, y + height - 5)
            ])