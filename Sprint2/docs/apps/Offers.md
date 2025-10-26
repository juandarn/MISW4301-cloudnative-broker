# Offers App - Microservicio de Ofertas

## Descripción

El microservicio de ofertas es responsable de gestionar las ofertas que los usuarios hacen para transportar objetos en rutas específicas. Permite crear, consultar, filtrar y eliminar ofertas de transporte.

## Estructura del Proyecto

```
offers_app/
├── app.py                     # Aplicación Flask principal
├── db.py                      # Configuración de SQLAlchemy
├── models/                    # Modelos de datos
│   └── offer.py              # Modelo de oferta
├── resources/                 # Recursos de la API
│   └── offer.py              # Endpoints REST
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
                └── test_offer.py
```

## API Endpoints

### 1. Creación de Oferta
- **POST** `/offers`
- **Descripción**: Crear una nueva oferta de transporte
- **Body**:
  ```json
  {
    "routeId": "uuid-string",
    "userId": "uuid-string",
    "description": "Descripción del objeto",
    "size": "S|M|L|XL",
    "fragile": true,
    "offer": 50.0
  }
  ```

### 2. Consulta de Ofertas
- **GET** `/offers`
- **Descripción**: Obtener y filtrar ofertas
- **Query Parameters**:
  - `route`: Filtrar por ruta (UUID)
  - `owner`: Filtrar por propietario (UUID)

### 3. Consulta de Oferta Específica
- **GET** `/offers/{offer_id}`
- **Descripción**: Obtener una oferta específica por ID

### 4. Eliminación de Oferta
- **DELETE** `/offers/{offer_id}`
- **Descripción**: Eliminar una oferta específica

### 5. Conteo de Ofertas
- **GET** `/offers/count`
- **Descripción**: Obtener el número total de ofertas

### 6. Health Check
- **GET** `/offers/ping`
- **Descripción**: Verificar estado del servicio

### 7. Reset de Base de Datos
- **POST** `/offers/reset`
- **Descripción**: Limpiar todos los datos de la base de datos

## Modelo de Datos

### Offer
```python
class OfferModel(db.Model):
    __tablename__ = "offers"
    
    id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
    routeId = db.Column(db.String(), nullable=False)
    userId = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    size = db.Column(db.String(), nullable=False)
    fragile = db.Column(db.Boolean(), nullable=False)
    offer = db.Column(db.Float(), nullable=False)
    createdAt = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)
```

## Variables de Entorno

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `DATABASE_URI` | URI de conexión a PostgreSQL | `sqlite:///offers.db` |
| `FLASK_ENV` | Entorno de ejecución | `development` |
| `POSTGRES_DB` | Nombre de la base de datos | `offers_db` |
| `POSTGRES_USER` | Usuario de la base de datos | `postgres` |
| `POSTGRES_PASSWORD` | Contraseña de la base de datos | `password` |

## Configuración

### Desarrollo Local
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export DATABASE_URI="sqlite:///offers.db"

# Ejecutar aplicación
python app.py
```

### Docker
```bash
# Construir imagen
docker build -t offers-app:v1.0.0 .

# Ejecutar contenedor
docker run -p 5000:5000 offers-app:v1.0.0
```

### Kubernetes
```bash
# Aplicar configuración
kubectl apply -f ../k8s/offers_app.yaml

# Verificar despliegue
kubectl get pods -l app=offers-app
```

## Pruebas

### Ejecutar Tests Unitarios
```bash
# Ejecutar todas las pruebas
python -m pytest test/ -v

# Ejecutar con cobertura
python -m pytest test/ -v --cov=.

# Ejecutar pruebas específicas
python -m pytest test/unit/domain/models/test_offer.py -v
```

### Ejecutar Tests de API
```bash
# Usar Postman Collection
# Archivo: test/api/offers.postman_collection.json
```

### Cobertura de Código
- **Cobertura mínima requerida**: 70%
- **Herramienta**: pytest-cov
- **Comando**: `python -m pytest test/ -v --cov=. --cov-report=html`

## Validaciones

### Tamaños de Objeto
- **Valores permitidos**: S, M, L, XL
- **Validación**: Enum en el esquema Marshmallow

### Precios
- **Tipo**: Float
- **Validación**: Debe ser un número positivo

### UUIDs
- **Formato**: UUID v4
- **Validación**: Formato UUID estándar

### Fechas
- **Formato**: ISO 8601 (UTC)
- **Ejemplo**: `2024-01-15T10:30:00Z`

## Base de Datos

### PostgreSQL (Producción)
- **Puerto**: 5432
- **Base de datos**: offers_db
- **Usuario**: postgres
- **Contraseña**: password

### SQLite (Desarrollo)
- **Archivo**: offers.db
- **Ubicación**: Raíz del proyecto

## Logs y Monitoreo

### Health Check
```bash
curl http://localhost:5000/offers/ping
# Respuesta: "pong"
```

### Logs de Aplicación
```bash
# Ver logs en tiempo real
kubectl logs -f deployment/offers-app-deployment

# Ver logs de base de datos
kubectl logs -f deployment/offers-db-deployment
```

## Troubleshooting

### Problemas Comunes

1. **Error de conexión a base de datos**
   ```bash
   # Verificar variables de entorno
   kubectl describe pod <offers-app-pod>
   
   # Verificar logs
   kubectl logs <offers-app-pod>
   ```

2. **Error de validación de datos**
   - Verificar formato de UUIDs
   - Verificar valores de tamaño (S, M, L, XL)
   - Verificar que el precio sea positivo

3. **Error de puerto**
   ```bash
   # Verificar servicios
   kubectl get services
   
   # Verificar port forwarding
   kubectl port-forward service/offers-app-service 8083:80
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
