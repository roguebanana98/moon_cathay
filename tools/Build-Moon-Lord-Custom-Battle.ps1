$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
$out=Join-Path $root 'build/moon-lord-custom-battle'
$pack=Join-Path $out 'mc_moon_warden_v4_custom_battle.pack'
if(Test-Path -LiteralPath $pack) { throw 'Destination exists' }
Copy-Item -LiteralPath (Join-Path $root 'build/moon-lord/mc_moon_warden_v3_name_fix.pack') -Destination $pack
$report=Get-Content (Join-Path $out 'report.json') -Raw | ConvertFrom-Json
foreach($internal in $report.files) {
 & $cfg.rpfm -g warhammer_3 pack add -p $pack -t $cfg.schema -f ((Join-Path $out ($internal+'.tsv'))+';'+$internal)
 if($LASTEXITCODE -ne 0) { throw "Import failed: $internal" }
}
$verify=Join-Path $root 'reference/local/moon-lord-v4-check'
New-Item -ItemType Directory -Path $verify -Force | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0) { throw 'Extract failed' }
& $cfg.rpfm -g warhammer_3 pack diagnose -g $cfg.game -P (Join-Path $root 'reference/local/wh3-diagnostics.pak2') -s $cfg.schema -p $pack *> (Join-Path $out 'diagnostics.txt')
if($LASTEXITCODE -ne 0) { throw 'Diagnose failed' }
@{pack=$pack;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false;verification_directory=$verify} | ConvertTo-Json | Set-Content (Join-Path $out 'manifest.json') -Encoding utf8
