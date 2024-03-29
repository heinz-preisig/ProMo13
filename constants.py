from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class FixedVariables:
# global
  TIME: ClassVar[str] = "V_1"
  INCIDENCE_MATRIX: ClassVar[str] = "V_2"
  INCIDENCE_MATRIX_NI_SOURCE: ClassVar[str] = "V_3"
  INCIDENCE_MATRIX_NI_SINK: ClassVar[str] = "V_4"
  INCIDENCE_MATRIX_AI_SOURCE: ClassVar[str] = "V_5"
  INCIDENCE_MATRIX_AI_SINK: ClassVar[str] = "V_6"
  INCIDENCE_MATRIX_NA_SOURCE: ClassVar[str] = "V_7"
  INCIDENCE_MATRIX_NA_SINK: ClassVar[str] = "V_8"
  
  SELECTION_MATRIX_I_INPUT: ClassVar[str] = "V_9"  #S_IP: ClassVar[str] = "V_14"     # to inputs and outputs
  SELECTION_MATRIX_I_OUTPUT: ClassVar[str] = "V_10" #S_IQ: ClassVar[str] = "V_15"
  
  I_TU: ClassVar[str] = "V_11"     # Identity matrix to switch from T to U in the control arcs    
  
  S_AP: ClassVar[str] = "V_12"     # Selection matrix mapping arcs and interfaces
  S_AQ: ClassVar[str] = "V_13"            
  
  S_NPU: ClassVar[str] = "V_14"    # Selection matrix for the stacker
  S_NQT: ClassVar[str] = "V_15"    # Selection matrix for the splitter
  
  MV_I: ClassVar[str] = "V_16"     # Interface variables from macro -> control
  CZ_N: ClassVar[str] = "V_17"     # Output from control
  CZ_I: ClassVar[str] = "V_18"     # Interface variable from control --> macro
  A_NPQ: ClassVar[str] = "V_19"    # Mapping from inputs to outputs
  A_NTU: ClassVar[str] = "V_20"    # Mapping from input elements to output
  # same as matrix D inside a ABCD controller
  U_NPT: ClassVar[str] = "V_21"    # Input signal in control domain
  Y_NTU: ClassVar[str] = "V_22"    # Output signal in control domain
  
  
 # physical
  COORDINATE_X: ClassVar[str] = "V_23"
  COORDINATE_Y: ClassVar[str] = "V_24"
  COORDINATE_Z: ClassVar[str] = "V_25"
  #S_NUS: ClassVar[str] = "V_x"    # Selection matrix for species related measures  
  #MW_IS: ClassVar[str] = "V_y"
  
# reactions
  STOCHIOMETRY_MATRIX: ClassVar[str] = "V_26"  # index NK
  
# global
  I_NA: ClassVar[str] = "V_27"     # Identity matrix to switch from N to A in the transport arcs   
