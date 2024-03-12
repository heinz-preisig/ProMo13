from dataclasses import dataclass
from pathlib import Path
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
  COORDINATE_X: ClassVar[str] = "V_9"
  COORDINATE_Y: ClassVar[str] = "V_10"
  COORDINATE_Z: ClassVar[str] = "V_11"
