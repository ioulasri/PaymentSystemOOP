import os
import sys
import unittest

from src.models.admin import Admin
from src.models.customer import Customer

# ensure project src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestCustomerModel(unittest.TestCase):
    def test_creation_and_info(self):
        c = Customer("Alice", "alice@example.com")
        self.assertIsNotNone(c._user_id)
        self.assertTrue(c._user_id.startswith("USR-"))
        info = c.get_user_info()
        self.assertEqual(info["id"], c._user_id)
        self.assertEqual(info["name"], "Alice")
        self.assertEqual(info["email"], "alice@example.com")
        self.assertEqual(info["role"], "customer")
        self.assertTrue(info["is_active"])

    def test_wallet_and_payment(self):
        c = Customer("Bob", "bob@example.com")
        # no saved methods => initiating should raise
        with self.assertRaises(ValueError):
            c.initiate_payment(10.0, "card-x")

        # save a payment method and attach a numeric wallet
        c.save_payment_method("card-x")
        c._wallets["card-x"] = 100.0
        txn = c.initiate_payment(30.0, "card-x")
        self.assertEqual(txn["status"], "success")
        # balance should be reduced
        self.assertAlmostEqual(c.view_balance(), 70.0)

    def test_transaction_history_appended(self):
        c = Customer("Carol", "carol@example.com")
        c.save_payment_method("m1")
        c._wallets["m1"] = 50.0
        txn = c.initiate_payment(5.0, "m1")
        history = c.view_transaction_history()
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[-1]["id"], txn["id"])


class TestAdminModel(unittest.TestCase):
    def test_admin_workflow(self):
        a = Admin("Dana", "dana@example.com", permissions=["approve_transactions"])
        info = a.get_user_info()
        self.assertIsNotNone(info["id"])
        self.assertTrue(info["id"].startswith("ADM-"))
        self.assertIn("approve_transactions", info["permissions"])

        # add a transaction to the review queue
        a._review_queue.append({"id": "tx1", "amount": 123.45})
        rec = a.review_transaction("tx1")
        self.assertIsNotNone(rec)
        self.assertEqual(rec["id"], "tx1")

        # approve it
        ok = a.approve_transaction("tx1")
        self.assertTrue(ok)
        # audit log should contain an approved record
        approved = [r for r in a._audit_log if r.get("action") == "approved"]
        self.assertTrue(len(approved) >= 1)

        # flag another transaction
        a.flag_transaction("tx2", "suspicious")
        flagged = a.view_flagged_transactions()
        self.assertTrue(any(r.get("id") == "tx2" for r in flagged))

        # permissions / deactivate
        self.assertTrue(a.has_permission("approve_transactions"))
        a.deactivate()
        self.assertFalse(a.get_user_info()["is_active"])


if __name__ == "__main__":
    unittest.main()
