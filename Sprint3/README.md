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

- [Dashboard de Tareas](https://github.com/orgs/MISW-4301-Desarrollo-Apps-en-la-Nube/projects/266)
- [Documentación Técnica](https://fluffy-funicular-z25pk9p.pages.github.io/)

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
├── credit_cards_app/           # Microservicio de tarjetas de crédito (RF-006)
├── libs/                       # Librerías compartidas
│   └── notifications/          # Servicio de notificaciones por email
└── terraform/                  # Infraestructura como código
    ├── deploy.sh
    ├── environments/
    ├── modules/
    └── stacks/
```

## Microservicios

El sistema utiliza **Ingress Controller** para enrutar tráfico a servicios internos via ClusterIP. Todos los servicios son accesibles a través del Ingress con rutas específicas.

### Aggregator Service (Orquestador)

- **Rutas Ingress**: `/rf003/*`, `/rf004/*`, `/rf005/*`, `/` (default)
- **Puerto interno**: 80 (ClusterIP) → 5000 (container)
- **Funcionalidades**: Orquestación de RF-003, RF-004 y RF-005
- **Endpoints clave**:
  - `POST /rf003/posts` - Crear publicación compuesta
  - `POST /rf004/posts/{id}/offers` - Crear oferta con score
  - `GET /rf005/posts/{id}` - Consultar publicación agregada

### Users App

- **Ruta Ingress**: `/users/*`
- **Puerto interno**: 80 (ClusterIP) → 5000 (container)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Registro, autenticación, gestión de usuarios, **verificación de identidad (RF-007)**
- **Nuevas características**: Verificación automática de identidad con TrueNative, estados de usuario, restricción de acceso
- [Documentación detallada](users_app/README.md)

### Posts App

- **Ruta Ingress**: `/posts/*`
- **Puerto interno**: 80 (ClusterIP) → 5000 (container)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Creación, consulta, eliminación de publicaciones
- [Documentación detallada](posts_app/README.md)

### Offers App

- **Ruta Ingress**: `/offers/*`
- **Puerto interno**: 80 (ClusterIP) → 5000 (container)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Gestión de ofertas de transporte
- [Documentación detallada](offers_app/README.md)

### Routes App

- **Ruta Ingress**: `/routes/*`
- **Puerto interno**: 80 (ClusterIP) → 5000 (container)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Gestión de rutas de viaje
- [Documentación detallada](routes_app/README.md)

### Scores App

- **Ruta Ingress**: `/score/*`
- **Puerto interno**: 80 (ClusterIP) → 5000 (container)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: Gestión de puntajes (scores) de ofertas
- **Integración**: Best-effort con Aggregator para RF-004

### Credit Cards App (RF-006)

- **Ruta Ingress**: `/credit-cards/*`
- **Puerto interno**: 80 (ClusterIP) → 5000 (container)
- **Base de datos**: PostgreSQL
- **Funcionalidades**: **Registro y verificación de tarjetas de crédito**
- **Características**: Verificación asíncrona con TrueNative, polling de estados, notificaciones por email
- [Documentación detallada](credit_cards_app/README.md)

### TrueNative Service

- **Ruta Ingress**: `/native/*`
- **Puerto interno**: 80 (ClusterIP) → 3000 (container)
- **Tipo**: Servicio externo de verificación
- **Funcionalidades**: Verificación de identidad y tarjetas de crédito

## Servicios de Soporte

### Producer Service

- **Ruta Ingress**: `/producer/*`
- **Puerto interno**: 80 (ClusterIP) → 80 (container)
- **Funcionalidades**: Generación y envío de mensajes a colas SQS
- **Uso**: Soporte para procesamiento asíncrono de verificaciones

### Publisher Service

- **Ruta Ingress**: `/publisher/*`
- **Puerto interno**: 80 (ClusterIP) → 80 (container)
- **Funcionalidades**: Publicación de eventos y notificaciones
- **Uso**: Sistema de eventos para RF-006 y RF-007

### Consumer Service

- **Puerto interno**: 5000 (container, sin Ingress)
- **Funcionalidades**: Procesamiento de mensajes de colas
- **Uso**: Procesamiento asíncrono de verificaciones de tarjetas

### Subscriber Service

- **Puerto interno**: 5000 (container, sin Ingress)
- **Funcionalidades**: Suscripción y procesamiento de eventos
- **Uso**: Manejo de eventos de verificación de usuarios

### Addition/Multiplication Services

- **Funcionalidades**: Servicios de cálculo matemático
- **Uso**: Soporte computacional para cálculos de scores y utilidades
- **Endpoints**: `/native/*`
- **Configuración**: Token secreto, variables de entorno para testing

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
# Desplegar TrueNative (requerido para RF-006 y RF-007)
kubectl apply -f k8s/k8s-true-native-deployment.yaml

# Desplegar Users App (incluye RF-007)
kubectl apply -f k8s/real_users_deployment.yaml

# Desplegar Posts App
kubectl apply -f k8s/real_posts_deployment.yaml

# Desplegar Offers App
kubectl apply -f k8s/real_offers_deployment.yaml

# Desplegar Routes App
kubectl apply -f k8s/real_routes_deployment.yaml

# Desplegar Credit Cards App (RF-006)
kubectl apply -f k8s/real_credit_cards_deployment.yaml

# Desplegar Ingress completo
kubectl apply -f k8s/complete_ingress.yaml
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
# Users App (incluye RF-007)
kubectl port-forward service/users-app-service 8080:80

# Posts App
kubectl port-forward service/posts-app-service 8081:80

# Offers App
kubectl port-forward service/offers-app-service 8083:80

# Routes App
kubectl port-forward service/routes-app-service 8084:80

# Credit Cards App (RF-006)
kubectl port-forward service/credit-cards-service 8086:80

# TrueNative Service
kubectl port-forward service/service-truenative 8087:80
```

**Endpoints Disponibles:**

Una vez desplegado, los siguientes endpoints estarán disponibles:

- `https://<host>/users/*` - Gestión de usuarios y verificación de identidad (RF-007)
- `https://<host>/posts/*` - Gestión de publicaciones
- `https://<host>/offers/*` - Gestión de ofertas
- `https://<host>/routes/*` - Gestión de rutas
- `https://<host>/credit-cards/*` - Gestión de tarjetas de crédito (RF-006)
- `https://<host>/native/*` - TrueNative API para verificaciones

**Nuevos endpoints RF-006:**

- `POST /credit-cards` - Registrar tarjeta de crédito
- `GET /credit-cards` - Consultar tarjetas del usuario
- `GET /credit-cards/count` - Contador de entidades
- `GET /credit-cards/ping` - Health check

**Nuevos endpoints RF-007:**

- `POST /users` - Registro con verificación automática
- `POST /users/auth` - Autenticación (solo usuarios verificados)
- `PATCH /users/webhook/verify` - Webhook para TrueNative
- `GET /users/verify-token` - Validación de tokens

#### Opción 2: Minikube Service

```bash
# Obtener URLs de servicios
minikube service users-app-service --url
minikube service posts-app-service --url
minikube service offers-app-service --url
minikube service routes-app-service --url
```

#### Opción 3: Minikube Tunnel

```bash
# Ejecutar en terminal separado
minikube tunnel

# Luego acceder directamente a los NodePorts
curl http://localhost:30001/users/ping
```

## Despliegue en AWS con Terraform y EKS

Esta sección describe cómo provisionar la infraestructura en AWS (EKS, SQS, SNS, Lambdas) y luego desplegar los manifiestos Kubernetes de los microservicios.

### Arquitectura Provisionada

Recursos creados por Terraform (stack `apps`):

- Cluster EKS (`module.eks_cluster`)
- SQS Queue (`module.sqs_queue`)
- Lambda Consumer + Event Source Mapping (SQS -> Lambda)
- SNS Topic + Lambda Subscriber (permiso `aws_lambda_permission`)
- (Módulos adicionales disponibles: `repository`, `lambda`, `sns`, `sqs`)

### Prerrequisitos

1. Cuenta AWS con credenciales configuradas (Access Key / Secret o SSO) y permisos para EKS, IAM, EC2, Lambda, SQS, SNS.
2. AWS CLI instalado y autenticado:

   ```bash
   aws sts get-caller-identity
   ```

3. Terraform >= 1.5 (ver `.terraform-version`).
4. kubectl instalado.
5. Opcional: `aws eks update-kubeconfig` permisos para escribir en kubeconfig.

### Estructura Terraform

```text
terraform/
├── deploy.sh                 # Script helper (init/plan/apply stack apps)
├── stacks/
│   └── apps/                 # Stack principal (EKS + colas + lambdas + sns)
├── modules/                  # Módulos reutilizables
│   ├── eks/                  # Creación de cluster EKS
│   ├── sqs/                  # Cola SQS
│   ├── sns/                  # Tópico SNS
│   ├── lambda/               # Funciones Lambda
│   └── repository/           # (si se requiere repos ECR)
└── environments/
    └── student/
        └── apps/terraform.tfvars  # Variables para el entorno
```

### Variables Clave (`environments/student/apps/terraform.tfvars`)

| Variable                        | Ejemplo                    | Descripción                |
| ------------------------------- | -------------------------- | -------------------------- |
| `region`                        | us-east-1                  | Región AWS                 |
| `cluster_name`                  | dann-cluster               | Nombre del cluster EKS     |
| `k8s_cluster_version`           | 1.33                       | Versión Kubernetes deseada |
| `queue_name`                    | producer-consumer-queue    | Nombre de la cola SQS      |
| `topic_name`                    | publisher-subscriber-topic | Nombre del tópico SNS      |
| `number_of_messages_to_process` | 2                          | Batch size Lambda consumer |

Lambdas: `consumer_config`, `subscriber_config` incluyen nombre, repo y variables de entorno.

### Uso rápido con Makefile (Terraform)

```bash
# Inicializar terraform (si no se ha hecho)
make terraform-init
# Plan estándar
make terraform-plan
# Aplicar cambios
make terraform-apply
# Plan con imágenes locales :latest
make terraform-plan-local
# Aplicar con imágenes locales
make terraform-apply-local
# Destruir
make terraform-destroy
```

### Flujo de Provisionamiento

1. Clonar repositorio y situarse en carpeta Terraform:
   ```bash
   cd terraform
   ```
2. (Opcional) Ajustar variables en `environments/student/apps/terraform.tfvars`.
3. Inicializar (solo primera vez o tras cambiar providers):
   ```bash
   cd stacks/apps
   terraform init -upgrade
   ```
4. Planificar:
   ```bash
   terraform plan -var-file="../../environments/student/apps/terraform.tfvars"
   ```
5. Aplicar:
   ```bash
   terraform apply -auto-approve -var-file="../../environments/student/apps/terraform.tfvars"
   ```

### Acceso al Cluster EKS

Una vez creado el cluster, actualizar el kubeconfig:

```bash
aws eks update-kubeconfig --region us-east-1 --name dann-cluster
kubectl get nodes
```

### Despliegue de Microservicios en EKS

Después de tener credenciales y contexto apuntando al nuevo cluster (o tras `make k8s-config`):

```bash
kubectl apply -f k8s/aggregator_deployment.yaml
kubectl rollout status deployment/aggregator-app

# (Aplicar el resto de manifests si corresponde)
kubectl apply -f k8s/
```

Verificar y logs:

```bash
kubectl get pods -o wide
kubectl logs -f deployment/aggregator-app
```

### Actualizaciones

Modificar variables en `terraform.tfvars` y volver a ejecutar `terraform plan` / `terraform apply`.

### Destrucción de Infraestructura (CUIDADO)

```bash
cd terraform/stacks/apps
terraform destroy -var-file="../../environments/student/apps/terraform.tfvars"
```

### Buenas Prácticas

- Revisar versiones de módulos (`eks` actualmente usa `terraform-aws-modules/eks` ~> 18.31).
- Mantener versionado de `terraform.lock.hcl` bajo control de cambios.
- Usar workspaces o carpetas `environments/` para separar dev / prod.
- Evitar `cluster_endpoint_public_access = true` en producción sin restricciones de red.

### Troubleshooting Terraform/EKS

| Problema                     | Causa Común         | Solución                                                          |
| ---------------------------- | ------------------- | ----------------------------------------------------------------- |
| Error IAM en creación de EKS | Roles no existentes | Validar ARNs en `locals.tf` del módulo EKS                        |
| Nodo no se une               | Seguridad / SG      | Revisar reglas adicionales `node_security_group_additional_rules` |
| `kubectl` Unauthorized       | aws-auth            | Confirmar configuración de `aws_auth_roles` y credenciales        |
| Timeout en plan/apply        | Límites de cuenta   | Verificar cuotas EC2/VPC                                          |

---

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

# Destruir

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
