# Vista Funcional

## Descripción General

Esta vista presenta los componentes que conforman la solución completa del sistema de microservicios:

**Entrega 1**: Cuatro microservicios de dominio base (Usuarios, Publicaciones, Ofertas y Rutas) con funcionalidad CRUD.

**Entrega 2**: Incorporación de componentes de orquestación:

- **Aggregator**: Orquestador que expone endpoints compuestos para RF-003, RF-004 y RF-005 reduciendo llamadas del cliente a una sola petición por requerimiento.
- **Scores**: Servicio de persistencia de la utilidad (score) asociada a cada oferta, integrado en modo best‑effort.

**Entrega 3**: Integración con servicios externos y verificación asíncrona:

- **Credit Cards Service**: Almacenamiento y verificación asíncrona de tarjetas de crédito (RF-006)
- **User Verification**: Verificación de identidad de usuarios vía webhooks (RF-007)
- **TrueNative Integration**: Servicio externo para verificaciones de identidad y tarjetas

El sistema evoluciona desde servicios independientes hacia una arquitectura híbrida que centraliza validaciones transversales, optimiza la experiencia de cliente y mejora resiliencia ante fallos parciales.

## Componentes del Sistema

### Aggregator Service (Orquestador)

Expone endpoints compuestos y coordina servicios internos. Centraliza validaciones de autenticación, ownership, expiraciones y unicidad; ensambla respuestas coherentes y degradables.

**Componentes principales:**

- **Aggregator API**: Endpoints compuestos `/rf003/posts`, `/rf004/posts/{id}/offers`, `/rf005/posts/{id}`
- **Workflows RF003/RF005**: Orquestación síncrona de secuencias (creación de ruta condicional, verificación de publicación, ensamble de datos)
- **Workflow RF004**: Cálculo de utilidad y registro best-effort
- **Health & Resilience**: Pings previos a servicios críticos y manejo homogéneo de errores (degradación a 503)

**Funcionalidades Clave:**

- Punto único para RF-003, RF-004 y RF-005
- Validaciones transversales uniformes
- Cálculo determinista de utilidad (score)
- Orquestación síncrona tolerante a fallos parciales (best‑effort con Scores)
- Ordenamiento de ofertas por utilidad descendente

### Scores Microservice

Almacena la utilidad (score) de cada oferta. Su indisponibilidad no bloquea la creación ni la consulta; RF-005 retorna `score = null` cuando no hay dato.

**Componentes principales:**

- **Scores API**: Endpoints para registrar y consultar utilidad de ofertas
- **Score Management**: Lógica de persistencia y validaciones básicas
- **Scores DB**: Base de datos PostgreSQL para almacenamiento de utilidades

**Funcionalidades:** Registro y consulta puntual de score; operación idempotente esperada para evitar duplicidades.

### Users Microservice

Gestión de usuarios, autenticación y perfil.

**Componentes principales:**

- **Users API**: Endpoints REST para operaciones CRUD de usuarios
- **User Management**: Lógica de negocio para gestión de usuarios
- **Authentication**: Sistema de autenticación basado en tokens UUID
- **Users DB**: Base de datos PostgreSQL para almacenamiento de usuarios

**Funcionalidades:**

- Registro de usuarios
- Autenticación y generación de tokens
- Consulta y actualización de perfiles
- Gestión de sesiones

### Posts Microservice

Gestión del ciclo de vida de publicaciones.

**Componentes principales:**

- **Posts API**: Endpoints REST para operaciones CRUD de publicaciones
- **Post Management**: Lógica de negocio para gestión de publicaciones
- **Posts DB**: Base de datos PostgreSQL para almacenamiento de publicaciones

**Funcionalidades:**

- Creación de publicaciones
- Consulta y filtrado de publicaciones
- Eliminación de publicaciones
- Gestión de fechas de expiración

### Offers Microservice

Gestión de ofertas sobre publicaciones activas.

**Componentes principales:**

- **Offers API**: Endpoints REST para operaciones CRUD de ofertas
- **Offer Management**: Lógica de negocio para gestión de ofertas
- **Offers DB**: Base de datos PostgreSQL para almacenamiento de ofertas

**Funcionalidades:**

- Creación de ofertas
- Consulta y filtrado de ofertas
- Eliminación de ofertas
- Gestión de precios y características de objetos

### Routes Microservice

Gestión de trayectos y costos de maleta asociados.

**Componentes principales:**

- **Routes API**: Endpoints REST para operaciones CRUD de rutas
- **Route Management**: Lógica de negocio para gestión de rutas
- **Routes DB**: Base de datos PostgreSQL para almacenamiento de rutas

