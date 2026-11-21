# Production Container for Zero-Budget AI Video Studio & HyperFrames Renderer
FROM python:3.11-slim-bookworm AS production

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8000 \
    PUPPETEER_ARGS="--no-sandbox --disable-setuid-sandbox"

WORKDIR /app

# 1. Install system utilities, FFmpeg, fonts, and browser runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    ffmpeg \
    fonts-dejavu-core \
    fonts-noto-cjk \
    ca-certificates \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libasound2 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Node.js 20 LTS & npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g npm@latest \
    && npx -y hyperframes@0.9.72 --version \
    && rm -rf /var/lib/apt/lists/*

# 3. Create non-root production user and set up workspace
RUN useradd -m -u 1000 -s /bin/bash appuser \
    && mkdir -p /app/data/audio /app/data/renders /app/data/assets /app/backend \
    && chown -R appuser:appuser /app

# 4. Install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 5. Copy backend source code
COPY backend /app/backend

# Set proper ownership for all application files
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
