import mysql.connector
from sshtunnel import SSHTunnelForwarder

# SSH Tunnel Verbindungsdaten
SSH_HOST = 'ofi.tech-lab.ch'
SSH_PORT = 23
SSH_USER = 'sieber_db'
SSH_PW = "hanshabersack"
# MySQL Datenbank Verbindungsdaten
MYSQL_HOST = '127.0.0.1'        # localhost im Tunnel
MYSQL_PORT = 3306               # MySQL Port
MYSQL_USER = 'pakirathan.ranujan'  # Dein DB Username 
MYSQL_PASSWORD = '47118330'      # Dein DB Passwort
MYSQL_DB = "pakirathan_ranujan"
MYSQL_TABLE = "Player"

with SSHTunnelForwarder(
    (SSH_HOST, SSH_PORT),
    ssh_username=SSH_USER,
    ssh_password=SSH_PW,  
    remote_bind_address=(MYSQL_HOST, MYSQL_PORT),
    local_bind_address=('127.0.0.1', 3306)  
) as tunnel:

    # Verbindung zur MySQL-Datenbank über Tunnel
    # Fehlerbehandlung Verbindungsaufbau
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = conn.cursor()
        print(f"Verbindung zu {SSH_HOST} Datenbank erfolgreich")

        # Beispiel-Abfrage
        cursor.execute("SELECT * FROM " + MYSQL_TABLE + " LIMIT 5;")

        # Alle Ergebnisse anzeigen
        for row in cursor.fetchall():
            print(row)

    except mysql.connector.Error as err:
        print(f"Fehler: {err}")

    finally:
        # Verbindung schliessen
        if cursor:
            cursor.close()
        if conn:
            conn.close()
