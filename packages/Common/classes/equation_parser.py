from typing import Dict
from ply import lex, yacc
import logging

from packages.Common.classes import translator
from packages.Common.classes import variable
from packages.Common.classes import index

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
  DOT = "O_3"
  COLON = "O_4"
  STAR = "O_5"


class EquationParser:
  def __init__(
      self,
      language: str,
      all_variables: Dict[str, variable.Variable],
      all_indices: Dict[str, index.Index],
  ):
    # TODO: Possibly remove: O_INSTANTIATE
    self.translator = translator.Translator(
        language, all_variables, all_indices)

  # Define the rule for ignoring whitespace
  t_ignore = ' \t'
  
  # Match operator and delimiter tokens
  def t_OPERATOR_OR_DELIMITER(self, t):
    r'[OD]_\d+'
    # Get all token patterns that start with t_O_ or t_D_
    token_patterns = {}
    for name in dir(self):
      if name.startswith(('t_O_', 't_D_')) and name != 't_OPERATOR_OR_DELIMITER':
        try:
          pattern = getattr(self, name)
          if isinstance(pattern, str):  # Only include string patterns
            token_patterns[name[2:]] = pattern  # Store without 't_' prefix
        except:
          continue
    
    # Check if the token value matches any known pattern
    for token_type, pattern in token_patterns.items():
      if t.value == pattern:
        t.type = token_type
        return t
    
    logger.warning(f"Unknown token: {t.value}")
    t.lexer.skip(len(t.value))

  ########################## TOKEN DEFINITIONS #########################
  tokens = (
      'VARIABLE',
      'UNARY_FUNCTION',
      # 'BINARY_FUNCTION',
      # 'QUATERNARY_FUNCTION',
      'INDEX',
      # 'DELIMITER',
      'O_PLUS',
      'O_MINUS',
      'O_HAT',
      'O_DOT',
      'O_COLON',
      'O_STAR',
      'O_DIVIDE',  # Added division operator
      # 'O_PIPE',
      'O_PARTIAL_DIFF',
      'O_TOTAL_DIFF',
      'O_INTEGRAL',
      'O_PRODUCT',
      'O_INSTANTIATE',
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
  t_UNARY_FUNCTION = r'F_(?:1[0-8]|[0-9])(?!\d)'
  # t_BINARY_FUNCTION = r'F_1[7-9]'
  # t_QUATERNARY_FUNCTION = r'F_20'
  t_INDEX = r'I_\d+'
  # OPERATORS
  # TODO: This should be done auto instead of hard coded, it needs to match with
  # the LIST_OPERATORS and LIST_DELIMITERS in resources.py
  t_O_PLUS = r'O_0'
  t_O_MINUS = r'O_1'
  t_O_HAT = r'O_2'
  t_O_DOT = r'O_4'
  t_O_COLON = r'O_3'
  t_O_STAR = r'O_5'
  t_O_DIVIDE = r'O_6'  # Added support for division operator
  t_O_PARTIAL_DIFF = r'O_7'
  t_O_TOTAL_DIFF = r'O_8'
  t_O_INTEGRAL = r'O_9'
  t_O_PRODUCT = r'O_10'
  t_O_INSTANTIATE = r'O_11'
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
      ('left', 'O_DOT', 'O_COLON', 'O_PRODUCT'),
      ('left', 'O_STAR', 'O_DIVIDE'),  # Added O_DIVIDE with same precedence as O_STAR
      ('left', 'O_HAT'),
      ('right', 'UMINUS'),
  )
  ############################ EXPRESSION RULES ########################

  def p_expr_variable(self, p: yacc.YaccProduction) -> None:
    '''expression : VARIABLE'''
    p[0] = self.translator.translate_variable(p[1])

  def p_expr_plus(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_PLUS expression'''
    p[0] = self.translator.translate_addition(p[1], p[3])

  def p_expr_minus(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_MINUS expression'''
    p[0] = self.translator.translate_substraction(p[1], p[3])

  def p_expr_uminus(self, p: yacc.YaccProduction) -> None:
    '''expression : O_MINUS expression %prec UMINUS'''
    p[0] = self.translator.translate_negation(p[2])

  def p_expr_einstein_sum_reduce(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_STAR INDEX expression'''
    p[0] = self.translator.translate_einstein_sum_contraction(p[1], p[3], p[4])

  def p_expr_einstein_sum(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_DOT expression'''
    p[0] = self.translator.translate_einstein_sum(p[1], p[3])
    
  def p_expr_divide(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_DIVIDE expression'''
    p[0] = f"({p[1]} / {p[3]})"  # Simple division for now, can be customized

  # def p_expr_expand_product(self, p: yacc.YaccProduction) -> None:
  #   '''expression : expression O_COLON expression'''
  #   p[0] = self.translator.translate_expand_product(p[1], p[3])

  # def p_expr_hadamard(self, p: yacc.YaccProduction) -> None:
  #   '''expression : expression O_DOT expression'''
  #   p[0] = self.translator.translate_hadamard(p[1], p[3])

  # def p_expr_reduce_product(self, p: yacc.YaccProduction) -> None:
  #   '''expression : expression O_STAR expression'''
  #   p[0] = self.translator.translate_reduce_product(p[1], p[3])

  # def p_expr_block_reduce_product(self, p: yacc.YaccProduction) -> None:
  #   '''expression : expression O_PIPE INDEX O_IN INDEX O_PIPE expression'''
  #   p[0] = self.translator.translate_block_reduce_product(
  #       p[1], p[3], p[5], p[7])

  def p_expr_product(self, p: yacc.YaccProduction) -> None:
    '''expression : O_PRODUCT D_LEFT_ROUND expression D_COMMA INDEX D_RIGHT_ROUND'''
    p[0] = self.translator.translate_product(p[3], p[5])

  def p_expr_power(self, p: yacc.YaccProduction) -> None:
    '''expression : expression O_HAT expression'''
    p[0] = self.translator.translate_power(p[1], p[3])

  def p_expr_parentheses(self, p: yacc.YaccProduction) -> None:
    '''expression : D_LEFT_ROUND expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_parentheses(p[2])

  def p_expr_partial_diff(self, p: yacc.YaccProduction) -> None:
    '''expression : O_PARTIAL_DIFF D_LEFT_ROUND expression D_COMMA expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_partial_diff(p[3], p[5])

  def p_expr_total_diff(self, p: yacc.YaccProduction) -> None:
    '''expression : O_TOTAL_DIFF D_LEFT_ROUND expression D_COMMA expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_total_diff(p[3], p[5])

  def p_expr_integral(self, p: yacc.YaccProduction) -> None:
    '''expression : O_INTEGRAL D_LEFT_ROUND expression D_DOUBLE_COLUMN expression O_IN D_LEFT_SQUARE expression D_COMMA expression D_RIGHT_SQUARE D_RIGHT_ROUND'''
    p[0] = self.translator.translate_integral(p[3], p[5], p[8], p[10])

  def p_expr_instantiate(self, p: yacc.YaccProduction) -> None:
    '''expression : O_INSTANTIATE D_LEFT_ROUND expression D_COMMA expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_instantiate(p[3], p[5])

  def p_unary_function(self, p: yacc.YaccProduction) -> None:
    '''expression : UNARY_FUNCTION D_LEFT_ROUND expression D_RIGHT_ROUND'''
    p[0] = self.translator.translate_unary_function(p[1], p[3])

  # def p_binary_function(self, p: yacc.YaccProduction) -> None:
  #   '''expression : BINARY_FUNCTION D_LEFT_ROUND expression D_COMMA expression D_RIGHT_ROUND'''
  #   p[0] = self.translator.translate_binary_function(p[1], p[3], p[5])

  # def p_quaternary_function(self, p: yacc.YaccProduction) -> None:
  #   '''expression : QUATERNARY_FUNCTION D_LEFT_ROUND expression D_COMMA expression D_COMMA expression D_COMMA expression D_RIGHT_ROUND'''
  #   p[0] = self.translator.translate_quaternary_function(
  #       p[1], p[3], p[5], p[7], p[9])
  ##############################################################################

  def p_error(self, p):
    if p:
      # Get the line and position of the error
      try:
        line = p.lineno
        position = p.lexpos
        
        # Get the line of text where the error occurred
        lexdata = p.lexer.lexdata
        lines = lexdata.split('\n')
        error_line = lines[line-1] if line-1 < len(lines) else ""
        
        # Create a pointer to the error position
        pointer = ' ' * (position - lexdata.rfind('\n', 0, position) - 1) + '^'
        
        logger.error(f"Syntax error at line {line}, position {position}")
        logger.error(error_line)
        logger.error(pointer)
        logger.error(f"Unexpected token: {p.type} ('{p.value}')")
        
        # Skip the current token and continue parsing
        return p
      except Exception as e:
        logger.error(f"Error in error handling: {e}")
    else:
      logger.error("Syntax error at end of input")

  def t_error(self, t):
    if t:
      logger.warning(f"Illegal character '{t.value[0]}' at position {t.lexpos}")
      logger.warning(f"Context: {t.lexer.lexdata[max(0, t.lexpos-5):t.lexpos+5]}")
      t.lexer.skip(1)
    else:
      logger.warning("Lexing error: No token provided")

  def parse(self, input_string):
    print(f"Input string: {input_string}")
    
    # Create the lexer with debug output
    lexer = lex.lex(module=self, debug=True)
    
    # Test the lexer
    lexer.input(input_string)
    print("\nToken stream:")
    for token in lexer:
      print(f"  {token.type}: {token.value}")
    
    # Reset lexer for the parser
    lexer = lex.lex(module=self)
    
    # Create the parser with debug output
    parser = yacc.yacc(module=self, debug=True, write_tables=False)
    
    try:
      # Parse the input string
      result = parser.parse(input_string, lexer=lexer, debug=True)
      print("\nParse successful!")
      return result
    except Exception as e:
      print(f"\nParse error: {e}")
      raise
