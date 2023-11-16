#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
  commander for ModelComposer
===============================================================================
  main switch board of Process Modeller


__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2018. 09. 15"
__license__ = "GPL"
__version__ = "5.01"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

"""
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QDialog

from Common.resources_icons import roundButton
from packages.ModelBuilder.ModelComposer.variant_selection import Ui_Dialog

def extract(variants, filter_and, filter_or, filter_not):
  remove_them = set()
  for f in filter_and:
    if "solid" in f:
      print("debugging", f)
    for v in variants:
      if "solid" in v:
        print("debugging", f, v)
      if f not in v:
        remove_them.add(v)
  for f in filter_not:
    for v in variants:
      if f in v:
        remove_them.add(v)

  selection = set(variants) - remove_them
  if filter_or:
    selection_2 = []
    for v in selection:
      for f in filter_or:
        if f in v:
          selection_2.append(v)
  else:
    selection_2 = list(selection)

  return selection_2

def splitEntity(entity):
  nw, node_or_arc, info, variant = entity.split(".")
  token, mechanism, nature = info.split("|")
  return nw,node_or_arc, token, mechanism, nature, variant




class VariantGUI(QDialog):
  def __init__(self, variants):

    # super().__init__()
    super().__init__(flags=QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)


    roundButton(self.ui.pushAccept, "accept", "accept choice")
    roundButton(self.ui.pushCancel, "reject", "reject choices")

    self.variants = variants
    self.ui.comboBoxVariations.addItems(variants)

  def on_comboBoxVariations_textChanged(self,text):
    self.selection = text

  def on_pushCancel_pressed(self):
    self.selection = None
    self.close()

  def on_pushAccept_pressed(self):
    self.selection = self.ui.comboBoxVariations.currentText()
    self.close()




if __name__ == '__main__':

  app = QApplication([])
  variants = ["macroscopic.arc.mass|convection|lumped.ConvectiveFlow",
              "macroscopic.arc.mass|convection|lumped.ConvectiveFlowControlled",
              "macroscopic.arc.mass|convection|lumped.ConvectiveFlow",
              "macroscopic.node.mass|event|lumped.massIntraFace",
              "macroscopic.arc.mass|diffusion|lumped.MassDiffusionFick",
              "macroscopic.arc.mass|convection|lumped.ConvectiveFlowPulse",
              "macroscopic.arc.charge|convection|lumped.ConvectiveFlowPulse",
              "macroscopic.arc.energy|convection|lumped.ConvectiveFlowPulse",
              ]
  var = extract(variants, ["arc","macroscopic"],["mass","energy"], ["MassDiffusionFick"])

  print(var)
  w = VariantGUI(var)
  w.show()
  app.exec()
  print(w.selection)





