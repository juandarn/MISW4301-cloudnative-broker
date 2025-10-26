# Vista de Desarrollo

## Descripción General

Decisiones de construcción: estructura, stack tecnológico, orquestación (Aggregator), servicio de utilidad (Scores), resiliencia, idempotencia y calidad.

## 1. Estructura del Proyecto

### 1.1 Raíz

```
s202514-proyecto-grupo17/
├── config.yaml                 # Configuración del equipo y aplicaciones
├── README.md                   # Este archivo
├── makefile                    # Automatización de tareas
├── .github/                    # Configuración de GitHub Actions
│   └── workflows/
│       ├── ci_evaluador_unit.yml
│       ├── ci_evaluador_entrega1_docs.yml
│       ├── ci_evaluador_entrega1_k8s.yml
│       └── pages/
├── docs/                       # Documentación técnica
│   ├── README.md              # Página principal de documentación
│   ├── information-view.md    # Vista de información
│   ├── functional-view.md     # Vista funcional
│   ├── deployment-view.md     # Vista de despliegue
│   ├── development-view.md    # Vista de desarrollo
│   └── diagrams/              # Diagramas PlantUML
│       ├── entities.puml
│       ├── components.puml
│       ├── deployment.puml
│       └── networks.puml
├── k8s/                        # Configuraciones de Kubernetes
│   ├── users-app-service.yaml
│   ├── users-db-service.yaml
│   ├── users-network.yaml
│   ├── posts-app-service.yaml
│   ├── posts-db-service.yaml
│   ├── posts-networks.yaml
│   ├── offers-app-service.yaml
│   ├── offers-db-service.yaml
│   ├── offers-network.yaml
│   ├── routes-app.yaml
│   ├── routes-db.yaml
│   └── routes-network.yaml
├── users_app/                  # Microservicio de usuarios
├── posts_app/                  # Microservicio de publicaciones
├── offers_app/                 # Microservicio de ofertas
├── routes_app/                 # Microservicio de rutas
└── pets_app/                   # Microservicio de mascotas (ejemplo)
```

### 1.2 Microservicio Tipo

Estructura homogénea simplifica navegación y pruebas (convención repetible):

```
microservicio/
├── app.py                     # Punto de entrada de la aplicación
├── db.py                      # Configuración de SQLAlchemy
├── models/                    # Modelos de dominio
│   └── entity.py             # Modelo principal de la entidad
├── resources/                 # Controladores de la API
│   └── entity.py             # Endpoints REST
├── schemas.py                 # Esquemas de validación Marshmallow
├── requirements.txt           # Dependencias Python
├── Dockerfile                 # Configuración de contenedor
├── pytest.ini                # Configuración de pruebas
├── README.md                 # Documentación específica
└── test/                     # Pruebas unitarias e integración
    ├── api/                  # Pruebas de API
    └── unit/                 # Pruebas unitarias
        └── domain/
            └── models/
                └── test_entity.py
```

## 2. Stack Tecnológico

### 2.1 Desarrollo

| Categoría                | Tecnología      | Versión | Propósito                                  |
| ------------------------ | --------------- | ------- | ------------------------------------------ |
| **Lenguaje**             | Python          | 3.9+    | Lenguaje principal de desarrollo           |
| **Framework Web**        | Flask           | 2.3.3   | Framework web para APIs REST               |
| **API Framework**        | Flask-Smorest   | 0.42.0  | Extensión para APIs REST con documentación |
| **ORM**                  | SQLAlchemy      | 3.0.5   | Mapeo objeto-relacional                    |
| **Validación**           | Marshmallow     | 3.20.1  | Serialización y validación de datos        |
| **Base de Datos**        | PostgreSQL      | 13      | Base de datos principal                    |
| **Driver DB**            | psycopg2-binary | 2.9.7   | Driver PostgreSQL para Python              |
| **Testing**              | pytest          | 7.4.2   | Framework de testing                       |
| **Cobertura**            | pytest-cov      | 4.1.0   | Cobertura de código                        |
| **Variables de Entorno** | python-dotenv   | 1.0.0   | Gestión de variables de entorno            |

### 2.2 Contenedores y Orquestación

