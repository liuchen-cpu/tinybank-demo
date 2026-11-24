<#
.SYNOPSIS
  收工：确认测试绿 → 推分支 → 按模板开 PR。CI 不过就合不了（main 有保护）。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts/ship-task.ps1 -Title "feat: 支持按权重分摊" -Why "issue 0001" -Verify "18 tests OK"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$Title,

    [string]$What = '（未填，请补一句改了什么）',
    [string]$Why = '（未填，请补一句为什么）',
    [string]$Verify = '全量测试绿（见本 PR 的 CI 检查）',
    [string]$Risk = '无'
)

$ErrorActionPreference = 'Stop'

function Fail([string]$message) {
    Write-Host "[ship-task] $message" -ForegroundColor Red
    exit 1
}

$root = git rev-parse --show-toplevel 2>$null
if (-not $root) { Fail '当前目录不在 git 仓库里' }
Set-Location $root

$branch = git rev-parse --abbrev-ref HEAD
if ($branch -eq 'main') { Fail '不要从 main 收工——先用 scripts/start-task.ps1 开分支' }

$dirty = git status --porcelain
if ($dirty) { Fail "还有没提交的改动：`n$dirty" }

Write-Host '[ship-task] 全量测试' -ForegroundColor Cyan
python -m compileall -q tinybank tests
if ($LASTEXITCODE -ne 0) { Fail '语法检查没过，不推' }
python -m unittest discover -s tests -t . -q
if ($LASTEXITCODE -ne 0) { Fail '测试没绿，不推' }
Write-Host '[ship-task] 测试绿' -ForegroundColor Green

git push -q -u origin HEAD
if ($LASTEXITCODE -ne 0) { Fail '推不上去' }
Write-Host "[ship-task] 已推送 $branch" -ForegroundColor Green

$body = @"
## 改了什么

$What

## 为什么

$Why

## 怎么验证

$Verify

## 风险

$Risk

## 完成定义

- [x] 全量测试绿
- [x] 新增行为有对应的新测试
- [x] 没有新增依赖
- [x] 没有降低检查强度
- [x] 提交信息能让人不看 diff 也知道改了什么
"@

$bodyFile = Join-Path $env:TEMP 'ship-task-pr-body.md'
[IO.File]::WriteAllText($bodyFile, $body, (New-Object System.Text.UTF8Encoding($false)))
$url = gh pr create --base main --head $branch --title $Title --body-file $bodyFile
Remove-Item $bodyFile -Force -ErrorAction SilentlyContinue
if ($LASTEXITCODE -ne 0) { Fail 'PR 创建失败（已有同名 PR？没有 gh 登录？）' }

Write-Host "[ship-task] PR: $url" -ForegroundColor Green
Write-Host '[ship-task] 等 CI 绿后：gh pr merge --squash --delete-branch' -ForegroundColor Cyan
