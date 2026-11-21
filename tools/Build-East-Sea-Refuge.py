"""Add refuge/homecoming events over v3 without changing its startpos/assets."""
import csv,hashlib,json,shutil,struct,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'build/east-sea-refuge';O.mkdir(parents=True,exist_ok=True)
C=json.loads((R/'config/local.json').read_text(encoding='utf-8-sig'));N=R/'reference/local/lord-vanilla/db'
BASE=R/'build/east-sea-characters/edh_east_sea_charter_characters_v3.pack'
assert hashlib.sha256(BASE.read_bytes()).hexdigest()=='d5f6f1a726c1023727b05ea614f19dbc6e09d63e322b182419c2622677015edb'
PACK=O/'edh_east_sea_charter_refuge_v4.pack';assert not PACK.exists(),'Use a new revision; preserve existing artifact'
files=[];loc=[]
def read(t):
 with (N/(t+'_tables/data__.tsv')).open(encoding='utf-8-sig',newline='') as f:a=list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
 return a[:2],[dict(zip(a[0],r)) for r in a[2:]]
def write(t,rows):
 (h,m),_=read(t);m=m.copy();p='db/'+t+'_tables/edh_refuge';m[0]=';'.join(m[0].split(';')[:2]+[p]);dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
 with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([h,m]+[[r[k] for k in h] for r in rows])
 files.append(p)
_,native=read('incidents');donor=next(r for r in native if r['key']=='wh2_main_incident_all_character_exp_up');incidents=[];options=[]
for i,(key,title,body) in enumerate([
 ('edh_charter_moon_sanctuary','Sanctuary of the Moon','East Sea Charter has fallen. Heinrich von Adlerhorst and Sariwa have joined Agents of the Moon. Their experience, skills and equipment are retained. Wounded characters continue their recovery; Heinrich can be recruited as a Lord when available.'),
 ('edh_charter_homecoming','The Charter Restored','East Sea Charter lives again. Heinrich von Adlerhorst and Sariwa have returned to their homeland, ending their service with Agents of the Moon. Their experience, skills and equipment are retained. Troops commanded for Agents of the Moon remain with that faction.')]):
 r=dict(donor);r.update(key=key,generate='false',prioritised='true',is_large_incident='true',ui_image='generic');incidents.append(r)
 for j,(option,value) in enumerate([('VAR_CHANCE','100'),('GEN_TARGET_NONE','')]):options.append(dict(id=str(1986111801+i*2+j),incident_key=key,option_key=option,value=value,target='default'))
 loc.extend([['incidents_localised_title_'+key,title,'true'],['incidents_localised_description_'+key,body,'true']])
write('incidents',incidents);write('cdir_events_incident_option_junctions',options)
_,existing=read('cdir_events_incident_option_junctions');assert not ({r['id'] for r in existing}&{r['id'] for r in options})
write('faction_agent_permitted_subtypes',[dict(agent=a,faction='cr_cth_agents_of_the_moon',subtype=s,mod_disabled='false') for a,s in [('general','edh_heinrich_cb'),('wizard','edh_sariwa')]])
write('units_to_groupings_military_permissions',[dict(unit=k,military_group='wh3_main_cth') for k in ['edh_heinrich_cb','edh_sariwa']])
p='text/db/edh_refuge.loc';dest=O/(p+'.tsv');dest.parent.mkdir(parents=True,exist_ok=True)
with dest.open('w',encoding='utf-8',newline='') as f:csv.writer(f,delimiter='\t',lineterminator='\n',quoting=csv.QUOTE_NONE,quotechar=None).writerows([['key','text','tooltip'],['#Loc;1;'+p,'','']]+loc)
files.append(p)
script='script/campaign/mod/edh_east_sea_charter_refuge.lua'
def cli(*args):
 r=subprocess.run([C['rpfm'],'-g','warhammer_3',*map(str,args)],capture_output=True,text=True)
 with (O/'build.log').open('a',encoding='utf-8') as f:f.write(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
shutil.copy2(BASE,PACK)
for p in files:cli('pack','add','-p',PACK,'-t',C['schema'],'-f',str(O/(p+'.tsv'))+';'+p)
cli('pack','add','-p',PACK,'-f',str(R/'src'/script)+';'+script);files.append(script)
def payloads(p):
 raw=p.read_bytes();assert raw[:4]==b'PFH5';flags,dc,ds,fc,fs,_=struct.unpack('<6I',raw[4:28]);pos=28+ds;stop=pos+fs;entries=[]
 for _ in range(fc):
  size,compression=struct.unpack('<IB',raw[pos:pos+5]);pos+=5;assert compression==0
  end=raw.index(0,pos);key=raw[pos:end].decode().replace('\\','/');pos=end+1;entries.append((key,size))
 assert pos==stop;result={}
 for key,size in entries:result[key]=raw[pos:pos+size];pos+=size
 assert pos==len(raw);return {k:v for k,v in result.items() if not k.endswith('.rpfm_reserved')}
before=payloads(BASE);after=payloads(PACK);assert set(after)-set(before)==set(files)
assert all(after[k]==data for k,data in before.items()),'Unrelated v3 payload changed'
Q=R/'reference/local/edh-refuge-roundtrip';cli('pack','extract','-p',PACK,'-t',C['schema'],'-F','/;'+str(Q))
for p in files:
 if p.startswith(('db/','text/')):
  def rows(path):
   with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.reader(f,delimiter='\t',quoting=csv.QUOTE_NONE))
  a,z=rows(O/(p+'.tsv')),rows(Q/(p+'.tsv'));assert a[0]==z[0] and a[2:]==z[2:],p
assert (Q/script).read_bytes()==(R/'src'/script).read_bytes()
report=dict(pack=str(PACK),sha256=hashlib.sha256(PACK.read_bytes()).hexdigest(),base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),added_payloads=files,all_v3_payloads_byte_identical=True,startpos_unchanged=True,model_and_skills_unchanged=True,db_loc_roundtrip=True,deployed=False,runtime_verified=False,runtime_testing_deferred_by_user=True)
(O/'build-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