| Categoría             | Tecnología | Versión | Propósito                                  |
| --------------------- | ---------- | ------- | ------------------------------------------ |
| **Contenedores**      | Docker     | Latest  | Contenedores de aplicaciones               |
| **Orquestación**      | Kubernetes | Latest  | Orquestación de contenedores               |
| **Clúster Local**     | Minikube   | Latest  | Clúster local de Kubernetes                |
| **Gestión de Config** | kubectl    | Latest  | Cliente de línea de comandos de Kubernetes |

### 2.3 CI/CD

| Categoría                | Tecnología     | Versión | Propósito                   |
| ------------------------ | -------------- | ------- | --------------------------- |
| **Pipelines**            | GitHub Actions | Latest  | Integración continua        |
| **Linting**              | Vale           | Latest  | Validación de documentación |
| **Control de Versiones** | Git            | Latest  | Control de versiones        |
| **Automatización**       | Make           | Latest  | Automatización de tareas    |

### 2.4 Documentación

| Categoría             | Tecnología      | Versión | Propósito                 |
| --------------------- | --------------- | ------- | ------------------------- |
| **Documentación**     | Markdown        | -       | Documentación técnica     |
| **Diagramas**         | PlantUML        | -       | Diagramas de arquitectura |
| **Documentación Web** | GitHub Pages    | -       | Documentación web         |
| **APIs**              | Swagger/OpenAPI | 3.0.3   | Documentación de APIs     |

## 3. Decisiones Arquitectónicas

Tabla consolidada de decisiones (evita repetición “Decisión/Justificación”):

| Tema             | Decisión                                      | Motivación Principal                                        |
| ---------------- | --------------------------------------------- | ----------------------------------------------------------- |
| Orquestación     | Aggregator centraliza RF003–RF005             | Unifica validaciones, reduce llamadas, facilita resiliencia |
| Score            | Servicio Scores separado                      | Escalado independiente y evolución de fórmula               |
| Best‑Effort      | No bloquear oferta si falla score             | Disponibilidad sobre consistencia estricta                  |
| Validaciones     | Centralizar en Aggregator                     | Evitar duplicación/divergencia de reglas                    |
| Errores          | Mapeo uniforme (503 y códigos funcionales)    | Experiencia consistente y observabilidad                    |
| Cálculo utilidad | `offer - (occupancy * bagCost)` en Aggregator | Tiene datos necesarios sin acoplar dominio extra            |
| Tiempos/Fechas   | ISO8601 UTC                                   | Eliminar ambigüedad de zonas horarias                       |
| Enumeraciones    | LARGE/MEDIUM/SMALL                            | Semántica clara y factores directos                         |
| Idempotencia     | Reusar ruta por `flightId`                    | Evitar duplicados y mantener relación estable               |
| Estado           | Aggregator stateless                          | Escalado horizontal simple                                  |
| Observabilidad   | Logs + pings previos                          | Fail‑fast y trazabilidad básica                             |
| Persistencia     | PostgreSQL por dominio                        | Aislamiento de datos y autonomía                            |
| Contenedores     | Docker + K8s                                  | Estandarización y escalabilidad                             |
| Testing          | pytest + cobertura ≥70%                       | Confianza y regresión controlada                            |
| Diagramas        | PlantUML como código                          | Versionado y automatización CI/CD                           |

## 4. Patrones Aplicados y Análisis de Atributos de Calidad

### 4.1 Patrón Orchestrator (Aggregator)

**Implementación**: El servicio Aggregator coordina los flujos compuestos RF003, RF004 y RF005, centralizando la lógica de orquestación y validaciones transversales.

**Justificación de la decisión**:

- **Complejidad de coordinación**: Los RFs requieren llamadas a múltiples servicios con validaciones y transformaciones específicas
- **Consistencia de reglas**: Evita duplicar lógica de validación across servicios
- **Punto único de entrada**: Simplifica la interfaz para clientes externos
- **Control transaccional**: Permite manejar fallos parciales de manera consistente

**Atributos de calidad beneficiados**:

