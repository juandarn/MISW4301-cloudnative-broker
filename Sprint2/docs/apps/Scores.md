# Scores App - Microservicio de Puntajes

## Descripción

El microservicio de puntajes (scores) es responsable de almacenar y exponer el puntaje (utilidad) calculado para una oferta específica. Permite registrar un nuevo puntaje y consultar el puntaje existente asociado a una oferta. Está diseñado para integrarse con otros servicios productores de ofertas y procesos que calculan la utilidad.

## Estructura del Proyecto

```any
scores_app/
├── app.py                     # Aplicación Flask principal (factory create_app)
├── db.py                      # Configuración de SQLAlchemy
├── models/                    # Modelos de datos
│   └── score.py               # Modelo ScoreModel
├── resources/                 # Recursos/Endpoints de la API
│   └── score.py               # Endpoints REST (Blueprint)
├── schemas.py                 # Esquemas de validación Marshmallow
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Imagen Docker
├── pytest.ini                 # Configuración de pruebas (si aplica)
├── README.md                  # Este documento
└── test/                      # Pruebas (pendiente / por implementar)
```

## API Endpoints

Todos los endpoints están bajo el prefijo `/score` al registrar el Blueprint.

### 1. Consultar Puntaje por Oferta

- **GET** `/score/{oferta_id}`
- **Descripción**: Retorna el puntaje (utilidad) asociado a una oferta. Si no existe un registro devuelve utilidad `null`.
- **Respuesta (200)**:

```json
{
  "oferta_id": "uuid-oferta",
  "utilidad": 0.85
}
```

Cuando no existe:

```json
{
  "oferta_id": "uuid-oferta",
  "utilidad": null
}
```

### 2. Crear/Registrar Puntaje

- **POST** `/score/`
- **Descripción**: Crea un nuevo registro de puntaje para una oferta.
- **Body**:

```json
{
  "oferta_id": "uuid-oferta",
  "utilidad": 0.92
}
```

- **Respuesta (200)**: Objeto creado con sus campos.

### 3. Health Check

- **GET** `/score/ping`
- **Descripción**: Verificar estado del servicio.
- **Respuesta (200)**:

```json
{ "message": "Pong" }
```

### 4. Reset de Base de Datos

- **POST** `/score/reset`
- **Descripción**: Elimina todas las tablas y las recrea (solo para entornos de desarrollo / pruebas).
- **Respuesta (200)**:

```json
{ "msg": "Todos los datos fueron eliminados" }
```

## Modelo de Datos

### Score

```python
class ScoreModel(db.Model):
	__tablename__ = "scores"

	id = db.Column(db.String(), primary_key=True, default=lambda: str(uuid.uuid4()))
	oferta_id = db.Column(db.String(), nullable=False)
	utilidad = db.Column(db.Float(), nullable=False)
	timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
```

## Esquemas (Marshmallow)

```python
class ScoreSchema(Schema):
	id = fields.Str(dump_only=True)
	oferta_id = fields.Str(required=True)
	utilidad = fields.Float(required=True)

class ScoreResponseSchema(Schema):
	oferta_id = fields.Str(required=True)
	utilidad = fields.Float(allow_none=True)
```

## Variables de Entorno

| Variable       | Descripción                                              | Valor por Defecto     |
| -------------- | -------------------------------------------------------- | --------------------- |
| `DATABASE_URI` | URI de conexión a la base de datos (PostgreSQL / SQLite) | `sqlite:///scores.db` |
| `FLASK_ENV`    | Entorno de ejecución                                     | `development`         |

> Ajusta `DATABASE_URI` para producción (por ejemplo un Postgres en Kubernetes).

## Configuración

### Desarrollo Local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Exportar variable (Linux/Mac) o set (Windows PowerShell: $Env:VARIABLE="valor")
export DATABASE_URI="sqlite:///scores.db"

# Ejecutar aplicación
python app.py
```

### Docker

```bash
# Construir imagen
docker build -t scores-app:v1.0.0 .

# Ejecutar contenedor
docker run -p 5000:5000 -e DATABASE_URI=sqlite:///scores.db scores-app:v1.0.0
```

### Kubernetes (Ejemplo genérico)

```bash
# Aplicar manifiestos (adaptar a nombre real si existe)
kubectl apply -f ../k8s/scores_app.yaml

# Verificar despliegue
kubectl get pods -l app=scores-app
```

## Pruebas

Actualmente no hay carpeta de pruebas implementada en `scores_app/test/`. Se recomienda:

1. Crear pruebas unitarias para el modelo (`ScoreModel`).
2. Crear pruebas de API para endpoints (GET/POST/ping/reset).
3. Incluir cobertura mínima del 70% usando `pytest-cov`.

### Ejemplo de Comandos

```bash
python -m pytest test/ -v
python -m pytest test/ -v --cov=. --cov-report=html
```

## Validaciones

| Campo       | Tipo     | Reglas                                                                    |
| ----------- | -------- | ------------------------------------------------------------------------- |
| `oferta_id` | String   | Requerido. Formato UUID (no se valida explícitamente pero se recomienda). |
| `utilidad`  | Float    | Requerido. Debe ser numérico.                                             |
| `timestamp` | DateTime | Se genera automáticamente al crear el registro.                           |

## Base de Datos

### Producción (Ejemplo PostgreSQL)

- Puerto: 5432
- Base de datos: `scores_db`
- Usuario: `scores_user`
- Contraseña: `scores_pass`

### Desarrollo (SQLite)

- Archivo: `scores.db`
- Ubicación: Raíz del proyecto (definido por `DATABASE_URI`)

## Logs y Monitoreo

### Health Check

```bash
curl http://localhost:5000/score/ping
# Respuesta: {"message": "Pong"}
```

### Logs de Aplicación (Kubernetes)

```bash
kubectl logs -f deployment/scores-app-deployment
```

## Troubleshooting

1. Error de conexión a base de datos

```bash
kubectl describe pod <scores-app-pod>
kubectl logs <scores-app-pod>
```

1. Error 500 al crear puntaje

   - Verificar que `utilidad` sea float
   - Validar que `oferta_id` no sea vacío

1. Respuesta con `utilidad: null`

   - No existe un registro para esa `oferta_id`

1. Reinicio accidental de datos
   - Evitar usar `/score/reset` en producción

## Dependencias (Principales)

- Flask
- Flask-Smorest
- SQLAlchemy
- Marshmallow
- python-dotenv

## Ejemplos de Uso

### Registrar un Puntaje

```bash
curl -X POST http://localhost:5000/score/ \
	-H "Content-Type: application/json" \
	-d '{
		"oferta_id": "550e8400-e29b-41d4-a716-446655440000",
		"utilidad": 0.87
	}'
```

### Consultar Puntaje

```bash
curl http://localhost:5000/score/550e8400-e29b-41d4-a716-446655440000
```

### Health Check (Ejemplo)

```bash
curl http://localhost:5000/score/ping
```

## Documentación API

Disponible automáticamente vía OpenAPI/Swagger:

- Swagger UI: `http://localhost:5000/swagger-ui`
- OpenAPI JSON: `http://localhost:5000/openapi.json`
