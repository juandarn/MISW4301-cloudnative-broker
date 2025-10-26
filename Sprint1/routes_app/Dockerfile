FROM python:3.11-slim

# Evita que Python guarde archivos .pyc y mantiene logs en stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  FLASK_RUN_HOST=0.0.0.0 \
  FLASK_RUN_PORT=5000

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la app al contenedor
COPY src/ ./src

# Directorio de trabajo dentro del contenedor
WORKDIR /src

# Asegurar que Python incluya /src en el path
ENV PYTHONPATH=/src

# Exponer puerto de Flask
EXPOSE 3002

# Ejecutar la app con Flask
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
