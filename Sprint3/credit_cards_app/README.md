# Credit Cards App - Microservicio de Tarjetas de Crédito (RF-006)

## Descripción

El microservicio de tarjetas de crédito es responsable de gestionar el registro y verificación asíncrona de tarjetas de crédito mediante integración con TrueNative. Permite a usuarios verificados registrar tarjetas, verificarlas de forma asíncrona y recibir notificaciones por email del resultado.

## Estructura del Proyecto

```text
credit_cards_app/
├── app.py                     # Aplicación Flask principal  
├── db.py                      # Configuración de SQLAlchemy
├── cards_poller.py           # Servicio de polling y colas
├── models/                    # Modelos de datos
│   └── credit_card.py        # Modelo de tarjeta de crédito
├── resources/                 # Recursos de la API
│   └── credit_cards.py       # Endpoints REST
├── schemas.py                 # Esquemas de validación Marshmallow
├── services/                  # Servicios externos
│   ├── truenative_cards_client.py  # Cliente TrueNative
│   ├── cards_queue_publisher.py    # Publisher de colas
│   ├── cards_queue_consumer.py     # Consumer de colas
│   ├── email_service.py       # Servicio de emails
│   └── notifications.py      # Servicio de notificaciones
├── utils/                     # Utilidades
├── requirements.txt           # Dependencias Python
├── Dockerfile                # Imagen Docker
├── pytest.ini               # Configuración de pruebas
├── README.md                 # Este archivo
└── test/                     # Pruebas
    ├── api/                  # Pruebas de API
    └── unit/                 # Pruebas unitarias
```

## API Endpoints

### 1. Registro de Tarjeta de Crédito

- **POST** `/credit-cards`
- **Descripción**: Registrar una nueva tarjeta de crédito
- **Headers**: `Authorization: Bearer <token>`
- **Body**:

  ```json
  {
    "cardNumber": "1234567890123456",
    "cvv": "123",
    "expirationDate": "25/12",
    "cardHolderName": "Juan Perez"
  }
  ```

- **Respuesta 201**:

  ```json
  {
    "id": "uuid",
    "userId": "uuid", 
    "createdAt": "2025-01-01T00:00:00Z"
  }
  ```

### 2. Consultar Tarjetas del Usuario

- **GET** `/credit-cards`
- **Descripción**: Obtener tarjetas del usuario autenticado
- **Headers**: `Authorization: Bearer <token>`
- **Respuesta 200**:

  ```json
  [
    {
      "id": "uuid",
      "token": "token_truenative",
      "userId": "uuid",
      "lastFourDigits": "3456", 
      "issuer": "VISA",
      "status": "APROBADA",
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:05:00Z"
    }
  ]
  ```

### 3. Health Check

- **GET** `/credit-cards/ping`
- **Descripción**: Verificar estado del servicio
- **Respuesta 200**: `pong`

### 4. Contador de Entidades

- **GET** `/credit-cards/count`
- **Descripción**: Obtener número de tarjetas en sistema
- **Respuesta 200**:

  ```json
  {
    "count": 42
  }
  ```

### 5. Reset (Testing)

- **POST** `/credit-cards/reset`
- **Descripción**: Eliminar todas las tarjetas (solo testing)
- **Respuesta 200**:

  ```json
  {
    "msg": "Todos los datos fueron eliminados"
  }
  ```

## Integración con TrueNative

### Registro de Tarjeta

1. Usuario envía datos de tarjeta a `/credit-cards`
2. Sistema valida y crea registro con estado `POR_VERIFICAR`  
3. Se envía solicitud a TrueNative `/native/cards`
4. TrueNative responde con RUV y token
5. Sistema actualiza registro con RUV y token

### Verificación Asíncrona

1. **Polling**: Servicio consulta cada 30s el estado en TrueNative
2. **Colas**: Mensajes de verificación procesados por consumer
3. **Update**: Estado actualizado a `APROBADA` o `RECHAZADA`
4. **Notificación**: Email enviado al usuario con resultado

## Variables de Entorno

```bash
# Base de Datos
DATABASE_URI=postgresql://user:pass@host:5432/credit_cards_db

# TrueNative
TRUENATIVE_BASE_URL=http://service-truenative
SECRET_TOKEN=supersecreto123

# Email
GMAIL_USER=your-email@gmail.com  
GMAIL_PASS=your-app-password

# Configuración
POLLING_INTERVAL=30  # segundos
```

## Estados de Tarjeta

| Estado | Descripción | Acciones |
|--------|-------------|----------|
| **POR_VERIFICAR** | Tarjeta registrada, esperando TrueNative | Polling activo |
| **APROBADA** | Verificación exitosa | Lista en consultas |
| **RECHAZADA** | Verificación fallida | Informativo, no usable |

## Arquitectura

### Componentes

- **API REST**: Endpoints de registro y consulta
- **Poller Service**: Verificación asíncrona via polling  
- **Queue System**: Procesamiento distribuido de verificaciones
- **Email Service**: Notificaciones de resultado
- **TrueNative Client**: Integración con servicio externo

### Patrones Utilizados

- **Polling Pattern**: Verificación periódica de estados
- **Circuit Breaker**: Protección ante fallos de TrueNative
- **Async Processing**: Verificación no bloquea respuesta
- **Event-Driven**: Notificaciones disparadas por cambios de estado

## Desarrollo

### Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Ejecutar aplicación
python app.py
```

### Testing

```bash  
# Ejecutar pruebas
pytest test/ -v --cov=.

# Cobertura específica
pytest --cov=resources --cov=models --cov=services
```

### Docker

```bash
# Construir imagen
docker build -t credit-cards-app:latest .

# Ejecutar contenedor
docker run -p 5000:5000 --env-file .env credit-cards-app:latest
```
