FROM python:3.11-slim as base
# Set labels
LABEL course="dann" \
      author="ca.forero10@uniandes.edu.co"
WORKDIR /app
ARG POETRY_VERSION=2.1.1
RUN pip install poetry==$POETRY_VERSION
COPY poetry.lock pyproject.toml ./
COPY src/ src/
# Install all the dependencies directly on the container
RUN poetry config virtualenvs.create false
# Install no dev dependencies
RUN poetry install --only main

FROM python:3.11-slim as runner
WORKDIR /app
# Create a non-root user
RUN groupadd -r noroot && useradd -r -g noroot noroot
# Copy only the necessary files from base
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin
# Copy application code
COPY --from=base /app/src/ /app/src/
# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
# Set proper permissions
RUN chown -R noroot:noroot /app
# Switch to non-root user
USER noroot
# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]