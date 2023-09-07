from typing import Dict, List
from dataclasses import dataclass

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
  PAR_DIFF: str = "F_17"
  TOTAL_DIFF: str = "F_18"
  PRODUCT: str = "F_19"
  INTEGRAL: str = "F_20"

@dataclass
class TranslationInfo:
  variable_with_index: str
  variable_no_index: str
  index: str
  addition: str
  substraction: str
  negation: str
  expand_product: str
  khatri_rao: str
  reduce_product: str
  block_reduce_product: str
  power: str
  parentheses: str
  exp: str
  log: str
  ln: str
  sqrt: str
  sin: str
  cos: str
  tan: str
  asin: str
  acos: str
  atan: str
  abs: str
  neg: str
  diffspace: str
  left: str
  right: str
  inv: str
  sign: str
  par_diff: str
  total_diff: str
  product: str
  integral: str


class Translator:
  def __init__(self, language: str):
    self.language = language
    self.FUNCTIONS = FunctionsMappings()
    # TODO: Call a function from the io module to load the
    # translation information.
    # self.translation_info = get_translation_info(self.language)
    self.translation_info = TranslationInfo(
        variable_with_index="{variable_name}({index_list})",
        variable_no_index="{variable_name}",
        index="{index_alias}",
        addition="{op1} + {op2}",
        substraction="{op1} - {op2}",
        negation="-{op1}",
        expand_product="{op1} .* {op2}",
        khatri_rao="khatrirao({op1}, {op2})",
        reduce_product="reduceproduct({op1}, \\\"{idx1}\\\", {op2})",
        block_reduce_product="blockreduce({op1}, \\\"{idx1}\\\", \\\"{idx2}\\\", {op2})",
        power="{op1} .^ {op2}",
        parentheses="({op1})",
        exp="exp({op1})",
        log="log({op1})",
        ln="ln({op1})",
        sqrt="sqrt({op1})",
        sin="sin({op1})",
        cos="cos({op1})",
        tan = "tan({op1})",
        asin = "asin({op1})",
        acos = "acos({op1})",
        atan = "atan({op1})",
        abs = "abs({op1})",
        neg = "neg({op1})",
        diffspace = "diffspace({op1})",
        left = "left({op1})",
        right = "right({op1})",
        inv = "inv({op1})",
        sign = "sign({op1})",
        par_diff = "pardiff({op1}, {op2})",
        total_diff = "totaldiff({op1}, {op2})",
        product = "product({op1}, {op2})",
        integral = "integral({op1}, {op2}, {op3}, {op4})",
    )

  def translate_variable(self, variable_name: str, index_list: List[str]):
    values = {item: value for item, value in locals().items()
              if item != "self"}
    values["index_list"] = ', '.join(index_list)

    if index_list:
      return self.translation_info.variable_with_index.format(**values)

    return self.translation_info.variable_no_index.format(**values)

  def translate_index(self, index_alias: str) -> str:
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.index.format(**values)

  def translate_addition(self, op1, op2):
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.addition.format(**values)

  def translate_substraction(self, op1, op2):
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.substraction.format(**values)

  def translate_negation(self, op1):
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.negation.format(**values)

  def translate_expand_product(self, op1, op2):
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.expand_product.format(**values)

  def translate_khatri_rao(self, op1, op2):
    # TODO: KhatriRao might need indexes
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.khatri_rao.format(**values)

  def translate_reduce_product(self, op1, idx1, op2):
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.reduce_product.format(**values)

  def translate_block_reduce_product(self, op1, idx1, idx2, op2):
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.block_reduce_product.format(**values)

  def translate_power(self, op1, op2):
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.power.format(**values)

  def translate_parentheses(self, op1):
    values = {item: value for item, value in locals().items()
              if item != "self"}

    return self.translation_info.parentheses.format(**values)
  
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
    
  def _translate_exp(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.exp.format(**values)

  def _translate_log(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.log.format(**values)

  def _translate_ln(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.ln.format(**values)

  def _translate_sqrt(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.sqrt.format(**values)

  def _translate_sin(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.sin.format(**values)

  def _translate_cos(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.cos.format(**values)

  def _translate_tan(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.tan.format(**values)

  def _translate_asin(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.asin.format(**values)

  def _translate_acos(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.acos.format(**values)

  def _translate_atan(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.atan.format(**values)

  def _translate_abs(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.abs.format(**values)

  def _translate_neg(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.neg.format(**values)

  def _translate_diffspace(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.diffspace.format(**values)

  def _translate_left(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.left.format(**values)

  def _translate_right(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.right.format(**values)

  def _translate_inv(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.inv.format(**values)

  def _translate_sign(self, op1: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.sign.format(**values)
  
  def translate_binary_function(self, function_id, op1, op2):
    # TODO: Move to a match structure when updating to python10+
    if function_id == self.FUNCTIONS.PAR_DIFF:
      return self._translate_par_diff(op1, op2)
    elif function_id == self.FUNCTIONS.TOTAL_DIFF:
      return self._translate_total_diff(op1, op2)
    elif function_id == self.FUNCTIONS.PRODUCT:
      return self._translate_product(op1, op2)
    
    return None
    
  def _translate_par_diff(self, op1: str, op2: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.par_diff.format(**values)

  def _translate_total_diff(self, op1: str, op2: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.total_diff.format(**values)
  
  def _translate_product(self, op1: str, op2: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.product.format(**values)
  
  def translate_quaternary_function(self, function_id, op1, op2, op3, op4):
    # TODO: Move to a match structure when updating to python10+
    if function_id == self.FUNCTIONS.INTEGRAL:
      return self._translate_integral(op1, op2, op3, op4)
    
    return None
    
  def _translate_integral(self, op1: str, op2: str, op3: str, op4: str):
        values = {item: value for item, value in locals().items()
                  if item != "self"}
        return self.translation_info.integral.format(**values)