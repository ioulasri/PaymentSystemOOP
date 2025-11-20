import sys
import os
import unittest

# ensure project src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.payment.methods.crypto import CryptoPayment


class TestCryptoPayment(unittest.TestCase):
    def test_validate_and_set_wallet(self):
        cp = CryptoPayment()
        self.assertFalse(cp.validate())
        cp.set_wallet('0xdeadbeefcafebabedeadbeefcafebabedeadbeef', 'ethereum')
        self.assertTrue(cp.validate())
        print('\n[DEBUG] wallet_info =', cp.get_wallet_info())

    def test_execute_invalid_amounts(self):
        cp = CryptoPayment()
        cp.set_wallet('0xabcdefabcdefabcdefabcdefabcdefabcdefabcd', 'ethereum')

        res_none = cp.execute(None)
        print('\n[DEBUG] execute(None) =>', res_none)
        self.assertEqual(res_none.get('status'), 'failed')

        res_neg = cp.execute(-10)
        print('\n[DEBUG] execute(-10) =>', res_neg)
        self.assertEqual(res_neg.get('status'), 'failed')

    def test_execute_success_and_receipt(self):
        cp = CryptoPayment()
        cp.set_wallet('0x1234567890123456789012345678901234567890', 'ethereum')
        txn = cp.execute(100.0)
        print('\n[DEBUG] execute(100.0) =>', txn)
        self.assertEqual(txn.get('status'), 'completed')
        self.assertIn('fee', txn)

        receipt = cp.generate_receipt()
        print('\n[DEBUG] receipt =>', receipt)
        self.assertEqual(receipt.get('transaction_id'), txn.get('id'))

    def test_fee_convert_track_refund(self):
        cp = CryptoPayment()
        cp.set_wallet('0xfeedfacecafebabedeadbeefcafebabedeadbeef', 'ethereum')
        fee = cp.estimate_fees(200.0)
        converted = cp.convert_currency(200.0, 'USD', 'BTC')
        txn = cp.execute(200.0)
        track = cp.track_transaction(txn.get('id'))
        refund = cp.refund(txn.get('id'), 50.0)

        print('\n[DEBUG] fee(200.0) =>', fee)
        print('\n[DEBUG] converted 200 USD -> BTC =>', converted)
        print('\n[DEBUG] track =>', track)
        print('\n[DEBUG] refund =>', refund)

        self.assertIsInstance(fee, float)
        self.assertIsInstance(converted, float)
        self.assertEqual(track.get('transaction_id'), txn.get('id'))
        self.assertEqual(refund.get('status'), 'refunded')
    def test_misc_helpers(self):
        cp = CryptoPayment()
        cp.set_wallet('0x1111111111111111111111111111111111111111', 'ethereum')

        inv = cp.generate_invoice(123.45, '2025-12-31')
        self.assertIn('invoice_id', inv)

        sched = cp.schedule_payment(10.0, 'method', '2025-12-31')
        self.assertIn('payment_id', sched)

        discounted = cp.apply_discount(50.0, 'X')
        self.assertLessEqual(discounted, 50.0)

        tax = cp.calculate_tax(100.0, 5.0)
        self.assertAlmostEqual(tax, 5.0)

        self.assertTrue(cp.verify_identity('u1', {'doc': 'ok'}))
        self.assertTrue(cp.link_bank_account({'acc': 'x'}))
        self.assertTrue(cp.unlink_bank_account('acc1'))
        linked = cp.get_linked_bank_accounts()
        self.assertIsInstance(linked, list)

if __name__ == '__main__':
    unittest.main()

class TestCryptoValidation(unittest.TestCase):
    def test_address_validation(self):
        """Test address validation for different formats."""
        cp = CryptoPayment()
        
        # Valid Ethereum address should work
        cp.set_wallet('0x1234567890123456789012345678901234567890', 'ethereum')
        self.assertTrue(cp.validate())
        
        # Invalid Ethereum address should fail
        with self.assertRaises(ValueError):
            cp.set_wallet('0x123', 'ethereum')  # Too short
            
        # Bitcoin testnet address (using generic validation for now)
        cp.set_wallet('1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa', 'bitcoin')
        self.assertTrue(cp.validate())
        
        # Test fallback validation for unknown networks
        cp.set_wallet('some-valid-looking-address-12345', 'unknown-network')
        self.assertTrue(cp.validate())
