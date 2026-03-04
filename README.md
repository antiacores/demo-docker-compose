# Demo Docker Compose — Sistemas Distribuidos

Aplicación de ejemplo que demuestra el uso de Docker Compose para orquestar múltiples servicios: una API en Flask, una base de datos PostgreSQL y una caché con Redis.

## Servicios

api - Flask (Python 3.11) - port 8000
db - PostgreSQL 14 - port 5432
redis - Redis 7 - port 6379

## Requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Cómo ejecutar

```bash
docker compose up --build
```
La API estará disponible en `http://localhost:8000`.

Para detener los servicios:
```bash
docker compose down
```

## Endpoints

### 'GET /'
Muestra los servicios disponibles y cuenta la visita (es la página de inicio)
```bash
curl http://localhost:8000/
```

### 'GET /health'
Verifica que la API esté conectada correctamente a PostgreSQL y Redis.
```bash
curl http://localhost:8000/health
```

### 'GET /visits'
Muestra el número total de visitas registradas en Redis.
```bash
curl http://localhost:8000/visits
```

### 'POST /users'
Crea un nuevo usuario en la base de datos.
```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan", "email": "juan@mail.com"}'
```

### 'GET /users'
Muestra la lista de todos los usuarios registrados en la base de datos.
```bash
curl http://localhost:8000/users
```

## Estructura del proyecto

demo_docker_compose/
├── app/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── docker-compose.yml
└── README.md

## Notas

- La tabla 'users' se crea automáticamente en PostgreSQL al iniciar la aplicación.
- Redis lleva un contador global de visitas que se incrementa en cada llamada a '/', '/users' (GET y POST).
- Los datos de PostgreSQL y Redis se persisten en volúmenes de Docker.