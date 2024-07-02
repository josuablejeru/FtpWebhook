# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  curl \
  libffi-dev \
  libssl-dev \
  && rm -rf /var/lib/apt/lists/*


# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"

# Copy the pyproject.toml and poetry.lock files (if you have one)
COPY pyproject.toml poetry.lock* ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copy the rest of your application's code
COPY . .

EXPOSE 21
EXPOSE 50000-50010

# Run your Python command
CMD ["python", "app/ftp_server.py", "--help"]