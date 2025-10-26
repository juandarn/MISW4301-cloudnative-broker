# Sistema de Microservicios - Grupo 17

[![Evaluador Documentación Entrega 1](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo17/actions/workflows/ci_evaluador_entrega1_docs.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo17/actions/workflows/ci_evaluador_entrega1_docs.yml)

[![Evaluador Implementación Entrega 1](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo17/actions/workflows/ci_evaluador_entrega1_k8s.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo17/actions/workflows/ci_evaluador_entrega1_k8s.yml)

[![Evaluador Pruebas Unitarias](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo17/actions/workflows/ci_evaluador_unit.yml/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo17/actions/workflows/ci_evaluador_unit.yml)

[![pages-build-deployment](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo17/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/MISW-4301-Desarrollo-Apps-en-la-Nube/s202514-proyecto-grupo17/actions/workflows/pages/pages-build-deployment)

## Equipo Cloudly

**Integrantes:**

- **jd.riosn1** (25%) - Responsable de Users App
- **hvlopez** (25%) - Responsable de Posts App
- **l.carretero** (25%) - Responsable de Offers App
- **f.fernandezr** (25%) - Responsable of Routes App

**Enlaces:**

- [Dashboard de Tareas](https://github.com/orgs/uniandes-isis2603/projects/1)
- [Documentación Técnica](https://uniandes-isis2603.github.io/s202514-proyecto-grupo17/)

## Estructura del Proyecto

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

## Microservicios

### Users App

- **Puerto**: 30001 (NodePort)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Registro, autenticación, gestión de usuarios
- [Documentación detallada](users_app/README.md)

### Posts App

- **Puerto**: 30001 (NodePort)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Creación, consulta, eliminación de publicaciones
- [Documentación detallada](posts_app/README.md)

### Offers App

- **Puerto**: 30003 (NodePort)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Gestión de ofertas de transporte
- [Documentación detallada](offers_app/README.md)

### Routes App

- **Puerto**: 30004 (NodePort)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Gestión de rutas de viaje
- [Documentación detallada](routes_app/README.md)

## Despliegue Local

### Prerrequisitos

1. **Docker**: Instalar Docker Desktop

   ```bash
   # macOS
   brew install --cask docker

   # Ubuntu
   sudo apt-get update
   sudo apt-get install docker.io
   ```

2. **Minikube**: Instalar Minikube

   ```bash
   # macOS
   brew install minikube

   # Ubuntu
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```

3. **kubectl**: Instalar kubectl

   ```bash
   # macOS
   brew install kubectl

   # Ubuntu
   sudo apt-get install kubectl
   ```

### Paso a Paso para Despliegue

#### 1. Iniciar Minikube

```bash
# Iniciar clúster local
minikube start

# Verificar estado
kubectl cluster-info
```

#### 2. Construir Imágenes Docker

```bash
# Construir imagen de Users App
cd users_app
docker build -t users-app:v1.0.0 .
cd ..

# Construir imagen de Posts App
cd posts_app
docker build -t posts-app:v1.0.0 .
cd ..

# Construir imagen de Offers App
cd offers_app
docker build -t offers-app:v1.0.0 .
cd ..

# Construir imagen de Routes App
cd routes_app
docker build -t routes-app:v1.0.0 .
cd ..
```

#### 3. Cargar Imágenes en Minikube

```bash
# Cargar imágenes en el clúster local
minikube image load users-app:v1.0.0
minikube image load posts-app:v1.0.0
minikube image load offers-app:v1.0.0
minikube image load routes-app:v1.0.0
```

#### 4. Desplegar Aplicaciones

```bash
# Desplegar Users App
kubectl apply -f k8s/users_app.yaml

# Desplegar Posts App
kubectl apply -f k8s/posts_app.yaml

# Desplegar Offers App
kubectl apply -f k8s/offers_app.yaml

# Desplegar Routes App
kubectl apply -f k8s/routes_app.yaml
```

#### 5. Verificar Despliegue

```bash
# Verificar pods
kubectl get pods

# Verificar servicios
kubectl get services

# Verificar deployments
kubectl get deployments
```

#### 6. Acceder a las Aplicaciones

**Opción 1: Port Forwarding (Recomendado)**

```bash
# Users App
kubectl port-forward service/users-app-service 8080:80

# Posts App
kubectl port-forward service/posts-app-service 8081:80

# Offers App
kubectl port-forward service/offers-app-service 8083:80

# Routes App
kubectl port-forward service/routes-app-service 8084:80
```

**Opción 2: Minikube Service**

```bash
# Obtener URLs de servicios
minikube service users-app-service --url
minikube service posts-app-service --url
minikube service offers-app-service --url
minikube service routes-app-service --url
```

**Opción 3: Minikube Tunnel**

```bash
# Ejecutar en terminal separado
minikube tunnel

# Luego acceder directamente a los NodePorts
curl http://localhost:30001/users/ping
```

## Despliegue en Kubernetes

### Configuración de Producción

1. **Configurar Registry de Imágenes**

   ```bash
   # Tag imágenes para registry
   docker tag users-app:v1.0.0 your-registry/users-app:v1.0.0
   docker tag posts-app:v1.0.0 your-registry/posts-app:v1.0.0
   docker tag offers-app:v1.0.0 your-registry/offers-app:v1.0.0
   docker tag routes-app:v1.0.0 your-registry/routes-app:v1.0.0

   # Push a registry
   docker push your-registry/users-app:v1.0.0
   docker push your-registry/posts-app:v1.0.0
   docker push your-registry/offers-app:v1.0.0
   docker push your-registry/routes-app:v1.0.0
   ```

2. **Actualizar Manifests**

   - Modificar las referencias de imagen en los archivos YAML
   - Configurar variables de entorno de producción
   - Ajustar recursos y límites

3. **Aplicar Configuración**
   ```bash
   kubectl apply -f k8s/
   ```

### Monitoreo y Logs

```bash
# Ver logs de aplicaciones
kubectl logs -f deployment/users-app-deployment
kubectl logs -f deployment/posts-app-deployment
kubectl logs -f deployment/offers-app-deployment
kubectl logs -f deployment/routes-app-deployment

# Ver logs de bases de datos
kubectl logs -f deployment/users-db-deployment
kubectl logs -f deployment/posts-db-deployment
kubectl logs -f deployment/offers-db-deployment
kubectl logs -f deployment/routes-db-deployment

# Verificar estado de pods
kubectl get pods -o wide
kubectl describe pod <pod-name>
```

## Testing

### Ejecutar Tests Unitarios

```bash
# Users App
cd users_app
python -m pytest test/ -v --cov=.

# Posts App
cd posts_app
python -m pytest test/ -v --cov=.

# Offers App
cd offers_app
python -m pytest test/ -v --cov=.

# Routes App
cd routes_app
python -m pytest test/ -v --cov=.
```

### Testing de APIs

```bash
# Usar Postman Collections
# Ubicadas en: test/api/ de cada aplicación
```

## Comandos Útiles

### Gestión de Minikube

```bash
# Iniciar clúster
minikube start

# Detener clúster
minikube stop

# Eliminar clúster
minikube delete

# Ver estado
minikube status

# Abrir dashboard
minikube dashboard
```

### Gestión de Kubernetes

```bash
# Ver todos los recursos
kubectl get all

# Ver pods específicos
kubectl get pods -l app=users-app

# Eliminar recursos
kubectl delete -f k8s/users_app.yaml

# Ver logs en tiempo real
kubectl logs -f <pod-name>

# Ejecutar comando en pod
kubectl exec -it <pod-name> -- /bin/bash
```

### Limpieza

```bash
# Eliminar todos los recursos
kubectl delete all --all

# Eliminar deployments específicos
kubectl delete deployment users-app-deployment
kubectl delete deployment posts-app-deployment
kubectl delete deployment offers-app-deployment
kubectl delete deployment routes-app-deployment
```

## Troubleshooting

### Problemas Comunes

1. **Pods no inician**

   ```bash
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

2. **Problemas de conectividad**

   ```bash
   # Verificar servicios
   kubectl get services
   kubectl describe service <service-name>

   # Verificar network policies
   kubectl get networkpolicies
   ```

3. **Problemas de base de datos**

   ```bash
   # Verificar logs de base de datos
   kubectl logs -f deployment/users-db-deployment

   # Verificar variables de entorno
   kubectl describe pod <db-pod-name>
   ```

### Logs y Debugging

```bash
# Ver logs de todos los pods
kubectl logs -l app=users-app

# Ver eventos del namespace
kubectl get events --sort-by='.lastTimestamp'

# Verificar configuración de red
kubectl get networkpolicies
kubectl describe networkpolicy users-app-network-policy
```

## Documentación Adicional

- [Documentación Técnica Completa](docs/README.md)
- [Vista de Información](docs/information-view.md)
- [Vista Funcional](docs/functional-view.md)
- [Vista de Despliegue](docs/deployment-view.md)
- [Vista de Desarrollo](docs/development-view.md)

## Contribución

1. Crear una rama para tu feature
2. Hacer cambios y commits
3. Ejecutar tests localmente
4. Crear Pull Request
5. Esperar revisión y aprobación

## Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.
