import os
from time import sleep
from flask import Flask, jsonify, request
import psycopg2
import redis

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")

def wait_for_db(max_retries=20):
    for _ in range(max_retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            return True
        except Exception:
            sleep(1)
    raise RuntimeError("DB no responde, está muerta :(")

# Crear la tabla de usuarios si no existe
def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# Contador de visitas usando Redis (para no repetir código en cada ruta)
def count_visit():
    r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
    return r.incr("visits")

@app.get("/")
def home():
    visits = count_visit() # Ahora cuenta la visita igual
    return jsonify({
        "message": "¡Hola desde Flask en Docker Compose!",
        "visits": visits,
        "services": {
            "/health": "Verifica la salud de la aplicación",
            "/visits": "Cuenta las visitas usando Redis",
            "/users": "GET para listar usuarios, POST para crear uno"
        }
    })

@app.get("/health")
def health():
    try:
        # Verificar conexión a la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT NOW();")
        now = cur.fetchone()[0]
        cur.close()
        conn.close()
        # Verificar conexión a Redis
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
        pong = r.ping()
        return jsonify({
            "status": "ok",
            "db_time": str(now),
            "redis_ping": pong
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    
@app.get("/visits")
def visits():
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)
        count = r.incr("visits")
        return jsonify({
            "visits": int(count)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.post("/users")
def create_user():
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        if not name or not email:
            return jsonify({
                "status": "error", 
                "message": "Se requieren nombre y correo"
            }), 400
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id;",
            (name, email)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        visits = count_visit()
        return jsonify({
            "status": "ok",
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            },
            "visits": visits
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.get("/users")
def get_users():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, name, email FROM users;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        users = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
        visits = count_visit()
        return jsonify({
            "status": "ok",
            "users": users,
            "visits": visits
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    wait_for_db()
    init_db()
    app.run(host="0.0.0.0", port=8000)