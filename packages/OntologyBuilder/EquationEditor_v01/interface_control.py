"""
interface control
buttons = ['pushAddIndex',
               'pushCompile',
               'pushExit',
               'pushInfo',
               'pushShowPDF',
               'pushShowVariables',
               'pushWrite'
               ]
  radios = ['radioArc',
            'radioGraph',
            'radioIndicesAliases',
            'radioNode',
            'radioVariables',
            'radioVariablesAliases'
            ]
  trees = ['treeWidget']
  combos = ['combo_EditVariableTypes'
            ]
"""

from Common.resources_icons import roundButton


class InterfaceControl():

    def __init__(self, ui):
        self.ui = ui
        attributes = dir(self.ui)
        self.pushButtons = {}
        self.radios = {}
        self.tabs = {}
        self.combos = {}
        self.trees = {}
        self.groups = {}
        self.ui_components = {}
        for attribute in attributes:
            if "push" in attribute:
                self.pushButtons[attribute] = getattr(self.ui, attribute)
                self.ui_components.update(self.pushButtons)
            if "radio" in attribute:
                self.radios[attribute] = getattr(self.ui, attribute)
                self.ui_components.update(self.radios)
            if "tab" in attribute:
                self.tabs[attribute] = getattr(self.ui, attribute)
                self.ui_components.update(self.tabs)
            if "tree" in attribute:
                self.trees[attribute] = getattr(self.ui, attribute)
                self.ui_components.update(self.trees)
            if "combo" in attribute:
                self.combos[attribute] = getattr(self.ui, attribute)
                self.ui_components.update(self.combos)
            if "group" in attribute:
                self.groups[attribute] = getattr(self.ui, attribute)
                self.ui_components.update(self.groups)

    def place_buttons(self):

        roundButton(self.ui.pushInfo, "info", tooltip="information")
        roundButton(self.ui.pushCompile, "compile", tooltip="compile")
        roundButton(self.ui.pushShowVariables, "variable_show", tooltip="show variables")
        roundButton(self.ui.pushWrite, "save", tooltip="save")
        roundButton(self.ui.pushShowPDF, "PDF", tooltip="show pdf variable equation documentation")
        roundButton(self.ui.pushExit, "off", tooltip="exit")
        self.signalButton = roundButton(self.ui.LED, "LED_green", tooltip="status", mysize=20)

    def start(self, condition):
        pass
        hide = ["pushShowVariables",
                "groupVariables",
                "groupEdit",
                ]
        show = ["pushShowPDF", ]
        self._do_show_and_hide(hide, show)

    def aliases(self):
        hide = ["groupEdit",
                "combo_EditVariableTypes", ]
        show = ["groupVariables", ]
        self._do_show_and_hide(hide, show)

    def tree_widget_radio_variables(self, condition):
        if condition:
            show = ["pushAddIndex", ]
            hide = []
        else:
            show = ["groupEdit", ]
            hide = ["pushAddIndex", ]

            self._do_show_and_hide(hide, show)

    def tree_widget_clicked(self):
        show = ["pushShowVariables"]
        hide = []
        self._do_show_and_hide(hide, show)

    def do_change_LED(self, state):
        if state:
            self.signalButton.changeIcon("LED_red")
        else:
            self.signalButton.changeIcon("LED_green")

    def _do_show_and_hide(self, hide, show):
        for component in hide:
            self.ui_components[component].hide()
        for component in show:
            self.ui_components[component].show()
