import pygame
import sys
import random
import time
import threading
from datetime import datetime
from sshtunnel import SSHTunnelForwarder
import mysql.connector

# Initialisierung
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reaction UFO Game")
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

# Farben
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
UFO_COLOR = (100, 255, 100)

# Sterne generieren
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(100)]

# Deine Datenbank-Zugangsdaten
MYSQL_USER = 'pakirathan.ranujan'
MYSQL_PASSWORD = '47118330'
MYSQL_DB = "pakirathan_ranujan"

# SSH-Verbindungsdetails
SSH_HOST = 'ofi.tech-lab.ch'
SSH_PORT = 23  # SSH Standardport
SSH_USER = 'sieber_db'
SSH_PW = 'hanshabersack'  # Dein SSH Passwort (falls benötigt)

# Funktionen
def draw_text(text, size, color, x, y, center=True):
    font = pygame.font.SysFont(None, size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

def draw_space_background():
    screen.fill(BLACK)
    for star in stars:
        pygame.draw.circle(screen, WHITE, star, 2)
        star[1] += 1
        if star[1] > HEIGHT:
            star[0] = random.randint(0, WIDTH)
            star[1] = 0

def draw_ufo(x, y):
    pygame.draw.ellipse(screen, UFO_COLOR, (x, y, 80, 40))
    pygame.draw.ellipse(screen, (0, 255, 255), (x + 20, y - 10, 40, 20))

def ask_username():
    username = ""
    input_active = True

    while input_active:
        draw_space_background()
        draw_text("Gib deinen Namen ein:", 40, WHITE, WIDTH // 2, HEIGHT // 3)
        draw_text(username, 48, WHITE, WIDTH // 2, HEIGHT // 2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 20:
                        username += event.unicode

    return username.strip()

def show_menu():
    while True:
        draw_space_background()
        draw_text("Reaction UFO Game", 60, WHITE, WIDTH//2, HEIGHT//4)
        draw_text("1 - Start Game", 40, WHITE, WIDTH//2, HEIGHT//2)
        draw_text("2 - Quit", 40, WHITE, WIDTH//2, HEIGHT//2 + 60)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return
                elif event.key == pygame.K_2:
                    pygame.quit()
                    sys.exit()

def show_results(times):
    screen.fill(BLACK)
    draw_text("Fertig!", 60, WHITE, WIDTH//2, HEIGHT//4)
    avg_time = sum(times) / len(times)
    for i, t in enumerate(times):
        draw_text(f"UFO {i+1}: {t:.3f} Sekunden", 36, WHITE, WIDTH//2, HEIGHT//2 + i * 30, center=True)
    draw_text(f"⏱ Durchschnitt: {avg_time:.3f} s", 40, WHITE, WIDTH//2, HEIGHT - 100)
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

def play_game():
    times = []
    for i in range(5):
        delay = random.uniform(1.5, 3.5)
        clicked = False
        ufo_x = random.randint(50, WIDTH - 130)
        ufo_y = random.randint(50, HEIGHT - 130)

        wait_start = time.time()
        while time.time() - wait_start < delay:
            draw_space_background()
            draw_text("Bereit für das nächste UFO...", 36, WHITE, WIDTH//2, HEIGHT//2)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        ufo_start = time.time()
        while not clicked:
            draw_space_background()
            draw_ufo(ufo_x, ufo_y)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if ufo_x <= mx <= ufo_x + 80 and ufo_y <= my <= ufo_y + 40:
                        clicked = True
                        reaction_time = time.time() - ufo_start
                        times.append(reaction_time)

                        draw_space_background()
                        draw_ufo(ufo_x, ufo_y)
                        draw_text("Getroffen!", 40, WHITE, WIDTH//2, HEIGHT//2)
                        pygame.display.flip()
                        pygame.time.delay(500)
            clock.tick(60)
    return times

def connect_to_db():
    tunnel = None
    conn = None
    cursor = None

    try:
        tunnel = SSHTunnelForwarder(
            (SSH_HOST, SSH_PORT),
            ssh_username=SSH_USER,
            ssh_password=SSH_PW,
            remote_bind_address=('127.0.0.1', 3306),
            local_bind_address=('127.0.0.1', 3307)
        )
        tunnel.start()

        conn = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = conn.cursor()

        print(f"Verbindung zu {SSH_HOST} Datenbank erfolgreich")
    
    except Exception as e:
        print(f"[connect_to_db] Fehler beim Verbindungsaufbau: {e}")
        return None, None, None
    
    return tunnel, conn, cursor

def save_game_result(username, avg_time, clicks):
    if not username or avg_time <= 0 or clicks <= 0:
        print("[save_game_result] Ungültige Daten, Speicherung übersprungen.")
        return

    tunnel, conn, cursor = None, None, None

    try:
        tunnel, conn, cursor = connect_to_db()

        if conn is None or cursor is None:
            print("[save_game_result] Fehler bei der Verbindung zur DB.")
            return

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = """
            INSERT INTO Player (name, timestamp, avg_time, clicks)
            VALUES (%s, %s, %s, %s)
        """
        values = (username, timestamp, round(avg_time, 3), clicks)
        cursor.execute(sql, values)
        conn.commit()

        print("[save_game_result] Spiel erfolgreich gespeichert.")

    except Exception as e:
        print(f"[save_game_result] Fehler: {e}")

    finally:
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"[save_game_result] Fehler beim Schließen des Cursors: {e}")

        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"[save_game_result] Fehler beim Schließen der Verbindung: {e}")

        if tunnel:
            try:
                tunnel.close()
            except Exception as e:
                print(f"[save_game_result] Fehler beim Schließen des Tunnels: {e}")

def save_game_result_async(username, avg_time, clicks):
    def task():
        try:
            save_game_result(username, avg_time, clicks)
        except Exception as e:
            print(f"[Thread] Fehler im Thread: {e}")

    threading.Thread(target=task, daemon=True).start()

# Hauptprogramm
username = ask_username()

while True:
    show_menu()
    results = play_game()

    if results:
        avg = sum(results) / len(results)
        save_game_result_async(username, avg, len(results))
    else:
        print("[Spiel] Keine Ergebnisse – kein DB-Eintrag.")

    if not show_results(results):
        break

pygame.quit()
