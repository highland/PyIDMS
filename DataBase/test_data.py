import unittest
from data import Pointer

class TestPointer(unittest.TestCase):
    def setUp(self):
        self.test_pointer = Pointer(1812, 3)

    def test_page(self):
        self.assertEqual(self.test_pointer.page, 1812)

    def test_line(self):
        self.assertEqual(self.test_pointer.line, 3)

    def test_str(self):
        self.assertEqual(str(self.test_pointer), '1812:3')

    def test_repr(self):
        self.assertEqual(repr(self.test_pointer), 'pointer(1812, 3)')

    def test_eq(self):
        other = Pointer(1812, 3)
        self.assertTrue(self.test_pointer == other)

    def test_from_bytes(self):
        byte_repr = (2023).to_bytes(length=3) + (6).to_bytes(length=1)
        other = Pointer.from_bytes(byte_repr)
        self.assertEqual(other.page, 2023)
        self.assertEqual(other.line, 6)

if __name__ == '__main__':
    unittest.main()
