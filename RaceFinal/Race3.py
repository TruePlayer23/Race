import pygame
import sys
import math

pygame.init()

WIDTH, HEIGHT = 1300, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Гонки")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (34, 177, 76)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
LIGHT_BLUE = (173, 216, 230)
CHECKERED = [(0, 0, 0), (255, 255, 255)]
RED = (255, 0, 0)  # Машинка
ORANGE = (255, 165, 0)
DARK_BLUE = (0, 0, 139)

car_radius = 5  # Размер машинки
car_pos = [100, 100]  # Начальная позиция
last_move = [0, 0]  # Последнее перемещение машинки
inertia_point = None  # Точка инерции
possible_moves = []  # Возможные точки для перемещения
path = []  # Список всех позиций машины
move_count = 0 #Счетчик ходов

# Трассы 
tracks = {
    "Автодром": {
        "points": [
           (200, 200), (1000, 200), (1000, 700), (200, 700),   
           (300, 650), (900, 650),  (900, 250), (300, 250), (300, 650)    
        ],
        "start": (2000, 2000, 0, 0),
        "finish": (2000, 2000, 0, 0),
        "track_width": 150,
        "car_start": (200, 200) 
    },
    "Трасса 1": {
        "points": [
            (50, 100), (500, 100), (100, 300), (500, 400),
            (600, 400), (700, 50), (1000, 400), (600, 600),
            (300, 500), (100, 700), (600, 800), (800, 700),
            (1100, 700)
        ],
        "start": (50, 50, 0, 1),
        "finish": (1100, 650, 0, 1),
        "track_width": 50,
        "car_start": (50, 100)
    },
    "Трасса 2": {
        "points": [
            (150,50), (50, 350), (230, 420), (350, 50), (550, 50), (750, 450),
            (950, 50), (1150, 50), (1050, 450), (950, 550), (650, 550), (450, 250),
            (250, 550), (50, 550), (50, 750), (250, 850), (450, 550), (650, 850), (1150, 750)
        ],
        "start": (100, 50, 1, 0),
        "finish": (1150, 700, 0, 1),
        "track_width": 50,
        "car_start": (150, 50)
    },
    "Трасса 3": {
        "points": [
            (150,50), (50, 450), (150, 620), (330, 350), (250, 50),
            (520, 50), (370, 550), (50, 850), (650, 650), (520, 450),
            (650, 250), (650, 50), (750, 50), (820, 250), (650, 450),
            (850, 750), (850, 450), (950, 350), (880, 50), (1180, 250),
            (980, 550), (980, 750), (1150, 750)
        ],
        "start": (100, 50, 1, 0),
        "finish": (1150, 700, 0, 1),
        "track_width": 45,
        "car_start": (150, 50)
    }
}

# Состояния игры
MENU = 0
RULES = 1
TRACK_SELECTION = 2
GAME = 3

current_state = MENU
current_track = None
track_points = []

def calculate_possible_moves(position):
    moves = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            new_x = position[0] + dx * 25
            new_y = position[1] + dy * 25
            moves.append((new_x, new_y))
    return moves

#Проверка на вылеты   
def is_point_on_track(point):
    x, y = point
    for i in range(len(track_points) - 1):
        x1, y1 = track_points[i]
        x2, y2 = track_points[(i + 1) % len(track_points)]
        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)
        px = x - x1
        py = y - y1
        t = (px * dx + py * dy) / (length * length)
        t = max(0, min(1, t))
        nearest_x = x1 + t * dx
        nearest_y = y1 + t * dy
        distance = math.hypot(x - nearest_x, y - nearest_y)
        if distance <= tracks[current_track]["track_width"]:
            return True
    return False

def check_segment_crossing_track(p1, p2):
    steps = 10
    x1, y1 = p1
    x2, y2 = p2
    
    for i in range(steps + 1):
        t = i / steps
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        if not is_point_on_track((x, y)):
            return True
    return False

def check_finish_line_crossing(path, finish_line):
    if len(path) < 2:
        return False
         
    fx, fy, fdx, fdy = finish_line
    line_length = 100
    
    if fdx == 0:
        line_start = (fx, fy)
        line_end = (fx, fy + fdy * line_length)
    else:
        line_start = (fx, fy)
        line_end = (fx + fdx * line_length, fy)
    
    for i in range(1, len(path)):
        p1 = path[i-1]
        p2 = path[i]
        
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = line_start
        x4, y4 = line_end
        
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if den == 0:
            continue
            
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            return True
            
    return False

