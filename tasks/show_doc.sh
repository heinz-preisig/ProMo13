#!/bin/bash

cd ../packages/Common/

programs=(
info_ontology_foundation_editor     #0
info_ontology_equation_editor       #1
info_graphic_object_editor          #2
info_behaviour_association_editor   #3
info_automata_editor                #4
info_typed_token_editor             #5
info_modeller_editor                #6
)


label=( "foundation"
        "equations"
        "components"
        "linker"
        "automaton"
        "typedtoken"
        "modeller"
)

echo "" ;
echo "ProMo tools brief documentation" ;
echo "===============================" ;
echo "" 
echo "Get information on what program ?";

for prog in "${label[@]}"; do
  echo "-    $prog" ;
done 
read prog


valid=1;

case $prog in 

  "foundation")
  prog=0 ;;
  
  "equations")
  prog=1 ;;
  
  "componets")
  prog=2 ;;
  
  "linker")
  prog=3 ;;
  
  "automaton")
  prog=4 ;;
  
  "typedtoken")
  prog=5 ;; 
  
  "modeller")
  prog=6 ;;
  
  *)
  valid=0 ;;
      
esac


case $valid in
  0)
  exit ;;
  
  1)
    #echo "start program" "${programs[$prog]}"  ;
    $1 "${programs[$prog]}.pdf" ;;
esac


