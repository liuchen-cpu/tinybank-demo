# agent-workflow-demo

一个刻意做小的仓库，用来演示「让 agent 真正干活」的最小闭环：

```
issue（任务规格 + 验收标准）
   ↓  scripts/start-task.ps1 开分支，把验收标准摊在眼前
先写失败测试（红）
   ↓
改实现 → 测试转绿
   ↓
git commit（pre-commit 跑全量测试，红了进不来）
   ↓
scripts/ship-task.ps1：再跑测试 → 推分支 → 按模板开 PR
   ↓
PR + CI 双版本矩阵 → main 保护放行 → 合并
```

## 跑测试

```powershell
python -m unittest discover -s tests -t . -v
```

零依赖，Python 3.10+。

## 目录

| 路径 | 作用 |
| --- | --- |
| `tinybank/core.py` | 账户与金额转换（整数分） |
| `tinybank/allocate.py` | 按权重分摊（Fraction 精确计算，余数按小数部分分配） |
| `tests/` | 回归测试 |
| `issues/` | 任务规格，agent 的「需求来源」 |
| `scripts/start-task.ps1` | 开工：校验工作区干净 → 拉最新 main → 建分支 → 打印 issue 验收标准 |
| `scripts/ship-task.ps1` | 收工：跑全量测试 → 推分支 → 按 PR 模板开 PR |
| `scripts/install-hooks.ps1` | 启用仓库自带的 pre-commit 钩子（每个 clone 一次） |
| `.githooks/pre-commit` | 钩子本体：`compileall` + 全量测试，red 就拦在提交前 |
| `.github/workflows/ci.yml` | 客观裁判：Python 3.10/3.12 矩阵跑语法检查 + 全量测试 |
| `.github/dependabot.yml` | 第三方 action 锁了 SHA，升级由它开 PR |
| `AGENTS.md` | 常驻说明书：约定、工作流、完成定义、禁区 |

## 结构要点

- **git 是后悔药**：每个任务一条分支，改坏了 `git restore` 就回到干净状态。
- **CI 是裁判**：`完成` 不是 agent 说完成，是测试绿了。main 有分支保护，直推会被 GH006 拒绝。
- **AGENTS.md 是护栏**：命令、约定、禁区写死在仓库里，比每次口头交代可靠。
- **两条命令一个任务**：`start-task` 管开工，`ship-task` 管收工，中间只有「先红后绿」这一件事。
