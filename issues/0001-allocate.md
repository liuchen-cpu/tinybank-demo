# 0001 · 实现按权重分摊 allocate()

**类型**：feat　**优先级**：P1　**标签**：`money` `exact-math`

## 背景

用户要把一笔钱按权重拆给多个收款方（分账、AA 制、按比例分佣金）。
现在的代码里只有接口声明（`tinybank/allocate.py`），调用会抛 `NotImplementedError`。

## 需求

```python
allocate(total: float, weights: Sequence[float]) -> list[float]
```

把 `total`（元）按 `weights` 分摊，返回每一方拿到的金额（元），长度等于 `len(weights)`。

## 验收标准

1. **一分钱都不能丢**：对任意合法输入，`sum(round(p * 100) for p in result)` 必须严格等于 `round(total * 100)`。
2. 余数（除不尽的那些「分」）按**小数部分从大到小**分配；小数部分相同时，索引小的优先。
   - 例：`allocate(100, [1, 1, 1])` → `[33.34, 33.33, 33.33]`
3. 权重为 0 的一方拿到 `0.0`；权重之和为 0 视为非法输入。
4. 非法输入抛 `InvalidAmount`：`total <= 0`、`weights` 为空、任一权重为负、权重之和为 0、金额精度超过 2 位小数。
5. 内部必须用整数 / `Fraction` 计算，禁止 float 累加。
6. 现有测试全部通过，不新增依赖。

## 非目标

- 不做币种换算
- 不做手续费
- 不改 `Account` 的接口
