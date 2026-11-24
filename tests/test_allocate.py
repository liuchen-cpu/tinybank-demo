"""issue/0001 的验收测试：按权重分摊，一分钱都不能丢。"""

import unittest

from tinybank import InvalidAmount, allocate


class TestAllocateExactness(unittest.TestCase):
    def test_three_way_split_puts_remainder_on_first(self):
        parts = allocate(100, [1, 1, 1])
        self.assertEqual(parts, [33.34, 33.33, 33.33])

    def test_sum_always_equals_total(self):
        for total in (0.01, 1, 9.99, 100, 1234.56):
            for weights in ([1], [1, 1], [1, 2, 3], [7, 3], [1] * 7, [0, 1]):
                with self.subTest(total=total, weights=weights):
                    parts = allocate(total, weights)
                    self.assertEqual(len(parts), len(weights))
                    self.assertEqual(
                        sum(round(p * 100) for p in parts),
                        round(total * 100),
                    )

    def test_remainder_goes_to_largest_fraction_then_lowest_index(self):
        # 100 分按 1:2 分 -> 33.333... 与 66.666...，余那 1 分给小数部分更大的第二方
        self.assertEqual(allocate(1, [1, 2]), [0.33, 0.67])

    def test_zero_weight_receives_nothing(self):
        self.assertEqual(allocate(10, [0, 1]), [0.0, 10.0])

    def test_no_float_drift_on_many_parts(self):
        parts = allocate(0.07, [1] * 3)
        self.assertEqual(sum(round(p * 100) for p in parts), 7)
        self.assertEqual(max(parts) - min(parts) <= 0.01, True)


class TestAllocateValidation(unittest.TestCase):
    def test_invalid_inputs_raise_invalid_amount(self):
        cases = [
            (0, [1]),          # 总额非正
            (-1, [1]),         # 总额为负
            (1, []),           # 无收款方
            (1, [-1]),         # 负权重
            (1, [0, 0]),       # 权重和为 0
            (1.005, [1]),      # 精度超过 2 位
        ]
        for total, weights in cases:
            with self.subTest(total=total, weights=weights):
                with self.assertRaises(InvalidAmount):
                    allocate(total, weights)


if __name__ == "__main__":
    unittest.main()
