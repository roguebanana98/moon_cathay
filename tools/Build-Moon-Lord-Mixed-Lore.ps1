$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
$out=Join-Path $root 'build/moon-lord-custom-battle'
$pack=Join-Path $out 'mc_moon_warden_v5_mixed_lore_fix.pack'
if(Test-Path -LiteralPath $pack) { throw 'Destination exists' }
Copy-Item -LiteralPath (Join-Path $out 'mc_moon_warden_v4_custom_battle.pack') -Destination $pack
foreach($table in @('special_ability_groups_tables','special_ability_groups_to_unit_abilities_junctions_tables')) {
 $internal='db/'+$table+'/mc_moon_warden'
 $source=Join-Path $root ('build/moon-lord/'+$internal+'.tsv')
 & $cfg.rpfm -g warhammer_3 pack add -p $pack -t $cfg.schema -f ($source+';'+$internal)
 if($LASTEXITCODE -ne 0) { throw "Import failed: $internal" }
}
$verify=Join-Path $root 'reference/local/moon-lord-v5-check'
New-Item -ItemType Directory -Path $verify -Force | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0) { throw 'Extract failed' }
& $cfg.rpfm -g warhammer_3 pack diagnose -g $cfg.game -P (Join-Path $root 'reference/local/wh3-diagnostics.pak2') -s $cfg.schema -p $pack *> (Join-Path $out 'v5-diagnostics.txt')
if($LASTEXITCODE -ne 0) { throw 'Diagnose failed' }
@{pack=$pack;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false;verification_directory=$verify} | ConvertTo-Json | Set-Content (Join-Path $out 'v5-manifest.json') -Encoding utf8
