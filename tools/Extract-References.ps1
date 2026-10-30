# Read-only source operations. Exports are private local reference material.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg = Get-Content -LiteralPath (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
foreach ($name in 'iee','mixer') {
    $out = Join-Path $root "reference/local/$name"
    New-Item -ItemType Directory -Path $out -Force | Out-Null
    & $cfg.rpfm -g warhammer_3 pack extract -p $cfg.$name -t $cfg.schema -F "db;$out" "text;$out" "script;$out" 2>&1 |
        Tee-Object -FilePath (Join-Path $root "reports/$name-extraction.log")
    if ($LASTEXITCODE -ne 0) { throw "Extraction failed: $name" }
}
$out = Join-Path $root 'reference/local/iee'
& $cfg.rpfm -g warhammer_3 pack extract -p $cfg.iee -f "campaigns/cr_combi_expanded/startpos.esf;$out"
if ($LASTEXITCODE -ne 0) { throw 'Startpos extraction failed' }
