$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') | ConvertFrom-Json
$out=Join-Path $root 'build/huyen-ve-model-v1'
& $cfg.python (Join-Path $PSScriptRoot 'Prepare-Huyen-Ve-Model-Graph.py')
if($LASTEXITCODE -ne 0){throw 'Model graph failed'}
& $cfg.python (Join-Path $PSScriptRoot 'Validate-Huyen-Ve-Model.py')
if($LASTEXITCODE -ne 0){throw 'Export checks failed'}
$roundtrip=Get-Content (Join-Path $out 'roundtrip-validation.json') | ConvertFrom-Json
if($roundtrip.status -ne 'passed'){throw 'RMV2 roundtrip has not passed'}
$bodyHash=(Get-FileHash -LiteralPath (Join-Path $out 'variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/mc_huyen_ve_body.rigid_model_v2')).Hash.ToLowerInvariant()
if($roundtrip.rmv2_sha256 -ne $bodyHash){throw 'RMV2 changed since roundtrip validation; rerun Verify-Huyen-Ve-Roundtrip.py'}
$pack=Join-Path $out 'mc_huyen_ve_model_v1_assets.pack'
if(Test-Path -LiteralPath $pack){throw "Refusing to overwrite $pack"}
& $cfg.rpfm -g warhammer_3 pack create -p $pack
if($LASTEXITCODE -ne 0){throw 'Pack creation failed'}
$manifest=Get-Content (Join-Path $out 'graphics-manifest.json') | ConvertFrom-Json
foreach($internal in $manifest.files){
    & $cfg.rpfm -g warhammer_3 pack add -p $pack -f ((Join-Path $out $internal)+';'+$internal)
    if($LASTEXITCODE -ne 0){throw "Import failed: $internal"}
}
$verify=Join-Path $root 'reference/local/huyen-ve-model-v1-check'
New-Item -ItemType Directory -Force $verify | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -F ('/;'+$verify)
if($LASTEXITCODE -ne 0){throw 'Pack extraction failed'}
foreach($internal in $manifest.files){
    $original=(Get-FileHash -LiteralPath (Join-Path $out $internal)).Hash
    $packed=(Get-FileHash -LiteralPath (Join-Path $verify $internal)).Hash
    if($original -ne $packed){throw "Pack payload differs: $internal"}
}
@{pack=$pack;sha256=(Get-FileHash $pack).Hash.ToLowerInvariant();files=$manifest.files.Count;
  payload_roundtrip='all 16 hashes match';deployed=$false;gameplay_tables=$false;runtime_verified=$false;
  scope='Graphics-only inspection pack; does not replace the live Lord model until explicitly linked by a separate integration'} |
    ConvertTo-Json | Set-Content (Join-Path $out 'pack-manifest.json')
Write-Output "Created $pack"
