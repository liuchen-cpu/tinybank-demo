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
2. `powershell -ExecutionPolicy Bypass -File scripts/start-task.ps1 -Type <feat|fix|refactor|docs|chore> -Slug <slug> [-Issue 0001]`
   （等价于从最新 main 切一个 `<type>/<slug>` 分支，顺手把 issue 的验收标准打出来）。
3. **先写测试**，跑一次确认它是红的（否则你不知道测试是否真的在测东西）。
4. 写最少量的实现让测试变绿。
5. 跑全量测试，确认没有回归。
6. 提交，风格：`<type>: <一句话>`，正文写「为什么」和「怎么验的」。
7. 收工一条命令：`powershell -ExecutionPolicy Bypass -File scripts/ship-task.ps1 -Title "<type>: <一句话>" -What "改了什么" -Why "为什么" -Verify "怎么验的"`。
   它会再跑一遍全量测试（绿了才推）、推分支、按模板开 PR。CI 不绿是合不进去的。

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

两条容易踩的：

- **fail-closed**：本机没有 `python` 时钩子直接拒绝提交（而不是跳过）。目的是不让没测过的代码进历史；
  确实要临时绕过是 `git commit --no-verify`，但那种提交在 PR 里要说明为什么。
- **可执行位**：`.githooks/pre-commit` 在索引里必须是 `100755`。macOS/Linux 上如果克隆下来丢了执行权限，
  git 会静默跳过钩子——CI 里有一条 `test -x .githooks/pre-commit` 专门守这个，别把它删了。

## 换行符

`.gitattributes` 已统一为 LF（`.ps1` / `.cmd` / `.bat` 除外，保留 CRLF）。
不要把文件改成 CRLF 提交——那会让 diff 变成「整文件重写」，review 时看不出真正改了哪行。

## 供应链：第三方 action 锁 SHA

`.github/workflows/ci.yml` 里的 `actions/checkout`、`actions/setup-python` 都锁到 **commit SHA**，
后面用注释标着人类可读的版本号。原因：tag 可以被改写，SHA 不能——万一上游仓库被改名/改写，
线上 CI 跑的还是你当初审过的那份代码。

升级**不要手动改 SHA**：`.github/dependabot.yml` 每周会自动开 PR 提版本，
照常看 diff、等两个检查绿、点合并即可。

## 分支保护

`main` 已开启保护（strict 模式）：必须走 PR，且 `test (3.10)` / `test (3.12)` 两个检查都绿才能合并；
要求线性历史，管理员同样受约束（`enforce_admins`），不允许 force push 和删除分支。

本地 `git push origin main` 被拒绝是**预期行为**，不是故障——请在分支上工作。典型报错：

```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: - Changes must be made through a pull request.
remote: - 2 of 2 required status checks are expected.
```

**这个仓库为什么是 public**：GitHub 免费账户下私有仓库开不了分支保护，API 会直接回
`403 Upgrade to GitHub Pro or make this repository public to enable this feature`。
本仓库没有密钥和真实数据，所以用公开换免费的护栏。如果哪天要转回私有，护栏会一并消失，
需要先确认能接受「只靠本地 pre-commit 把关」。

## 禁区

- 不要 `git push --force` 到 `main`。
- 不要提交密钥、token、`.env`、`__pycache__`。
- 测试变绿只能靠改**实现**，不能靠改**断言**。想让断言改，先说明为什么原断言是错的。
