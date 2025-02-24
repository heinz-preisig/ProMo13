import unittest
from equation_parser import EquationParser


class Variable:
  def __init__(self, var_id, name):
    self.var_id = var_id
    self.label = name

  def get_label(self, language):
    return self.label


class Index:
  def __init__(self, idx_id, alias):
    self.idx_id = idx_id
    self.alias = alias

  def get_alias(self, language):
    return self.alias


class MyParserTestCase(unittest.TestCase):
  def setUp(self):
    self.variables = {
        "V_1": Variable("V_1", "p"),
        "V_2": Variable("V_2", "c"),
        "V_3": Variable("V_3", "n"),
    }
    self.indices = {
        "I_1": Index("I_1", "N"),
        "I_2": Index("I_2", "A"),
        "I_3": Index("I_3", "S"),
        "I_5": Index("I_5", "N_x_S")
    }
    self.parser = EquationParser("E_3", "Matlab", self.variables, self.indices)

  def test_variable(self):
    result = self.parser.parse("V_1")
    expected = "p"
    self.assertEqual(result, expected)

  def test_plus_minus(self):
    result = self.parser.parse("V_1 O_0 V_2")
    expected = "p + c"
    self.assertEqual(result, expected)

    result = self.parser.parse("V_1 O_1 V_2")
    expected = "p - c"
    self.assertEqual(result, expected)

    result = self.parser.parse("V_1 O_0 V_2 O_0 V_3")
    expected = "p + c + n"
    self.assertEqual(result, expected)

    result = self.parser.parse("V_1 O_0 V_2 O_1 V_3")
    expected = "p + c - n"
    self.assertEqual(result, expected)

  def test_expand_product(self):
    result = self.parser.parse("V_1 O_0 V_2 O_4 V_3")
    expected = "p + c .* n"
    self.assertEqual(result, expected)

  def test_khatrirao(self):
    result = self.parser.parse("V_1 O_3 V_2")
    expected = "khatrirao(p, c)"
    self.assertEqual(result, expected)

    result = self.parser.parse("V_1 O_1 V_1 O_3 V_2 O_3 V_3")
    expected = "p - khatrirao(khatrirao(p, c), n)"
    self.assertEqual(result, expected)

  def test_reduce_product1(self):
    result = self.parser.parse("V_1 O_5 I_1 O_5 V_2")
    expected = "reduceproduct(p, \\\"N\\\", c)"
    self.assertEqual(result, expected)

  def test_reduce_product2(self):
    result = self.parser.parse("V_1 O_1 V_1 O_5 I_1 O_5 V_2")
    expected = "p - reduceproduct(p, \\\"N\\\", c)"
    self.assertEqual(result, expected)

  def test_block_reduce_product(self):
    result = self.parser.parse("V_1 O_0 V_1 O_5 I_1 O_14 I_2 O_5 V_2")
    expected = "p + blockreduce(p, \\\"N\\\", \\\"A\\\", c)"
    self.assertEqual(result, expected)

  def test_power(self):
    result = self.parser.parse("V_1 O_2 V_2")
    expected = "p .^ c"
    self.assertEqual(result, expected)

    result = self.parser.parse("V_1 O_3 V_2 O_2 V_3")
    expected = "khatrirao(p, c .^ n)"
    self.assertEqual(result, expected)

  def test_parentheses(self):
    result = self.parser.parse("D_0 V_2 O_0 V_3 D_1")
    expected = "(c + n)"
    self.assertEqual(result, expected)

    result = self.parser.parse("V_1 O_3 D_0 V_2 O_0 V_3 D_1")
    expected = "khatrirao(p, (c + n))"
    self.assertEqual(result, expected)

  def test_unary_function(self):
    result = self.parser.parse("F_0 D_0 V_1 D_1")
    expected = "exp(p)"
    self.assertEqual(result, expected)

    result = self.parser.parse("F_0 D_0 V_1 O_0 V_2 D_1")
    expected = "exp(p + c)"
    self.assertEqual(result, expected)

    result = self.parser.parse("V_3 O_1 F_3 D_0 V_1 D_1")
    expected = "n - sqrt(p)"
    self.assertEqual(result, expected)

    result = self.parser.parse("O_1 F_2 D_0 F_1 D_0 V_2 D_1 D_1")
    expected = "-ln(log(c))"
    self.assertEqual(result, expected)

    result = self.parser.parse("F_0 D_0 V_3 O_0 V_1 O_5 I_1 O_5 V_2 D_1")
    expected = "exp(n + reduceproduct(p, \\\"N\\\", c))"
    self.assertEqual(result, expected)

  def test_binary_function(self):
    result = self.parser.parse("F_17 D_0 V_1 D_7 V_2 D_1")
    expected = "pardiff(p, c)"
    self.assertEqual(result, expected)

  def test_quaternary_function(self):
    result = self.parser.parse("F_20 D_0 V_1 D_7 V_2 D_7 V_3 D_7 V_1 D_1")
    expected = "integral(p, c, n, p)"
    self.assertEqual(result, expected)

  # def test_list_simple(self):
  #   result = self.parser.parse("V_1 D_7 V_2")
  #   expected = "p, c"
  #   self.assertEqual(result, expected)

  # def test_list_composed(self):
  #   result = self.parser.parse("V_1 D_7 V_2 D_7 V_3")
  #   expected = "p, c, n"
  #   self.assertEqual(result, expected)

  # def test_function_simple(self):
  #   result = self.parser.parse("F_1 D_0 V_2 D_1")
  #   expected = "sin(c)"
  #   self.assertEqual(result, expected)

  # def test_function_composed(self):
  #   result = self.parser.parse("F_1 D_0 V_1 O_7 V_2 D_1")
  #   expected = "sin(p, c)"
  #   self.assertEqual(result, expected)


if __name__ == '__main__':
  unittest.main()
