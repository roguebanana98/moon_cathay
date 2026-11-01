param([switch]$Rebuild)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
& (Join-Path $PSScriptRoot 'Verify-Dependencies.ps1')
$iconReference=Join-Path $root 'reference/local/huyen-ve-native-icons'
New-Item -ItemType Directory -Path $iconReference -Force | Out-Null
foreach($name in @('wh_magic_item_passive_talisman','wh_main_character_abilities_arcane_conduit','wh3_dlc27_character_abilities_the_black_tongue')) {
 & $cfg.rpfm -g warhammer_3 pack extract -p (Join-Path $cfg.game 'data/ui.pack') -f ('ui/battle ui/ability_icons/'+$name+'.png;'+$iconReference)
 if($LASTEXITCODE -ne 0) { throw "Native icon extraction failed: $name" }
}
& $cfg.python (Join-Path $PSScriptRoot 'Prepare-Huyen-Ve-Equipment.py')
if($LASTEXITCODE -ne 0) { throw 'Equipment preparation failed' }
$out=Join-Path $root 'build/huyen-ve-equipment'
$pack=Join-Path $out 'mc_huyen_ve_v14_native_icons.pack'
if((Test-Path -LiteralPath $pack) -and -not $Rebuild) { throw 'Destination exists; use -Rebuild for this generated artifact' }
Copy-Item -LiteralPath (Join-Path $root 'build/huyen-ve-name/mc_huyen_ve_v12_name.pack') -Destination $pack -Force
$report=Get-Content (Join-Path $out 'equipment-report.json') -Raw | ConvertFrom-Json
foreach($internal in $report.files) {
 if($internal.StartsWith('db/') -or $internal.EndsWith('.loc')) {
  & $cfg.rpfm -g warhammer_3 pack add -p $pack -t $cfg.schema -f ((Join-Path $out ($internal+'.tsv'))+';'+$internal)
 } else {
  & $cfg.rpfm -g warhammer_3 pack add -p $pack -f ((Join-Path $out $internal)+';'+$internal)
 }
 if($LASTEXITCODE -ne 0) { throw "Import failed: $internal" }
}
$verify=Join-Path $root 'reference/local/huyen-ve-v14-check'
New-Item -ItemType Directory -Path $verify -Force | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0) { throw 'Extract failed' }
& $cfg.rpfm -g warhammer_3 pack diagnose -g $cfg.game -P (Join-Path $root 'reference/local/wh3-diagnostics.pak2') -s $cfg.schema -p $pack *> (Join-Path $out 'diagnostics.txt')
if($LASTEXITCODE -ne 0) { throw 'Diagnose failed' }
@{pack=$pack;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false;verification_directory=$verify} | ConvertTo-Json | Set-Content (Join-Path $out 'manifest.json') -Encoding utf8
& $cfg.python (Join-Path $PSScriptRoot 'Validate-Huyen-Ve-Equipment.py')
if($LASTEXITCODE -ne 0) { throw 'Equipment validation failed' }
