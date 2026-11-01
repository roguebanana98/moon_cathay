$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
$out=Join-Path $root 'build/moon-lord-spell-ranks'
$pack=Join-Path $out 'mc_moon_warden_v11_spell_progression.pack'
if(Test-Path -LiteralPath $pack) { throw 'Destination exists' }
Copy-Item -LiteralPath (Join-Path $root 'build/moon-lord-spell-ranks/mc_moon_warden_v10_spell_ranks.pack') -Destination $pack
$report=Get-Content (Join-Path $out 'lord-report.json') -Raw | ConvertFrom-Json
foreach($internal in $report.files) {
 if($internal -like 'db/character_skill_level_to_effects_junctions_tables/*' -or $internal -like 'db/battle_set_piece_armies_characters_skillsets_skills_tables/*') { continue }
 & $cfg.rpfm -g warhammer_3 pack add -p $pack -t $cfg.schema -f ((Join-Path $out ($internal+'.tsv'))+';'+$internal)
 if($LASTEXITCODE -ne 0) { throw "Import failed: $internal" }
}
$verify=Join-Path $root 'reference/local/moon-lord-v11-check'
New-Item -ItemType Directory -Path $verify -Force | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0) { throw 'Extract failed' }
& $cfg.rpfm -g warhammer_3 pack diagnose -g $cfg.game -P (Join-Path $root 'reference/local/wh3-diagnostics.pak2') -s $cfg.schema -p $pack *> (Join-Path $out 'v11-diagnostics.txt')
if($LASTEXITCODE -ne 0) { throw 'Diagnose failed' }
@{pack=$pack;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false;verification_directory=$verify} | ConvertTo-Json | Set-Content (Join-Path $out 'v11-manifest.json') -Encoding utf8

