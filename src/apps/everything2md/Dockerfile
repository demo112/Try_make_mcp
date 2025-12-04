FROM python:3.10-slim-bullseye

# Set timezone
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies
# libreoffice-headless: for office doc conversion
# pandoc: for html/csv -> markdown
# fonts-noto-cjk: for Chinese font support
# tini: for proper signal handling
RUN apt-get update && apt-get install -y \
    libreoffice-headless \
    libreoffice-java-common \
    pandoc \
    fonts-noto-cjk \
    tini \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage cache
COPY src/apps/everything2md/requirements.txt .

# Install Python dependencies
# Use a mirror if needed, but for global accessibility we use default pypi or allow config via build args
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
# We copy the entire src tree to preserve package structure if imports need it
COPY src /app/src

# Set environment variables
ENV PYTHONPATH=/app
ENV LIBREOFFICE_PATH=soffice
ENV PANDOC_PATH=pandoc

# Default Path Mapping (Can be overridden at runtime)
# Example for Windows Docker Desktop
ENV HOST_ROOT="C:/"
ENV CONTAINER_ROOT="/mnt/c/"

# Entrypoint using Tini
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run the server
CMD ["python", "src/apps/everything2md/server.py"]
