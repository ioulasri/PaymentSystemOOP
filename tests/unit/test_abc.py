import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

from src.core.base import PaymentStrategy
from src.models.user import User


class TestPayment(unittest.TestCase):
    def test_abstract_instantiation_raises(self):
        with self.assertRaises(TypeError):
            PaymentStrategy()


class TestUser(unittest.TestCase):
    def test_abstract_instantiation_raises(self):
        with self.assertRaises(TypeError):
            User()


if __name__ == "__main__":
    # Allow running this file directly, but keep it discovery-friendly
    # so test runners (unittest discovery / pytest) can import it safely.
    unittest.main()
