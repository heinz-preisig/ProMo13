# installing ProMo  all components but not the Model_repository

# run it in the directory you want to install your project

userdirectory=CAM-projects      # users choice

mkdir $userdirectory   


cd $userdirectory

mkdir ProMo
cd ProMo

git clone git@github.com:heinz-preisig/ProMo-tasks.git
mv ProMo-tasks tasks

mkdir packages
cd packages

git clone git@github.com:heinz-preisig/ProMo-packages-Common.git
mv ProMo-packages-Common Common

git clone git@github.com:heinz-preisig/ProMo-packages-OntologyBuilder.git
mv ProMo-packages-OntologyBuilder OntologyBuilder

git clone git@github.com:heinz-preisig/ProMo-packages-ModelBuilder.git
mv ProMo-packages-ModelBuilder ModelBuilder

git clone git@github.com:heinz-preisig/ProMo-packages-TaskBuilder.git
mv ProMo-packages-TaskBuilder TaskBuilder

cd ../..
mkdir Ontology_Repository

#git clone git@github.com:heinz-preisig/ProMo-Model_Repository.git
#mv ProMo-Model_Repository Model_Repository

