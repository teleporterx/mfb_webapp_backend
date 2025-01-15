# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the pyproject.toml and poetry.lock files first to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install Poetry and create a virtual environment, then install dependencies
RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry install

# Set environment variables for the virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Set default values for RabbitMQ and MongoDB host (this can be overridden in docker-compose or environment files)
ENV MONGO_URL=mongoose

# Copy the 'api' directory into the container
COPY api /app/api
COPY main.py /app/main.py

# Expose the port the app will run on
EXPOSE 8000

# Run the application using Uvicorn, inside the virtual environment
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]