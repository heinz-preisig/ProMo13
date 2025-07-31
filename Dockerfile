# Stage 1: Build environment
FROM ubuntu:24.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12 and required build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    python3-full \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip in the virtual environment
RUN pip install --upgrade pip



# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install PyQt5 in the virtual environment
RUN pip3 install --no-cache-dir PyQt5

COPY requirements.txt .
RUN pip install -r requirements.txt

# Stage 2: Runtime environment
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.12 and runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-dev \
    # Graphics and UI dependencies
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
    ibus \
    # Documentation and graphics
    graphviz \
    texlive-science \
    texlive-latex-extra \
    dvipng \
    imagemagick \
    # Core libraries
    libssl3 \
    libffi8 \
    zlib1g \
    libsqlite3-0 \
    liblzma5 \
    libbz2-1.0 \
    libncursesw6 \
    libtinfo6 \
    libreadline8 \
    libgdbm6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set environment variables for virtual environment
ENV PATH="/opt/venv/bin:$PATH"
    


# Set Qt plugin path and other environment variables
ENV QT_QPA_PLATFORM_PLUGIN_PATH=/opt/venv/lib/python3.10/site-packages/PyQt5/Qt5/plugins


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
