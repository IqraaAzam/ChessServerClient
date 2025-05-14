## ChessServerClient
ChessNet is a multiplayer chess game using Python's socket programming, allowing two players to play in real-time over a network.

# ♟️ Chess Multiplayer Game (Client-Server)

[![GitHub stars](https://img.shields.io/github/stars/IqraaAzam/ChessServerClient?style=flat&logo=github&color=yellow)](https://github.com/IqraaAzam/ChessServerClient/stargazers)

Welcome to the *Chess Multiplayer Game!* 🎮 This is an exciting multiplayer chess game that allows you to play with others in real-time, using Python and sockets for seamless communication. 🌐

The game features both player vs. player and spectator modes, enabling everyone to join the chess battle! 🏆 Whether you're playing or watching, the action never stops. 
## 🔥 Features

### ✨ What’s Included:

+ 🤝 Multiplayer chess with player vs. player support.

+ 👀 Spectator mode to watch ongoing games.

+ 💬 In-game chat for players to communicate.

+ 🔄 Real-time game state updates using socket communication.

+ ⏱️ Timers for each player’s turn to keep things moving.

## 💻 Technologies Used
We’ve used powerful tools and libraries to create this chess game:

+ 🐍 Python 3.x

+ 🔌 Socket Programming (TCP)

+ 🎮 Pygame for the graphical interface (GUI)

+ ♟️ Chess Library for managing game logic

## ⚡ Setup and Installation
### 📦 Requirements
Before running the project, make sure you have Python 3.x installed along with these libraries:

+ **pygame**
+ **chess**

You can install them with **pip**:

```bash
pip install pygame chess

```

## 🗂️ Folder Structure
```bash
chess-multiplayer/
├── assets/            # Chess piece images
├── server.py          # Server-side code
├── client.py          # Client-side code
├── chess_logic.py     # Chess game logic (contains ChessGame class)
└── README.md          # This file

```

### 🚀 Running the Server
To start the server, run the following command in VS Code terminal:
```bash
python server.py
```
The server will start on localhost (127.0.0.1) and listen on port 5555 by default.
### 🎉 Server Output:
![image](https://github.com/user-attachments/assets/a0bbfab4-6cf9-49ff-b503-114e5fec996b)



### 🎮 Running the Client
To run the client and join the game:
```bash
python client.py
```
#### 🎉 Client Output (Example):

![image](https://github.com/user-attachments/assets/c61c14b0-947e-40fd-9575-cae34c391b07)

When prompted, you can choose whether you want to play as a player or spectate an ongoing game. 🧑‍🤝‍🧑

## 📸 Assets
The client needs images for the chess pieces. Make sure they’re in the assets/ folder, following these names:

wp.png – White Pawn

wr.png – White Rook

wn.png – White Knight

wb.png – White Bishop

wq.png – White Queen

wk.png – White King

bp.png – Black Pawn

br.png – Black Rook

bn.png – Black Knight

bb.png – Black Bishop

bq.png – Black Queen

bk.png – Black King

You can replace the images at your own as long as the filenames match. 🖼️

## 🎮 Controls
+ **Player Mode:** Click on a piece to move it, then click the destination square.

+ **Spectator Mode:** Watch the game unfold without interacting. Updates are provided in real-time. 👀

## 📝 Code Overview
### 🖥️ server.py
The server.py file is where the server-side magic happens. It manages client connections, handles game creation, and broadcasts game states and chat messages to both players and spectators.

### 🎮 client.py
The client.py file is the client-side application. It uses Pygame to render the chessboard and take user input. It communicates with the server to send and receive game state updates and chat messages.

### ♟️ chess_logic.py
This file contains the core game logic, including the ChessGame class that handles all chess rules and move validation. It integrates with the chess library to manage game state and piece movement.

## 🔥 Usage Example
Start the server by running:
```bash
python server.py
```
Start the client by running:
```bash
python client.py
```
**Choose whether to play as a player or spectate an ongoing game. 🎮👀**

+ In player mode, click on pieces to move them. ⬇️ 

+ In spectator mode, enjoy watching the game progress. 🧐

### 🤝 Contributing
Feel free to fork this repository and make your contributions! Pull requests are always welcome. 🌟

### 📝 License
This project is licensed under the MIT License. You can freely use, modify, and distribute it. See the LICENSE file for more details.
