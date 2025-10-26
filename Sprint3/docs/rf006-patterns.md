# Patrones de Solución RF-006

## Requerimiento RF-006: Almacenar Tarjetas de Crédito

### Patrón 1: Polling Pattern

| Aspecto | Descripción |
|---------|-------------|
| **Requerimiento** | RF-006 |
| **Patrón utilizado** | Polling Pattern |
| **Justificación** | TrueNative requiere consultas activas para obtener el estado de verificación de tarjetas (no ofrece webhook para tarjetas). Este patrón permite verificar el estado de manera asíncrona sin bloquear la respuesta inicial al usuario. |
| **Atributos de calidad favorecidos** | Disponibilidad (no depende de webhooks externos), Tolerancia a fallos (resistente a fallos temporales), Simplicidad (implementación directa) |
| **Atributos de calidad desfavorecidos** | Eficiencia (consultas periódicas innecesarias), Latencia (retraso hasta próximo polling), Escalabilidad (incremento lineal de consultas) |
| **Componentes involucrados** | Card Poller Service (CP-SRV), TrueNative Service (TN-SRV), Credit Cards DB, Email Notification Service (EN-SRV) |

### Patrón 2: Circuit Breaker Pattern

| Aspecto | Descripción |
|---------|-------------|
| **Requerimiento** | RF-006 |
| **Patrón utilizado** | Circuit Breaker Pattern |
| **Justificación** | TrueNative es un servicio externo que puede fallar o volverse lento. El Circuit Breaker previene cascadas de fallos y permite degradación controlada cuando el servicio externo no está disponible. |
| **Atributos de calidad favorecidos** | Disponibilidad (sistema continúa con servicios externos fallidos), Resiliencia (recuperación automática), Performance (evita timeouts largos) |
| **Atributos de calidad desfavorecidos** | Funcionalidad (operaciones incompletas durante fallos), Complejidad (lógica adicional de estados) |
| **Componentes involucrados** | Card Verification Service (CV-SRV), TrueNative Service (TN-SRV) |

### Patrón 3: Asynchronous Processing Pattern

| Aspecto | Descripción |
|---------|-------------|
| **Requerimiento** | RF-006 |
| **Patrón utilizado** | Asynchronous Processing Pattern |
| **Justificación** | La verificación de tarjetas puede tomar hasta 30 segundos. El procesamiento asíncrono permite responder inmediatamente al usuario mientras la verificación ocurre en background, mejorando la experiencia de usuario. |
| **Atributos de calidad favorecidos** | Responsividad (respuesta inmediata), Throughput (procesamiento concurrente), Escalabilidad (desacopla respuesta de tiempo de procesamiento) |
| **Atributos de calidad desfavorecidos** | Consistencia (estado eventual vs. inmediato), Complejidad (manejo de estados intermedios y notificaciones asíncronas) |
| **Componentes involucrados** | Credit Cards API (CC-API), Card Verification Service (CV-SRV), Card Poller Service (CP-SRV), Email Notification Service (EN-SRV) |

### Patrón 4: Event-Driven Architecture Pattern

| Aspecto | Descripción |
|---------|-------------|
| **Requerimiento** | RF-006 |
| **Patrón utilizado** | Event-Driven Architecture Pattern |
| **Justificación** | Los cambios de estado de tarjetas deben disparar notificaciones por email. La arquitectura dirigida por eventos permite desacoplar la detección de cambios de estado de las acciones consecuentes. |
| **Atributos de calidad favorecidos** | Desacoplamiento (productores y consumidores independientes), Extensibilidad (fácil agregar nuevos manejadores), Reactividad (respuesta automática a cambios) |
| **Atributos de calidad desfavorecidos** | Complejidad (debugging y trazabilidad más difícil), Consistencia (posibles eventos perdidos o duplicados) |
| **Componentes involucrados** | Card Poller Service (CP-SRV), Email Notification Service (EN-SRV), Credit Cards DB |

### Patrón 5: Template Method Pattern

| Aspecto | Descripción |
|---------|-------------|
| **Requerimiento** | RF-006 |
| **Patrón utilizado** | Template Method Pattern |
| **Justificación** | Las notificaciones por email requieren diferentes templates según el resultado (APROBADA/RECHAZADA) pero comparten estructura común. Este patrón permite reutilizar código común mientras personaliza el contenido específico. |
| **Atributos de calidad favorecidos** | Reutilización (código común compartido), Mantenibilidad (cambios centralizados), Consistencia (formato uniforme en notificaciones) |
| **Atributos de calidad desfavorecidos** | Flexibilidad (estructura rígida puede limitar customización específica) |
| **Componentes involucrados** | Email Notification Service (EN-SRV) |