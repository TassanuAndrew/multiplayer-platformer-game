"""
Platformer with Multiplayer + Chat
"""
import pygame
import sys
import time
from core.config import *
from core.network import NetworkClient
from entities.player import Player
from entities.objects import *
from entities.enemies import Enemy
from levels.builder import build_level, build_level_2, build_level_3, build_level_4, build_level_5
from ui.chat import ChatBox

# Initialize
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Multiplayer Platformer + Chat")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Network
network = NetworkClient()
other_players = {}
my_player_id = None
player_chat_bubbles = {}  # {player_id: {"text": str, "time": float}}

# Game state
current_level = 1
score = 0
gems_collected = 0
total_gems = 0

# Chat
chat = ChatBox(10, WINDOW_HEIGHT - 180, 350, 170)

def load_level(level_num):
    """Load level"""
    global player, platforms, trees, clouds, gems, enemies, level_width, camera_x, gems_collected, total_gems
    
    player = Player(100, 500)
    camera_x = 0
    gems_collected = 0
    
    if level_num == 1:
        platforms, trees, clouds, gems, enemies, level_width = build_level()
    elif level_num == 2:
        platforms, trees, clouds, gems, enemies, level_width = build_level_2()
    elif level_num == 3:
        platforms, trees, clouds, gems, enemies, level_width = build_level_3()
    elif level_num == 4:
        platforms, trees, clouds, gems, enemies, level_width = build_level_4()
    else:
        platforms, trees, clouds, gems, enemies, level_width = build_level_5()
    
    total_gems = len(gems)
    print(f"Level {level_num} loaded! Gems: {total_gems}")

# Network callbacks
def on_init(message):
    global my_player_id
    my_player_id = message.get("player_id")
    game_state = message.get("game_state", {})
    for pid, pdata in game_state.get("players", {}).items():
        if pid != my_player_id:
            other_players[pid] = {
                "player": Player(pdata["x"], pdata["y"]),
                "name": pdata["name"]
            }
    chat.add_message("System", f"You are {my_player_id}")

def on_player_join(message):
    player_id = message.get("player_id")
    player_data = message.get("player_data")
    if player_id not in other_players and player_id != my_player_id:
        other_players[player_id] = {
            "player": Player(player_data["x"], player_data["y"]),
            "name": player_data["name"]
        }
        chat.add_message("System", f"{player_data['name']} joined")

def on_player_leave(message):
    player_id = message.get("player_id")
    if player_id in other_players:
        name = other_players[player_id]["name"]
        del other_players[player_id]
        chat.add_message("System", f"{name} left")

def on_player_move(message):
    player_id = message.get("player_id")
    if player_id in other_players:
        other_players[player_id]["player"].x = message.get("x")
        other_players[player_id]["player"].y = message.get("y")

def on_chat_message(message):
    name = message.get("name")
    text = message.get("text")
    player_id = message.get("player_id")
    
    # Don't show own name in chat box (avoid "You" + "Player1" overlap)
    if player_id == my_player_id:
        chat.add_message("You", text)
    else:
        chat.add_message(name, text)
    
    # Add speech bubble above player
    player_chat_bubbles[player_id] = {
        "text": text,
        "time": time.time()
    }

def on_gem_collected(message):
    gem_id = message.get("gem_id")
    for gem in gems:
        if id(gem) == gem_id and not gem.collected:
            gem.collected = True
            break

# Set callbacks
network.on_init = on_init
network.on_player_join = on_player_join
network.on_player_leave = on_player_leave
network.on_player_move = on_player_move
network.on_chat = on_chat_message
network.on_gem_collected = on_gem_collected

# Connect
print("Connecting to server...")
if not network.connect():
    print("Server not running!")
    print("Run: python server.py")
    sys.exit()

load_level(current_level)

# Main loop
running = True
keys = set()
level_complete = False
last_position_send = 0

print("="*60)
print("MULTIPLAYER PLATFORMER + CHAT")
print("="*60)
print("Controls:")
print("  A/D: Move | SPACE: Jump")
print("  Type to Chat | R: Restart")
print("="*60)

