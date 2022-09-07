
Process Modeller ProMod
=======================

.. image:: file: /home/heinz/1_Gits/ProcessModeller/ProcessModeller_v7_04/packages/Common/icons/ProMo_logo.svg
   :align: center
   :scale: 50
   :height: 300px





Usage
-----

.. |date| date::

:Date: 2020-02-28
:Version: 7.04
:Authors:
    - Heinz A `PREISIG`_
    - Arne Tobias `ELVE` : ModelFactory



 .. _PREISIG: https://www.ntnu.no/ansatte/heinz.a.preisig
 .. _ELVE: `<arne.t.elve(at)ntnu.no>`

Installation
------------

ProMo has been split into a set of gits for practical reasons.

 - ProMo-tasks                         -- all task, mostly editors constructed on PyQt5
 - ProMo-packages-OntologyBuilder      -- the expert's sandbox
 - ProMo-packages-ModelBuilder         -- the translator's & the model builder's sandbox
 - ProMo-packages-TaskBuilder          -- the part that builds applications, thus belongs to the model builder's sandbox
 - ProMo-packages-Common               -- utilities that are used by the various editors/tasks
 - ProMo-Model_Repository-playground   -- as it says: the model repository just and example -- will change with time

The ProMo software uses relative referencing of the differernt modules. It must currently be manually put into a
corresponding directory tree:

 - <your choice>
    - ProMo
       - packages
           - Common
           - OntologyBuilder
           - ModelBuilder
           - TaskBuilder
       - tasks
    - Ontology_Repository
    
ProMo ontologies and models
---------------------------
ProMo will ask for an ontology name to be created when starting with the ProMo_OntologyFoundationDesigner. It will generate a directory tree in the Ontology_Repository branch with the given name and a basic ontology as well as resources. As developments are going on, some structural elements and files may change with time.


Requirements
^^^^^^^^^^^^
 - PyQt5


Licence
-------
 - GPL
