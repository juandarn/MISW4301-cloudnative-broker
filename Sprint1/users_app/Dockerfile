FROM python:3.11-slim

# Evita que Python guarde archivos .pyc y mantiene logs en stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la app al contenedor
COPY . .

# Asegurar que Python incluya /app en el path
ENV PYTHONPATH=/app

# Exponer puerto de Flask
EXPOSE 5000

# Ejecutar la app con Flask
CMD ["flask", "run"]
