# Documentación Técnica - Sistema de Microservicios

## Equipo Cloudly

**Integrantes:**

- **jd.riosn1** (25%) - Responsable de Users App
- **hvlopez** (25%) - Responsable de Posts App
- **l.carretero** (25%) - Responsable de Offers App
- **f.fernandezr** (25%) - Responsable de Routes App

**Enlaces:**

- [Dashboard de Tareas](https://github.com/orgs/uniandes-isis2603/projects/1)
- [GitHub Pages](https://uniandes-isis2603.github.io/s202514-proyecto-grupo17/)

## Tecnologías Seleccionadas

### Lenguajes de Programación

- **Python 3.9+**: Lenguaje principal para el desarrollo de microservicios
- **YAML**: Para configuración de Kubernetes y CI/CD

### Frameworks y Librerías

- **Flask 2.3.3**: Framework web para APIs REST
- **Flask-Smorest 0.42.0**: Extensión para APIs REST con documentación automática
- **SQLAlchemy 3.0.5**: ORM para manejo de bases de datos
- **Marshmallow 3.20.1**: Serialización y validación de datos
- **psycopg2-binary 2.9.7**: Driver PostgreSQL para Python

### Base de Datos

- **PostgreSQL 13**: Base de datos relacional principal
- **SQLite**: Base de datos para desarrollo local y testing

### Testing

- **pytest 7.4.2**: Framework de testing
- **pytest-cov 4.1.0**: Cobertura de código
- **Postman**: Testing de APIs

### Contenedores y Orquestación

- **Docker**: Contenedores de aplicaciones
- **Kubernetes (Minikube)**: Orquestación de contenedores
- **Helm**: Gestión de paquetes Kubernetes (opcional)

### CI/CD

- **GitHub Actions**: Pipelines de integración continua
- **Docker Hub**: Registro de imágenes

### Documentación

- **Markdown**: Documentación técnica
- **PlantUML**: Diagramas de arquitectura
- **GitHub Pages**: Documentación web

### Herramientas de Desarrollo

- **Git**: Control de versiones
- **Make**: Automatización de tareas
- **Vale**: Linting de documentación

## Tabla de Contenido

### Vistas de Arquitectura

1. **[Vista de Información](information-view.md)** - Modelo de datos y entidades
2. **[Vista Funcional](functional-view.md)** - Componentes del sistema
3. **[Vista de Despliegue](deployment-view.md)** - Arquitectura de despliegue
4. **[Vista de Desarrollo](development-view.md)** - Decisiones de desarrollo

### Documentación de Aplicaciones

- **[Users App](../users_app/README.md)** - Microservicio de usuarios
- **[Posts App](../posts_app/README.md)** - Microservicio de publicaciones
- **[Offers App](../offers_app/README.md)** - Microservicio de ofertas
- **[Routes App](../routes_app/README.md)** - Microservicio de rutas

### Guías de Despliegue

- **[Despliegue Local](../README.md#despliegue-local)** - Instrucciones para desarrollo
- **[Despliegue en Kubernetes](../README.md#despliegue-en-kubernetes)** - Instrucciones para producción

## Características del Sistema

### Arquitectura de Microservicios

- **4 microservicios independientes**: Users, Posts, Offers, Routes
- **Bases de datos aisladas**: Cada microservicio tiene su propia base de datos PostgreSQL
- **APIs REST**: Comunicación mediante HTTP/REST
- **Contenedores Docker**: Cada microservicio se ejecuta en contenedores independientes

### Seguridad y Aislamiento

- **Network Policies**: Aislamiento de red entre microservicios
- **Tokens UUID**: Autenticación mediante tokens UUID (no JWT)
- **Bases de datos aisladas**: Cada microservicio solo accede a su propia base de datos

### Escalabilidad y Disponibilidad

- **Kubernetes**: Orquestación y escalabilidad automática
- **Health Checks**: Endpoints `/ping` para verificación de estado
- **Reset Endpoints**: Endpoints `/reset` para limpieza de datos

### Calidad de Código

- **Cobertura de pruebas**: Mínimo 70% por aplicación
- **Linting**: Validación de código y documentación
- **CI/CD**: Pipelines automatizados de testing y despliegue
