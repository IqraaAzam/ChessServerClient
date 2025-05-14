import chess
import json

class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.white_time = 600  # 10 minutes in seconds
        self.black_time = 600
        self.current_turn = chess.WHITE
        self.move_history = []

    def make_move(self, uci_move):
        try:
            move = chess.Move.from_uci(uci_move)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(uci_move)
                self.current_turn = not self.current_turn
                return True, "Valid move"
            return False, "Illegal move"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_game_state(self):
        return {
            "fen": self.board.fen(),
            "turn": "white" if self.current_turn == chess.WHITE else "black",
            "white_time": self.white_time,
            "black_time": self.black_time,
            "move_history": self.move_history,
            "is_checkmate": self.board.is_checkmate(),
            "is_stalemate": self.board.is_stalemate(),
            "is_game_over": self.board.is_game_over()
        }

    def update_time(self, delta, player_color):
        if player_color == chess.WHITE:
            self.white_time = max(0, self.white_time - delta)
        else:
            self.black_time = max(0, self.black_time - delta)