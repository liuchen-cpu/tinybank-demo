"""按权重分摊金额。

接口已由 issues/0001-allocate.md 约定，实现待补（当前会抛 NotImplementedError）。
"""

from __future__ import annotations

from typing import Sequence

from .core import InvalidAmount, from_cents, to_cents


def allocate(total: float, weights: Sequence[float]) -> list[float]:
    """把 total（元）按 weights 精确分摊给 len(weights) 方，返回每方金额（元）。

    硬性要求：返回值的「分」之和必须恒等于 total 的「分」，一分钱都不能丢。
    验收标准见 issues/0001-allocate.md。
    """
    raise NotImplementedError("allocate 尚未实现，见 issues/0001-allocate.md")
