# AGENTS.md

给 agent（和新人）的常驻说明书。改动行为前先读完这一页。

## 项目是什么

`tinybank` 是一个刻意做小的账务内核，用来演示「agent + git + CI」的闭环：
issue 出题 → agent 开分支 → 先写失败测试 → 改实现 → 测试转绿 → 提交 → PR。

## 跑起来（只有这一条命令）

```powershell
python -m unittest discover -s tests -t . -v
```

⚠️ 没有第三方依赖，**不要** `pip install` 任何东西，也**不要**加 `requirements.txt`。

## 代码约定

- 金额在内部**只以「分」为单位的 int 存储**；float 只允许出现在对外接口的边界上，且只能转换一次（`to_cents` / `from_cents`）。
- 任何涉及钱的计算都不许用 float 累加；需要精确比例时用 `fractions.Fraction`。
- 业务错误继承 `TinyBankError`，不要直接 `raise ValueError`。
- 公共函数要有 docstring，说明输入、输出和失败条件。

## 工作流（按顺序，不许跳步）

1. 读 issue，把**验收标准**抄进分支说明。
2. `git switch -c <type>/<slug> main`（type: `feat` / `fix` / `refactor`）。
3. **先写测试**，跑一次确认它是红的（否则你不知道测试是否真的在测东西）。
4. 写最少量的实现让测试变绿。
5. 跑全量测试，确认没有回归。
6. 提交，风格：`<type>: <一句话>`，正文写「为什么」和「怎么验的」。
7. 输出 PR 描述：改了什么 / 怎么验证 / 风险。

## 完成定义（Definition of Done）

一个任务只有同时满足以下条件才算完成，缺一条就是没完成：

- [ ] 全量测试绿
- [ ] 新增行为有对应的新测试
- [ ] 没有新增依赖
- [ ] 没有降低检查强度（不许改 CI、不许 `skip`、不许放宽断言来让测试变绿）
- [ ] 提交信息能让人不看 diff 也知道改了什么

## 本地快速反馈（pre-commit）

首次 clone 后跑一次：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install-hooks.ps1
```

之后每次 `git commit` 会自动跑 `compileall` + 全量测试，红了直接拦在提交前，不用等 CI 往返。
钩子本体在 `.githooks/pre-commit`，跟着仓库走，换机器不用重新教。

## 换行符

`.gitattributes` 已统一为 LF（`.ps1` / `.cmd` / `.bat` 除外，保留 CRLF）。
不要把文件改成 CRLF 提交——那会让 diff 变成「整文件重写」，review 时看不出真正改了哪行。

## 分支保护

`main` 已开启保护：必须走 PR，且 `test (3.10)` / `test (3.12)` 两个检查都绿才能合并。
本地 `git push origin main` 被拒绝是**预期行为**，不是故障——请在分支上工作。

## 禁区

- 不要 `git push --force` 到 `main`。
- 不要提交密钥、token、`.env`、`__pycache__`。
- 测试变绿只能靠改**实现**，不能靠改**断言**。想让断言改，先说明为什么原断言是错的。