- **🟢 Mantenibilidad**: Centralizar lógica reduce duplicación y facilita evolución de reglas de negocio
- **🟢 Usabilidad**: API única y consistente para el cliente, reduciendo complejidad de integración
- **🟢 Testabilidad**: Flujos complejos se testean en un solo lugar
- **🟢 Modificabilidad**: Cambios en lógica de orquestación no impactan otros servicios
- **🟢 Interoperabilidad**: Abstrae complejidades internas del ecosistema de servicios

**Atributos de calidad perjudicados**:

- **🔴 Disponibilidad**: Punto único de falla - si el Aggregator cae, todos los RFs fallan
- **🔴 Performance**: Introduce latencia adicional (hop extra) y bottleneck potencial
- **🔴 Escalabilidad**: Concentra carga de múltiples operaciones en un componente
- **🔴 Acoplamiento**: Crea dependencia del Aggregator hacia todos los servicios de dominio

### 4.2 Patrón Best-Effort Write (Servicio Scores)

**Implementación**: El registro de scores en RF004 no bloquea la creación de ofertas. Si el servicio Scores falla, la oferta se crea exitosamente y el score se omite.

**Justificación de la decisión**:

- **Criticidad diferenciada**: La funcionalidad core (crear oferta) es más importante que la métrica (score)
- **Disponibilidad del servicio principal**: Evita que fallos en servicios auxiliares afecten funcionalidades críticas
- **Experiencia de usuario**: El usuario puede completar su acción principal sin interrupciones
- **Tolerancia a fallos**: El sistema continúa operando con degradación graceful

**Atributos de calidad beneficiados**:

- **🟢 Disponibilidad**: Alta disponibilidad del flujo principal ante fallos parciales
- **🟢 Resilencia**: Sistema tolera fallos de componentes no críticos
- **🟢 Performance**: No introduce bloqueos por servicios lentos o caídos
- **🟢 Usabilidad**: Usuario no experimenta errores por funcionalidades secundarias

**Atributos de calidad perjudicados**:

- **🔴 Consistencia**: Posible inconsistencia entre ofertas y sus scores correspondientes
- **🔴 Integridad de datos**: Pérdida de información de utilidad que podría ser valiosa para análisis
- **🔴 Observabilidad**: Más difícil detectar y monitorear fallos "silenciosos"
- **🔴 Predictabilidad**: Comportamiento variable dependiendo del estado del servicio Scores

### 4.3 Patrón Projection (RF005 - Composición de datos)

**Implementación**: RF005 agrega datos de Post, Route, Offers y Scores en una sola respuesta, proyectando información desde múltiples servicios sin crear acoplamientos directos entre bases de datos.

**Justificación de la decisión**:

- **Eficiencia de red**: Una sola llamada del cliente en lugar de múltiples requests
- **Autonomía de servicios**: Cada servicio mantiene su independencia de datos
- **Responsabilidad clara**: El Aggregator es responsable de la composición
- **Flexibilidad de presentación**: Permite adaptar la respuesta según necesidades del cliente

**Atributos de calidad beneficiados**:

- **🟢 Performance**: Reduce chattiness entre cliente y servicios
- **🟢 Usabilidad**: Interfaz simplificada para el cliente (una llamada vs múltiples)
- **🟢 Mantenibilidad**: Separación clara de responsabilidades entre servicios
- **🟢 Autonomía**: Servicios mantienen independencia de esquemas de datos
- **🟢 Modificabilidad**: Cambios en estructura de datos locales no afectan otros servicios

**Atributos de calidad perjudicados**:

- **🔴 Latencia**: Latencia acumulada de múltiples llamadas secuenciales
- **🔴 Acoplamiento operacional**: Aggregator depende de disponibilidad de todos los servicios
- **🔴 Complejidad**: Lógica de composición y manejo de errores se concentra en un lugar
- **🔴 Cacheabilidad**: Difícil cachear respuestas que agregan datos dinámicos de múltiples fuentes

### 4.4 Patrón Validation Gateway

**Implementación**: Validaciones transversales (autenticación, autorización, formato de datos) se centralizan en el Aggregator antes de llamar servicios downstream.

**Justificación de la decisión**:

