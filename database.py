import sqlite3

DATABASE = 'favoritos.db'

def init_db():
    """Crea la tabla si no existe"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anime_id INTEGER UNIQUE,
            titulo TEXT,
            imagen TEXT,
            score REAL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Base de datos 'favoritos.db' lista.")

def agregar_favorito(anime_id, titulo, imagen, score):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        # Intentamos insertar. Si ya existe (anime_id repetido), no hace nada o actualiza
        # Aquí usamos INSERT OR REPLACE para simplificar: si existe, lo reescribe (efecto toggle)
        cursor.execute('''
            INSERT OR REPLACE INTO favoritos (anime_id, titulo, imagen, score)
            VALUES (?, ?, ?, ?)
        ''', (anime_id, titulo, imagen, score))
        conn.commit()
        print(f"✅ Guardado favorito: {titulo}")
        return True
    except Exception as e:
        print(f"❌ Error al guardar: {e}")
        return False
    finally:
        conn.close()

def eliminar_favorito(anime_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM favoritos WHERE anime_id = ?', (anime_id,))
        conn.commit()
        print(f"🗑️ Eliminado favorito ID: {anime_id}")
        return True
    except Exception as e:
        print(f"❌ Error al eliminar: {e}")
        return False
    finally:
        conn.close()

def obtener_favoritos():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM favoritos ORDER BY id DESC')
    lista = cursor.fetchall()
    conn.close()
    return lista

def es_favorito(anime_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM favoritos WHERE anime_id = ?', (anime_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Inicializar al importar
init_db()