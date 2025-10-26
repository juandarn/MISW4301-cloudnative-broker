# Posts App - Microservicio de Publicaciones

## Descripción

El microservicio de publicaciones es responsable de gestionar las publicaciones que los usuarios crean para anunciar necesidades de transporte en rutas específicas. Permite crear, consultar, filtrar y eliminar publicaciones con fechas de expiración.

## Estructura del Proyecto

```
posts_app/
├── app.py                     # Aplicación Flask principal
├── db.py                      # Configuración de SQLAlchemy
├── models/                    # Modelos de datos
│   └── post.py               # Modelo de publicación
├── resources/                 # Recursos de la API
│   └── post.py               # Endpoints REST
├── schemas.py                 # Esquemas de validación Marshmallow
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Imagen Docker
├── pytest.ini                # Configuración de pruebas
├── README.md                 # Este archivo
└── test/                     # Pruebas
    ├── api/                  # Pruebas de API
    └── unit/                 # Pruebas unitarias
        └── domain/
            └── models/
                └── test_posts.py
```

## API Endpoints

### 1. Creación de Publicación
- **POST** `/posts`
- **Descripción**: Crear una nueva publicación
- **Body**:
  ```json
  {
    "routeId": "uuid-string",
    "userId": "uuid-string",
    "expireAt": "2024-02-01T18:00:00Z"
  }
  ```

### 2. Consulta de Publicaciones
- **GET** `/posts`
- **Descripción**: Obtener y filtrar publicaciones
- **Query Parameters**:
  - `expire`: Filtrar por estado de expiración (true/false)
  - `route`: Filtrar por ruta (UUID)
  - `owner`: Filtrar por propietario (UUID)

### 3. Consulta de Publicación Específica
- **GET** `/posts/{post_id}`
- **Descripción**: Obtener una publicación específica por ID

### 4. Eliminación de Publicación
- **DELETE** `/posts/{post_id}`
- **Descripción**: Eliminar una publicación específica

### 5. Conteo de Publicaciones
- **GET** `/posts/count`
- **Descripción**: Obtener el número total de publicaciones

### 6. Health Check
- **GET** `/posts/ping`
- **Descripción**: Verificar estado del servicio

### 7. Reset de Base de Datos
- **POST** `/posts/reset`
- **Descripción**: Limpiar todos los datos de la base de datos

## Modelo de Datos

### Post
```python
class PostModel(db.Model):
    __tablename__ = "posts"
    
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    routeId = db.Column(db.String(), nullable=False)
    userId = db.Column(db.String(), nullable=False)
    expireAt = db.Column(db.DateTime(timezone=True), nullable=False)
    createdAt = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
```

## Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URI` | URI de conexión a PostgreSQL | `sqlite:///posts.db` |
| `FLASK_ENV` | Entorno de ejecución | `development` |
| `POSTGRES_DB` | Nombre de la base de datos | `posts_db` |
| `POSTGRES_USER` | Usuario de la base de datos | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña de la base de datos | `password` |

## Configuración

### Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URI="sqlite:///posts.db"

# Ejecutar aplicación
python app.py
```

### Docker
```bash
# Construir imagen
docker build -t posts-app:v1.0.0 .

# Ejecutar contenedor
docker run -p 5000:5000 posts-app:v1.0.0
```

### Kubernetes
```bash
# Aplicar configuración
kubectl apply -f ../k8s/posts_app.yaml

# Verificar despliegue
kubectl get pods -l app=posts-app
```

## Pruebas

### Ejecutar Tests Unitarios
```bash
# Ejecutar todas las pruebas
python -m pytest test/ -v

# Ejecutar con cobertura
python -m pytest test/ -v --cov=.

