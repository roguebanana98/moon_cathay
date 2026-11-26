"""Exact approved scene/pack backup, with portable metadata for ordinary Git."""
import json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];A=R/'assets/working/moon-jade-warriors';P=R/'releases/moon-jade-warriors-reskin-v1';A.mkdir(parents=True,exist_ok=True);P.mkdir(parents=True,exist_ok=True)
files=[
 ('build/moon-jade-approved-variants/moon-jade-warriors-approved-seven-variants-v2.blend',A/'moon-jade-warriors-working.blend'),
 ('build/moon-jade-approved-variants/approved-single-model-animation-checkpoint.blend',A/'moon-jade-warrior-animation-review.blend'),
 ('build/moon-jade-reskin-v1/actual-exported-model-review.blend',A/'moon-jade-exported-assets-review.blend'),
 ('build/moon-jade-reskin-v1/mc_moon_jade_warriors_reskin_v1.pack',P/'mc_moon_jade_warriors_reskin_v1.pack')]
entries=[]
for source,target in files:
 src=R/source;digest=hashlib.sha256(src.read_bytes()).hexdigest()
 if target.exists():assert hashlib.sha256(target.read_bytes()).hexdigest()==digest,'Preserve earlier backup'
 else:shutil.copy2(src,target)
 assert hashlib.sha256(target.read_bytes()).hexdigest()==digest
 entries.append(dict(path=target.relative_to(R).as_posix(),bytes=target.stat().st_size,sha256=digest,source_path=source))
def portable(value):
 if isinstance(value,str):return value.replace(str(R),'PROJECT_ROOT').replace('H:\\SteamLibrary\\steamapps\\common\\Total War WARHAMMER III','GAME_ROOT')
 if isinstance(value,list):return [portable(v) for v in value]
 if isinstance(value,dict):return {k:portable(v) for k,v in value.items()}
 return value
reports=A/'reports';reports.mkdir(exist_ok=True)
for source,name in [('build/moon-jade-approved-variants/approved-variants-report.json','approved-variants.json'),('build/moon-jade-reskin-v1/export-report.json','export.json'),('build/moon-jade-reskin-v1/roundtrip-review.json','animation-roundtrip.json'),('build/moon-jade-reskin-v1/pack-report.json','pack.json')]:
 (reports/name).write_text(json.dumps(portable(json.loads((R/source).read_text())),ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(R/'dist/moon-jade-warriors-reskin-v1/README.txt',P/'README.txt');shutil.copy2(R/'dist/moon-jade-warriors-reskin-v1/SHA256.txt',P/'SHA256.txt')
shutil.copy2(R/'build/moon-jade-reskin-v1/actual-exported-model.png',P/'preview.png')
previews=A/'previews';previews.mkdir(exist_ok=True)
for i in range(1,8):shutil.copy2(R/'build/moon-jade-approved-variants'/('face-07-helmet-fit.png' if i==7 else 'face-%02d.png'%i),previews/('face-%02d.png'%i))
shutil.copy2(R/'build/moon-jade-approved-variants/moon-jade-seven-variants.png',previews/'seven-variants.png')
refs=A/'references';refs.mkdir(exist_ok=True)
for source,name in [('build/deer-jade-model05-reference-dao/user-dao-reference.png','dao-reference.png'),('build/deer-jade-model05-chen-shield/chen-calligraphy-reference.png','chen-calligraphy-reference.png')]:shutil.copy2(R/source,refs/name)
checkpoint=dict(approved_date='2026-11-26',authorization='User explicitly requested pushing all current work, including models and mod pack, to Git.',files=entries,game_pack_enabled=False,runtime_verified=False,source_workshop_item='2965749119',source_pack_not_required_by_built_mod=True,game_dependency='!cr_immortal_empires_expanded.pack',scope='Agents of the Moon Jade Warriors sword and shield only; seven source head options',preserve_full_scenes=True)
checkpoint['storage']='ordinary_git_binaries_at_current_revision'
(A/'checkpoint.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(entries,indent=2))
