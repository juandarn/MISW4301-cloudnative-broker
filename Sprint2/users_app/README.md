# Users App - Microservicio de Usuarios

## Descripción

El microservicio de usuarios es responsable de gestionar los usuarios del sistema, incluyendo registro, autenticación y gestión de perfiles. Permite crear usuarios, autenticarlos y gestionar sus sesiones mediante tokens UUID.

## Estructura del Proyecto

```
users_app/
├── app.py                     # Aplicación Flask principal
├── db.py                      # Configuración de SQLAlchemy
├── models/                    # Modelos de datos
│   └── user.py               # Modelo de usuario
├── resources/                 # Recursos de la API
│   └── user.py               # Endpoints REST
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
                └── test_users.py
```

## API Endpoints

### 1. Registro de Usuario
- **POST** `/users`
- **Descripción**: Crear un nuevo usuario
- **Body**:
  ```json
  {
    "username": "usuario123",
    "email": "usuario@example.com",
    "password": "password123"
  }
  ```

### 2. Autenticación de Usuario
- **POST** `/users/auth`
- **Descripción**: Autenticar usuario y generar token
- **Body**:
  ```json
  {
    "username": "usuario123",
    "password": "password123"
  }
  ```

### 3. Consulta de Usuario
- **GET** `/users/{user_id}`
- **Descripción**: Obtener información de un usuario específico

### 4. Actualización de Usuario
- **PUT** `/users/{user_id}`
- **Descripción**: Actualizar información de un usuario
- **Body**:
  ```json
  {
    "username": "nuevo_usuario",
    "email": "nuevo@example.com"
  }
  ```

### 5. Eliminación de Usuario
- **DELETE** `/users/{user_id}`
- **Descripción**: Eliminar un usuario específico

### 6. Conteo de Usuarios
- **GET** `/users/count`
- **Descripción**: Obtener el número total de usuarios

### 7. Health Check
- **GET** `/users/ping`
- **Descripción**: Verificar estado del servicio

### 8. Reset de Base de Datos
- **POST** `/users/reset`
- **Descripción**: Limpiar todos los datos de la base de datos

## Modelo de Datos

### User
```python
class UserModel(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    token = db.Column(db.String(), unique=True)
    expireAt = db.Column(db.DateTime(timezone=True))
    createdAt = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
```

## Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URI` | URI de conexión a PostgreSQL | `sqlite:///users.db` |
| `FLASK_ENV` | Entorno de ejecución | `development` |
| `POSTGRES_DB` | Nombre de la base de datos | `users_db` |
| `POSTGRES_USER` | Usuario de la base de datos | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña de la base de datos | `password` |

## Configuración

### Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URI="sqlite:///users.db"

# Ejecutar aplicación
python app.py
```

### Docker
```bash
# Construir imagen
docker build -t users-app:v1.0.0 .

# Ejecutar contenedor
docker run -p 5000:5000 users-app:v1.0.0
```

### Kubernetes
```bash
# Aplicar configuración
kubectl apply -f ../k8s/users_app.yaml

# Verificar despliegue
kubectl get pods -l app=users-app
```

## Pruebas

### Ejecutar Tests Unitarios
```bash
# Ejecutar todas las pruebas
python -m pytest test/ -v

# Ejecutar con cobertura
python -m pytest test/ -v --cov=.

# Ejecutar pruebas específicas
python -m pytest test/unit/domain/models/test_users.py -v
```

### Ejecutar Tests de API
```bash
# Usar Postman Collection
# Archivo: test/api/users.postman_collection.json
```

### Cobertura de Código
- **Cobertura mínima requerida**: 70%
- **Herramienta**: pytest-cov
- **Comando**: `python -m pytest test/ -v --cov=. --cov-report=html`

## Validaciones

### Username
- **Tipo**: String
- **Longitud**: Máximo 80 caracteres
- **Validación**: Debe ser único
- **Formato**: Alfanumérico y guiones bajos

### Email
- **Tipo**: String
- **Longitud**: Máximo 80 caracteres
- **Validación**: Debe ser único y formato válido
- **Formato**: RFC 5322

### Password
- **Tipo**: String
- **Longitud**: Máximo 80 caracteres
- **Validación**: No puede estar vacío

### Tokens
- **Formato**: UUID v4
- **Validación**: Generado automáticamente
- **Expiración**: 1 hora desde la autenticación

### Fechas
- **Formato**: ISO 8601 (UTC)
- **Ejemplo**: `2024-01-15T10:30:00Z`

## Base de Datos

### PostgreSQL (Producción)
- **Puerto**: 5432
- **Base de datos**: users_db
- **Usuario**: postgres
- **Contraseña**: password

### SQLite (Desarrollo)
- **Archivo**: users.db
- **Ubicación**: Raíz del proyecto

## Logs y Monitoreo

### Health Check
```bash
curl http://localhost:5000/users/ping
# Respuesta: "pong"
```

### Logs de Aplicación
```bash
# Ver logs en tiempo real
kubectl logs -f deployment/users-app-deployment

# Ver logs de base de datos
kubectl logs -f deployment/users-db-deployment
```

## Autenticación

### Sistema de Tokens
- **Tipo**: UUID generado aleatoriamente
- **Duración**: 1 hora
- **Almacenamiento**: Base de datos
- **Validación**: Verificación de existencia y expiración

### Flujo de Autenticación
1. Usuario envía credenciales (username/password)
2. Sistema valida credenciales
3. Sistema genera token UUID único
4. Sistema almacena token con fecha de expiración
5. Sistema retorna token al usuario

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   ```bash
   # Verificar variables de entorno
   kubectl describe pod <users-app-pod>
   
   # Verificar logs
   kubectl logs <users-app-pod>
   ```

2. **Error de validación de datos**
   - Verificar formato de email
   - Verificar unicidad de username/email
   - Verificar longitud de campos

3. **Error de autenticación**
   - Verificar credenciales
   - Verificar expiración de token
   - Verificar formato de UUID

4. **Error de puerto**
   ```bash
   # Verificar servicios
   kubectl get services
   
   # Verificar port forwarding
   kubectl port-forward service/users-app-service 8080:80
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

### Registrar Usuario
```bash
curl -X POST http://localhost:5000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario123",
    "email": "usuario@example.com",
    "password": "password123"
  }'
```

### Autenticar Usuario
```bash
curl -X POST http://localhost:5000/users/auth \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario123",
    "password": "password123"
  }'
```

### Obtener Usuario
```bash
curl http://localhost:5000/users/{user-id}
```

## Seguridad

### Contraseñas
- **Almacenamiento**: En texto plano (requerimiento del proyecto)
- **Validación**: Longitud mínima y formato
- **Recomendación**: En producción usar hash bcrypt

### Tokens
- **Generación**: UUID aleatorio
- **Expiración**: 1 hora automática
- **Validación**: Verificación de existencia y tiempo

### Validaciones
- **Email**: Formato RFC 5322
- **Username**: Alfanumérico y guiones bajos
- **Unicidad**: Username y email únicos

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
