import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple

class Player(NamedTuple):
    name: str  # Armazena o nome do jogador
    label: str
    color: str

class Move(NamedTuple):
    row: int
    col: int
    label: str = ""

BOARD_SIZE = 3

class TicTacToeGame:
    def __init__(self, players, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [[(move.row, move.col) for move in row] for row in self._current_moves]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def toggle_player(self):
        """Alterna para o próximo jogador."""
        self.current_player = next(self._players)

    def is_valid_move(self, move):
        """Verifica se o movimento é válido."""
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    def process_move(self, move):
        """Processa a jogada e verifica vitória."""
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self):
        return self._has_winner

    def is_tied(self):
        no_winner = not self._has_winner
        played_moves = (move.label for row in self._current_moves for move in row)
        return no_winner and all(played_moves)

    def reset_game(self):
        """Reinicia o jogo."""
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []
        self.current_player = next(self._players)  # Reinicia para o primeiro jogador

class TicTacToeBoard(tk.Tk):
    def __init__(self, game, player1_name, player2_name):
        super().__init__()
        self.title("Jogo da Velha")
        self._cells = {}
        self._game = game
        self.player1_name = player1_name
        self.player2_name = player2_name
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()
        self._create_reset_button()  # Adiciona o botão de reiniciar

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Jogar Novamente", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=quit)
        menu_bar.add_cascade(label="Opções", menu=file_menu)

    def _create_board_display(self):
        """Cria a área onde será exibido o turno atual."""
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text=f"Turno de {self._game.current_player.name}",
            font=font.Font(size=20, weight="bold"),
        )
        self.display.pack()

    def _create_board_grid(self):
        """Cria o tabuleiro do jogo."""
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def _create_reset_button(self):
        """Cria um botão para reiniciar o jogo."""
        reset_button = tk.Button(
            master=self,
            text="Reiniciar Jogo",
            font=font.Font(size=14, weight="bold"),
            fg="black",
            bg="lightgray",
            command=self.reset_board,
        )
        reset_button.pack(pady=10)

    def play(self, event):
        """Gerencia a jogada do jogador."""
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display("Empate!", "red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f"{self._game.current_player.name} venceu!"
                color = self._game.current_player.color
                self._update_display(msg, color)
            else:
                self._game.toggle_player()
                self._update_display(f"Turno de {self._game.current_player.name}")

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def reset_board(self):
        """Reinicia o tabuleiro e o jogo."""
        self._game.reset_game()
        self._update_display(f"Turno de {self._game.current_player.name}")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")

def iniciar_jogo(player1_name, player2_name):
    """Inicia o jogo com os nomes dos jogadores."""
    players = (
        Player(name=player1_name, label="X", color="blue"),
        Player(name=player2_name, label="O", color="green"),
    )
    game = TicTacToeGame(players)
    board = TicTacToeBoard(game, player1_name, player2_name)
    board.mainloop()

def main():
    """Cria a tela de entrada de nomes e inicia o jogo."""
    root = tk.Tk()
    root.title("Captura de Nomes")
    root.geometry("300x200")

    tk.Label(root, text="Player 1:").pack(pady=5)
    entrada_player1 = tk.Entry(root)
    entrada_player1.pack(pady=5)

    tk.Label(root, text="Player 2:").pack(pady=5)
    entrada_player2 = tk.Entry(root)
    entrada_player2.pack(pady=5)

    def capturar_nomes():
        player1_name = entrada_player1.get()
        player2_name = entrada_player2.get()
        root.destroy()  # Destroi a janela de captura de nomes
        iniciar_jogo(player1_name, player2_name)  # Inicia o jogo

    tk.Button(root, text="Iniciar Jogo", command=capturar_nomes).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()