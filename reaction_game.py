import tkinter as tk
import random
import time
import threading
from datetime import datetime
import paramiko
import pymysql
from sshtunnel import SSHTunnelForwarder
import mysql.connector

# Datenbank und SSH Details
MYSQL_USER = 'pakirathan.ranujan'
MYSQL_PASSWORD = '47118330'
MYSQL_DB = "pakirathan_ranujan"
SSH_HOST = 'ofi.tech-lab.ch'
SSH_PORT = 23
SSH_USER = 'sieber_db'
SSH_PW = 'hanshabersack'

class ReactionGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Reaction UFO Game")
        self.canvas = tk.Canvas(root, width=800, height=600, bg='black')
        self.canvas.pack()

        self.stars = [[random.randint(0, 800), random.randint(0, 600)] for _ in range(100)]
        self.animate_stars()

        self.username = ""
        self.times = []
        self.round = 0
        self.ufo = None
        self.start_time = None

        self.ask_username()

    def animate_stars(self):
        self.canvas.delete("star")
        for star in self.stars:
            self.canvas.create_oval(star[0], star[1], star[0]+2, star[1]+2, fill="white", outline="", tags="star")
            star[1] += 1
            if star[1] > 600:
                star[0] = random.randint(0, 800)
                star[1] = 0
        self.root.after(50, self.animate_stars)

    def ask_username(self):
        top = tk.Toplevel(self.root)
        top.title("Name eingeben")
        top.geometry("300x150")
        top.grab_set()
        name_var = tk.StringVar()

        tk.Label(top, text="Bitte Namen eingeben:", font=("Arial", 12)).pack(pady=10)
        entry = tk.Entry(top, textvariable=name_var, font=("Arial", 14))
        entry.pack()
        entry.focus()

        def submit():
            name = name_var.get().strip()
            if name:
                self.username = name
                top.destroy()
                self.show_menu()

        tk.Button(top, text="Weiter", command=submit, font=("Arial", 12)).pack(pady=10)

    def show_menu(self):
        self.canvas.delete("all")
        self.canvas.create_text(400, 200, text="Reaction UFO Game", fill="white", font=("Arial", 36))
        self.canvas.create_text(400, 300, text="Drücke SPACE zum Starten", fill="white", font=("Arial", 24))
        self.root.bind("<space>", lambda e: self.start_game())

    def start_game(self):
        self.root.unbind("<space>")
        self.times = []
        self.round = 0
        self.next_round()

    def next_round(self):
        if self.round >= 5:
            self.show_results()
            return
        delay = random.uniform(1.5, 3.5)
        self.canvas.delete("ufo")
        self.canvas.create_text(400, 300, text="Bereit für das nächste UFO...", fill="white", font=("Arial", 24), tags="ufo")
        self.root.after(int(delay * 1000), self.spawn_ufo)

    def spawn_ufo(self):
        self.canvas.delete("ufo")
        x = random.randint(50, 720)
        y = random.randint(50, 520)
        self.ufo = self.canvas.create_oval(x, y, x+80, y+40, fill="lime", outline="white", tags="ufo")
        self.canvas.create_oval(x+20, y-10, x+60, y+10, fill="cyan", outline="white", tags="ufo")
        self.start_time = time.time()
        self.canvas.tag_bind("ufo", "<Button-1>", self.hit_ufo)

    def hit_ufo(self, event):
        reaction_time = time.time() - self.start_time
        self.times.append(reaction_time)
        self.round += 1
        self.canvas.delete("ufo")
        self.canvas.create_text(400, 300, text="Getroffen!", fill="white", font=("Arial", 24), tags="ufo")
        self.root.after(500, self.next_round)

    def show_results(self):
        avg_time = sum(self.times) / len(self.times)
        self.canvas.delete("all")
        y = 200
        self.canvas.create_text(400, 100, text="Fertig!", fill="white", font=("Arial", 36))
        for i, t in enumerate(self.times):
            self.canvas.create_text(400, y, text=f"UFO {i+1}: {t:.3f} Sekunden", fill="white", font=("Arial", 18))
            y += 30
        self.canvas.create_text(400, y+30, text=f"⏱ Durchschnitt: {avg_time:.3f} s", fill="white", font=("Arial", 20))
        self.canvas.create_text(400, y+70, text="Drücke R für Replay oder Q zum Beenden", fill="white", font=("Arial", 16))

        self.save_game_result_async(self.username, avg_time, len(self.times))

        self.root.bind("<r>", lambda e: self.reset_game())
        self.root.bind("<q>", lambda e: self.root.destroy())

    def reset_game(self):
        self.root.unbind("<r>")
        self.root.unbind("<q>")
        self.show_menu()

    def connect_with_sshtunnel(self):
        try:
            # SSH-Tunnel aufbauen
            with SSHTunnelForwarder(
                (SSH_HOST, SSH_PORT),
                ssh_username=SSH_USER,
                ssh_password=SSH_PW,
                remote_bind_address=('127.0.0.1', 3306)
            ) as server:
                # MySQL-Verbindung über Tunnel
                conn = mysql.connector.connect(
                    user=MYSQL_USER,
                    password=MYSQL_PASSWORD,
                    host='127.0.0.1',
                    port=server.local_bind_port,
                    database=MYSQL_DB
                )
                print("[DB] MySQL-Verbindung erfolgreich aufgebaut.")
                return conn
        except Exception as e:
            print(f"[DB] Fehler beim Verbinden: {e}")
            return None

    def save_game_result(self, username, avg_time, clicks):
        print(f"[DB] Starte Speichern: username={username}, avg_time={avg_time}, clicks={clicks}")
        conn = self.connect_with_sshtunnel()
        if not conn:
            print("[DB] Keine Verbindung zum MySQL-Server möglich.")
            return
        
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = """INSERT INTO Player (name, timestamp, avg_time, clicks)
                     VALUES (%s, %s, %s, %s)"""
            values = (username, timestamp, round(avg_time, 3), clicks)
            print(f"[DB] SQL: {sql}")
            print(f"[DB] Values: {values}")
            cursor = conn.cursor()
            cursor.execute(sql, values)
            conn.commit()
            print("[DB] Ergebnis erfolgreich gespeichert.")
        except Exception as e:
            print(f"[DB] Fehler beim Speichern: {e}")
        finally:
            try:
                conn.close()
                print("[DB] Verbindung geschlossen.")
            except Exception as e:
                print(f"[DB] Fehler beim Schließen der Verbindung: {e}")

    def save_game_result_async(self, username, avg_time, clicks):
        threading.Thread(target=self.save_game_result, args=(username, avg_time, clicks), daemon=True).start()

# App starten
if __name__ == "__main__":
    root = tk.Tk()
    app = ReactionGameApp(root)
    root.mainloop()
