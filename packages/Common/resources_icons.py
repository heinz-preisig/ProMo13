import os

from PyQt5 import QtCore
from PyQt5 import QtGui

from Common.resource_initialisation import DIRECTORIES

# ===========================================  icons ==============================
ICONS = {}
ICONS["+"] = "plus-icon.png"
ICONS["-"] = "minus-icon.png"
ICONS["->"] = "right-icon.png"
ICONS["<-"] = "left-icon.png"
ICONS["^"] = "up-icon.png"
ICONS["v"] = "right-icon.png"
# ICONS["delete"] = "icon_trash_it.png"
ICONS["ontology"] = "ontology.xpm"
ICONS["exit"] = "exit_button_hap.svg"
ICONS["task_automata"] = "task_automata.svg"
ICONS["task_ontology_foundation"] = "task_ontology_foundation.svg"
ICONS["task_ontology_equations"] = "task_ontology_equations.svg"
ICONS["task_model_composer"] = "task_model_composer.svg"
ICONS["task_graphic_objects"] = "task_graphic_objects.svg"
ICONS["task_entity_generation"] = "task_entity_generation.svg"
ICONS["task_automata"] = "task_automata.svg"
ICONS["info"] = "info_button_hap.svg"
ICONS["accept"] = "accept_button_hap.svg"
ICONS["reject"] = "reject_button_hap.svg"
ICONS["back"] = "back_button_hap.svg"
ICONS["new"] = "new_button_hap.svg"
ICONS["compile"] = "compile_button_hap.svg"
ICONS["dot_graph"] = "dot_graph_button_hap.svg"
ICONS["save"] = "save_button_hap.svg"
ICONS["port"] = "port_button_hap.svg"
ICONS["dependent_variable"] = "dependent_new_button.svg"
ICONS["variable_show"] = "variable_show_button.svg"
ICONS["delete"] = "delete_button_hap.svg"
ICONS["reset"] = "reset_button_hap.svg"
ICONS["equation"] = "quation_button_hap.svg"
ICONS["schnipsel"] = "schnipsel_button_hap.svg"
ICONS["screen_shot"] = "screen_shot_button_hap.svg"
ICONS["save_as"] = "save_as_button_hap.svg"
ICONS["plus"] = "plus_button_hap.svg"
ICONS["LaTex"] = "latex_button_hap.svg"
ICONS["update"] = "update_button_hap.svg"
ICONS["next"] = "next_button_hap.svg"

size = 52
BUTTON_ICON_SIZE = QtCore.QSize(size, size)
round = 'border-radius: %spx; ' % (size / 2)
BUTTON_ICON_STYLE_ROUND = 'background-color: white; '
BUTTON_ICON_STYLE_ROUND += 'border-style: outset; '
BUTTON_ICON_STYLE_ROUND += 'border-width: 2px; '
BUTTON_ICON_STYLE_ROUND += round
BUTTON_ICON_STYLE_ROUND += 'border-color: white;    '
BUTTON_ICON_STYLE_ROUND += 'font: bold 14px;   '
BUTTON_ICON_STYLE_ROUND += 'padding: 6px;'


def roundButton(button, what, tooltip=None):
  button.setText("")
  button.setFixedSize(BUTTON_ICON_SIZE)
  button.setIcon(getIcon(what))
  button.setStyleSheet(BUTTON_ICON_STYLE_ROUND)
  button.setIconSize(BUTTON_ICON_SIZE)
  button.setToolTip(tooltip)
  # button.setStyleSheet("""QToolTip {
  #                            background-color: black;
  #                            color: white;
  #                            border: black solid 1px
  #                            }""")


def getIcon(what):
  try:
    what in ICONS.keys()
  except:
    print("assertation error %s is not in the icon dictionary" % what)
    os.exit()

  f_name = os.path.join(DIRECTORIES["icon_location"], ICONS[what])
  # print("debugging .....", f_name)
  if os.path.exists(f_name):
    pm = QtGui.QPixmap(f_name)
    return QtGui.QIcon(pm)
  else:
    print("no such file : ", f_name)
    pass
