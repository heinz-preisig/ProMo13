from dataclasses import dataclass, fields
from pathlib import Path
from typing import ClassVar


@dataclass(frozen=True)
class FixedVariables:
  TIME: str = "V_1"
  INCIDENCE_MATRIX: str = "V_2"
  INCIDENCE_MATRIX_NI_SOURCE: str = "V_3"
  INCIDENCE_MATRIX_NI_SINK: str = "V_4"
  INCIDENCE_MATRIX_AI_SOURCE: str = "V_5"
  INCIDENCE_MATRIX_AI_SINK: str = "V_6"
  SELECTION_MATRIX_I_INPUT: str = "V_7"
  SELECTION_MATRIX_I_OUTPUT: str = "V_8"
  COORDINATE_X: str = "V_9"
  COORDINATE_Y: str = "V_10"
  COORDINATE_Z: str = "V_11"
