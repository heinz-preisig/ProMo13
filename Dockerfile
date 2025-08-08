# Stage 1: Build environment
FROM python:3.12-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.12-slim

# Install runtime dependencies
    # Graphics and UI dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libxext6 \
    libx11-6 \
    libxkbcommon-x11-0 \
    libsm6 \
    libice6 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-shm0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libx11-xcb1 \
    libglib2.0-0 \
    libdbus-1-3 \
    libxkbcommon0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

    # Documentation and graphics
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-science \
    texlive-latex-extra \
    dvipng \
    imagemagick \
    evince \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"
ENV QT_QPA_PLATFORM_PLUGIN_PATH="/opt/venv/lib/python3.12/site-packages/PyQt5/Qt5/plugins"

# Create a non-root user
RUN useradd -m appuser
# X11 forwarding setup
ENV DISPLAY=:0
ENV QT_X11_NO_MITSHM=1
ENV QT_QPA_PLATFORM=xcb
ENV XDG_RUNTIME_DIR=/tmp/runtime-appuser

RUN mkdir "Ontology_Repository"
WORKDIR /ProMo
COPY ./tasks/ tasks/
COPY ./packages/ packages/
COPY ./src/ src/
COPY ./tools/ tools/
COPY ./constants.py constants.py
COPY ./static_assets static_assets/

## Set the DISPLAY environment variable
ENV XDG_RUNTIME_DIR="/ProMo/tasks/"
RUN chmod 0700 /ProMo/tasks

RUN chmod +x tasks/*.sh

WORKDIR /ProMo/tasks
#CMD ["bash", "cd /ProMo/tasks"]
CMD ["python3", "run.py"]
