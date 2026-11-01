# Narrow repair: preserve every payload except the two forbidden DB tables.
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
$out=Join-Path $root 'build/moon-lord'
$source=Join-Path $out 'mc_moon_warden_v1_test.pack'
$pack=Join-Path $out 'mc_moon_warden_v2_startup_fix.pack'
if(Test-Path -LiteralPath $pack) { throw "Refusing to overwrite $pack" }
Copy-Item -LiteralPath $source -Destination $pack
foreach($table in @('agent_subtype_ownership_content_pack_junctions_tables','main_unit_ownership_content_pack_junctions_tables')) {
    & $cfg.rpfm -g warhammer_3 pack delete -p $pack -f ('db/'+$table+'/mc_moon_warden')
    if($LASTEXITCODE -ne 0) { throw "Remove failed: $table" }
}
$verify=Join-Path $root 'reference/local/moon-lord-v2-check'
New-Item -ItemType Directory -Path $verify -Force | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0) { throw 'Extract failed' }
@{pack=$pack;original_pack=$source;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false;verification_directory=$verify} | ConvertTo-Json | Set-Content (Join-Path $out 'pack-manifest.json') -Encoding utf8
