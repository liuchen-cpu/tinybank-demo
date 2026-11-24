# agent-workflow-demo

一个刻意做小的仓库，用来演示「让 agent 真正干活」的最小闭环：

```
issue（任务规格 + 验收标准）
   ↓  agent 开分支
先写失败测试（红）
   ↓
改实现 → 测试转绿
   ↓
git commit（小步、说明为什么）
   ↓
PR + CI 判定 → 人 review → 合并
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
| `tinybank/allocate.py` | 按权重分摊，**当前未实现** |
| `tests/` | 回归测试 |
| `issues/` | 任务规格，agent 的「需求来源」 |
| `AGENTS.md` | 常驻说明书：约定、工作流、完成定义 |
| `.github/workflows/ci.yml` | 客观裁判：语法检查 + 全量测试 |

## 结构要点

- **git 是后悔药**：每个任务一条分支，改坏了 `git restore` 就回到干净状态。
- **CI 是裁判**：`完成` 不是 agent 说完成，是测试绿了。
- **AGENTS.md 是护栏**：命令、约定、禁区写死在仓库里，比每次口头交代可靠。