def draw_menu():
    screen.fill(LIGHT_BLUE)
    font_large = pygame.font.SysFont("Arial", 60)
    font_medium = pygame.font.SysFont("Arial", 40)
    
    title = font_large.render("ГОНКИ", True, DARK_BLUE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
    
    play_btn = pygame.Rect(WIDTH//2 - 150, 350, 300, 60)
    pygame.draw.rect(screen, GREEN, play_btn, border_radius=10)
    text = font_medium.render("Играть", True, WHITE)
    screen.blit(text, (play_btn.centerx - text.get_width()//2, play_btn.centery - text.get_height()//2))
    
    rules_btn = pygame.Rect(WIDTH//2 - 150, 450, 300, 60)
    pygame.draw.rect(screen, BLUE, rules_btn, border_radius=10)
    text = font_medium.render("Правила игры", True, WHITE)
    screen.blit(text, (rules_btn.centerx - text.get_width()//2, rules_btn.centery - text.get_height()//2))
    
    pygame.display.flip()
    return play_btn, rules_btn

def draw_rules():
    screen.fill(LIGHT_BLUE)
    font_title = pygame.font.SysFont("Arial", 50)
    font_text = pygame.font.SysFont("Arial", 30)
    font_button = pygame.font.SysFont("Arial", 40)
    
    title = font_title.render("Правила игры", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 50))
    
    rules = [
        "1. Выберите трассу для прохождения",
        "2. Красная точка указвает положение машинки",
        "3. Синие точки указывают возможные передвижения машинки.",
        " Нажимайте на них для передвижения",
        "4. Оранжевая точка показывает направление инерции",
        "5. Не выезжайте за пределы трассы",
        "6. Достигните финишной линии, чтобы победить",
        "",
        "Суть игры: С линии старта игрок может выбрать любую из восьми точек вокруг машинки.",
        " Далее рассчитывается место куда машинка попадает по инерции.",
        " Для этого откладывается от положения машинки такое же расстояние и направление,",
        " которое она проехала на предыдущем ходу.",
        " Игрок может выбрать точку куда машинка попадает по инерции",
        " или же любую из 8 точек вокруг точки инерции."
    ]
    
    y_pos = 150
    for rule in rules:
        text = font_text.render(rule, True, BLACK)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
        y_pos += 50
    
    back_btn = pygame.Rect(WIDTH//2 - 100, 850, 200, 60)
    pygame.draw.rect(screen, RED, back_btn, border_radius=10)
    text = font_button.render("Назад", True, WHITE)
    screen.blit(text, (back_btn.centerx - text.get_width()//2, back_btn.centery - text.get_height()//2))
    
    pygame.display.flip()
    return back_btn

def draw_track_selection():
    screen.fill(LIGHT_BLUE)
    font = pygame.font.SysFont("Arial", 40)
    
    title = font.render("Выберите трассу:", True, BLACK)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
    
    buttons = []
    y_pos = 200
    for track_name in tracks.keys():
        btn_rect = pygame.Rect(WIDTH//2 - 150, y_pos, 300, 60)
        pygame.draw.rect(screen, BLUE, btn_rect, border_radius=10)
        text = font.render(track_name, True, WHITE)
        screen.blit(text, (btn_rect.centerx - text.get_width()//2, btn_rect.centery - text.get_height()//2))
        buttons.append((btn_rect, track_name))
        y_pos += 100
    
    back_btn = pygame.Rect(20, 20, 200, 60)
    pygame.draw.rect(screen, RED, back_btn, border_radius=5)
    text = font.render("Назад", True, WHITE)
    screen.blit(text, (back_btn.centerx - text.get_width()//2, back_btn.centery - text.get_height()//2))
    
    pygame.display.flip()
    return buttons, back_btn

def draw_start_finish(start, finish):
    sx, sy, sdx, sdy = start
    start_length = 100
    if sdx == 0:
        start_line = pygame.Rect(sx - tracks[current_track]["track_width"]//2, sy, tracks[current_track]["track_width"], sdy * start_length)
    else:
        start_line = pygame.Rect(sx, sy - tracks[current_track]["track_width"]//2, sdx * start_length, tracks[current_track]["track_width"])
    pygame.draw.rect(screen, LIGHT_BLUE, start_line)
    
    fx, fy, fdx, fdy = finish
    finish_length = 100
    if fdx == 0:
        for i in range(0, finish_length, 20):
            color = CHECKERED[(i // 20) % 2]
            pygame.draw.rect(screen, color, (fx - tracks[current_track]["track_width"]//2, fy + i * (1 if fdy > 0 else -1), tracks[current_track]["track_width"], 20))
    else:
        for i in range(0, finish_length, 20):
            color = CHECKERED[(i // 20) % 2]
            pygame.draw.rect(screen, color, (fx + i * (1 if fdx > 0 else -1), fy - tracks[current_track]["track_width"]//2, 20, tracks[current_track]["track_width"]))

def reset_game_state():
    global car_pos, last_move, inertia_point, possible_moves, path, game_over, win, move_count
    car_pos = list(tracks[current_track]["car_start"])
    last_move = [0, 0]
    inertia_point = None
    possible_moves = calculate_possible_moves(car_pos)
    path = []
    game_over = False
    win = False
    move_count = 0

# БАЗА
running = True
game_over = False
win = False
track_buttons = []
menu_buttons = []
rules_button = None

while running:
    if current_state == MENU:
        play_btn, rules_btn = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_btn.collidepoint(event.pos):
                        current_state = TRACK_SELECTION
                    elif rules_btn.collidepoint(event.pos):
                        current_state = RULES
    
    elif current_state == RULES:
        back_btn = draw_rules()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and back_btn.collidepoint(event.pos):
                    current_state = MENU
    
    elif current_state == TRACK_SELECTION:
        track_buttons, back_btn = draw_track_selection()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_btn.collidepoint(event.pos):
                        current_state = MENU
                    else:
                        for btn_rect, track_name in track_buttons:
                            if btn_rect.collidepoint(event.pos):
                                current_track = track_name
                                track_points = tracks[track_name]["points"]
                                reset_game_state()
                                current_state = GAME
                                break
    
    elif current_state == GAME:
        screen.fill(GREEN)

        font_small = pygame.font.SysFont("Arial", 30)
        text = font_small.render(f"Ходы: {move_count}", True, BLACK)
        screen.blit(text, (WIDTH - 150, 20))
        
        # Отрисовка трассы
        for i in range(len(track_points) - 1):
            x1, y1 = track_points[i]
            x2, y2 = track_points[(i + 1) % len(track_points)]
            pygame.draw.line(screen, GRAY, (x1, y1), (x2, y2), tracks[current_track]["track_width"] * 2)

        draw_start_finish(tracks[current_track]["start"], tracks[current_track]["finish"])

        back_btn = pygame.Rect(20, 20, 100, 40)
        pygame.draw.rect(screen, RED, back_btn, border_radius=5)
        font = pygame.font.SysFont("Arial", 20)
        text = font.render("Назад", True, WHITE)
        screen.blit(text, (back_btn.centerx - text.get_width()//2, back_btn.centery - text.get_height()//2))

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_btn.collidepoint(event.pos):
                        current_state = TRACK_SELECTION
                        continue
                    
                    if not game_over and not win:
                        mouse_pos = pygame.mouse.get_pos()
                        for move in possible_moves:
                            if math.hypot(move[0] - mouse_pos[0], move[1] - mouse_pos[1]) < 10:
                                if check_segment_crossing_track(car_pos, move):
                                    game_over = True
                                    break
                                
                                last_move = [move[0] - car_pos[0], move[1] - car_pos[1]]
                                car_pos = list(move)
                                path.append(car_pos.copy())
                                move_count += 1

                                if check_finish_line_crossing(path, tracks[current_track]["finish"]):
                                    win = True
                                    break

                                inertia_point = [car_pos[0] + last_move[0], car_pos[1] + last_move[1]]
                                possible_moves = calculate_possible_moves(inertia_point)
                                possible_moves.append(inertia_point)
                                break

        # Отрисовка следов
        if len(path) > 1:
            for i in range(1, len(path)):
                x1, y1 = path[i - 1]
                x2, y2 = path[i]
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0 and dy == 0:
                     continue
            
                angle = math.atan2(dy, dx)
        
                offset_x = -math.sin(angle) * 5 
                offset_y = math.cos(angle) * 5
        
                pygame.draw.line(screen, BROWN, 
                        (x1 + offset_x, y1 + offset_y),
                        (x2 + offset_x, y2 + offset_y), 2)
                pygame.draw.line(screen, BROWN,
                        (x1 - offset_x, y1 - offset_y),
                        (x2 - offset_x, y2 - offset_y), 2)

        # Отрисовка машинки и траектории
        pygame.draw.circle(screen, RED, car_pos, car_radius)
        if inertia_point and not game_over and not win:
            pygame.draw.circle(screen, ORANGE, inertia_point, 3)
            pygame.draw.line(screen, ORANGE, car_pos, inertia_point, 2)

        # Отрисовка возможных ходов
        if not game_over and not win:
            for move in possible_moves:
                pygame.draw.circle(screen, BLUE, move, 3)

        if game_over:
            font = pygame.font.SysFont("Arial", 40)
            text = font.render("Вы разбились(", True, RED)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            
            retry_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            pygame.draw.rect(screen, BLUE, retry_btn, border_radius=5)
            text = font.render("Заново", True, WHITE)
            screen.blit(text, (retry_btn.centerx - text.get_width()//2, retry_btn.centery - text.get_height()//2))
            
            mouse_click = pygame.mouse.get_pressed()
            if mouse_click[0] and retry_btn.collidepoint(pygame.mouse.get_pos()):
                reset_game_state()
                
        elif win:
            font = pygame.font.SysFont("Arial", 40)
            text = font.render("Победа!", True, RED)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            
            next_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50)
            pygame.draw.rect(screen, BLUE, next_btn, border_radius=5)
            text = font.render("Далее", True, WHITE)
            screen.blit(text, (next_btn.centerx - text.get_width()//2, next_btn.centery - text.get_height()//2))
            
            mouse_click = pygame.mouse.get_pressed()
            if mouse_click[0] and next_btn.collidepoint(pygame.mouse.get_pos()):
                current_state = TRACK_SELECTION

    pygame.display.flip()

pygame.quit()
sys.exit()