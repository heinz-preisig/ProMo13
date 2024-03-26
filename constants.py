from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class FixedVariables:
  TIME: ClassVar[str] = "V_1"
  INCIDENCE_MATRIX: ClassVar[str] = "V_2"
  INCIDENCE_MATRIX_NI_SOURCE: ClassVar[str] = "V_3"
  INCIDENCE_MATRIX_NI_SINK: ClassVar[str] = "V_4"
  INCIDENCE_MATRIX_AI_SOURCE: ClassVar[str] = "V_5"
  INCIDENCE_MATRIX_AI_SINK: ClassVar[str] = "V_6"
  SELECTION_MATRIX_I_INPUT: ClassVar[str] = "V_7"
  SELECTION_MATRIX_I_OUTPUT: ClassVar[str] = "V_8"
  INCIDENCE_MATRIX_NA_SOURCE: ClassVar[str] = "V_9"
  INCIDENCE_MATRIX_NA_SINK: ClassVar[str] = "V_10"
  COORDINATE_X: ClassVar[str] = "V_11"
  COORDINATE_Y: ClassVar[str] = "V_12"
  COORDINATE_Z: ClassVar[str] = "V_13"
  A_NPQ: ClassVar[str] = "V_14"    # Mapping from inputs to outputs
  A_NTU: ClassVar[str] = "V_15"    # Mapping from input elements to output
  # same as matrix D inside a ABCD controller
  U_NPT: ClassVar[str] = "V_16"    # Input signal in control domain
  Y_NTU: ClassVar[str] = "V_17"    # Output signal in control domain
  I_TU: ClassVar[str] = "V_18"     # Identity matrix to switch from T to U in
  # in the control arcs
  # Selection matrix for species related measures
  S_NUS: ClassVar[str] = "V_19"
  # Selection matrix mapping arcs and interfaces
  S_AP: ClassVar[str] = "V_20"
  S_AQ: ClassVar[str] = "V_21"     # to inputs and outputs
  S_IP: ClassVar[str] = "V_22"
  S_IQ: ClassVar[str] = "V_23"
  S_NPU: ClassVar[str] = "V_24"    # Selection matrix for the stacker
  S_NQT: ClassVar[str] = "V_25"    # Selection matrix for the splitter
  MV_I: ClassVar[str] = "V_26"     # Interface variables from macro -> control
  MW_IS: ClassVar[str] = "V_27"
  CZ_N: ClassVar[str] = "V_28"     # Output from control
  CZ_I: ClassVar[str] = "V_29"     # Interface variable from control --> macro
  STOCHIOMETRY_MATRIX: ClassVar[str] = "V_30"  # index NK
