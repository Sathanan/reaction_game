import pygame
import random
import time
import sys
from datetime import datetime
import mysql.connector
from sshtunnel import SSHTunnelForwarder

# ---------- DB KONFIGURATION (aus aktuellem Code übernommen) ----------
def connect_to_db():
    SSH_HOST = 'ofi.tech-lab.ch'
    SSH_PORT = 23
    SSH_USER = 'sieber_db'
    SSH_PW = "hanshabersack"

    MYSQL_HOST = '127.0.0.1'
    MYSQL_PORT = 3306
    MYSQL_USER = 'pakirathan.ranujan'
    MYSQL_PASSWORD = '47118330'
    MYSQL_DB = "pakirathan_ranujan"

    tunnel = SSHTunnelForwarder(
        (SSH_HOST, SSH_PORT),
        ssh_username=SSH_USER,
        ssh_password=SSH_PW,
        remote_bind_address=(MYSQL_HOST, MYSQL_PORT),
        local_bind_address=('127.0.0.1', 3307)
    )
    tunnel.start()

    conn = mysql.connector.connect(
        host='127.0.0.1',
        port=3307,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )
    return tunnel, conn

def save_game_result(username, avg_time, clicks):
    tunnel, conn = connect_to_db()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    sql = """
        INSERT INTO Player (name, timestamp, avg_time, clicks)
        VALUES (%s, %s, %s, %s)
    """
    values = (username, timestamp, avg_time, clicks)
    cursor.execute(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
    tunnel.close()

# ---------- SPIEL SETUP ----------
pygame.init()
WIDTH, HEIGHT = 800, 600
WHITE, BLACK, RED = (255,255,255), (0,0,0), (255,0,0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reaction Space")
font = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()
username = None

def draw_text(text, size, color, x, y, center=True):
    font_obj = pygame.font.SysFont(None, size)
    text_surf = font_obj.render(text, True, color)
    text_rect = text_surf.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    screen.blit(text_surf, text_rect)

def draw_space_background():
    screen.fill((0, 0, 20))
    for _ in range(100):
        pygame.draw.circle(screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)

# ---------- Username-Eingabe (aus aktuellem Code übernommen) ----------
def input_name():
    input_box = pygame.Rect(WIDTH//2 - 140, HEIGHT//2, 280, 50)
    color = pygame.Color('lightskyblue3')
    text = ''
    active = True
    while active:
        draw_space_background()
        draw_text("Bitte gib deinen Namen ein:", 40, WHITE, WIDTH//2, HEIGHT//2 - 60)
        pygame.draw.rect(screen, color, input_box, 2)
        txt_surface = font.render(text, True, color)
        screen.blit(txt_surface, (input_box.x+5, input_box.y+10))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(text) > 0:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 20:
                        text += event.unicode

def show_results(times):
    screen.fill(BLACK)
    draw_text("Fertig!", 60, WHITE, WIDTH//2, HEIGHT//4)
    avg_time = sum(times) / len(times)
    for i, t in enumerate(times):
        draw_text(f"UFO {i+1}: {t:.3f} Sekunden", 36, WHITE, WIDTH//2, HEIGHT//2 + i * 30)
    draw_text(f"⏱ Durchschnitt: {avg_time:.3f} s", 40, WHITE, WIDTH//2, HEIGHT - 100)

    save_game_result(username, avg_time, len(times))

    draw_text("Drücke [R] für Replay oder [Q] zum Beenden", 32, WHITE, WIDTH//2, HEIGHT - 50)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    return False

def main():
    global username
    username = input_name()

    while True:
        times = []
        for _ in range(5):
            screen.fill(BLACK)
            draw_text("Bereit?", 50, WHITE, WIDTH//2, HEIGHT//2)
            pygame.display.flip()
            pygame.time.delay(random.randint(1000, 3000))

            draw_space_background()
            ufo = pygame.Rect(random.randint(50, WIDTH-100), random.randint(50, HEIGHT-100), 60, 60)
            pygame.draw.ellipse(screen, RED, ufo)
            pygame.display.flip()
            start_time = time.time()

            clicked = False
            while not clicked:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if ufo.collidepoint(event.pos):
                            reaction_time = time.time() - start_time
                            times.append(reaction_time)
                            clicked = True

        if not show_results(times):
            break

main()
pygame.quit()

# Old Code
#import pygame
#import random
#import time
#import sys
#from datetime import datetime
#import mysql.connector
#from sshtunnel import SSHTunnelForwarder
#
## ---------- DB KONFIGURATION ----------
#def connect_to_db():
#    SSH_HOST = 'ofi.tech-lab.ch'
#    SSH_PORT = 23
#    SSH_USER = 'sieber_db'
#    SSH_PW = "hanshabersack"
#
#    MYSQL_HOST = '127.0.0.1'
#    MYSQL_PORT = 3306
#    MYSQL_USER = 'pakirathan.ranujan'
#    MYSQL_PASSWORD = '47118330'
#    MYSQL_DB = "pakirathan_ranujan"
#
#    tunnel = SSHTunnelForwarder(
#        (SSH_HOST, SSH_PORT),
#        ssh_username=SSH_USER,
#        ssh_password=SSH_PW,
#        remote_bind_address=(MYSQL_HOST, MYSQL_PORT),
#        local_bind_address=('127.0.0.1', 3307)
#    )
#    tunnel.start()
#
#    conn = mysql.connector.connect(
#        host='127.0.0.1',
#        port=3307,
#        user=MYSQL_USER,
#        password=MYSQL_PASSWORD,
#        database=MYSQL_DB
#    )
#    return tunnel, conn
#
#def save_game_result(username, avg_time, clicks):
#    tunnel, conn = connect_to_db()
#    cursor = conn.cursor()
#    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#
#    sql = """
#        INSERT INTO Player (name, timestamp, avg_time, clicks)
#        VALUES (%s, %s, %s, %s)
#    """
#
#    values = (username, timestamp, avg_time, clicks)
#    cursor.execute("SELECT * FROM Player LIMIT 5;")
#    conn.commit()
#    cursor.close()
#    conn.close()
#    tunnel.close()
#
## ---------- SPIEL SETUP ----------
#pygame.init()
#WIDTH, HEIGHT = 800, 600
#WHITE, BLACK, RED = (255,255,255), (0,0,0), (255,0,0)
#screen = pygame.display.set_mode((WIDTH, HEIGHT))
#pygame.display.set_caption("Reaction Space")
#font = pygame.font.SysFont(None, 40)
#clock = pygame.time.Clock()
#username = None
#
#def draw_text(text, size, color, x, y, center=True):
#    font_obj = pygame.font.SysFont(None, size)
#    text_surf = font_obj.render(text, True, color)
#    text_rect = text_surf.get_rect()
#    if center:
#        text_rect.center = (x, y)
#    else:
#        text_rect.topleft = (x, y)
#    screen.blit(text_surf, text_rect)
#
#def draw_space_background():
#    screen.fill((0, 0, 20))
#    for _ in range(100):
#        pygame.draw.circle(screen, WHITE, (random.randint(0, WIDTH), random.randint(0, HEIGHT)), 1)
#
#def input_name():
#    input_box = pygame.Rect(WIDTH//2 - 140, HEIGHT//2, 280, 50)
#    color = pygame.Color('lightskyblue3')
#    text = ''
#    active = True
#    while active:
#        draw_space_background()
#        draw_text("Bitte gib deinen Namen ein:", 40, WHITE, WIDTH//2, HEIGHT//2 - 60)
#        pygame.draw.rect(screen, color, input_box, 2)
#        txt_surface = font.render(text, True, color)
#        screen.blit(txt_surface, (input_box.x+5, input_box.y+10))
#        pygame.display.flip()
#
#        for event in pygame.event.get():
#            if event.type == pygame.QUIT:
#                pygame.quit()
#                sys.exit()
#            elif event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_RETURN and len(text) > 0:
#                    return text
#                elif event.key == pygame.K_BACKSPACE:
#                    text = text[:-1]
#                else:
#                    if len(text) < 20:
#                        text += event.unicode
#
#def show_results(times):
#    screen.fill(BLACK)
#    draw_text("Fertig!", 60, WHITE, WIDTH//2, HEIGHT//4)
#    avg_time = sum(times) / len(times)
#    for i, t in enumerate(times):
#        draw_text(f"UFO {i+1}: {t:.3f} Sekunden", 36, WHITE, WIDTH//2, HEIGHT//2 + i * 30)
#    draw_text(f"⏱ Durchschnitt: {avg_time:.3f} s", 40, WHITE, WIDTH//2, HEIGHT - 100)
#
#    save_game_result(username, avg_time, len(times))
#
#    draw_text("Drücke [R] für Replay oder [Q] zum Beenden", 32, WHITE, WIDTH//2, HEIGHT - 50)
#    pygame.display.flip()
#
#    while True:
#        for event in pygame.event.get():
#            if event.type == pygame.QUIT:
#                pygame.quit()
#                sys.exit()
#            elif event.type == pygame.KEYDOWN:
#                if event.key == pygame.K_r:
#                    return True
#                elif event.key == pygame.K_q:
#                    return False
#
#def main():
#    global username
#    username = input_name()
#
#    while True:
#        times = []
#        for _ in range(5):
#            screen.fill(BLACK)
#            draw_text("Bereit?", 50, WHITE, WIDTH//2, HEIGHT//2)
#            pygame.display.flip()
#            pygame.time.delay(random.randint(1000, 3000))
#
#            draw_space_background()
#            ufo = pygame.Rect(random.randint(50, WIDTH-100), random.randint(50, HEIGHT-100), 60, 60)
#            pygame.draw.ellipse(screen, RED, ufo)
#            pygame.display.flip()
#            start_time = time.time()
#
#            clicked = False
#            while not clicked:
#                for event in pygame.event.get():
#                    if event.type == pygame.QUIT:
#                        pygame.quit()
#                        sys.exit()
#                    elif event.type == pygame.MOUSEBUTTONDOWN:
#                        if ufo.collidepoint(event.pos):
#                            reaction_time = time.time() - start_time
#                            times.append(reaction_time)
#                            clicked = True
#
#        if not show_results(times):
#            break
#
#main()
#pygame.quit()