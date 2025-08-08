import os

from PyQt5 import QtCore
from PyQt5 import QtGui

# from resources.pop_up_message_box import makeMessageBox
from Common.pop_up_message_box import makeMessageBox
from Common.resource_initialisation import DIRECTORIES

# ===========================================  icons ==============================

ICONS = {}
ICONS["+"] = "plus-icon.png"
ICONS["-"] = "minus-icon.png"
ICONS["->"] = "right-icon.png"
ICONS["<-"] = "left-icon.png"
ICONS["^"] = "up-icon.png"
ICONS["v"] = "right-icon.png"
ICONS["accept"] = "accept_button_hap.svg"
ICONS["back"] = "back_button_hap.svg"
ICONS["cancel"] = "back_button_hap.svg"
ICONS["compile"] = "compile_button_hap.svg"
ICONS["delete"] = "delete_button_hap.svg"
ICONS["dependent_variable"] = "dependent_new_button.svg"
ICONS["dot_graph"] = "dot_graph_button_hap.svg"
ICONS["edit"] = "edit_button_hap.svg"
ICONS["equation"] = "quation_button_hap.svg"
ICONS["exit"] = "exit_button_hap.svg"
ICONS["filter"] = "filter_button_hap.svg"
ICONS["IRI"] = "iri_button_hap.svg"
ICONS["info"] = "info_button_hap.svg"
ICONS["LaTex"] = "latex_button_hap.svg"
ICONS["new"] = "new_button_hap.svg"
ICONS["next"] = "next_button_hap.svg"
ICONS["number"] = "instantiate_button_hap.svg"
ICONS["off"] = "off_button_2_hap.svg"
ICONS["ontology"] = "ontology.xpm"
ICONS["PDF"] = "variable_pdf_button.svg"
ICONS["plus"] = "plus_button_hap.svg"
ICONS["port"] = "port_button_hap.svg"
ICONS["reject"] = "reject_button_hap.svg"
ICONS["reset"] = "reset_button_hap.svg"
ICONS["SI"] = "SI_units_button_hap.svg"
ICONS["save"] = "save_button_hap.svg"
ICONS["save_as"] = "save_as_button_hap.svg"
ICONS["screen_shot"] = "screen_shot_button_hap.svg"
ICONS["schnipsel"] = "schnipsel_button_hap.svg"
ICONS["task_automata"] = "task_automata.svg"
ICONS["task_ontology_foundation"] = "task_ontology_foundation.svg"
ICONS["task_ontology_equations"] = "task_ontology_equations.svg"
ICONS["task_model_composer"] = "task_model_composer.svg"
ICONS["task_graphic_objects"] = "task_graphic_objects.svg"
ICONS["task_entity_generation"] = "task_entity_generation.svg"
ICONS["task_automata"] = "task_automata.svg"
ICONS["update"] = "update_button_hap.svg"
ICONS["variable_show"] = "variable_show_button.svg"
ICONS["V"] = "V_button_hap.svg"
ICONS["LED_green"] = "LED_green.svg"
ICONS["LED_red"] = "LED_red.svg"


def getIcon(what):
  try:
    what in ICONS.keys()
  except:
    makeMessageBox("assertation error %s is not in the icon dictionary %s\n I exit" % what, ["OK"])
    os.exit()

  # f_name = os.path.join(os.getcwd(), 'resources', "icons", ICONS[what])
  f_name = os.path.join(DIRECTORIES["icon_location"], ICONS[what])
  # print("debugging .....", f_name)
  if os.path.exists(f_name):
    # pm = QtGui.QPixmap(f_name)
    icon = QtGui.QIcon(f_name)

    return icon  # QtGui.QIcon(pm)
  else:
    makeMessageBox("no such file : %s" % f_name, ["OK"])
    pass

class roundButton:


  def __init__(self, button, what, tooltip=None, mysize=None):
    defaultsize = 52
    if mysize:
      size=mysize
    else:
      size = defaultsize

    BUTTON_ICON_SIZE = QtCore.QSize(size, size)
    round = 'border-radius: %spx; ' % (size / 2)
    BUTTON_ICON_STYLE_ROUND = 'background-color: white; '
    BUTTON_ICON_STYLE_ROUND += 'border-style: outset; '
    BUTTON_ICON_STYLE_ROUND += 'border-width: 2px; '
    BUTTON_ICON_STYLE_ROUND += round
    BUTTON_ICON_STYLE_ROUND += 'border-color: white;    '
    BUTTON_ICON_STYLE_ROUND += 'font: bold 14px;   '
    BUTTON_ICON_STYLE_ROUND += 'padding: 6px;'

    button.setText("")
    button.setFixedSize(size,size)
    icon = getIcon(what)
    button.setIcon(icon) #getIcon(what))
    button.setStyleSheet(BUTTON_ICON_STYLE_ROUND)
    button.setIconSize(BUTTON_ICON_SIZE)
    button.setToolTip(tooltip)
    self.button = button



  def changeIcon(self, what):
    icon = getIcon(what)
    self.button.setIcon(icon)
