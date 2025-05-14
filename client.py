import socket
import threading
import json
import pygame
import chess
import sys
import time
import os
import argparse

class ChessClient:
    def __init__(self, host='127.0.0.1', port=5555, mode="player"):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.mode = mode
        self.connect()
        self.board = chess.Board()
        self.color = None
        self.game_id = None
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Multiplayer Chess")
        self.clock = pygame.time.Clock()
        self.chat_messages = []
        self.input_text = ""
        self.selected_square = None
        self.running = True
        self.disconnected = False

        # Load chess piece images
        self.piece_images = {}
        assets_path = os.path.join(os.path.dirname(__file__), 'assets')
        print(f"Looking for assets in: {assets_path}")
        piece_symbols = {
            'p': 'p', 'r': 'r', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k'
        }
        for color in ['w', 'b']:
            for symbol, name in piece_symbols.items():
                filename = f"{color}{name}.png"
                filepath = os.path.join(assets_path, filename)
                if os.path.exists(filepath):
                    try:
                        image = pygame.image.load(filepath).convert_alpha()
                        self.piece_images[f"{color}{symbol}"] = image
                        print(f"Loaded image: {filename}")
                    except pygame.error as e:
                        print(f"Error loading {filename}: {e}")
                else:
                    print(f"Warning: Image {filename} not found at {filepath}")

    def connect(self):
        try:
            self.client.connect((self.host, self.port))
        except Exception as e:
            print(f"Connection failed: {e}")
            self.running = False

    def send_initial_message(self):
        try:
            self.client.send(json.dumps({"type": self.mode}).encode() + b"\n")
            if self.mode == "spectator":
                data = self.client.recv(1024).decode()
                message = json.loads(data)
                if message.get("action") == "game_list":
                    print("Available games:", message["games"])
                    game_id = input("Enter game ID to spectate (or press Enter to join first available): ")
                    if not game_id:
                        game_id = message["games"][0] if message["games"] else None
                    if game_id:
                        self.game_id = int(game_id)  # Set game_id here
                        self.client.send(json.dumps({"game_id": int(game_id)}).encode() + b"\n")
        except Exception as e:
            print(f"Error sending initial message: {e}")
            self.running = False

    def draw_board(self):
        square_size = 50
        for row in range(8):
            for col in range(8):
                color = (255, 255, 255) if (row + col) % 2 == 0 else (100, 100, 100)
                pygame.draw.rect(self.screen, color, (col * square_size, row * square_size, square_size, square_size))
                piece = self.board.piece_at(chess.square(col, 7 - row))
                if piece:
                    piece_symbol = piece.symbol().lower()
                    color_symbol = 'w' if piece.color == chess.WHITE else 'b'
                    key = f"{color_symbol}{piece_symbol}"
                    if key in self.piece_images:
                        image = self.piece_images[key]
                        image = pygame.transform.scale(image, (int(square_size * 0.8), int(square_size * 0.8)))
                        self.screen.blit(image, (col * square_size + square_size * 0.1, row * square_size + square_size * 0.1))
                    else:
                        print(f"Missing image for key: {key}")
                        pygame.draw.circle(self.screen, (0, 0, 255) if piece.color == chess.WHITE else (255, 0, 0),
                                          ((col + 0.5) * square_size, (row + 0.5) * square_size), 20)
        if self.selected_square is not None and self.mode == "player":
            col, row = chess.square_file(self.selected_square), 7 - chess.square_rank(self.selected_square)
            pygame.draw.rect(self.screen, (0, 255, 0), (col * square_size, row * square_size, square_size, square_size), 3)

    def draw_chat(self):
        font = pygame.font.Font(None, 24)
        pygame.draw.rect(self.screen, (220, 220, 220), (420, 150, 350, 300))
        y = 160
        for msg in self.chat_messages[-5:]:
            text = font.render(msg, True, (0, 0, 0))
            self.screen.blit(text, (430, y))
            y += 25
        pygame.draw.rect(self.screen, (255, 255, 255), (420, 410, 350, 30))
        input_box = font.render(f"> {self.input_text}", True, (0, 0, 0))
        self.screen.blit(input_box, (430, 415))

    def draw_timers(self):
        font = pygame.font.Font(None, 36)
        white_time = self.board.white_time if hasattr(self.board, 'white_time') else 600
        black_time = self.board.black_time if hasattr(self.board, 'black_time') else 600
        white_text = font.render(f"White: {int(white_time)}s", True, (0, 0, 0))
        black_text = font.render(f"Black: {int(black_time)}s", True, (0, 0, 0))
        self.screen.blit(white_text, (420, 50))
        self.screen.blit(black_text, (420, 80))

    def handle_click(self, pos):
        if self.mode == "player":
            square_size = 50
            col, row = pos[0] // square_size, pos[1] // square_size
            square = chess.square(col, 7 - row)
            if self.selected_square is None:
                if self.board.piece_at(square) and self.board.piece_at(square).color == self.color:
                    self.selected_square = square
            else:
                move = chess.Move(self.selected_square, square)
                if move in self.board.legal_moves and self.game_id is not None:
                    uci_move = move.uci()
                    try:
                        self.client.send(json.dumps({"action": "move", "move": uci_move, "game_id": self.game_id}).encode() + b"\n")
                        print(f"Sent move: {uci_move}")
                    except:
                        self.chat_messages.append("Error: Failed to send move. Reconnecting...")
                        self.reconnect()
                self.selected_square = None

    def reconnect(self):
        self.disconnected = True
        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        if self.running and self.game_id:
            self.client.send(json.dumps({"action": "reconnect", "game_id": self.game_id}).encode() + b"\n")
            self.disconnected = False

    def receive_messages(self):
        buffer = ""
        while self.running:
            try:
                data = self.client.recv(1024).decode()
                if not data:
                    self.disconnected = True
                    break
                buffer += data
                while "\n" in buffer:
                    message_end = buffer.index("\n")
                    message_str = buffer[:message_end].strip()
                    buffer = buffer[message_end + 1:].strip()
                    if message_str:
                        try:
                            message = json.loads(message_str)
                            print(f"Received ({self.mode}): {message}")  # Debug
                            action = message.get("action")
                            if action == "start":
                                self.color = chess.WHITE if message["color"] == "white" else chess.BLACK
                                self.game_id = message["game_id"]
                            elif action == "update":
                                self.board = chess.Board(message["state"]["fen"])
                                self.board.white_time = message["state"]["white_time"]
                                self.board.black_time = message["state"]["black_time"]
                                turn = message["state"]["turn"]
                                print(f"Current turn: {turn.capitalize()}")
                            elif action == "chat":
                                self.chat_messages.append(message["message"])
                            elif action == "error":
                                self.chat_messages.append(f"Error: {message['message']}")
                            elif action == "opponent_disconnected":
                                self.chat_messages.append("Opponent disconnected. Waiting for reconnection...")
                                self.disconnected = True
                            elif action == "reconnected":
                                self.chat_messages.append("Reconnected to game!")
                                self.disconnected = False
                            elif action == "game_over":
                                self.chat_messages.append(f"Game Over: {message['reason']}")
                                self.running = False
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}, Buffer: {message_str[:50]}...")
                            continue
            except Exception as e:
                print(f"Receive error: {e}")
                self.disconnected = True
                break

        if self.disconnected and self.running:
            self.reconnect()

    def run(self):
        self.send_initial_message()
        threading.Thread(target=self.receive_messages, daemon=True).start()
        pygame.init()
        font = pygame.font.Font(None, 36)
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and self.color is not None and not self.disconnected:
                    self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.input_text:
                            try:
                                self.client.send(json.dumps({"action": "chat", "message": self.input_text}).encode() + b"\n")
                                self.chat_messages.append(f"You: {self.input_text}")
                                self.input_text = ""
                            except:
                                self.chat_messages.append("Error: Failed to send chat. Reconnecting...")
                                self.reconnect()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    else:
                        self.input_text += event.unicode

            self.screen.fill((200, 200, 200))
            self.draw_board()
            self.draw_chat()
            self.draw_timers()
            if self.mode == "spectator":
                font = pygame.font.Font(None, 30)
                text = font.render("Spectator Mode", True, (0, 0, 0))
                self.screen.blit(text, (420, 120))
            pygame.display.flip()
            self.clock.tick(60)

        self.client.close()
        pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multiplayer Chess Client")
    parser.add_argument("--mode", choices=["player", "spectator"], default="player", help="Mode to join as (player or spectator)")
    args = parser.parse_args()
    client = ChessClient(mode=args.mode)
    client.run()