- **DRY (Don't Repeat Yourself)**: Evita duplicar validaciones en múltiples servicios
- **Consistencia**: Garantiza aplicación uniforme de reglas de negocio
- **Performance**: Fail-fast sin llamadas innecesarias a servicios downstream
- **Segregación de responsabilidades**: Servicios de dominio se enfocan en su lógica específica

**Atributos de calidad beneficiados**:

- **🟢 Consistencia**: Validaciones uniformes across todos los endpoints
- **🟢 Performance**: Validación temprana evita procesamientos innecesarios
- **🟢 Mantenibilidad**: Cambios en reglas de validación en un solo lugar
- **🟢 Seguridad**: Punto centralizado para aplicar políticas de seguridad
- **🟢 Testabilidad**: Validaciones complejas se testean una vez

**Atributos de calidad perjudicados**:

- **🔴 Acoplamiento**: Aggregator debe conocer reglas de validación de todos los dominios
- **🔴 Responsabilidad**: Viola parcialmente el principio de responsabilidad única
- **🔴 Evolución independiente**: Cambios en validaciones requieren modificar el Aggregator
- **🔴 Disponibilidad**: Fallos en validaciones centralizadas afectan todos los flujos

### 4.5 Patrón Repository (Ligero)

**Implementación**: Capa ligera de acceso a datos por servicio, sin abstracción compleja pero separando queries de lógica de negocio.

**Justificación de la decisión**:

- **Simplicidad**: Evita over-engineering con abstracciones pesadas
- **Testabilidad**: Facilita mocking de acceso a datos en pruebas
- **Separación mínima**: Distingue entre lógica de negocio y acceso a datos
- **Flexibilidad**: Permite evolucionar patrones de acceso a datos independientemente

**Atributos de calidad beneficiados**:

- **🟢 Testabilidad**: Facilita unit testing con mocks de datos
- **🟢 Mantenibilidad**: Separación clara entre capas de responsabilidad
- **🟢 Modificabilidad**: Cambios en esquemas de DB no afectan lógica de negocio directamente
- **🟢 Legibilidad**: Código de negocio más limpio sin queries SQL embebidas

**Atributos de calidad perjudicados**:

- **🔴 Performance**: Capa adicional de abstracción introduce overhead mínimo
- **🔴 Simplicidad**: Añade estructura adicional que podría ser innecesaria en servicios simples
- **🔴 Curva de aprendizaje**: Desarrolladores deben entender el patrón repository

### 4.6 Patrón Defensive Ping

**Implementación**: Antes de orquestar llamadas complejas, el Aggregator verifica la salud de servicios downstream mediante endpoints `/ping`.

**Justificación de la decisión**:

- **Fail-fast**: Detecta fallos temprano antes de iniciar procesamiento costoso
- **Experiencia de usuario**: Errores más rápidos y informativos
- **Observabilidad**: Permite identificar qué servicio específico está fallando
- **Prevención de recursos**: Evita usar recursos en operaciones destinadas a fallar

**Atributos de calidad beneficiados**:

- **🟢 Resilencia**: Detección temprana de fallos del sistema
- **🟢 Performance**: Latencia reducida en escenarios de fallo
- **🟢 Observabilidad**: Mejor visibilidad del estado del sistema
- **🟢 Usabilidad**: Mensajes de error más específicos y útiles

**Atributos de calidad perjudicados**:

- **🔴 Latencia**: Overhead adicional de pings en cada operación
- **🔴 Complejidad**: Lógica adicional de health checking y manejo de estados
- **🔴 Tráfico de red**: Incremento en número de llamadas de red
- **🔴 Race conditions**: Estado del servicio puede cambiar entre ping y llamada real

### 4.7 Patrón Idempotencia Lógica

**Implementación**: Reutilización de rutas basada en `flightId` garantiza que operaciones repetidas no creen duplicados.

**Justificación de la decisión**:

- **Tolerancia a reintentos**: Permite que clientes reintenten operaciones sin efectos secundarios
- **Consistencia**: Mantiene relación estable entre vuelos y rutas
- **Recursos**: Evita proliferación innecesaria de entidades duplicadas
- **Predictabilidad**: Misma entrada produce misma salida

**Atributos de calidad beneficiados**:

- **🟢 Consistencia**: Previene duplicación de datos
- **🟢 Resilencia**: Permite reintentos seguros ante fallos de red
- **🟢 Integridad**: Mantiene relaciones lógicas estables
- **🟢 Usabilidad**: Cliente puede reintentar sin preocuparse por efectos secundarios

**Atributos de calidad perjudicados**:

- **🔴 Complejidad**: Lógica adicional para detectar y manejar duplicados
- **🔴 Performance**: Validaciones extra para verificar existencia previa
- **🔴 Storage**: Potencial acumulación de referencias a entidades no utilizadas

### 4.8 Resumen de Trade-offs Arquitectónicos

| Patrón             | Principal Beneficio | Principal Costo   | Decisión Estratégica                                           |
| ------------------ | ------------------- | ----------------- | -------------------------------------------------------------- |
| Orchestrator       | 🟢 Mantenibilidad   | 🔴 Disponibilidad | Priorizar simplicidad del cliente sobre resilencia distribuida |
| Best-Effort        | 🟢 Disponibilidad   | 🔴 Consistencia   | Funcionalidad core > métricas auxiliares                       |
| Projection         | 🟢 Usabilidad       | 🔴 Latencia       | UX integrada > performance de llamadas individuales            |
| Validation Gateway | 🟢 Consistencia     | 🔴 Acoplamiento   | Uniformidad > autonomía completa de servicios                  |
| Repository         | 🟢 Testabilidad     | 🔴 Complejidad    | Mantenibilidad a largo plazo > simplicidad inicial             |
| Defensive Ping     | 🟢 Observabilidad   | 🔴 Latencia       | Visibilidad de fallos > performance óptima                     |
| Idempotencia       | 🟢 Consistencia     | 🔴 Complejidad    | Integridad de datos > simplicidad de operaciones               |

**Filosofía general**: El diseño prioriza **mantenibilidad**, **usabilidad** y **consistencia** sobre **performance absoluto** y **disponibilidad distribuida**, asumiendo que para el contexto y escala del proyecto, es más importante tener un sistema predecible y fácil de mantener que uno optimizado para alta escala y tolerancia a fallos distribuidos.

## 5. Testing

| Nivel       | Alcance                                 | Herramientas       | Notas                               |
| ----------- | --------------------------------------- | ------------------ | ----------------------------------- |
| Unitario    | Validaciones, helpers, cálculo utilidad | pytest, pytest-cov | Cobertura objetivo ≥70%             |
| Integración | Endpoints orquestados RF003–RF005       | Flask test client  | Mock selectivo si crece complejidad |
| API         | Recorridos funcionales                  | Postman            | Soporta verificación manual rápida  |

Principios: casos felices + bordes (expiración, ownership, ausencia de score). Evitar mocks excesivos en primeras capas.

## 6. Despliegue y Operación

| Aspecto              | Estrategia                              | Notas                           |
| -------------------- | --------------------------------------- | ------------------------------- |
| Orquestación         | Kubernetes (Minikube / EKS)             | Un único Ingress                |
| Escalado             | Horizontal (Aggregator / Scores)        | Dominio independiente por carga |
| Aislamiento          | DB por servicio                         | Sin FKs cruzadas                |
| Health               | `/ping`, `/rf005/ping`                  | Integrable a probes K8s         |
| Logs                 | Estructurados (INFO/ERROR)              | Orquestación y latencias clave  |
| Métricas (sugeridas) | Latencia RF003/4/5, 5xx, pings fallidos | Futuro: tracing distribuido     |

## 7. Calidad y Versionado

| Dimensión      | Práctica                | Herramienta           |
| -------------- | ----------------------- | --------------------- |
| Estilo Código  | PEP8 / convenciones     | (Editor/Linter local) |
| Docs Markdown  | Lint y consistencia     | Vale                  |
| Diagramas      | Código versionado       | PlantUML              |
| CI/CD          | Pipelines de build/test | GitHub Actions        |
| Versionado     | Tags semánticos         | Git                   |
| Automatización | Tareas comunes          | Make                  |

Documentación por servicio (+ vistas de arquitectura) soporta onboarding y evolución.
