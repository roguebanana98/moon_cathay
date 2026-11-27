"""Install the validated combined candidate beside existing packs; no launcher edits."""
import hashlib,json,os,shutil,sys,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/moon-v36-zhao-jade';v=json.loads((O/'validation.json').read_text());d=json.loads((O/'diagnostic-summary.json').read_text());a=json.loads((O/'asset-review.json').read_text())
assert v['design_passed'] and v['roundtrip_equal'] and v['original_v35_unchanged'] and v['all_unrelated_v35_payloads_byte_identical'] and v['all_approved_jade_v2_payloads_byte_identical']
assert not d['non_schema_issues'] and a['status']=='passed' and not a['warnings']
lua=json.loads((R/'build/toolchain-setup/lua-tests.json').read_text());assert any(x['test'].replace('\\','/').endswith('zhao-v36-migration.lua') and x['status']=='passed' for x in lua['results'])
pack=Path(v['pack'])
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(pack)==v['sha256']
dist=R/'dist/moon-v36-zhao-jade';dist.mkdir(parents=True,exist_ok=True)
game=Path('H:/SteamLibrary/steamapps/common/Total War WARHAMMER III/data');assert game.is_dir()
running=subprocess.run(['powershell','-NoProfile','-Command','@(Get-Process -Name Warhammer3 -ErrorAction SilentlyContinue).Count'],check=True,capture_output=True,text=True);assert running.stdout.strip()=='0','Close game before replacing a candidate'
previous=json.loads((O/'installation.json').read_text()) if (O/'installation.json').exists() else None
for target in [dist/pack.name,game/pack.name]:
 if target.exists():
  if sha(target)!=v['sha256']:
   assert '--replace-owned-candidate' in sys.argv and previous and sha(target)==previous['sha256'],'Do not overwrite another build'
   temp=target.with_name(target.name+'.v36.tmp');assert not temp.exists();shutil.copy2(pack,temp);assert sha(temp)==v['sha256'];os.replace(temp,target)
 else:shutil.copy2(pack,target)
 assert sha(target)==v['sha256']
report=dict(pack=pack.name,sha256=v['sha256'],bytes=v['bytes'],installed=str(game/pack.name),distribution=str(dist/pack.name),launcher_changed=False,enabled_by_tools=False,game_launched=False,runtime_verified=False,original_v35_unchanged=True,diagnostic_reference_definition_warnings=d['counts'],blocking_non_schema_diagnostics=0)
(O/'installation.json').write_text(json.dumps(report,indent=2));(dist/'installation.json').write_text(json.dumps(report,indent=2));(dist/'SHA256.txt').write_text(v['sha256']+'  '+pack.name+'\n')
for name in ['validation.json','design-manifest.json','diagnostic-summary.json','asset-review.json']:shutil.copy2(O/name,dist/name)
(dist/'README.txt').write_text('''MOON V36 — ZHAO REDESIGN + APPROVED JADE RESKIN FAMILY

Enable mc_moonshadow_heroes_v36_zhao_jade.pack in the launcher.
Disable older mc_moonshadow_heroes packs, including v35 if enabled, and standalone
mc_moon_jade_warriors_reskin_v1.pack / v2_family.pack: their contents are included.
Keep MIXER, IEE and the other IEE dependencies required by your campaign enabled.
Launcher selection/load order has not been changed by these tools.

Zhao: approved agile caster design, six Moon/Deep/Fire native spells, one Yin
passive, 54 visible nodes, six donor-budget uniques, one-of-four bound affinity,
native red/blue/common branches. Foot HP bonus4160, armour20, MA45/MD35,
charge20, damage210+90AP, run4.2. Mounts use corresponding native Shugengan
deltas, retain native mount movement, and unlock at displayed ranks5/15.
Foot body/sword/Yuan Bo animations remain unchanged. Mounted-only sword uses
a separate four-LOD hand attachment. No edited Blender montage is exported.

Moon-only Jade reskins: sword/shield, halberds, crossbows, shielded crossbows,
Jade Lancers. Approved body05/rear neckguard/brown boots and seven head options.
Sword/shield keeps the custom dao and round red 陳 shield. Other four types keep
their native equipment, horse and animation. All v2 asset bytes are retained.

Existing Mooncourt lords: one-time native skill reset if legacy private skills
are detected; no XP or extra skill-point grant. Background traits/identity kept,
old Command Seal removed, two basic spells and earned mount milestones restored.
Immortality follows the purchased rank20 skill. Script scope/idempotence tests
passed; actual engine refunds and old-save migration are not runtime verified.
Use a separate save when testing and check the first-load skill reset.

All unrelated v35 payloads match by SHA256; source v35 remains unchanged.
RPFM DB/loc roundtrip and design checks passed. 168 schema/cache reference-
definition warnings remain; no other RPFM diagnostic types after corrections.
45 Zhao sampled poses and actual mounted-sword four-LOD export checked; approved
unchanged Jade v2 animation checks reused. Full clipping and game runtime remain
unverified. No game launch, native/Workshop edit, Git push or Git LFS rule added.
The approved roster renaming list and Skywing model integration are not included.
''',encoding='utf-8')
print(json.dumps(report,indent=2))
