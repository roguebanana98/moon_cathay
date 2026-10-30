# Phase 1: an EMPTY mod pack with dependency metadata only, never deployed.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg = Get-Content -LiteralPath (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
foreach ($p in @($cfg.rpfm, $cfg.iee, $cfg.mixer)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { throw "Missing verified input: $p" }
}
$buildDir = Join-Path $root 'build'
New-Item -ItemType Directory -Path $buildDir -Force | Out-Null
$pack = Join-Path $buildDir ('moon_cathay_phase1_' + [Guid]::NewGuid().ToString('N') + '.pack')
& $cfg.rpfm -g warhammer_3 pack create -p $pack
if ($LASTEXITCODE -ne 0) { throw 'Pack create failed' }
foreach ($dependency in @($cfg.mixer, $cfg.iee)) {
    & $cfg.rpfm -g warhammer_3 pack add-dependency-pack -p $pack -d ([IO.Path]::GetFileName($dependency))
    if ($LASTEXITCODE -ne 0) { throw 'Dependency metadata failed' }
}
& $cfg.rpfm -g warhammer_3 pack list -p $pack
if ($LASTEXITCODE -ne 0) { throw 'Pack reopen failed' }
Write-Output "Empty Phase 1 skeleton: $pack"