**Funcionalidades:**

- Creación de rutas
- Consulta y filtrado de rutas
- Eliminación de rutas
- Gestión de costos y fechas de viaje

### Credit Cards Microservice (RF-006)

Gestión del ciclo de vida de tarjetas de crédito con verificación asíncrona mediante TrueNative.

**Componentes principales:**

- **Credit Cards API**: Endpoints REST para operaciones CRUD de tarjetas de crédito
- **Card Verification Service**: Integración con TrueNative para verificación
- **Card Poller Service**: Servicio de polling para obtener estados de verificación
- **Email Notification Service**: Notificaciones por correo electrónico
- **Credit Cards DB**: Base de datos PostgreSQL para almacenamiento de tarjetas

**Funcionalidades:**

- Registro de tarjetas de crédito
- Verificación asíncrona mediante TrueNative (polling)
- Notificación por email del resultado de verificación
- Consulta de tarjetas del usuario
- Gestión de estados de tarjeta (POR_VERIFICAR, APROBADA, RECHAZADA)

### User Verification Service (RF-007)

Servicio integrado en Users Microservice para verificación de identidad de usuarios mediante TrueNative.

**Componentes principales:**

- **User Verification Handler**: Procesamiento de webhooks de verificación
- **Identity Verification Service**: Integración con TrueNative para verificación
- **Webhook Endpoint**: Endpoint para recibir callbacks de TrueNative
- **Email Notification Service**: Notificaciones por correo electrónico

**Funcionalidades:**

- Verificación automática de identidad en creación de usuario
- Procesamiento de webhooks de TrueNative
- Actualización de estados de usuario (POR_VERIFICAR, VERIFICADO, NO_VERIFICADO)
- Notificación por email del resultado de verificación
- Restricción de acceso para usuarios no verificados

### TrueNative Integration Service

Servicio externo para verificación de identidad y tarjetas de crédito.

**Componentes principales:**

- **Identity Verification API**: Verificación de identidad de usuarios
- **Card Registration API**: Registro y verificación de tarjetas de crédito
- **Webhook System**: Sistema de callbacks para notificaciones
- **Audit Endpoints**: Endpoints de auditoría para desarrollo

### Servicios de Soporte (Arquitectura Asíncrona)

#### Producer Service

Generador de mensajes para colas SQS. Facilita el procesamiento asíncrono de verificaciones.

**Componentes principales:**

- **Message Producer**: Generación y envío de mensajes
- **SQS Adapter**: Integración con Amazon SQS
- **Producer API**: Endpoints para generar eventos

#### Publisher Service

Publicador de eventos y notificaciones para el sistema.

**Componentes principales:**

- **Event Publisher**: Publicación de eventos de sistema
- **Notification Handler**: Manejo de notificaciones
- **Publisher API**: Endpoints de publicación

#### Consumer Service

Procesador de mensajes de colas para verificaciones asíncronas.

**Componentes principales:**

- **Message Consumer**: Procesamiento de mensajes SQS
- **Verification Handler**: Manejo de verificaciones pendientes
- **Queue Processor**: Procesador de cola de trabajo

#### Subscriber Service

Suscriptor de eventos para procesamiento distribuido.

**Componentes principales:**

- **Event Subscriber**: Suscripción a eventos de sistema
- **Event Handler**: Procesamiento de eventos recibidos
- **Notification Processor**: Procesamiento de notificaciones

#### Mathematical Services (Addition/Multiplication)

Servicios computacionales de soporte para cálculos.

**Componentes principales:**

- **Mathematical Operations**: Operaciones aritméticas básicas
- **Score Calculation Support**: Soporte para cálculo de utilidades
- **Computational API**: Endpoints de cálculo

## Comunicación entre Componentes

### APIs REST

Todos los microservicios internos exponen APIs REST. El cliente sólo interactúa con un host expuesto vía Ingress. El Aggregator enruta y orquesta internamente:

- **Aggregator API** (punto único): expone `/rf003`, `/rf004`, `/rf005`
- **Users API**: Gestión de usuarios y autenticación
- **Posts API**: Gestión de publicaciones base
- **Routes API**: Gestión de rutas y costos de maleta
- **Offers API**: Gestión de ofertas individuales
- **Scores API**: Persistencia y consulta de utilidad

### Endpoints Comunes

Todos los servicios de dominio exponen:

- `GET /ping`: Salud
- `POST /reset`: Limpieza controlada (entornos de prueba)
- Endpoints del dominio

### Aislamiento

