"""
Contain constants to be used throughout ProMo

Classes:
    FixedVariables: Contain fixed ids for important variables.
"""
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class FixedVariables:
  """
  Contain fixed ids for important variables.

  Attributes:
      TIME (str): time
      INCIDENCE_MATRIX (str): Main incidence matrix linking node to arcs
      INCIDENCE_MATRIX_NI_SOURCE (str): Link interfaces to their source
       nodes.
      INCIDENCE_MATRIX_NI_SINK (str): Link interfaces to their sink
       nodes.
      INCIDENCE_MATRIX_AI_SOURCE (str): Link interfaces to their source
       arcs.
      INCIDENCE_MATRIX_AI_SINK (str): Link interfaces to their sink
       arcs.
      INCIDENCE_MATRIX_NA_SOURCE (str): Link arcs to their source nodes.
      INCIDENCE_MATRIX_NA_SINK (str): Link arcs to their sink nodes.

      SELECTION_MATRIX_I_INPUT (str): Link interfaces to node inputs.
      SELECTION_MATRIX_I_OUTPUT (str): Link interfaces to node outputs.

      I_TU (str): Identity matrix to switch from T to U in the control
       arcs.

      S_AP (str): Link arcs to node inputs.
      S_AQ (str): Link arcs to node outputs.

      S_NPU (str): Selection matrix for the stacker.
      S_NQT (str): Selection matrix for the splitter.

      MV_I (str): Interface variables from macro -> control.
      CZ_N (str): Output variable from control network.
      CZ_I (str): Interface variable from control --> macro.

      A_NPQ (str): Mapping from node inputs to node outputs.
      A_NTU (str): Mapping from input elements to output elements. Used
        as matrix D inside an ABCD controller.

      U_NPT (str): Input signal in control domain.
      Y_NTU (str): Output signal in control domain.

      COORDINATE_X (str): Cartesian coordinate x.
      COORDINATE_Y (str): Cartesian coordinate y.
      COORDINATE_Z (str): Cartesian coordinate z.

      STOCHIOMETRY_MATRIX (str): Stechiometry information for reaction
       systems.

      I_NA (str): Identity matrix to switch from N to A in the transport
       arcs.



  """
  # global
  TIME: ClassVar[str] = "V_1"
  INCIDENCE_MATRIX: ClassVar[str] = "V_2"
  INCIDENCE_MATRIX_NI_SOURCE: ClassVar[str] = "V_3"
  INCIDENCE_MATRIX_NI_SINK: ClassVar[str] = "V_4"
  INCIDENCE_MATRIX_AI_SOURCE: ClassVar[str] = "V_5"
  INCIDENCE_MATRIX_AI_SINK: ClassVar[str] = "V_6"
  INCIDENCE_MATRIX_NA_SOURCE: ClassVar[str] = "V_7"
  INCIDENCE_MATRIX_NA_SINK: ClassVar[str] = "V_8"

  SELECTION_MATRIX_I_INPUT: ClassVar[str] = "V_9"
  SELECTION_MATRIX_I_OUTPUT: ClassVar[str] = "V_10"

  I_TU: ClassVar[str] = "V_11"

  S_AP: ClassVar[str] = "V_12"
  S_AQ: ClassVar[str] = "V_13"

  S_NPU: ClassVar[str] = "V_14"
  S_NQT: ClassVar[str] = "V_15"

  MV_I: ClassVar[str] = "V_16"
  CZ_N: ClassVar[str] = "V_17"
  CZ_I: ClassVar[str] = "V_18"

  A_NPQ: ClassVar[str] = "V_19"
  A_NTU: ClassVar[str] = "V_20"

  U_NPT: ClassVar[str] = "V_21"
  Y_NTU: ClassVar[str] = "V_22"

  # physical
  COORDINATE_X: ClassVar[str] = "V_23"
  COORDINATE_Y: ClassVar[str] = "V_24"
  COORDINATE_Z: ClassVar[str] = "V_25"

  # TODO: Check why they are commented out.
  # S_NUS: ClassVar[str] = "V_x"    # Selection matrix for species related measures
  # MW_IS: ClassVar[str] = "V_y"

# reactions
  STOCHIOMETRY_MATRIX: ClassVar[str] = "V_26"

  I_NA: ClassVar[str] = "V_27"
