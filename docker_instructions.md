
**Pre-requisites**
make a docker group
sudo usermod -a -G docker $USER

**building the docker image**
docker build -t  promo .

**running the docker image**
docker run --rm -it  --net=host   -v /home/heinz/1_Gits/CAM/Ontology_Repository:/Ontology_Repository promo_3 python3 ProMo_OntologyFoundationDesigner.py

the -v <local repository> <related docker repository>
 