"""
Socket Server for Multiplayer Game
"""
import socket
import threading
import json

class GameServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.game_state = {"players": {}, "gems": []}
        self.running = True
        self.client_counter = 0
    
    def start(self):
        try:
            self.server.bind((self.host, self.port))
        except socket.error as e:
            print(f" Error: {e}")
            return
        
        self.server.listen(5)
        print("="*60)
        print("🎮 MULTIPLAYER GAME SERVER")
        print("="*60)
        print(f"Server: {self.host}:{self.port}")
        print("Waiting for connections...")
        print("="*60)
        
        while self.running:
            try:
                conn, addr = self.server.accept()
                self.client_counter += 1
                player_id = f"P{self.client_counter}"
                
                self.clients[conn] = {"id": player_id, "name": f"Player{self.client_counter}"}
                self.game_state["players"][player_id] = {
                    "x": 100 + (self.client_counter - 1) * 50,
                    "y": 500,
                    "name": f"Player{self.client_counter}"
                }
                
                print(f"✅ {player_id} connected from {addr}")
                
                self.send_to_client(conn, {
                    "type": "INIT",
                    "player_id": player_id,
                    "game_state": self.game_state
                })
                
                self.broadcast({"type": "PLAYER_JOIN", "player_id": player_id, "player_data": self.game_state["players"][player_id]}, exclude=conn)
                
                threading.Thread(target=self.handle_client, args=(conn,)).start()
            except:
                pass
    
    def handle_client(self, conn):
        player_id = self.clients[conn]["id"]
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break
                try:
                    message = json.loads(data.decode('utf-8'))
                    self.process_message(conn, message)
                except:
                    pass
        except:
            pass
        finally:
            self.disconnect_client(conn)
    
    def process_message(self, conn, message):
        msg_type = message.get("type")
        player_id = self.clients[conn]["id"]
        
        if msg_type == "MOVE":
            x, y = message.get("x"), message.get("y")
            if player_id in self.game_state["players"]:
                self.game_state["players"][player_id]["x"] = x
                self.game_state["players"][player_id]["y"] = y
            self.broadcast({"type": "PLAYER_MOVE", "player_id": player_id, "x": x, "y": y}, exclude=conn)
        
        elif msg_type == "CHAT":
            text = message.get("text")
            name = self.game_state["players"][player_id]["name"]
            print(f"💬 {name}: {text}")
            self.broadcast({"type": "CHAT", "player_id": player_id, "name": name, "text": text})
        
        elif msg_type == "GEM":
            gem_id = message.get("gem_id")
            if gem_id not in self.game_state["gems"]:
                self.game_state["gems"].append(gem_id)
                self.broadcast({"type": "GEM_COLLECTED", "player_id": player_id, "gem_id": gem_id})
    
    def send_to_client(self, conn, data):
        try:
            conn.send((json.dumps(data) + "\n").encode('utf-8'))
        except:
            pass
    
    def broadcast(self, data, exclude=None):
        message = json.dumps(data) + "\n"
        for conn in list(self.clients.keys()):
            if conn != exclude:
                try:
                    conn.send(message.encode('utf-8'))
                except:
                    pass
    
    def disconnect_client(self, conn):
        if conn in self.clients:
            player_id = self.clients[conn]["id"]
            print(f"❌ {player_id} disconnected")
            if player_id in self.game_state["players"]:
                del self.game_state["players"][player_id]
            self.broadcast({"type": "PLAYER_LEAVE", "player_id": player_id})
            del self.clients[conn]
            conn.close()

if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
