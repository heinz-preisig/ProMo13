from typing import Dict
from ply import lex, yacc
import logging

from packages.Common.classes import translator
# from packages.Common.classes import variable

# Setting up a logger
logger = logging.getLogger(__name__)


class DELIMITERS:
  LEFT_ROUND = "D_0"
  RIGHT_ROUND = "D_1"
  LEFT_SQUARE = "D_2"
  RIGHT_SQUARE = "D_3"
  LEFT_WIGGLED = "D_4"
  RIGHT_WIGGLED = "D_5"
  OR = "D_6"
  COMMA = "D_7"
  DOUBLE_COLUMN = "D_8"
  AMPERSAND = "D_9"
  UNDERLINE = "D_10"


class OPERATORS:
  PLUS = "O_0"
  MINUS = "O_1"
  HAT = "O_2"
  COLON = "O_3"
  DOT = "O_4"
  PIPE = "O_5"


class EquationParser:
  def __init__(
      self,
      language: str,
      variables,  # : Dict[str, variable.Variable]
      indices: Dict[str, str],  # : Dict[str, index???]
  ):
    self.language = language
    self.translator = translator.Translator(language)
    self.variables = variables
    self.indices = indices

  # Define the rule for ignoring whitespace
  t_ignore = ' \t'

  ########################## TOKEN DEFINITIONS #########################
  tokens = (
      'VARIABLE',
      'UNARY_FUNCTION',
      'BINARY_FUNCTION',
      'QUATERNARY_FUNCTION',
      'INDEX',
      'DELIMITER',
      'O_PLUS',
      'O_MINUS',
      'O_HAT',
      'O_COLON',
      'O_DOT',
      'O_PIPE',
      'O_IN',
      'D_LEFT_ROUND',
      'D_RIGHT_ROUND',
      'D_LEFT_SQUARE',
      'D_RIGHT_SQUARE',
      'D_LEFT_WIGGLED',
      'D_RIGHT_WIGGLED',
      'D_OR',
      'D_COMMA',
      'D_DOUBLE_COLUMN',
      'D_AMPERSAND',
      'D_UNDERLINE',
  )

  t_VARIABLE = r'V_\d+'
  t_UNARY_FUNCTION = r'F_(?:1[0-6]|[0-9])(?!\d)'
  t_BINARY_FUNCTION = r'F_1[7-9]'
  t_QUATERNARY_FUNCTION = r'F_20'
  t_INDEX = r'I_\d+'
  # OPERATORS
  t_O_PLUS = r'O_0'
  t_O_MINUS = r'O_1'
  t_O_HAT = r'O_2'
  t_O_COLON = r'O_3'
  t_O_DOT = r'O_4'
  t_O_PIPE = r'O_5'
  t_O_IN = r'O_14'
  # DELIMITERS
  t_D_LEFT_ROUND = r'D_0'
  t_D_RIGHT_ROUND = r'D_1'
  t_D_LEFT_SQUARE = r'D_2'
  t_D_RIGHT_SQUARE = r'D_3'
  t_D_LEFT_WIGGLED = r'D_4'
  t_D_RIGHT_WIGGLED = r'D_5'
  t_D_OR = r'D_6'
  t_D_COMMA = r'D_7'
  t_D_DOUBLE_COLUMN = r'D_8'
  t_D_AMPERSAND = r'D_9'
  t_D_UNDERLINE = r'D_10'

  ############################## PRECEDENCE ############################
  precedence = (
      ('left', 'O_PLUS', 'O_MINUS'),
      ('left', 'O_DOT', 'O_COLON', 'O_PIPE'),
      ('left', 'O_HAT'),
      ('right', 'UMINUS'),
  )
  ############################ EXPRESSION RULES ########################

  def p_expr_variable(self, p: yacc.YaccProduction) -> None:
    '''expression : VARIABLE'''

    var_id = p[1]
    if var_id not in self.variables:
      raise ValueError(
          f"Variable {var_id} not found."
      )
    var_name = self.variables[var_id].get_alias(self.language)
    # TODO: Probably make an INDEX class
    var_indices = []
    for index in self.variables[var_id].get_indices():
      var_indices.append(self.indices[str(index)]["aliases"][self.language][0])

    p[0] = self.translator.translate_variable(var_name, var_indices)

  def p_expr_plus(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_PLUS expression'''
    p[0] = self.translator.translate_addition(p[1], p[3])

  def p_expr_minus(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_MINUS expression'''
    p[0] = self.translator.translate_substraction(p[1], p[3])

  def p_expr_uminus(self, p: yacc.YaccProduction) -> None:
    '''expression : O_MINUS expression %prec UMINUS'''
    p[0] = self.translator.translate_negation(p[2])

  def p_expr_expand_product(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_DOT expression'''
    p[0] = self.translator.translate_expand_product(p[1], p[3])

  def p_expr_khatri_rao(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_COLON expression'''
    p[0] = self.translator.translate_khatri_rao(p[1], p[3])

  def p_expr_reduce_product(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_PIPE INDEX O_PIPE expression'''

    # TODO: Change after making an index class
    idx1 = self.indices[p[3][-1]]["aliases"][self.language]
    p[0] = self.translator.translate_reduce_product(p[1], idx1, p[5])

  def p_expr_block_reduce_product(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_PIPE INDEX O_IN INDEX O_PIPE expression'''
    # TODO: Change after making an index class
    idx1 = self.indices[p[3][-1]]["aliases"][self.language]
    idx2 = self.indices[p[5][-1]]["aliases"][self.language]
    p[0] = self.translator.translate_block_reduce_product(
        p[1], idx1, idx2, p[7])

  def p_expr_power(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_HAT expression'''
    p[0] = self.translator.translate_power(p[1], p[3])

  def p_expr_parentheses(self, p: yacc.YaccProduction) -> None:
    '''expression : D_LEFT_ROUND expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_parentheses(p[2])

  def p_unary_function(self, p: yacc.YaccProduction) -> None:
    '''expression : UNARY_FUNCTION D_LEFT_ROUND expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_unary_function(p[1], p[3])

  def p_binary_function(self, p: yacc.YaccProduction) -> None:
    '''expression : BINARY_FUNCTION D_LEFT_ROUND expression D_COMMA expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_binary_function(p[1], p[3], p[5])

  def p_quaternary_function(self, p: yacc.YaccProduction) -> None:
    '''expression : QUATERNARY_FUNCTION D_LEFT_ROUND expression D_COMMA expression D_COMMA expression D_COMMA expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_quaternary_function(
        p[1], p[3], p[5], p[7], p[9])
  ##############################################################################

  # Check for the translations
  def get_translation(self, item):
    translation = self.language_specifications.get(item)
    if translation is None:
      raise ValueError(
          f"Translation not found for item: {item}"
      )

    return translation

  def t_error(self, t):
    logger.warning(f"Illegal character '{t.value[0]}' at index {t.lexpos}")
    t.lexer.skip(1)

  def parse(self, input_string):
    # Create the lexer and parser
    lexer = lex.lex(module=self)
    # lexer.input(input_string)
    # for token in lexer:
    #   print(token)

    # print("===============")
    parser = yacc.yacc(module=self)

    # Parse the input string
    result = parser.parse(input_string, lexer=lexer)

    # Return the parsed result
    return result
