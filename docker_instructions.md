# Docker building and running

### **Pre-requisites**

```bash
make a docker group
sudo usermod -a -G docker $USER
```



### **Building the docker image**

```bash
docker build -t  promo .
```

for different dockerfile:

```bash
docker build -f Dockerfile -t promo .
```



### **Running the docker image**

```bash
xhost +local:docker

docker run --rm -it \
  -e DISPLAY=$DISPLAY_ENV \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v $LOCAL_ONTOLOGY_REPOSITORY:$DOKER_ONTOLOGY_REPOSITORY \
  $IMAGE_NAME
  
xhost -local:docker
```

For HAP installation:

```bash
IMAGE_NAME="promo"
LOCAL_ONTOLOGY_REPOSITORY="/home/heinz/1_Gits/CAM/Ontology_Repository"
DOKER_ONTOLOGY_REPOSITORY="/Ontology_Repository"
```