- Cada microservicio mantiene su base de datos y no comparte tablas.
- La comunicación entre dominios para los flujos RF-003, RF-004 y RF-005 ocurre únicamente a través del Aggregator (patrón Orchestrator). No hay acoplamientos directos entre servicios de dominio.
- La ausencia temporal del servicio de Scores no interrumpe RF-005 (score opcional con valor null) ni RF-004 (registro best-effort).

## Diagrama de Componentes

![Diagrama de componentes](diagrams/components.png)

El diagrama incorpora Aggregator y Scores sin introducir dependencias laterales entre servicios de dominio.

## Tecnologías por Componente

### Framework Web

- **Flask**: Framework web para todos los microservicios
- **Flask-Smorest**: Extensión para APIs REST con documentación automática

### Base de Datos

- **SQLAlchemy**: ORM para acceso a bases de datos
- **PostgreSQL**: Base de datos principal para todos los microservicios
- **psycopg2**: Driver PostgreSQL para Python

### Validación y Serialización

- **Marshmallow**: Validación y serialización
- **UUID**: Identificadores únicos

### Testing (Microservicios)

- **pytest**: Framework de testing para todos los microservicios
- **pytest-cov**: Cobertura de código
- **SQLite**: Base de datos para testing

## Patrones de Diseño

### Arquitectura de Capas

Cada microservicio sigue una arquitectura de capas:

1. **Capa de Presentación**: APIs REST
2. **Capa de Lógica de Negocio**: Gestión de entidades
3. **Capa de Datos**: Acceso a base de datos

### Factory Pattern

- Patrón de fábrica para creación de aplicaciones Flask
- Configuración centralizada de bases de datos
- Inyección de dependencias

### Repository Pattern

- Abstrae persistencia y facilita pruebas

### Orchestrator Pattern (Aggregator)

- **Rol**: Centralizar la coordinación de microservicios para flujos compuestos que requieren múltiples validaciones y agregación de datos.
- **Beneficio**: Simplifica el cliente (una sola llamada), evita lógica distribuida en cada microservicio, mantiene independencia de datos.
- **Trade-offs**: Punto adicional a escalar; mitigado con diseño stateless y posibilidad de replicas.

### Best-Effort Integration (Scores)

Evita fallos totales si la persistencia de score está indisponible (`score = null`).

### Validation Gateway

Centraliza validaciones transversales para reducir duplicación y divergencias.

## Escalabilidad y Mantenibilidad

### Independencia

- Servicios de dominio escalan independientemente.
- Aggregator escala horizontalmente según uso de endpoints compuestos.
- Scores escala según ratio lectura/escritura de utilidades.

### Flujos Clave

| Requerimiento | Endpoint                      | Flujo Resumido                                                                                                                                        |
| ------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| RF-003        | POST /rf003/posts             | Token → Validar fechas → Buscar/crear ruta → Unicidad → Crear publicación → Respuesta                                                                 |
| RF-004        | POST /rf004/posts/{id}/offers | Token → Usuario → Publicación → Ownership/Expiración → Derivar bagCost → Crear oferta → Calcular utilidad → Registrar score (best‑effort) → Respuesta |
| RF-005        | GET /rf005/posts/{id}         | Token → Usuario → Publicación → Ownership → Ofertas → Scores (best‑effort) → Ruta → Ordenar por score desc → Respuesta                                |

### Reglas de Negocio Consolidada (Resumen)

- Fechas en ISO UTC.
- Una publicación activa por usuario y ruta.
- Prohibido ofertar la propia publicación.
- Sólo publicaciones vigentes aceptan ofertas.
- offer > 0 y size ∈ {LARGE, MEDIUM, SMALL}.
- score = offer − (occupancy × bagCost) (occupancy por size).

### Testing

- Tests unitarios y de integración
- Cobertura ≥ 70% por microservicio

### Documentación

- APIs documentadas (Swagger/OpenAPI)
- READMEs por microservicio
- Documentación centralizada

## Diagramas de Secuencia

### RF-003

![RF003](diagrams/seq_rf003.png)

### RF-004

![RF004](diagrams/seq_rf004.png)

### RF-005

![RF005](diagrams/seq_rf005.png)

Cada diagrama muestra validaciones, llamadas a servicios y degradación controlada (best‑effort para Score en RF004/RF005).

## Nuevos Componentes para RF-006 y RF-007

### Componente: Credit Cards API

