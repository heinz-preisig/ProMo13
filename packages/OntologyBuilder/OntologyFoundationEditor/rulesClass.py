# ontology rules
# initial values


class Rules(dict):
  def __init__(self):
    dict.__init__(self)
    self["networks"] = {
            "network_enable_adding_indices": {},
            "normed_network" : {},
            }
    self["variable_classes"] = {
            "variable_classes_having_port_variables": [],
            "are_persistent_variables"              : [],
            "are_constants"                         : [],
            }
    self["node_classes"] = {
            "nodes_allowing_token_injection" : [],  # ["constant"],
            "nodes_allowing_token_conversion": [],  # ["dynamic", "event"],
            }
    self["fixed"] = {
            "nodes_allowing_token_transfer"  : ["intraface", "node_arc"],}

class RulesRadioButtons(dict):
  def __init__(self,ui):
    dict.__init__(self)
    self["network_enable_adding_indices"] = ui.radioButtonIsEnableAddingIndex
    self["variable_classes_having_port_variables"] = ui.radioButtonHasPortVariables
    self["are_persistent_variables"] = ui.radioButtonHasPersistantVariables
    self["are_constants"] = ui.radioButtonAreConstants
    self["nodes_allowing_token_injection"] = ui.radioButtonAllowsInjection
    self["nodes_allowing_token_conversion"] = ui.radioButtonAllowsTokenConversion
    # self["nodes_allowing_token_transfer"] = ui.radioButtonAlowsTokenTransfer