"""按权重分摊金额。

接口契约与验收标准见 issues/0001-allocate.md。
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import Sequence

from .core import InvalidAmount, from_cents, to_cents


def allocate(total: float, weights: Sequence[float]) -> list[float]:
    """把 total（元）按 weights 精确分摊给 len(weights) 方，返回每方金额（元）。

    返回值的「分」之和恒等于 total 的「分」：整数部分先按比例下取整，
    剩下的余数按小数部分从大到小分配（相同时索引小的优先）。

    Raises:
        InvalidAmount: total <= 0、weights 为空、权重为负 / 非数字、
            权重之和为 0，或金额精度超过 2 位小数。
    """
    total_cents = to_cents(total)
    if total_cents <= 0:
        raise InvalidAmount(f"分摊总额必须为正数「分」，收到 {total!r}")

    if not weights:
        raise InvalidAmount("weights 不能为空：至少需要一个收款方")

    parts: list[Fraction] = []
    for i, weight in enumerate(weights):
        if isinstance(weight, bool) or not isinstance(weight, (int, float)):
            raise InvalidAmount(f"weights[{i}] 必须是数字，收到 {weight!r}")
        if weight != weight:  # NaN
            raise InvalidAmount(f"weights[{i}] 不能是 NaN")
        if weight < 0:
            raise InvalidAmount(f"weights[{i}] 不能为负：{weight!r}")
        parts.append(Fraction(weight))

    total_weight = sum(parts, Fraction(0))
    if total_weight <= 0:
        raise InvalidAmount("权重之和必须为正，不能把整笔钱分给零权重的各方")

    # 精确有理数份额：不做任何 float 累加
    exact = [Fraction(total_cents) * part / total_weight for part in parts]
    cents = [math.floor(share) for share in exact]

    # 余数按「小数部分降序、索引升序」分配，保证一分不丢
    remainder = total_cents - sum(cents)
    order = sorted(
        range(len(parts)),
        key=lambda i: (-(exact[i] - cents[i]), i),
    )
    for i in order[:remainder]:
        cents[i] += 1

    return [from_cents(c) for c in cents]
