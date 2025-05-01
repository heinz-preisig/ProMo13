FROM ubuntu:22.04

LABEL authors="heinz <heinz.preisig@chemeng.ntnu.no>"

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /ProMo

# Install Python 3, PyQt5
RUN apt-get update && apt-get install -qq -y \
#	python3-pyqt5 \
#    python3-pyqt5sip \
    graphviz \
#	texlive okular \
	texlive-science \
	texlive-latex-extra \
	dvipng\
	imagemagick\
	libcanberra-gtk-module \
	libcanberra-gtk3-module \
	python3-simplejson \
	python3-ujson \
	python3-pip \
    xvfb \
    libglu1-mesa-dev \
    libx11-xcb-dev \
    '^libxcb*' \
    libxcb-cursor-dev \
    libxkbcommon-dev \
    libxkbcommon-x11-dev \
    libgl1-mesa-glx \
    libxcb-cursor0 \
   && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install -r requirements.txt
#RUN apt-get update && apt-get install -y pyqt5-sip

WORKDIR /ProMo
COPY ./tasks/ tasks/
COPY ./packages/ packages/
COPY ./src/ src/


## Set the DISPLAY environment variable
#ENV DISPLAY=:
#
## Start Xvfb before running the Qt application
#CMD ["Xvfb", ":99", "-screen", "0", "1024x768x24", "&", "promo"]
#
## Mount the host machine's X11 socket
#RUN mkdir -p /tmp/.X11-unix
VOLUME /tmp/.X11-unix

# Set the DISPLAY environment variable
ENV DISPLAY=:0
ENV XDG_RUNTIME_DIR="/ProMo/tasks/"
RUN chmod 0700 /ProMo/tasks

# Allow the container to connect to the host machine's display
#CMD ["your_qt_application"]

ENV QT_QPA_PLATFORM=xcb

RUN chmod +x tasks/task.sh


#EXPOSE 8000

WORKDIR /ProMo/tasks
CMD ["bash", "task.sh"]