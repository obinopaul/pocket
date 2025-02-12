# Use an official Python runtime as a parent image
FROM python:3.11.5-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# this was added newly.
ENV HOME="/root"
ENV PATH="/usr/lib/libreoffice/program:${PATH}"

# Install system dependencies (including HTTPS certificates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev \
    libreoffice \
    libreoffice-writer \
    libreoffice-java-common \
    default-jre \
    ca-certificates \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Create and set permissions for the results directory
RUN mkdir -p /app/static/results && \
    chmod -R 777 /app/static/results

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies without caching
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make sure temp directory exists and has proper permissions
RUN mkdir -p /tmp && chmod 777 /tmp

# Expose the port the app runs on
EXPOSE 10000

# Command to run the app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]




# # Use an official lightweight Python runtime
# FROM python:3.11.5-slim

# # Set environment variables
# ENV PYTHONUNBUFFERED=1

# # Install system dependencies (including HTTPS certificates)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libssl-dev \
#     libreoffice \
#     ca-certificates \
#     && rm -rf /var/lib/apt/lists/*

# # Create a non-root user
# RUN useradd --create-home --shell /bin/bash appuser

# # Set working directory (after creating the user)
# WORKDIR /app

# # Change ownership of the working directory
# RUN chown -R appuser:appuser /app

# # Switch to the non-root user
# USER appuser

# # Copy only requirements first to leverage Docker caching
# COPY requirements.txt .

# # Install Python dependencies without caching
# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt

# # Copy the rest of the application code
# COPY . .

# # Expose the port (Render will dynamically map it)
# EXPOSE 10000

# # Start the app (Uses Render’s $PORT dynamically)
# CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
