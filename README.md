# ☁️ CloudNative – Package Delivery Broker (MISW-4301)

> Academic project developed for the course **Desarrollo de Aplicaciones Nativas en la Nube (MISW-4301)**  
> Universidad de los Andes – 2025  
> Team project – 4 members

---

## 🧭 Introduction

This repository contains the implementation of the **Package Delivery Broker**, an academic project that simulates a **collaborative logistics platform** for parcel delivery.  
The project applies **cloud-native principles**, using **microservices architecture**, **containerization**, and **orchestration** to deploy scalable and resilient applications.

The platform allows users to act in two roles:

- **Lessor (Arrendador)** – a user who wants to send a package using the available luggage space of another traveler.  
- **Lessee (Arrendatario)** – a traveler who offers space in their luggage in exchange for an economic benefit.

Both users benefit from the transaction, and the company takes a commission for acting as the intermediary.

---

## 💼 Business Model

The goal of the platform is to become a competitive alternative in the **delivery and logistics** sector through a **collaborative economy model**.

Users can:
- Publish trips with available luggage space (*Publicaciones*).  
- Make offers (*Ofertas*) to ship packages along a trip route (*Trayecto*).  
- Calculate an estimated **profit or utility (score)** for each offer using:

$$
\text{Utility} = \text{Offer Amount} - \big(\text{Luggage Occupation}\ \% \times \text{Luggage Value}\big)
$$

| Package Size | Luggage Occupation |
|---------------|-------------------|
| LARGE | 100% |
| MEDIUM | 50% |
| SMALL | 25% |

This initial version focuses on the backend services, cloud deployment, and integration pipelines, leaving user interaction external to the app.

---

## 🚀 Project Objectives

- Design and deploy a **cloud-native application** using microservices.  
- Apply **containerization (Docker)** and **orchestration (Kubernetes / Docker Compose)**.  
- Incorporate **CI/CD pipelines** for automated testing and deployment.  
- Use **serverless services and event-driven patterns** in the final stage.  
- Ensure scalability, extensibility, resilience, and availability.

---

## 🧩 Technologies and Tools

| Category | Technologies |
|-----------|--------------|
| **Backend** | Python, Flask, SQLAlchemy |
| **Databases** | PostgreSQL / MongoDB (depending on microservice) |
| **Containerization** | Docker |
| **Orchestration** | Kubernetes / Docker Compose |
| **Serverless (Entrega 3)** | Cloud Functions / AWS Lambda |
| **Messaging** | Cloud Pub/Sub / RabbitMQ |
| **Continuous Integration** | GitHub Actions, Jenkins |
| **Documentation** | GitHub Wiki, Markdown |
| **Project Management** | GitHub Projects |

---

## 📅 Deliverables Schedule

| Delivery | Week | Description |
|-----------|-------|-------------|
| **Entrega 1** | Week 3 | Build the first local version using containerization and orchestration tools. |
| **Entrega 2** | Week 6 | Apply design patterns and integrate new components and technologies. |
| **Entrega 3** | Week 8 | Add serverless components and event-driven architecture features. |

---

## 🏗️ System Architecture (Overview)

The system follows a **microservices-based architecture**, where each service is deployed independently:

```

cloudnative-broker/
│
├── user-service/          # Manages user profiles and roles
├── trip-service/          # Manages trips and routes (trayectos)
├── offer-service/         # Handles package offers and calculations
├── gateway-service/       # API Gateway for routing
├── notification-service/  # Event-driven notifications (Entrega 3)
├── scripts/               # Deployment and orchestration files
└── ci/                    # CI/CD configuration (GitHub Actions, Jenkins)

```

---

## 🧪 Testing and CI/CD

Each microservice includes:
- Unit and integration tests with `unittest` or `pytest`.
- Continuous integration pipelines with **GitHub Actions** for:
  - Linting and testing.
  - Docker image build and push.
  - Deployment to a container registry or cluster.

---

## 🌩️ Cloud Deployment

The final system will be deployed using a **cloud provider** (AWS, GCP, or Azure) and will include:
- Container orchestration (Kubernetes or GKE).  
- Serverless event triggers (Cloud Functions / Lambda).  
- Cloud-hosted databases and messaging services.  

---

## 👥 Team Members

| Full Name | GitHub Username |
|------------|------------------|
| **Juan David Rios** | [@juandarn](https://github.com/juandarn) |
| **Laura Carretero** | [@lauths12](https://github.com/lauths12) |
| **Franklin Romero** | [@FranklinSRomero](https://github.com/FranklinSRomero) |
| **Hector Lopez** | [@hector-lopez-wizeline](https://github.com/hector-lopez-wizeline) |

---

## 📘 Course Information

**Course:** Desarrollo de Aplicaciones Nativas en la Nube (MISW-4301)  
**Institution:** Universidad de los Andes  
**Year:** 2025  

---

## 📄 License

Academic use only — Project developed as part of the MISW-4301 course.  
All rights reserved to the authors and Universidad de los Andes.
```
