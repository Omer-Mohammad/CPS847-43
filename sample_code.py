
import unittest

def multiply_numbers_add_five(first, second):
    return (int(first) * int(second)) + 5

class TestMultiply(unittest.TestCase):
    def test_multiply_numbers_add_five(self):
        self.assertEqual(multiply_numbers_add_five(2, 3), 11)
        self.assertEqual(multiply_numbers_add_five(5, 7), 40)
        
if __name__ == '__main__':
    unittest.main()