# Ejecutar pruebas específicas
python -m pytest test/unit/domain/models/test_posts.py -v
```

### Ejecutar Tests de API
```bash
# Usar Postman Collection
# Archivo: test/api/posts.postman_collection.json
```

### Cobertura de Código
- **Cobertura mínima requerida**: 70%
- **Herramienta**: pytest-cov
- **Comando**: `python -m pytest test/ -v --cov=. --cov-report=html`

## Validaciones

### Fechas de Expiración
- **Formato**: ISO 8601 (UTC)
- **Validación**: Debe ser una fecha futura
- **Ejemplo**: `2024-02-01T18:00:00Z`

### UUIDs
- **Formato**: UUID v4
- **Validación**: Formato UUID estándar
- **Campos**: routeId, userId, id

### Filtros de Consulta
- **expire**: Boolean (true/false)
- **route**: UUID válido
- **owner**: UUID válido

## Base de Datos

### PostgreSQL (Producción)
- **Puerto**: 5432
- **Base de datos**: posts_db
- **Usuario**: postgres
- **Contraseña**: password

### SQLite (Desarrollo)
- **Archivo**: posts.db
- **Ubicación**: Raíz del proyecto

## Logs y Monitoreo

### Health Check
```bash
curl http://localhost:5000/posts/ping
# Respuesta: "pong"
```

### Logs de Aplicación
```bash
# Ver logs en tiempo real
kubectl logs -f deployment/posts-app-deployment

# Ver logs de base de datos
kubectl logs -f deployment/posts-db-deployment
```

## Gestión de Expiración

### Lógica de Expiración
- **Validación**: Las fechas de expiración deben ser futuras
- **Filtrado**: Permite filtrar por publicaciones expiradas/no expiradas
- **Automatización**: Las publicaciones expiradas se pueden identificar por fecha

### Filtros Disponibles
- **expire=true**: Solo publicaciones expiradas
- **expire=false**: Solo publicaciones no expiradas
- **Sin filtro**: Todas las publicaciones

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   ```bash
   # Verificar variables de entorno
   kubectl describe pod <posts-app-pod>
   
   # Verificar logs
   kubectl logs <posts-app-pod>
   ```

2. **Error de validación de fechas**
   - Verificar que expireAt sea una fecha futura
   - Verificar formato ISO 8601
   - Verificar zona horaria UTC

3. **Error de validación de UUIDs**
   - Verificar formato de UUIDs
   - Verificar que routeId y userId sean UUIDs válidos

4. **Error de puerto**
   ```bash
   # Verificar servicios
   kubectl get services
   
   # Verificar port forwarding
   kubectl port-forward service/posts-app-service 8081:80
   ```

## Dependencias

### Principales
- Flask 2.3.3
- Flask-Smorest 0.42.0
- SQLAlchemy 3.0.5
- Marshmallow 3.20.1
- psycopg2-binary 2.9.7

### Testing
- pytest 7.4.2
- pytest-cov 4.1.0

### Desarrollo
- python-dotenv 1.0.0

## Ejemplos de Uso

### Crear una Publicación
```bash
curl -X POST http://localhost:5000/posts \
  -H "Content-Type: application/json" \
  -d '{
    "routeId": "550e8400-e29b-41d4-a716-446655440000",
    "userId": "550e8400-e29b-41d4-a716-446655440001",
    "expireAt": "2024-02-01T18:00:00Z"
  }'
```

### Consultar Publicaciones
```bash
# Todas las publicaciones
curl http://localhost:5000/posts

# Solo publicaciones no expiradas
curl "http://localhost:5000/posts?expire=false"

# Filtrar por ruta
curl "http://localhost:5000/posts?route=550e8400-e29b-41d4-a716-446655440000"
```

### Obtener Publicación Específica
```bash
curl http://localhost:5000/posts/{post-id}
```

## Contribución

1. Crear una rama para tu feature
2. Implementar cambios
3. Agregar pruebas
4. Verificar cobertura mínima (70%)
5. Crear Pull Request

## Documentación API

La documentación automática de la API está disponible en:
- **Swagger UI**: `http://localhost:5000/swagger-ui`
- **OpenAPI JSON**: `http://localhost:5000/openapi.json`