| Aspecto | Descripción |
|---------|-------------|
| **Componente** | Credit Cards API |
| **Código/Id del componente** | CC-API |
| **Tipo** | Servicio |
| **Responsabilidad** | Gestiona el ciclo de vida de tarjetas de crédito, incluyendo registro, verificación asíncrona y consultas. Actúa como punto de entrada para todas las operaciones relacionadas con tarjetas. |
| **Consideraciones de diseño** | Implementa polling hacia TrueNative para verificación asíncrona. Trade-off: Mayor complejidad vs. disponibilidad independiente del webhook. Impacto mínimo en sistema existente al ser completamente nuevo microservicio. |
| **Integraciones** | TrueNative (HTTP/REST), Email Service (HTTP interno), Users Service (HTTP/REST), Credit Cards DB (SQL) |

### Componente: Card Verification Service

| Aspecto | Descripción |
|---------|-------------|
| **Componente** | Card Verification Service |
| **Código/Id del componente** | CV-SRV |
| **Tipo** | Servicio |
| **Responsabilidad** | Maneja la integración específica con TrueNative para verificación de tarjetas. Abstrae la lógica de comunicación externa y manejo de errores. |
| **Consideraciones de diseño** | Patrón Circuit Breaker para fallos de TrueNative. Retry logic con backoff exponencial. Separación de responsabilidades del API principal. |
| **Integraciones** | TrueNative (HTTP/REST), Credit Cards API (HTTP interno) |

### Componente: Card Poller Service

| Aspecto | Descripción |
|---------|-------------|
| **Componente** | Card Poller Service |
| **Código/Id del componente** | CP-SRV |
| **Tipo** | Servicio |
| **Responsabilidad** | Ejecuta polling periódico a TrueNative para obtener estados de verificación de tarjetas. Actualiza estados en base de datos y dispara notificaciones. |
| **Consideraciones de diseño** | Patrón Polling con intervalos configurables. Trade-off: Latencia de actualización vs. carga en TrueNative. Implementación como proceso en background independiente. |
| **Integraciones** | TrueNative (HTTP/REST), Credit Cards DB (SQL), Email Service (HTTP interno) |

### Componente: User Verification Handler

| Aspecto | Descripción |
|---------|-------------|
| **Componente** | User Verification Handler |
| **Código/Id del componente** | UV-HDL |
| **Tipo** | Servicio |
| **Responsabilidad** | Procesa webhooks de TrueNative para verificación de usuarios. Actualiza estados de usuarios y maneja la lógica de verificación de tokens. |
| **Consideraciones de diseño** | Webhook pattern para comunicación asíncrona. Validación de tokens de TrueNative para seguridad. Integración con sistema de autenticación existente. |
| **Integraciones** | TrueNative (HTTP webhook), Users DB (SQL), Email Service (HTTP interno) |

### Componente: Identity Verification Service

| Aspecto | Descripción |
|---------|-------------|
| **Componente** | Identity Verification Service |
| **Código/Id del componente** | IV-SRV |
| **Tipo** | Servicio |
| **Responsabilidad** | Maneja la solicitud inicial de verificación de identidad a TrueNative cuando se crea un usuario. Configura webhooks y maneja respuestas. |
| **Consideraciones de diseño** | Integración automática en flujo de registro. Trade-off: Acoplamiento vs. experiencia de usuario fluida. Manejo de fallos de TrueNative con degradación controlada. |
| **Integraciones** | TrueNative (HTTP/REST), Users API (HTTP interno), Webhook Handler (HTTP interno) |

### Componente: Email Notification Service

| Aspecto | Descripción |
|---------|-------------|
| **Componente** | Email Notification Service |
| **Código/Id del componente** | EN-SRV |
| **Tipo** | Servicio |
| **Responsabilidad** | Servicio centralizado para envío de notificaciones por correo electrónico. Maneja templates y configuración SMTP para RF-006 y RF-007. |
| **Consideraciones de diseño** | Servicio compartido entre múltiples componentes. Patrón Template Method para diferentes tipos de email. Configuración SMTP externalizada. |
| **Integraciones** | SMTP Server (SMTP), Credit Cards API (HTTP interno), Users API (HTTP interno) |

### Componente: TrueNative Service

| Aspecto | Descripción |
|---------|-------------|
| **Componente** | TrueNative Service |
| **Código/Id del componente** | TN-SRV |
| **Tipo** | Servicio Externo |
| **Responsabilidad** | Proveedor externo para verificación de identidad y tarjetas de crédito. Ofrece APIs de verificación y sistema de webhooks/polling. |
| **Consideraciones de diseño** | Servicio externo con limitaciones de tiempo de respuesta (30-120 segundos). Configuración de tokens secretos. Rate limiting y gestión de cuotas. |
| **Integraciones** | Credit Cards API (HTTP/REST), Users API (HTTP/REST), Webhook Endpoints (HTTP) |
