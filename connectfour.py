import tkinter as tk
import copy
from tkinter import messagebox
from tkinter import simpledialog
from matplotlib import ticker


ROWS = 6
COLS = 7


PLAYER1 = 'X'
PLAYER2 = 'O'


def initialize_board():
    return [[' ' for _ in range(COLS)] for _ in range(ROWS)]


def make_move(board, col, player):
    row = get_empty_row(board, col)
    if row is not None:
        board[row][col] = player
        return True
    return False


def get_empty_row(board, col):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == ' ':
            return row
    return None

def check_win(board, row, col, player):
    if row is not None and col is not None:

        if count_connected(board, row, col, player, 0, 1) + count_connected(board, row, col, player, 0, -1) >= 4:
            return True


        if count_connected(board, row, col, player, 1, 0) >= 4:
            return True


        if count_connected(board, row, col, player, 1, 1) + count_connected(board, row, col, player, -1, -1) >= 4:
            return True

       
        if count_connected(board, row, col, player, 1, -1) + count_connected(board, row, col, player, -1, 1) >= 4:
            return True

    return False


def count_connected(board, row, col, player, row_dir, col_dir):
    count = 0
    while 0 <= row < ROWS and 0 <= col < COLS and board[row][col] == player:
        count += 1
        row += row_dir
        col += col_dir
    return count

def check_tie(board):
    return all(cell != ' ' for row in board for cell in row)

def evaluate_board(board):
    score = 0

    
    for row in range(ROWS):
        for col in range(COLS - 3):
            score += evaluate_window(board[row][col:col+4])

    
    for row in range(ROWS - 3):
        for col in range(COLS):
            score += evaluate_window([board[row+i][col] for i in range(4)])

    
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            score += evaluate_window([board[row+i][col+i] for i in range(4)])

    
    for row in range(ROWS - 3):
        for col in range(3, COLS):
            score += evaluate_window([board[row+i][col-i] for i in range(4)])

    return score

def evaluate_window(window):

    if window.count(PLAYER2) == 4:
        return 100
    elif window.count(PLAYER2) == 3 and window.count(' ') == 1:
        return 5
    elif window.count(PLAYER2) == 2 and window.count(' ') == 2:
        return 2
    elif window.count(PLAYER1) == 3 and window.count(' ') == 1:
        return -5
    elif window.count(PLAYER1) == 2 and window.count(' ') == 2:
        return -2
    else:
        return 0


def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or check_win(board, None, None, PLAYER1) or check_win(board, None, None, PLAYER2) or check_tie(board):
        return {'score': evaluate_board(board), 'col': None}

    available_moves = get_available_moves(board)
    best_move = {'score': float('-inf') if maximizing_player else float('inf'), 'col': None}

    for move in available_moves:
        new_board = make_move_copy(board, move, PLAYER2 if maximizing_player else PLAYER1)
        score = minimax(new_board, depth - 1, alpha, beta, not maximizing_player)['score']

        if maximizing_player:
            if score > best_move['score']:
                best_move['score'] = score
                best_move['col'] = move
            alpha = max(alpha, best_move['score'])
        else:
            if score < best_move['score']:
                best_move['score'] = score
                best_move['col'] = move
            beta = min(beta, best_move['score'])

        if beta <= alpha:
            break

    return best_move

def get_available_moves(board):
    return [col for col in range(COLS) if board[0][col] == ' ']


def make_move_copy(board, col, player):
    new_board = copy.deepcopy(board)
    make_move(new_board, col, player)
    return new_board

class ConnectFourGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Connect Four")
        self.board = initialize_board()
        self.current_player = PLAYER1
        self.create_board_buttons()
        self.create_status_label()

    def create_board_buttons(self):
        for row in range(ROWS):
            for col in range(COLS):
                button = tk.Button(self.root, text='', width=4, height=2, command=lambda r=row, c=col: self.make_move(r, c))
                button.grid(row=row, column=col)

    def create_status_label(self):
        self.status_label = tk.Label(self.root, text=f"Player {self.current_player}'s turn")
        self.status_label.grid(row=ROWS, columnspan=COLS)

    def make_move(self, row, col):
        if make_move(self.board, col, self.current_player):
            self.update_button_text(row, col)
            if check_win(self.board, row, col, self.current_player):
                self.show_winner_message()
                self.reset_game()
            elif check_tie(self.board):
                self.show_tie_message()
                self.reset_game()
            else:
                self.current_player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1
                self.update_status_label()
                
                if self.current_player == PLAYER2:
                    self.make_ai_move()

    def make_ai_move(self):
        ai_move = minimax(self.board, 4, float('-inf'), float('inf'), True)['col']
        if ai_move is not None:
            self.make_move(get_empty_row(self.board, ai_move), ai_move)

    def update_button_text(self, row, col):
        button = self.root.grid_slaves(row=row, column=col)[0]
        button.config(text=self.current_player)

    def update_status_label(self):
        self.status_label.config(text=f"Player {self.current_player}'s turn")

    def show_winner_message(self):
        winner = f"Player {self.current_player}"
        self.show_message_dialog("Game Over", f"{winner} wins!")

    def show_tie_message(self):
        self.show_message_dialog("Game Over", "It's a tie!")

    def show_message_dialog(self, title, message):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
    
        label = tk.Label(dialog, text=message)
        label.pack(padx=10, pady=10)

        ok_button = tk.Button(dialog, text="OK", command=dialog.destroy)
        ok_button.pack(pady=10)

    def reset_game(self):
        self.board = initialize_board()
        for button in self.root.grid_slaves():
            button.config(text='')
        self.current_player = PLAYER1
        self.update_status_label()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = ConnectFourGUI()
    gui.run()
