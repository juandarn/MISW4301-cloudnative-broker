# Routes App - Microservicio de Rutas

## Descripción

El microservicio de rutas es responsable de gestionar las rutas de viaje que conectan diferentes ciudades. Permite crear, consultar, filtrar y eliminar rutas de transporte.

## Estructura del Proyecto

```any
routes_app/
├── app.py                     # Aplicación Flask principal
├── db.py                      # Configuración de SQLAlchemy
├── models/                    # Modelos de datos
│   └── route.py              # Modelo de ruta
├── resources/                 # Recursos de la API
│   └── route.py              # Endpoints REST
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
                └── test_route.py
```

## API Endpoints

### 1. Creación de Ruta

- **POST** `/routes`
- **Descripción**: Crear una nueva ruta de viaje
- **Body**:

  ```json
  {
    "origin": "Bogotá",
    "destination": "Medellín",
    "bagCost": 25.0,
    "plannedStartDate": "2024-02-01T08:00:00Z",
    "plannedEndDate": "2024-02-01T18:00:00Z"
  }
  ```

### 2. Consulta de Rutas

- **GET** `/routes`
- **Descripción**: Obtener y filtrar rutas
- **Query Parameters**:
  - `origin`: Filtrar por ciudad de origen
  - `destination`: Filtrar por ciudad de destino
  - `since`: Filtrar por fecha de inicio (desde)
  - `until`: Filtrar por fecha de inicio (hasta)

### 3. Consulta de Ruta Específica

- **GET** `/routes/{route_id}`
- **Descripción**: Obtener una ruta específica por ID

### 4. Eliminación de Ruta

- **DELETE** `/routes/{route_id}`
- **Descripción**: Eliminar una ruta específica

### 5. Conteo de Rutas

- **GET** `/routes/count`
- **Descripción**: Obtener el número total de rutas

### 6. Health Check

- **GET** `/routes/ping`
- **Descripción**: Verificar estado del servicio

### 7. Reset de Base de Datos

- **POST** `/routes/reset`
- **Descripción**: Limpiar todos los datos de la base de datos

## Modelo de Datos

### Route

```python
class RouteModel(db.Model):
    __tablename__ = "routes"

    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    origin = db.Column(db.String(), nullable=False)
    destination = db.Column(db.String(), nullable=False)
    bagCost = db.Column(db.Float(), nullable=False)
    plannedStartDate = db.Column(db.DateTime(timezone=True), nullable=False)
    plannedEndDate = db.Column(db.DateTime(timezone=True), nullable=False)
    createdAt = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
```

## Variables de Entorno

| Variable            | Descripción                    | Valor por Defecto                                               |
| ------------------- | ------------------------------ | --------------------------------------------------------------- |
| `DATABASE_URI`      | URI de conexión a PostgreSQL   | `postgresql://routes_user:routes_pass@routes-db:5432/routes_db` |
| `FLASK_ENV`         | Entorno de ejecución           | `development`                                                   |
| `POSTGRES_DB`       | Nombre de la base de datos     | `routes_db`                                                     |
| `POSTGRES_USER`     | Usuario de la base de datos    | `routes_user`                                                   |
| `POSTGRES_PASSWORD` | Contraseña de la base de datos | `routes_pass`                                                   |

## Configuración

### Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URI="postgresql://routes_user:routes_pass@routes-db:5432/routes_db"

# Ejecutar aplicación
python app.py
```

### Docker

```bash
# Construir imagen
docker build -t routes-app:v1.0.0 .

# Ejecutar contenedor
docker run -p 5000:5000 routes-app:v1.0.0
```

### Kubernetes

```bash
# Aplicar configuración
kubectl apply -f ../k8s/routes_app.yaml

# Verificar despliegue
kubectl get pods -l app=routes-app
```

## Pruebas

### Ejecutar Tests Unitarios

```bash
# Ejecutar todas las pruebas
python -m pytest test/ -v

# Ejecutar con cobertura
python -m pytest test/ -v --cov=.

# Ejecutar pruebas específicas
python -m pytest test/unit/domain/models/test_route.py -v
```

### Ejecutar Tests de API

```bash
# Usar Postman Collection
# Archivo: test/api/routes.postman_collection.json
```

### Cobertura de Código

- **Cobertura mínima requerida**: 70%
- **Herramienta**: pytest-cov
- **Comando**: `python -m pytest test/ -v --cov=. --cov-report=html`

## Validaciones

### Ciudades

- **Tipo**: String
- **Validación**: No puede estar vacío
- **Ejemplos**: "Bogotá", "Medellín", "Cali"

### Costos

- **Tipo**: Float
- **Validación**: Debe ser un número positivo

### Fechas

- **Formato**: ISO 8601 (UTC)
- **Validación**: plannedEndDate debe ser posterior a plannedStartDate
- **Ejemplo**: `2024-02-01T08:00:00Z`

### UUIDs

- **Formato**: UUID v4
- **Validación**: Formato UUID estándar

## Base de Datos

### PostgreSQL (Producción)

- **Puerto**: 5432
- **Base de datos**: routes_db
- **Usuario**: postgres
- **Contraseña**: password

### SQLite (Desarrollo)

- **Archivo**: routes.db
- **Ubicación**: Raíz del proyecto

## Logs y Monitoreo

### Health Check

```bash
curl http://localhost:5000/routes/ping
# Respuesta: "pong"
```

### Logs de Aplicación

```bash
# Ver logs en tiempo real
kubectl logs -f deployment/routes-app-deployment

# Ver logs de base de datos
kubectl logs -f deployment/routes-db-deployment
```

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**

   ```bash
   # Verificar variables de entorno
   kubectl describe pod <routes-app-pod>

   # Verificar logs
   kubectl logs <routes-app-pod>
   ```

2. **Error de validación de fechas**

   - Verificar que plannedEndDate sea posterior a plannedStartDate
   - Verificar formato ISO 8601
   - Verificar zona horaria UTC

3. **Error de validación de costos**

   - Verificar que bagCost sea un número positivo
   - Verificar tipo de dato Float

4. **Error de puerto**

   ```bash
   # Verificar servicios
   kubectl get services

   # Verificar port forwarding
   kubectl port-forward service/routes-app-service 8084:80
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

### Crear una Ruta

```bash
curl -X POST http://localhost:5000/routes \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "Bogotá",
    "destination": "Medellín",
    "bagCost": 25.0,
    "plannedStartDate": "2024-02-01T08:00:00Z",
    "plannedEndDate": "2024-02-01T18:00:00Z"
  }'
```

### Consultar Rutas

```bash
# Todas las rutas
curl http://localhost:5000/routes

# Filtrar por origen
curl "http://localhost:5000/routes?origin=Bogotá"

# Filtrar por fecha
curl "http://localhost:5000/routes?since=2024-02-01T00:00:00Z"
```

### Obtener Ruta Específica

```bash
curl http://localhost:5000/routes/{route-id}
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