while running:
    dt = clock.tick(FPS) / 1000.0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Click outside chat to deactivate
            if chat.active and not chat.is_mouse_over(event.pos):
                chat.active = False
                chat.input_text = ""
        
        elif event.type == pygame.KEYDOWN:
            keys.add(event.key)
            
            # Chat (only if not playing)
            message = chat.handle_event(event)
            if message:
                network.send_chat(message)
                player_chat_bubbles[my_player_id] = {
                    "text": message,
                    "time": time.time()
                }
            # If chat is active, skip game controls
            if chat.active:
                continue
            
            if event.key == pygame.K_r:
                load_level(current_level)
                level_complete = False
            elif event.key == pygame.K_n and level_complete:
                if current_level < 5:
                    current_level += 1
                    load_level(current_level)
                    level_complete = False
        
        elif event.type == pygame.KEYUP:
            keys.discard(event.key)
    
    # Input (if not chatting)
    if not chat.active:
        if pygame.K_a in keys or pygame.K_LEFT in keys:
            player.move_left()
        elif pygame.K_d in keys or pygame.K_RIGHT in keys:
            player.move_right()
        else:
            player.stop()
        
        if pygame.K_SPACE in keys or pygame.K_w in keys or pygame.K_UP in keys:
            player.jump()
    
    # Update
    player.update(dt, platforms)
    
    # Send position
    if time.time() - last_position_send > 0.05:
        network.send_move(player.x, player.y)
        last_position_send = time.time()
    
    for tree in trees:
        tree.update(dt)
    
    for cloud in clouds:
        cloud.update(dt)
    
    for gem in gems:
        if not gem.collected:
            gem.update(dt)
            if player.get_rect().colliderect(gem.get_rect()):
                gem.collected = True
                gems_collected += 1
                score += 10
                network.send_gem(id(gem))
                print(f"Gem {gems_collected}/{total_gems}")
                
                if gems_collected >= total_gems:
                    level_complete = True
                    score += 100
                    print(f"Level {current_level} Complete!")
    
    for enemy in enemies:
        if enemy.alive:
            enemy.update(dt, platforms)
            if player.get_rect().colliderect(enemy.get_rect()):
                if player.vel_y > 0 and player.y + player.height - 10 < enemy.y + enemy.height // 2:
                    enemy.stomp()
                    player.vel_y = -8
                    score += 100
                else:
                    player.x = 100
                    player.y = 500
                    player.vel_x = 0
                    player.vel_y = 0
    
    # Camera
    target_camera = player.x - WINDOW_WIDTH // 3
    if target_camera < 0:
        target_camera = 0
    if target_camera > level_width - WINDOW_WIDTH:
        target_camera = level_width - WINDOW_WIDTH
    camera_x += (target_camera - camera_x) * CAMERA_SMOOTHNESS
    
    # Draw
    screen.fill(SKY_COLOR)
    
    for cloud in clouds:
        cloud.draw(screen, camera_x)
    
    water_y = 680
    pygame.draw.rect(screen, WATER_BLUE, (0, water_y, WINDOW_WIDTH, WINDOW_HEIGHT - water_y))
    
    for platform in platforms:
        platform.draw(screen, camera_x)
    
    for tree in trees:
        tree.draw(screen, camera_x)
    
    for gem in gems:
        gem.draw(screen, camera_x)
    
    for enemy in enemies:
        enemy.draw(screen, camera_x)
    
    # Draw other players
    for pid, pdata in other_players.items():
        other_player = pdata["player"]
        other_player.draw(screen, camera_x)
        name_surface = small_font.render(pdata["name"], True, (255, 200, 100))
        name_x = other_player.x - camera_x - name_surface.get_width() // 2 + 16
        name_y = other_player.y - 15
        screen.blit(name_surface, (name_x, name_y))
        
        # Speech bubble
        if pid in player_chat_bubbles:
            bubble_data = player_chat_bubbles[pid]
            if time.time() - bubble_data["time"] < 5:  # Show for 5 seconds
                text = bubble_data["text"]
                bubble_font = pygame.font.Font(None, 16)
                bubble_text = bubble_font.render(text[:30], True, (0, 0, 0))
                
                # Bubble background
                bubble_width = bubble_text.get_width() + 12
                bubble_height = 22
                bubble_x = other_player.x - camera_x - bubble_width // 2 + 16
                bubble_y = other_player.y - 45
                
                # White bubble with border
                pygame.draw.rect(screen, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=8)
                pygame.draw.rect(screen, (100, 100, 100), (bubble_x, bubble_y, bubble_width, bubble_height), 2, border_radius=8)
                
                # Text
                screen.blit(bubble_text, (bubble_x + 6, bubble_y + 4))
            else:
                # Remove expired bubble
                del player_chat_bubbles[pid]
    
    # Draw my player
    player.draw(screen, camera_x)
    if my_player_id:
        my_name = small_font.render("You", True, (100, 255, 100))
        my_name_x = player.x - camera_x - my_name.get_width() // 2 + 16
        my_name_y = player.y - 15
        screen.blit(my_name, (my_name_x, my_name_y))
        
        # My speech bubble
        if my_player_id in player_chat_bubbles:
            bubble_data = player_chat_bubbles[my_player_id]
            if time.time() - bubble_data["time"] < 5:  # Show for 5 seconds
                text = bubble_data["text"]
                bubble_font = pygame.font.Font(None, 16)
                bubble_text = bubble_font.render(text[:30], True, (0, 0, 0))
                
                # Bubble background
                bubble_width = bubble_text.get_width() + 12
                bubble_height = 22
                bubble_x = player.x - camera_x - bubble_width // 2 + 16
                bubble_y = player.y - 45
                
                # White bubble with border
                pygame.draw.rect(screen, (255, 255, 255), (bubble_x, bubble_y, bubble_width, bubble_height), border_radius=8)
                pygame.draw.rect(screen, (100, 100, 100), (bubble_x, bubble_y, bubble_width, bubble_height), 2, border_radius=8)
                
                # Text
                screen.blit(bubble_text, (bubble_x + 6, bubble_y + 4))
            else:
                # Remove expired bubble
                del player_chat_bubbles[my_player_id]
    
    # HUD
    pygame.draw.rect(screen, (0, 0, 0, 100), (10, 10, 250, 100), border_radius=10)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))
    gems_color = GRASS_GREEN if gems_collected >= total_gems else GEM_COLOR
    gems_text = font.render(f"{gems_collected}/{total_gems}", True, gems_color)
    screen.blit(gems_text, (20, 55))
    
    # Online count
    online_text = small_font.render(f"Players: {len(other_players) + 1}", True, WHITE)
    screen.blit(online_text, (WINDOW_WIDTH - 80, 20))
    
    # Chat
    chat.draw(screen)
    
    # Level complete
    if level_complete:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 150), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        screen.blit(overlay, (0, 0))
        
        if current_level < 5:
            complete_text = font.render("LEVEL COMPLETE!", True, GRASS_GREEN)
            next_text = small_font.render("Press N for next", True, WHITE)
        else:
            complete_text = font.render("ALL COMPLETE!", True, (255, 215, 0))
            next_text = small_font.render("You won!", True, WHITE)
        
        screen.blit(complete_text, complete_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 30)))
        screen.blit(next_text, next_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 10)))
    
    # Instructions
    if chat.active:
        inst = small_font.render("Typing... | ENTER: Send | ESC: Cancel | Click outside: Cancel", True, (255, 200, 100))
        screen.blit(inst, (WINDOW_WIDTH // 2 - 300, WINDOW_HEIGHT - 25))
    else:
        inst = small_font.render("A/D: Move | SPACE: Jump | Type to Chat | Ctrl+C: Toggle Chat | R: Restart", True, (100, 100, 100))
        screen.blit(inst, (WINDOW_WIDTH // 2 - 320, WINDOW_HEIGHT - 25))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
