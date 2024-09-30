from dataclasses import dataclass
from typing import List, Dict

# from packages.Common.classes.io import load_translation_info_from_file
from packages.Common.classes import io
from packages.Common.classes import variable
from packages.Common.classes import index


@dataclass
class FunctionsMappings:
  EXP: str = "F_0"
  LOG: str = "F_1"
  LN: str = "F_2"
  SQRT: str = "F_3"
  SIN: str = "F_4"
  COS: str = "F_5"
  TAN: str = "F_6"
  ASIN: str = "F_7"
  ACOS: str = "F_8"
  ATAN: str = "F_9"
  ABS: str = "F_10"
  NEG: str = "F_11"
  DIFFSPACE: str = "F_12"
  LEFT: str = "F_13"
  RIGHT: str = "F_14"
  INV: str = "F_15"
  SIGN: str = "F_16"
  ROOT: str = "F_17"


class Translator:
  def __init__(
      self,
      language: str,
      all_variables: Dict[str, variable.Variable],
      all_indices: Dict[str, index.Index],
  ):
    self.language = language
    self.translated_variables = {
        var_id: var.get_alias(language)
        for var_id, var in all_variables.items()
    }

    self.var_idx_map = {}
    for var_id, var in all_variables.items():
      full_index_list = var.get_indices()
      outer_index_list = full_index_list.copy()
      for i, idx_id in enumerate(full_index_list):
        idx = all_indices.get(idx_id)
        # Only the outer indices if there are block indices.
        if idx.is_block_index():
          outer_index_list[i] = idx.get_sub_indices()[0]

      self.var_idx_map[var_id] = outer_index_list

    self.translated_indices = {
        idx_id: idx.get_translation(language)
        for idx_id, idx in all_indices.items()
    }
    self.FUNCTIONS = FunctionsMappings()

    self.translation_info = io.load_translation_info_from_file(self.language)

  def translate_variable(self, var_id: str):
    if var_id not in self.translated_variables:
      raise ValueError(
          f"Variable {var_id} not found."
      )

    translated_index_list = [
        self.translated_indices.get(idx_id)
        for idx_id in self.var_idx_map.get(var_id)
    ]
    values = {
        "variable_name": self.translated_variables.get(var_id),
        "index_list": ', '.join(translated_index_list),
    }

    if translated_index_list:
      return self.translation_info.variable_with_index.format(**values)

    return self.translation_info.variable_no_index.format(**values)

  # def translate_index(self, idx_id: str) -> str:
  #   values = {item: value for item, value in locals().items()
  #             if item != "self"}

  #   return self.translation_info.index.format(**values)

  def translate_addition(self, op1, op2):
    values = {"op1": op1, "op2": op2}

    return self.translation_info.addition.format(**values)

  def translate_substraction(self, op1, op2):
    values = {"op1": op1, "op2": op2}

    return self.translation_info.substraction.format(**values)

  def translate_negation(self, op1):
    values = {"op1": op1}

    return self.translation_info.negation.format(**values)

  def translate_einstein_sum_contraction(self, op1, idx, op2):
    values = {"op1": op1, "op2": op2, "idx": self.translated_indices[idx]}

    return self.translation_info.einstein_sum_contraction.format(**values)

  def translate_einstein_sum(self, op1, op2):
    values = {"op1": op1, "op2": op2}

    return self.translation_info.einstein_sum.format(**values)

  # def translate_expand_product(self, op1, op2):
  #   values = {"op1": op1, "op2": op2}

  #   return self.translation_info.expand_product.format(**values)

  # def translate_hadamard(self, op1, op2):
  #   values = {"op1": op1, "op2": op2}

  #   return self.translation_info.hadamard.format(**values)

  # def translate_reduce_product(self, op1, op2):
  #   values = {
  #       "op1": op1,
  #       "op2": op2,
  #   }

  #  return self.translation_info.reduce_product.format(**values)

  # TODO: Delete
  # def translate_block_reduce_product(self, op1, idx_id1, idx_id2, op2):
  #   values = {
  #       "op1": op1,
  #       "op2": op2,
  #       "idx1": self.translated_indices.get(idx_id1),
  #       "idx2": self.translated_indices.get(idx_id2),
  #   }

  #   return self.translation_info.block_reduce_product.format(**values)

  def translate_product(self, op1: str, idx_id: str):
    values = {
        "op1": op1,
        "idx1": self.translated_indices.get(idx_id),
    }

    return self.translation_info.product.format(**values)

  def translate_power(self, op1, op2):
    values = {"op1": op1, "op2": op2}

    return self.translation_info.power.format(**values)

  def translate_parentheses(self, op1):
    values = {"op1": op1}

    return self.translation_info.parentheses.format(**values)

  def translate_instantiate(self, op1, op2):
    values = {"op1": op1, "op2": op2}

    return self.translation_info.instantiate.format(**values)

  def translate_unary_function(self, function_id, op1):
    # TODO: Move to a match structure when updating to python10+
    if function_id == self.FUNCTIONS.EXP:
      return self._translate_exp(op1)
    elif function_id == self.FUNCTIONS.LOG:
      return self._translate_log(op1)
    elif function_id == self.FUNCTIONS.LN:
      return self._translate_ln(op1)
    elif function_id == self.FUNCTIONS.SQRT:
      return self._translate_sqrt(op1)
    elif function_id == self.FUNCTIONS.SIN:
      return self._translate_sin(op1)
    elif function_id == self.FUNCTIONS.COS:
      return self._translate_cos(op1)
    elif function_id == self.FUNCTIONS.TAN:
      return self._translate_tan(op1)
    elif function_id == self.FUNCTIONS.ASIN:
      return self._translate_asin(op1)
    elif function_id == self.FUNCTIONS.ACOS:
      return self._translate_acos(op1)
    elif function_id == self.FUNCTIONS.ATAN:
      return self._translate_atan(op1)
    elif function_id == self.FUNCTIONS.ABS:
      return self._translate_abs(op1)
    elif function_id == self.FUNCTIONS.NEG:
      return self._translate_neg(op1)
    elif function_id == self.FUNCTIONS.DIFFSPACE:
      return self._translate_diffspace(op1)
    elif function_id == self.FUNCTIONS.LEFT:
      return self._translate_left(op1)
    elif function_id == self.FUNCTIONS.RIGHT:
      return self._translate_right(op1)
    elif function_id == self.FUNCTIONS.INV:
      return self._translate_inv(op1)
    elif function_id == self.FUNCTIONS.SIGN:
      return self._translate_sign(op1)
    elif function_id == self.FUNCTIONS.ROOT:
      return self._translate_root(op1)

  def _translate_exp(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.exp.format(**values)

  def _translate_log(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.log.format(**values)

  def _translate_ln(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.ln.format(**values)

  def _translate_sqrt(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.sqrt.format(**values)

  def _translate_sin(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.sin.format(**values)

  def _translate_cos(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.cos.format(**values)

  def _translate_tan(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.tan.format(**values)

  def _translate_asin(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.asin.format(**values)

  def _translate_acos(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.acos.format(**values)

  def _translate_atan(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.atan.format(**values)

  def _translate_abs(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.abs.format(**values)

  def _translate_neg(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.neg.format(**values)

  def _translate_diffspace(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.diffspace.format(**values)

  def _translate_left(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.left.format(**values)

  def _translate_right(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.right.format(**values)

  def _translate_inv(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.inv.format(**values)

  def _translate_sign(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.sign.format(**values)

  def _translate_root(self, op1: str):
    values = {"op1": op1}
    return self.translation_info.root.format(**values)

  def translate_binary_function(self, function_id, op1, op2):
    pass

  def translate_partial_diff(self, op1: str, op2: str):
    values = {"op1": op1, "op2": op2}
    return self.translation_info.par_diff.format(**values)

  def translate_total_diff(self, op1: str, op2: str):
    values = {"op1": op1, "op2": op2}
    return self.translation_info.total_diff.format(**values)

  def translate_quaternary_function(self, function_id, op1, op2, op3, op4):
    pass

  def translate_integral(self, op1: str, op2: str, op3: str, op4: str):
    values = {"op1": op1, "op2": op2, "op3": op3, "op4": op4}
    return self.translation_info.integral.format(**values)
