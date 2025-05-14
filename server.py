import socket
import threading
import json
import chess
import time
from chess_logic import ChessGame

class ChessServer:
    def __init__(self, host='0.0.0.0', port=5555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(10)
        print("Server started on port 5555...")
        self.games = {}  # game_id: ChessGame
        self.clients = {}  # client_socket: {"type": "player"/"spectator", "game_id": int, "color": bool, "addr": tuple}
        self.lobby = []  # List of waiting players
        self.game_counter = 0
        self.lock = threading.Lock()

    def handle_client(self, client_socket, addr):
        try:
            data = client_socket.recv(1024).decode()
            initial_message = json.loads(data)
            client_type = initial_message.get("type", "player")
            with self.lock:
                self.clients[client_socket] = {"type": client_type, "game_id": None, "color": None, "addr": addr}

            if client_type == "player":
                self.handle_player(client_socket)
            else:
                self.handle_spectator(client_socket)
        except Exception as e:
            print(f"Error with client {addr}: {e}")
        finally:
            self.disconnect_client(client_socket)

    def handle_player(self, client_socket):
        with self.lock:
            self.lobby.append(client_socket)
            print(f"Player added to lobby. Lobby size: {len(self.lobby)}")
            if len(self.lobby) >= 2:
                player1 = self.lobby.pop(0)
                player2 = self.lobby.pop(0)
                self.start_game(player1, player2)

        buffer = ""
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                buffer += data
                while buffer:
                    try:
                        message_end = buffer.find("\n")
                        if message_end == -1:
                            break
                        message_str = buffer[:message_end].strip()
                        buffer = buffer[message_end + 1:].strip()
                        if message_str:
                            message = json.loads(message_str)
                            action = message.get("action")
                            game_id = message.get("game_id", self.clients[client_socket]["game_id"])
                            print(f"Received from {self.clients[client_socket]['addr']}: {message}")

                            if action == "move" and game_id in self.games:
                                with self.lock:
                                    success, reason = self.games[game_id].make_move(message["move"])
                                    print(f"Move processed: {message['move']}, Success: {success}, Reason: {reason}")
                                    if success:
                                        self.broadcast_game_state(game_id)
                                    else:
                                        client_socket.send(json.dumps({"action": "error", "message": reason}).encode() + b"\n")
                            elif action == "chat":
                                self.broadcast_chat(game_id, message["message"], client_socket)
                            elif action == "reconnect":
                                self.handle_reconnection(client_socket, message.get("game_id"))
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}, Buffer: {buffer[:50]}...")
                        if not buffer.strip():
                            break
                        continue
            except Exception as e:
                print(f"Error in handle_player: {e}")
                break

    def start_game(self, player1, player2):
        self.game_counter += 1
        game_id = self.game_counter
        self.games[game_id] = ChessGame()
        self.clients[player1]["game_id"] = game_id
        self.clients[player1]["color"] = chess.WHITE
        self.clients[player2]["game_id"] = game_id
        self.clients[player2]["color"] = chess.BLACK

        player1.send(json.dumps({"action": "start", "color": "white", "game_id": game_id}).encode() + b"\n")
        player2.send(json.dumps({"action": "start", "color": "black", "game_id": game_id}).encode() + b"\n")
        self.broadcast_game_state(game_id)

        threading.Thread(target=self.timer_thread, args=(game_id,)).start()

    def handle_spectator(self, client_socket):
        client_socket.send(json.dumps({"action": "game_list", "games": list(self.games.keys())}).encode() + b"\n")
        data = client_socket.recv(1024).decode()
        message = json.loads(data)
        game_id = message.get("game_id")
        if game_id in self.games:
            with self.lock:
                self.clients[client_socket]["game_id"] = game_id
                self.broadcast_game_state(game_id)
            # Keep spectator active to receive updates
            buffer = ""
            while True:
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break
                    buffer += data
                    while buffer:
                        try:
                            message_end = buffer.find("\n")
                            if message_end == -1:
                                break
                            message_str = buffer[:message_end].strip()
                            buffer = buffer[message_end + 1:].strip()
                            if message_str:
                                message = json.loads(message_str)
                                action = message.get("action")
                                if action == "chat":
                                    self.broadcast_chat(game_id, message["message"], client_socket)
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}, Buffer: {buffer[:50]}...")
                            if not buffer.strip():
                                break
                            continue
                except Exception as e:
                    print(f"Error in handle_spectator: {e}")
                    break

    def handle_reconnection(self, client_socket, game_id):
        if game_id in self.games:
            with self.lock:
                self.clients[client_socket]["game_id"] = game_id
                self.clients[client_socket]["type"] = "player"
                self.clients[client_socket]["color"] = chess.WHITE if len([c for c, info in self.clients.items() if info["game_id"] == game_id and info["color"] == chess.BLACK]) > 0 else chess.BLACK
                client_socket.send(json.dumps({"action": "reconnected", "game_id": game_id, "color": "white" if self.clients[client_socket]["color"] == chess.WHITE else "black"}).encode() + b"\n")
                self.broadcast_game_state(game_id)

    def broadcast_game_state(self, game_id):
        if game_id in self.games:
            game_state = self.games[game_id].get_game_state()
            message = json.dumps({"action": "update", "state": game_state}) + "\n"
            for client, info in self.clients.items():
                if info["game_id"] == game_id:
                    print(f"Broadcasting to {info['type']} at {info['addr']} for game {game_id}")
                    try:
                        client.send(message.encode())
                    except:
                        print(f"Failed to send update to {info['addr']}")

    def broadcast_chat(self, game_id, chat_message, sender_socket):
        message = json.dumps({"action": "chat", "message": chat_message}) + "\n"
        for client, info in self.clients.items():
            if info["game_id"] == game_id and client != sender_socket:
                try:
                    client.send(message.encode())
                except:
                    print(f"Failed to send chat to {info['addr']}")

    def timer_thread(self, game_id):
        last_time = time.time()
        while game_id in self.games and not self.games[game_id].get_game_state()["is_game_over"]:
            current_time = time.time()
            delta = current_time - last_time
            last_time = current_time
            with self.lock:
                current_turn = chess.WHITE if self.games[game_id].board.turn == chess.WHITE else chess.BLACK
                self.games[game_id].update_time(delta, current_turn)
                self.broadcast_game_state(game_id)
            time.sleep(1)

    def disconnect_client(self, client_socket):
        with self.lock:
            if client_socket in self.clients:
                game_id = self.clients[client_socket]["game_id"]
                if game_id in self.games and self.clients[client_socket]["type"] == "player":
                    for client, info in self.clients.items():
                        if info["game_id"] == game_id and client != client_socket:
                            client.send(json.dumps({"action": "opponent_disconnected", "game_id": game_id}).encode() + b"\n")
                if client_socket in self.lobby:
                    self.lobby.remove(client_socket)
                del self.clients[client_socket]
                client_socket.close()

    def run(self):
        while True:
            client_socket, addr = self.server.accept()
            print(f"New connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    server = ChessServer()
    server.run()