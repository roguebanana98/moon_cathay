$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
& (Join-Path $PSScriptRoot 'Verify-Dependencies.ps1')
$out=Join-Path $root 'build/huyen-ve-animation-integration'
$base=Join-Path $root 'build/huyen-ve-equipment/mc_huyen_ve_v14_native_icons.pack'
$pack=Join-Path $out 'mc_huyen_ve_v15_model_animations.pack'
if(Test-Path -LiteralPath $pack){throw 'Refusing to overwrite the existing v15 pack'}
$scene=Get-Content (Join-Path $out 'scene-integration-report.json') | ConvertFrom-Json
if($scene.action_count -ne 89 -or -not $scene.body_mesh_and_weights_unchanged){throw 'Approved scene validation missing'}
$roundtrip=Get-Content (Join-Path $out 'animation-roundtrip-validation.json') | ConvertFrom-Json
if($roundtrip.status -ne 'passed' -or $roundtrip.clip_count -ne 89){throw 'Full animation roundtrip validation missing'}
foreach($entry in $roundtrip.hashes.psobject.Properties){
 $path=Join-Path $out ('variantmeshes/wh_variantmodels/hu1e/cth/mc_huyen_ve/'+$entry.Name)
 if((Get-FileHash -LiteralPath $path).Hash.ToLowerInvariant() -ne $entry.Value){throw ('Stale roundtrip for '+$entry.Name)}
}
Copy-Item -LiteralPath $base -Destination $pack
$links=Get-Content (Join-Path $out 'integration-links.json') | ConvertFrom-Json
foreach($internal in $links.files){
 if($internal.StartsWith('db/')){
  & $cfg.rpfm -g warhammer_3 pack add -p $pack -t $cfg.schema -f ((Join-Path $out ($internal+'.tsv'))+';'+$internal)
 }else{
  & $cfg.rpfm -g warhammer_3 pack add -p $pack -f ((Join-Path $out $internal)+';'+$internal)
 }
 if($LASTEXITCODE -ne 0){throw ('Import failed: '+$internal)}
}
$verify=Join-Path $root 'reference/local/huyen-ve-v15-check'
New-Item -ItemType Directory -Force -Path $verify | Out-Null
& $cfg.rpfm -g warhammer_3 pack extract -p $pack -t $cfg.schema -F ('/;'+$verify)
if($LASTEXITCODE -ne 0){throw 'v15 extraction failed'}
@{pack=$pack;sha256=(Get-FileHash -LiteralPath $pack).Hash.ToLowerInvariant();base_pack=$base;base_sha256=(Get-FileHash -LiteralPath $base).Hash.ToLowerInvariant();
 deployed=$false;runtime_verified=$false;verification_directory=$verify;scope='Private integrated model/animation links over v14; no native clip copies'} |
 ConvertTo-Json | Set-Content (Join-Path $out 'pack-manifest.json') -Encoding utf8
& $cfg.rpfm -g warhammer_3 pack diagnose -g $cfg.game -P (Join-Path $root 'reference/local/wh3-diagnostics.pak2') -s $cfg.schema -p $pack *> (Join-Path $out 'diagnostics.txt')
if($LASTEXITCODE -ne 0){throw 'v15 diagnostics failed'}
& $cfg.python (Join-Path $PSScriptRoot 'Validate-Huyen-Ve-Animation-Pack.py')
if($LASTEXITCODE -ne 0){throw 'v15 integration validation failed'}
Write-Output ('Created '+$pack)
