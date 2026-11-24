<#
.SYNOPSIS
  开工：从最新的 main 拉一个任务分支，并把 issue 的验收标准摊在眼前。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts/start-task.ps1 -Type feat -Slug allocate -Issue 0001
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateSet('feat', 'fix', 'refactor', 'docs', 'chore')]
    [string]$Type,

    [Parameter(Mandatory)]
    [ValidatePattern('^[a-z0-9][a-z0-9-]*$')]
    [string]$Slug,

    [string]$Issue = ''
)

$ErrorActionPreference = 'Stop'

function Fail([string]$message) {
    Write-Host "[start-task] $message" -ForegroundColor Red
    exit 1
}

$root = git rev-parse --show-toplevel 2>$null
if (-not $root) { Fail '当前目录不在 git 仓库里' }
Set-Location $root

$branch = "$Type/$Slug"
if (git branch --list $branch) { Fail "分支 $branch 已存在，换个 slug 或者先处理掉它" }

$dirty = git status --porcelain
if ($dirty) { Fail "工作区不干净，先提交或 stash：`n$dirty" }

git switch -q main
if ($LASTEXITCODE -ne 0) { Fail '切不回 main' }
git pull -q --ff-only origin main
if ($LASTEXITCODE -ne 0) { Fail 'main 拉不下来（本地有分叉？先处理）' }

git switch -q -c $branch
if ($LASTEXITCODE -ne 0) { Fail "建分支 $branch 失败" }

Write-Host "[start-task] 已在 $branch 上开工" -ForegroundColor Green

if ($Issue) {
    $file = Join-Path $root "issues/$Issue.md"
    if (Test-Path $file) {
        Write-Host "[start-task] 验收标准来自 issues/$Issue.md：" -ForegroundColor Cyan
        Get-Content $file | Where-Object { $_ -match '^#|验收|标准' } | ForEach-Object { Write-Host "  $_" }
    }
    else {
        Write-Host "[start-task] 没找到 issues/$Issue.md，记得把验收标准写进 PR 描述" -ForegroundColor Yellow
    }
}

Write-Host ''
Write-Host '[start-task] 接下来的顺序（AGENTS.md 里有完整版）：' -ForegroundColor Cyan
Write-Host '  1. 先写测试，跑一次确认它是红的'
Write-Host '  2. 写最少量的实现让它变绿'
Write-Host '  3. 提交（pre-commit 会跑全量测试）'
Write-Host '  4. powershell -ExecutionPolicy Bypass -File scripts/ship-task.ps1 -Title "<type>: <一句话>"'
