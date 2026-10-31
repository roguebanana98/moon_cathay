# User authorized a private local pack containing derived IEE startpos/DB data.
# Does not deploy to game/Workshop, launch gameplay, or publish.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$cfg = Get-Content -LiteralPath (Join-Path $root 'config/local.json') -Raw | ConvertFrom-Json
& (Join-Path $PSScriptRoot 'Verify-Dependencies.ps1')
$candidateDir = Join-Path $root 'build/province-edit'
$report = Get-Content (Join-Path $candidateDir 'candidate-report.json') -Raw | ConvertFrom-Json
$startpos = Join-Path $candidateDir 'province-candidate.esf'
if ((Get-FileHash $startpos).Hash.ToLowerInvariant() -ne $report.output_sha256) { throw 'Candidate hash mismatch' }
$buildId = [Guid]::NewGuid().ToString('N')
$pack = Join-Path $candidateDir ('mc_longvi_8slots_test_' + $buildId + '.pack')
function Invoke-Rpfm {
    param([string[]]$Arguments)
    & $cfg.rpfm -g warhammer_3 @Arguments
    if ($LASTEXITCODE -ne 0) { throw "RPFM failed: $Arguments" }
}
Invoke-Rpfm @('pack','create','-p',$pack)
foreach ($dependency in @($cfg.mixer,$cfg.iee)) {
    Invoke-Rpfm @('pack','add-dependency-pack','-p',$pack,'-d',[IO.Path]::GetFileName($dependency))
}
foreach ($entry in @(
    @('region_to_province_junctions_tables','!cr_map_expansion'),
    @('regions_to_region_groups_junctions_tables','!cr_map_expansion_province')
)) {
    $internal = 'db/' + $entry[0] + '/' + $entry[1]
    $source = Join-Path $candidateDir ($internal + '.tsv')
    Invoke-Rpfm @('pack','add','-p',$pack,'-t',$cfg.schema,'-f',($source + ';' + $internal))
}
Invoke-Rpfm @('pack','add','-p',$pack,'-f',($startpos + ';campaigns/cr_combi_expanded/startpos.esf'))
$buildings = Get-Content (Join-Path $candidateDir 'long-vi-buildings-report.json') -Raw | ConvertFrom-Json
foreach ($internal in $buildings.files) {
    $source = Join-Path $candidateDir ($internal + '.tsv')
    Invoke-Rpfm @('pack','add','-p',$pack,'-t',$cfg.schema,'-f',($source + ';' + $internal))
}
Invoke-Rpfm @('pack','list','-p',$pack)
$verifyDir = Join-Path $root ('reference/local/province-pack-check/' + $buildId)
New-Item -ItemType Directory -Path $verifyDir -Force | Out-Null
Invoke-Rpfm @('pack','extract','-p',$pack,'-t',$cfg.schema,'-F',('/;' + $verifyDir))
$manifest = [ordered]@{
    pack = $pack
    sha256 = (Get-FileHash $pack).Hash.ToLowerInvariant()
    verification_directory = $verifyDir
    status = 'built_pending_static_verification_not_game_tested'
    private_local_only = $true
    deployed = $false
}
$manifest | ConvertTo-Json | Set-Content (Join-Path $candidateDir 'pack-manifest.json') -Encoding utf8
Write-Output ($manifest | ConvertTo-Json)
