"""Cria o banco resort.db com dados de exemplo. Rode UMA vez: python3 criar_banco.py"""
import sqlite3, os

if os.path.exists("resort.db"):
    os.remove("resort.db")

con = sqlite3.connect("resort.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE quarto (
    id INTEGER PRIMARY KEY,
    numero INTEGER NOT NULL,
    categoria TEXT NOT NULL,
    diaria REAL NOT NULL
)""")

cur.execute("""
CREATE TABLE reserva (
    id INTEGER PRIMARY KEY,
    hospede TEXT NOT NULL,
    quarto_id INTEGER NOT NULL,
    noites INTEGER NOT NULL,
    FOREIGN KEY (quarto_id) REFERENCES quarto(id)
)""")

quartos = [
    (1, 101, "comum", 200.0),
    (2, 102, "comum", 200.0),
    (3, 201, "suite", 500.0),
    (4, 301, "presidencial", 1200.0),
]
cur.executemany("INSERT INTO quarto VALUES (?,?,?,?)", quartos)

reservas = [
    (1, "Ana Souza", 1, 3),
    (2, "Bruno Lima", 3, 2),
    (3, "Carla Dias", 1, 5),
    (4, "Diego Melo", 4, 1),
    (5, "Ana Souza", 3, 2),
]
cur.executemany("INSERT INTO reserva VALUES (?,?,?,?)", reservas)

con.commit()
con.close()
print("Banco resort.db criado: 4 quartos, 5 reservas.")
