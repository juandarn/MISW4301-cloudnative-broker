# Use Python base image compatible with Lambda
FROM python:3.11-slim

# Set labels
LABEL course="dann" \
      author="ca.forero10@uniandes.edu.co"

# Set working directory
WORKDIR /var/task

# Install poetry
ARG POETRY_VERSION=2.1.1
RUN pip install poetry==$POETRY_VERSION

# Copy dependency files
COPY poetry.lock pyproject.toml ./

# Copy source code
COPY src/ src/

# Install dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --only main

# Create lambda handler
RUN echo 'import sys; sys.path.append("/var/task/src"); from entrypoints.topic.main import handler' > /var/task/lambda_function.py

# Set the CMD to your handler
CMD ["python", "/var/task/lambda_function.py"]