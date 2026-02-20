# 🎮 Multiplayer Platformer Game with Chat System

Socket Programming Project - Real-time multiplayer platformer with live chat using Python & Pygame

---

## 📖 Project Overview

A 2D platformer game featuring real-time multiplayer and chat system built with Socket Programming (TCP/IP). Players can see each other, collect gems, defeat enemies, and communicate through an integrated chat system with speech bubbles.

---

## ✨ Key Features

### 🌐 Multiplayer System
- Client-Server architecture using TCP/IP sockets
- Real-time player position synchronization
- Support for multiple concurrent players
- Player join/leave notifications

### 💬 Chat System
- Live chat with speech bubbles above characters
- Messages displayed for 5 seconds
- Toggle chat window visibility
- Broadcast messages to all connected players

### 🎮 Gameplay
- 5 unique levels with increasing difficulty
- Collectible gems and enemy NPCs
- Smooth 60 FPS animations
- Beautiful pixel art graphics
- Camera following system

---

## 🚀 Installation & Setup

### Prerequisites
```bash
Python 3.9+
pip install pygame
```

### Running the Game

**Step 1: Start Server**
```bash
python server.py
```

**Step 2: Start Client(s)**
```bash
python main.py
```
Open multiple terminals to run multiple clients for multiplayer.

---

## 🎮 Controls

| Action | Key |
|--------|-----|
| Move | A/D or Arrow Keys |
| Jump | SPACE |
| Open/Send Chat | ENTER |
| Cancel Chat | ESC |
| Toggle Chat Window | TAB |
| Restart Level | R |

---

## 📁 Project Structure
```
platformer_with_multiplayer/
├── server.py              # Socket server (TCP/IP)
├── main.py                # Game client
├── core/
│   ├── config.py          # Game configuration
│   └── network.py         # Network client module
├── entities/
│   ├── player.py          # Player character logic
│   ├── objects.py         # Platforms, trees, gems
│   └── enemies.py         # Enemy AI
├── levels/
│   └── builder.py         # Level designs (5 levels)
└── ui/
    └── chat.py            # Chat interface
```

---

## 🔧 Technical Implementation

### Network Architecture
- **Protocol:** TCP/IP
- **Port:** 5555
- **Data Format:** JSON
- **Server:** Multi-threaded to handle concurrent connections
- **Client:** Asynchronous message handling with callbacks

### Message Protocol

| Message Type | Purpose | Example |
|--------------|---------|---------|
| INIT | Connection handshake | `{"type": "INIT", "player_id": "P1"}` |
| MOVE | Position update | `{"type": "MOVE", "x": 100, "y": 200}` |
| CHAT | Chat message | `{"type": "CHAT", "text": "Hello!"}` |
| GEM | Item collected | `{"type": "GEM", "gem_id": 12345}` |
| PLAYER_JOIN | New player | `{"type": "PLAYER_JOIN", "player_id": "P2"}` |
| PLAYER_LEAVE | Player disconnect | `{"type": "PLAYER_LEAVE", "player_id": "P2"}` |

### Architecture Diagram
```
       Server (server.py)
              |
    ┌─────────┼─────────┐
    |         |         |
Client 1  Client 2  Client 3
 (P1)      (P2)      (P3)
    |         |         |
    └─────────┴─────────┘
       TCP/IP (Port 5555)
```

---

## 🎓 Learning Objectives

This project demonstrates key concepts in:
- Socket Programming (TCP/IP)
- Client-Server Architecture
- Multi-threading and Concurrency
- Network Protocol Design
- Real-time Data Synchronization
- JSON Serialization
- Game Development with Pygame

---

## 🐛 Troubleshooting

**Issue:** Connection refused  
**Solution:** Ensure server is running before starting clients

**Issue:** Port already in use  
**Solution:**
```bash
lsof -i :5555
kill -9 <PID>
```

---

## 📝 License

MIT License - Feel free to use for educational purposes.

---

⭐ **If you found this project helpful, please star the repository!**
