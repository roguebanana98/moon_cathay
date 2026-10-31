# Keep the runtime-confirmed v2 startpos; replace only Long Vi building tables.
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
& (Join-Path $PSScriptRoot 'Verify-Dependencies.ps1')
$out=Join-Path $root 'build/longvi-tiered'
$pack=Join-Path $out 'mc_longvi_v3_tiered_capital.pack'
if(Test-Path -LiteralPath $pack) { throw "Refusing to overwrite $pack" }
Copy-Item -LiteralPath (Join-Path $root 'build/province-array-fix/mc_longvi8_v2_uint32_fix.pack') -Destination $pack
$report=Get-Content (Join-Path $out 'long-vi-buildings-report.json') -Raw | ConvertFrom-Json
foreach($internal in $report.files) {
    $source=Join-Path $out ($internal+'.tsv')
    & $cfg.rpfm -g warhammer_3 pack add -p $pack -t $cfg.schema -f ($source+';'+$internal)
    if($LASTEXITCODE -ne 0) { throw "Failed to import $internal" }
}
$verify=Join-Path $root 'reference/local/longvi-tiered-check'
New-Item -ItemType Directory -Path $verify -Force | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0) { throw 'Extract failed' }
@{pack=$pack;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false;verification_directory=$verify} | ConvertTo-Json | Set-Content (Join-Path $out 'pack-manifest.json') -Encoding utf8
