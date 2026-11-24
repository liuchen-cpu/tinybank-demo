"""core 模块的回归测试：金额转换、存取、转账。"""

import unittest

from tinybank import (
    Account,
    InsufficientFunds,
    InvalidAmount,
    TinyBankError,
    from_cents,
    to_cents,
)


class TestToCents(unittest.TestCase):
    def test_basic_conversion(self):
        self.assertEqual(to_cents(0.1), 10)
        self.assertEqual(to_cents(12.34), 1234)

    def test_float_accumulation_does_not_drift(self):
        # 0.1 + 0.2 == 0.30000000000000004，但必须落到 30 分
        self.assertEqual(to_cents(0.1 + 0.2), 30)

    def test_rejects_sub_cent_precision(self):
        with self.assertRaises(InvalidAmount):
            to_cents(1.005)

    def test_rejects_nan_and_bool(self):
        with self.assertRaises(InvalidAmount):
            to_cents(float("nan"))
        with self.assertRaises(InvalidAmount):
            to_cents(True)

    def test_round_trip(self):
        self.assertEqual(from_cents(to_cents(99.99)), 99.99)


class TestAccount(unittest.TestCase):
    def test_deposit_increases_balance(self):
        a = Account("alice")
        a.deposit(10)
        a.deposit(0.35)
        self.assertEqual(a.balance_cents, 1035)
        self.assertEqual(a.balance, 10.35)

    def test_withdraw_decreases_balance(self):
        a = Account("alice", 10)
        a.withdraw(3.5)
        self.assertEqual(a.balance, 6.5)

    def test_withdraw_more_than_balance_raises_and_keeps_state(self):
        a = Account("alice", 5)
        with self.assertRaises(InsufficientFunds):
            a.withdraw(5.01)
        self.assertEqual(a.balance, 5)

    def test_non_positive_amount_rejected(self):
        a = Account("alice", 5)
        for bad in (0, -1, -0.01):
            with self.assertRaises(InvalidAmount):
                a.deposit(bad)
        self.assertEqual(a.balance, 5)

    def test_transfer_moves_money_and_conserves_total(self):
        a, b = Account("alice", 100), Account("bob", 0)
        a.transfer(b, 33.33)
        self.assertEqual((a.balance, b.balance), (66.67, 33.33))
        self.assertEqual(a.balance_cents + b.balance_cents, 10000)

    def test_transfer_to_self_rejected(self):
        a = Account("alice", 100)
        with self.assertRaises(TinyBankError):
            a.transfer(a, 1)

    def test_failed_transfer_leaves_both_sides_untouched(self):
        a, b = Account("alice", 1), Account("bob", 0)
        with self.assertRaises(InsufficientFunds):
            a.transfer(b, 2)
        self.assertEqual((a.balance, b.balance), (1, 0))


if __name__ == "__main__":
    unittest.main()
