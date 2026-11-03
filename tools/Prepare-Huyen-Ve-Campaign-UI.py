"""Prepare ASCII UI, private portraits and a one-time campaign test loadout."""
import csv,json,unicodedata,subprocess,copy,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/huyen-ve-v17-campaign';REF=R/'reference/local/huyen-ve-v17-base';C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));spec=json.loads((R/'src/campaign/huyen-ve-equipment.json').read_text());files=[]
def ascii_text(s):
 for a,b in {'\u0111':'d','\u0110':'D','\u2014':' - ','\u2013':'-','\u2019':"'",'\u2018':"'",'\u201c':'"','\u201d':'"','\u2026':'...'}.items():s=s.replace(a,b)
 return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode()
def load(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t'))
def write(internal,rows):
 p=O/(internal+'.tsv');p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n').writerows(rows)
 files.append(internal)
translations={x['key']:x['name'] for x in spec['items']};ability={'mc_huyen_ve_warden_aura':'Warden Authority','mc_huyen_ve_moon_lantern':'Moonlight Radiance','mc_huyen_ve_pha_ta':'Banish Evil'};loc_count=0
for p in (REF/'text/db').glob('*.loc.tsv'):
 rows=load(p)
 for row in rows[2:]:
  key=row[0];text=row[1]
  if key.startswith('ancillaries_onscreen_name_') and key.removeprefix('ancillaries_onscreen_name_') in translations:text=translations[key.removeprefix('ancillaries_onscreen_name_')]
  elif key=='ancillary_sets_name_'+spec['set_key']:text=spec['set_name']
  for a,name in ability.items():
   if key in ['unit_abilities_onscreen_name_'+a,'special_ability_phases_onscreen_name_'+a]:text=name
  if key.startswith('effects_description_mc_huyen_ve_enable_'):
   suffix=key.removeprefix('effects_description_mc_huyen_ve_enable_');text='Ability: '+ability['mc_huyen_ve_'+suffix]
  for a,b in {'An Tran Thu':"the Warden's Seal",'Nguyet Dang':'the Moon Lantern','Kiem Tran Da':"the Nightwarden's Blade"}.items():text=text.replace(a,b)
  row[1]=ascii_text(text);assert row[1].isascii();loc_count+=1
 write('text/db/'+p.name.removesuffix('.tsv'),rows)
def table(table,name,patches):
 internal='db/'+table+'_tables/'+name;rows=load(REF/(internal+'.tsv'));head=rows[0]
 for row in rows[2:]:
  for k,v in patches.items():row[head.index(k)]=v
 write(internal,rows)
portrait='ui/portraits/portholes/no_culture/mc_huyen_ve_0.png'
table('unit_variants','mc_moon_warden',{'unit_card':'mc_huyen_ve'})
table('units_custom_battle_permissions','mc_moon_warden_custom_battle',{'general_portrait':portrait})
table('battle_set_piece_armies_characters','mc_moon_warden_custom_battle',{'portrait':portrait})
# Native portrait-settings database selects static images by art-set ID.
for folder in ['units','portholes','faction_leaders']:
 donor='portholes' if folder=='faction_leaders' else folder;d=json.loads((O/('portrait-donor-'+donor+'.json')).read_text());entry=d['entries'][0];entry['id']='mc_moon_warden_art';variant=entry['variants'][0];variant['filename']='mc_huyen_ve_human';variant['file_diffuse']='ui/portraits/'+folder+('/no_culture' if folder!='faction_leaders' else '')+'/mc_huyen_ve_0.png'
 variant['faction_leader']=folder=='faction_leaders'
 jp=O/('portrait-'+folder+'.json');jp.write_text(json.dumps(d,indent=2));internal='ui/portraits/'+folder+'/portrait_settings__mc_huyen_ve.bin';bp=O/internal;bp.parent.mkdir(parents=True,exist_ok=True)
 subprocess.run([C['rpfm'],'-g','warhammer_3','portrait-settings','from-json','-j',str(jp),'-b',str(bp)],check=True,stdout=subprocess.DEVNULL);files.append(internal)
for script in ['mc_huyen_ve_name.lua','mc_huyen_ve_campaign_test_items.lua']:
 internal='script/campaign/mod/'+script;p=O/internal;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/'src'/internal,p);assert p.read_text().isascii();files.append(internal)
for row in json.loads((O/'portrait-render-report.json').read_text())['images']:assert (O/row['file']).is_file();files.append(row['file'])
(O/'ui-campaign-manifest.json').write_text(json.dumps({'files':files,'ascii_loc_rows':loc_count,'items':translations,'portrait_art_set':'mc_moon_warden_art','name_repair':'ASCII direct custom name on load and faction turn','test_loadout':'One-time grant and force equip five items; saved per-item markers','runtime_verified':False},indent=2));print('V17_UI_PREPARED',len(files),'files',loc_count,'ASCII loc rows')

