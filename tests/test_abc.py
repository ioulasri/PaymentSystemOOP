import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.payment.payment_strategy import PaymentStrategy
import unittest

class TestPayment(unittest.TestCase):
    def test_abstract_instantiation_raises(self):
        # Direct instantiation of abstract class should fail
        with self.assertRaises(TypeError):
            PaymentStrategy()


unittest.main()