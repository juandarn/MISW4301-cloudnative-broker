# Vista de Desarrollo

## Descripción General

La vista de desarrollo describe las decisiones de desarrollo tomadas para el desarrollo del proyecto, incluyendo la estructura de carpetas, tecnologías seleccionadas y patrones de diseño implementados.

## Estructura del Proyecto

### Organización de Carpetas

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

### Estructura de Cada Microservicio

Cada microservicio sigue una estructura consistente:

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

## Tabla de Tecnologías

### Herramientas de Desarrollo

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

### Herramientas de Contenedores y Orquestación

| Categoría             | Tecnología | Versión | Propósito                                  |
| --------------------- | ---------- | ------- | ------------------------------------------ |
| **Contenedores**      | Docker     | Latest  | Contenedores de aplicaciones               |
| **Orquestación**      | Kubernetes | Latest  | Orquestación de contenedores               |
| **Clúster Local**     | Minikube   | Latest  | Clúster local de Kubernetes                |
| **Gestión de Config** | kubectl    | Latest  | Cliente de línea de comandos de Kubernetes |

### Herramientas de CI/CD

| Categoría                | Tecnología     | Versión | Propósito                   |
| ------------------------ | -------------- | ------- | --------------------------- |
| **Pipelines**            | GitHub Actions | Latest  | Integración continua        |
| **Linting**              | Vale           | Latest  | Validación de documentación |
| **Control de Versiones** | Git            | Latest  | Control de versiones        |
| **Automatización**       | Make           | Latest  | Automatización de tareas    |

### Herramientas de Documentación

| Categoría             | Tecnología      | Versión | Propósito                 |
| --------------------- | --------------- | ------- | ------------------------- |
| **Documentación**     | Markdown        | -       | Documentación técnica     |
| **Diagramas**         | PlantUML        | -       | Diagramas de arquitectura |
| **Documentación Web** | GitHub Pages    | -       | Documentación web         |
| **APIs**              | Swagger/OpenAPI | 3.0.3   | Documentación de APIs     |

## Decisiones de Desarrollo

### Arquitectura de Microservicios

**Decisión**: Implementar una arquitectura de microservicios con 4 servicios independientes.

**Justificación**:

- **Escalabilidad**: Cada microservicio puede escalar independientemente
- **Mantenibilidad**: Cambios en un servicio no afectan a otros
- **Tecnología**: Permite usar diferentes tecnologías por servicio
- **Equipo**: Facilita el trabajo en paralelo por diferentes desarrolladores

### Framework Web: Flask

**Decisión**: Usar Flask como framework web principal.

**Justificación**:

- **Simplicidad**: Framework ligero y fácil de aprender
- **Flexibilidad**: Permite configuraciones personalizadas
- **Ecosistema**: Amplia comunidad y librerías disponibles
- **Rendimiento**: Adecuado para APIs REST

### ORM: SQLAlchemy

**Decisión**: Usar SQLAlchemy como ORM.

**Justificación**:

- **Madurez**: ORM maduro y estable
- **Flexibilidad**: Soporte para múltiples bases de datos
- **Migraciones**: Herramientas de migración incluidas
- **Testing**: Fácil mock para pruebas unitarias

### Base de Datos: PostgreSQL

**Decisión**: Usar PostgreSQL como base de datos principal.

**Justificación**:

- **Requerimiento**: Especificado en el enunciado del proyecto
- **Confiabilidad**: Base de datos robusta y confiable
- **Características**: Soporte completo para ACID
- **Escalabilidad**: Adecuada para aplicaciones de producción

### Contenedores: Docker

**Decisión**: Usar Docker para contenedores.

**Justificación**:

- **Estandarización**: Estándar de la industria
- **Portabilidad**: Funciona en diferentes entornos
- **Integración**: Excelente integración con Kubernetes
- **Herramientas**: Amplio ecosistema de herramientas

### Orquestación: Kubernetes

**Decisión**: Usar Kubernetes para orquestación.

**Justificación**:

- **Escalabilidad**: Orquestación automática de contenedores
- **Confiabilidad**: Auto-healing y auto-scaling
- **Ecosistema**: Amplio ecosistema de herramientas
- **Estándar**: Estándar de la industria para contenedores

### Testing: pytest

**Decisión**: Usar pytest para testing.

**Justificación**:

- **Simplicidad**: Framework simple y fácil de usar
- **Características**: Fixtures, parametrización, plugins
- **Integración**: Excelente integración con CI/CD
- **Cobertura**: Herramientas de cobertura incluidas

### Documentación: PlantUML

**Decisión**: Usar PlantUML para diagramas.

**Justificación**:

- **Texto**: Diagramas como código
- **Versionado**: Fácil versionado con Git
- **Integración**: Integración con pipelines CI/CD
- **Estándar**: Estándar para diagramas UML

## Patrones de Diseño Implementados

### Factory Pattern

- **Aplicación**: Creación de aplicaciones Flask
- **Beneficio**: Configuración centralizada y testing

### Repository Pattern

- **Aplicación**: Acceso a datos en modelos
- **Beneficio**: Separación de lógica de negocio y persistencia

### Blueprint Pattern

- **Aplicación**: Organización de endpoints en Flask
- **Beneficio**: Modularidad y reutilización

### Dependency Injection

- **Aplicación**: Inyección de dependencias en aplicaciones
- **Beneficio**: Testing y configuración flexible

## Estrategias de Testing

### Testing Unitario

- **Cobertura mínima**: 70% por aplicación
- **Herramienta**: pytest + pytest-cov
- **Alcance**: Modelos, servicios, utilidades

### Testing de Integración

- **Herramienta**: pytest con Flask test client
- **Alcance**: Endpoints de API
- **Base de datos**: SQLite en memoria para testing

### Testing de API

- **Herramienta**: Postman
- **Alcance**: Endpoints completos
- **Ambiente**: Contenedores Docker

## Estrategias de Despliegue

### Desarrollo Local

- **Herramienta**: Minikube
- **Configuración**: Namespace default
- **Acceso**: Port forwarding para testing

### CI/CD

- **Pipelines**: GitHub Actions
- **Testing**: Automático en cada commit
- **Despliegue**: Manual con kubectl

### Monitoreo

- **Health Checks**: Endpoints `/ping`
- **Logs**: Logs de aplicaciones y bases de datos
- **Métricas**: Métricas de Kubernetes

## Calidad de Código

### Linting y Formato

- **Python**: PEP 8 compliance
- **Markdown**: Vale para documentación
- **YAML**: Validación de sintaxis

### Documentación

- **Código**: Docstrings en funciones y clases
- **APIs**: Documentación automática con Swagger
- **Arquitectura**: Diagramas PlantUML
- **README**: Documentación específica por aplicación

### Versionado

- **Git**: Control de versiones distribuido
- **Tags**: Versionado semántico
- **Branches**: Feature branches para desarrollo
