"""
Network Client
"""
import socket
import threading
import json

class NetworkClient:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = 'localhost'
        self.port = 5555
        self.connected = False
        self.player_id = None
        self.buffer = ""
        
        # Callbacks
        self.on_init = None
        self.on_player_move = None
        self.on_player_join = None
        self.on_player_leave = None
        self.on_chat = None
        self.on_gem_collected = None
    
    def connect(self):
        try:
            self.client.connect((self.host, self.port))
            self.connected = True
            print(f" Connected to {self.host}:{self.port}")
            threading.Thread(target=self.receive_data, daemon=True).start()
            return True
        except Exception as e:
            print(f" Connection failed: {e}")
            return False
    
    def receive_data(self):
        while self.connected:
            try:
                data = self.client.recv(4096).decode('utf-8')
                if not data:
                    self.connected = False
                    break
                self.buffer += data
                while '\n' in self.buffer:
                    line, self.buffer = self.buffer.split('\n', 1)
                    if line:
                        try:
                            message = json.loads(line)
                            self.process_message(message)
                        except:
                            pass
            except:
                self.connected = False
                break
    
    def process_message(self, message):
        msg_type = message.get("type")
        if msg_type == "INIT":
            self.player_id = message.get("player_id")
            if self.on_init:
                self.on_init(message)
        elif msg_type == "PLAYER_MOVE" and self.on_player_move:
            self.on_player_move(message)
        elif msg_type == "PLAYER_JOIN" and self.on_player_join:
            self.on_player_join(message)
        elif msg_type == "PLAYER_LEAVE" and self.on_player_leave:
            self.on_player_leave(message)
        elif msg_type == "CHAT" and self.on_chat:
            self.on_chat(message)
        elif msg_type == "GEM_COLLECTED" and self.on_gem_collected:
            self.on_gem_collected(message)
    
    def send_move(self, x, y):
        self.send_data({"type": "MOVE", "x": x, "y": y})
    
    def send_chat(self, text):
        self.send_data({"type": "CHAT", "text": text})
    
    def send_gem(self, gem_id):
        self.send_data({"type": "GEM", "gem_id": gem_id})
    
    def send_data(self, data):
        if self.connected:
            try:
                self.client.send((json.dumps(data) + "\n").encode('utf-8'))
            except:
                self.connected = False
