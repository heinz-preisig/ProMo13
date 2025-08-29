from packages.Common.classes.equation_parser import EquationParser
from typing import Dict

# Mock classes for testing
class MockVariable:
    def __init__(self, name):
        self.name = name

class MockIndex:
    def __init__(self, name):
        self.name = name

def test_parser():
    # Setup test data
    variables = {"x": MockVariable("x"), "y": MockVariable("y")}
    indices = {"i": MockIndex("i"), "j": MockIndex("j")}
    
    # Create parser
    parser = EquationParser("python", variables, indices)
    
    # Test cases
    test_cases = [
        "O_0 D_0 x D_7 y D_1",  # x + y
        "O_1 D_0 x D_7 y D_1",  # x - y
        "O_2 D_0 x D_7 y D_1",  # x ^ y
        "O_3 D_0 x D_7 y D_1",  # x . y
        "O_4 D_0 x D_7 y D_1",  # x : y
        "O_5 D_0 x D_7 I_i D_1",  # x * i
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test}")
        try:
            result = parser.parse(test)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_parser()
