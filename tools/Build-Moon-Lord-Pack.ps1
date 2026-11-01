$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
& (Join-Path $PSScriptRoot 'Verify-Dependencies.ps1')
$out=Join-Path $root 'build/moon-lord'
$pack=Join-Path $out 'mc_moon_warden_v1_test.pack'
if(Test-Path -LiteralPath $pack) { throw "Refusing to overwrite $pack" }
Copy-Item -LiteralPath (Join-Path $root 'build/longvi-tiered/mc_longvi_v3_tiered_capital.pack') -Destination $pack
$report=Get-Content (Join-Path $out 'lord-report.json') -Raw | ConvertFrom-Json
foreach($internal in $report.files) {
    & $cfg.rpfm -g warhammer_3 pack add -p $pack -t $cfg.schema -f ((Join-Path $out ($internal+'.tsv'))+';'+$internal)
    if($LASTEXITCODE -ne 0) { throw "Import failed: $internal" }
}
& $cfg.rpfm -g warhammer_3 pack add -p $pack -f ((Join-Path $out 'startpos.esf')+';campaigns/cr_combi_expanded/startpos.esf')
if($LASTEXITCODE -ne 0) { throw 'Startpos import failed' }
$verify=Join-Path $root 'reference/local/moon-lord-check'
New-Item -ItemType Directory -Path $verify -Force | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0) { throw 'Extract failed' }
@{pack=$pack;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false;verification_directory=$verify} | ConvertTo-Json | Set-Content (Join-Path $out 'pack-manifest.json') -Encoding utf8
