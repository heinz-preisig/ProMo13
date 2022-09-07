# !/bin/sh

# generate git for ontology branch
# needs to run in ontology branch's root directory
dat=$(  date +'%Y-%m-%d %H:%M' ) ;
direc=$( basename $PWD ) ;

git init ;
git add . ;
git commit . -m"new ontology $direc $dat" ;




