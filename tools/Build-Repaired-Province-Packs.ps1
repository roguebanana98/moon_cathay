# Same two previously tested packs; replace only their repaired startpos payload.
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg=Get-Content (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
$out=Join-Path $root 'build/province-array-fix'
& (Join-Path $PSScriptRoot 'Verify-Dependencies.ps1')
$pairs=@(
    @('province_v2','mc_province_test_fee299cf08e14425b7402cbcb32261c0.pack'),
    @('longvi8_v2','mc_longvi_8slots_test_b2cbe56e484b44719ecd658a6ca36cc4.pack')
)
$manifest=@()
foreach($pair in $pairs) {
    $source=Join-Path $root ('build/province-edit/'+$pair[1])
    $destination=Join-Path $out ('mc_'+$pair[0]+'_uint32_fix.pack')
    if(Test-Path -LiteralPath $destination) { throw "Refusing to overwrite: $destination" }
    Copy-Item -LiteralPath $source -Destination $destination
    $esf=Join-Path $out ($pair[0]+'.esf')
    & $cfg.rpfm -g warhammer_3 pack add -p $destination -f ($esf+';campaigns/cr_combi_expanded/startpos.esf')
    if($LASTEXITCODE -ne 0) { throw 'Pack write failed' }
    $manifest+=@{label=$pair[0];original_pack=$source;pack=$destination;sha256=(Get-FileHash $destination).Hash.ToLowerInvariant();deployed=$false;runtime_verified=$false}
}
$manifest | ConvertTo-Json | Set-Content (Join-Path $out 'pack-manifest.json') -Encoding utf8
