# 启用仓库自带的 git 钩子（每个 clone 只需跑一次）。
# 之所以用 core.hooksPath 而不是往 .git/hooks 里拷文件：
# .githooks/ 会跟着仓库走，agent 换机器也不用重新教。

$ErrorActionPreference = 'Stop'

$root = git rev-parse --show-toplevel
if (-not $root) { throw "这里不是 git 仓库" }

git -C $root config core.hooksPath .githooks
Write-Output "已启用 pre-commit 钩子"
Write-Output ("core.hooksPath = " + (git -C $root config --get core.hooksPath))
Write-Output "下次 git commit 会自动先跑测试，红了会被拦下。"
