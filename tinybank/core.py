"""tinybank —— 演示用的最小账务内核。

设计约束（见 AGENTS.md）：
- 所有金额以「分」为单位的整数存储，禁止用 float 做累计。
- 对外接口接受 float 元，只在系统边界转换一次。
"""

from __future__ import annotations


class TinyBankError(Exception):
    """业务异常基类。"""


class InvalidAmount(TinyBankError):
    """金额非法：非数字、NaN、负值，或精度超过 2 位小数。"""


class InsufficientFunds(TinyBankError):
    """余额不足。"""


def to_cents(amount: float) -> int:
    """元 -> 分。纯转换，不做正负校验；仅在系统边界调用一次。"""
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise InvalidAmount(f"金额必须是数字，收到 {amount!r}")
    if amount != amount:  # NaN
        raise InvalidAmount("金额不能是 NaN")
    cents = round(amount * 100)
    if abs(amount * 100 - cents) > 1e-6:
        raise InvalidAmount(f"金额精度超过 2 位小数：{amount!r}")
    return int(cents)


def from_cents(cents: int) -> float:
    """分 -> 元。"""
    return cents / 100


class Account:
    """一个账户。内部只保存整数分。"""

    __slots__ = ("name", "_cents")

    def __init__(self, name: str, balance: float = 0.0) -> None:
        if not name:
            raise TinyBankError("账户名不能为空")
        self.name = name
        self._cents = 0
        if balance:
            self.deposit(balance)

    @property
    def balance(self) -> float:
        return from_cents(self._cents)

    @property
    def balance_cents(self) -> int:
        return self._cents

    def deposit(self, amount: float) -> int:
        cents = self._require_positive(amount)
        self._cents += cents
        return self._cents

    def withdraw(self, amount: float) -> int:
        cents = self._require_positive(amount)
        if cents > self._cents:
            raise InsufficientFunds(
                f"{self.name} 余额不足：需要 {from_cents(cents)}，只有 {self.balance}"
            )
        self._cents -= cents
        return self._cents

    def transfer(self, target: "Account", amount: float) -> int:
        """转账。先校验、后落实，避免只成功一半。"""
        if target is self:
            raise TinyBankError("不能转账给自己")
        cents = self._require_positive(amount)
        if cents > self._cents:
            raise InsufficientFunds(
                f"{self.name} 余额不足：需要 {from_cents(cents)}，只有 {self.balance}"
            )
        self._cents -= cents
        target._cents += cents
        return self._cents

    @staticmethod
    def _require_positive(amount: float) -> int:
        cents = to_cents(amount)
        if cents <= 0:
            raise InvalidAmount(f"金额必须为正数，收到 {amount!r}")
        return cents

    def __repr__(self) -> str:
        return f"Account({self.name!r}, balance={self.balance})"
