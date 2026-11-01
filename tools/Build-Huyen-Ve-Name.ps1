$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
& (Join-Path $PSScriptRoot 'Verify-Dependencies.ps1')
& $cfg.python (Join-Path $PSScriptRoot 'Prepare-Huyen-Ve-Name.py')
if($LASTEXITCODE -ne 0) { throw 'Name preparation failed' }
$out=Join-Path $root 'build/huyen-ve-name'
$pack=Join-Path $out 'mc_huyen_ve_v12_name.pack'
if(Test-Path -LiteralPath $pack) { throw 'Destination exists' }
Copy-Item -LiteralPath (Join-Path $root 'build/moon-lord-spell-ranks/mc_moon_warden_v11_spell_progression.pack') -Destination $pack
$report=Get-Content (Join-Path $out 'name-report.json') -Raw | ConvertFrom-Json
foreach($internal in $report.files) {
 if($internal.EndsWith('.loc')) {
  & $cfg.rpfm -g warhammer_3 pack add -p $pack -t $cfg.schema -f ((Join-Path $out ($internal+'.tsv'))+';'+$internal)
 } else {
  & $cfg.rpfm -g warhammer_3 pack add -p $pack -f ((Join-Path $out $internal)+';'+$internal)
 }
 if($LASTEXITCODE -ne 0) { throw "Import failed: $internal" }
}
$verify=Join-Path $root 'reference/local/huyen-ve-v12-check'
New-Item -ItemType Directory -Path $verify -Force | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0) { throw 'Extract failed' }
& $cfg.rpfm -g warhammer_3 pack diagnose -g $cfg.game -P (Join-Path $root 'reference/local/wh3-diagnostics.pak2') -s $cfg.schema -p $pack *> (Join-Path $out 'diagnostics.txt')
if($LASTEXITCODE -ne 0) { throw 'Diagnose failed' }
@{pack=$pack;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false;verification_directory=$verify} | ConvertTo-Json | Set-Content (Join-Path $out 'manifest.json') -Encoding utf8
& $cfg.python (Join-Path $PSScriptRoot 'Validate-Huyen-Ve-Name.py')
if($LASTEXITCODE -ne 0) { throw 'Name validation failed' }
