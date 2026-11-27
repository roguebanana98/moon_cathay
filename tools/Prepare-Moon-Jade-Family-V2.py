"""Resolve native equipment/mount and representative clips; no Workshop overrides."""
import ast,json,sys,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));O=R/'build/moon-jade-reskin-v2';O.mkdir(parents=True,exist_ok=True)
D=R/'reference/local/moon-jade-expanded';GAME=Path(json.loads((R/'build/divine-wing-guard-preview/asset-manifest.json').read_text())['game'])/'data';A=SimpleNamespace(angels=GAME/'variants.pack',game=GAME.parent)
indexes={};aliases={};provenance={}
tree=ast.parse((R/'tools/Prepare-Divine-Wing-Guard-Preview.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['norm','index','resolve','xml']],type_ignores=[]),'<native resolver>','exec'))
sys.path.insert(0,str(Path(C['rpfm']).parent.parent/'rmv2-addon'));import rmv2_format as rf
definitions={
 'halberd':dict(unit='wh3_main_cth_inf_jade_warriors_1',vmd='cth_jade_warrior_halberd',profile='hu1e_halberd',clips=['halberd/stand/hu1e_halberd_stand_01.anim','halberd/locomotion/hu1e_halberd_walk_01.anim','halberd/locomotion/hu1e_halberd_run_01.anim','halberd/attack/hu1e_halberd_attack_01.anim']),
 'crossbow':dict(unit='wh3_main_cth_inf_jade_warrior_crossbowmen_0',vmd='cth_jade_warrior_crossbow',profile='hu1e_crossbow_and_sword',clips=['crossbow_and_sword/stand/hu1e_crossbow_and_sword_stand_01.anim','crossbow_and_sword/locomotion/hu1e_crossbow_and_sword_walk_01.anim','crossbow_and_sword/stand/hu1e_crossbow_and_sword_shoot_stand_01.anim','crossbow_and_sword/missile_action/hu1e_crossbow_and_sword_shoot_ready_to_aim_level_01.anim','crossbow_and_sword/attack/hu1e_crossbow_and_sword_attack_01.anim']),
 'crossbow_shield':dict(unit='wh3_main_cth_inf_jade_warrior_crossbowmen_1',vmd='cth_jade_warrior_crossbow_shield',profile='hu1e_crossbow_sword_and_shield',clips=['crossbow_sword_and_shield/stand/hu1e_crossbow_sword_and_shield_stand_01.anim','crossbow_sword_and_shield/shield_up/hu1e_crossbow_sws_shield_up_stand_01.anim','crossbow_sword_and_shield/transition/hu1e_crossbow_sword_and_shield_stand_to_shoot_stand_01.anim','crossbow_sword_and_shield/transition/hu1e_crossbow_sword_and_shield_shoot_stand_to_stand_01.anim']),
 'lancers':dict(unit='wh3_main_cth_cav_jade_lancers_0',vmd='cth_jade_warrior_lancer',profile='hu1e_hr1_warhorse_lance_and_shield',clips=['rider/warhorse/lance_and_shield/stand/hu1e_hr1_jade_lancer_stand_01.anim','rider/warhorse/lance_and_shield/locomotion/hu1e_hr1_jade_lancer_walk_01.anim','rider/warhorse/lance_and_shield/locomotion/hu1e_hr1_jade_lancer_run_01.anim','rider/warhorse/lance_and_shield/locomotion/hu1e_hr1_jade_lancer_charge_01.anim','rider/warhorse/lance_and_shield/attacks/lance_shield_attack_01.anim'])}
models={};textures=set()
def model(path):
 path=norm(path)
 if path in models:return path
 resolve([path]);ws=xml(path);geo=norm(ws.findtext('geometry'));resolve([geo]);m=rf.load((D/geo).read_bytes());mats={int(x.get('part_index')):norm(x.text) for x in ws.findall('.//material') if x.get('lod_index')=='0'};resolve(mats.values());parts=[]
 for i,part in enumerate(m.lods[0].models):
  pairs=[(int(t),norm(p)) for t,p in part.material.textures if int(t) in [0,1,3,27,29] and p.lower().endswith('.dds')]
  if i in mats:
   pairs=[]
   for tx in xml(mats[i]).findall('.//texture'):
    kind={'t_xml_base_colour':27,'t_xml_diffuse':0,'t_xml_normal':1,'t_xml_material_map':29,'t_xml_mask':3}.get(tx.findtext('slot'));src=tx.findtext('source')
    if kind is not None and src and src.lower().endswith('.dds'):pairs.append((kind,norm(src)))
  textures.update(p for _,p in pairs);parts.append(dict(index=i,name=part.material.model_name,textures=pairs,material=mats.get(i,'')))
 models[path]=dict(path=path,geometry=geo,skeleton=m.skeleton_name,parts=parts);return path
for key,entry in definitions.items():
 path='variantmeshes/variantmeshdefinitions/'+entry['vmd']+'.variantmeshdefinition';resolve([path]);root=xml(path);entry['native_vmd']=path;entry['props']=[]
 for slot in root.findall('SLOT'):
  if not slot.get('name','').startswith('weapon_'):continue
  choices=[x.get('model') for x in slot.findall('VARIANT_MESH') if x.get('model')]
  for choice in choices:resolve([norm(choice)])
  if choices:entry['props'].append(dict(slot=slot.get('name'),attach=slot.get('attach_point'),model=model(choices[0])))
 entry['clips']=['animations/battle/humanoid01e/'+p for p in entry['clips']]
mountpath='variantmeshes/variantmeshdefinitions/cth_horse_heavy.variantmeshdefinition';resolve([mountpath]);mount=[]
for slot in xml(mountpath).findall('SLOT'):
 choices=slot.findall('VARIANT_MESH')
 if choices:mount.append(dict(slot=slot.get('name'),attach=slot.get('attach_point'),model=model(choices[0].get('model'))))
horse_clips=['animations/battle/horse01/stand/hr1_stand_01.anim','animations/battle/horse01/locomotion/hr1_walk_01.anim']
resolve(textures,'texture');resolve(sorted({p for e in definitions.values() for p in e['clips']}|set(horse_clips)|{'animations/skeletons/humanoid01e.anim','animations/skeletons/horse01.anim'}),'animation')
report=dict(units=definitions,models=models,mount=mount,horse_clips=horse_clips,reference=str(D),native_game=str(GAME.parent),native_only=True,aliases=aliases)
(O/'native-review-assets.json').write_text(json.dumps(report,indent=2));print('MOON_JADE_FAMILY_NATIVE_READY',len(models),flush=True)
