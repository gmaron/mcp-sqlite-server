"""Script para crear y poblar la base de datos SQLite de ejemplo.

Genera 10 usuarios aleatorios mayores de 18 años con datos
representativos de nombres hispanos.
"""

import sqlite3
import random
from datetime import datetime, timedelta


def setup_db() -> None:
    """Crea la tabla ``usuarios`` e inserta 10 registros de prueba.

    La base de datos se genera en el archivo ``users.db`` del
    directorio actual. Si la tabla ya existe se preserva su
    estructura gracias al ``IF NOT EXISTS``.
    """
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            nacionalidad TEXT NOT NULL,
            profesion TEXT NOT NULL,
            fecha_de_nacimiento DATE NOT NULL
        )
    """)

    # Datos para generar usuarios aleatorios
    nombres = [
        "Juan", "Maria", "Carlos", "Ana", "Luis",
        "Lucia", "Diego", "Elena", "Pedro", "Sofia",
    ]
    apellidos = [
        "Gomez", "Rodriguez", "Perez", "Garcia", "Lopez",
        "Martinez", "Sanchez", "Fernandez", "Torres", "Ramirez",
    ]
    nacionalidades = [
        "Argentina", "España", "México",
        "Colombia", "Chile", "Uruguay",
    ]
    profesiones = [
        "Ingeniero", "Médico", "Docente",
        "Arquitecto", "Programador", "Abogado", "Diseñador",
    ]

    # Generar 10 usuarios mayores de 18 años
    hoy = datetime.now()
    inicio_nacimiento = hoy - timedelta(days=365 * 60)  # Hace 60 años
    fin_nacimiento = hoy - timedelta(days=365 * 19)     # Hace 19 años

    for _ in range(10):
        nombre = random.choice(nombres)
        apellido = random.choice(apellidos)
        nacionalidad = random.choice(nacionalidades)
        profesion = random.choice(profesiones)

        # Generar fecha de nacimiento aleatoria
        gap = fin_nacimiento - inicio_nacimiento
        random_days = random.randrange(gap.days)
        fecha_nac = (
            inicio_nacimiento + timedelta(days=random_days)
        ).strftime("%Y-%m-%d")

        cursor.execute(
            """
            INSERT INTO usuarios (
                nombre, apellido, nacionalidad,
                profesion, fecha_de_nacimiento
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (nombre, apellido, nacionalidad, profesion, fecha_nac),
        )

    conn.commit()
    conn.close()
    print("Base de datos 'users.db' creada con 10 usuarios.")


if __name__ == "__main__":
    setup_db()
